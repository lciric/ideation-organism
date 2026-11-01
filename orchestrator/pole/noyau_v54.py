"""Noyau commun de la v54 : orchestration d'étapes sous S17, appels comptés, aiguilleur, juges croisés, garde A4 — partagé par
la génération de la course 2 (`course2_v54`) et le pré-pilote (`prepilote_v54`).

Ce que ce noyau garantit (et que la v53 ne garantissait pas) :

- **CL18-01** : *tout* appel (proposeur, aiguilleur, **juge**, lecteur, metteur en fusion, rédacteur, metteur en forme,
  relecteur, vérificateur…) passe par `Orchestre.appel`, qui note au coffre une consommation par appel (étape, rôle, coût,
  fournisseur, modèle demandé et servi, statut, durée, coût inconnu) **dans un bloc `finally`** : une exception après
  l'appel ne perd jamais le coût engagé ; une exception de l'adaptateur compte le plafond de la session (pire cas).
- **CL18-02** : un reste de budget nul rencontré pendant une étape **marque l'étape coupée** (`etat["coupee"]`), notée au
  journal de consommation (marque `coupure`, montant 0) ; le budget la déclare « non mesurée (budget) » si elle est
  protégée ; l'orchestrateur s'arrête au premier « non mesuré » (nœud, C13).
- **A3, A11, A14** : `SuiviRoles` (échecs consécutifs, appels coupés, refus et limite d'Opus, part d'appels sans sortie).
  A14 dépassée par un rôle de l'étape → étape « non mesurée (technique) » (nœud), marquée au journal de consommation.
- **CL18-05** : le passeport de l'aiguilleur se vérifie sur l'empreinte **recalculée** du contenu présent.
- **CL18-06, CL18-12** : garde A4 en mode injecté, sur la fiche puis sur l'entrée complète ; action sur une fiche injectée
  (arrêt ou fiche exclue, comptée) ; dossiers de session **opaques** (empreinte du chemin logique ; la correspondance est
  déposée au coffre).
- **CL18-10** : un refus de l'aiguilleur sur une fiche de Kimi compte au débordement ou aux échecs techniques selon
  `garde_kimi.refus_aiguilleur`.
"""

import hashlib
import os
import time

from . import fiches_v54 as fv
from .aiguilleur_v53 import CLASSES, DebordementKimi, SansPasseport, lire_classe
from .budget_v54 import JOUER, BudgetV54
from .coffre_v53 import Coffre
from .configuration_v53 import texte_piece
from .graines_v53 import Graines
from .juges_croises_v53 import VersionServieChangee, lire_verdict
from .outils import ecrire_json_scelle
from .suivi_roles_v54 import RoleArrete, SuiviRoles

VERSION = "noyau-v54"
EPS = 1e-9


class NoeudArret(RuntimeError):
    """Arrêt de nœud (C13, A5, A6, A7, A12…) : la course ne continue pas ; motif consigné."""


