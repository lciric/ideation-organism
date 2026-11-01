"""Banc de mutations de la v57b (R5 : chaque garde neutralisée doit faire échouer son essai, **pour la bonne raison**) — le
câblage du verdict calculé par le noyau (décision R-1057) : étage v5 (`pole/tests_de_mort_v5.py`), point de sélection entre
générations (`pole/etage_entre_generations_v57.py`), course 2 v57 (`pole/course2_v57.py`) ; essais `test_v57b_cablage_verdict`.

Reprend la mécanique du banc v55 par le banc v56 (`mutations_v56.appliquer` : recompilation en mémoire, substitution, raison
attendue de l'échec, défaut du banc distingué, restauration, témoin avant et après). **Seules les mutations de la v57b sont
jouées** : les bancs v54 à v57 ne sont pas rejoués ici (ils se jouent par `mutations_v57.py`). Aucun fichier n'est modifié.

  python3 -I -B essais/mutations_v57b.py [--raisons]      (depuis le dossier orchestrator)
"""

import os
import sys
import traceback

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path[:0] = [RACINE, ICI]
sys.dont_write_bytecode = True

from essais import mutations_v56 as m56  # noqa: E402  (mécanique m55 ; son principal n'est pas joué)
from pole import course2_v57 as C57  # noqa: E402
from pole import etage_entre_generations_v57 as E57  # noqa: E402
from pole import tests_de_mort_v5 as V5  # noqa: E402

m55 = m56.m55
T = "essais.test_v57b_cablage_verdict."
NR = m56.NR
VERDICT_AFFICHE = 'resultat["verdict"] = noyau["verdict"]'

