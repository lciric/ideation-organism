"""Banc de mutations de la v61 (R5 : chaque garde neutralisée fait échouer son essai, pour la bonne raison) — cœur du tour fermé
(`pole/tour_ferme_v61.py`), lecture gelée v61 (`pole/lecture_tour_ferme_v61.py`), réserve durcie
(`pole/reserve_tenue_a_l_ecart_v61.py`). Mécanique du banc v56. Les mutations C3 de la contre-lecture y sont : « T2 attend 8
passes quand la recopie joue une génération », « contre-calcul absent accepté », « T-ELIM jamais testé accepté », « lectures
d'héritage manquantes acceptées », « cause de A4 ignorée » ; plus : témoin dans l'archive accepté, seuil du proposeur accepté,
contre-calcul tolérant, familles non séparées acceptées, décision hors liste acceptée, orthographe des tâches ignorée.

  python3 -I -B essais/mutations_v61.py [--raisons]      (depuis le dossier orchestrator)
"""

import os
import sys
import traceback

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path[:0] = [RACINE, ICI]
sys.dont_write_bytecode = True

from essais import mutations_v56 as m56  # noqa: E402
from pole import lecture_tour_ferme_v61 as LE  # noqa: E402
from pole import reserve_tenue_a_l_ecart_v61 as RV  # noqa: E402
from pole import tour_ferme_v61 as TF  # noqa: E402

m55 = m56.m55
TL = "essais.test_v61_lecture_tour_ferme."
TT = "essais.test_v61_tour_ferme."
TR = "essais.test_v61_reserve_tenue_a_l_ecart."
PAS_LEVEE = r"not raised"

MUTATIONS_V61 = [
    ("v61 lecture : T2 attend 8 passes codées en dur (B4)", LE, "lire_etage1", "t2 = (len(vraie) == attendues and attendues > 0",
     "attendues = 8 if jouees['recopie_melange'] else 6\n    t2 = (len(vraie) == attendues and attendues > 0", [TL + "Etage1"], r"8 != 7"),
    ("v61 lecture : contre-calcul absent accepté (B5)", LE, "exiger_contre_calculs", "if sans:", "if False:", [TL + "Etage1", TL + "Etage2"],
     r"ReleveInvalide not raised|'Z' != 'N'"),
    ("v61 lecture : T-ELIM jamais « éliminée » accepté (I5)", LE, "lire_etage1", 'sum(c.get("verdict") == "éliminée" for c in elim) >= attendues - 1',
     'sum(c.get("verdict") == "éliminée" for c in elim) >= 0', [TL + "Etage1"], r"True is not false"),
    ("v61 lecture : lectures d'héritage manquantes acceptées (I5)", LE, "lire_etage1", "and lectures_faites == lectures_attendues", "",
     [TL + "Etage1"], r"True is not false"),
    ("v61 lecture : cause de A4 ignorée (B3)", LE, "lire_etage1", "cause = A4_SENSIBILITE if (diff_info is not None and diff_info[0] > 0) else A4_TAILLE",
     "cause = A4_TAILLE", [TL + "Etage1"], r"!="),
    ("v61 lecture : T4 par bras seulement (I5)", LE, "lire_etage1", "t4 = ((nc / testees if testees else 0.0) <= SEUIL_INCONCLUSIF\n          and",
     "t4 = (", [TL + "Etage1"], r"True is not false"),
    ("v61 cœur : témoin dans l'archive accepté (garde 7)", TF, "exiger_sans_temoin", "if presents:", "if False:", [TT + "Garde7"], PAS_LEVEE),
    ("v61 cœur : seuil du proposeur accepté (garde 8)", TF, "completer_carte", "if en_trop or manquantes:", "if manquantes:", [TT + "Garde8"],
     r"is not None"),
    ("v61 cœur : contre-calcul tolérant (garde 10)", TF, "contre_calculer", "<= TOLERANCE_CONTRE_CALCUL", "<= 1.0", [TT + "Garde10"], r"True is not false"),
    ("v61 cœur : familles non séparées acceptées (garde 9)", TF, "exiger_familles_separees", "or experimentateur[1] == verificateur[1]", "",
     [TT + "Garde9"], PAS_LEVEE),
    ("v61 cœur : décision hors liste acceptée", TF, "verifier_decisions", "if decisions[k] not in permises:", "if False:", [TT + "Decisions"],
     PAS_LEVEE),
    ("v61 cœur : plafond de dépense ignoré (garde 5)", TF.Compteur, "ajouter", "if self.usd > self.plafond_usd:", "if False:", [TT + "Garde5Et13"],
     PAS_LEVEE),
    ("v61 réserve : orthographe des tâches ignorée (I3)", RV, "verifier_orthographe", "if ecarts:", "if False:", [TR + "Orthographe"], PAS_LEVEE),
    ("v61 réserve : recherche sur la forme exacte seulement (I3)", RV, "taches_reservees_dans", "or normaliser(t) in texte", "", [TR + "Contexte"],
     r"!="),
    ("v61 réserve : disjonction sans la forme normalisée (I3)", RV, "verifier_disjonction", "reservees = set(taches_reservees) | {normaliser(t) for t in taches_reservees}", "reservees = set(taches_reservees)",
     [TR + "Disjonction"], PAS_LEVEE),
]


def principal(argv=None):
    argv = list(argv if argv is not None else sys.argv[1:])
    raisons = "--raisons" in argv
    noms = sorted({x for m in MUTATIONS_V61 for x in m[5]})
    for n in noms:
        m55.unittest.defaultTestLoader.loadTestsFromName(n)
    temoin = m55.jouer(noms)
    print(f"témoin (aucune mutation) : {temoin[0]} essais, {len(temoin[1])} en échec")
    comptes = {}
    for libelle, cible, nom, ancien, nouveau, essais, motif in MUTATIONS_V61:
        try:
            restaurer = m56.appliquer(cible, nom, ancien, nouveau)
        except (LookupError, OSError, TypeError) as e:
            comptes["NON APPLIQUÉE"] = comptes.get("NON APPLIQUÉE", 0) + 1
            print(f"NON APPLIQUÉE  {libelle} : {e}")
            continue
        try:
            n, echecs = m55.jouer(essais)
        except Exception:  # noqa: BLE001
            n, echecs = 0, [("chargement", traceback.format_exc())]
        finally:
            restaurer()
        verdict = m55.classer(echecs, motif)
        comptes[verdict] = comptes.get(verdict, 0) + 1
        print(f"{verdict}  {libelle} : {len(echecs)}/{n} essais en échec")
        if raisons or verdict != "tuée":
            for t, txt in echecs[:3]:
                print(f"      {t} : {m55._derniere_ligne(txt)}")
    apres = m55.jouer(noms)
    total = len(MUTATIONS_V61)
    print(f"mutations v61 : {total} ; tuées pour la raison attendue : {comptes.get('tuée', 0)} ; tuées pour une autre raison : "
          f"{comptes.get('TUÉE POUR UNE AUTRE RAISON', 0)} ; défaut du banc : {comptes.get('DÉFAUT DU BANC', 0)} ; survivantes : "
          f"{comptes.get('SURVIVANTE', 0)} ; non appliquées : {comptes.get('NON APPLIQUÉE', 0)}")
    print(f"témoin après restauration : {apres[0]} essais, {len(apres[1])} en échec")
    return 0 if comptes.get("tuée", 0) == total and not temoin[1] and not apres[1] else 1


if __name__ == "__main__":
    raise SystemExit(principal())
