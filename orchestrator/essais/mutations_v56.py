"""Banc de mutations de la v56 (R5 : chaque garde neutralisée doit faire échouer son essai, **pour la bonne raison**).

Reprend la mécanique du banc v55 (`mutations_v55` : recompilation avec la cellule `__class__`, raison attendue de l'échec,
défaut du banc distingué, restauration et témoin), ses 103 mutations (v54 et v55, sur leur code et leurs essais) et ajoute les
mutations des gardes neuves de la v56 (essais `test_v56_corrections`). Le lanceur v8 est muté par son chargeur (source relu à
chaque chargement), comme le v7 dans le banc v55. Aucun fichier n'est modifié.

  python3 -B essais/mutations_v56.py [--raisons] [--v56-seulement]      (depuis le dossier de livraison)
"""

import os
import sys
import traceback

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path[:0] = [RACINE, ICI]
sys.dont_write_bytecode = True

from essais import mutations_v55 as m55  # noqa: E402  (mécanique, listes v54 et v55 ; son principal n'est pas joué)
from pole import adaptateurs_v56, budget_v56, configuration_v56, course2_v56, etage_entre_generations_v56  # noqa: E402
from pole import gardes_e0_v56, noyau_v56, prepilote_v56  # noqa: E402

T = "essais.test_v56_corrections."
NR = r"not raised"
C, P, O = course2_v56.GenerationV56, prepilote_v56.PrePiloteV56, noyau_v56.OrchestreV56
LANCEUR = "lanceur_v8"

