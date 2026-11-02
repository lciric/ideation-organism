"""Banc de mutations de la v62 (R5 : chaque correction neutralisée fait échouer son essai, pour la bonne raison) — cœur
(`pole/tour_ferme_v62.py`), évaluateur servi (`pole/evaluateur_lois_v62.py`), lecture gelée (`pole/lecture_tour_ferme_v62.py`),
lanceur (`demonstrations/tour_ferme_v62.py`) et programme de lecture (`demonstrations/lire_tour_ferme_v62.py`), ces deux derniers
chargés par `essais/test_tour_ferme_v62.py` sous « essais. » (le banc les atteint). Au moins une mutation par correction de la
contre-lecture 2 (B7/C8, B8/C9, B9/C10, C11 à C21). Mécanique du banc v56 (recompilation, raison attendue, restauration, témoin).

  python3 -I -B essais/mutations_tour_ferme_v62.py [--raisons]      (depuis le dossier orchestrator)
"""

import os
import sys
import traceback

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path[:0] = [RACINE, ICI]
sys.dont_write_bytecode = True

from essais import mutations_v56 as m56  # noqa: E402
from essais import test_tour_ferme_v62 as E  # noqa: E402  (charge le lanceur et le programme de lecture sous « essais. »)
from pole import evaluateur_lois_v62 as EV  # noqa: E402
from pole import lecture_tour_ferme_v62 as LE  # noqa: E402
from pole import tour_ferme_v62 as TF  # noqa: E402

m55 = m56.m55
LANCEUR, LECTEUR = E.LANCEUR, E.LECTEUR
TT = "essais.test_tour_ferme_v62."
NR = r"not raised"

MUTATIONS_V62 = [
    ("C8 (B7) : loi non servie dans le texte du test", TF, "texte_du_test", '+ MARQUE_LOI + json_canonique(loi).decode("utf-8"))', ")",
     [TT + "ServiceDeLaLoi"], r"C8 : loi absente"),
    ("C9 (B8) : grammaire non servie aux proposeurs", TF, "contexte_du_proposeur", '"grammaire": json.loads(json.dumps(GRAMMAIRE))},', "},",
     [TT + "GrammaireServie"], r"C9 : grammaire"),
    ("C9 : borne ±4 du gabarit non tenue", TF, "verifier_loi_servable", "if borne_softmax is not None and any(", "if False and any(",
     [TT + "GrammaireServie"], r"C9 : borne"),
    ("C10 (B9) : lectures attendues = générations jouées (v61)", LE, "lire_etage1",
     "lectures_attendues = sorted((x, g) for x in BRAS_ETAGE1 for g in range(2, n_gen + 1))  # B9 : jouées ou non",
     "lectures_attendues = sorted((x, g) for x, v in jouees.items() for g in v if g >= 2)", [TT + "LectureV62", TT + "CourseMuette"], r"B9"),
    ("C11 (I22) : machine jetable non vérifiée en mode réel", LANCEUR, "exiger_machine_jetable_reel",
     "exiger_machine_jetable_v56(environnement, permis_en_plus=permis)", "pass", [TT + "MachineJetable"], NR),
    ("C12 (I10) : session du proposeur en échec tue (« réponse illisible »)", TF.ProposeurAdaptateur, "proposer",
     'if r.statut != "ok" or r.erreur or refus is not None:', "if False:", [TT + "ProposeurChemin"], NR),
    ("C12 (I10) : exception d'une génération non convertie en arrêt à relevé partiel", TF, "jouer_etage_1",
     'arret = f"{type(e).__name__} : {str(e)[:500]}"', "raise", [TT + "Arrets"], r"C12"),
    ("C13 (I12) : part d'un relais ignorée", TF.Compteur, "ajouter",
     "if relais in self.parts and self.par_relais[relais] > self.parts[relais] + 1e-9:", "if False:", [TT + "PartsDesRelais"], NR),
    ("C13 (I12) : pire cas avant l'étage ignoré", TF.Compteur, "verifier_parts_avant_etage",
     "if relais in self.parts and self.parts[relais] - self.par_relais.get(relais, 0.0) < besoin - 1e-9:", "if False:",
     [TT + "PartsDesRelais"], NR),
    ("C13 (I12) : « budget_depasse » d'un relais pris pour le plafond de la fiche", TF.AdaptateurEtageV62, "lancer",
     'if r.statut == "budget_depasse" and (', "if False and (", [TT + "PartsDesRelais"], NR),
    ("C14 (I14) : gains écrits arrondis à 4 décimales", EV, "ecrire_gains", '"%d,%r\\n" % (i, x)', '"%d,%.4f\\n" % (i, x)',
     [TT + "PleinePrecision"], r"C14"),
    ("C14 (mineur 24) : copie de la tranche non vérifiée", TF, "contre_calculer",
     "if sha_attendue is not None and sha256_fichier(chemin_episodes) != sha_attendue:", "if False:", [TT + "PleinePrecision"], NR),
    ("garde 10 : contre-calcul tolérant (arrêt de bout en bout)", TF, "contre_calculer", "<= TOLERANCE_CONTRE_CALCUL", "<= 1.0",
     [TT + "Arrets"], r"arrondi|fabrique"),
    ("C15 (I15) : identifiant réel servi à l'étage", TF, "identifiant_opaque",
     'return "F-" + hashlib.sha256(f"{racine}|{tache}|{ident_reel}".encode("utf-8")).hexdigest()[:12]', "return ident_reel",
     [TT + "Aveugle"], r"C15"),
    ("C16 (I17) : A4 « promeut autant » sans carte réelle jugée (v61)", LE, "lire_etage1",
     "    elif not nr or not na:\n        a4 = A4_NON_MESURABLE  # I17 : jamais « promeut autant » sans carte réelle jugée\n    elif diff[0] > 0:",
     "    elif diff is not None and diff[0] > 0:", [TT + "LectureV62"], r"I17"),
    ("C16 (I16) : P4 sans cas", LE, "cas_p4", 'return "informative" if max(g2) > 0 else "vide"', 'return "informative"',
     [TT + "LectureV62"], r"I16"),
    ("C16 (I18) : recherche de la loi plantée absente acceptée", LE, "exiger_recherche",
     'raise ReleveInvalide("recherche de la loi plantée absente, nulle ou mal formée (S1, point 3) : relevé invalide")',
     'return {"contextes_cherches": 0, "touches": [], "lignes_de_tranche_dans_les_contextes": []}', [TT + "LectureV62"], NR),
    ("C16 (T34) : S5 sans le « non concluant » par bras", LE, "lire_etage1", '"S5_asymetrie": bool(s5_gardien or s5_nc)',
     '"S5_asymetrie": bool(s5_gardien)', [TT + "LectureV62"], r"S5"),
    ("C17 (I19) : sceau du préenregistrement non vérifié", LANCEUR, "lire_preenregistrement", "if not verifier_scelle(reel):", "if False:",
     [TT + "Garde6Complete"], NR),
    ("C17 (I19) : marqueur hors de l'étage 2 accepté", LANCEUR, "lire_preenregistrement",
     "restants = sorted(set(MARQUEUR.findall(hors_zone)))", "restants = []", [TT + "Garde6Complete"], NR),
    ("C18 (I20) : relevé non scellé lu", LECTEUR, "lire", "if not verifier_scelle(chemin):", "if False:", [TT + "CourseSaine"], r"C18"),
    ("C19 (I23) : la recopie de g lit le bilan réel de g", TF, "jouer_etage_1",
     'src = source_recopie if bras == "recopie_melange" else etat[bras]', 'src = etat["reel"] if bras == "recopie_melange" else etat[bras]',
     [TT + "CourseSaine"], r"C19"),
    ("C20 (I24) : monde planté non vérifié", LANCEUR, "verifier_monde", 'if monde.get("sha256") != sha_attendue:', "if False:",
     [TT + "MondeGele"], NR),
    ("C21 (mineur 21) : moteur « simule » en mode réel", LANCEUR, "moteur_de_l_etage", 'return "claude-sdk" if reel else "simule"',
     'return "simule"', [TT + "EtageV62"], r"C21"),
]


