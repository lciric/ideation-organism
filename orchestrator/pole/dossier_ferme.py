"""Dossier fermé du tour (c) « outils clôturés » (v46 ; décisions de Lazar du 29 octobre 2026, R-433, R-434, R-441, R-444,
R-448 ; note de conception `note-tour-c-outils-clotures-v1.md`).

Un **dossier fermé** est un dossier qui contient exactement les fichiers listés dans son manifeste scellé `index.json`
(compagnon `index.json.sha256`, et `index.json` dans la liste blanche de la course) : pour chaque fichier, chemin relatif,
empreinte, titre, résumé, et, s'ils sont connus, sections et nombre de pages. Avant la course, le noyau vérifie : aucun
lien symbolique, aucun fichier en plus ni en moins, aucun fragment interdit (`donnees`, `mode-tenu-a-l-ecart`…), chaque
empreinte, un texte UTF-8 (un PDF n'est jamais servi : il défait les retraits de sûreté des extraits), un caviardage sans
effet (aucun secret : la copie servie aux outils du kit est alors identique à l'original), et le nombre de pages déclaré.

Pages : une ligne qui commence par `[p.N]` ouvre la page N (forme des extraits du corpus primaire ; plusieurs passages
d'une même page sont joints) ; à défaut, le saut de page (`\\f`) ; à défaut, le fichier entier est la page 1.

Ce module sert aussi, par **protocole**, les demandes d'un proposeur sans outil (Argon, et Claude sous
`--outils-par-protocole`) : `{"demandes": [{"lire": "<chemin>", "pages": [a, b]}, {"chercher": "<motif>"}]}` ; une page
servie à un proposeur est servie aux autres depuis un **cache partagé** (même texte, même empreinte, consigné) ; la
demande `{"moissonner": …}` est reconnue et refusée : « moisson non disponible » sans `--moisson`, et sous `--moisson`
(v47) « au tour de moisson seulement » (la moisson a son propre bloc, `pole/moisson.py`). Il vérifie enfin les
**citations** `[chemin, p.N]` des fiches (L7) : la page existe ; le passage cité entre guillemets juste avant s'y
retrouve. v47 : la lecture du bloc de demandes vit dans `pole/protocole_outils.py`, partagée avec la moisson.

Bibliothèque standard seule ; aucune écriture hors de la copie demandée ; aucun réseau.
"""

import hashlib
import json
import os
import re
import shutil

from .caviardage import caviarder
from .outils import normaliser_texte, sha256_fichier, verifier_scelle

NOM_INDEX = "index.json"
MARQUE_PAGE = re.compile(r"(?m)^[ \t]*\[\s*p\.\s*(\d+)\s*\]")
TAILLE_MAX_TITRE = 300
TAILLE_MAX_RESUME = 3000
MAX_SECTIONS = 80
MAX_DEMANDES_LECTURE_DEFAUT = 1000  # R-441, R-444 : garde-fou anti-boucle ; au-delà : incident, arrêt de la session
TAILLE_MAX_SERVIE_PAR_TOUR = 200_000  # caractères servis au plus par tour ; le reste est redemandé au tour suivant
MAX_RESULTATS_RECHERCHE = 50
TAILLE_MAX_LIGNE_TROUVEE = 300
TAILLE_MIN_MOTIF, TAILLE_MAX_MOTIF = 2, 200
SEUIL_AVERTISSEMENT_BUDGET = 0.8
TYPES_DEMANDE = ("lire", "chercher", "moissonner")
MOTIF_MOISSON = "moisson non disponible (v47)"  # course sans `--moisson` : inchangé depuis la v46
# v47 : sous `--moisson`, la moisson se demande au tour de moisson (entre les passes) par le bloc {"moisson": [...]},
# jamais dans un tour de lecture du dossier fermé
MOTIF_MOISSON_AU_TOUR = ("moisson : par le bloc {\"moisson\": [{\"source\": …, \"requete\": …, \"resultats\": …}]} au tour "
                         "de moisson, entre les passes ; pas dans un tour de lecture")
