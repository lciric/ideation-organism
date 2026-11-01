"""Génération et course 2, version 56 — au-dessus de `course2_v55` (inchangé, R12). Contre-lecture CL20.

| constat | correction |
|---|---|
| CL20-05 | une fusion n'est **complète** qu'avec son passeport **et** tous ses verdicts, dans une étape des fusions **jouée** (une étape retirée ou non mesurée ne rend aucune fusion) (présence notée par `juger`, jamais le contenu) ; seules les fusions complètes entrent au lot (mémoire anti-redite, classement, fiches, héritage, étage) — défaut (b) de D-CL20-2 ; toute fusion non écrite, incohérente (refusée), exclue par A4, sans passeport (aiguillage coupé ou classe hors niveau méthode), non jugée ou jugée en partie est **archivée** dans `fusions-inachevees.json` scellé (rang, cause, contenu s'il existe, empreinte ; jamais le bras), écrit sur tout chemin, jamais relu par le programme ; l'entrée du bisociateur exclut toute fusion |
| CL20-10 | déclaration des bras : Gu-Krenn en mode « substitut » seulement (configuration) ; source absente, à empreinte différente ou illisible → « non produit (source absente) » ; **toute autre exception = erreur interne = arrêt** (`ErreurInterneBras`) ; bras méta : forme des blocs JSON de l'annexe vérifiée d'abord (types), puis lecture v55 ; seuls les refus nommés (`BisociationRefusee`), les fichiers illisibles et le JSON mal formé font « annexe non conforme » ; une pièce modifiée depuis la lecture (A16) est un arrêt |
| CL20-11 | causes de M9 alignées sur le texte : (iii) Gu-Krenn « moins de 2 fiches notables » ; (iv) bras **basique** « moins de 2 fiches étiquetées » ; le bras méta garde les causes de la v54 (« niches indistinctes », « aucune paire éligible ») — la cause v55 « moins de 2 fiches étiquetées » du bras méta, hors texte, est retirée |
| CL20-04 | signal (SIGTERM, SIGINT) : arrêt propre ; tout arrêt (exception de base comprise) pose `arret` ; le manifeste de fin, le rangement des sessions, `consommations.json`, l'archive des fusions et `empreintes-sortie.txt` sont écrits |
| CL20-03 | manifeste de départ : la spécification vérifiée (préenregistrement scellé et sa contre-lecture), jamais « brouillon 7 » en dur |
| CL20-02, 06, 12 | noyau v56 (`OrchestreV56`) |
"""

import copy
import json
import os
import re

from . import bisociateur_v53 as b53
from . import bisociateur_v54 as b54
from . import bisociateur_v55 as b55
from . import course2_v53 as c53
from . import course2_v54 as c54
from . import course2_v55 as c55
from . import fiches_v54 as fv
from .budget_v56 import REGLE
from .configuration_v53 import ConfigurationRefusee, chemin_piece, texte_piece
from .juges_croises_v53 import classement
from .noyau_v54 import NoeudArret
from .noyau_v56 import ArretSurSignal, OrchestreV56, motif_arret
from .outils import EcrasementInterdit, ecrire_json_scelle, empreinte_objet, lister_fichiers, sha256_fichier

VERSION = "course-2-generation-v56"
ETAPES = c55.ETAPES
CAUSE_SOURCE_ABSENTE, CAUSE_ANNEXE = c55.CAUSE_SOURCE_ABSENTE, c55.CAUSE_ANNEXE
CAUSE_BASIQUE = "non produit (moins de 2 fiches étiquetées)"
CAUSE_GK_NOTABLES = "non produit (moins de 2 fiches notables)"
verifier_bascule_gk, BasculeGuKrennInterdite = c55.verifier_bascule_gk, c55.BasculeGuKrennInterdite
ARCHIVE_FUSIONS = "fusions-inachevees.json"