def principal(argv=None):
    argv = list(argv if argv is not None else sys.argv[1:])
    raisons = "--raisons" in argv
    noms = sorted({x for m in MUTATIONS_V62 for x in m[5]})
    for n in noms:
        m55.unittest.defaultTestLoader.loadTestsFromName(n)
    temoin = m55.jouer(noms)
    print(f"témoin (aucune mutation) : {temoin[0]} essais, {len(temoin[1])} en échec")
    for t, txt in temoin[1][:3]:
        print(f"      {t} : {m55._derniere_ligne(txt)}")
    comptes = {}
    for libelle, cible, nom, ancien, nouveau, essais, motif in MUTATIONS_V62:
        try:
            restaurer = m56.appliquer(cible, nom, ancien, nouveau)
        except (LookupError, OSError, TypeError, KeyError) as e:
            comptes["NON APPLIQUÉE"] = comptes.get("NON APPLIQUÉE", 0) + 1
            print(f"NON APPLIQUÉE  {libelle} : {type(e).__name__} : {e}")
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
    total = len(MUTATIONS_V62)
    print(f"mutations v62 : {total} ; tuées pour la raison attendue : {comptes.get('tuée', 0)} ; tuées pour une autre raison : "
          f"{comptes.get('TUÉE POUR UNE AUTRE RAISON', 0)} ; défaut du banc : {comptes.get('DÉFAUT DU BANC', 0)} ; survivantes : "
          f"{comptes.get('SURVIVANTE', 0)} ; non appliquées : {comptes.get('NON APPLIQUÉE', 0)}")
    print(f"témoin après restauration : {apres[0]} essais, {len(apres[1])} en échec")
    return 0 if comptes.get("tuée", 0) == total and not temoin[1] and not apres[1] else 1


if __name__ == "__main__":
    raise SystemExit(principal())
