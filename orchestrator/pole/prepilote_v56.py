"""Pré-pilote de la course 2, version 56 — au-dessus de `prepilote_v55` (inchangé, R12) et de la génération v56. Spécification :
le préenregistrement du pré-pilote nommé et vérifié au lancement (`specification`, CL20-03), écrit au brouillon 10 à ce jour.

| constat | correction |
|---|---|
| CL20-02 | budget v56 (relais du devis v6) par le noyau ; **É9 entière** vérifie d'abord les fiches de la réduction stratifiée (liste scellée `prepilote.anteriorite.liste_reduite`), puis les autres ; coupée par son relais fixe, elle est **lue réduite** si toutes les fiches de la réduction l'ont été avant la coupure (appel lancé et rendu), sinon « non mesuré (budget) » (`etat["lue_reduite"]`, noté au journal de consommations) |
| CL20-04 | arrêt propre sur signal ; tout arrêt pose `arret` ; le pré-pilote écrit aussi `empreintes-sortie.txt` et `consommations.json` |
| CL20-05 | fusions d'É7c : seules les complètes sont ouvertes après É9 ; les autres archivées (`fusions-inachevees.json`) |
| CL20-07 | `prepilote.d_i` exigé ; la v56 ne code que (1) : (2) et (3) **refusés** à la configuration (le code jouerait (1) sans le dire) |
| CL20-08 | D-g (b) : les fiches de M6b sont **écrites par le rédacteur en É1** à partir de `prepilote.m6b.nombre` sources tirées (tâche `pp2-m6b`) dans la liste scellée `prepilote.m6b.liste_sources` (DEP2c : chaque source porte titre, auteurs, identifiant, extrait servi au rédacteur, empreinte du PDF) ; fiches scellées (`temoins/m6b-fiches.json`), clé fiche → source au coffre ; É9b les vérifie, garde de la ligne 31 (source hors de l'entrée) sur le flux complet ; les pièces `m6b.fiches` / `m6b.sources` (fiches écrites hors du pré-pilote) sont refusées |
| CL20-09 | `_exempts_a8` retiré à la fin d'É3 (`finally`) : plus aucune copie de la clé des classes en mémoire après É3 (la docstring v55 disait « après É1 » : faux pour É3) |
| CL20-13 | S6 : la **numérotation de liste** (1 ou 2 chiffres suivis de « . » ou « ) » en début de ligne, après tiret ou puce, ou après « : » ou « ; ») est comptée à part (`numerotation`), jamais comme nombre ajouté ; le maximum de nombres ajoutés reste à Lazar (configuration) |
| N5 (CL19-03) | interrupteur `prepilote.a21_lecture` **en attente de N5** : absent ou « programme_journalise » = comportement v55 (lectures par programme journalisées en É3 et É5) ; « stricte » = aucun lancement (la boîte d'É5 et l'exemption A8 hors de l'orchestrateur ne sont pas codées) |
"""

import json
import os
import re

from . import fiches_v54 as fv
from . import prepilote_v54 as p54
from . import prepilote_v55 as p55
from .budget_v56 import REGLE
from .configuration_v53 import ConfigurationRefusee, chemin_piece, entier, texte_piece
from .course2_v56 import GenerationV56
from .noyau_v54 import NoeudArret
from .noyau_v56 import ArretSurSignal, motif_arret
from .outils import ecrire_json_scelle, extraire_bloc_json, verifier_scelle

VERSION = "pre-pilote-course-2-v56"
PLAN, ROLES, CLASSES_N, ITEM_DE = p55.PLAN, p55.ROLES, p55.CLASSES_N, p55.ITEM_DE
EtageUnAbsent = p55.EtageUnAbsent
ATTESTATION_V1 = p55.ATTESTATION_V1
ROLE_E3, ROLE_E5 = p55.ROLE_E3, p55.ROLE_E5
A21_MODES = ("programme_journalise", "stricte")
A21_DEFAUT = "programme_journalise"


# --- S6, numérotation de liste (CL20-13) --------------------------------------------------------------------------------------

NUMEROTATION = re.compile(r"(?m)(?:^[ \t]*(?:[-*•][ \t]*)?|(?<=[:;][ \t]))\(?\d{1,2}[.)](?=\s)")


