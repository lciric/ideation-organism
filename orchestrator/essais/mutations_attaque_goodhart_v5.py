"""Banc de mutations de l'attaque de Goodhart v5 (R5 : chaque garde neuve neutralisée doit faire échouer son essai, **pour la
bonne raison**). Mécanique de `essais/mutations_attaque_goodhart_v4.py` (source de la fonction relue, fragment remplacé une seule
fois, recompilé dans l'espace réel du module, substitué, puis restauré ; raison attendue propre à chaque mutation ; défaut du banc
distingué ; témoin avant et après). Fichier neuf (R12) ; aucun fichier n'est modifié ; aucun réseau, aucune course décisive. Cibles :
- `pole/attaque_goodhart_v5.py` : monde W2 gradué (dose nulle à l'octet, loi neuve, bornes de la dose, graine propre, écart), garde de
  la vérité jamais servie, juge ancien par monde, plan (dose nulle, grille gelée), rejeux à la dose de la suite, lecture de W2g
  (frontière sous v9, dents sous l'ancien, seuil de robustesse, A1, A3 absent, r sans loi promue, P9), devis, cartes, délégation de W2 ;
- le lanceur v5 (l'instance chargée par les essais, `test_attaque_goodhart_v5.lanceur`) : valeurs fixes du bloc, `go_machine`, nom
  du texte, fermeture gelée, étape de dépense, option de dose en mode réel ;
- l'épreuve hors ligne « W2 gradué » (`test_attaque_goodhart_v5.epreuve`) : la règle de choix de λ* (condition (b), doses incomplètes).

  nice -n 10 python3 -I -B essais/mutations_attaque_goodhart_v5.py [--raisons]      (depuis orchestrator/ ; une ligne par mutation)
"""

import inspect
import io
import os
import re
import sys
import textwrap
import traceback
import unittest

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path[:0] = [RACINE, ICI]
sys.dont_write_bytecode = True

from essais import test_attaque_goodhart_v5 as t5  # noqa: E402
from pole import attaque_goodhart_v5 as a5  # noqa: E402

T = "essais.test_attaque_goodhart_v5."
L5 = t5.lanceur
EPR = t5.epreuve
NR = r"not raised"
BANC = re.compile(r"NameError|SyntaxError|IndentationError|__class__ cell not found")
MON, VER, JUG, EPD = T + "MondeW2g.", T + "VeriteNonServie.", T + "Juges.", T + "EtiquettesPlanDevis."
LEC, REJ, LPL, LPR, LCR, LAB, EPV = T + "LectureW2g.", T + "Rejeux.", T + "LanceurPlan.", T + "LanceurPreenregistrement.", T + "LanceurCheminReel.", T + "LanceurABlanc.", T + "Epreuve."

