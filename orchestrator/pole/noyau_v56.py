"""Noyau de la v56 — un mélange (`OrchestreV56`) placé devant `OrchestreV55` (inchangé, R12) dans les classes de la course et du
pré-pilote. Contre-lecture CL20.

- **CL20-02 (bloquant)** : budget `BudgetV56` (règle d'A1 du brouillon 10, relais du devis v6). Au lancement de chaque étape,
  le plafond dur calculé est (1) recalculé par le **second programme** (`rejouer_consommations_v56`, décisions et plafond sur
  le seul journal de consommations) et par une **formule indépendante** (`plafond_independant`) : égalité au centime exigée,
  sinon `PlafondDeRelaisFaux` (arrêt) ; (2) **transmis à chaque relais** par sa porte (`adaptateurs_v56`), accusé au centime
  exigé, sinon `RelaisSansPlafond` (A15 : l'étape n'est pas lancée, l'exécution s'arrête) ; (3) tenu par le noyau : le plafond
  de chaque appel est borné au reste **de l'étape** sous ce plafond dur ; un reste nul coupe l'étape (statuts de la ligne 11b).
  Le plafond ne change pas pendant l'étape. Après l'étape, un cumul au-delà de S17 est un arrêt (`CumulAuDelaDeS17`). Chaque
  transmission, chaque coupure et la lecture réduite de M6 entière coupée sont notées au journal de consommations.
- **CL20-12** : A2 « modèle servi non lu » pour une réponse « ok », et A2 « version servie d'un juge changée » : **arrêt de ce
  rôle** (texte A2 : « arrêt de ce rôle ; aucune bascule sans mot de Lazar »), réponse jamais lue, appel compté inexploitable
  (A14 juge ensuite l'étape) — la v55 arrêtait toute l'exécution.
- **CL20-06** : chaque adaptateur du kit doit interdire la lecture de la sortie (et du coffre) ; vérifié à la construction.
- **CL20-05** : `juger` note la **présence** de chaque verdict (jamais son contenu) : une fusion n'est complète qu'avec son
  passeport et tous ses verdicts.
- **CL20-04** : `ArretSurSignal` convertit SIGTERM et SIGINT en `ArretParSignal` (exception de base, que les `except Exception`
  ne retiennent pas) ; les signaux reçus pendant le nettoyage sont notés, sans lever, pour que le manifeste de fin soit écrit.
"""

import signal
import threading

from .adaptateurs_v56 import (LectureNonInterdite, PortePlafondNoyau, RelaisSansPlafond, est_adaptateur_reel,
                              verifier_lecture_interdite)
from .budget_v56 import (EPS, JOUER, BudgetV56, CumulAuDelaDeS17, PlafondDeRelaisFaux, centimes, plafond_independant,
                         rejouer_consommations_v56)
from .configuration_v53 import ConfigurationRefusee
from .noyau_v55 import OrchestreV55
from .suivi_roles_v54 import RoleArrete

VERSION = "noyau-v56"


# --- CL20-04 : signaux ----------------------------------------------------------------------------------------------------------


class ArretParSignal(BaseException):
    """SIGTERM ou SIGINT reçu : arrêt propre (manifeste de fin, sessions rangées, empreintes de sortie)."""

    def __init__(self, signum):
        self.signum = signum
        super().__init__(f"signal {signal.Signals(signum).name} reçu : arrêt propre")


class ArretSurSignal:
    """Contexte : au premier SIGTERM ou SIGINT, lève `ArretParSignal` dans le fil principal ; pendant le nettoyage
    (`nettoyage()`), et après le premier, les signaux sont notés sans lever. Hors du fil principal : rien n'est installé (dit)."""

    SIGNAUX = (signal.SIGTERM, signal.SIGINT)

    def __init__(self):
        self.recu, self.differes, self._anciens, self._nettoyage = None, [], {}, False

    def _gestionnaire(self, signum, frame):
        if self.recu is None and not self._nettoyage:
            self.recu = signum
            raise ArretParSignal(signum)
        self.differes.append(signal.Signals(signum).name)

    def __enter__(self):
        if threading.current_thread() is threading.main_thread():
            for s in self.SIGNAUX:
                ancien = signal.getsignal(s)
                signal.signal(s, self._gestionnaire)
                self._anciens[s] = signal.SIG_DFL if ancien is None else ancien
        return self

    def nettoyage(self):
        self._nettoyage = True

    def __exit__(self, *exc):
        for s, h in self._anciens.items():
            signal.signal(s, h)
        return False

    def etat(self):
        return {"installe": bool(self._anciens), "recu": None if self.recu is None else signal.Signals(self.recu).name,
                "differes_pendant_le_nettoyage": list(self.differes)}