class ErreurInterneBras(RuntimeError):
    """CL20-10 : exception inattendue à la déclaration d'un bras (défaut de code) : arrêt, jamais « non produit »."""


def verifier_configuration_generation_v56(conf):
    return c54.verifier_configuration_generation_v54(conf)


# --- CL20-10 : déclaration des bras --------------------------------------------------------------------------------------------

_NOMBRE = (int, float)


def _nombre(v):
    return isinstance(v, _NOMBRE) and not isinstance(v, bool)


def forme_annexe_v56(chemin):
    """Types des blocs JSON de l'annexe, avant la lecture v55 : une forme fautive est un refus nommé (`BisociationRefusee`),
    jamais une `KeyError` ou une `TypeError` (qui seraient, après ceci, des défauts de code). Annexe absente : rien ici (la
    lecture le dit)."""
    if not chemin or not os.path.isfile(chemin):
        return False
    with open(chemin, encoding="utf-8") as f:
        texte = f.read()
    blocs = []
    for brut in b55.BLOC.findall(texte):
        try:
            blocs.append(json.loads(brut))
        except ValueError:
            raise b54.BisociationRefusee("A20 : bloc JSON illisible dans l'annexe") from None
    params = [b["parametres_bras_meta"] for b in blocs if isinstance(b, dict) and "parametres_bras_meta" in b]
    if len(params) != 1 or not isinstance(params[0], dict):
        raise b54.BisociationRefusee("A20 : un seul bloc parametres_bras_meta (objet) exigé")
    p = params[0]
    def liste_de_chaines(k):
        return isinstance(p[k], list) and all(isinstance(x, str) and x for x in p[k])
    controles = {"niches": liste_de_chaines, "types_structure": liste_de_chaines,
                 "communication": lambda k: isinstance(p[k], dict) and all(isinstance(a, str) and _nombre(v) for a, v in p[k].items()),
                 "eloignement": lambda k: isinstance(p[k], dict) and all(isinstance(a, str) and _nombre(v) for a, v in p[k].items()),
                 "seuil_communication_faible": lambda k: _nombre(p[k]), "poids": lambda k: _nombre(p[k]),
                 "bande": lambda k: isinstance(p[k], list) and len(p[k]) == 2 and all(_nombre(x) for x in p[k]),
                 "structure_forte": lambda k: isinstance(p[k], dict) and isinstance(p[k].get("nombre_min"), int)
                 and not isinstance(p[k].get("nombre_min"), bool) and isinstance(p[k].get("types"), list)
                 and all(isinstance(x, str) for x in p[k]["types"]),
                 "repli": lambda k: isinstance(p[k], str), "contre_lecture": lambda k: isinstance(p[k], str),
                 "approbation_lazar": lambda k: isinstance(p[k], str),
                 "definitions_niches": lambda k: isinstance(p[k], dict) and all(isinstance(v, str) for v in p[k].values()),
                 "definitions_structures": lambda k: isinstance(p[k], dict) and all(isinstance(v, str) for v in p[k].values()),
                 "accord_min_niche_kappa": lambda k: _nombre(p[k]), "accord_min_structures_jaccard": lambda k: _nombre(p[k])}
    fautives = [k for k, ok in controles.items() if k in p and not ok(k)]
    if fautives:
        raise b54.BisociationRefusee("A20 : forme des paramètres de l'annexe fautive : " + ", ".join(fautives))
    for b in blocs:
        jeu = b.get("jeu_essai_non_vacuite") if isinstance(b, dict) else None
        if jeu is not None and not (isinstance(jeu, dict) and all(isinstance(f, dict) and isinstance(f.get("niche"), str)
                                                                   and isinstance(f.get("structures", []), list) for f in jeu.values())):
            raise b54.BisociationRefusee("A20 : forme du jeu d'essai de non-vacuité fautive")
    return True


REFUS_LEGITIMES = (b54.BisociationRefusee, OSError, UnicodeDecodeError, json.JSONDecodeError)