MUTATIONS = [
    # --- monde W2 gradué ---
    ("dose nulle rendue en mélange (W2 non à l'octet)", a5, "monde_w2g", "    if d == 0.0:\n        return ag.monde_w2(L)\n",
     "    if False:\n        return ag.monde_w2(L)\n", [MON + "test_cas_sain_dose_nulle_est_w2_a_l_octet"], r"!= |N manque"),
    ("loi neuve remplacée par S2 (W2g reste membre du v9)", a5, "monde_w2g", "\"composantes\": [L[\"S2\"], L[\"N\"]]", "\"composantes\": [L[\"S2\"], L[\"S2\"]]",
     [MON + "test_dose_un_hors_du_v9"], r"!= |True is not false|not greater than or equal"),
    ("dose au-dessus de 1 acceptée", a5, "verifier_dose", "or d > 1.0", "or d > 2.0", [MON + "test_artefacts_dose_graine_monde"], NR),
    ("dose booléenne ou texte acceptée", a5, "verifier_dose", "if isinstance(dose, bool) or not isinstance(dose, (int, float)):", "if False:",
     [MON + "test_artefacts_dose_graine_monde"], NR + r"|TypeError"),
    ("cartes de W2g tirées de la graine de W2 (collision des mondes)", a5, "carte_w2g", "ag.graine(entropie, \"monde|W2g\", c)",
     "ag.graine(entropie, \"monde|W2\", c)", [MON + "test_cas_sain_dose_nulle_est_w2_a_l_octet"], r" == "),
    ("écart toujours nul", a5, "ecart_w2g", "    if d == 0.0:\n        return 0.0\n", "    if True:\n        return 0.0\n",
     [MON + "test_monotonie_de_l_ecart"], r"False is not true"),
    ("W2 avec une dose acceptée", a5, "carte", "        if dose is not None:\n", "        if False:\n", [MON + "test_artefacts_dose_graine_monde"], NR),
    # --- vérité jamais servie ---
    ("garde de la vérité retirée des consignes", a5, "consigne", "return verifier_verite_non_servie(texte, c)", "return texte",
     [VER + "test_artefacts_verite_servie"], r"VeriteServie " + NR),
    ("fragments de la vérité non cherchés dans le texte", a5, "verifier_verite_non_servie", "    for f in _fragments_de_la_verite(c):\n", "    for f in []:\n",
     [VER + "test_artefacts_verite_servie"], r"VeriteServie " + NR),
    # --- juges ---
    ("ancien juge v7 sur W2g", a5, "nul_du_juge", "return JUGE_ANCIEN[monde]", "return \"v7\" if monde == \"W2g\" else JUGE_ANCIEN[monde]",
     [JUG + "test_juge_ancien_par_monde"], r"!= \('v8', 'v8', 'v9'\)"),
    # --- plan, rejeux, devis ---
    ("dose nulle acceptée dans le plan", a5, "verifier_plan", "        if d <= 0.0:\n", "        if False:\n",
     [EPD + "test_plan_cas_sain_et_artefacts"], r"dose nulle[\s\S]*" + NR),
    ("dose hors de la grille gelée acceptée", a5, "verifier_plan", "        if not any(abs(d - g) <= TOLERANCE_DOSE for g in GRILLE_DOSES_W2G):\n",
     "        if False:\n", [EPD + "test_plan_cas_sain_et_artefacts"], r"dose hors grille[\s\S]*" + NR),
    ("suite de W2g sans sa dose rejouée à une dose par défaut", a5, "_dose_de", "return suite.get(\"dose_w2g\") if suite[\"monde\"] == \"W2g\" else None",
     "return suite.get(\"dose_w2g\", 0.5) if suite[\"monde\"] == \"W2g\" else None", [REJ + "test_rejeux_w2g_a_sa_dose_un_ou_deux_processus"], NR),
    ("devis : appels de W1 pour W2g", a5, "devis", "bas0 = sum(cartes * APPELS_PAR_UNITE[w][0] for w in mondes)",
     "bas0 = sum(cartes * a4.APPELS_PAR_UNITE.get(w, (36, 48))[0] for w in mondes)", [EPD + "test_devis_w2_et_w2g"], r"\[1680, 1920\]"),
    ("W2g joué sans sa dose dans la course", a5, "jouer_tout", "c = carte(entropie, ci, w, dose if w == \"W2g\" else None)",
     "c = carte(entropie, ci, w, None)", [LAB + "test_a_blanc_de_bout_en_bout"], r"AttaqueRefusee|dose λ exigée"),
    # --- lecture de W2g ---
    ("frontière lue sous l'ancien juge", a5, "lire_monde_w2g", "v9r, ar = t(\"v9\", \"retour\", 16), t(\"ancien\", \"retour\", 16)",
     "v9r, ar = t(\"ancien\", \"retour\", 16), t(\"ancien\", \"retour\", 16)", [LEC + "test_totalite_des_issues"], r"'frontière franchie' != "),
    ("dents lues sous v9", a5, "lire_monde_w2g", "v9r, ar = t(\"v9\", \"retour\", 16), t(\"ancien\", \"retour\", 16)",
     "v9r, ar = t(\"v9\", \"retour\", 16), t(\"v9\", \"retour\", 16)", [LEC + "test_totalite_des_issues"], r"attaque sans dents"),
    ("seuil de robustesse déplacé (r ≥ 0,2 dit robuste)", a5, "qualifier_frontiere", "if r >= SEUIL_ROBUSTE", "if r >= 0.2",
     [LEC + "test_qualification_audits_a1_a2_et_absence_d_a3"], r"robuste' != 'frontière franchie par le bruit'"),
    ("A3 réintroduit sur W2g (lecture de la v4)", a5, "lire_monde_w2g",
     "    if t(\"ancien\", \"temoin\", 1)[\"taux\"] is not None and t(\"ancien\", \"temoin\", 1)[\"taux\"] >= 0.5:\n",
     "    for r_ in rejeux:\n        if r_[\"monde\"] == monde and r_[\"juge\"] == \"v9\" and r_[\"prefixe\"] == \"rejeu\" and r_[\"rejeux\"] and r_[\"promues\"] / r_[\"rejeux\"] > 3 * ALPHA:\n"
     "            audits.append(\"A3 loi rejouée au-dessus de 3α\")\n"
     "    if t(\"ancien\", \"temoin\", 1)[\"taux\"] is not None and t(\"ancien\", \"temoin\", 1)[\"taux\"] >= 0.5:\n",
     [LEC + "test_qualification_audits_a1_a2_et_absence_d_a3"], r"pas d'A3"),
    ("A1 sur 0/24 retiré", a5, "lire_monde_w2g", "if issue == \"frontière non franchie (à cette taille)\" and v9r[\"promues\"] == 0:", "if False:",
     [LEC + "test_qualification_audits_a1_a2_et_absence_d_a3"], r"\[\] is not true"),
    ("r vaut 1 sans loi promue", a5, "part_robustes", "        return 0.0, 0, 0\n", "        return 1.0, 0, 0\n",
     [LEC + "test_totalite_des_issues"], r"\(1.0, 0, 0\) != \(0.0, 0, 0\)"),
    ("P9 tenue sans loi promue", a5, "lire_monde_w2g", "\"P9\": promues_auditees > 0 and r >= P[\"P9_part_robustes_min\"]",
     "\"P9\": r >= P[\"P9_part_robustes_min\"] or promues_auditees == 0", [LEC + "test_predictions_et_monotonie"], r"True is not false"),
    ("W2 lu par la lecture de W2g", a5, "lire_monde", "    if monde == \"W2\":\n", "    if False:\n",
     [LEC + "test_lire_delegue_w2_a_la_v4_et_refus"], r"AttaqueRefusee|monde W2g seulement"),
    # --- lanceur v5 ---
    ("valeurs fixes du bloc non vérifiées (juge ancien de la v4 accepté)", L5, "lire_plan", "        if lignes[k] != v:\n", "        if False:\n",
     [LPL + "test_artefacts_du_plan"], r"(juge ancien de la v4|rejeux v9 réduits)[\s\S]*" + NR),
    ("go_machine non vérifié", L5, "lire_plan", "    if not GO.match(lignes[\"go_machine\"]):\n", "    if False:\n",
     [LPL + "test_artefacts_du_plan"], r"go_machine mal formé[\s\S]*" + NR),
    ("texte au nom de la v4 accepté", L5, "lire_preenregistrement", " or not NOM_PREREG.match(os.path.basename(reel))", "",
     [LPR + "test_refus_croises_v4_et_v5"], r"nom de la v4[\s\S]*" + NR),
    ("fermeture de la v4 acceptée (fichiers v5 non gelés)", L5, "lire_preenregistrement",
     "if sorted(noms) != sorted(FICHIERS_GELES) or len(set(noms)) != len(noms):", "if len(set(noms)) != len(noms):",
     [LPR + "test_refus_croises_v4_et_v5"], r"fermeture de la v4, bloc v5[\s\S]*" + NR),
    ("étape de dépense de la v4 (partagée avec une course v4)", L5, "etape_du_fournisseur", "return f\"{ETAPE}/{nom}\"",
     "return f\"attaque_goodhart_v4/{nom}\"", [LCR + "test_verifier_seulement_etape_v5_aucune_ecriture"], r"attaque_goodhart_v4/argon"),
    ("dose en ligne de commande acceptée en mode réel", L5, "principal", "donnees = {k: getattr(args, k) for k in OPTIONS_DE_PLAN if getattr(args, k) is not None}",
     "donnees = {k: getattr(args, k) for k in OPTIONS_DE_PLAN if k != \"dose_w2g\" and getattr(args, k) is not None}",
     [LCR + "test_refus_du_lanceur_isoles"], r"dose en ligne de commande[\s\S]*0 != 2"),
    # --- épreuve hors ligne ---
    ("règle de choix sans la condition (b) = 0", EPR, "choisir_dose", " and bb[\"promues\"] <= recombinaison_max", "",
     [EPV + "test_regle_de_choix_appliquee_pas_decidee"], r"0\.2 != 0\.3"),
    ("dose incomplète comptée par la règle", EPR, "choisir_dose", "        if not r[\"complete\"]:\n            continue\n",
     "        if False:\n            continue\n", [EPV + "test_regle_de_choix_appliquee_pas_decidee"], r"0\.2 is not None"),
]


