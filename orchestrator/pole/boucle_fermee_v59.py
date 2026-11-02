"""Boucle fermée entre générations, version 59 (fichier neuf, R12 ; tâche A2) — la génération g+1 **lit** la sélection scellée
de la génération g.

Constat de départ (README § 2, étape 9 ; `pole/etage_entre_generations_v57.py`) : la v57b calcule, scelle et consigne la
sélection entre générations (`selection-entre-generations-v57.json`), mais aucune génération ne la lit ; l'héritage servi reste
le classement des juges, écrit avant l'étage. Ce module ferme la flèche :

1. **Bilan scellé de la génération g** (`ecrire_bilan_generation`) : il nomme, avec leurs empreintes, le fichier de sélection
   (v57), le fichier des cartes de la génération (lois comprises), et le verdict scellé du noyau de chaque carte testée
   (`verdict-noyau-v5.json`) ; il porte l'archive cumulée (lois retenues jusqu'à g). Son empreinte est rendue à l'appelant,
   qui la passe, telle quelle, à la génération g+1.
2. **Lecture vérifiée** (`lire_heritage`) : chaque fichier est lu **une fois**, en octets, hors lien symbolique, sceau compagnon
   vérifié **et** empreinte égale à celle que la génération g a consignée — vérifiée **avant** toute lecture du contenu (les
   octets hachés sont ceux qui sont lus) ; tout écart lève `SelectionNonVerifiee` (refus net, aucun repli, aucune lecture
   partielle). Puis une **contre-vérification** mécanique : les retenues de la sélection doivent être exactement les cartes
   dont le verdict scellé du noyau est « survit » (`survivantes_des_verdicts`), chacune présente parmi les cartes ; sinon
   `HeritageRefuse`.
3. **Ce que voit le proposeur suivant** (`vue_pour_proposeur`) : les seules lois de l'archive (identifiant, loi), jamais un
   verdict, une richesse, une promotion, un motif ou un compte ; la garde `exiger_vue_sans_verdict` refuse toute vue qui en
   porte (`VueAvecVerdict`).
4. **Graines** (`graine_de_tache`, R9) : `numpy.random.SeedSequence(racine, spawn_key=(cle_de_tache(tache),))`, la clé de tâche
   de `pole/graines_v53.py` (même fonction que `src/controle_ia/manifeste.py`).

Ce qui change pour les proposeurs (dit, décision demandée par la tâche A2) : la génération g+1 n'hérite plus du classement des
juges ; elle reçoit les seules lois retenues (« survit », verdict du noyau) — c'est ce qu'un préenregistrement du tour fermé
doit citer.
"""

import hashlib
import json
import os
import stat

from .etage_entre_generations_v57 import NOM_SELECTION
from .etage_entre_generations_v57 import VERSION as VERSION_SELECTION_V57
from .graines_v53 import _numpy, cle_de_tache
from .outils import ecrire_json_scelle, verifier_scelle
from .tests_de_mort_v4 import ETIQUETTE_NOYAU, rang_verdict

VERSION = "boucle-fermee-v59"
NOM_BILAN = "bilan-generation-v59.json"
NOM_CARTES = "cartes-generation-v59.json"
DOSSIER_ETAGE = "etage"
CLES_INTERDITES_VUE = frozenset({"verdict", "verdict_final", "verdict_noyau", "promue", "promues", "log_richesse",
                                 "log_richesse_max", "richesse", "trajectoire_log_w", "multiplicite", "motif", "motif_verdict",
                                 "exclues", "comptes", "pari", "evaluation", "evaluations", "juge", "membre_dominant_final"})


class HeritageRefuse(RuntimeError):
    """La génération suivante refuse l'héritage : contre-vérification en échec, bilan d'une autre version, carte absente."""


class SelectionNonVerifiee(HeritageRefuse):
    """Fichier de la boucle (bilan, sélection, cartes, verdict) absent, lien, sceau faux ou empreinte ≠ celle consignée."""


class VueAvecVerdict(RuntimeError):
    """Une vue servie à un proposeur porte un verdict, une richesse, une promotion ou un compte du juge."""


class GraineRefusee(ValueError):
    pass


# --- graines (R9) ------------------------------------------------------------------------------------------------------------


def graine_de_tache(racine, tache):
    """Graine entière (64 bits) d'une tâche : `SeedSequence(racine, spawn_key=(cle_de_tache(tache),))`. Racine : entier ≥ 0 ;
    tâche : texte non vide (aucun défaut)."""
    if isinstance(racine, bool) or not isinstance(racine, int) or racine < 0:
        raise GraineRefusee(f"racine des graines : entier ≥ 0 attendu (reçu {racine!r})")
    if not isinstance(tache, str) or not tache:
        raise GraineRefusee("tâche : texte non vide attendu (la graine est dérivée de la tâche, R9)")
    np = _numpy()
    ss = np.random.SeedSequence(racine, spawn_key=(cle_de_tache(tache),))
    return int(ss.generate_state(1, dtype=np.uint64)[0])


