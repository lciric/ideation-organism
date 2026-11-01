"""Outils communs : JSON canonique, empreintes, écriture scellée sans écrasement, graines, blocs JSON.

Bibliothèque standard seule.
"""

import datetime
import hashlib
import json
import math
import os
import re
import unicodedata


class EcrasementInterdit(FileExistsError):
    """Un fichier existe déjà : on n'écrase jamais (R12)."""


def json_canonique(objet):
    """Octets du JSON canonique : clés triées, séparateurs compacts, UTF-8, aucun NaN."""
    texte = json.dumps(objet, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    return texte.encode("utf-8")


def sha256_octets(octets):
    return hashlib.sha256(octets).hexdigest()


def empreinte_objet(objet):
    return sha256_octets(json_canonique(objet))


def sha256_fichier(chemin):
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for morceau in iter(lambda: f.read(1 << 16), b""):
            h.update(morceau)
    return h.hexdigest()


def ecrire_scelle(chemin, contenu, ecraser=False):
    """Écrit `contenu` (str ou octets) et son compagnon `.sha256` au format de sha256sum ; refuse d'écraser."""
    if isinstance(contenu, str):
        contenu = contenu.encode("utf-8")
    if os.path.exists(chemin) and not ecraser:
        raise EcrasementInterdit(chemin)
    os.makedirs(os.path.dirname(os.path.abspath(chemin)), exist_ok=True)
    with open(chemin, "wb") as f:
        f.write(contenu)
    empreinte = sha256_octets(contenu)
    with open(chemin + ".sha256", "w", encoding="utf-8") as f:
        f.write(f"{empreinte}  {os.path.basename(chemin)}\n")
    return empreinte


def dossier_traces(dossier_agent):
    """Dossier **voisin** de celui d'un agent, où l'orchestrateur écrit ses propres traces (consigne, réponse, produits).

    v7, version 5 (défaut 1 du premier lancement réel) : l'orchestrateur ne partage plus aucun nom de fichier avec un
    agent. En génération 1 de (a), une leçon de la mémoire (« toujours écrire reponse.txt ») a fait écrire aux agents le
    fichier que l'orchestrateur se réservait ; son écriture sans écrasement a échoué cinq fois sur cinq. Le dossier voisin
    est hors du dossier de l'agent : la garde des outils et le bac à sable lui en refusent l'écriture."""
    dossier_agent = os.path.normpath(os.path.abspath(dossier_agent))
    return os.path.join(os.path.dirname(dossier_agent), "traces-" + os.path.basename(dossier_agent))


def ecrire_json_scelle(chemin, objet, ecraser=False):
    texte = json.dumps(objet, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"
    return ecrire_scelle(chemin, texte, ecraser=ecraser)


def verifier_scelle(chemin):
    """Vrai si le fichier correspond à son compagnon `.sha256`."""
    try:
        with open(chemin + ".sha256", encoding="utf-8") as f:
            attendue = f.read().split()[0]
    except (OSError, IndexError):
        return False
    return os.path.exists(chemin) and sha256_fichier(chemin) == attendue


def graine_derivee(graine_maitresse, *etiquettes):
    """Graine entière sur 64 bits : 8 premiers octets de SHA-256(« graine|étiquette|… »).

    Le brief impose la bibliothèque standard : la dérivation par `numpy.random.SeedSequence` (R9) est remplacée
    par cette dérivation documentée, stable d'une plateforme à l'autre et indépendante de l'ordre des fils.
    """
    texte = "|".join([str(graine_maitresse)] + [str(e) for e in etiquettes])
    return int.from_bytes(hashlib.sha256(texte.encode("utf-8")).digest()[:8], "big")


def normaliser_texte(texte):
    """Minuscules, accents retirés, tout caractère non alphanumérique remplacé par une espace, espaces réduites."""
    decompose = unicodedata.normalize("NFD", texte)
    sans_accents = "".join(c for c in decompose if not unicodedata.combining(c))
    return re.sub(r"[^0-9a-z]+", " ", sans_accents.lower()).strip()


def nombre_fini(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


_DECODEUR = json.JSONDecoder()


def extraire_bloc_json(texte, cle_requise=None):
    """Dernier objet JSON du texte (bloc clôturé ```json d'abord, sinon objet nu) qui contient `cle_requise`."""
    if not isinstance(texte, str):
        return None
    trouves = []
    for bloc in re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", texte, flags=re.S):
        try:
            objet = json.loads(bloc)
        except ValueError:
            continue
        if isinstance(objet, dict):
            trouves.append(objet)
    if not trouves:
        for position in [m.start() for m in re.finditer(r"\{", texte)]:
            try:
                objet, _ = _DECODEUR.raw_decode(texte, position)
            except ValueError:
                continue
            if isinstance(objet, dict):
                trouves.append(objet)
    for objet in reversed(trouves):
        if cle_requise is None or cle_requise in objet:
            return objet
    return None


def horodatage(fourni=None):
    """Horodatage d'un journal : celui passé par l'opérateur (lu sur `date -u`), sinon l'horloge du processus."""
    if fourni:
        return {"valeur": fourni, "source": "argument --horodatage (date -u dans la commande de lancement)"}
    maintenant = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {"valeur": maintenant, "source": "horloge du processus (aucun --horodatage fourni)"}


def chemin_dans(dossier, chemin):
    """Vrai si `chemin` (absolu ou relatif à `dossier`) reste dans `dossier` après normalisation et liens résolus."""
    base = os.path.realpath(dossier)
    cible = chemin if os.path.isabs(chemin) else os.path.join(base, chemin)
    cible = os.path.realpath(os.path.normpath(cible))
    return cible == base or cible.startswith(base + os.sep)


def lister_fichiers(dossier):
    """Fichiers réguliers sous `dossier`, chemins relatifs triés."""
    sortie = []
    for racine, _, fichiers in os.walk(dossier):
        for nom in fichiers:
            sortie.append(os.path.relpath(os.path.join(racine, nom), dossier))
    return sorted(sortie)


def manifeste(**reglages):
    """Manifeste d'une exécution : versions, empreinte de chaque fichier du code du pôle, réglages et règle des graines."""
    import sys
    from . import __version__
    ici = os.path.dirname(os.path.abspath(__file__))
    code = {nom: sha256_fichier(os.path.join(ici, nom)) for nom in sorted(os.listdir(ici)) if nom.endswith(".py")}
    return {"version_pole": __version__, "python": sys.version.split()[0], "plateforme": sys.platform,
            "code_sha256": code, "regle_des_graines": "graine_derivee(graine maîtresse, étiquettes…) : 8 premiers octets "
            "de SHA-256 (bibliothèque standard imposée ; numpy.random.SeedSequence non utilisée)", "reglages": reglages}
