"""Programme de lecture gelée de la plus petite course réelle de la boucle complète, version 65 (fichier neuf, R12).

Après la course, par un lecteur neuf (R13) : vérifie le sceau (compagnon `.sha256`) et, si elle est donnée, l'empreinte du rapport
`SORTIE/boucle-reelle-v65.json` ; vérifie qu'il vient du cœur v65 (champ `version`, « boucle-reelle-v65 ») ; applique
`pole.lecture_boucle_reelle_v65.lire_boucle` (critères C1 à C6 et audits A1 à A4 du brouillon 1, § 8 et 9) au champ `releve`, avec le
journal de la course (audit A1) ; écrit la lecture, scellée, dans un fichier neuf (jamais d'écrasement). Aucun appel de modèle,
aucun réseau.

  python3 -I -B demonstrations/lire_boucle_reelle_v65.py SORTIE LECTURE.json [--releve-sha256 SHA] [--rejeux-a2 200]
Codes : 0 lecture écrite ; 2 refus (rapport absent, non scellé, d'une autre empreinte, d'une autre version, lecture déjà présente).
"""

import argparse
import datetime
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

from pole import a_blanc_v59 as A  # noqa: E402
from pole import boucle_reelle_v65 as B  # noqa: E402
from pole import lecture_boucle_reelle_v65 as L  # noqa: E402
from pole.outils import ecrire_json_scelle, sha256_fichier, verifier_scelle  # noqa: E402

NOM_RAPPORT = "boucle-reelle-v65.json"


class LectureRefusee(RuntimeError):
    pass


def lire(sortie, sha_attendue=None, rejeux_a2=L.REJEUX_A2):
    """Rend (lecture, empreinte du rapport, mode) ; lève `LectureRefusee` sinon."""
    chemin = os.path.join(sortie, NOM_RAPPORT)
    if os.path.islink(chemin) or not os.path.isfile(chemin):
        raise LectureRefusee(f"rapport absent ou lien : {chemin}")
    if not verifier_scelle(chemin):
        raise LectureRefusee(f"rapport non scellé (compagnon .sha256 absent ou faux) : {chemin}")
    sha = sha256_fichier(chemin)
    if sha_attendue is not None and sha != sha_attendue:
        raise LectureRefusee(f"rapport d'empreinte {sha[:12]}… ≠ empreinte donnée {sha_attendue[:12]}…")
    with open(chemin, encoding="utf-8") as f:
        rapport = json.load(f)
    if not isinstance(rapport, dict) or not isinstance(rapport.get("releve"), dict):
        raise LectureRefusee("rapport sans champ « releve »")
    if rapport.get("version") != B.VERSION or rapport["releve"].get("version") != B.VERSION:
        raise LectureRefusee(f"rapport d'une autre version du cœur ({rapport.get('version')!r}) : la lecture v65 ne lit que {B.VERSION}")
    try:
        lecture = L.lire_boucle(rapport["releve"], A.charger_monde(RACINE), rejeux_a2=rejeux_a2, journal=rapport.get("journal"))
    except L.LectureImpossible as x:
        raise LectureRefusee(str(x)) from None
    return lecture, sha, rapport.get("mode")


def principal(argv=None):
    a = argparse.ArgumentParser(description="lecture gelée de la course réelle minimale de la boucle complète (v65)")
    a.add_argument("sortie")
    a.add_argument("lecture")
    a.add_argument("--releve-sha256")
    a.add_argument("--rejeux-a2", type=int, default=L.REJEUX_A2)
    args = a.parse_args(argv)
    try:
        if os.path.exists(args.lecture):
            raise LectureRefusee(f"lecture déjà présente : {args.lecture} (on n'écrase jamais)")
        lecture, sha, mode = lire(args.sortie, args.releve_sha256, args.rejeux_a2)
    except (LectureRefusee, OSError, ValueError) as x:
        print(f"refus : {type(x).__name__} : {x}", file=sys.stderr)
        return 2
    sortie = dict(lecture, rapport={"chemin": os.path.join(os.path.abspath(args.sortie), NOM_RAPPORT), "sha256": sha, "mode": mode},
                  lecteur=L.VERSION, lu_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"))
    sha_l = ecrire_json_scelle(args.lecture, sortie)
    print(json.dumps({"lecture_sha256": sha_l, "issue": lecture["issue"], "libelle": lecture["libelle"], "partielles": lecture["partielles"],
                      "audits_declenches": sorted(k for k, v in lecture["audits"].items() if v.get("declenche"))}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(principal())