class Orchestre:
    def __init__(self, conf, sortie, adaptateurs, *, prefixe_taches, horloge=None):
        self.conf, self.sortie, self.ad = conf, sortie, adaptateurs
        self.prefixe = prefixe_taches
        self.horloge = horloge or time.monotonic
        self.graines = Graines(conf["racine_graines"])
        self.coffre = Coffre(os.path.join(sortie, "coffre"))
        b = conf["budget"]
        self.budget = BudgetV54(b["plafond_usd"], b["arret_etape_usd"], b["etapes"])
        self.suivi = SuiviRoles(conf["arrets"], horloge=self.horloge)
        self.ps = conf["plafonds_session"]
        self.interdites = conf["etiquettes_interdites"]
        self.a4_mode, self.a4_action = conf["a4"]["mode"], conf["a4"]["action"]
        self.evenements, self.etapes_etat, self.sessions = [], {}, {}
        self.exclues_a4, self.appels_sautes = {}, {}
        self.noeud = None
        self.modele_servi_juges, self.absents_juges = {}, {j["etiquette"]: 0 for j in conf["juges"]}
        self.lots_juges = set()
        self.cles_anonymisation = {}

    # --- outils ------------------------------------------------------------------------------------------------------------

    def ev(self, quoi, **champs):
        self.evenements.append(dict({"n": len(self.evenements) + 1, "evenement": quoi}, **champs))

    def tache(self, *morceaux):
        return "-".join([self.prefixe] + [str(m) for m in morceaux])

    def session(self, *logique):
        chemin = "/".join(str(x) for x in logique)
        opaque = hashlib.sha256(f"{self.conf['racine_graines']}|{self.prefixe}|{chemin}".encode("utf-8")).hexdigest()[:16]
        self.sessions[opaque] = chemin
        d = os.path.join(self.sortie, "sessions", opaque)
        os.makedirs(d, exist_ok=True)
        return d

    def piece(self, nom):
        return texte_piece(self.conf, nom)

    def appel(self, etat, *, role, role_kit, fournisseur, modele, consigne, plafond_role, session, lire=None):
        """Un appel compté. Rend None si l'appel n'est pas lancé (reste nul : étape coupée ; rôle arrêté), sinon
        {r, lu (None si inexploitable ou coupé), motif, duree}."""
        reste = etat["reste"] - etat["cout"]
        if reste <= EPS:
            etat["coupee"] = True
            self.ev("coupure-budget", etape=etat["etape"], role=role)
            return None
        try:
            debut = self.suivi.avant(role)
        except RoleArrete as e:
            self.appels_sautes[role] = self.appels_sautes.get(role, 0) + 1
            self.ev("appel-saute-role-arrete", etape=etat["etape"], role=role, motif=str(e)[:200])
            return None
        plafond = min(float(self.ps[plafond_role]), reste)
        dossier = self.session(*session)
        r, cout, statut, duree = None, None, "exception", 0.0
        try:
            r = self.ad[fournisseur].lancer(role_kit, consigne, dossier, plafond, 1, modele=modele)
            cout, statut = float(r.cout_declare_usd), r.statut
        finally:
            duree = self.horloge() - debut
            inconnu = cout is None or bool(getattr(r, "cout_inconnu", False))
            cout = plafond if cout is None else cout
            etat["cout"] += cout
            self.coffre.noter_consommation(etat["etape"], role, cout, fournisseur=fournisseur, modele_demande=modele,
                                           modele_servi=getattr(r, "modele_servi", None), statut=statut,
                                           duree_s=round(duree, 3), cout_inconnu=inconnu,
                                           jetons="non lus (l'adaptateur ne les rend pas)")
        texte = (r.texte_brut or r.texte_final) if r.statut == "ok" else None
        lu = (lire(texte) if lire else texte) if texte is not None else None
        utilisable, motif, _ = self.suivi.apres(role, etat["etape"], fournisseur=fournisseur, modele=modele, duree=duree,
                                                statut=r.statut, exploitable=lu is not None, refus=r.refus,
                                                modele_servi=r.modele_servi)
        if motif:
            self.ev("appel-inexploitable", etape=etat["etape"], role=role, motif=motif)
        return {"r": r, "lu": lu if utilisable else None, "motif": motif, "duree": duree}

    def jouer_etape(self, nom, fonction):
        decision, detail = self.budget.avant_etape(nom)
        self.ev("etape", etape=nom, decision=decision, **{k: v for k, v in detail.items() if k != "motif"})
        if decision != JOUER:
            self.etapes_etat[nom] = decision
            return decision
        etat = {"cout": 0.0, "reste": detail["reste_avant_plafond_usd"], "coupee": False, "etape": nom}
        try:
            fonction(etat)
        finally:
            if etat["coupee"]:
                self.coffre.noter_consommation(nom, "coupure", 0.0, coupure=True)
            res = self.budget.apres_etape(nom, etat["cout"], coupee=etat["coupee"])
            if res == "jouee":
                trop = {role: part for role, part in self.suivi.depassements_a14().items()
                        if nom in self.suivi.roles[role]["etapes"]}
                if trop:
                    motif = "A14 : part d'appels sans sortie exploitable au-delà du seuil : " + ", ".join(
                        f"{k} {v:.2f}" for k, v in sorted(trop.items()))
                    self.coffre.noter_consommation(nom, "a14", 0.0, technique=True, motif=motif)
                    res = self.budget.marquer_technique(nom, motif)
            self.etapes_etat[nom] = res
        return self.etapes_etat[nom]

    def c13_ou_noeud(self, nom):
        """Après une étape : si C13 n'est plus satisfaite, nœud (CL18-02) ; rend vrai si l'on peut continuer."""
        e = self.budget.etat()
        if e["c13_satisfaite"]:
            return True
        self.noeud = (f"C13 non satisfaite après l'étape {nom} ({self.etapes_etat.get(nom)}) : nœud (O12) ; la course ne "
                      "continue pas")
        self.ev("noeud-c13", etape=nom, etat=self.etapes_etat.get(nom))
        return False

    # --- A4 -------------------------------------------------------------------------------------------------------------------

    def servir(self, consigne, fiche, quoi, identifiant_servi=None):
        """Entrée consigne + une fiche (A4 sur la fiche puis sur l'entrée complète). Rend None si la fiche est exclue
        (`a4.action = fiche_exclue`) ; lève `EtiquetteDansEntree` sinon."""
        try:
            return fv.entree_une_fiche(consigne, fiche, self.interdites, self.a4_mode, identifiant_servi)
        except fv.EtiquetteDansEntree as e:
            dans_fiche = fv.trouver(fv.corps_fiche(fiche), self.interdites, self.a4_mode)
            if dans_fiche and self.a4_action == "fiche_exclue":
                self.exclure_a4(fiche, dans_fiche, quoi)
                return None
            raise e

    def exclure_a4(self, fiche, trouvees, quoi):
        self.exclues_a4[fiche["ident"]] = {"etiquettes": trouvees, "destination": quoi}
        if hasattr(self, "aiguilleur"):
            self.aiguilleur.retirer(fiche)
        self.ev("incident-a4-fiche-exclue", ident=fiche["ident"], destination=quoi, etiquettes=trouvees)

    # --- juges croisés ------------------------------------------------------------------------------------------------------

    def juger(self, fiche, lot, etat):
        """Chaque juge, un appel par fiche (consommation notée par appel, CL18-01) ; verdicts au coffre (A21) ; A2."""
        self.aiguilleur.exiger_passeport(fiche, "un juge")
        self.lots_juges.add(lot)
        verdicts = {}
        for j in self.conf["juges"]:
            ident_servi = "F" + self.graines.jeton_opaque(self.tache("anonymisation", j["etiquette"], fiche["ident"]), 5)
            entree = self.servir(self.piece(j["consigne"]), fiche, "un juge", identifiant_servi=ident_servi)
            if entree is None:
                return False
            a = self.appel(etat, role=j["etiquette"], role_kit="juge_ideation", fournisseur=j["fournisseur"], modele=j["modele"],
                           consigne=entree, plafond_role="juge", session=("juges", lot, j["etiquette"], fiche["ident"]),
                           lire=lambda t: lire_verdict(t, self.conf["items_juge"]))
            if a is not None and a["r"].statut == "ok" and a["r"].modele_servi:
                vu = self.modele_servi_juges.setdefault(j["etiquette"], a["r"].modele_servi)
                if vu != a["r"].modele_servi:
                    raise VersionServieChangee(f"A2 : juge {j['etiquette']} servi par {a['r'].modele_servi!r} après {vu!r} : arrêt du rôle")
            v = a["lu"] if a is not None else None
            if v is None:
                self.absents_juges[j["etiquette"]] += 1
            verdicts[j["etiquette"]] = v
            self.cles_anonymisation.setdefault(j["etiquette"], {})[ident_servi] = fiche["ident"]
        self.coffre.deposer(f"verdicts-{lot}-{fiche['ident']}", {"ident": fiche["ident"], "empreinte": fiche["empreinte"],
                                                                 "verdicts": verdicts})
        return True

    def ouvrir_verdicts(self, idents):
        sortie = {}
        for lot in sorted(self.lots_juges):
            for i in idents:
                nom = f"verdicts-{lot}-{i}"
                if os.path.exists(os.path.join(self.coffre.dossier, nom + ".json")):
                    sortie[i] = self.coffre.ouvrir(nom)["verdicts"]
        return sortie

    def deposer_cles(self):
        """Clés déposées scellées au coffre (A21) : sessions opaques, anonymisation des juges."""
        self.coffre.deposer(self.tache("cle-sessions"), self.sessions)
        self.coffre.deposer(self.tache("cle-anonymisation"), self.cles_anonymisation)