# Kit d'agent, outil Read : lignes lues par défaut quand `limit` n'est pas donné (SUPPOSÉ d'après la documentation de l'outil)
LIGNES_READ_PAR_DEFAUT = 2000


class DossierFermeInvalide(ValueError):
    """Le dossier fermé est refusé avant tout appel (rien payé)."""


def decouper_pages(texte):
    """(pages {N: texte}, premières lignes {N: numéro de la première ligne, 1-based}) — voir la docstring du module."""
    marques = list(MARQUE_PAGE.finditer(texte))
    pages, lignes = {}, {}
    if marques:
        bornes = [m.start() for m in marques] + [len(texte)]
        for k, m in enumerate(marques):
            debut = 0 if k == 0 else bornes[k]
            n = int(m.group(1))
            segment = texte[debut:bornes[k + 1]]
            pages[n] = (pages[n] + "\n" + segment) if n in pages else segment
            lignes.setdefault(n, texte.count("\n", 0, debut) + 1)
        return pages, lignes
    if "\f" in texte:
        morceaux = texte.split("\f")
        if morceaux and not morceaux[-1].strip():
            morceaux = morceaux[:-1]
        position = 0
        for k, morceau in enumerate(morceaux, 1):
            pages[k] = morceau
            lignes[k] = texte.count("\n", 0, position) + 1
            position += len(morceau) + 1
        return pages, lignes
    return {1: texte}, {1: 1}


def _chemin_relatif_propre(chemin):
    if not isinstance(chemin, str) or not chemin or chemin != chemin.strip():
        return False
    if os.path.isabs(chemin) or "\\" in chemin or "\x00" in chemin:
        return False
    composants = chemin.split("/")
    if any(c in ("", ".", "..") or c.startswith("~") for c in composants):
        return False
    return os.path.normpath(chemin) == chemin


