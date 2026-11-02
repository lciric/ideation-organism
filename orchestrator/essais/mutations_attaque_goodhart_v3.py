"""Banc de mutations de l'attaque de Goodhart v3 (A1-bis ; R5 : chaque garde neuve neutralisée doit faire échouer son essai,
**pour la bonne raison**). Mécanique du banc v2 (`essais/mutations_attaque_goodhart_v2.py`, inchangé), reprise en version
autonome et étendue aux mutations à plusieurs fragments (liste de couples (ancien, nouveau) sur la même fonction).

Cibles : le cœur `pole/attaque_goodhart_v3.py` et le lanceur `demonstrations/attaque_goodhart_v3.py` (l'instance chargée par les
essais). Aucun fichier n'est modifié ; aucune mutation ne peut lancer une course réelle (les essais du chemin réel n'utilisent
que des commandes factices locales). Les gardes de la v2 restent couvertes par le banc v2.

  python3 -I -B essais/mutations_attaque_goodhart_v3.py [--raisons]      (depuis orchestrator/ ; une ligne par mutation)
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

from essais import test_attaque_goodhart_v3 as t3  # noqa: E402

A3, L = t3.a3, t3.lanceur
T = "essais.test_attaque_goodhart_v3."
NR = r"not raised"
BANC = re.compile(r"NameError|SyntaxError|IndentationError|__class__ cell not found")

MUTATIONS = [
    # --- repli (R5) ---
    ("repli silencieux : unité de repli non étiquetée", A3, "jouer_unite",
     'modele, repli, avant = spec["repli"], True, b.journal', 'modele, repli, avant = spec["repli"], False, b.journal',
     [T + "Repli.test_bascule_au_debut_d_une_unite_cas_sain"], r"test_bascule_au_debut[\s\S]*False is not true"),
    ("bascule au milieu d'une unité (sonde à toute tentative)", A3, "jouer_suite",
     "if sonde_repli is not None and k == 1 and brut is None and _echecs_consecutifs_pour_bascule(journal):",
     "if sonde_repli is not None and brut is None and _echecs_consecutifs_pour_bascule(journal):",
     [T + "Repli.test_jamais_au_milieu_d_une_unite"], r"test_jamais_au_milieu[\s\S]*True is not false"),
    ("essais_avant_repli ignoré : bascule au premier échec", A3, "jouer_suite",
     "essais = sonde_repli[1] if (sonde_repli is not None and k == 1) else 2", "essais = 1 if (sonde_repli is not None and k == 1) else 2",
     [T + "Repli.test_moins_d_echecs_que_le_seuil_reste_principal"], r"test_moins_d_echecs[\s\S]*True is not false"),
    ("repli non déclaré : bascule vers un modèle par défaut", A3, "jouer_unite",
     [('sonde = (spec["repli"], essais_avant_repli) if spec.get("repli") else None',
       'sonde = (spec.get("repli") or "claude-opus-4-6", essais_avant_repli)'),
      ('        if not spec.get("repli"):\n            raise AttaqueRefusee("bascule demandée sans repli déclaré : refusée (jamais de repli non déclaré)")\n'
       '        modele, repli, avant = spec["repli"], True, b.journal',
       '        modele, repli, avant = spec.get("repli") or "claude-opus-4-6", True, b.journal')], None,
     [T + "Repli.test_sans_repli_declare_jamais_de_bascule"], r"test_sans_repli_declare[\s\S]*True is not false"),
    ("modèle servi non écrit au journal de chaque appel", A3, "appeler",
     '"modele_demande": modele,\n                        "modele_servi": servi})', '"modele_demande": modele})',
     [T + "Repli.test_modele_demande_et_servi_ecrits_a_chaque_appel"], r"modele_servi"),
    ("modeles_servis_permis non vide accepté (repli muet par la configuration)", L, "reglages_de_configuration",
     '        if f.get("modeles_servis_permis"):\n', "        if False:\n",
     [T + "LanceurCheminReel.test_artefacts_de_configuration"], r"repli muet[\s\S]*" + NR),
    # --- lecture à part ---
    ("unités de repli fondues dans « ensemble »", A3, "_taux",
     '                        sel = [s for s in sel0 if not s.get("repli")]', "                        sel = list(sel0)",
     [T + "LectureAPart.test_unites_de_repli_comptees_a_part"], r"test_unites_de_repli[\s\S]*4 != 2"),
    ("colonne du fournisseur fondue avec sa colonne de repli", A3, "colonne_de",
     'return suite["fournisseur"] + ("-repli" if suite.get("repli") else "")', 'return suite["fournisseur"]',
     [T + "LectureAPart.test_unites_de_repli_comptees_a_part"], r"test_unites_de_repli[\s\S]*0 != 2"),
    ("unités de repli dans Δ et dans les paires", A3, "lire_monde",
     '    principales = [s for s in choisies if not s.get("repli")]', "    principales = list(choisies)",
     [T + "LectureAPart.test_unites_de_repli_comptees_a_part"], r"test_unites_de_repli[\s\S]*4 != 2"),
    # --- fournisseurs lus du texte ---
    ("fournisseurs codés en dur dans le lanceur", L, "lire_plan",
     "fournisseurs = a3.verifier_fournisseurs([lire_fournisseur(n, lignes_f[n]) for n in noms])",
     "fournisseurs = a3.verifier_fournisseurs(list(a3.PLAN_A1_BIS))",
     [T + "LanceurPlan.test_plan_de_course_lu_du_texte"], r"PreenregistrementRefuse|!="),
    ("mode du bloc non confronté au nom du texte", L, "lire_plan",
     "    if mode_attendu is not None and mode != mode_attendu:\n", "    if False:\n",
     [T + "LanceurPlan.test_artefacts_du_plan"], r"cas=\"mode d'essai dans un texte de course\"[\s\S]*" + NR),
    ("texte à un autre chemin accepté", L, "lire_preenregistrement",
     "    if os.path.dirname(reel) != dossier or mode is None:\n", '    mode = mode or "course"\n    if False:\n',
     [T + "LanceurPreenregistrement.test_artefacts_isoles"], r"cas='brouillon'[\s\S]*" + NR),
    # --- compteur, fils, part ---
    ("compteur sans verrou", A3, "Compteur",
     "    def compter(self, fournisseur, cout, statut, modele_servi=None, modele_demande=None, duree_s=None):\n        with self.verrou:\n",
     "    def compter(self, fournisseur, cout, statut, modele_servi=None, modele_demande=None, duree_s=None):\n        if True:\n",
     [T + "CompteurPartage.test_compter_et_verifier_sous_verrou"], r"\['entrée', 'sortie'\] != \['entrée', 'sortie', 'entrée', 'sortie'\]"),
    ("part du plafond entière transmise à chaque porte", L, "proposeurs_reels",
     'part = plan["plafond_usd"] / len(fournisseurs)', 'part = plan["plafond_usd"]',
     [T + "LanceurCheminReel.test_cas_sain_quatre_proposeurs_part_repartie_repli_demande_explicitement"], r"1000\.0[\s\S]*!= [\s\S]*250\.0"),
    ("le fil change le résultat (graine décalée sur les fils de rang > 0)", A3, "jouer_tout",
     "s = jouer_unite(proposeurs[f], spec, carte(entropie, ci, w), entropie, compteur, n_max, essais)",
     "s = jouer_unite(proposeurs[f], spec, carte(entropie + (0 if threading.current_thread().name.endswith('_0') "
     "or '_' not in threading.current_thread().name else 1), ci, w), entropie, compteur, n_max, essais)",
     [T + "Fils.test_un_fil_egale_trois_fils"], r"test_un_fil_egale_trois_fils[\s\S]*!="),
    # --- mode essai ---
    ("issue calculée en mode essai", A3, "rapport_essai",
     'return verifier_sortie_essai({"mesures": sortie})', 'return {"mesures": sortie, "issue": "résiste (à cette taille)"}',
     [T + "Essai.test_mode_essai_sans_issue"], r"'issue'"),
    ("garde des clés d'issue retirée du rapport d'essai", A3, "verifier_sortie_essai",
     '                if isinstance(k, str) and (k in CLES_INTERDITES_EN_ESSAI or CLE_DE_TAUX.match(k) or k.startswith("issue")):\n',
     "                if False:\n", [T + "Essai.test_un_essai_qui_reclame_une_issue_est_refuse"], r"AttaqueRefusee " + NR),
    # --- grilles ---
    ("grille non admise acceptée (ε par défaut)", A3, "verifier_grille",
     '    if u not in GRILLES:\n        raise AttaqueRefusee(f"grille : {u} unités par case non admise ; admises : {sorted(GRILLES)}")\n'
     '    eps = GRILLES[u]["eps"]', '    eps = GRILLES.get(u, {"eps": 0.25})["eps"]',
     [T + "Grilles.test_artefacts_de_grille"], r"AttaqueRefusee " + NR),
    ("chevauchement de « résiste » et « brèche » non vérifié", A3, "verifier_grille",
     "    if r is None or r >= b:\n", "    if False:\n", [T + "Grilles.test_artefacts_de_grille"], r"AttaqueRefusee " + NR),
    # --- devis ---
    ("devis au taux du premier fournisseur pour tous", A3, "devis",
     "    for f in fournisseurs:\n", '    for f in [dict(x, taux_usd=fournisseurs[0]["taux_usd"]) for x in fournisseurs]:\n',
     [T + "Devis.test_devis_par_fournisseur"], r"test_devis_par_fournisseur[\s\S]*!= \(\[72\.0, 132\.0\], 192\.0\)"),
    ("plafond sous le maximum du devis accepté", L, "lire_plan", '    if not plafond >= d["total"]["usd_max"]:\n', "    if False:\n",
     [T + "LanceurPlan.test_artefacts_du_plan"], r"cas='plafond sous le devis'[\s\S]*" + NR),
    ("durée sous la durée attendue haute (avec fils) acceptée", L, "lire_plan", "    if not duree >= attendue:\n", "    if False:\n",
     [T + "LanceurPlan.test_artefacts_du_plan"], r"cas='durée sous la durée attendue haute'[\s\S]*" + NR),
]


def appliquer_fonction(module, nom, ancien, nouveau):
    """Fonction ou classe `nom` du module recompilée avec `ancien` remplacé par `nouveau` (une seule occurrence ; ou une liste
    de couples (ancien, nouveau), chacun une seule occurrence), dans l'espace réel du module, puis substituée ; rend la
    fonction de restauration."""
    f = getattr(module, nom)
    src = textwrap.dedent(inspect.getsource(f))
    couples = ancien if isinstance(ancien, list) else [(ancien, nouveau)]
    for a, n in couples:
        if src.count(a) != 1:
            raise LookupError(f"fragment trouvé {src.count(a)} fois dans {nom}")
        src = src.replace(a, n)
    exec(compile(src, f"<mutation {nom}>", "exec"), vars(module))

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