class AiguilleurV54:
    """Aiguilleur (M4) : passeport sur empreinte recalculée (CL18-05) ; refus compté à part (CL18-10) ; contenu des fiches
    retenues jamais copié (R-575)."""

    def __init__(self, orch, *, etiquette, modele, fournisseur, consigne, dossier):
        self.o, self.etiquette, self.modele, self.fournisseur, self.nom_consigne = orch, etiquette, modele, fournisseur, consigne
        os.makedirs(dossier)
        self.dossier = dossier
        self.passeports, self.decisions, self.journal = {}, {}, []
        self.refus = 0

    def classer(self, fiche, etat, lot):
        """Rend la classe retenue, ou None si l'appel n'a pas été lancé (coupure, rôle arrêté, fiche exclue par A4)."""
        entree = self.o.servir(self.o.piece(self.nom_consigne), fiche, "l'aiguilleur")
        if entree is None:
            return None
        a = self.o.appel(etat, role=self.etiquette, role_kit="juge_ideation", fournisseur=self.fournisseur, modele=self.modele,
                         consigne=entree, plafond_role="aiguilleur", session=("aiguillage", lot, fiche["ident"]),
                         lire=lambda t: lire_classe(t)[0] and lire_classe(t))
        if a is None:
            self.decisions[fiche["ident"]] = {"classe": None, "motif": "non lancé (coupure ou rôle arrêté)"}
            return None
        lu = a["lu"]
        classe, categorie = (lu if lu else (None, None))
        refus = classe is None
        if refus:
            self.refus += 1
        retenue = "concret" if refus else classe
        self.decisions[fiche["ident"]] = {"classe": retenue, "lue": classe, "refus": refus, "motif": a["motif"]}
        if retenue == "niveau_methode":
            self.passeports[fiche["ident"]] = fiche["empreinte"]
        else:
            self.journal.append({"ident": fiche["ident"], "empreinte": fiche["empreinte"], "classe": retenue, "categorie": categorie,
                                 "fournisseur": fiche["meta"]["fournisseur"], "origine": fiche["meta"]["origine"],
                                 "refus_aiguilleur": refus, "contenu": "non copié (R-575)"})
        return retenue

    def a_passeport(self, fiche):
        e = self.passeports.get(fiche.get("ident"))
        return e is not None and e == fiche.get("empreinte") and e == fv.empreinte_contenu(fiche)

    def exiger_passeport(self, fiche, destination):
        if not self.a_passeport(fiche):
            raise SansPasseport(f"A17 : fiche {fiche.get('ident')!r} sans passage « niveau méthode » valide (empreinte recalculée) "
                                f"présentée à {destination} : arrêt, notations annulées")
        return True

    def retirer(self, fiche):
        self.passeports.pop(fiche["ident"], None)

    def sceller(self):
        return ecrire_json_scelle(os.path.join(self.dossier, "journal-aiguillage.json"), {
            "version": VERSION, "regle": "fiches retenues : identifiant, empreinte, classe ; contenu jamais copié (R-575)",
            "retenues": self.journal, "refus_aiguilleur": self.refus, "passeports": len(self.passeports), "classes": list(CLASSES)})