def motif_arret(e):
    if isinstance(e, ArretParSignal):
        return f"signal {signal.Signals(e.signum).name} reçu (ArretParSignal) : arrêt propre, manifeste de fin écrit"
    if isinstance(e, KeyboardInterrupt):
        return "interruption clavier (KeyboardInterrupt) : arrêt propre, manifeste de fin écrit"
    return f"{type(e).__name__} : {str(e)[:500]}"


# --- l'orchestre ---------------------------------------------------------------------------------------------------------------


class OrchestreV56(OrchestreV55):
    """Mélange à placer avant `GenerationV55` ; `portes` ({fournisseur: porte}) lu en argument nommé ou sur l'instance
    (`_portes_demandees`) si posé avant `__init__`."""

    def __init__(self, *a, **kw):
        portes = kw.pop("portes", None)
        if portes is None:
            portes = getattr(self, "_portes_demandees", None)
        adaptateurs = a[2] if len(a) > 2 else kw.get("adaptateurs", {})
        self.portes = self._portes(dict(portes or {}), adaptateurs)
        super().__init__(*a, **kw)
        b = self.conf["budget"]
        self.budget = BudgetV56(b["plafond_usd"], b["arret_etape_usd"], b["etapes"])  # CL20-02 (la v54 posait la règle « réservation »)
        self.transmissions, self.roles_arretes_a2, self.verdicts_presents = [], {}, {}
        try:
            self.lecture_interdite = {f: v for f, ad in sorted(self.ad.items())
                                      if (v := verifier_lecture_interdite(ad, self.sortie, self.racine_sessions)) is not None}
        except LectureNonInterdite:
            self.ranger_sessions()
            raise

    @staticmethod
    def _portes(portes, adaptateurs):
        inconnues = sorted(set(portes) - set(adaptateurs))
        if inconnues:
            raise ConfigurationRefusee("portes de plafond pour des fournisseurs sans adaptateur : " + ", ".join(inconnues))
        for f, ad in adaptateurs.items():
            if f not in portes:
                if est_adaptateur_reel(ad):
                    raise RelaisSansPlafond(f"A15 : relais réel « {f} » sans porte de plafond d'étape : incapable de recevoir le "
                                            "plafond dur au lancement de chaque étape (DEP4, brouillon 10) : aucun lancement")
                portes[f] = PortePlafondNoyau()
            elif isinstance(portes[f], PortePlafondNoyau) and est_adaptateur_reel(ad):
                raise RelaisSansPlafond(f"A15 : la porte « noyau » ne vaut que sans relais réel (fournisseur {f})")
            if not callable(getattr(portes[f], "transmettre", None)):
                raise ConfigurationRefusee(f"porte de plafond de {f} : méthode transmettre(étape, plafond) exigée")
        return portes

    def description_portes(self):
        return {f: (p.description() if hasattr(p, "description") else type(p).__name__) for f, p in sorted(self.portes.items())}

    # --- un appel (A2 : arrêt de ce rôle) -----------------------------------------------------------------------------------

    def _arreter_role_a2(self, role, etape, motif, deja_compte_exploitable=False):
        r = self.suivi._r(role)
        if deja_compte_exploitable:  # l'appel avait été compté exploitable : sa réponse n'est pas lue
            r["inexploitables"] += 1
            r["etapes"].setdefault(etape, {"appels": 0, "inexploitables": 0})["inexploitables"] += 1
        if not r["arrete"]:
            r["arrete"] = motif
        self.roles_arretes_a2.setdefault(role, motif)
        self.ev("arret-role-a2", etape=etape, role=role, motif=motif[:300])

    def appel(self, etat, *, role, role_kit, fournisseur, modele, consigne, plafond_role, session, lire=None):
        """Comme la v54 (consommation notée dans un bloc `finally`, plafond de l'appel borné au reste de l'étape), avec le reste
        pris sous le **plafond dur de l'étape** (CL20-02) et A2 en arrêt de rôle (CL20-12)."""
        reste = etat["reste"] - etat["cout"]
        if reste <= EPS:
            etat["coupee"] = True
            self.ev("coupure-plafond-relais", etape=etat["etape"], role=role, plafond_dur_usd=etat.get("plafond_dur_usd"))
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
                                           duree_s=round(duree, 3), cout_inconnu=inconnu, plafond_appel_usd=round(plafond, 6),
                                           jetons="non lus (l'adaptateur ne les rend pas)")
        servi = getattr(r, "modele_servi", None)
        a2 = r.statut == "ok" and not servi
        texte = (r.texte_brut or r.texte_final) if (r.statut == "ok" and not a2) else None
        lu = (lire(texte) if lire else texte) if texte is not None else None
        utilisable, motif, _ = self.suivi.apres(role, etat["etape"], fournisseur=fournisseur, modele=modele, duree=duree,
                                                statut=r.statut, exploitable=lu is not None, refus=r.refus, modele_servi=servi)
        if a2:
            motif = (f"A2 : modèle servi non lu pour une réponse « ok » (modèle demandé {modele!r}) : arrêt de ce rôle, aucune "
                     "bascule sans mot de Lazar ; réponse non lue")
            self._arreter_role_a2(role, etat["etape"], motif)
        if motif:
            self.ev("appel-inexploitable", etape=etat["etape"], role=role, motif=motif)
        return {"r": r, "lu": lu if (utilisable and not a2) else None, "motif": motif, "duree": duree}

    # --- juges : présence des verdicts ; A2 version changée = arrêt de ce rôle ------------------------------------------------

    def juger(self, fiche, lot, etat):
        from .juges_croises_v53 import lire_verdict
        self.aiguilleur.exiger_passeport(fiche, "un juge")
        self.lots_juges.add(lot)
        verdicts, presents = {}, {}
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
                    motif = (f"A2 : juge {j['etiquette']} servi par {a['r'].modele_servi!r} après {vu!r} : arrêt de ce rôle, "
                             "aucune bascule sans mot de Lazar ; verdict non lu")
                    self._arreter_role_a2(j["etiquette"], etat["etape"], motif, deja_compte_exploitable=a["lu"] is not None)
                    a = dict(a, lu=None, motif=motif)
            v = a["lu"] if a is not None else None
            if v is None:
                self.absents_juges[j["etiquette"]] += 1
            verdicts[j["etiquette"]] = v
            presents[j["etiquette"]] = v is not None
            self.cles_anonymisation.setdefault(j["etiquette"], {})[ident_servi] = fiche["ident"]
        self.coffre.deposer(f"verdicts-{lot}-{fiche['ident']}", {"ident": fiche["ident"], "empreinte": fiche["empreinte"],
                                                                 "verdicts": verdicts})
        self.verdicts_presents[fiche["ident"]] = presents  # présence seulement, jamais le contenu (A21)
        return True

    # --- une étape sous son plafond dur (CL20-02) -----------------------------------------------------------------------------

    def _verifier_et_transmettre(self, nom, detail):
        plafond = detail["plafond_dur_usd"]
        b = self.conf["budget"]
        cons = self.coffre.consommations()
        decisions, _, plafonds = rejouer_consommations_v56(b["plafond_usd"], b["arret_etape_usd"], b["etapes"], cons, jusqu_a=nom)
        if decisions != self.budget.decisions() or nom not in plafonds or centimes(plafonds[nom]) != centimes(plafond):
            raise PlafondDeRelaisFaux(f"11a : plafond dur de {nom} ({plafond:.2f} USD) différent de celui du second programme "
                                      f"({plafonds.get(nom)!r}) ou décisions différentes : arrêt")
        p2, souple2 = plafond_independant(b["etapes"], b["plafond_usd"], self.budget.journal, cons, nom)
        if centimes(p2) != centimes(plafond) or souple2 != detail["souple"]:
            raise PlafondDeRelaisFaux(f"11a : plafond dur de {nom} ({plafond:.2f} USD, souple={detail['souple']}) différent de la "
                                      f"formule indépendante ({p2:.2f} USD, souple={souple2}) : arrêt")
        for f in sorted(self.ad):
            try:
                accuse = self.portes[f].transmettre(nom, plafond)
            except Exception as e:  # noqa: BLE001 — toute impossibilité de recevoir le plafond est un refus A15, motif dit
                raise RelaisSansPlafond(f"A15 : relais « {f} » incapable de recevoir le plafond dur de l'étape {nom} "
                                        f"({plafond:.2f} USD) : {type(e).__name__} : {str(e)[:300]}") from e
            if not isinstance(accuse, dict) or accuse.get("etape") != nom or not isinstance(accuse.get("plafond_usd"), (int, float)) \
                    or centimes(accuse["plafond_usd"]) != centimes(plafond):
                raise RelaisSansPlafond(f"A15 : accusé du relais « {f} » différent du plafond dur de {nom} ({plafond:.2f} USD) : "
                                        f"{accuse!r}")
            self.transmissions.append({"etape": nom, "fournisseur": f, "plafond_usd": plafond, "par": str(accuse.get("par"))[:120]})
            self.coffre.noter_consommation(nom, "plafond-relais", 0.0, fournisseur=f, plafond_dur_usd=plafond,
                                           souple=bool(detail["souple"]), par=str(accuse.get("par"))[:120])

    def jouer_etape(self, nom, fonction):
        decision, detail = self.budget.avant_etape(nom)
        self.ev("etape", etape=nom, decision=decision, **{k: v for k, v in detail.items() if k != "motif"})
        if decision != JOUER:
            self.etapes_etat[nom] = decision
            return decision
        try:
            self._verifier_et_transmettre(nom, detail)
        except BaseException as e:
            self.etapes_etat[nom] = self.budget.refuser_lancement(nom, f"{type(e).__name__} : {e}")
            raise
        etat = {"cout": 0.0, "reste": detail["plafond_dur_usd"], "coupee": False, "etape": nom,
                "plafond_dur_usd": detail["plafond_dur_usd"]}
        try:
            fonction(etat)
        finally:
            if etat["coupee"]:
                self.coffre.noter_consommation(nom, "coupure", 0.0, coupure=True)
            if "lue_reduite" in etat:
                self.coffre.noter_consommation(nom, "m6-lue-reduite", 0.0, lue_reduite=etat["lue_reduite"] is True)
            res = self.budget.apres_etape(nom, etat["cout"], coupee=etat["coupee"], lue_reduite=etat.get("lue_reduite"))
            if res == "jouee":
                trop = {role: part for role, part in self.suivi.depassements_a14().items() if nom in self.suivi.roles[role]["etapes"]}
                if trop:
                    motif = "A14 : part d'appels sans sortie exploitable au-delà du seuil : " + ", ".join(
                        f"{k} {v:.2f}" for k, v in sorted(trop.items()))
                    self.coffre.noter_consommation(nom, "a14", 0.0, technique=True, motif=motif)
                    res = self.budget.marquer_technique(nom, motif)
            self.etapes_etat[nom] = res
        if self.budget.cumul > float(self.conf["budget"]["plafond_usd"]) + EPS:
            raise CumulAuDelaDeS17(f"11a : cumul {self.budget.cumul:.6f} USD au-delà de S17 après l'étape {nom} (un relais n'a pas "
                                   "tenu son plafond dur) : arrêt")
        return self.etapes_etat[nom]


__all__ = ("OrchestreV56", "ArretParSignal", "ArretSurSignal", "motif_arret", "RelaisSansPlafond", "LectureNonInterdite",
           "PlafondDeRelaisFaux", "CumulAuDelaDeS17")