# --- lecture vérifiée ------------------------------------------------------------------------------------------------------


def lire_scelle_verifie(chemin, sha256_attendu, quoi):
    """Les octets de `chemin`, vérifiés avant lecture du contenu : fichier régulier (aucun lien suivi), sceau compagnon juste,
    empreinte égale à `sha256_attendu` (celle que la génération précédente a consignée) ; rend l'objet JSON. Lève
    `SelectionNonVerifiee` sinon."""
    if not isinstance(sha256_attendu, str) or len(sha256_attendu) != 64:
        raise SelectionNonVerifiee(f"{quoi} : empreinte attendue absente ou mal formée ({sha256_attendu!r}) : aucune lecture")
    try:
        st = os.lstat(chemin)
    except OSError as e:
        raise SelectionNonVerifiee(f"{quoi} : fichier absent ({chemin}) : {type(e).__name__}") from None
    if not stat.S_ISREG(st.st_mode):
        raise SelectionNonVerifiee(f"{quoi} : pas un fichier régulier (lien ou autre) : {chemin}")
    if not verifier_scelle(chemin):
        raise SelectionNonVerifiee(f"{quoi} : sceau compagnon absent ou faux : {chemin}")
    with open(chemin, "rb") as f:
        octets = f.read()
    sha = hashlib.sha256(octets).hexdigest()
    if sha != sha256_attendu:
        raise SelectionNonVerifiee(f"{quoi} : empreinte {sha[:16]}… ≠ empreinte consignée par la génération précédente "
                                   f"{sha256_attendu[:16]}… : refus, aucune lecture")
    try:
        return json.loads(octets.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as e:
        raise SelectionNonVerifiee(f"{quoi} : JSON illisible ({type(e).__name__})") from None


def survivantes_des_verdicts(verdicts):
    """Identifiants (triés) des cartes dont le verdict scellé du noyau est « survit » (étiquette du noyau exigée ; tout autre
    mot connu → exclue ; mot inconnu → `VerdictInconnu`)."""
    retenues = []
    for ident, v in sorted(verdicts.items()):
        if not isinstance(v, dict) or v.get("etiquette") != ETIQUETTE_NOYAU:
            continue
        rang_verdict(v.get("verdict"))
        if v.get("verdict") == "survit":
            retenues.append(ident)
    return retenues


def heritage_initial():
    """L'héritage de la première génération : aucune lecture, archive vide (dit au bilan)."""
    return {"version": VERSION, "generation_lue": None, "bilan_sha256": None, "retenues": [], "archive": {},
            "empreintes_lues": {}}


def ecrire_bilan_generation(dossier_generation, *, generation, bras, cartes, resume_etage, chemin_selection, sha_selection,
                            archive_precedente, heritage_lu, comptes, graines):
    """Scelle `cartes-generation-v59.json` puis `bilan-generation-v59.json` dans `dossier_generation` ; rend l'empreinte du
    bilan. `resume_etage` : résumé de l'étage v5 (None si aucun étage, faute de carte promue) ; `chemin_selection` : chemin du
    fichier de sélection v57 scellé ; l'archive cumulée = archive précédente ∪ lois des retenues de cette génération."""
    sha_cartes = ecrire_json_scelle(os.path.join(dossier_generation, NOM_CARTES), {"version": VERSION, "generation": generation,
                                                                                    "bras": bras, "cartes": cartes})
    verdicts = {}
    for r in (resume_etage or {}).get("par_fiche", []):
        if r.get("statut") == "testée":
            rel = os.path.join(DOSSIER_ETAGE, "noyau", "tests-de-mort", r["identifiant_auteur"], "verdict-noyau-v5.json")
            verdicts[r["identifiant_auteur"]] = {"fichier": rel, "sha256": r["verdict_noyau_sha256"]}
    with open(chemin_selection, "rb") as f:
        retenues = json.loads(f.read().decode("utf-8"))["retenues"]
    lois = {c["identifiant"]: c["loi_predictive"] for c in cartes}
    archive = dict(archive_precedente)
    archive.update({i: lois[i] for i in retenues})
    bilan = {"version": VERSION, "generation": generation, "bras": bras,
             "heritage_lu": {k: heritage_lu.get(k) for k in ("generation_lue", "bilan_sha256", "retenues", "empreintes_lues")},
             "cartes": {"fichier": NOM_CARTES, "sha256": sha_cartes},
             "selection": {"fichier": os.path.relpath(chemin_selection, dossier_generation), "sha256": sha_selection},
             "verdicts": verdicts, "archive": archive, "comptes": comptes, "graines": graines,
             "regle": ("la génération suivante lit ce bilan (empreinte passée par l'orchestrateur), puis la sélection, les "
                       "cartes et les verdicts qu'il nomme, chacun vérifié (sceau et empreinte) avant lecture ; seules les "
                       "lois retenues (« survit », verdict du noyau) entrent à l'archive et dans la vue des proposeurs")}
    return ecrire_json_scelle(os.path.join(dossier_generation, NOM_BILAN), bilan)


def lire_heritage(dossier_generation, sha256_bilan):
    """L'héritage de la génération g, lu par la génération g+1 : bilan, sélection, cartes et verdicts vérifiés (sceau et
    empreinte) avant lecture, puis contre-vérification (retenues = survivantes du noyau, chacune parmi les cartes, archive
    cohérente). Rend {generation_lue, bilan_sha256, retenues, archive, empreintes_lues}. Lève `SelectionNonVerifiee` ou
    `HeritageRefuse` (aucun repli, aucune lecture partielle)."""
    bilan = lire_scelle_verifie(os.path.join(dossier_generation, NOM_BILAN), sha256_bilan, "bilan de la génération")
    if not isinstance(bilan, dict) or bilan.get("version") != VERSION:
        raise HeritageRefuse(f"bilan d'une autre version ({(bilan or {}).get('version')!r}) : refus")
    sel = bilan.get("selection") or {}
    selection = lire_scelle_verifie(os.path.join(dossier_generation, str(sel.get("fichier"))), sel.get("sha256"), "sélection")
    if not isinstance(selection, dict) or selection.get("version") != VERSION_SELECTION_V57 \
            or os.path.basename(str(sel.get("fichier"))) != NOM_SELECTION:
        raise HeritageRefuse("sélection d'une autre version que celle de l'étage entre générations v57 : refus")
    if not isinstance(selection.get("retenues"), list) or not isinstance(selection.get("exclues"), list):
        raise HeritageRefuse("sélection sans « retenues » ni « exclues » : refus")
    retenues = list(selection["retenues"])
    ca = bilan.get("cartes") or {}
    cartes = lire_scelle_verifie(os.path.join(dossier_generation, str(ca.get("fichier"))), ca.get("sha256"), "cartes")
    lois = {c["identifiant"]: c["loi_predictive"] for c in cartes.get("cartes", [])}
    verdicts = {}
    for ident, ref in sorted((bilan.get("verdicts") or {}).items()):
        verdicts[ident] = lire_scelle_verifie(os.path.join(dossier_generation, ref["fichier"]), ref["sha256"],
                                              f"verdict du noyau de {ident}")
    derivees = survivantes_des_verdicts(verdicts)
    if sorted(retenues) != derivees:
        raise HeritageRefuse(f"contre-vérification : retenues de la sélection {sorted(retenues)} ≠ survivantes des verdicts "
                             f"scellés du noyau {derivees} : refus")
    absentes = [i for i in retenues if i not in lois]
    if absentes:
        raise HeritageRefuse(f"retenue(s) absente(s) des cartes de la génération : {absentes} : refus")
    archive = bilan.get("archive")
    if not isinstance(archive, dict) or any(archive.get(i) != lois[i] for i in retenues):
        raise HeritageRefuse("archive du bilan incohérente avec les lois des retenues : refus")
    return {"version": VERSION, "generation_lue": bilan.get("generation"), "bilan_sha256": sha256_bilan, "retenues": retenues,
            "archive": archive, "empreintes_lues": {"bilan": sha256_bilan, "selection": sel.get("sha256"),
                                                     "cartes": ca.get("sha256"),
                                                     "verdicts": {i: r["sha256"] for i, r in (bilan.get("verdicts") or {}).items()}}}


# --- vue servie aux proposeurs ------------------------------------------------------------------------------------------------


def exiger_vue_sans_verdict(vue):
    """Garde : lève `VueAvecVerdict` si une clé interdite (verdict, richesse, promotion, motif, compte…) apparaît à n'importe
    quelle profondeur de la vue ; rend la vue sinon."""
    pile, trouvees = [vue], set()
    while pile:
        x = pile.pop()
        if isinstance(x, dict):
            trouvees |= {k for k in x if k in CLES_INTERDITES_VUE}
            pile.extend(x.values())
        elif isinstance(x, (list, tuple)):
            pile.extend(x)
    if trouvees:
        raise VueAvecVerdict(f"vue servie au proposeur avec des informations du juge ({', '.join(sorted(trouvees))}) : refus")
    return vue


def vue_pour_proposeur(heritage):
    """Ce que la génération suivante sert à un proposeur : les lois de l'archive (identifiant, loi), rien d'autre."""
    vue = {"generation_lue": heritage.get("generation_lue"),
           "lois_retenues": [{"identifiant": i, "loi": heritage["archive"][i]} for i in sorted(heritage.get("archive") or {})]}
    return exiger_vue_sans_verdict(json.loads(json.dumps(vue)))


__all__ = ("HeritageRefuse", "SelectionNonVerifiee", "VueAvecVerdict", "GraineRefusee", "graine_de_tache", "lire_scelle_verifie",
           "survivantes_des_verdicts", "heritage_initial", "ecrire_bilan_generation", "lire_heritage", "exiger_vue_sans_verdict",
           "vue_pour_proposeur", "VERSION", "NOM_BILAN", "NOM_CARTES", "DOSSIER_ETAGE")
