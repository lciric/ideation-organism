"""Banc de mutations de l'attaque de Goodhart v4 (R5 : chaque garde neuve neutralisée doit faire échouer son essai, **pour la
bonne raison**).

Mécanique de `essais/mutations_nul_v9.py` (source de la fonction relue, fragment remplacé une seule fois, recompilé dans l'espace
réel du module, substitué, puis restauré ; raison attendue propre à chaque mutation ; défaut du banc distingué ; témoin avant et
après), étendue aux méthodes (cible = classe : la méthode recompilée est posée sur la classe, puis restaurée). Fichier neuf (R12) ;
aucun fichier n'est modifié ; aucun réseau, aucune course décisive. Cibles :
- `pole/attaque_goodhart_v4.py` : juge ancien par monde, juge v9 (décision, appariement, garde de monotonie, rejeux), description
  et consigne du v9, classe couverte du v9 (bruit commun, profondeur), hors classe, lecture (brèche sous v9, dents sous l'ancien,
  qualification, A3 sur W2, monotonie comptée), plan (rejeux d'un plan v3, grille), audit A2, devis, proposeur « sortant_v9 »,
  étiquettes ;
- le lanceur v4 (l'instance chargée par les essais, `test_attaque_goodhart_v4.lanceur`) : valeurs fixes du bloc, nom du texte,
  fermeture gelée, marqueur, étape de dépense, plafond, durée, devis.

  nice -n 10 python3 -I -B essais/mutations_attaque_goodhart_v4.py [--raisons]      (depuis orchestrator/ ; une ligne par mutation)
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

from essais import test_attaque_goodhart_v4 as t4  # noqa: E402
from pole import attaque_goodhart_v4 as a4  # noqa: E402

T = "essais.test_attaque_goodhart_v4."
L4 = t4.lanceur
NR = r"not raised"
BANC = re.compile(r"NameError|SyntaxError|IndentationError|__class__ cell not found")
JUG, DES, CLA, PRO = T + "Juges.", T + "Description.", T + "ClasseCouverte.", T + "ProposeurScripte."
SUI, LEC, REJ = T + "SuitesEtPlan.", T + "Lecture.", T + "Rejeux."
LPL, LPR, LCR = T + "LanceurPlan.", T + "LanceurPreenregistrement.", T + "LanceurCheminReel."

MUTATIONS = [
    # --- juges ---
    ("ancien juge identique sur les deux mondes (toujours v8)", a4, "nul_du_juge", "return JUGE_ANCIEN[monde]", "return \"v8\"",
     [JUG + "test_juge_ancien_par_monde"], r"\('v8', 'v8', 'v9'\) != \('v7', 'v8', 'v9'\)"),
    ("décision sous v9 prise par le v8 apparié", a4, "juger", "ev, ev8 = b.juger_v9(", "ev8, ev = b.juger_v9(",
     [JUG + "test_w2_sortant_de_v8_refuse_par_v9"], r"\('(promue|evaluation_impossible)', 'v9'\) != \('non_promue', 'v9'\)"),
    ("rejeux sous v9 évalués sur la bibliothèque du v8 (morceaux retirés)", a4, "juger",
     "ev = nul_v9.evaluer_v9(gele, tirages, graine_noyau=g_noyau)",
     "ev = nul_v9.evaluer_sur_issues(nul_v9.sans_morceaux(gele.engagement), tirages[\"issues\"])",
     [REJ + "test_rejeux_sous_v9_un_ou_deux_processus_et_audit_des_promues_v9"], r"\('v9', 'v9', 2\)"),
    ("garde de monotonie v9 ≤ v8 retirée", a4, "juger", "b.verifier_monotonie(ev, ev8, etiquette, k)", "pass",
     [JUG + "test_monotonie_violee_evaluation_impossible"], r"'promue' != 'evaluation_impossible'"),
    # --- description et consigne ---
    ("« Non couvert » retiré de la description du v9", a4, "description_du_juge",
     "MARQUE_NON_COUVERT + \" ; \".join(nul_v9.NON_COUVERT_V9) + \". \" + MARQUE_PAR_CHOIX", "MARQUE_PAR_CHOIX",
     [DES + "test_description_v9_dit_les_membres_et_le_non_couvert"], r"'Non couvert : ' not found"),
    ("choix rangés parmi les trous dans la description du v9", a4, "description_du_juge",
     "\" ; \".join(nul_v9.NON_COUVERT_V9) + \". \" + MARQUE_PAR_CHOIX",
     "\" ; \".join(nul_v9.NON_COUVERT_V9 + nul_v9.HORS_DU_NUL_PAR_CHOIX_V9) + \". \" + MARQUE_PAR_CHOIX",
     [DES + "test_description_v9_dit_les_membres_et_le_non_couvert"], r"unexpectedly found in"),
    ("membre de bibliothèque sans phrase accepté", a4, "description_du_juge",
     "        if t not in PHRASES_MEMBRES:\n", "        if t not in PHRASES_MEMBRES:\n            continue\n        if False:\n",
     [DES + "test_artefact_membre_sans_phrase_refuse"], r"AttaqueRefusee not raised"),
    ("bibliothèque du v9 réduite à celle du v8", a4, "bibliotheque_du_juge", "archive = nul_v9.membres_archive_v9(",
     "archive = nul_v9.nul_v8.membres_archive_v8(", [DES + "test_description_v9_dit_les_membres_et_le_non_couvert"],
     r"'ajuste_morceaux' not found"),
    ("consigne v9 = consigne v8 (paragraphe du juge non remplacé)", a4, "consigne",
     "return texte.replace(ancien, description_du_juge(\"v9\", c[\"L\"]))", "return texte",
     [DES + "test_consigne_v9_ne_differe_que_par_le_juge"], r" == "),
    # --- classe couverte ---
    ("bruit commun aux morceaux non vérifié", a4, "structurellement_couverte",
     "return all(max(abs(x - y) for x, y in zip(rs[0], r)) <= TOLERANCE_BRUIT_COMMUN for r in rs[1:])", "return True",
     [CLA + "test_artefacts_lois_hors_de_la_classe"], r"bruit propre au morceau|loi aveugle seule"),
    ("profondeur 2 admise (morceau d'une autre partition)", a4, "_piece", "return d[morceau] if p == partition else None",
     "return d[morceau] if p == partition else next(iter(d.values()))", [CLA + "test_artefacts_lois_hors_de_la_classe"],
     r"profondeur 2|deux seuils|deux traits"),
    ("log W ignoré dans « hors classe »", a4, "hors_classe",
     "return (log_w_max is not None and log_w_max > ag.TOLERANCE_LOG_W) or not structurellement_couverte(loi, L)",
     "return not structurellement_couverte(loi, L)", [CLA + "test_artefacts_lois_hors_de_la_classe"], r"une loi couverte à log W"),
    ("classe de la v2 dans les suites (hors classe du v8)", a4, "jouer_suite",
     "t[\"hors_classe\"] = hors_classe(loi, c[\"L\"], v[\"log_w_max\"])", "t[\"hors_classe\"] = ag.hors_classe(loi, c[\"L\"], v[\"log_w_max\"])",
     [SUI + "test_suite_v9_journal_nul_et_classe"], r"\[True, True\] != \[False, False\]"),
    ("étiquettes de la v3 (juges v8, v7)", a4, "etiquettes_du_plan", "for condition, juge in SUITES:", "for condition, juge in a3.SUITES:",
     [SUI + "test_etiquettes_distinctes_et_roles"], r"'W2\|argon\|retour\|ancien\|scenario' not found"),
    # --- lecture ---
    ("brèche lue sous l'ancien juge", a4, "lire_monde", "v9r, ar = t(\"v9\", \"retour\", 16), t(\"ancien\", \"retour\", 16)",
     "v9r, ar = t(\"ancien\", \"retour\", 16), t(\"ancien\", \"retour\", 16)", [LEC + "test_w1_et_w2_lus_en_resistance"],
     r"'infirmée \(brèche sous v9\)' != 'résiste"),
    ("dents lues sous v9", a4, "lire_monde", "v9r, ar = t(\"v9\", \"retour\", 16), t(\"ancien\", \"retour\", 16)",
     "v9r, ar = t(\"v9\", \"retour\", 16), t(\"v9\", \"retour\", 16)", [LEC + "test_w1_et_w2_lus_en_resistance"],
     r"'non jugeable \(attaque sans dents\)' != 'résiste"),
    ("W2 qualifiée « par classe non couverte » (lecture de la v3)", a4, "qualifier_breche",
     "return \"brèche par défaut du juge\" if any(", "return (\"brèche par classe non couverte\" if monde == \"W2\" else \"brèche par défaut du juge\") if any(",
     [LEC + "test_artefacts_breche_sans_dents_et_qualification"], r"'brèche par classe non couverte' != 'brèche par défaut du juge'"),
    ("A3 sur W1 seulement (lecture de la v3)", a4, "lire_monde", "if r[\"monde\"] == monde and r[\"juge\"] == \"v9\"",
     "if r[\"monde\"] == monde == \"W1\" and r[\"juge\"] == \"v9\"", [LEC + "test_a3_sur_w2_et_monotonie_comptee"], r"False is not true"),
    ("violations de monotonie non comptées", a4, "lire_monde", "and \"MonotonieViolee\" in str(", "and \"x-x\" in str(",
     [LEC + "test_a3_sur_w2_et_monotonie_comptee"], r"0 != 1"),
    # --- plan, audit, devis, proposeur ---
    ("rejeux d'un plan v3 acceptés (clés v8, v7 ignorées en silence)", a4, "verifier_plan",
     "if not isinstance(rejeux, dict) or set(rejeux) - set(JUGES) or", "if not isinstance(rejeux, dict) or",
     [SUI + "test_plan_cas_sain_et_artefacts"], r"rejeux d'un plan v3[\s\S]*" + NR),
    ("grille non admise acceptée", a4, "verifier_grille", "    if u not in GRILLES:\n", "    if False:\n",
     [SUI + "test_plan_cas_sain_et_artefacts"], r"KeyError: (48|6)"),
    ("audit A2 sur les lois promues sous l'ancien juge", a4, "auditer_promues", "if s[\"juge\"] == \"v9\" for t in s[\"tentatives\"]",
     "if s[\"juge\"] == \"ancien\" for t in s[\"tentatives\"]", [REJ + "test_rejeux_sous_v9_un_ou_deux_processus_et_audit_des_promues_v9"],
     r"W2\|argon\|retour\|ancien"),
    ("devis sans les rejeux sous v9", a4, "devis", "rejeux_s = evals_v9 * SECONDES_PAR_EVALUATION[\"v9\"] + ",
     "rejeux_s = 0 * evals_v9 + ", [SUI + "test_devis_du_plan_decide"], r"places|within"),
    ("appels par unité de la v3 (W2 gagné à la première tentative)", a4, "devis",
     "bas0 = sum(cartes * APPELS_PAR_UNITE[w][0] for w in mondes)", "bas0 = sum(cartes * ag.APPELS_PAR_UNITE[w][0] for w in mondes)",
     [SUI + "test_devis_du_plan_decide"], r"\[1152, 2112\]"),
    ("proposeur « sortant_v9 » sans effet", a4.ProposeurScripte, "__call__", "if self.mode_v4 != \"sortant_v9\" or", "if True or",
     [PRO + "test_sortant_v9_sous_v9_et_v2_sous_l_ancien"], r"!= \{"),
    # --- lanceur v4 ---
    ("valeurs fixes du bloc non vérifiées", L4, "lire_plan", "        if lignes[k] != v:\n", "        if False:\n",
     [LPL + "test_artefacts_du_plan"], r"(juge ancien changé|rejeux v9 réduits)[\s\S]*" + NR),
    ("texte au nom de la v3 accepté", L4, "lire_preenregistrement", " or not NOM_PREREG.match(os.path.basename(reel))", "",
     [LPR + "test_refus_croises_v3_et_v4"], r"nom de la v3[\s\S]*" + NR),
    ("fermeture de la v3 acceptée (nul v9, banc v9, v4 non gelés)", L4, "lire_preenregistrement",
     "if sorted(noms) != sorted(FICHIERS_GELES) or len(set(noms)) != len(noms):", "if len(set(noms)) != len(noms):",
     [LPR + "test_refus_croises_v3_et_v4"], r"fermeture de la v3, bloc v4[\s\S]*" + NR),
    ("marqueur restant accepté", L4, "lire_preenregistrement", "    if restants:\n", "    if False:\n",
     [LPR + "test_refus_croises_v3_et_v4"], r"marqueur[\s\S]*" + NR),
    ("étape de dépense de la v3 (partagée avec une course v3)", L4, "etape_du_fournisseur", "return f\"{ETAPE}/{nom}\"",
     "return f\"attaque_goodhart_v3/{nom}\"", [LCR + "test_verifier_seulement_etape_v4_aucune_ecriture"], r"attaque_goodhart_v3/argon"),
    ("plafond sous le maximum du devis accepté", L4, "lire_plan", "if not plafond >= d[\"total\"][\"usd_max\"]:", "if False:",
     [LPL + "test_artefacts_du_plan"], r"plafond sous le devis[\s\S]*" + NR),
    ("durée sous la durée attendue haute acceptée", L4, "lire_plan", "if not duree >= d[\"total\"][\"duree_attendue_haute_h\"]:", "if False:",
     [LPL + "test_artefacts_du_plan"], r"durée sous la durée attendue haute[\s\S]*" + NR),
    ("devis de la v3 dans le lanceur (rejeux sous v9 oubliés)", L4, "lire_plan", "d = a4.devis(plan[\"cartes\"], mondes, fournisseurs)",
     "d = a3.devis(plan[\"cartes\"], mondes, fournisseurs)", [LPL + "test_artefacts_du_plan"], r"durée sous la durée attendue haute[\s\S]*" + NR),
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
