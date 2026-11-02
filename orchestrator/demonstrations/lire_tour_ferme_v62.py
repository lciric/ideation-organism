"""Lecture gelée de l'étage 1 du tour fermé, version 62 (fichier neuf, R12 ; contre-lecture 2, I20 et C18).

Après la course, par un lecteur neuf (R13) : vérifie le sceau (compagnon `.sha256`) et, si elle est donnée, l'empreinte du relevé
`SORTIE/tour-ferme-v1-etage1.json` ; applique `pole.lecture_tour_ferme_v62.lire_tour_etage_1` au seul champ `releve` ; écrit
la lecture, scellée, dans un fichier neuf (jamais d'écrasement). Aucun appel de modèle, aucun réseau.

  python3 -I -B demonstrations/lire_tour_ferme_v62.py SORTIE LECTURE.json [--releve-sha256 SHA]
Codes : 0 lecture écrite ; 2 refus (relevé absent, non scellé, d'une autre empreinte, lecture déjà présente).
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

from pole import lecture_tour_ferme_v62 as L  # noqa: E402
from pole.outils import ecrire_json_scelle, sha256_fichier, verifier_scelle  # noqa: E402

NOM_RELEVE = "tour-ferme-v1-etage1.json"


class LectureRefusee(RuntimeError):
    pass


def lire(sortie, sha_attendue=None):
    """Rend (lecture, empreinte du relevé, mode) ; lève `LectureRefusee` si le relevé n'est pas scellé ou n'a pas l'empreinte dite."""
    chemin = os.path.join(sortie, NOM_RELEVE)
    if os.path.islink(chemin) or not os.path.isfile(chemin):
        raise LectureRefusee(f"relevé absent ou lien : {chemin}")
    if not verifier_scelle(chemin):
        raise LectureRefusee(f"relevé non scellé (compagnon .sha256 absent ou faux) : {chemin}")
    sha = sha256_fichier(chemin)
    if sha_attendue is not None and sha != sha_attendue:
        raise LectureRefusee(f"relevé d'empreinte {sha[:12]}… ≠ empreinte donnée {sha_attendue[:12]}…")
    with open(chemin, encoding="utf-8") as f:
        rapport = json.load(f)
    if not isinstance(rapport, dict) or not isinstance(rapport.get("releve"), dict):
        raise LectureRefusee("rapport sans champ « releve »")
    return L.lire_tour_etage_1(rapport["releve"]), sha, rapport.get("mode")


def principal(argv=None):
    a = argparse.ArgumentParser(description="lecture gelée de l'étage 1 du tour fermé (v62)")
    a.add_argument("sortie")
    a.add_argument("lecture")
    a.add_argument("--releve-sha256")
    args = a.parse_args(argv)
    try:
        if os.path.exists(args.lecture):
            raise LectureRefusee(f"lecture déjà présente : {args.lecture} (on n'écrase jamais)")
        lecture, sha, mode = lire(args.sortie, args.releve_sha256)
    except (LectureRefusee, OSError, ValueError) as x:
        print(f"refus : {type(x).__name__} : {x}", file=sys.stderr)
        return 2
    sortie = dict(lecture, releve={"chemin": os.path.join(os.path.abspath(args.sortie), NOM_RELEVE), "sha256": sha, "mode": mode},
                  lecteur=L.VERSION, lu_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"))
    sha_l = ecrire_json_scelle(args.lecture, sortie)
    print(json.dumps({"lecture_sha256": sha_l, "issue_etage_1": lecture["etage_1"]["issue_etage_1"],
                      "issue_a4": lecture["etage_1"].get("issue_a4")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(principal())