class DossierFerme:
    """Un dossier fermé vérifié : fichiers (texte, pages), index servi, recherche."""

    def __init__(self, racine, index_sha256, fichiers):
        self.racine = racine
        self.index_sha256 = index_sha256
        self.fichiers = fichiers  # {chemin: {sha256, titre, resume, sections, pages_declarees, texte, pages, lignes}}

    @property
    def pages_total(self):
        return sum(len(f["pages"]) for f in self.fichiers.values())

    def vue_index(self):
        """L'index servi dans la consigne des proposeurs (le texte n'y est pas) : chemin, titre, résumé, taille, pages,
        sections."""
        vue = []
        for chemin in sorted(self.fichiers):
            f = self.fichiers[chemin]
            e = {"chemin": chemin, "titre": f["titre"], "resume": f["resume"], "taille_caracteres": len(f["texte"]),
                 "pages": sorted(f["pages"])}
            if f["sections"]:
                e["sections"] = list(f["sections"])
            vue.append(e)
        return vue

    def description(self):
        """Pour le manifeste de départ : empreinte de l'index, fichiers (chemin, empreinte, pages, taille)."""
        return {"index_sha256": self.index_sha256, "racine": os.path.basename(self.racine),
                "fichiers": [{"chemin": c, "sha256": f["sha256"], "pages": len(f["pages"]), "taille_caracteres": len(f["texte"])}
                             for c, f in sorted(self.fichiers.items())],
                "pages_total": self.pages_total}

    def trouver(self, nom):
        """Le chemin du dossier désigné par `nom` : chemin exact, nom de base, ou nom sans extension (casse ignorée) ;
        None si aucun ou ambigu."""
        if not isinstance(nom, str):
            return None
        n = nom.strip().strip("`'\"").lower()
        if n in {c.lower(): c for c in self.fichiers}:
            return {c.lower(): c for c in self.fichiers}[n]
        for cle in (lambda c: os.path.basename(c).lower(), lambda c: os.path.splitext(os.path.basename(c))[0].lower()):
            trouves = [c for c in self.fichiers if cle(c) == n]
            if len(trouves) == 1:
                return trouves[0]
        return None

    def page(self, chemin, numero):
        f = self.fichiers.get(chemin)
        return None if f is None else f["pages"].get(numero)

    def pages_de_lignes(self, chemin, debut, nombre):
        """Pages couvertes par les lignes [debut, debut + nombre − 1] (1-based) d'un fichier ; approximation des lectures
        `Read` du kit (lignes) en pages."""
        f = self.fichiers.get(chemin)
        if f is None:
            return []
        fin = debut + max(1, nombre) - 1
        ordre = sorted(f["lignes"].items(), key=lambda kv: kv[1])
        couvertes = []
        for k, (n, premiere) in enumerate(ordre):
            derniere = (ordre[k + 1][1] - 1) if k + 1 < len(ordre) else float("inf")
            if premiere <= fin and derniere >= debut:
                couvertes.append(n)
        return sorted(set(couvertes))

    def chercher(self, motif, dans=None, maximum=MAX_RESULTATS_RECHERCHE):
        """Lignes qui contiennent `motif` (sous-chaîne littérale, casse ignorée ; jamais une expression rationnelle) :
        [(chemin, page, ligne)], au plus `maximum`, et le nombre total trouvé."""
        m = motif.lower()
        trouves, total = [], 0
        for chemin in ([dans] if dans else sorted(self.fichiers)):
            f = self.fichiers[chemin]
            for n in sorted(f["pages"]):
                for ligne in f["pages"][n].splitlines():
                    if m in ligne.lower():
                        total += 1
                        if len(trouves) < maximum:
                            trouves.append((chemin, n, ligne.strip()[:TAILLE_MAX_LIGNE_TROUVEE]))
        return trouves, total

    def copier_vers(self, destination):
        """Copie le dossier (fichiers listés seulement, sous leur chemin relatif) dans `destination` (absente) et vérifie
        chaque empreinte ; rend {chemin: sha256}. Lève DossierFermeInvalide sur une empreinte différente."""
        if os.path.exists(destination):
            raise DossierFermeInvalide(f"copie du dossier fermé : destination existante ({destination})")
        os.makedirs(destination)
        empreintes = {}
        for chemin, f in sorted(self.fichiers.items()):
            cible = os.path.join(destination, chemin)
            os.makedirs(os.path.dirname(cible), exist_ok=True)
            with open(cible, "w", encoding="utf-8", newline="") as sortie:
                sortie.write(f["texte"])
            empreintes[chemin] = sha256_fichier(cible)
            if empreintes[chemin] != f["sha256"]:
                raise DossierFermeInvalide(f"copie du dossier fermé : empreinte différente pour {chemin}")
        return empreintes

    def verifier_copie(self, destination):
        """Après la session : liste des écarts de la copie (fichier altéré, absent, ou en plus) ; vide si intacte."""
        ecarts = []
        presents = set()
        for racine, dossiers, noms in os.walk(destination):
            for nom in noms:
                presents.add(os.path.relpath(os.path.join(racine, nom), destination))
        for chemin, f in self.fichiers.items():
            cible = os.path.join(destination, chemin)
            if not os.path.isfile(cible) or os.path.islink(cible):
                ecarts.append({"chemin": chemin, "ecart": "absent ou remplacé par un lien"})
            elif sha256_fichier(cible) != f["sha256"]:
                ecarts.append({"chemin": chemin, "ecart": "empreinte différente"})
        for chemin in sorted(presents - set(self.fichiers)):
            ecarts.append({"chemin": chemin, "ecart": "fichier en plus"})
        return ecarts