def controle_ancres_v56(rendu, squelette):
    """S6 v55 (bornes, couples, nombres ajoutés) ; la numérotation de liste est comptée à part et n'est pas un nombre ajouté."""
    brut = fv.texte_plat(rendu)
    numeros = NUMEROTATION.findall(brut)
    texte = p55._plat(brut)
    ancres, couples = squelette["ancres"], squelette["couples"]
    present = lambda a: p55.motif_ancre(a).search(texte) is not None  # noqa: E731
    part_a = sum(1 for a in ancres if present(a)) / len(ancres) if ancres else 1.0
    part_c = sum(1 for a, b in couples if present(a) and present(b)) / len(couples) if couples else 1.0
    permis = set().union(*(p55.nombres(x) for x in list(ancres) + [y for c in couples for y in c])) if (ancres or couples) else set()
    ajoutes = sorted(p55.nombres(NUMEROTATION.sub(" ", brut)) - permis)
    return {"ancres": round(part_a, 6), "couples": round(part_c, 6), "nombres_ajoutes": len(ajoutes), "numerotation": len(numeros)}


# --- configuration -----------------------------------------------------------------------------------------------------------


def lire_liste_sources_m6b(conf):
    """DEP2c : liste scellée des sources de M6b (session-depot) ; rend la liste vérifiée."""
    m = conf["prepilote"]["m6b"]
    nom = m.get("liste_sources")
    if not isinstance(nom, str) or nom not in (conf.get("pieces") or {}):
        raise ConfigurationRefusee("prepilote.m6b.liste_sources : pièce scellée exigée (DEP2c, tenue par session-depot)")
    if not verifier_scelle(chemin_piece(conf, conf["pieces"][nom]["chemin"])):
        raise ConfigurationRefusee("prepilote.m6b.liste_sources : liste non scellée (compagnon .sha256 absent ou faux)")
    sources = json.loads(texte_piece(conf, nom)).get("sources")
    if not isinstance(sources, list):
        raise ConfigurationRefusee("liste des sources de M6b : {\"sources\": [...]} exigé")
    idents = []
    for s in sources:
        if not (isinstance(s, dict) and isinstance(s.get("ident"), str) and s["ident"] and isinstance(s.get("titre"), str) and s["titre"]
                and isinstance(s.get("identifiant"), str) and isinstance(s.get("extrait"), str) and s["extrait"].strip()
                and isinstance(s.get("auteurs"), list) and all(isinstance(a, str) for a in s["auteurs"])
                and isinstance(s.get("pdf_sha256"), str) and re.fullmatch(r"[0-9a-f]{64}", s["pdf_sha256"])):
            raise ConfigurationRefusee("source de M6b : {ident, titre, auteurs, identifiant, extrait, pdf_sha256} exigés")
        idents.append(s["ident"])
    if len(set(idents)) != len(idents) or len(sources) < m["nombre"]:
        raise ConfigurationRefusee(f"liste des sources de M6b : identifiants uniques et au moins {m['nombre']} sources exigés")
    return sources


def lire_attestation_v1_v56(conf):
    t = conf["prepilote"]["temoins"]
    nom = t.get("sortie_v1")
    if not isinstance(nom, str) or nom not in (conf.get("pieces") or {}):
        raise ConfigurationRefusee("temoins.version = 2 : pièce prepilote.temoins.sortie_v1 exigée (attestation scellée du nœud "
                                   "É5bis de la version 1, écrite par le pré-pilote ; jamais une valeur de configuration seule)")
    if not verifier_scelle(chemin_piece(conf, conf["pieces"][nom]["chemin"])):
        raise ConfigurationRefusee("temoins.sortie_v1 : attestation non scellée")
    att = json.loads(texte_piece(conf, nom))
    if att.get("version_temoins_epuisee") != 1 or att.get("noeud") != "É5bis" or att.get("version") not in (p55.VERSION, VERSION):
        raise ConfigurationRefusee("temoins.sortie_v1 : attestation d'un nœud É5bis de la version 1 (pré-pilote v55 ou v56) exigée")
    return att


