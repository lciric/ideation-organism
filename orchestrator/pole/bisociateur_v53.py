"""Bisociateur exploratoire à trois bras (R-601, R-619, R-635, R-636, R-638, R-639, R-642, R-643 ; brouillon 6, M9) — v53.

Trois bras, `k_paires` paires par session chacun (injecté ; S22/S23), **pas de bras hasard** :

- **bras méta, version 1** (profil « trou à structure commune ») : tous ses paramètres (S28, S29 a à f) sont lus dans
  l'**annexe scellée** `annexe-bras-meta-v1.md` (bloc JSON `parametres_bras_meta`), dont l'empreinte est injectée. **A20** :
  annexe absente, non scellée (compagnon `.sha256` faux), à empreinte différente de celle injectée, sans contre-lecture ni
  approbation de Lazar déclarées, ou paramètres incomplets → bras méta « non produit (annexe non conforme) », décidé à É0,
  écrit au manifeste ; aucun paramètre n'est choisi en route. Score = 1[communication faible] × 1[structure forte] ×
  1[éloignement dans la bande] × (1 + poids × s) ; le **désaccord n'entre jamais dans le score** (R-638, garde R5 ligne 24 :
  la fonction de score ne le reçoit pas) ; aucune paire dans le profil → règle de repli de l'annexe, paire comptée « hors
  profil » ;
- **bras « substitut inspiré de Gu et Krenn »** (S31) : source gelée (fichier JSON `{"oeuvres": [{"date", "concepts"}]}`)
  dont l'empreinte est injectée ; vocabulaire = concepts portés par au moins `oeuvres_min_vocabulaire` œuvres ; « reliées »
  = au moins une œuvre portant les deux concepts entre `date_debut` et `date_coupure` ; « actif » = au moins
  `actif_min_oeuvres` œuvres entre `actif_depuis` et la coupure. Note d'une paire de fiches = part des paires de concepts
  (c_a ≠ c_b) jamais reliées et toutes deux actives ; fiche à moins de 2 concepts du vocabulaire : non notable. **A19** :
  source absente ou à empreinte différente → bras « non produit (source absente) » ; le mode « modèle » (leur modèle ou sa
  reproduction) n'est pas branché en v53 : seul « substitut » est accepté, déclaré au manifeste à É0 ;
- **bras basique** « loin en domaine, proche en concept » : domaine = vecteur indicateur (axe, case) ; concept = étiquettes de
  la liste fermée (union des deux lecteurs) ; score = (1 − cos²_domaine)^exposant × (κ_concept + décalage), exposant et
  décalage injectés (forme du préenregistrement scellé de bisociation v2).

Règle des paires (CP4-05) : n fiches éligibles (passe 1, même case, munies d'un passeport) ; n < 2 : aucune paire, bras « non
produits (effectif) » ; n = 2 : une seule paire, au premier bras (ordre de priorité tiré) qui peut la noter ; n ≥ 3 : chaque bras,
dans l'ordre de priorité tiré (`bisoc-ordre`, SeedSequence R9), prend ses meilleures paires non déjà prises ; égalités
départagées par une clé tirée par bras (`bisoc-basique`, `bisoc-gk`, `bisoc-meta`). Gardes de paire (R5 ligne 16) : deux
fiches distinctes, même case, chacune avec passeport ; deux bras jamais sur la même paire.

Fusion (aveugle) : l'ordre d'écriture des fusions est tiré (`bisoc-ordre-fusion`) ; l'entrée du metteur en fusion porte la
consigne figée (la même pour les trois bras) et les deux fiches, **sans nom de bras ni de règle** (garde A4) ; la fusion est
étiquetée « exploratoire » au registre seulement, comptée à part ; la clé des bras est déposée au coffre (A21).
"""

import datetime
import itertools
import json
import os

from .fiches_v53 import garde_etiquettes, vue_servie
from .outils import extraire_bloc_json, sha256_fichier, verifier_scelle

VERSION = "bisociateur-v53"
REPLIS_CONNUS = ("indicateurs_puis_structure",)


class BisociationRefusee(RuntimeError):
    pass


def cle_paire(a, b):
    return tuple(sorted((a, b)))


def _niche_cle(a, b):
    return "|".join(sorted((a, b)))


# --- étiquettes (gardes R5 lignes 18 et 23) ----------------------------------------------------------------------------------


