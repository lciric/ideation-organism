"""Banc de mutations de la v57 (R5 : chaque garde neutralisée doit faire échouer son essai, **pour la bonne raison**).

Reprend la mécanique du banc v55 par le banc v56 (`mutations_v56` : recompilation en mémoire, raison attendue de l'échec, défaut
du banc distingué, restauration et témoin), ses listes (v54, v55, v56) et ajoute les mutations du verdict calculé par le noyau
(`pole/tests_de_mort_v4.py`, décision R-1057 ; essais `test_v57_verdict_noyau`). Aucun fichier n'est modifié.

  python3 -I -B essais/mutations_v57.py [--raisons] [--v57-seulement]      (depuis le dossier orchestrator)
"""

import os
import sys
import traceback

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path[:0] = [RACINE, ICI]
sys.dont_write_bytecode = True

from essais import mutations_v56 as m56  # noqa: E402  (mécanique m55, listes v54 à v56 ; son principal n'est pas joué)
from pole import tests_de_mort_v4 as V4  # noqa: E402

m55 = m56.m55
T = "essais.test_v57_verdict_noyau."
NR = m56.NR
NON_CONCLUANT_ATTENDU = r"'(?:survit|éliminée)' != 'non concluant'"

MUTATIONS_V57 = [
    # les trois mutations demandées
    ("R-1057 comparateur inversé", V4, "verdict_du_noyau", "survit = comparer(valeur, comparateur, seuil)",
     "survit = not comparer(valeur, comparateur, seuil)", [T + "TestVerdictCasSain"], r"'éliminée' != 'survit'|'survit' != 'éliminée'"),
    ("R-1057 chiffre du script lu à la place du fichier", V4, "verdict_du_noyau",
     "valeur, motif, info = lire_fichier_brut(dossier_sortie, e, bloc)",
     "valeur, motif, info = (chiffre, None, None) if chiffre is not None else lire_fichier_brut(dossier_sortie, e, bloc)",
     [T + "TestArtefact1ChiffreDuScript", T + "TestArtefact3FichierAbsent", T + "TestArtefact4FichierIllisible"],
     r"'survit' != 'éliminée'|'éliminée' != 'survit'|" + NON_CONCLUANT_ATTENDU),
    ("R-1057 « non concluant » rangé comme « survit »", V4, "rang_verdict",
     "if verdict == \"non concluant\":\n        return 0", "if verdict == \"non concluant\":\n        return 2",
     [T + "TestRangEtSelection"], r"2 not less than or equal to 1|Lists differ"),
    # sélection
    ("R-1057 sélection : « non concluant » gardé (seule « éliminée » sort)", V4, "selectionner",
     "if rang_verdict(v.get(\"verdict\")) == rang_verdict(\"survit\"):", "if v.get(\"verdict\") != \"éliminée\":",
     [T + "TestRangEtSelection"], r"Lists differ"),
    ("R-1057 sélection : étiquette du noyau non vérifiée", V4, "selectionner",
     "if not isinstance(v, dict) or v.get(\"etiquette\") != ETIQUETTE_NOYAU:", "if not isinstance(v, dict):",
     [T + "TestRangEtSelection.test_selection_refuse_un_verdict_hors_noyau"], r"VerdictNonNoyau not raised"),
    # préenregistrement
    ("R-1057 bloc statistique non exigé", V4, "verdict_du_noyau", "if bloc is None:", "if False:",
     [T + "TestArtefact5PreregSansStatistique"], r"PreregSansStatistique not raised|'NoneType' object is not iterable"),
    ("R-1057 sceau du préenregistrement non vérifié", V4, "prereg_scelle",
     "if _empreinte_scellee(dossier_sortie, NOM_PREREG) != empreinte:", "if False:", [T + "TestPreregScelle"],
     r"PreregNonScelle not raised"),
    ("R-1057 préenregistrement scellé non comparé au préenregistrement passé", V4, "prereg_scelle", "if scelle != passe:", "if False:",
     [T + "TestPreregScelle"], r"PreregNonScelle not raised"),
    # exécution et fichier lus
    ("R-1057 exécution non réussie lue", V4, "derniere_execution_reussie", "e.get(\"statut\") == \"réussie\"",
     "e.get(\"statut\") is not None", [T + "TestExecutionLue", T + "TestArtefact3FichierAbsent"],
     r"'survit' != 'éliminée'|" + NON_CONCLUANT_ATTENDU),
    ("R-1057 première exécution réussie lue au lieu de la dernière", V4, "derniere_execution_reussie",
     "for e in reversed(list(executions or [])):", "for e in list(executions or []):", [T + "TestExecutionLue"],
     r"'survit' != 'éliminée'|" + NON_CONCLUANT_ATTENDU),
    ("R-1057 numéro de l'exécution non vérifié (verdict)", V4, "verdict_du_noyau",
     "if isinstance(numero, bool) or not isinstance(numero, int) or numero < 0:", "if False:",
     [T + "TestExecutionLue.test_execution_reussie_sans_numero_utilisable"], r"KeyError: 'numero'"),
    ("R-1057 numéro de l'exécution non vérifié (lecture du fichier)", V4, "lire_fichier_brut",
     "if isinstance(numero, bool) or not isinstance(numero, int) or numero < 0:", "if False:",
     [T + "TestExecutionLue.test_execution_reussie_sans_numero_utilisable"], r"Unknown format code|'numéro' not found"),
    ("R-1057 fichier inscrit deux fois accepté", V4, "lire_fichier_brut", "if len(entrees) > 1:", "if False:",
     [T + "TestCopieScellee.test_inventaire_incoherent"], NON_CONCLUANT_ATTENDU),
    ("R-1057 copie inscrite sous un autre nom acceptée", V4, "lire_fichier_brut", "if entree.get(\"copie\") != copie:", "if False:",
     [T + "TestCopieScellee.test_inventaire_incoherent"], NON_CONCLUANT_ATTENDU),
    ("R-1057 copie non comparée à l'inventaire", V4, "lire_fichier_brut", "if empreinte != entree.get(\"sha256\"):", "if False:",
     [T + "TestCopieScellee"], NON_CONCLUANT_ATTENDU),
    ("R-1057 sceau de la copie non vérifié", V4, "lire_fichier_brut",
     "if _empreinte_scellee(dossier_sortie, relatif) != empreinte:", "if False:", [T + "TestCopieScellee"], NON_CONCLUANT_ATTENDU),
    ("R-1057 erreur CSV non rattrapée", V4, "lire_fichier_brut", "except csv.Error as x:", "except ZeroDivisionError as x:",
     [T + "TestArtefact4FichierIllisible"], r"field larger than field limit"),
    ("R-1057 statistique non finie acceptée", V4, "lire_fichier_brut", "if not math.isfinite(valeur):", "if False:",
     [T + "TestArtefact4FichierIllisible"], NON_CONCLUANT_ATTENDU),
    # témoin
    ("R-1057 concordance du témoin toujours vraie", V4, "concordance_du_temoin", "return abs(chiffre - valeur) <= tolerance",
     "return True", [T + "TestArtefact1ChiffreDuScript"], r"True is not False"),
]