def verifier_configuration_pre_pilote_v56(conf):
    pp = conf.get("prepilote")
    manques = []
    if isinstance(pp, dict):
        d_i = pp.get("d_i")
        if isinstance(d_i, bool) or d_i not in (1, 2, 3):
            manques.append("prepilote.d_i ∈ {1, 2, 3} exigé (plan des fonds, décision de Lazar, aucun défaut)")
        elif d_i != 1:
            manques.append(f"prepilote.d_i = {d_i} : variante non codée en v56 ((2) : 4 rendus appariés, tâche pp2-pa, É3, É4, É8 ; "
                           "(3) : 24 fonds dont 4 doublés) — le code jouerait (1) sans le dire (CL20-07) : aucun lancement")
        a21 = pp.get("a21_lecture", A21_DEFAUT)
        if a21 not in A21_MODES:
            manques.append(f"prepilote.a21_lecture ∈ {A21_MODES} (absent : « {A21_DEFAUT} », comportement v55 ; en attente de N5)")
        elif a21 == "stricte":
            manques.append("prepilote.a21_lecture = « stricte » (en attente de N5) : aucune lecture de la clé des classes par "
                           "programme avant la fin d'É9 — la boîte d'É5 et l'exemption A8 tenues hors de l'orchestrateur ne sont "
                           "pas codées en v56 : aucun lancement")
        if pp.get("d_g") == "b":
            m = pp.get("m6b")
            if not isinstance(m, dict):
                manques.append("prepilote.m6b manquant (D-g = b)")
            else:
                for k in ("fiches", "sources"):
                    if k in m:
                        manques.append(f"prepilote.m6b.{k} : fiches écrites hors du pré-pilote refusées (brouillon 10 : rédacteur en "
                                       "É1, tirage pp2-m6b sur la liste scellée, CL20-08)")
                for k in ("liste_sources", "consigne_redaction", "consigne"):
                    if not isinstance(m.get(k), str) or m[k] not in (conf.get("pieces") or {}):
                        manques.append(f"prepilote.m6b.{k} : pièce exigée (aucun défaut)")
                for k in ("nombre", "references_par_fiche"):
                    if not entier(m.get(k), 1):
                        manques.append(f"prepilote.m6b.{k} : entier ≥ 1 exigé (aucun défaut)")
    if manques:
        raise ConfigurationRefusee("configuration du pré-pilote v56 refusée :\n- " + "\n- ".join(manques))
    p54.verifier_configuration_pre_pilote(conf)
    manques = []
    if not entier(pp["s6"].get("nombres_ajoutes_max"), 0):
        manques.append("prepilote.s6.nombres_ajoutes_max : entier ≥ 0 exigé (CL19-07, aucun défaut)")
    if pp["temoins"].get("version") not in (1, 2):
        manques.append("prepilote.temoins.version ∈ {1, 2} exigé (jamais une troisième)")
    if manques:
        raise ConfigurationRefusee("configuration du pré-pilote v56 refusée :\n- " + "\n- ".join(manques))
    p55.lire_liste_reduite(conf)
    if pp["temoins"]["version"] == 2:
        lire_attestation_v1_v56(conf)
    if pp["d_g"] == "b":
        lire_liste_sources_m6b(conf)
    return True


def valider_fiche_m6b(fiche, references):
    if not isinstance(fiche, dict):
        return "réponse du rédacteur illisible (bloc fiche_m6b absent)"
    refs = fiche.get("references")
    if not isinstance(refs, list) or len(refs) != references or not all(isinstance(r, dict) and isinstance(r.get("titre"), str)
                                                                         and r["titre"].strip() for r in refs):
        return f"fiche de M6b : exactement {references} antériorités réelles {{titre, …}} exigées"
    return None


# --- le pré-pilote -----------------------------------------------------------------------------------------------------------