def declarer_bras_v56(conf):
    """É0 : chaque bras produit, ou « non produit » avec sa cause légitime ; toute autre exception arrête (CL20-10)."""
    b = conf["bisociateur"]
    decl, params = {}, {}
    for bras in b["bras"]:
        try:
            if bras == "gu_krenn":
                g = b["gu_krenn"]
                if g.get("mode") != "substitut":  # la configuration v56 le refuse déjà : jamais « source absente »
                    raise ConfigurationRefusee(f"A19 : mode Gu-Krenn {g.get('mode')!r} non branché en v56 (CL20-10)")
                try:
                    params[bras] = b53.SourceGuKrenn(chemin_piece(conf, g["source"]["chemin"]), g["source"]["sha256"],
                                                     oeuvres_min_vocabulaire=g["oeuvres_min_vocabulaire"], date_debut=g["date_debut"],
                                                     date_coupure=g["date_coupure"], actif_depuis=g["actif_depuis"],
                                                     actif_min_oeuvres=g["actif_min_oeuvres"])
                    decl[bras] = {"produit": True, "mode": "substitut", "source_sha256": g["source"]["sha256"],
                                  "vocabulaire": len(params[bras].vocabulaire)}
                except REFUS_LEGITIMES as e:
                    decl[bras] = {"produit": False, "cause": CAUSE_SOURCE_ABSENTE, "motif": str(e)[:300]}
            elif bras == "meta":
                m = b["meta"]
                try:
                    forme_annexe_v56(chemin_piece(conf, m["annexe"]["chemin"]))
                    texte_lecteur = texte_piece(conf, b["consigne_lecteur_etiquettes"]) if m["definitions"] == "consigne" else None
                    p, jeu = b55.lire_annexe_meta_v55(chemin_piece(conf, m["annexe"]["chemin"]), m["annexe"]["sha256"],
                                                      definitions=m["definitions"], texte_consigne_lecteur=texte_lecteur,
                                                      brouillon_relu=c55._piece_annexe(conf, m, "brouillon_relu"),
                                                      rapport=c55._piece_annexe(conf, m, "rapport_contre_lecture"))
                    non_vacuite = b54.verifier_non_vacuite(p, jeu)
                    n0, n1 = p["niches"][:2]
                    b54.garde_desaccord_v54(b54.score_meta, p, n0, n1, set(), set())
                    p["_s28"] = b54.seuils_s28(p, m["s28"])
                    params[bras] = p
                    decl[bras] = {"produit": True, "annexe_sha256": m["annexe"]["sha256"], "non_vacuite_e0": non_vacuite,
                                  "s28": p["_s28"], "definitions": m["definitions"]}
                except REFUS_LEGITIMES as e:
                    params.pop(bras, None)
                    decl[bras] = {"produit": False, "cause": CAUSE_ANNEXE, "motif": str(e)[:300]}
            else:
                try:
                    liste = json.loads(texte_piece(conf, b["basique"]["liste_concepts"]))
                    if not isinstance(liste, list) or not liste or not all(isinstance(x, str) for x in liste):
                        raise b53.BisociationRefusee("liste fermée des concepts : liste JSON de chaînes attendue")
                    params[bras] = {"liste": liste, "exposant": b["basique"]["exposant"], "decalage": b["basique"]["decalage"]}
                    decl[bras] = {"produit": True, "liste_concepts": len(liste)}
                except REFUS_LEGITIMES as e:
                    decl[bras] = {"produit": False, "cause": "non produit (liste absente)", "motif": str(e)[:300]}
        except ConfigurationRefusee:
            raise  # pièce modifiée depuis la lecture (A16) ou mode non branché : arrêt, jamais « non produit »
        except Exception as e:  # noqa: BLE001 — défaut de code : arrêt, motif dit (CL20-10)
            raise ErreurInterneBras(f"erreur interne à la déclaration du bras {bras} ({type(e).__name__} : {str(e)[:300]}) : "
                                    "arrêt, jamais une absence légitime (CL20-10)") from e
    return decl, params


