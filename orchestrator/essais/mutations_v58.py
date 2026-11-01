"""Banc de mutations de la v58 (R5 : chaque garde neutralisée doit faire échouer son essai, **pour la bonne raison**).

Sur le modèle de `mutations_v56.py` (mécanique de `mutations_v55` : source de la fonction relu, fragment remplacé une seule
fois, recompilé dans l'espace du module, substitué, puis restauré ; raison attendue de l'échec propre à chaque mutation ;
défaut du banc distingué ; témoin avant et après), en version autonome et légère : les listes v54 à v56 ne sont pas
rejouées ici (`mutations_v56.py` les garde). Cibles :
- `pole/nul_v8.py` : configuration du juge, garde de configuration, membres d'archive, garde des membres ;
- le banc des tricheurs v8 (l'instance chargée par les essais, `test_v58_nul_v8.banc`) : graines et espaces de graines,
  règle du préenregistrement (fichier nommé, scellement, code gelé complet, plan), lecture gelée (test exact, Clopper-Pearson,
  Holm, marge de perte, issues, audits), code de sortie, liste d'arrêt ;
- les démonstrations v8 : mutées par leur chargeur (source relu à chaque chargement), comme le lanceur v8 dans le banc v56.
Les mutations « membre retiré, garde contournée » ne visent que les essais statistiques (tricheurs du banc à 20
répétitions) : elles montrent que ces essais ont des dents sans l'aide de la garde structurelle. Aucun fichier n'est modifié.
Aucune mutation ne peut lancer une vraie course décisive : l'essai des refus remplace la course par un bouchon.

  python3 -I -B essais/mutations_v58.py [--raisons]      (depuis orchestrator/ ; une ligne par mutation)
"""

import importlib.machinery
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

from essais import test_v58_nul_v8 as t58  # noqa: E402
from pole import nul_v8  # noqa: E402

T = "essais.test_v58_nul_v8."
B = t58.banc  # instance du banc v8 que les essais appellent
NR = r"not raised"
BANC = re.compile(r"NameError|SyntaxError|IndentationError|__class__ cell not found")
DEMO_PROPOSEUR = os.path.join("demonstrations", "demo_couche1_proposeur_v8.py")
DEMO_COUCHE1 = os.path.join("demonstrations", "demo_couche1_v8.py")
PRE, LEC = T + "GrainesEtPreenregistrement.", T + "LectureGelee."