def valider_etiquettes(etiquettes, liste_fermee):
    if not isinstance(etiquettes, list) or not all(isinstance(e, str) for e in etiquettes):
        raise BisociationRefusee("étiquettes : liste de chaînes attendue")
    hors = sorted(set(etiquettes) - set(liste_fermee))
    if hors:
        raise BisociationRefusee("étiquette hors liste fermée (rejetée) : " + ", ".join(hors))
    return sorted(set(etiquettes))


def valider_niche(lecture, niches, types_structure):
    if not isinstance(lecture, dict) or not isinstance(lecture.get("niche"), str):
        raise BisociationRefusee("lecture de niche : {niche, structures} attendu, une niche par fiche")
    if lecture["niche"] not in niches:
        raise BisociationRefusee(f"niche hors grille (rejetée) : {lecture['niche']!r}")
    st = lecture.get("structures", [])
    if not isinstance(st, list):
        raise BisociationRefusee("structures : liste attendue")
    sortie = set()
    for s in st:
        if not isinstance(s, dict) or s.get("type") not in types_structure or not isinstance(s.get("nom"), str) or not s["nom"]:
            raise BisociationRefusee(f"structure hors grille (rejetée) : {s!r}")
        sortie.add((s["type"], s["nom"]))
    return lecture["niche"], sortie


def accord_jaccard(lectures_a, lectures_b):
    """Règle de S24 : fiche sans étiquette chez les deux lecteurs exclue (comptée) ; chez un seul : Jaccard 0."""
    valeurs, exclues = [], 0
    for ident in lectures_a:
        a, b = set(lectures_a[ident]), set(lectures_b.get(ident, []))
        if not a and not b:
            exclues += 1
            continue
        valeurs.append(len(a & b) / len(a | b))
    return {"jaccard_moyen": (sum(valeurs) / len(valeurs)) if valeurs else None, "n": len(valeurs), "exclues": exclues}


def kappa_niches(niches_a, niches_b):
    """Kappa de Cohen sur la niche ; règle des marges constantes (S28) : 1 si les deux étiquettes uniques coïncident, sinon 0,
    et la grille est marquée « dégénérée sur ce lot »."""
    ids = sorted(niches_a)
    if not ids:
        return {"kappa": None, "degenere": False}
    a, b = [niches_a[i] for i in ids], [niches_b[i] for i in ids]
    if len(set(a)) == 1 and len(set(b)) == 1:
        return {"kappa": 1.0 if a[0] == b[0] else 0.0, "degenere": True}
    n = len(ids)
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in set(a) | set(b))
    return {"kappa": 1.0 if pe == 1 else (po - pe) / (1 - pe), "degenere": False}


# --- bras basique ------------------------------------------------------------------------------------------------------------


def cos_domaine(fa, fb, axe_de):
    """Vecteurs indicateurs (axe) ⊕ (case), normes √2 : cos = (axe égal + case égale) / 2."""
    return ((axe_de(fa) == axe_de(fb)) + (list(fa["meta"]["case"]) == list(fb["meta"]["case"]))) / 2


def score_basique(fa, fb, concepts, axe_de, exposant, decalage):
    ca, cb = concepts.get(fa["ident"], set()), concepts.get(fb["ident"], set())
    kappa = len(ca & cb) / len(ca | cb) if (ca | cb) else 0.0
    c = cos_domaine(fa, fb, axe_de)
    return (1 - c * c) ** exposant * (kappa + decalage)


# --- bras substitut inspiré de Gu et Krenn (S31) -----------------------------------------------------------------------------