# --- la génération -------------------------------------------------------------------------------------------------------------


class GenerationV56(OrchestreV56, c55.GenerationV55):
    @staticmethod
    def verifier_configuration(conf):
        return verifier_configuration_generation_v56(conf)

    def __init__(self, conf, sortie, adaptateurs, **kw):
        spec = kw.pop("specification", None)
        super().__init__(conf, sortie, adaptateurs, **kw)
        self.bras_decl, self.bras_params = declarer_bras_v56(conf)
        self.bras_decl_e0 = copy.deepcopy(self.bras_decl)
        self.specification = spec or getattr(self, "_specification_demandee", None) or {
            "conforme": None, "motif": "aucune spécification vérifiée transmise (moteur simulé)"}
        self.fusions_archive = []
        self.garde_signal = None

    # --- CL20-05 : entrée du bisociateur sans fusion ; fusions archivées ------------------------------------------------------

    def _entree_bisociateur(self):
        return [f for f in super()._entree_bisociateur() if f["meta"].get("origine") != "fusion"]

    def _archiver(self, rang, cause, contenu=None):
        entree = {"rang": rang, "cause": cause, "contenu": contenu,
                  "empreinte": empreinte_objet(contenu) if contenu is not None else None}
        self.fusions_archive.append(entree)
        self.ev("fusion-archivee", rang=rang, cause=cause[:200])

    def etape_fusions(self, etat):
        self._etape_fusions = etat["etape"]  # « fusions » (course) ou « e7c_fusions » (pré-pilote)
        a_ecrire = [(b, q) for b in self.ordre_bras for q in self.paires.get(b, [])]
        perm = self._rng_ordre.permutation(len(a_ecrire)) if a_ecrire else []
        a_ecrire = [a_ecrire[int(i)] for i in perm]
        mf = self.conf["bisociateur"]["metteur_fusion"]
        if mf["etiquette"] in self.roles_arretes:
            self.ev("fusions-non-produites", motif="rôle du metteur en fusion arrêté")
            for n in range(len(a_ecrire)):
                self._archiver(n, "non écrite (rôle du metteur en fusion arrêté)")
            return
        cle_bras, nouvelles = {}, []
        consigne_fusion = self.piece(self.conf["bisociateur"]["consigne_fusion"])
        for n, (bras, (ia, ib)) in enumerate(a_ecrire):
            entree = b54.b53.entree_fusion(consigne_fusion, self.fiches[ia], self.fiches[ib], [])
            fv.garde(json.dumps([fv.vue_servie(self.fiches[ia]), fv.vue_servie(self.fiches[ib])], ensure_ascii=False),
                     self.interdites, self.a4_mode, "l'entrée de fusion")
            a = self.appel(etat, role=mf["etiquette"], role_kit="proposeur_ideation", fournisseur=mf["fournisseur"], modele=mf["modele"],
                           consigne=entree, plafond_role="fusion", session=("fusions", n), lire=c54._fiches_ou_none)
            if a is None:
                self._archiver(n, "non écrite (plafond du relais atteint ou rôle arrêté)")
                continue
            if a["lu"] is None:
                self._archiver(n, f"non écrite (sortie inexploitable : {a['motif']})", a["r"].texte_final or None)
                continue
            try:
                if len(a["lu"]) != 1:
                    raise fv.FicheRefusee("une fusion = une fiche")
                ident = "f" + self.graines.jeton_opaque(self.tache("ident-fusion", n), 6)
                f = fv.preparer(a["lu"][0], self.conf["champs_fiche"], ident=ident, case=self.fiches[ia]["meta"]["case"],
                                fournisseur=mf["fournisseur"], passe="fusion", origine="fusion")
            except fv.FicheRefusee as e:
                self.ev("fusion-refusee", rang=n, motif=str(e)[:200])
                self._archiver(n, f"incohérente (refusée : {str(e)[:200]})", a["lu"])
                continue
            f["meta"]["exploratoire"] = True
            f["meta"]["rang_fusion"] = n
            self.fiches[ident] = f
            self.ordre.append(ident)
            nouvelles.append(f)
            cle_bras[ident] = {"bras": bras, "paire": [ia, ib]}
        self.coffre.deposer(self.tache("cle-bras"), cle_bras)
        self.fusions = nouvelles
        self._aiguiller(nouvelles, etat, "fusions")
        self._juger(nouvelles, "fusions", etat)

    def cause_fusion(self, f):
        """None si la fusion est complète (passeport et tous les verdicts présents, étape des fusions jouée), sinon la cause."""
        cause = self._cause_fiche_fusion(f)
        etape = getattr(self, "_etape_fusions", None)
        if etape is not None and self.etapes_etat.get(etape, "jouee") != "jouee":
            return (f"étape des fusions « {self.etapes_etat[etape]} » (coupée par son relais ou non mesurée : rien n'en revient) ; "
                    + (cause or "complète avant la coupure"))
        return cause

    def _cause_fiche_fusion(self, f):
        ident = f["ident"]
        if ident in self.exclues_a4:
            return "exclue par A4 (étiquette interdite)"
        if not self.aiguilleur.a_passeport(f):
            d = self.aiguilleur.decisions.get(ident) or {}
            if d.get("classe") is None:
                return "sans passeport : aiguillage non lancé (plafond du relais atteint, rôle arrêté ou arrêt)"
            return f"sans passeport : classée « {d.get('classe')} » par l'aiguilleur (jamais jugée)"
        pres = self.verdicts_presents.get(ident)
        if not pres or not any(pres.values()):
            return "non jugée (aucun appel de juge : plafond du relais atteint, rôle arrêté ou arrêt)"
        manquent = [j for j, v in pres.items() if not v]
        if manquent or len(pres) != len(self.conf["juges"]):
            return f"jugée en partie ({sum(pres.values())} verdict(s) sur {len(self.conf['juges'])})"
        return None

    def fusions_completes(self):
        return [f for f in self.fusions if self.cause_fusion(f) is None]

    def lot_mesure(self):
        """Fiches munies d'un passeport, fusions inachevées exclues (CL20-05)."""
        completes = {f["ident"] for f in self.fusions_completes()}
        return [self.fiches[i] for i in self.ordre if self.aiguilleur.a_passeport(self.fiches[i])
                and (self.fiches[i]["meta"].get("origine") != "fusion" or i in completes)]

    def ecrire_archive_fusions(self):
        archive = list(self.fusions_archive)
        for f in self.fusions:
            cause = self.cause_fusion(f)
            if cause is not None:
                archive.append({"rang": f["meta"].get("rang_fusion"), "ident": f["ident"], "cause": cause, "contenu": f["contenu"],
                                "empreinte": f["empreinte"]})
        ecrire_json_scelle(os.path.join(self.sortie, ARCHIVE_FUSIONS), {
            "version": VERSION, "regle": ("fusion complète = passeport et tous ses verdicts ; les autres sont archivées ici, hors "
                                          "de l'héritage, de la mémoire, du classement, de l'étage et de l'entrée du bisociateur "
                                          "(CL20-05) ; jamais relu par le programme ; le bras n'y figure pas (A21)"),
            "fusions": archive})
        causes = {}
        for x in archive:
            k = x["cause"].split(" (")[0].split(" « ")[0]
            causes[k] = causes.get(k, 0) + 1
        return {"completes": len(self.fusions_completes()), "inachevees": len(archive), "causes": causes, "archive": ARCHIVE_FUSIONS,
                "etiquette": "exploratoire (registre seulement) ; seules les complètes reviennent (défaut (b) de D-CL20-2)"}

    # --- CL20-11 : causes de M9 ----------------------------------------------------------------------------------------------

    def _notes(self, eligibles):
        notes, departage, causes = c54.GenerationV54._notes(self, eligibles)  # causes v54 ; la cause méta hors texte de la v55 retirée
        l1n, l2n = (l["etiquette"] for l in self.conf["lecteurs_etiquettes"])
        if "basique" in self.etiquettes:
            l1, l2 = self.etiquettes["basique"][l1n], self.etiquettes["basique"][l2n]
            etiquetees = [f for f in eligibles if set(l1.get(f["ident"], [])) | set(l2.get(f["ident"], []))]
            if len(etiquetees) < 2:  # (iv)
                notes["basique"], departage["basique"] = {}, {}
                causes["basique"] = CAUSE_BASIQUE
        if "gu_krenn" in self.etiquettes and not notes.get("gu_krenn"):  # (iii)
            l1, l2 = self.etiquettes["gu_krenn"][l1n], self.etiquettes["gu_krenn"][l2n]
            notables = [f for f in eligibles if len(set(l1.get(f["ident"], [])) | set(l2.get(f["ident"], []))) >= 2]
            causes["gu_krenn"] = CAUSE_GK_NOTABLES if len(notables) < 2 else "non produit (aucune paire éligible)"
        return notes, departage, causes

    # --- l'exécution ---------------------------------------------------------------------------------------------------------

    def manifeste_depart_v56(self):
        return {"version": VERSION, "generation": self.numero, "configuration_sha256": self.conf["empreinte_configuration"],
                "specification": self.specification, "go": self.go, "bras": self.bras_decl, "etapes": list(ETAPES),
                "prefixe_taches": self.prefixe, "regle_depense": REGLE, "relais": self.description_portes(),
                "lecture_interdite_kit": self.lecture_interdite,
                "choix_v54": {k: c53._get(self.conf, k) for k in ("budget.portee_plafond", "garde_kimi.refus_aiguilleur",
                                                                   "garde_kimi.arret_metteur_fusion", "tableau.juger_passe_tableau",
                                                                   "bisociateur.fournisseurs_entree", "a4.mode", "a4.action")},
                "adaptateurs": {k: (a.description() if hasattr(a, "description") else type(a).__name__) for k, a in self.ad.items()},
                "regle_de_lecture": "aucun verdict ni clé lu avant la fin de la phase de mesure (A21) ; au nœud, rien n'est ouvert (O12)",
                "fusions": "seules les fusions complètes (passeport et tous les verdicts) reviennent ; les autres sont archivées (CL20-05)",
                "sessions": {"base": self.base_sessions, "regle": "hors de la sortie (CL19-04)"},
                "manifeste_r9": c53.manifeste_r9(self.graines)}

    def ecrire_fin_commune(self, fin):
        """Sur tout chemin : sessions rangées, consommations, archive des fusions, manifeste de fin, empreintes de sortie."""
        rangement = self.ranger_sessions()
        ecrire_json_scelle(os.path.join(self.sortie, "consommations.json"), {
            "version": VERSION, "regle": "M7 : une entrée par appel, marques de plafond transmis, de coupure, de lecture réduite, "
                                         "d'A14 ; montants seulement (A21) ; rejouable par budget_v56.rejouer_consommations_v56",
            "consommations": self.coffre._consommations})
        fin["fusions"] = self.ecrire_archive_fusions()
        fin["sessions"] = {"base": self.base_sessions, "nombre": len(self.sessions), "rangement": rangement}
        fin["signaux"] = self.garde_signal.etat() if self.garde_signal is not None else None
        fin["relais"] = {"transmissions": len(self.transmissions), "portes": self.description_portes()}
        fin["roles_arretes_a2"] = self.roles_arretes_a2
        ecrire_json_scelle(os.path.join(self.sortie, "manifeste-fin.json"), fin)
        with open(os.path.join(self.sortie, "empreintes-sortie.txt"), "w", encoding="utf-8") as g:
            for rel in lister_fichiers(self.sortie):
                if rel != "empreintes-sortie.txt" and not rel.endswith(".sha256"):
                    g.write(f"{sha256_fichier(os.path.join(self.sortie, rel))}  {rel}\n")

    def executer(self):
        resultat = []
        with ArretSurSignal() as garde:
            self.garde_signal = garde
            try:
                ecrire_json_scelle(os.path.join(self.sortie, "manifeste-depart.json"), self.manifeste_depart_v56())
                for nom in ETAPES:
                    self.jouer_etape(nom, getattr(self, "etape_" + nom))
                    if not self.c13_ou_noeud(nom):
                        break
                self.deposer_cles()
                if self.noeud:  # O12 : rien n'est lu de ce qui a été mesuré
                    self.ev("noeud-rien-ouvert", regle="O12 : rejeu de la seule mesure non mesurée sur GO ; rien n'en a été lu")
                    return resultat
                lot = self.lot_mesure()
                ecrire_json_scelle(os.path.join(self.sortie, "memoire.json"), self.memoire.detecter(lot))
                self.coffre.declarer_fin_e9()
                verdicts = self.ouvrir_verdicts([f["ident"] for f in lot])
                ag = self.conf["agregation"]
                resultat = classement(verdicts, ag["regle"], ag.get("q"))
                completes = [f["ident"] for f in self.fusions_completes()]
                ecrire_json_scelle(os.path.join(self.sortie, "classement.json"), {
                    "lignes": [{k: l[k] for k in ("ident", "rang", "notable", "n_notables", "n_presents", "somme_x")}
                               | {"exploratoire": bool(self.fiches[l["ident"]]["meta"].get("exploratoire"))} for l in resultat],
                    "regle_agregation": ag, "fusions_comptees_a_part": completes,
                    "fusions_inachevees": len(self.fusions) - len(completes) + len(self.fusions_archive), "noeud": self.noeud})
                ecrire_json_scelle(os.path.join(self.sortie, "fiches.json"),
                                   {f["ident"]: {"contenu": f["contenu"], "empreinte": f["empreinte"], "meta": f["meta"]} for f in lot})
                self.memoire.ajouter_memoire(lot, self.numero)
            except BaseException as e:
                self.arret = motif_arret(e)
                raise
            finally:
                garde.nettoyage()
                self.aiguilleur.sceller()
                self.ecrire_fin_commune({
                    "version": VERSION, "generation": self.numero, "arret": self.arret, "noeud": self.noeud,
                    "evenements": self.evenements, "etapes": self.etapes_etat, "budget": self.budget.etat(),
                    "graines": self.graines.manifeste(), "coffre": self.coffre.journal(), "garde_kimi": self.garde_kimi.etat(),
                    "roles_arretes": self.roles_arretes, "suivi_roles": self.suivi.etat(), "bras": self.bras_decl,
                    "non_produits": self.non_produits, "c12": b54.compter_c12(self.bras_decl, self.non_produits),
                    "paires": {"nombre": sum(len(v) for v in self.paires.values()), "coffre": self.tache("paires-par-bras")},
                    "desaccord_des_paires": ("lu par paire après le choix, déposé au coffre ; hors score" if getattr(self, "journal_desaccord", None)
                                             else "non lu (aucune paire méta notée ou étape non jouée)"),
                    "refus_lectures": self.refus_lectures, "exclues_a4": self.exclues_a4, "appels_sautes": self.appels_sautes,
                    "juges_absents": self.absents_juges, "modele_servi_juges": self.modele_servi_juges})
        return resultat

    def texte_heritage(self, resultat):
        """Lignes du classement (fusions inachevées absentes du lot, donc du classement) ; vide au nœud."""
        return json.dumps([], ensure_ascii=False) if self.noeud else c54.GenerationV54.texte_heritage(self, resultat)