class GardeKimiV54:
    """M5 en course : taux de débordement de Kimi proposeur contre S12 ; refus de l'aiguilleur compté selon le choix 6."""

    def __init__(self, debordement_max, refus_aiguilleur):
        self.seuil, self.mode = float(debordement_max), refus_aiguilleur
        self.vues, self.concretes, self.refus_techniques = 0, 0, 0
        self.refusees = []

    def noter(self, fiche, classe, refus):
        if refus and self.mode == "technique":
            self.refus_techniques += 1
            return
        self.vues += 1
        if classe == "concret":
            self.concretes += 1
        if classe != "niveau_methode":
            self.refusees.append({"ident": fiche["ident"], "empreinte": fiche["empreinte"], "classe": classe, "refus": refus})

    def taux(self):
        return self.concretes / self.vues if self.vues else 0.0

    def verifier(self):
        if self.vues and self.taux() > self.seuil + 1e-12:
            raise DebordementKimi(f"débordement de Kimi proposeur {self.concretes}/{self.vues} = {self.taux():.3f} > S12 = "
                                  f"{self.seuil:g} : arrêt du rôle proposeur de Kimi (nœud)")
        return True

    def etat(self):
        return {"vues": self.vues, "concretes": self.concretes, "taux": self.taux(), "seuil_S12": self.seuil,
                "refus_aiguilleur": self.mode, "refus_comptes_techniques": self.refus_techniques, "refusees": self.refusees}