class SourceGuKrenn:
    def __init__(self, chemin, sha256_attendu, *, oeuvres_min_vocabulaire, date_debut, date_coupure, actif_depuis, actif_min_oeuvres):
        if not os.path.isfile(chemin):
            raise BisociationRefusee("source de S31 absente")
        if sha256_fichier(chemin) != sha256_attendu:
            raise BisociationRefusee("source de S31 à empreinte différente de celle écrite en tête")
        with open(chemin, "r", encoding="utf-8") as f:
            brut = json.load(f)
        oeuvres = brut.get("oeuvres") if isinstance(brut, dict) else None
        if not isinstance(oeuvres, list) or not oeuvres:
            raise BisociationRefusee("source de S31 illisible : {oeuvres: [{date, concepts}]} attendu")
        d0, dc, da = (datetime.date.fromisoformat(x) for x in (date_debut, date_coupure, actif_depuis))
        compte, actif, reliees = {}, {}, set()
        for o in oeuvres:
            try:
                d = datetime.date.fromisoformat(o["date"])
                cs = sorted(set(o["concepts"]))
            except (KeyError, TypeError, ValueError):
                raise BisociationRefusee("œuvre de la source illisible (date ISO, liste de concepts)") from None
            for c in cs:
                compte[c] = compte.get(c, 0) + 1
                if da <= d <= dc:
                    actif[c] = actif.get(c, 0) + 1
            if d0 <= d <= dc:
                reliees.update(itertools.combinations(cs, 2))
        self.vocabulaire = sorted(c for c, n in compte.items() if n >= oeuvres_min_vocabulaire)
        self.actifs = {c for c in self.vocabulaire if actif.get(c, 0) >= actif_min_oeuvres}
        self.reliees = reliees
        self.sha256 = sha256_attendu

    def note(self, ca, cb):
        """Part des paires (c_a, c_b), c_a ≠ c_b, jamais reliées et toutes deux actives ; None si une fiche a moins de 2
        concepts du vocabulaire (non notable)."""
        voc = set(self.vocabulaire)
        if set(ca) - voc or set(cb) - voc:
            raise BisociationRefusee("concept hors vocabulaire : refusé")
        if len(ca) < 2 or len(cb) < 2:
            return None
        paires = [(x, y) for x in ca for y in cb if x != y]
        if not paires:
            return 0.0
        bonnes = sum(1 for x, y in paires if cle_paire(x, y) not in self.reliees and x in self.actifs and y in self.actifs)
        return bonnes / len(paires)


# --- bras méta (annexe scellée) ----------------------------------------------------------------------------------------------

CLES_ANNEXE = ("niches", "types_structure", "communication", "seuil_communication_faible", "structure_forte", "eloignement",
               "bande", "poids", "repli", "contre_lecture", "approbation_lazar")


def lire_annexe_meta(chemin, sha256_attendu):
    """A20 : rend les paramètres de l'annexe, ou lève `BisociationRefusee` (le bras méta est alors « non produit »)."""
    if not chemin or not os.path.isfile(chemin):
        raise BisociationRefusee("A20 : annexe du bras méta absente")
    if not verifier_scelle(chemin):
        raise BisociationRefusee("A20 : annexe du bras méta non scellée (compagnon .sha256 absent ou faux)")
    if sha256_fichier(chemin) != sha256_attendu:
        raise BisociationRefusee("A20 : annexe du bras méta à empreinte différente de celle injectée")
    with open(chemin, "r", encoding="utf-8") as f:
        bloc = extraire_bloc_json(f.read(), "parametres_bras_meta")
    p = (bloc or {}).get("parametres_bras_meta")
    if not isinstance(p, dict):
        raise BisociationRefusee("A20 : bloc JSON parametres_bras_meta absent de l'annexe")
    manquants = [k for k in CLES_ANNEXE if k not in p]
    if manquants:
        raise BisociationRefusee("A20 : paramètres manquants dans l'annexe : " + ", ".join(manquants))
    for k in ("contre_lecture", "approbation_lazar"):
        if not isinstance(p[k], str) or not p[k].strip() or "À REMPLIR" in p[k]:
            raise BisociationRefusee(f"A20 : annexe sans {k} déclarée")
    niches = p["niches"]
    if not isinstance(niches, list) or len(niches) < 2:
        raise BisociationRefusee("A20 : grille des niches : au moins deux niches")
    for a, b in itertools.combinations(niches, 2):
        for table in ("communication", "eloignement"):
            if _niche_cle(a, b) not in p[table]:
                raise BisociationRefusee(f"A20 : {table} non définie pour {a} | {b}")
    if p["repli"] not in REPLIS_CONNUS:
        raise BisociationRefusee(f"A20 : règle de repli inconnue {p['repli']!r} (connues : {REPLIS_CONNUS})")
    sf = p["structure_forte"]
    if not isinstance(sf, dict) or not isinstance(sf.get("nombre_min"), int) or not isinstance(sf.get("types"), list):
        raise BisociationRefusee("A20 : structure_forte {nombre_min, types} attendue")
    if not (isinstance(p["bande"], list) and len(p["bande"]) == 2 and p["bande"][0] <= p["bande"][1]):
        raise BisociationRefusee("A20 : bande [e_min, e_max] attendue")
    return p