MUTATIONS_V56 = [
    # CL20-01
    ("CL20-01 modèle servi non recopié", adaptateurs_v56.AdaptateurCommandeExterneV56, "lancer", "return replace(r, modele_servi=servi)",
     "return r", [T + "TestCL20_01AdaptateurReel"], r"Tuples differ: \('ok', None\)"),
    ("CL20-01 ligne 1 sans le vrai adaptateur v56", gardes_e0_v56, "ligne_1_adaptateur_reel",
     "r = lancer(AdaptateurCommandeExterneV56(ok,", "r = lancer(AdaptateurCommandeExterne(ok,", [T + "TestCL20_01AdaptateurReel"],
     r"Tuples differ: \(False, True\)"),
    # CL20-02
    ("CL20-02 protégée sans plafond souple", budget_v56.BudgetV56, "plafond_dur", "if self.retirable(e):", "if True:",
     [T + "TestCL20_02Budget"], r"Tuples differ: \('jouer', 2\.0, False\)|2\.0 != 2\.5"),
    ("CL20-02 attendu des restantes non réservé", budget_v56.BudgetV56, "plafond_dur",
     "self.plafond - self.cumul - self.attendu_restantes(nom)", "self.plafond - self.cumul", [T + "TestCL20_02Budget"],
     r"5\.0 != 2\.5|10\.0, True"),
    ("CL20-02 second programme non consulté", O, "_verifier_et_transmettre",
     "if decisions != self.budget.decisions() or nom not in plafonds or centimes(plafonds[nom]) != centimes(plafond):", "if False:",
     [T + "TestCL20_02Budget.test_artefact_second_programme_et_formule_independante"], r"second programme"),
    ("CL20-02 formule indépendante non consultée", O, "_verifier_et_transmettre",
     "if centimes(p2) != centimes(plafond) or souple2 != detail[\"souple\"]:", "if False:",
     [T + "TestCL20_02Budget.test_artefact_second_programme_et_formule_independante"], NR),
    ("CL20-02 porte non appelée", O, "_verifier_et_transmettre", "accuse = self.portes[f].transmettre(nom, plafond)",
     "accuse = {\"etape\": nom, \"plafond_usd\": plafond, \"par\": \"mutation\"}", [T + "TestCL20_02Budget"], r"RelaisSansPlafond not raised"),
    ("CL20-02 accusé de la porte non vérifié (noyau)", O, "_verifier_et_transmettre",
     "or centimes(accuse[\"plafond_usd\"]) != centimes(plafond):", "or False:",
     [T + "TestCL20_02Budget.test_artefact_porte_injectee_qui_accuse_un_autre_plafond"], NR),
    ("CL20-02 accusé de la commande non vérifié", adaptateurs_v56.PortePlafondCommande, "transmettre",
     "or centimes(v) != centimes(p):", "or False:", [T + "TestCL20_02Budget"], NR),
    ("CL20-02 relais réel sans porte accepté", O, "_portes", "if est_adaptateur_reel(ad):", "if False:", [T + "TestCL20_02Budget", T + "TestCL20_06LectureInterdite"], NR),
    ("CL20-02 coupure ignorée", budget_v56.BudgetV56, "apres_etape", "if bool(coupee) or cout > dur + EPS:", "if False:",
     [T + "TestCL20_02Budget"], r"'jouee' != 'non_mesuree_budget'"),
    ("CL20-02 M6 entière jamais lue réduite", budget_v56, "statut_attendu_coupure",
     "return \"jouee\" if lue_reduite is True else NON_MESUREE", "return NON_MESUREE", [T + "TestCL20_02Budget"],
     r"'non_mesuree_budget' != 'jouee'|Tuples differ"),
    ("CL20-02 réduction non vérifiée d'abord", P, "etape_e9_anteriorite",
     "ordre = premieres + [f for f in fiches if f[\"ident\"] not in set(reduction)]",
     "ordre = [f for f in fiches if f[\"ident\"] not in set(reduction)] + premieres", [T + "TestCL20_02Budget"],
     r"'non_mesuree_budget' != 'jouee'"),
    ("CL20-02 reservation_usd acceptée", budget_v56, "verifier_etapes_v56",
     "if \"reservation_usd\" in e or \"reservation_usd\" in (e.get(\"reduite\") or {}):", "if False:", [T + "TestCL20_02Budget"], NR),
    ("CL20-02 phrase DEP4 acceptée", configuration_v56, "_cles_v56", "if \"dep4_phrase\" in dep:", "if False:", [T + "TestCL20_02Budget"], NR),
    ("CL20-02 cumul au-delà de S17 sans arrêt", O, "jouer_etape",
     "if self.budget.cumul > float(self.conf[\"budget\"][\"plafond_usd\"]) + EPS:", "if False:", [T + "TestCL20_02Budget"], NR),
    ("CL20-02 lignes 11a et 11b non substituées", gardes_e0_v56, "rejouer_gardes_v56", "lignes.remove(par.pop(\"11\"))", "pass",
     [T + "TestLanceurV8"], r"'11' unexpectedly found"),
    # CL20-03
    ("CL20-03 empreinte non vérifiée", configuration_v56, "verifier_specification_v56", "if sha256_fichier(chemin) != p[\"sha256\"]:",
     "if False:", [T + "TestCL20_03Specification"], r"'empreinte' not found"),
    ("CL20-03 sceau non vérifié", configuration_v56, "verifier_specification_v56", "if not verifier_scelle(chemin):", "if False:",
     [T + "TestCL20_03Specification"], r"'non scellé' not found|argument of type 'NoneType'|ligne 29 \(ÉCHEC"),
    ("CL20-03 marqueurs ignorés", configuration_v56, "verifier_specification_v56", "if restants:", "if False:",
     [T + "TestCL20_03Specification"], r"'non gelé' not found|argument of type 'NoneType'|ligne 29 \(ÉCHEC|GardesE0Refusees not raised"),
    ("CL20-03 ligne 29 sans la spécification", gardes_e0_v56, "rejouer_gardes_v56", "l29 = ligne_29_specification(conf, specification)",
     "l29 = None", [T + "TestCL20_03Specification"], r"GardesE0Refusees not raised"),
    ("CL20-03 spécification non exigée au lancement réel", LANCEUR, "executer",
     "if args.moteur == \"reel\" and spec[\"conforme\"] is not True:", "if False:", [T + "TestLanceurV8"], r"'CL20-03' not found"),
    # CL20-04
    ("CL20-04 arrêt de base non noté (course)", C, "executer", "except BaseException as e:", "except Exception as e:", [T + "TestCL20_04Signal"], r"NoneType"),
    ("CL20-04 arrêt de base non noté (pré-pilote)", P, "executer", "except BaseException as e:", "except Exception as e:", [T + "TestCL20_04Signal"], r"NoneType"),
    ("CL20-04 consommations non écrites à l'arrêt", C, "ecrire_fin_commune",
     "ecrire_json_scelle(os.path.join(self.sortie, \"consommations.json\"), {", "(lambda *a: None)(os.path.join(self.sortie, \"x\"), {",
     [T + "TestCL20_04Signal"], r"False is not true|FileNotFoundError.*consommations"),
    # CL20-05
    ("CL20-05 fusions inachevées dans le lot", C, "lot_mesure",
     "and (self.fiches[i][\"meta\"].get(\"origine\") != \"fusion\" or i in completes)]", "]", [T + "TestCL20_05Fusions"],
     r"Items in the first set but not the second|\{'f[0-9a-f]+'|is not false|unexpectedly"),
    ("CL20-05 étape des fusions coupée ignorée", C, "cause_fusion",
     "if etape is not None and self.etapes_etat.get(etape, \"jouee\") != \"jouee\":", "if False:", [T + "TestCL20_05Fusions"],
     r"relais=0\.13|complète avant la coupure|is not false"),
    ("CL20-05 archive vide", C, "ecrire_archive_fusions", "if cause is not None:", "if False:", [T + "TestCL20_05Fusions"],
     r"AssertionError: \d != 3|False is not true"),
    ("CL20-05 « non jugée » confondue", C, "_cause_fiche_fusion", "if not pres or not any(pres.values()):", "if not pres:",
     [T + "TestCL20_05Fusions"], r"relais=0\.04"),
    ("CL20-05 présence des verdicts non notée", O, "juger", "self.verdicts_presents[fiche[\"ident\"]] = presents", "pass",
     [T + "TestCL20_05Fusions"], r"Items in the first set|0 != 3|is not true"),
    ("CL20-05 entrée du bisociateur avec fusions", C, "_entree_bisociateur",
     "return [f for f in super()._entree_bisociateur() if f[\"meta\"].get(\"origine\") != \"fusion\"]",
     "return list(super()._entree_bisociateur())", [T + "TestCL20_05Fusions.test_entree_du_bisociateur_sans_fusion"], r"is not false"),
    # CL20-06
    ("CL20-06 lecture interdite non vérifiée à la construction", O, "__init__",
     "if (v := verifier_lecture_interdite(ad, self.sortie, self.racine_sessions)) is not None}", "if (v := None) is not None}",
     [T + "TestCL20_06LectureInterdite"], r"LectureNonInterdite not raised"),
    ("CL20-06 sortie non cherchée dans denyRead", adaptateurs_v56, "verifier_lecture_interdite",
     "if not any(_sous(cible, d) for d in refus):", "if False:", [T + "TestCL20_06LectureInterdite"], NR),
    ("CL20-06 lanceur sans lecture interdite", LANCEUR, "adaptateurs_reels_v56",
     "ad = AdaptateurClaudeSDK(f[\"url_relais\"], arme=True, interdire_lecture=interdits)",
     "ad = AdaptateurClaudeSDK(f[\"url_relais\"], arme=True)", [T + "TestCL20_06LectureInterdite"], r"None != \["),
    # CL20-07, N5
    ("CL20-07 D-i (2) accepté", prepilote_v56, "verifier_configuration_pre_pilote_v56", "elif d_i != 1:", "elif False:",
     [T + "TestCL20_07DiEtN5"], NR),
    ("CL20-07 D-i non recoupé", configuration_v56, "verifier_dependances_lancement_v56",
     "if isinstance(dec.get(\"d_i\"), str) and MARQUEUR not in dec[\"d_i\"]", "if False and isinstance(dec.get(\"d_i\"), str) and MARQUEUR not in dec[\"d_i\"]",
     [T + "TestCL20_07DiEtN5"], r"False is not true"),
    ("N5 lecture « stricte » acceptée sans code", prepilote_v56, "verifier_configuration_pre_pilote_v56", "elif a21 == \"stricte\":",
     "elif False:", [T + "TestCL20_07DiEtN5"], NR),
    # CL20-08, CL20-09
    ("CL20-08 M6b non écrite en É1", P, "etape_e1_redacteur", "self._ecrire_m6b(etat)", "pass", [T + "TestCL20_08M6b.test_cas_sain_flux_complet"], r"m6b-fiches|A13"),
    ("CL20-08 fiches hors du pré-pilote acceptées", prepilote_v56, "verifier_configuration_pre_pilote_v56", "if k in m:", "if False:",
     [T + "TestCL20_08M6b"], NR),
    ("CL20-08 ligne 31 non jouée sur le flux", P, "_verifier_fiches", "if not ok:", "if False:", [T + "TestCL20_08M6b"], r"0 != 4"),
    ("CL20-08 sceau des fiches non revérifié", P, "etape_e9b_m6b", "if not verifier_scelle(chemin):", "if False:", [T + "TestCL20_08M6b"],
     r"NoeudArret not raised"),
    ("CL20-08 fiche non validée", P, "_ecrire_m6b", "motif = valider_fiche_m6b(fiche, m[\"references_par_fiche\"])", "motif = None",
     [T + "TestCL20_08M6b.test_artefact_fiche_mal_formee"], r"0 != 4|1 != 0|4 != 0"),
    ("CL20-09 copie de la clé gardée après É3", P, "etape_e3_rendus", "self.__dict__.pop(\"_exempts_a8\", None)", "pass",
     [T + "TestCL20_08M6b"], r"True is not false"),
    # CL20-10, CL20-11
    ("CL20-10 mode « modele » sans motif propre", configuration_v56, "_cles_v56", "if mode == \"modele\":", "if False:",
     [T + "TestCL20_10_11Bras"], r"does not match|non branché"),
    ("CL20-10 erreur interne comptée « source absente »", course2_v56, "declarer_bras_v56",
     "except REFUS_LEGITIMES as e:\n                    decl[bras] = {\"produit\": False, \"cause\": CAUSE_SOURCE_ABSENTE",
     "except Exception as e:\n                    decl[bras] = {\"produit\": False, \"cause\": CAUSE_SOURCE_ABSENTE", [T + "TestCL20_10_11Bras"],
     r"ErreurInterneBras not raised"),
    ("CL20-10 forme de l'annexe non vérifiée", course2_v56, "declarer_bras_v56", "forme_annexe_v56(chemin_piece(conf, m[\"annexe\"][\"chemin\"]))",
     "None", [T + "TestCL20_10_11Bras.test_annexe_de_forme_fautive_non_conforme"], r"ErreurInterneBras|'forme' not found"),
    ("CL20-11 cause (iv) du bras basique perdue", C, "_notes", "causes[\"basique\"] = CAUSE_BASIQUE", "pass", [T + "TestCL20_10_11Bras"],
     r"KeyError: 'basique'"),
    ("CL20-11 cause (iii) de Gu-Krenn perdue", C, "_notes", "causes[\"gu_krenn\"] = CAUSE_GK_NOTABLES if len(notables) < 2 else",
     "causes[\"gu_krenn\"] = \"non produit (aucune paire éligible)\" if len(notables) < 2 else", [T + "TestCL20_10_11Bras"],
     r"moins de 2 fiches notables"),
    # CL20-12
    ("CL20-12 modèle servi absent sans arrêt du rôle", O, "appel", "a2 = r.statut == \"ok\" and not servi", "a2 = False",
     [T + "TestCL20_12A2Role"], r"'prop-argon' not found"),
    ("CL20-12 version de juge changée sans arrêt du rôle", O, "juger", "if vu != a[\"r\"].modele_servi:", "if False:",
     [T + "TestCL20_12A2Role"], r"'juge-argon' not found"),
    # CL20-13, CL20-14
    ("CL20-13 numérotation comptée comme nombre ajouté", prepilote_v56, "controle_ancres_v56",
     "ajoutes = sorted(p55.nombres(NUMEROTATION.sub(\" \", brut)) - permis)", "ajoutes = sorted(p55.nombres(brut) - permis)",
     [T + "TestCL20_13_14"], r"Tuples differ: \(1\.0, 2\) != \(1\.0, 0\)"),
    ("CL20-14 liste blanche retirée", etage_entre_generations_v56, "exiger_machine_jetable_v56",
     "inconnus = sorted(n for n in env if n not in NOMS_PERMIS and n not in en_plus)", "inconnus = []", [T + "TestCL20_13_14"], NR),
    ("CL20-14 nom de clé permis par la configuration", etage_entre_generations_v56, "exiger_machine_jetable_v56", "if cles_ajoutees:",
     "if False:", [T + "TestCL20_13_14"], NR),
]


