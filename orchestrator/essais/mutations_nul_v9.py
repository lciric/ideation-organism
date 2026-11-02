"""Banc de mutations du nul v9 (R5 : chaque garde neutralisée doit faire échouer son essai, **pour la bonne raison**).

Mécanique de `essais/mutations_v58.py` (source de la fonction relu, fragment remplacé une seule fois, recompilé dans l'espace
réel du module, substitué, puis restauré ; raison attendue propre à chaque mutation ; défaut du banc distingué ; témoin avant et
après), en version autonome. Fichier neuf (R12) ; aucun fichier n'est modifié ; aucune mutation ne peut lancer une course
décisive (l'essai des refus remplace la course par un bouchon). Cibles :
- `pole/nul_v9.py` : certificat de Frank-Wolfe, sommets du polytope, coupes des seuils, morceaux de la sous-population, membres
  et leur garde, liste des types ajustés de l'évaluateur, refus d'un membre inconnu, gardes d'engagement, sens du pas de Newton ;
- le banc v9 (l'instance chargée par les essais, `test_nul_v9.banc`) : monotonie gardée, perte appariée, lecture gelée (issues,
  artefacts appariés, audits A4 et A5), préenregistrement (nom, scellement, empreintes), espace des graines, liste d'arrêt,
  code de sortie.

  nice -n 10 python3 -I -B essais/mutations_nul_v9.py [--raisons]      (depuis orchestrator/ ; une ligne par mutation)
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

from essais import test_nul_v9 as t9  # noqa: E402
from pole import nul_v9  # noqa: E402

T = "essais.test_nul_v9."
B = t9.banc
NR = r"not raised"
BANC = re.compile(r"NameError|SyntaxError|IndentationError|__class__ cell not found")
CERT, EVAL, TRI = T + "CertificatMorceaux.", T + "EvaluateurV9.", T + "TricheursParMorceaux."
MEM, LEC, PRE = T + "MembresNulV9.", T + "LectureGelee.", T + "GrainesEtPreenregistrement."
DOMINE = CERT + "test_cas_sain_valeur_domine_la_vraisemblance_de_tout_monde_de_la_famille"
SOUS = r"< log-vraisemblance du monde|valeur .* sous la référence|M0\d\|v9 promue [1-9]|log_w_max_max|not less than or equal to 1e-06"

MUTATIONS = [
    # --- pole/nul_v9.py : calcul ---
    ("certificat remplacé par la valeur atteinte (sans écart de Frank-Wolfe)", nul_v9, "maximiser_par_lots",
     "certificat = np.minimum(0.0, f + np.maximum(0.0, V - actif.sum(axis=0)))", "certificat = f",
     [DOMINE, CERT + "test_reference_independante_scipy_petits_echantillons"], SOUS),
    ("certificat final sans écart de Frank-Wolfe", nul_v9, "_certificats",
     "return f, np.minimum(0.0, f + np.maximum(0.0, V - actif.sum(axis=0)))", "return f, f",
     [CERT + "test_artefact_valeur_atteinte_au_depart_n_est_pas_une_borne", DOMINE], r"le certificat au même point domine|" + SOUS),
    ("sommets r = δ_k oubliés dans l'écart de Frank-Wolfe", nul_v9, "maximiser_par_lots",
     "V = np.maximum(V, g[:, P * J:].max(axis=1))", "V = V",
     [DOMINE, CERT + "test_reference_independante_scipy_petits_echantillons", TRI + "test_artefact_tricheurs_par_morceaux_m02_a_m07_jamais_promus"],
     SOUS),
    ("seuils limités à une grille fixe", nul_v9, "_coupes",
     "seuils = np.concatenate([[-np.inf], np.unique(z[:t])])", "seuils = np.array([-np.inf, -1.0, -0.5, 0.0, 0.5, 1.0])",
     [DOMINE, CERT + "test_seuil_egal_a_une_valeur_observee"], SOUS + r"|not greater than or equal to"),
    ("seuil lu sur le mauvais trait (toujours z0)", nul_v9, "_coupes",
     "z = np.array([float(inst[\"z\"][j]) for inst in instances])", "z = np.array([float(inst[\"z\"][0]) for inst in instances])",
     [DOMINE, CERT + "test_seuil_egal_a_une_valeur_observee"], SOUS + r"|not greater than or equal to"),
    ("élagage trop agressif (coupes qui peuvent porter le maximum élaguées)", nul_v9, "maximiser_par_lots",
     "garde = (bornes[actives] >= meilleure[groupes[actives]] - TOLERANCE_ELAGAGE) & ~termine[groupes[actives]]",
     "garde = (bornes[actives] >= meilleure[groupes[actives]] + 5.0) & ~termine[groupes[actives]]",
     [CERT + "test_reference_independante_scipy_petits_echantillons"], r"loin au-dessus de la référence"),
    ("départ sur le bord du polytope (aucune part du centre)", nul_v9, "detail_morceaux_groupe",
     "x0 = np.concatenate([np.tile(_depart(J, K, P, departs[qu[1]]), (qu[2].shape[2], 1)) for qu in questions])",
     "x0 = np.concatenate([np.tile(_depart(J, K, P, departs[qu[1]], centre=0.0) * 0.0 + np.eye(1, J * P + K)[0], (qu[2].shape[2], 1)) for qu in questions])",
     [DOMINE], r"départ du calcul par morceaux (non admissible|hors des contraintes)"),
    ("sous-population : un seul morceau", nul_v9, "_coupes",
     "M = np.stack([((g == v).astype(float) * dedans)[:, None] for v in valeurs_g])", "M = np.stack([dedans[:, None]])",
     [DOMINE, TRI + "test_artefact_m01_jamais_promu_sous_v9_promu_sous_v8"], SOUS),
    ("pas de Newton dans le mauvais sens (descente)", nul_v9, "maximiser_par_lots", "rhs[:, :q, 0] = -g", "rhs[:, :q, 0] = g",
     [CERT + "test_reference_independante_scipy_petits_echantillons"], r"loin au-dessus de la référence|not less than or equal to"),
    # --- pole/nul_v9.py : membres et garde ---
    ("aucun membre par morceaux pour deux lois connues", nul_v9, "membres_morceaux", "if len(lois) < 2:", "if len(lois) < 3:",
     [MEM + "test_cas_sain_membres_fiche_fille_et_une_seule_loi"], r"Lists differ|\[\] != \["),
    ("garde des membres neutralisée", nul_v9, "exiger_membres_v9", "    if defauts:\n", "    if False:\n",
     [MEM + "test_artefact_membre_absent_altere_ou_en_trop_refuse"], NR),
    ("garde des membres : lois connues non vérifiées", nul_v9, "exiger_membres_v9", " or m.get(\"lois\") != a[\"lois\"]", "",
     [MEM + "test_artefact_membre_absent_altere_ou_en_trop_refuse"], r"lois (tronquées|d'un autre ordre)[\s\S]*" + NR),
    ("garde des membres : membres du v8 non vérifiés", nul_v9, "exiger_membres_v9",
     "        nul_v8.exiger_membres_ajustes([m for m in membres if m.get(\"type\") != TYPE_MORCEAUX], survivantes, lois_parents)\n",
     "        pass\n", [MEM + "test_artefact_membre_absent_altere_ou_en_trop_refuse"], r"membre linéaire du v8 retiré[\s\S]*" + NR),
    # --- pole/nul_v9.py : évaluateur ---
    ("membres par morceaux ignorés par l'évaluateur", nul_v9, "evaluer_sur_issues",
     "ajustes = [m for m in bibliotheque if m[\"type\"] in TYPES_AJUSTES_V9]",
     "ajustes = [m for m in bibliotheque if m[\"type\"] in nf.TYPES_AJUSTES]",
     [TRI + "test_artefact_m01_jamais_promu_sous_v9_promu_sous_v8"], r"membre de bibliothèque inconnu|M01\|v9 promue"),
    ("membre ajusté inconnu ignoré en silence", nul_v9, "valeurs_ajustees_v9",
     "            raise NulV9Refuse(f\"membre ajusté inconnu : {m['type']!r}\")\n", "            continue\n",
     [EVAL + "test_membre_inconnu_refuse"], NR),
    ("garde d'engagement retirée de l'évaluateur", nul_v9, "evaluer_v9",
     "    if empreinte_objet(gele.engagement) != gele.empreinte:\n", "    if False:\n",
     [EVAL + "test_gardes_d_engagement_et_de_tirages"], r"EngagementModifie not raised"),
    ("départage des membres changé (ordre au lieu du nom)", nul_v9, "evaluer_sur_issues",
     "meilleur, nom = max(candidats, key=lambda c: (c[0], c[1]))", "meilleur, nom = max(candidats, key=lambda c: c[0])",
     [EVAL + "test_departage_des_membres_comme_v2", EVAL + "test_identique_a_v2_sans_morceaux"], r"'a' != 'b'|membre_dominant_final"),
    # --- banc v9 : juge et répétitions ---
    ("monotonie non gardée", B, "verifier_monotonie",
     "    if max(ecarts) > TOLERANCE_MONOTONIE + 1e-6 or (ev9[\"promue\"] and not ev8[\"promue\"]):\n", "    if False:\n",
     [PRE + "test_banc_reduit_et_liste_d_arret"], r"monotonie[\s\S]*(0 != 3|1 != 3)"),
    ("perte appariée comptée à l'envers", B, "jouer_ligne", "perdues += bool(ev8[\"promue\"]) and not ev[\"promue\"]",
     "perdues += bool(ev[\"promue\"]) and not ev8[\"promue\"]", [TRI + "test_perte_appariee_comptee_dans_le_bon_sens"],
     r"Tuples differ|\(1, 3, 0\)"),
    ("v8 apparié évalué avec les membres par morceaux (v9 contre v9)", B, "juger_v9",
     "nul_v9.evaluer_sur_issues(nul_v9.sans_morceaux(gele.engagement), tirages[\"issues\"], None)",
     "nul_v9.evaluer_sur_issues(gele.engagement, tirages[\"issues\"], None)",
     [TRI + "test_artefact_m01_jamais_promu_sous_v9_promu_sous_v8"], r"M01 sous le v8 apparié"),
    # --- banc v9 : lecture gelée ---
    ("lecture : ligne fatale non tenue sans effet (« trou » jamais rendu)", B, "lire_v9",
     "elif NON_TENUE in lecture[\"fatales\"].values():", "elif False:",
     [LEC + "test_artefact_ligne_fatale_au_dessus_de_alpha_trou"], r"'trou'"),
    ("lecture : perte de puissance sans effet", B, "lire_v9",
     "elif NON_TENUE in lecture[\"perte_de_puissance\"].values():", "elif False:",
     [LEC + "test_artefact_perte_de_puissance"], r"'puissance perdue'"),
    ("lecture : marge de perte ignorée", B, "lire_v9",
     "p_haut = {n: v8.p_valeur_exacte(x[\"apparie_v8\"][\"perdues\"], x[\"repetitions\"], MARGE_PERTE, \"haute\")",
     "p_haut = {n: v8.p_valeur_exacte(x[\"apparie_v8\"][\"perdues\"], x[\"repetitions\"], 1.0, \"haute\")",
     [LEC + "test_artefact_perte_de_puissance"], r"non tenue|tenue"),
    ("lecture : artefacts appariés (dents sur la classe nouvelle) non lus", B, "lire_v9",
     "        if x[\"ligne\"] in ARTEFACTS_APPARIES and \"apparie_v8\" in x:\n", "        if False:\n",
     [LEC + "test_artefact_banc_sans_dents"], r"KeyError: 'M02\|v8 apparié'|banc sans dents"),
    ("lecture : audit A4 retiré pour la classe par morceaux", B, "lire_v9",
     "if x[\"ligne\"] in CLASSE_LINEAIRE + CLASSE_MORCEAUX and x[\"log_w_max_max\"] > TOLERANCE_LOG_W:",
     "if x[\"ligne\"] in CLASSE_LINEAIRE and x[\"log_w_max_max\"] > TOLERANCE_LOG_W:",
     [LEC + "test_audits_symetriques"], r"'A4 M01\|v9' not found"),
    ("lecture : audit A5 retiré (refus qui ne viendrait pas des morceaux)", B, "lire_v9",
     "            if par_morceaux < x[\"repetitions\"] / 2:\n", "            if False:\n",
     [LEC + "test_audits_symetriques"], r"'A5 M05\|v9' not found"),
    ("lecture : test exact inversé pour les lignes fatales", B, "lire_v9",
     "p_haute = {c: v8.p_valeur_exacte(x[\"promues\"], x[\"repetitions\"], ALPHA, \"haute\")",
     "p_haute = {c: v8.p_valeur_exacte(x[\"promues\"], x[\"repetitions\"], ALPHA, \"basse\")",
     [LEC + "test_cas_sain_tout_tenu_confirme"], r"'confirmé'|non concluant"),
    # --- banc v9 : préenregistrement, graines, liste d'arrêt, code de sortie ---
    ("préenregistrement : brouillon accepté (nom non vérifié)", B, "lire_preenregistrement",
     " or not MOTIF_PREREG.match(os.path.basename(chemin))", "",
     [PRE + "test_cas_sain_et_artefacts_preenregistrement"], r"brouillon[\s\S]*" + NR),
    ("préenregistrement non scellé accepté", B, "lire_preenregistrement", "if not verifier_scelle(chemin):", "if False:",
     [PRE + "test_cas_sain_et_artefacts_preenregistrement"], r"non scellé[\s\S]*PreenregistrementNonScelle not raised"),
    ("préenregistrement : empreintes du code non vérifiées", B, "lire_preenregistrement", "    if ecarts:\n", "    if False:\n",
     [PRE + "test_cas_sain_et_artefacts_preenregistrement"], r"empreinte fausse[\s\S]*" + NR),
    ("graines : espace exploratoire non borné", B, "principal",
     "if not 0 <= args.graine < GRAINE_EXPLORATOIRE_MAX:", "if args.graine < 0:",
     [PRE + "test_refus_du_banc_avant_toute_course"], r"18446744073709551616|1 != 2|0 != 2"),
    ("ligne en erreur : repli silencieux au lieu de l'arrêt", B, "jouer_tout",
     "return resultats, f\"{t[1]}|{t[2]} : {type(e).__name__} : {e}\"", "continue",
     [PRE + "test_banc_reduit_et_liste_d_arret"], r"(0|1) != 3"),
    ("code de sortie : artefact et fatale ignorés", B, "code_de_sortie",
     "return 1 if fatales_au_dessus_de_alpha(resultats) or artefacts_non_vus(resultats) else 0", "return 0",
     [PRE + "test_banc_reduit_et_liste_d_arret"], r"0 != 1"),
]


def appliquer_fonction(module, nom, ancien, nouveau):
    """Fonction `nom` du module recompilée avec `ancien` remplacé par `nouveau` (une seule occurrence), dans l'espace réel du
    module (comme `mutations_v58.appliquer_fonction`), puis restaurée par la fonction rendue."""
    f = getattr(module, nom)
    src = textwrap.dedent(inspect.getsource(f))
    if src.count(ancien) != 1:
        raise LookupError(f"fragment trouvé {src.count(ancien)} fois dans {nom}")
    exec(compile(src.replace(ancien, nouveau), f"<mutation {nom}>", "exec"), vars(module))

    def restaurer():
        setattr(module, nom, f)
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