def indicateurs_meta(p, na, nb, sa, sb):
    """Rend (c faible, s forte, e dans la bande, s) pour deux niches différentes. Le désaccord n'est pas un argument."""
    if na == nb:
        raise BisociationRefusee("paire de deux fiches de même niche : refusée (bras méta)")
    c = p["communication"][_niche_cle(na, nb)]
    e = p["eloignement"][_niche_cle(na, nb)]
    s = len({x for x in (sa & sb) if x[0] in p["structure_forte"]["types"]})
    return (c <= p["seuil_communication_faible"], s >= p["structure_forte"]["nombre_min"],
            p["bande"][0] <= e <= p["bande"][1], s)


def score_meta(p, na, nb, sa, sb):
    cf, sf, eb, s = indicateurs_meta(p, na, nb, sa, sb)
    return (1.0 if (cf and sf and eb) else 0.0) * (1 + p["poids"] * s)


def score_repli(p, na, nb, sa, sb):
    cf, sf, eb, s = indicateurs_meta(p, na, nb, sa, sb)
    return (cf + sf + eb, s)


# --- sélection des paires ----------------------------------------------------------------------------------------------------


def verifier_paire(fa, fb, aiguilleur):
    """Garde R5 ligne 16."""
    if fa["ident"] == fb["ident"]:
        raise BisociationRefusee("paire d'une fiche avec elle-même")
    if list(fa["meta"]["case"]) != list(fb["meta"]["case"]):
        raise BisociationRefusee("paire traversant une case")
    for f in (fa, fb):
        aiguilleur.exiger_passeport(f, "le bisociateur")
    return True


def choisir_paires(fiches, notes_par_bras, ordre_bras, k, aiguilleur, departage):
    """`notes_par_bras` : {bras: {cle_paire: (score triable, détail)}} ; `departage` : {bras: {cle_paire: réel tiré}}.
    Rend {bras: [paires]} et {bras: cause de non-production}."""
    par_ident = {f["ident"]: f for f in fiches}
    n = len(fiches)
    prises, choix, non_produits = set(), {b: [] for b in ordre_bras}, {}
    if n < 2:
        return choix, {b: "non produit (effectif)" for b in ordre_bras}
    if n == 2:
        paire = cle_paire(*[f["ident"] for f in fiches])
        gagnant = next((b for b in ordre_bras if paire in notes_par_bras.get(b, {})), None)
        for b in ordre_bras:
            if b == gagnant:
                verifier_paire(par_ident[paire[0]], par_ident[paire[1]], aiguilleur)
                choix[b] = [paire]
            else:
                non_produits[b] = "non produit (effectif)"
        return choix, non_produits
    for b in ordre_bras:
        notes = notes_par_bras.get(b, {})
        candidates = sorted((p for p in notes if p not in prises),
                            key=lambda p: (notes[p][0], departage[b].get(p, 0.0)), reverse=True)
        for p in candidates[:k]:
            verifier_paire(par_ident[p[0]], par_ident[p[1]], aiguilleur)
            prises.add(p)
            choix[b].append(p)
        if not choix[b]:
            non_produits[b] = "non produit (aucune paire notable)"
    return choix, non_produits


def garde_desaccord_hors_score(fonction_score, p, na, nb, sa, sb):
    """Garde R5 ligne 24 : la même paire, désaccord « oui » puis « non », reçoit le même score ; une fonction de score qui
    accepte un argument de désaccord et en dépend est un arrêt."""
    import inspect
    noms = set(inspect.signature(fonction_score).parameters)
    if not noms & {"desaccord", "d"}:
        return True
    cle = "desaccord" if "desaccord" in noms else "d"
    oui = fonction_score(p, na, nb, sa, sb, **{cle: "oui"})
    non = fonction_score(p, na, nb, sa, sb, **{cle: "non"})
    if oui != non:
        raise BisociationRefusee("R-638 : le désaccord entre dans le score du bras méta (scores différents) : arrêt")
    return True


def entree_fusion(consigne_fusion, fa, fb, etiquettes_interdites):
    """Entrée du metteur en fusion : consigne figée commune aux trois bras + les deux fiches, sans nom de bras ni de règle."""
    corps = json.dumps([vue_servie(fa), vue_servie(fb)], ensure_ascii=False, indent=1)
    garde_etiquettes(corps, etiquettes_interdites)
    return consigne_fusion.rstrip() + "\n\n## Les deux fiches\n```json\n" + corps + "\n```\n"