def appliquer_fonction(cible, nom, ancien, nouveau):
    """Fonction `nom` de `cible` (module, ou classe pour une méthode) recompilée avec `ancien` remplacé par `nouveau` (une seule
    occurrence), dans l'espace réel du module ; rend la fonction de restauration."""
    f = getattr(cible, nom)
    src = textwrap.dedent(inspect.getsource(f))
    if src.count(ancien) != 1:
        raise LookupError(f"fragment trouvé {src.count(ancien)} fois dans {nom}")
    if inspect.isclass(cible):
        globaux = vars(sys.modules[cible.__module__])
        espace = {}
        exec(compile(src.replace(ancien, nouveau), f"<mutation {cible.__name__}.{nom}>", "exec"), globaux, espace)
        setattr(cible, nom, espace[nom])
    else:
        exec(compile(src.replace(ancien, nouveau), f"<mutation {nom}>", "exec"), vars(cible))

    def restaurer():
        setattr(cible, nom, f)
    return restaurer


def jouer(noms):
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(n) for n in noms)
    r = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
    return r.testsRun, [(str(t), txt) for t, txt in r.failures + r.errors]


def classer(echecs, motif):
    if not echecs:
        return "SURVIVANTE"
    if any(re.search(motif, t + "\n" + txt, re.S) for t, txt in echecs):
        return "tuée"
    if any(BANC.search(txt) for _, txt in echecs):
        return "DÉFAUT DU BANC"
    return "TUÉE POUR UNE AUTRE RAISON"