def charger_dossier_ferme(dossier, liste_blanche=None):
    """Vérifie et charge un dossier fermé (voir la docstring du module) ; lève DossierFermeInvalide avec un motif."""
    from .ideation import fragments_interdits_dans  # import tardif : ideation importe ce module
    if not isinstance(dossier, str) or not dossier:
        raise DossierFermeInvalide("dossier fermé : chemin manquant")
    if os.path.islink(dossier.rstrip("/")):
        raise DossierFermeInvalide(f"dossier fermé : lien symbolique refusé ({dossier})")
    racine = os.path.realpath(dossier)
    if not os.path.isdir(racine):
        raise DossierFermeInvalide(f"dossier fermé absent : {dossier}")
    mauvais = fragments_interdits_dans(racine)
    if mauvais:
        raise DossierFermeInvalide(f"dossier fermé refusé ({mauvais[0]!r}) : {dossier}")
    index = os.path.join(racine, NOM_INDEX)
    if os.path.islink(index) or not os.path.isfile(index):
        raise DossierFermeInvalide(f"dossier fermé : {NOM_INDEX} absent ou lien symbolique")
    if not verifier_scelle(index):
        raise DossierFermeInvalide(f"dossier fermé : {NOM_INDEX} non scellé ou au sceau faux")
    index_sha256 = sha256_fichier(index)
    if liste_blanche is not None:
        if index not in liste_blanche:
            raise DossierFermeInvalide(f"dossier fermé : {NOM_INDEX} hors de la liste blanche")
        if liste_blanche[index] != index_sha256:
            raise DossierFermeInvalide(f"dossier fermé : empreinte de {NOM_INDEX} différente de la liste blanche")
    try:
        with open(index, "r", encoding="utf-8") as f:
            brut = json.load(f)
    except ValueError as e:
        raise DossierFermeInvalide(f"dossier fermé : {NOM_INDEX} illisible ({e})") from e
    if not isinstance(brut, dict) or set(brut) - {"fichiers", "titre", "description"} \
            or not isinstance(brut.get("fichiers"), list) or not brut["fichiers"]:
        raise DossierFermeInvalide(f"dossier fermé : {NOM_INDEX} doit être {{\"fichiers\": [...]}} non vide")
    attendus = {}
    for i, e in enumerate(brut["fichiers"], 1):
        if not isinstance(e, dict) or set(e) - {"chemin", "sha256", "titre", "resume", "sections", "pages"}:
            raise DossierFermeInvalide(f"index, entrée {i} : champs permis chemin, sha256, titre, resume, sections, pages")
        chemin = e.get("chemin")
        if not _chemin_relatif_propre(chemin) or chemin in (NOM_INDEX, NOM_INDEX + ".sha256"):
            raise DossierFermeInvalide(f"index, entrée {i} : chemin relatif propre attendu (ni absolu, ni .., ni ~) : {chemin!r}")
        if chemin in attendus:
            raise DossierFermeInvalide(f"index : chemin en double : {chemin}")
        if not isinstance(e.get("sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", e["sha256"]):
            raise DossierFermeInvalide(f"index, {chemin} : empreinte mal formée")
        titre, resume = e.get("titre"), e.get("resume")
        if not isinstance(titre, str) or not titre.strip() or len(titre) > TAILLE_MAX_TITRE:
            raise DossierFermeInvalide(f"index, {chemin} : titre manquant ou trop long")
        if not isinstance(resume, str) or len(resume) > TAILLE_MAX_RESUME:
            raise DossierFermeInvalide(f"index, {chemin} : résumé manquant ou trop long (≤ {TAILLE_MAX_RESUME})")
        sections = e.get("sections") or []
        if not isinstance(sections, list) or len(sections) > MAX_SECTIONS \
                or not all(isinstance(s, str) and 0 < len(s) <= TAILLE_MAX_TITRE for s in sections):
            raise DossierFermeInvalide(f"index, {chemin} : sections, liste de textes courts")
        pages = e.get("pages")
        if pages is not None and (isinstance(pages, bool) or not isinstance(pages, int) or pages < 1):
            raise DossierFermeInvalide(f"index, {chemin} : pages, entier ≥ 1")
        mauvais = fragments_interdits_dans(chemin)
        if mauvais:
            raise DossierFermeInvalide(f"dossier fermé : fichier refusé ({mauvais[0]!r}) : {chemin}")
        attendus[chemin] = e
    presents = set()
    for base, dossiers, noms in os.walk(racine, followlinks=False):
        for nom in dossiers + noms:
            p = os.path.join(base, nom)
            if os.path.islink(p):
                raise DossierFermeInvalide(f"dossier fermé : lien symbolique refusé ({os.path.relpath(p, racine)})")
        for nom in noms:
            presents.add(os.path.relpath(os.path.join(base, nom), racine))
    presents -= {NOM_INDEX, NOM_INDEX + ".sha256"}
    if presents - set(attendus):
        raise DossierFermeInvalide("dossier fermé : fichiers non listés dans l'index : " + ", ".join(sorted(presents - set(attendus))[:5]))
    if set(attendus) - presents:
        raise DossierFermeInvalide("dossier fermé : fichiers de l'index absents : " + ", ".join(sorted(set(attendus) - presents)[:5]))
    fichiers = {}
    for chemin, e in attendus.items():
        p = os.path.join(racine, chemin)
        if sha256_fichier(p) != e["sha256"]:
            raise DossierFermeInvalide(f"dossier fermé : empreinte différente de l'index pour {chemin}")
        try:
            with open(p, "r", encoding="utf-8", newline="") as f:
                texte = f.read()
        except UnicodeDecodeError as err:
            raise DossierFermeInvalide(f"dossier fermé : {chemin} n'est pas un texte UTF-8 (un PDF n'est jamais servi : il "
                                       "défait les retraits de sûreté des extraits)") from err
        if caviarder(texte)[0] != texte:
            raise DossierFermeInvalide(f"dossier fermé : {chemin} contient un secret (le caviardage le changerait) : refusé")
        pages, lignes = decouper_pages(texte)
        if e.get("pages") is not None and e["pages"] != len(pages):
            raise DossierFermeInvalide(f"dossier fermé : {chemin} déclare {e['pages']} pages, {len(pages)} trouvées")
        fichiers[chemin] = {"sha256": e["sha256"], "titre": caviarder(e["titre"])[0], "resume": caviarder(e["resume"])[0],
                            "sections": [caviarder(s)[0] for s in (e.get("sections") or [])], "pages_declarees": e.get("pages"),
                            "texte": texte, "pages": pages, "lignes": lignes}
    return DossierFerme(racine, index_sha256, fichiers)


def ecrire_index(dossier, entrees):
    """Aide (devis, essais) : écrit et scelle `index.json` pour des entrées {chemin, titre, resume[, sections, pages]} ;
    l'empreinte de chaque fichier est calculée ici."""
    from .outils import ecrire_json_scelle
    fichiers = []
    for e in entrees:
        e = dict(e)
        e["sha256"] = sha256_fichier(os.path.join(dossier, e["chemin"]))
        fichiers.append(e)
    chemin = os.path.join(os.path.realpath(dossier), NOM_INDEX)
    ecrire_json_scelle(chemin, {"fichiers": fichiers})
    return chemin


# --- protocole : demandes servies par le noyau ------------------------------------------------------------------------


def extraire_demandes(texte):
    """(demandes, motif) : la liste du dernier bloc JSON `{"demandes": [...]}` de la réponse, ou (None, None) s'il n'y en
    a pas ; (None, motif) si le bloc est mal formé. v47 : lecture partagée avec la moisson (`protocole_outils`)."""
    from .protocole_outils import extraire_bloc_demandes
    return extraire_bloc_demandes(texte, "demandes")


class CachePages:
    """R-444 : cache partagé des pages servies — une page servie à un proposeur est servie à un autre depuis le cache
    (même texte, même empreinte) ; chaque service est consigné."""

    def __init__(self, dossier):
        self.dossier = dossier
        self.entrees = {}  # (chemin, page) → {texte, sha256, servie_a: [...]}
        self.services = []

    def obtenir(self, chemin, numero, etiquette, passe, tour):
        cle = (chemin, numero)
        depuis_cache = cle in self.entrees
        if not depuis_cache:
            texte = self.dossier.page(chemin, numero)
            self.entrees[cle] = {"texte": texte, "sha256": hashlib.sha256(texte.encode("utf-8")).hexdigest(), "servie_a": []}
        e = self.entrees[cle]
        e["servie_a"].append(f"{etiquette}/passe-{passe}/tour-{tour}")
        self.services.append({"chemin": chemin, "page": numero, "etiquette": etiquette, "passe": passe, "tour": tour,
                              "depuis_cache": depuis_cache, "sha256": e["sha256"]})
        return e["texte"], e["sha256"], depuis_cache

    def resume(self):
        return {"entrees": len(self.entrees), "services": len(self.services),
                "servies_depuis_cache": sum(1 for s in self.services if s["depuis_cache"]),
                "par_page": {f"{c}|p.{n}": {"sha256": e["sha256"], "servie_a": list(e["servie_a"])}
                             for (c, n), e in sorted(self.entrees.items())},
                "services_detail": list(self.services)}


def _bornes_pages(pages):
    if pages is None:
        return None, None
    if not (isinstance(pages, list) and 1 <= len(pages) <= 2 and all(isinstance(p, int) and not isinstance(p, bool) for p in pages)):
        return None, "pages : [a, b] (entiers) attendu"
    a, b = (pages[0], pages[-1])
    if a < 1 or b < a:
        return None, "pages : 1 ≤ a ≤ b attendu"
    return (a, b), None


def servir_demandes(dossier, cache, demandes, etiquette, passe, tour, mesures, taille_max=TAILLE_MAX_SERVIE_PAR_TOUR,
                    moisson_active=False):
    """Sert les demandes d'un tour depuis le dossier fermé, rien d'autre ; rend la liste des réponses (une par demande,
    statut « servie » ou « refusée » avec motif). `mesures` (dict du proposeur et de la passe) reçoit les pages lues dans
    l'ordre, les recherches et les comptes. Au-delà de `taille_max` caractères servis dans le tour, une demande de
    lecture est refusée « à redemander au tour suivant ». v47 : `moisson_active` change seulement le motif du refus
    d'une demande `moissonner` (la moisson se demande au tour de moisson, par son propre bloc)."""
    reponses, servis = [], 0
    for d in demandes:
        mesures["demandes"]["total"] += 1
        types = [t for t in TYPES_DEMANDE if t in d]
        if len(types) != 1:
            mesures["demandes"]["refusees"] += 1
            reponses.append({"demande": d, "statut": "refusée", "motif": "demande inconnue : un seul de lire, chercher "
                             + ("(moissonner : au tour de moisson)" if moisson_active else "(moissonner : non disponible)")})
            continue
        t = types[0]
        if t == "moissonner":
            mesures["demandes"]["moissonner"] += 1
            mesures["demandes"]["refusees"] += 1
            reponses.append({"demande": d, "statut": "refusée", "motif": MOTIF_MOISSON_AU_TOUR if moisson_active else MOTIF_MOISSON})
            continue
        if t == "lire":
            mesures["demandes"]["lire"] += 1
            chemin = d.get("lire")
            if not isinstance(chemin, str) or chemin not in dossier.fichiers or set(d) - {"lire", "pages"}:
                mesures["demandes"]["refusees"] += 1
                reponses.append({"demande": d, "statut": "refusée", "motif": "hors du dossier fermé : chemin exact de "
                                 "l'index attendu (aucun autre fichier n'est servi)"})
                continue
            bornes, motif = _bornes_pages(d.get("pages"))
            if motif:
                mesures["demandes"]["refusees"] += 1
                reponses.append({"demande": d, "statut": "refusée", "motif": motif})
                continue
            existantes = sorted(dossier.fichiers[chemin]["pages"])
            voulues = existantes if bornes is None else [n for n in existantes if bornes[0] <= n <= bornes[1]]
            if not voulues:
                mesures["demandes"]["refusees"] += 1
                reponses.append({"demande": d, "statut": "refusée", "motif": f"aucune page de {chemin} dans cette plage "
                                 f"(pages : {existantes})"})
                continue
            textes, non_servies = [], []
            for n in voulues:
                taille = len(dossier.page(chemin, n))
                if servis + taille > taille_max:
                    non_servies.append(n)
                    continue
                texte, sha, depuis_cache = cache.obtenir(chemin, n, etiquette, passe, tour)
                servis += len(texte)
                textes.append({"page": n, "texte": texte})
                mesures["pages_lues"].append({"ordre": len(mesures["pages_lues"]) + 1, "tour": tour, "chemin": chemin,
                                              "page": n, "depuis_cache": depuis_cache, "sha256": sha})
            r = {"demande": d, "statut": "servie" if textes else "refusée", "chemin": chemin, "pages": textes}
            if non_servies:
                r["non_servies"] = non_servies
                r["motif"] = (f"au-delà de {taille_max} caractères servis dans ce tour : pages {non_servies} à redemander "
                              "au tour suivant")
            if not textes:
                mesures["demandes"]["refusees"] += 1
            reponses.append(r)
            continue
        mesures["demandes"]["chercher"] += 1
        motif = d.get("chercher")
        dans = d.get("dans")
        if not isinstance(motif, str) or not TAILLE_MIN_MOTIF <= len(motif) <= TAILLE_MAX_MOTIF or set(d) - {"chercher", "dans"} \
                or (dans is not None and dans not in dossier.fichiers):
            mesures["demandes"]["refusees"] += 1
            reponses.append({"demande": d, "statut": "refusée", "motif": f"chercher : motif de {TAILLE_MIN_MOTIF} à "
                             f"{TAILLE_MAX_MOTIF} caractères ; « dans » : chemin exact de l'index"})
            continue
        trouves, total = dossier.chercher(motif, dans)
        mesures["recherches"].append({"ordre": len(mesures["recherches"]) + 1, "tour": tour, "motif": motif, "dans": dans,
                                      "resultats": total})
        reponses.append({"demande": d, "statut": "servie", "resultats": [{"chemin": c, "page": n, "ligne": l} for c, n, l in trouves],
                         "total": total, "tronque": total > len(trouves)})
    return reponses


def nouvelles_mesures(mode):
    return {"mode": mode, "tours": 0, "demandes": {"total": 0, "lire": 0, "chercher": 0, "moissonner": 0, "refusees": 0},
            "pages_lues": [], "recherches": [], "versions_fiche": 0, "distances_entre_versions": [],
            "sous_avertissement": False, "avertissements": [], "journal_outils": None}


def resumer_mesures(mesures, dossier):
    """Ajoute pages distinctes, répétitions et part du dossier lu à des mesures de lecture."""
    vues = {}
    for p in mesures["pages_lues"]:
        cle = f"{p['chemin']}|p.{p['page']}"
        vues[cle] = vues.get(cle, 0) + 1
    total = dossier.pages_total
    return dict(mesures, pages_distinctes=len(vues), repetitions={k: v for k, v in sorted(vues.items()) if v > 1},
                part_du_dossier_lu=round(len(vues) / total, 6) if total else None)


def mesures_depuis_journal_outils(journal, dossier, racine_copie, mesures):
    """Outils du kit : pages lues (approximation lignes → pages pour `Read`), recherches (`Grep`, `Glob`) et comptes, depuis
    le journal du crochet."""
    for appel in journal or []:
        mesures["demandes"]["total"] += 1
        outil, e = appel.get("outil"), appel.get("entree") or {}
        if not appel.get("autorise"):
            mesures["demandes"]["refusees"] += 1
        if outil == "Read":
            mesures["demandes"]["lire"] += 1
            if appel.get("autorise"):
                chemin = os.path.relpath(os.path.realpath(e.get("file_path", "")) if os.path.isabs(e.get("file_path", ""))
                                         else os.path.realpath(os.path.join(racine_copie, e.get("file_path", ""))),
                                         os.path.realpath(racine_copie))
                debut = int(e.get("offset") or 1)
                nombre = int(e.get("limit") or LIGNES_READ_PAR_DEFAUT)
                for n in dossier.pages_de_lignes(chemin, debut, nombre):
                    mesures["pages_lues"].append({"ordre": len(mesures["pages_lues"]) + 1, "tour": appel.get("rang"),
                                                  "chemin": chemin, "page": n, "depuis_cache": None,
                                                  "approximation": "lignes → pages (Read du kit)"})
        elif outil in ("Grep", "Glob"):
            mesures["demandes"]["chercher"] += 1
            mesures["recherches"].append({"ordre": len(mesures["recherches"]) + 1, "tour": appel.get("rang"), "outil": outil,
                                          "motif": e.get("pattern"), "dans": e.get("path") or e.get("glob"),
                                          "resultats": None, "autorise": bool(appel.get("autorise"))})
    mesures["journal_outils"] = list(journal or [])
    return mesures


# --- L7 : vérification mécanique des citations ------------------------------------------------------------------------

CITATION = re.compile(r"\[\s*(?:(?P<fichier>[^\[\],]+?)\s*[,:;]?\s*)?p\.\s*(?P<page>\d+)\s*\]")
GUILLEMETS_AVANT = re.compile(r"(?:\"([^\"\n]{3,})\"|«\s*([^»\n]{3,}?)\s*»|“([^”\n]{3,})”)\s*[,;:]?\s*$")


def _passage_dans(passage, texte_page):
    """Vrai si chaque fragment du passage (coupé aux points de suspension), normalisé, se retrouve dans la page normalisée,
    dans l'ordre."""
    page = " " + normaliser_texte(texte_page) + " "
    position = 0
    fragments = [normaliser_texte(f) for f in re.split(r"\.\.\.|…|\[\s*\.\.\.\s*\]", passage)]
    fragments = [f for f in fragments if len(f) >= 3]
    if not fragments:
        return False
    for f in fragments:
        k = page.find(f, position)
        if k < 0:
            return False
        position = k + len(f)
    return True


def _mentions(texte, dossier):
    """[(position de fin, chemin)] des fichiers du dossier nommés dans le texte (chemin, nom de base, nom sans extension de
    trois caractères au moins)."""
    vus = []
    bas = texte.lower()
    for chemin in dossier.fichiers:
        noms = {chemin.lower(), os.path.basename(chemin).lower()}
        racine = os.path.splitext(os.path.basename(chemin))[0].lower()
        if len(racine) >= 3:
            noms.add(racine)
        for nom in noms:
            for m in re.finditer(re.escape(nom), bas):
                vus.append((m.end(), chemin))
    return vus


def verifier_citations_texte(textes, dossier):
    """Citations `[p.N]` des textes (chaînes feuilles d'une fiche) : (vérifiées, non attribuées). Une citation est
    attribuée au fichier nommé dans ses crochets (`[chemin, p.N]`) ou, à défaut, au dernier fichier du dossier nommé avant
    elle dans la même chaîne ; elle est vérifiée si la page existe et, quand un passage entre guillemets la précède, si ce
    passage se retrouve à la page."""
    verifiees, non_attribuees = [], []
    for texte in textes:
        mentions = _mentions(texte, dossier)
        for m in CITATION.finditer(texte):
            page = int(m.group("page"))
            nomme = m.group("fichier")
            chemin = dossier.trouver(nomme) if nomme else None
            if chemin is None and nomme is None:
                avant = [c for fin, c in mentions if fin <= m.start()]
                chemin = max(((fin, c) for fin, c in mentions if fin <= m.start()), default=(None, None))[1] if avant else None
            if chemin is None:
                non_attribuees.append({"citation": m.group(0), "motif": "aucun fichier du dossier fermé nommé"
                                       + (f" ({nomme!r} inconnu)" if nomme else "")})
                continue
            g = GUILLEMETS_AVANT.search(texte[:m.start()])
            passage = next((x for x in g.groups() if x), None) if g else None
            texte_page = dossier.page(chemin, page)
            existe = texte_page is not None
            retrouve = (_passage_dans(passage, texte_page) if existe else False) if passage else None
            ok = existe and (passage is None or bool(retrouve))
            verifiees.append({"citation": m.group(0), "fichier": chemin, "page": page, "page_existe": existe,
                              "passage": passage, "passage_retrouve": retrouve, "verifiee": ok,
                              "motif": ("page et passage retrouvés" if ok and passage else "page existante" if ok
                                        else "page absente du fichier" if not existe else "passage introuvable à la page")})
    return verifiees, non_attribuees