class PrePiloteV56(p55.PrePiloteV55, GenerationV56):
    @staticmethod
    def verifier_configuration(conf):
        return verifier_configuration_pre_pilote_v56(conf)

    def __init__(self, conf, sortie, adaptateurs, *, go=None, horloge=None, etage1=None, gardes_e0=None, racine_sessions=None,
                 portes=None, specification=None):
        self._portes_demandees = portes
        self._specification_demandee = specification
        super().__init__(conf, sortie, adaptateurs, go=go, horloge=horloge, etage1=etage1, gardes_e0=gardes_e0,
                         racine_sessions=racine_sessions)
        self.m6b_fiches, self._sources_m6b = [], {}

    # --- É1 : fiches de M6b écrites par le rédacteur (CL20-08) ----------------------------------------------------------------

    def etape_e1_redacteur(self, etat):
        super().etape_e1_redacteur(etat)
        if self.pp["d_g"] == "b":
            self._ecrire_m6b(etat)

    def _ecrire_m6b(self, etat):
        m, r = self.pp["m6b"], self.pp["redacteur"]
        ordre = sorted(lire_liste_sources_m6b(self.conf), key=lambda s: s["ident"])
        g = self.graines.generateur(self.tache("m6b"))  # pp2-m6b (brouillon 10, graines)
        tirees = [ordre[int(i)] for i in g.permutation(len(ordre))][: m["nombre"]]
        consigne = self.piece(m["consigne_redaction"])
        cle = {}
        for k, s in enumerate(tirees):
            servi = {"titre": s["titre"], "auteurs": s["auteurs"], "identifiant": s["identifiant"], "extrait": s["extrait"]}
            entree = consigne.rstrip() + "\n\n## Source M6b\n```json\n" + json.dumps(servi, ensure_ascii=False, indent=1) + "\n```\n"
            a = self.appel(etat, role=r["etiquette"], role_kit="proposeur_ideation", fournisseur=r["fournisseur"], modele=r["modele"],
                           consigne=entree, plafond_role="redacteur", session=("e1", "m6b", k),
                           lire=lambda t: extraire_bloc_json(t, "fiche_m6b"))
            fiche = (a["lu"] or {}).get("fiche_m6b") if a else None
            motif = valider_fiche_m6b(fiche, m["references_par_fiche"])
            if motif:
                self.ev("m6b-fiche-non-ecrite", rang=k, motif=motif[:200])
                continue
            ident = "m" + self.graines.jeton_opaque(self.tache("ident-m6b", k), 5)
            self.m6b_fiches.append(dict({c: v for c, v in fiche.items() if c != "ident"}, ident=ident))
            self._sources_m6b[ident] = {"titre": s["titre"], "auteurs": list(s["auteurs"]), "identifiant": s["identifiant"]}
            cle[ident] = s["ident"]
        ecrire_json_scelle(os.path.join(self.sortie, "temoins", "m6b-fiches.json"), self.m6b_fiches)
        self.coffre.deposer(self.tache("cle-m6b"), cle)
        self.ev("m6b-ecrites", fiches=len(self.m6b_fiches), tirees=len(tirees))

    # --- É3 : aucune copie de la clé après l'étape (CL20-09) ; S6 (CL20-13) ---------------------------------------------------

    def etape_e3_rendus(self, etat):
        try:
            super().etape_e3_rendus(etat)
        finally:
            self.__dict__.pop("_exempts_a8", None)

    def _rendre(self, etat, f, essai):
        m = self.pp["metteurs"][f["metteur"]]
        sq = self.squelettes[f["ident"]]
        corps = json.dumps({"ancres": sq["ancres"], "couples": sq["couples"]}, ensure_ascii=False, indent=1)
        entree = self.piece(self.pp["consigne_rendu"]).rstrip() + "\n\n## Éléments à mettre en forme\n```json\n" + corps + "\n```\n"
        fv.garde(entree, self.interdites, self.a4_mode, "l'entrée complète d'un rendu (consigne comprise)")
        a = self.appel(etat, role=m["etiquette"], role_kit="proposeur_ideation", fournisseur=m["fournisseur"], modele=m["modele"],
                       consigne=entree, plafond_role="metteur", session=("e3", f["ident"], essai), lire=p54._fiches_ou_none)
        if a is None or not a["lu"] or len(a["lu"]) != 1:
            return None, "rendu sans sortie exploitable"
        try:
            fiche = fv.preparer(a["lu"][0], self.conf["champs_fiche"], ident=f["ident"], case=self.conf["cases"][0],
                                fournisseur=f["metteur"], passe="rendu", origine="rendu")
        except fv.FicheRefusee as e:
            return None, f"rendu refusé : {e}"
        s6 = controle_ancres_v56(fiche, sq)
        if f["ident"] not in self._exempts_a8:
            ok_l, n = p55.controle_longueur(fiche, self.pp["a8"]["min"], self.pp["a8"]["max"])
            if not ok_l:
                return None, f"A8 : longueur {n} hors de [{self.pp['a8']['min']} ; {self.pp['a8']['max']}]"
        if s6["ancres"] + 1e-12 < self.pp["s6"]["ancres_min"] or s6["couples"] + 1e-12 < self.pp["s6"]["couples_min"]:
            return None, f"A5 : fidélité sous S6 (ancres {s6['ancres']}, couples {s6['couples']})"
        if s6["nombres_ajoutes"] > self.pp["s6"]["nombres_ajoutes_max"]:
            return None, f"A5 : {s6['nombres_ajoutes']} nombre(s) ajouté(s) au rendu > {self.pp['s6']['nombres_ajoutes_max']} (S6)"
        fiche["meta"]["s6"] = s6
        return fiche, None

    # --- É9, É9b ------------------------------------------------------------------------------------------------------------

    def _verifier_fiches(self, etat, fiches, lot, sources=None):
        """Comme la v54 ; rend l'ensemble des fiches dont l'appel du vérificateur a été lancé et rendu (pour M6 entière coupée)."""
        v = self.pp["anteriorite"]["verificateur"]
        consigne = self.piece(self.pp["anteriorite"]["consigne"] if lot == "e9" else self.pp["m6b"]["consigne"])
        verifiees = set()
        for fiche in fiches:
            corps = json.dumps(fiche, ensure_ascii=False, indent=1)
            entree = consigne.rstrip() + "\n\n## La fiche\n```json\n" + corps + "\n```\n"
            if sources is not None:
                if fiche["ident"] not in sources:
                    raise NoeudArret(f"M6b : source de la fiche {fiche['ident']} inconnue (clé d'É1 perdue) : arrêt")
                ok, motif = p55.garde_m6b(entree, sources[fiche["ident"]])
                if not ok:
                    self.ev("m6b-fiche-arretee", ident=fiche["ident"], motif=motif)
                    continue
            a = self.appel(etat, role=v["etiquette"], role_kit=v["role_kit"], fournisseur=v["fournisseur"], modele=v["modele"],
                           consigne=entree, plafond_role="verificateur", session=(lot, fiche["ident"]),
                           lire=lambda t: extraire_bloc_json(t, "references"))
            if a is not None:
                verifiees.add(fiche["ident"])
            self.coffre.deposer(f"verdicts-{lot}-{fiche['ident']}", {"ident": fiche["ident"], "verdict": a["lu"] if a else None})
        return verifiees

    def etape_e9_anteriorite(self, etat):
        an = self.pp["anteriorite"]
        fiches = json.loads(self.piece(an["fiches"]))["fiches"]
        reduction = p55.lire_liste_reduite(self.conf)  # liste scellée (pp2-reduction-e9, session-depot) ; jamais la clé d'antériorité
        par_ident = {f["ident"]: f for f in fiches}
        premieres = [par_ident[i] for i in reduction]
        if self.budget.etapes["e9_anteriorite"]["reduite_appliquee"]:
            self.ev("e9-reduite", fiches=len(premieres), source="liste de réduction scellée")
            self._verifier_fiches(etat, premieres, "e9")
            return
        ordre = premieres + [f for f in fiches if f["ident"] not in set(reduction)]
        verifiees = self._verifier_fiches(etat, ordre, "e9")
        etat["lue_reduite"] = set(reduction) <= verifiees
        self.ev("e9-entiere", fiches=len(ordre), reduction_d_abord=len(premieres), reduction_verifiee=etat["lue_reduite"])

    def etape_e9b_m6b(self, etat):
        chemin = os.path.join(self.sortie, "temoins", "m6b-fiches.json")
        if not verifier_scelle(chemin):
            raise NoeudArret("A13 : fiches de M6b scellées à É1 absentes ou modifiées avant É9b : arrêt")
        self._verifier_fiches(etat, self.m6b_fiches, "e9b", sources=self._sources_m6b)

    # --- exécution -----------------------------------------------------------------------------------------------------------

    def executer(self):
        self.etage1_resultats = {}
        resultat = None
        a21 = self.pp.get("a21_lecture", A21_DEFAUT)
        with ArretSurSignal() as garde:
            self.garde_signal = garde
            try:
                ecrire_json_scelle(os.path.join(self.sortie, "manifeste-depart.json"), {
                    "version": VERSION, "specification": self.specification, "configuration_sha256": self.conf["empreinte_configuration"],
                    "go": self.go, "plan": list(self.plan), "bras": self.bras_decl, "prefixe_taches": self.prefixe,
                    "gardes_e0": self.gardes_e0, "lectures": {k: self.pp[k] for k in ("L1", "L2", "d_g", "d_i")},
                    "regle_depense": REGLE, "relais": self.description_portes(), "lecture_interdite_kit": self.lecture_interdite,
                    "m4": "non étalonné (M4 sans témoins concrets : aucun lot du bras d'attaque servi)",
                    "m6b": ("fiches écrites par le rédacteur en É1 (tirage pp2-m6b dans la liste scellée DEP2c), vérifiées en É9b"
                            if self.pp["d_g"] == "b" else "sans objet (D-g a)"),
                    "lectures_par_programme_permises": sorted([n, r] for n, r in self.coffre.lectures_permises),
                    "a21_lecture": f"{a21} (interrupteur en attente de N5 ; défaut : comportement v55)",
                    "sessions": {"base": self.base_sessions, "regle": "hors de la sortie (CL19-04)"},
                    "regle_de_lecture": "aucun verdict d'É6/É7 ni clé ouvert avant la fin d'É9 ; deux lectures par programme de la clé "
                                        "des classes (É3, É5), journalisées au coffre, comptes seulement (A21 : N5 ouvert) ; au nœud, "
                                        "rien n'est ouvert (O12)"})
                for nom in self.plan:
                    self.jouer_etape(nom, getattr(self, "etape_" + nom))
                    if not self.c13_ou_noeud(nom):
                        break
                self._deposer_cles_une_fois()
                if self.noeud:
                    raise NoeudArret(self.noeud)
                for i, f in sorted(self.rendus.items()):
                    self.etage1_resultats[i] = bool(self.etage1.signaler(f))
                self.coffre.deposer(self.tache("etage1"), self.etage1_resultats)
                self.coffre.declarer_fin_e9()  # après É9 et É9b
                verdicts = self.ouvrir_verdicts(sorted(set(self.rendus) | {f["ident"] for f in self.fusions_completes()}))
                resultat = self._analyse_m1(verdicts)
                ecrire_json_scelle(os.path.join(self.sortie, "analyse-m1.json"), resultat)
            except NoeudArret as e:
                self.noeud = self.noeud or str(e)
                self.ev("noeud-rien-ouvert", regle="O12 : ni fin d'É9, ni clé, ni verdict, ni analyse ; main rendue à Lazar")
                self._deposer_cles_une_fois()
                if "É5bis" in self.noeud and self.pp["temoins"]["version"] == 1:
                    ecrire_json_scelle(os.path.join(self.sortie, ATTESTATION_V1), {
                        "version": VERSION, "version_temoins_epuisee": 1, "noeud": "É5bis",
                        "configuration_sha256": self.conf["empreinte_configuration"]})
                raise
            except BaseException as e:
                self.arret = motif_arret(e)
                raise
            finally:
                garde.nettoyage()
                self.aiguilleur.sceller()
                self.ecrire_fin_commune({
                    "version": VERSION, "arret": self.arret, "noeud": self.noeud, "evenements": self.evenements,
                    "etapes": self.etapes_etat, "budget": self.budget.etat(), "graines": self.graines.manifeste(),
                    "coffre": self.coffre.journal(), "suivi_roles": self.suivi.etat(), "bras": self.bras_decl,
                    "non_produits": self.non_produits, "exclus": self.exclus, "exclus_techniques": self.exclus_techniques,
                    "exclues_a4": self.exclues_a4, "rendus": len(self.rendus), "fonds": len(self.fonds),
                    "m5": {k: len(v) for k, v in self.m5.items()}, "e5": self.decisions_e5,
                    "m6b": {"fiches_ecrites_e1": len(self.m6b_fiches)},
                    "juges_absents": self.absents_juges, "modele_servi_juges": self.modele_servi_juges})
        return resultat


__all__ = ("PrePiloteV56", "controle_ancres_v56", "verifier_configuration_pre_pilote_v56", "lire_liste_sources_m6b",
           "lire_attestation_v1_v56", "valider_fiche_m6b", "EtageUnAbsent", "PLAN", "ATTESTATION_V1", "A21_MODES", "NUMEROTATION")