def principal(argv=None):
    argv = list(argv if argv is not None else sys.argv[1:])
    raisons, seulement = "--raisons" in argv, "--v57-seulement" in argv
    tout = [] if seulement else [(lib, cib, nom, anc, nou, ess, m55.MOTIFS_V54.get(lib, r"(?!)")) for lib, cib, nom, anc, nou, ess in m55.m54.MUTATIONS]
    tout += [] if seulement else m55.MUTATIONS_V55 + m56.MUTATIONS_V56
    tout += MUTATIONS_V57
    noms = sorted({x for m in tout for x in m[5]})
    for n in noms:
        m55.unittest.defaultTestLoader.loadTestsFromName(n)
    temoin = m55.jouer(noms)
    print(f"témoin (aucune mutation) : {temoin[0]} essais, {len(temoin[1])} en échec")
    for t, txt in temoin[1][:5]:
        print(f"      {t} : {m55._derniere_ligne(txt)}")
    comptes, v57, v56 = {}, {id(m) for m in MUTATIONS_V57}, {id(m) for m in m56.MUTATIONS_V56}
    for m in tout:
        libelle, cible, nom, ancien, nouveau, essais, motif = m
        couche = "v57" if id(m) in v57 else "v56" if id(m) in v56 else ("v54" if libelle in m55.MOTIFS_V54 else "v55")
        try:
            restaurer = m56.appliquer(cible, nom, ancien, nouveau)
        except (LookupError, OSError, TypeError) as e:
            comptes["NON APPLIQUÉE"] = comptes.get("NON APPLIQUÉE", 0) + 1
            print(f"NON APPLIQUÉE  [{couche}] {libelle} : {e}")
            continue
        try:
            n, echecs = m55.jouer(essais)
        except Exception:  # noqa: BLE001
            n, echecs = 0, [("chargement", traceback.format_exc())]
        finally:
            restaurer()
        verdict = m55.classer(echecs, motif)
        comptes[verdict] = comptes.get(verdict, 0) + 1
        print(f"{verdict}  [{couche}] {libelle} : {len(echecs)}/{n} essais en échec")
        if raisons or verdict != "tuée":
            for t, txt in echecs[:3]:
                print(f"      {t} : {m55._derniere_ligne(txt)}")
    apres = m55.jouer(noms)
    total = len(tout)
    print(f"mutations : {total} (v57 : {len(MUTATIONS_V57)}"
          + ("" if seulement else f", v56 : {len(m56.MUTATIONS_V56)}, v55 : {len(m55.MUTATIONS_V55)}, v54 : {len(m55.m54.MUTATIONS)}")
          + f") ; tuées pour la raison attendue : {comptes.get('tuée', 0)} ; tuées pour une autre raison : "
          f"{comptes.get('TUÉE POUR UNE AUTRE RAISON', 0)} ; défaut du banc : {comptes.get('DÉFAUT DU BANC', 0)} ; survivantes : "
          f"{comptes.get('SURVIVANTE', 0)} ; non appliquées : {comptes.get('NON APPLIQUÉE', 0)}")
    print(f"témoin après restauration : {apres[0]} essais, {len(apres[1])} en échec")
    return 0 if comptes.get("tuée", 0) == total and not temoin[1] and not apres[1] else 1


if __name__ == "__main__":
    raise SystemExit(principal())