MUTATIONS_V57B = [
    # 1. l'étage lit `RESULTAT:` (ou un autre témoin) au lieu du verdict du noyau
    ("v57b l'étage lit le chiffre imprimé (RESULTAT:, lecture mécanique) au lieu du verdict du noyau", V5, "executer_tests_de_mort",
     VERDICT_AFFICHE, 'resultat["verdict"] = mecanique["verdict"]', [T + "TestBoutEnBoutV57b", T + "TestDefautFermeEtMemeChemin"],
     r"'survit' != 'éliminée'|'survit' != 'non concluant'"),
    ("v57b le verdict du lecteur neuf (témoin) décide", V5, "executer_tests_de_mort", VERDICT_AFFICHE,
     'resultat["verdict"] = lu["verdict"]', [T + "TestBoutEnBoutV57b"], r"'survit' != 'éliminée'|'survit' != 'non concluant'"),
    ("v57b repli sur le chiffre du script quand le noyau refuse le préenregistrement", V5, "executer_tests_de_mort",
     "        except PreregRefuse as x:\n            raise EtageInterrompu(",
     "        except PreregRefuse as x:\n            noyau = dict(verdict_mecanique(prereg, executions), etiquette=ETIQUETTE_NOYAU, "
     "incidents=[])\n            if False: raise EtageInterrompu(", [T + "TestPreregAltere"], r"EtageInterrompu not raised"),
    ("v57b consigne de la v2 servie (le chiffre imprimé y reste « le chiffre lu »)", V5, "executer_tests_de_mort",
     "consigne = consigne_experimentateur(prereg, prereg_sha256, tranche, dossier, historique,",
     "consigne = _v2.consigne_experimentateur(prereg, prereg_sha256, tranche, dossier, historique,", [T + "TestBoutEnBoutV57b"],
     r"not found in|unexpectedly found in"),
    # 2. incident ignoré
    ("v57b incident ignoré par la règle du noyau (verdict_du_noyau_v5)", V5, "verdict_du_noyau_v5", "if incidents:", "if False:",
     [T + "TestVerdictDuNoyauV5", T + "TestBoutEnBoutV57b"],
     r"'survit' != 'non concluant'|\('(?:survit|éliminée)', '(?:survit|éliminée)'\) != \('non concluant'"),
    ("v57b incidents de la fiche non transmis au noyau par l'étage", V5, "executer_tests_de_mort",
     'verdict_du_noyau_v5(prereg, d_fiche, executions, resultat["incidents"])', "verdict_du_noyau_v5(prereg, d_fiche, executions, [])",
     [T + "TestBoutEnBoutV57b"], r"'survit' != 'non concluant'"),
    ("v57b incidents mal donnés acceptés (chaîne, objet)", V5, "verdict_du_noyau_v5", "if not isinstance(incidents, (list, tuple)):",
     "if False:", [T + "TestVerdictDuNoyauV5"], r"TypeError not raised"),
    # 3. sélection contournée
    ("v57b sélection contournée : « non concluant » gardé (seule « éliminée » sort)", E57, "selection_entre_generations",
     "retenus = {id(v) for v in selectionner(verdicts)}", 'retenus = {id(v) for v in verdicts if v.get("verdict") != "éliminée"}',
     [T + "TestBoutEnBoutV57b", T + "TestSelectionEntreGenerations"], r"Lists differ|VerdictNonNoyau not raised"),
    ("v57b sélection contournée : étiquette du noyau prêtée à un verdict qui ne la porte pas", E57, "selection_entre_generations",
     "        verdicts.append(v)\n",
     "        verdicts.append(v if isinstance(v, dict) and v.get(\"etiquette\") else {\"etiquette\": \"verdict calculé par le noyau "
     "depuis le fichier brut\", \"verdict\": r.get(\"verdict\"), \"motif\": None})\n",
     [T + "TestSelectionEntreGenerations", T + "TestDefautFermeEtMemeChemin", T + "TestJouerEtageV57", T + "TestCourse2V57"],
     r"VerdictNonNoyau not raised"),
    ("v57b sélection : verdict affiché ≠ verdict du noyau accepté", E57, "selection_entre_generations",
     'if isinstance(v, dict) and r.get("verdict") != v.get("verdict"):', "if False:", [T + "TestSelectionEntreGenerations"], NR),
    ("v57b course : point entre générations de la v56 (étage v3, aucune sélection)", C57, "executer_course_v57",
     "from .etage_entre_generations_v57 import jouer_etage_v57",
     "from .etage_entre_generations_v56 import jouer_etage_v56 as jouer_etage_v57", [T + "TestCourse2V57"],
     r"KeyError: '(?:selection|version_etage)'|VerdictNonNoyau not raised"),
    # 4. fiche sans bloc acceptée
    ("v57b fiche sans bloc acceptée : repli du validateur sur celui de la v2", V5, "valider_champ_test",
     "return valider_champ_test_v4(brut)",
     "return valider_champ_test_v4(brut) if isinstance(brut, dict) and CLE_STATISTIQUE in brut else _v2.valider_champ_test(brut)",
     [T + "TestValidateurEtPreregV5"], r"ChampTestInvalide not raised"),
    ("v57b fiche sans bloc acceptée : préenregistrement de la v2 à l'étage", V5, "executer_tests_de_mort",
     'prereg, motif = extraire_prereg_court(fiche, tranche, ligne["rang"], quotas)',
     'prereg, motif = _v2.extraire_prereg_court(fiche, tranche, ligne["rang"], quotas)', [T + "TestBoutEnBoutV57b"],
     r"sans bloc « statistique »"),
    ("v57b consigne écrite sans bloc", V5, "consigne_experimentateur", "    if bloc is None:\n        raise PreregSansStatistique(",
     "    if False:\n        raise PreregSansStatistique(", [T + "TestConsignesV5"],
     r"PreregSansStatistique not raised|'NoneType' object is not subscriptable"),
    # consignation
    ("v57b consignation : étiquette du noyau non vérifiée", V5, "ecrire_verdict_du_noyau_v5",
     'if not isinstance(verdict, dict) or verdict.get("etiquette") != ETIQUETTE_NOYAU:', "if not isinstance(verdict, dict):",
     [T + "TestConsignationV5"], r"VerdictNonNoyau not raised"),
]


def principal(argv=None):
    argv = list(argv if argv is not None else sys.argv[1:])
    raisons = "--raisons" in argv
    noms = sorted({x for m in MUTATIONS_V57B for x in m[5]})
    for n in noms:
        m55.unittest.defaultTestLoader.loadTestsFromName(n)
    temoin = m55.jouer(noms)
    print(f"témoin (aucune mutation) : {temoin[0]} essais, {len(temoin[1])} en échec")
    for t, txt in temoin[1][:5]:
        print(f"      {t} : {m55._derniere_ligne(txt)}")
    comptes = {}
    for libelle, cible, nom, ancien, nouveau, essais, motif in MUTATIONS_V57B:
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
    total = len(MUTATIONS_V57B)
    print(f"mutations v57b : {total} ; tuées pour la raison attendue : {comptes.get('tuée', 0)} ; tuées pour une autre raison : "
          f"{comptes.get('TUÉE POUR UNE AUTRE RAISON', 0)} ; défaut du banc : {comptes.get('DÉFAUT DU BANC', 0)} ; survivantes : "
          f"{comptes.get('SURVIVANTE', 0)} ; non appliquées : {comptes.get('NON APPLIQUÉE', 0)}")
    print(f"témoin après restauration : {apres[0]} essais, {len(apres[1])} en échec")
    return 0 if comptes.get("tuée", 0) == total and not temoin[1] and not apres[1] else 1


if __name__ == "__main__":
    raise SystemExit(principal())
