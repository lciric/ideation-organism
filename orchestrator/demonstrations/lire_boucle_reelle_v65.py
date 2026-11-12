"""Programme de lecture gelée de la plus petite course réelle de la boucle complète, version 65 (fichier neuf, R12 ; pièce M5).

Après la course, par un lecteur neuf (R13) : vérifie le sceau (compagnon `.sha256`) et, si elle est donnée, l'empreinte du relevé
`SORTIE/boucle-reelle-v65.json` ; vérifie qu'il vient du cœur v65 (champ `version`) ; applique `pole.lecture_boucle_reelle_v65.lire_boucle`
(critères C1 à C6 dans l'ordre du texte, audits A1 à A4 écrits avant la phrase de résultat, oracle lu une seule fois pour la
mesure P7) au seul champ `releve` ; écrit la lecture, scellée, dans un fichier neuf (jamais d'écrasement). Aucun appel de modèle.

  python3 -I -B demonstrations/lire_boucle_reelle_v65.py SORTIE LECTURE.json [--releve-sha256 SHA] [--sans-oracle]
Codes : 0 lecture écrite ; 2 refus (relevé absent, non scellé, d'une autre empreinte, d'une autre version, lecture déjà présente).
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
from pole import lecture_boucle_reelle_v65 as L  # noqa: E402
from pole.outils import ecrire_json_scelle, sha256_fichier, verifier_scelle  # noqa: E402

NOM_RELEVE = "boucle-reelle-v65.json"


class LectureRefusee(RuntimeError):
    pass


def lire(sortie, sha_attendue=None, oracle=True):
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
    if not isinstance(rapport, dict) or not isinstance(rapport.get("releve"), dict) or rapport.get("version") != L.VERSION_DU_COEUR:
        raise LectureRefusee(f"rapport d'une autre version ou sans relevé ({rapport.get('version') if isinstance(rapport, dict) else None!r})")
    monde = A.charger_monde(RACINE) if oracle else None
    if monde is not None and rapport["releve"].get("monde_sha256") not in (None, monde["sha256"]):
        raise LectureRefusee("monde planté d'une autre empreinte que celle du relevé")
    return L.lire_boucle(rapport["releve"], monde), sha, rapport.get("mode")


def principal(argv=None):
    a = argparse.ArgumentParser(description="lecture gelée de la boucle réelle (v65)")
    a.add_argument("sortie")
    a.add_argument("lecture")
    a.add_argument("--releve-sha256")
    a.add_argument("--sans-oracle", action="store_true")
    args = a.parse_args(argv)
    try:
        if os.path.exists(args.lecture):
            raise LectureRefusee(f"lecture déjà présente : {args.lecture} (on n'écrase jamais)")
        lecture, sha, mode = lire(args.sortie, args.releve_sha256, not args.sans_oracle)
    except (LectureRefusee, L.ReleveInvalide, OSError, ValueError) as x:
        print(f"refus : {type(x).__name__} : {x}", file=sys.stderr)
        return 2
    sortie = dict(lecture, releve={"chemin": os.path.join(os.path.abspath(args.sortie), NOM_RELEVE), "sha256": sha, "mode": mode},
                  lecteur=L.VERSION, lu_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"))
    sha_l = ecrire_json_scelle(args.lecture, sortie)
    print(json.dumps({"lecture_sha256": sha_l, "code": lecture["code"], "issue": lecture["issue"], "aussi": lecture["aussi"]},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(principal())