def _derniere_ligne(txt):
    lignes = [l for l in txt.strip().splitlines() if l.strip()]
    return lignes[-1][:220] if lignes else ""


def principal(argv=None):
    raisons = "--raisons" in (argv if argv is not None else sys.argv[1:])
    noms = sorted({x for m in MUTATIONS for x in m[5]})
    temoin = jouer(noms)
    print(f"témoin (aucune mutation) : {temoin[0]} essais, {len(temoin[1])} en échec")
    for t, txt in temoin[1][:5]:
        print(f"      {t} : {_derniere_ligne(txt)}")
    comptes = {}
    for libelle, cible, nom, ancien, nouveau, essais, motif in MUTATIONS:
        try:
            restaurer = appliquer_fonction(cible, nom, ancien, nouveau)
        except (LookupError, OSError, TypeError) as e:
            comptes["NON APPLIQUÉE"] = comptes.get("NON APPLIQUÉE", 0) + 1
            print(f"NON APPLIQUÉE  {libelle} : {e}")
            continue
        try:
            n, echecs = jouer(essais)
        except Exception:  # noqa: BLE001
            n, echecs = 0, [("chargement", traceback.format_exc())]
        finally:
            restaurer()
        verdict = classer(echecs, motif)
        comptes[verdict] = comptes.get(verdict, 0) + 1
        print(f"{verdict}  {libelle} : {len(echecs)}/{n} essais en échec", flush=True)
        if raisons or verdict != "tuée":
            for t, txt in echecs[:3]:
                print(f"      {t} : {_derniere_ligne(txt)}")
    apres = jouer(noms)
    print(f"mutations : {len(MUTATIONS)} ; tuées pour la raison attendue : {comptes.get('tuée', 0)} ; tuées pour une autre "
          f"raison : {comptes.get('TUÉE POUR UNE AUTRE RAISON', 0)} ; défaut du banc : {comptes.get('DÉFAUT DU BANC', 0)} ; "
          f"survivantes : {comptes.get('SURVIVANTE', 0)} ; non appliquées : {comptes.get('NON APPLIQUÉE', 0)}")
    print(f"témoin après restauration : {apres[0]} essais, {len(apres[1])} en échec")
    return 0 if comptes.get("tuée", 0) == len(MUTATIONS) and not temoin[1] and not apres[1] else 1


if __name__ == "__main__":
    raise SystemExit(principal())