def executer_course_v56(conf, sortie, adaptateurs, *, nombre_generations, go, etage=None, environnement=None, horloge=None,
                        racine_sessions=None, portes=None, specification=None):
    """Comme la v55 (nœud : ni génération suivante, ni étage), avec `GenerationV56`, la machine jetable v56 (liste blanche) et
    l'arrêt sur signal au niveau de la course (bilan écrit)."""
    from .etage_entre_generations_v53 import preparer_generation
    from .etage_entre_generations_v56 import exiger_machine_jetable_v56, jouer_etage_v56
    if isinstance(nombre_generations, bool) or not isinstance(nombre_generations, int) or nombre_generations < 1:
        raise ConfigurationRefusee("nombre de générations : entier ≥ 1, aucun défaut")
    permis = (conf.get("etage_tests_de_mort") or {}).get("environnement_permis") or ()
    if etage is not None:
        exiger_machine_jetable_v56(environnement, permis_en_plus=permis)
        for c in ("adaptateur", "reglages", "nombre", "tranche_index_sha256", "correspondance", "plafond_etage_usd"):
            if c not in etage:
                raise ConfigurationRefusee(f"étage entre générations : {c} manquant (aucun défaut)")
    if os.path.exists(sortie):
        raise EcrasementInterdit(f"sortie {sortie} déjà présente (R12)")
    os.makedirs(sortie)
    memoire, heritage, bilan, noeud, arret = None, None, [], None, None
    with ArretSurSignal() as garde:
        try:
            for g in range(1, nombre_generations + 1):
                rs = None if racine_sessions is None else os.path.join(racine_sessions, f"generation-{g}")
                gen = GenerationV56(conf, os.path.join(sortie, f"generation-{g}"), adaptateurs, numero=g, memoire=memoire,
                                    heritage_texte=heritage, go=go, horloge=horloge, racine_sessions=rs, portes=portes,
                                    specification=specification)
                resultat = gen.executer()
                ligne = {"generation": g, "fiches_classees": len(resultat), "notables": sum(l["notable"] for l in resultat),
                         "c13_satisfaite": gen.budget.etat()["c13_satisfaite"], "noeud": gen.noeud}
                if gen.noeud:
                    noeud = f"génération {g} : {gen.noeud}"
                    bilan.append(ligne)
                    break
                memoire, heritage = gen.memoire, gen.texte_heritage(resultat)
                if etage is not None and g < nombre_generations:
                    d = preparer_generation(os.path.join(sortie, f"etage-apres-generation-{g}"), resultat, gen.fiches,
                                            nombre=etage["nombre"], tranche_index_sha256=etage["tranche_index_sha256"],
                                            correspondance=etage["correspondance"], lisible=gen.arret is None)
                    ligne["etage"] = jouer_etage_v56(etage["adaptateur"], d, reglages=etage["reglages"], environnement=environnement,
                                                     executer=etage.get("executer"), permis_en_plus=permis)
                bilan.append(ligne)
        except BaseException as e:
            arret = motif_arret(e)
            raise
        finally:
            garde.nettoyage()
            ecrire_json_scelle(os.path.join(sortie, "bilan-course.json"), {"version": VERSION, "go": go, "generations": bilan,
                                                                           "noeud": noeud, "arret": arret, "signaux": garde.etat()})
    if noeud:
        raise NoeudArret(noeud)
    return bilan


__all__ = ("GenerationV56", "declarer_bras_v56", "forme_annexe_v56", "executer_course_v56", "ErreurInterneBras",
           "verifier_configuration_generation_v56", "CAUSE_BASIQUE", "CAUSE_GK_NOTABLES", "CAUSE_SOURCE_ABSENTE", "CAUSE_ANNEXE",
           "ARCHIVE_FUSIONS")
_ = re