MUTATIONS = [
    # --- pole/nul_v8.py : configuration ---
    ("nul_archive_ajuste forcé à faux (garde en place)", nul_v8, "configuration_nul_v8",
     "ConfigGeneration(**dict(reglages, **REGLAGES_NUL_V8))",
     "ConfigGeneration(**dict(reglages, **dict(REGLAGES_NUL_V8, nul_archive_ajuste=False)))",
     [T + "ConfigurationNulV8.test_cas_sain_nul_v8_impose_autres_reglages_conserves"], r"NulV8Refuse: nul v8 : juge configuré sans"),
    ("nul_archive_ajuste forcé à faux et garde retirée", nul_v8, "configuration_nul_v8",
     "config = ConfigGeneration(**dict(reglages, **REGLAGES_NUL_V8)).valider()\n    return exiger_nul_v8(config)",
     "config = ConfigGeneration(**dict(reglages, **dict(REGLAGES_NUL_V8, nul_archive_ajuste=False))).valider()\n    return config",
     [T + "ConfigurationNulV8.test_cas_sain_nul_v8_impose_autres_reglages_conserves", T + "ProductionNulV8"],
     r"nul v8 : nul_archive_ajuste doit être vrai|M1 survit sous le nul v8"),
    ("refus remplacé par un repli silencieux (réglage contraire écrasé)", nul_v8, "configuration_nul_v8", "    if ecarts:\n",
     "    if False:\n", [T + "ConfigurationNulV8.test_artefact_configuration_sans_nul_ajuste_refusee"], NR),
    ("garde de type relâchée (1 vaut vrai)", nul_v8, "_conforme",
     "return type(valeur) is type(attendu) and valeur == attendu", "return valeur == attendu",
     [T + "ConfigurationNulV8.test_artefact_configuration_sans_nul_ajuste_refusee"], r"nul_archive_ajuste': 1\}.*" + NR),
    ("garde de configuration neutralisée", nul_v8, "exiger_nul_v8", "    if ecarts:\n", "    if False:\n",
     [T + "ConfigurationNulV8.test_artefact_garde_refuse_un_juge_construit_sans_nul_v8"], NR),
    # --- pole/nul_v8.py : membres ---
    ("membre ajuste_lineaire:archive retiré, garde contournée (essais statistiques seuls)", nul_v8, "membres_archive_v8",
     "return exiger_membres_ajustes(membres, survivantes, lois_parents)",
     "return [m for m in membres if m[\"nom\"] != MEMBRE_LINEAIRE]",
     [T + "ArtefactsTricheurs"], r"T0(2|3b|4)\|v8 promue [1-9]\d*/20 sous le nul v8"),
    ("survivantes tempérées et inclinées retirées, garde contournée (essais statistiques seuls)", nul_v8, "membres_archive_v8",
     "return exiger_membres_ajustes(membres, survivantes, lois_parents)",
     "return [m for m in membres if not m[\"nom\"].startswith(\"ajuste_log:archive:\")]",
     [T + "ArtefactsTricheurs"], r"T05s\|v8 promue [1-9]\d*/20 sous le nul v8"),
    ("membres d'archive demandés sans ajustement (ajuste=False)", nul_v8, "membres_archive_v8", "memoire, ajuste=True,",
     "memoire, ajuste=False,",
     [T + "ArtefactsTricheurs"], r"NulV8Refuse: nul v8 : membre\(s\) ajusté\(s\) absent\(s\)"),
    ("garde des membres neutralisée", nul_v8, "exiger_membres_ajustes", "    if defauts:\n", "    if False:\n",
     [T + "MembresNulV8.test_artefact_membre_ajuste_absent_ou_altere_refuse"], NR),
    ("garde des membres : lois mises en commun non vérifiées", nul_v8, "exiger_membres_ajustes",
     " or lineaire[0].get(\"lois\") != connues", "", [T + "MembresNulV8.test_artefact_membre_ajuste_absent_ou_altere_refuse"],
     r"mise en commun tronquée[\s\S]*" + NR),
    # --- banc v8 : graines ---
    ("graines : répétition absente de la clé", B, "graines", "spawn_key=(cle_ligne(ident), int(r))",
     "spawn_key=(cle_ligne(ident),)", [PRE + "test_graines_seedsequence"], r"Tuples differ|!= 4"),
    ("graines : clés de lignes non vérifiées", B, "verifier_cles_distinctes",
     "    if len(set(idents)) != len(idents) or len(set(cles)) != len(cles):\n", "    if False:\n",
     [PRE + "test_cles_de_graines_distinctes"], r"ValueError not raised"),
    ("graines : espace exploratoire non borné (graine ≥ 2⁶⁴ acceptée)", B, "principal",
     "if not 0 <= args.graine < GRAINE_EXPLORATOIRE_MAX:", "if args.graine < 0:",
     [PRE + "test_refus_du_banc_avant_toute_course"], r"refus attendu pour \[.*18446744073709551616"),
    ("graines : entropie décisive dans l'espace exploratoire acceptée", B, "lire_preenregistrement",
     "    if entropie < GRAINE_EXPLORATOIRE_MAX:\n", "    if False:\n",
     [PRE + "test_artefacts_preenregistrement"], r"EcartAuPlan not raised"),
    # --- banc v8 : règle du préenregistrement ---
    ("préenregistrement : autre fichier que le fichier nommé accepté", B, "lire_preenregistrement",
     "    if os.path.realpath(chemin) != os.path.realpath(PREREG_DECISIF):\n", "    if False:\n",
     [PRE + "test_artefacts_preenregistrement"], r"EcartAuPlan not raised"),
    ("préenregistrement non scellé accepté", B, "lire_preenregistrement", "if not verifier_scelle(chemin):", "if False:",
     [PRE + "test_artefacts_preenregistrement"], r"PreenregistrementNonScelle not raised"),
    ("préenregistrement : code importé non exigé dans le gel", B, "lire_preenregistrement", "    if manquants:\n",
     "    if False:\n", [PRE + "test_artefacts_preenregistrement"], r"EcartAuPlan not raised"),
    ("préenregistrement : empreintes du code gelé non vérifiées", B, "lire_preenregistrement", "    if ecarts:\n",
     "    if False:\n", [PRE + "test_artefacts_preenregistrement"], r"EcartAuPlan not raised"),
    ("préenregistrement : plan gelé non vérifié (--lignes, --repetitions, --duree-max-s)", B, "principal",
     "if args.lignes or args.repetitions != REPETITIONS_DECISIVES or args.duree_max_s != DUREE_MAX_S:", "if False:",
     [PRE + "test_refus_du_banc_avant_toute_course"], r"refus attendu pour \[.*'--lignes', 'T02'"),
    # --- banc v8 : lecture gelée ---
    ("lecture : sens du test exact inversé", B, "p_valeur_exacte", "        return binom_cdf(succes, n, seuil)",
     "        return binom_sf(succes, n, seuil)", [LEC + "test_cas_sain_tout_tenu_confirmee"],
     r"Items in the first set but not the second:\s*'non jugeable"),
    ("lecture : borne basse de Clopper-Pearson remplacée par la proportion observée", B, "clopper_pearson",
     "bas = 0.0 if x == 0 else _bissection(lambda p: binom_sf(x, n, p) - gamma, 0.0, 1.0)", "bas = x / n",
     [LEC + "test_bornes_de_clopper_pearson_et_valeurs_p_exactes"], r"borne basse de Clopper-Pearson"),
    ("lecture : Holm retiré (bornes non corrigées)", B, "holm", "if p_valeurs[cle] > niveau / (len(ordre) - j):",
     "if p_valeurs[cle] > niveau:", [LEC + "test_correction_de_holm"], r"test_correction_de_holm[\s\S]*Tuples differ"),
    ("lecture : marge de perte ignorée", B, "p_valeur_newcombe", "return haut < marge if sens == \"haute\" else bas > marge",
     "return haut < 1.0 if sens == \"haute\" else bas > marge", [LEC + "test_perte_de_puissance"],
     r"test_perte_de_puissance[\s\S]*Tuples differ"),
    ("lecture : ligne fatale non tenue sans effet sur l'issue", B, "lire_v8",
     "elif NON_TENUE in lecture[\"fatales\"].values():", "elif False:",
     [LEC + "test_artefact_ligne_fatale_au_dessus_de_alpha_infirmee"], r"infirmée \(validité\)"),
    ("lecture : banc sans dents lu comme confirmé", B, "lire_v8",
     "    elif not artefacts or any(v != TENUE for v in artefacts):\n", "    elif False:\n",
     [LEC + "test_artefact_requis_non_vu_banc_sans_dents"], r"banc sans dents"),
    ("lecture : audit A1 retiré (promotion d'une ligne refusée par construction)", B, "lire_v8",
     "        if x[\"ligne\"] in CLASSE_LINEAIRE + CLASSE_LOG_LINEAIRE and x[\"promues\"] > 0:\n", "        if False:\n",
     [LEC + "test_audits_symetriques"], r"A1 : promotion d'une ligne refusée par construction"),
    ("lecture : audit A2 retiré (v8 plus puissant que v7)", B, "lire_v8",
     "        if newcombe(a[\"promues\"], a[\"repetitions\"], b[\"promues\"], b[\"repetitions\"], Z_95)[1] < 0:\n",
     "        if False:\n", [LEC + "test_audits_symetriques"], r"A2 : nul v8 plus puissant que v7"),
    ("lecture : audit A4 retiré (log W > 0 dans la classe linéaire)", B, "lire_v8",
     "        if x[\"ligne\"] in CLASSE_LINEAIRE and x[\"log_w_max_max\"] > TOLERANCE_LOG_W:\n", "        if False:\n",
     [LEC + "test_audits_symetriques"], r"A4 : log W > 0 dans la classe linéaire"),
    ("code de sortie : artefact non vu ignoré", B, "code_de_sortie",
     "return 1 if fatales_au_dessus_de_alpha(resultats) or artefacts_non_vus(resultats) else 0",
     "return 1 if fatales_au_dessus_de_alpha(resultats) else 0",
     [LEC + "test_artefact_requis_non_vu_banc_sans_dents"], r"artefact non vu sans échec du code de sortie"),
    ("code de sortie du script forcé à 0 (l'intégration continue ne peut plus échouer)", B, "principal",
     "    return code_de_sortie(resultats)\n", "    return 0\n",
     [PRE + "test_banc_reduit_et_liste_d_arret"], r"ligne fatale au-dessus de α sans échec du code de sortie"),
    # --- banc v8 : liste d'arrêt ---
    ("ligne en erreur : repli silencieux au lieu de l'arrêt", B, "jouer_tout",
     "return resultats, f\"{t[1]}|{t[2]} : {type(e).__name__} : {e}\"", "continue",
     [PRE + "test_banc_reduit_et_liste_d_arret"], r"test_banc_reduit_et_liste_d_arret[\s\S]*0 != 3"),
    # --- démonstrations v8 (chargeur) ---
    ("démonstration v8 avec proposeur : configuration de la v7 non remplacée", DEMO_PROPOSEUR, None,
     "v7.ConfigGeneration = configuration\n", "", [T + "DemonstrationsV8.test_cas_sain_configuration_remplacee_par_le_nul_v8"],
     r"nul v8 : nul_archive_ajuste doit être vrai"),
    ("démonstration v8 avec proposeur : garde de executer_pole retirée", DEMO_PROPOSEUR, None,
     "    nul_v8.exiger_nul_v8(config)\n", "", [T + "DemonstrationsV8.test_artefact_course_sans_nul_v8_refusee_avant_ecriture"],
     NR + r"|ValueError: la liste de témoins ne contient aucun témoin"),  # la course v7 a pris la main : garde franchie
    ("démonstration v8 couche 1 : configuration de la v7 non remplacée", DEMO_COUCHE1, None,
     "v7.ConfigGeneration = configuration\n", "", [T + "DemonstrationsV8.test_cas_sain_configuration_remplacee_par_le_nul_v8"],
     r"nul v8 : nul_archive_ajuste doit être vrai"),
]