def _appliquer_lanceur_v8(nom, ancien, nouveau):
    import importlib.machinery
    chemin = os.path.join(RACINE, "demonstrations", "ideation_v8.py")
    with open(chemin, encoding="utf-8") as x:
        src = x.read()
    if src.count(ancien) != 1:
        raise LookupError(f"fragment trouvé {src.count(ancien)} fois")
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
    if cible == LANCEUR:
        return _appliquer_lanceur_v8(nom, ancien, nouveau)
    return m55.appliquer(cible, nom, ancien, nouveau)


def principal(argv=None):
    argv = list(argv if argv is not None else sys.argv[1:])
    raisons, seulement = "--raisons" in argv, "--v56-seulement" in argv
    tout = [] if seulement else [(lib, cib, nom, anc, nou, ess, m55.MOTIFS_V54.get(lib, r"(?!)")) for lib, cib, nom, anc, nou, ess in m55.m54.MUTATIONS]
    tout += [] if seulement else m55.MUTATIONS_V55
    tout += MUTATIONS_V56
    noms = sorted({x for m in tout for x in m[5]})
    for n in noms:
        m55.unittest.defaultTestLoader.loadTestsFromName(n)
    temoin = m55.jouer(noms)
    print(f"témoin (aucune mutation) : {temoin[0]} essais, {len(temoin[1])} en échec")
    for t, txt in temoin[1][:5]:
        print(f"      {t} : {m55._derniere_ligne(txt)}")
    comptes, v56 = {}, {id(m) for m in MUTATIONS_V56}
    for m in tout:
        libelle, cible, nom, ancien, nouveau, essais, motif = m
        couche = "v56" if id(m) in v56 else ("v54" if libelle in m55.MOTIFS_V54 else "v55")
        try:
            restaurer = appliquer(cible, nom, ancien, nouveau)
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
    print(f"mutations : {total} (v56 : {len(MUTATIONS_V56)}{'' if seulement else f', v54 : {len(m55.m54.MUTATIONS)}, v55 : {len(m55.MUTATIONS_V55)}'}) ; "
          f"tuées pour la raison attendue : {comptes.get('tuée', 0)} ; tuées pour une autre raison : "
          f"{comptes.get('TUÉE POUR UNE AUTRE RAISON', 0)} ; défaut du banc : {comptes.get('DÉFAUT DU BANC', 0)} ; survivantes : "
          f"{comptes.get('SURVIVANTE', 0)} ; non appliquées : {comptes.get('NON APPLIQUÉE', 0)}")
    print(f"témoin après restauration : {apres[0]} essais, {len(apres[1])} en échec")
    return 0 if comptes.get("tuée", 0) == total and not temoin[1] and not apres[1] else 1


if __name__ == "__main__":
    raise SystemExit(principal())
