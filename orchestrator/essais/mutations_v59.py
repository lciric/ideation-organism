"""Banc de mutations de la v59 (R5 : chaque garde neutralisée doit faire échouer son essai, **pour la bonne raison**) — boucle
fermée entre générations (`pole/boucle_fermee_v59.py`), mode à blanc (`pole/a_blanc_v59.py`), proposeurs de référence
(`pole/proposeurs_references_v59.py`) ; essais `essais/test_v59_boucle_fermee.py`.

Mécanique du banc v56 (`mutations_v56.appliquer` : recompilation en mémoire, substitution, raison attendue de l'échec, défaut du
banc distingué, restauration, témoin avant et après). Seules les mutations de la v59 sont jouées. Aucun fichier n'est modifié.
Le témoin et chaque mutation jouent l'essai du vrai bac à sable s'il est joué (sinon il est ignoré avec son motif, si la
variable `POLE_ESSAI_BAC_REEL_NON_JOUE=1` est posée).

  python3 -I -B essais/mutations_v59.py [--raisons]      (depuis le dossier orchestrator)
"""

import os
import sys
import traceback

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path[:0] = [RACINE, ICI]
sys.dont_write_bytecode = True

from essais import mutations_v56 as m56  # noqa: E402
from pole import a_blanc_v59 as AB  # noqa: E402
from pole import boucle_fermee_v59 as BF  # noqa: E402
from pole import proposeurs_references_v59 as PR  # noqa: E402

m55 = m56.m55
T = "essais.test_v59_boucle_fermee."

MUTATIONS_V59 = [
    ("v59 la génération suivante ignore la sélection (héritage initial au lieu de la lecture)", AB, "jouer_bras",
     "heritage = bf.lire_heritage(dossier_prec, sha_prec)", "heritage = bf.heritage_initial()", [T + "TestBoutEnBoutABlanc"],
     r"None != '[0-9a-f]{64}'|Lists differ"),
    ("v59 l'empreinte de la sélection n'est pas vérifiée", BF, "lire_scelle_verifie", "if sha != sha256_attendu:", "if False:",
     [T + "TestLectureHeritageV59"], r"SelectionNonVerifiee not raised"),
    ("v59 un test de mort échoué compte comme survivant", BF, "survivantes_des_verdicts", 'if v.get("verdict") == "survit":',
     'if v.get("verdict") != "non concluant":', [T + "TestVueEtSurvivantes", T + "TestBoutEnBoutABlanc"],
     r"Lists differ|HeritageRefuse|contre-vérification"),
    ("v59 la contre-vérification des retenues est sautée", BF, "lire_heritage", "if sorted(retenues) != derivees:", "if False:",
     [T + "TestLectureHeritageV59"], r"HeritageRefuse not raised"),
    ("v59 le bac à sable est contourné en silence (repli sur le factice sans bwrap)", AB, "choisir_executeur",
     "    if not which(\"bwrap\"):\n        raise BacASableIndisponible(",
     "    if not which(\"bwrap\"):\n        return v5.ExecuteurFactice(delai_s=60.0), {\"nom\": \"factice\", \"factice\": True}\n"
     "        raise BacASableIndisponible(", [T + "TestBacASableV59"], r"BacASableIndisponible not raised"),
    ("v59 la graine n'est pas dérivée de la tâche", BF, "graine_de_tache",
     "ss = np.random.SeedSequence(racine, spawn_key=(cle_de_tache(tache),))", "ss = np.random.SeedSequence(racine, spawn_key=())",
     [T + "TestGrainesV59"], r"\d+ == \d+|\d+ != \d+"),
    ("v59 un proposeur de référence voit le verdict du juge (évaluations servies avec la vue)", AB, "jouer_generation",
     "vue = bf.vue_pour_proposeur(heritage)",
     "vue = dict(bf.vue_pour_proposeur(heritage), evaluations={i: {\"promue\": True} for i in heritage[\"archive\"]})",
     [T + "TestBoutEnBoutABlanc"], r"VueAvecVerdict"),
    ("v59 la garde de la vue est neutralisée", BF, "exiger_vue_sans_verdict", "    if trouvees:\n", "    if False:\n",
     [T + "TestVueEtSurvivantes"], r"VueAvecVerdict not raised"),
    ("v59 le proposeur aléatoire ne vérifie pas sa vue", PR, "proposer_aleatoire", "    exiger_vue_sans_verdict(vue)\n",
     "    pass\n", [T + "TestVueEtSurvivantes"], r"VueAvecVerdict not raised"),
]


def principal(argv=None):
    argv = list(argv if argv is not None else sys.argv[1:])
    raisons = "--raisons" in argv
    noms = sorted({x for m in MUTATIONS_V59 for x in m[5]})
    for n in noms:
        m55.unittest.defaultTestLoader.loadTestsFromName(n)
    temoin = m55.jouer(noms)
    print(f"témoin (aucune mutation) : {temoin[0]} essais, {len(temoin[1])} en échec")
    for t, txt in temoin[1][:5]:
        print(f"      {t} : {m55._derniere_ligne(txt)}")
    comptes = {}
    for libelle, cible, nom, ancien, nouveau, essais, motif in MUTATIONS_V59:
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
    total = len(MUTATIONS_V59)
    print(f"mutations v59 : {total} ; tuées pour la raison attendue : {comptes.get('tuée', 0)} ; tuées pour une autre raison : "
          f"{comptes.get('TUÉE POUR UNE AUTRE RAISON', 0)} ; défaut du banc : {comptes.get('DÉFAUT DU BANC', 0)} ; survivantes : "
          f"{comptes.get('SURVIVANTE', 0)} ; non appliquées : {comptes.get('NON APPLIQUÉE', 0)}")
    print(f"témoin après restauration : {apres[0]} essais, {len(apres[1])} en échec")
    return 0 if comptes.get("tuée", 0) == total and not temoin[1] and not apres[1] else 1


if __name__ == "__main__":
    raise SystemExit(principal())