def appliquer_fonction(module, nom, ancien, nouveau):
    """Fonction `nom` du module recompilée avec `ancien` remplacé par `nouveau` (une seule occurrence), puis substituée.

    Compilée dans l'espace **réel** du module (pas une copie) : la fonction mutée voit les attributs que les essais
    remplacent pendant leur exécution (`unittest.mock.patch.object(banc, "PREREG_DECISIF", …)`) ; avec une copie, elle
    lisait l'ancienne valeur et la mutation était tuée pour une autre raison (défaut du banc v58, corrigé)."""
    f = getattr(module, nom)
    src = textwrap.dedent(inspect.getsource(f))
    if src.count(ancien) != 1:
        raise LookupError(f"fragment trouvé {src.count(ancien)} fois dans {nom}")
    exec(compile(src.replace(ancien, nouveau), f"<mutation {nom}>", "exec"), vars(module))  # lie `nom` à la version mutée

    def restaurer():
        setattr(module, nom, f)
    return restaurer


def appliquer_source(relatif, ancien, nouveau):
    """Fichier rechargé à chaque chargement (démonstrations) : le chargeur rend le source muté."""
    chemin = os.path.join(RACINE, relatif)
    with open(chemin, encoding="utf-8") as x:
        src = x.read()
    if src.count(ancien) != 1:
        raise LookupError(f"fragment trouvé {src.count(ancien)} fois dans {relatif}")
    orig = importlib.machinery.SourceFileLoader.get_data

    def get_data(self, path):
        if os.path.realpath(path) == os.path.realpath(chemin):
            return src.replace(ancien, nouveau).encode("utf-8")
        return orig(self, path)
    importlib.machinery.SourceFileLoader.get_data = get_data

    def restaurer():
        importlib.machinery.SourceFileLoader.get_data = orig
    return restaurer


def appliquer(cible, nom, ancien, nouveau):
    if isinstance(cible, str):
        return appliquer_source(cible, ancien, nouveau)
    return appliquer_fonction(cible, nom, ancien, nouveau)


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
            restaurer = appliquer(cible, nom, ancien, nouveau)
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
        print(f"{verdict}  {libelle} : {len(echecs)}/{n} essais en échec")
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
