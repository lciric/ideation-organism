"""Banc de mutations du code v66 : les 20 mutations du contre-lecteur du code v65 (X01 à X20, `contre-lecture-code-v65-v2.md`,
`c4ddfc7f…`, section 3, CLV65-04 ; X06 « toute la branche réelle » découpée en six), les 38 mutations du banc v65 portées sur le
code que joue la v66, et les mutations neuves des corrections CLV65-01 à CLV65-10.

Chaque mutation est une liste de remplacements textuels exacts (chaque texte d'origine présent **une seule fois**) dans une copie
neuve de `orchestrator/` ; on joue les essais nommés sur la copie mutée, **sans** `-x`, et l'on relève les essais en échec.
Issues : « tuée » si au moins un essai en échec est celui de la **raison attendue** (sous-chaîne de son identifiant) ; « tuée
pour une autre raison » sinon ; « survit » si tout passe ; « défaut du banc » si un texte d'origine manque ou est ambigu, ou si
pytest ne joue rien (code 5) ou se plaint de son usage. Le banc commence par jouer chaque sélection sur la copie **non mutée** :
chacune doit réussir avec au moins un essai **passé** (une sélection entièrement sautée est un défaut du banc, jamais « survit »
ni « tuée » : CLV65-06) et la raison attendue de chaque mutation doit être un essai collecté de sa sélection.

  POLE_ESSAI_BAC_REEL_NON_JOUE=1 python3 -I -B essais/mutations_boucle_reelle_v66.py [--processus 4] [--sortie RESULTAT.json]
      [--seulement ID,ID] [--verifier-textes]
Codes : 0 toutes tuées pour la raison attendue ; 1 au moins une autre issue ; 2 essais sains en échec ou raison non collectée.
"""

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
C66, C65 = "pole/boucle_reelle_v66.py", "pole/boucle_reelle_v65.py"
LB, RG = "pole/lecture_boucle_reelle_v66.py", "pole/registre_go_v66.py"
DL, LP = "demonstrations/boucle_reelle_v66.py", "demonstrations/lire_boucle_reelle_v66.py"
TB, TL, TR = "essais/test_boucle_reelle_v66.py", "essais/test_lecture_boucle_reelle_v66.py", "essais/test_registre_go_v66.py"


def M(ident, origine, fichier, paires, essais, raison):
    return {"id": ident, "origine": origine, "fichier": fichier, "paires": [paires] if isinstance(paires, tuple) else paires,
            "essais": essais, "raison": raison}


FAM_C = ('    T.exiger_familles_separees((roles["experimentateur"][0], roles["familles"]["experimentateur"]),\n'
         '                               (roles["verificateur"][0], roles["familles"]["verificateur"]))\n'
         '    adaptateur_etage.parts')
FAM_L = ('        T.exiger_familles_separees((roles["experimentateur"][0], roles["familles"]["experimentateur"]),\n'
         '                                   (roles["verificateur"][0], roles["familles"]["verificateur"]))\n'
         '        if args.verifier_seulement:')
CL, V65, V66 = "contre-lecteur", "banc v65 porté", "neuve v66"

MUTATIONS = [
    # --- les vingt du contre-lecteur (CLV65-04), sur le code que joue la v66 ---------------------------------------------------
    M("X01-garde-7-selection", CL, C66, ("        exiger_selection_sans_plantee(retenues, ids_plantees, tache)\n", "        pass\n"),
      [(TB, "loi_plantee_dans_la_selection")], "test_artefact_loi_plantee_dans_la_selection"),
    M("X02-familles-coeur", CL, C66, (FAM_C, "    adaptateur_etage.parts"), [(TB, "familles_dans_le_coeur")], "test_familles_dans_le_coeur"),
    M("X03-familles-lanceur", CL, DL, (FAM_L, "        if args.verifier_seulement:"), [(TB, "familles_dans_le_lanceur")],
      "test_familles_dans_le_lanceur"),
    M("X04-appel-garde-21", CL, C66, ("            B65.exiger_copies_de_la_selection(copies, h2)\n", ""),
      [(TB, "copie_d_une_carte_non_retenue")], "test_artefact_copie_d_une_carte_non_retenue"),
    M("X05-bac-factice-reel", CL, DL, ('        if args.bac == "factice" and reel:', "        if False:"), [(TB, "refus_nommes")], "test_refus_nommes"),
    M("X06a-reel-GO-verifie", CL, DL, ('                go = R.verifier_go_v66(args.go, args.registre_go, p["go_montant_usd"], part=PART_DU_GO)',
                                        '                go = {"identifiant": args.go, "plafond_lu_usd": 45.0}'),
      [(TB, "refus_nommes")], "test_refus_nommes"),
    M("X06b-reel-GO-du-texte", CL, DL, ('            if not args.registre_go or args.go != p["go"]:', "            if not args.registre_go:"),
      [(TB, "refus_nommes")], "test_refus_nommes"),
    M("X06c-reel-empreinte-configuration", CL, DL, ('            if sha_conf != p["configuration_sha256"]:', "            if False:"),
      [(TB, "refus_nommes")], "test_refus_nommes"),
    M("X06d-reel-options", CL, DL, ("            if args.graine is not None or options:", "            if False:"), [(TB, "refus_nommes")],
      "test_refus_nommes"),
    M("X06e-reel-confirmation", CL, DL, ('            if args.moteur != "reel" or not args.confirmer_moteur_reel or not args.configuration or not args.heritage_depart:',
                                          "            if False:"), [(TB, "refus_nommes")], "test_refus_nommes"),
    M("X06f-reel-garde-17", CL, DL, ("            heritage_depart = B65.lire_heritage_depart(chemin_depart, sha_depart, jeu)  # garde 17, avant toute porte",
                                      '            heritage_depart = {"archive": dict(jeu["archive_de_depart"]), "bilan_sha256": sha_depart}'),
      [(TB, "refus_nommes")], "test_refus_nommes"),
    M("X07-cout-appel-qui-s-arrete", CL, C66, ('            compteur.ajouter(e.cout, "proposeur", p.relais)\n            raise\n', "            raise\n"),
      [(TB, "cout_d_un_appel")], "test_artefact_cout_d_un_appel_qui_s_arrete_compte"),
    M("X08-plafond-restant", CL, C65, ("    if compteur.plafond_usd - compteur.usd < float(besoin_usd) - 1e-9:", "    if False:"),
      [(TB, "plafond_restant")], "test_artefact_plafond_restant_avant_l_appel"),
    M("X09-heritage-version-generation", CL, C65, ('    if not isinstance(h, dict) or h.get("version") != VERSION_HERITAGE_DEPART or h.get("generation") != 0:',
                                                    "    if not isinstance(h, dict):"), [(TB, "garde_17")], "test_garde_17"),
    M("X10-jeu-grammaire", CL, C65, ("            motif = T.verifier_loi_servable(loi)\n", "            motif = None\n"),
      [(TB, "garde_19")], "test_garde_19"),
    M("X11-lecteur-empreinte", CL, LP, ("    if not isinstance(sha_attendue, str) or sha != sha_attendue:", "    if False:"),
      [(TB, "bout_en_bout")], "test_bout_en_bout_et_lecture"),
    M("X12-lecteur-monde", CL, LP, ('    if rapport["releve"].get("monde_sha256") != monde["sha256"]:', "    if False:"),
      [(TB, "bout_en_bout")], "test_bout_en_bout_et_lecture"),
    M("X13-relecture-finale", CL, C66, ("            fin = lire(d2, sha2)  # la sélection de la génération 2 est scellée et relue ; aucune génération 3",
                                         '            fin = {"archive": {}, "retenues": [], "bilan_sha256": sha2}'),
      [(TB, "relecture_finale_refusee")], "test_artefact_relecture_finale_refusee"),
    M("X14-plan-positifs", CL, DL, ("    if any(not (v > 0) for v in reels.values()):", "    if False:"), [(TB, "plan_artefacts")],
      "test_plan_artefacts"),
    M("X15-A1-contre-calcul", CL, LB, ('"contre_calcul_egal": bool(testees) and all(x.get("contre_calcul_ok") is True for x in testees),',
                                        '"contre_calcul_egal": True,'), [(TL, "A1_artefacts")], "test_A1_artefacts"),
    M("X16-A1-bac-reel", CL, LB, ('"bac_reel_partout": len(etages) == 2 and all(e.get("factice") is False for e in etages),',
                                   '"bac_reel_partout": True,'), [(TL, "A1")], "test_A1_d_office_sous_C1"),
    M("X17-A3", CL, LB, ('"non concluante" if p.get("verdict") == "non concluant"', '"non concluante" if False'), [(TL, "A3")],
      "test_A3_sans_dents"),
    M("X18-fausse-decouverte-reelle", CL, LB, ('        if k["fausse_decouverte"]:\n            fd.append(', "        if False:\n            fd.append("),
      [(TL, "fausse_decouverte_en_tete")], "test_oracle_mesures_wilson_et_fausse_decouverte_en_tete"),
    M("X19a-g2-ne-sert-que-K1", CL, C66, ("    vue = bf.vue_pour_proposeur(heritage)\n",
                                           '    vue = bf.vue_pour_proposeur(dict(heritage, archive={k: v for k, v in heritage["archive"].items() if k == "K1"}))\n'),
      [(TB, "vues_servies_au_releve")], "test_sain_vues_servies_au_releve"),
    M("X19b-texte-servi-K1", CL, C66, ("            texte, cout = p.proposer(consigne, contexte, tache)",
                                        '            texte, cout = p.proposer(consigne, dict(contexte, lois_retenues=contexte["lois_retenues"][:1]), tache)'),
      [(TB, "vues_servies_au_releve")], "test_sain_vues_servies_au_releve"),
    M("X20-seuil-T-ELIM", CL, C65, ('seuil=SEUIL_T_ELIM if nom == "T-ELIM" else SEUIL_TEST', "seuil=SEUIL_TEST"), [(TL, "C1_sain")],
      "test_C1_sain"),
    # --- banc v65 porté sur le code que joue la v66 -----------------------------------------------------------------------------
    M("G17-empreinte", V65, C65, ('h = bf.lire_scelle_verifie(chemin, sha_du_texte, "héritage de départ")', 'h = json.load(open(chemin, encoding="utf-8"))'),
      [(TB, "garde_17")], "test_garde_17"),
    M("G17-K1-alteree", V65, C65, ('if not _egales(archive, jeu["archive_de_depart"]):', "if False:"), [(TB, "garde_17")], "test_garde_17"),
    M("G17-statut", V65, C65, ('if h.get("statut") != {k: STATUT_K1 for k in ARCHIVE_DE_DEPART}:', "if False:"), [(TB, "garde_17")], "test_garde_17"),
    M("G17-cles", V65, C65, ("if not isinstance(archive, dict) or sorted(archive) != sorted(ARCHIVE_DE_DEPART):", "if not isinstance(archive, dict):"),
      [(TB, "garde_17")], "test_garde_17"),
    M("G19-empreinte", V65, C65, ("if not isinstance(sha_attendue, str) or sha != sha_attendue:", "if False:"), [(TB, "garde_19")], "test_garde_19"),
    M("G19-classe-tout", V65, C65, ("    connues = list(archive.values())\n    if not connues or not isinstance(loi, dict):\n        return None",
                                     "    connues = list(archive.values())\n    return \"copie d'une loi de l'archive\""), [(TB, "garde_19")], "test_garde_19"),
    M("G19-melange-non-fixe", V65, C65, ('if None in sortes or "archive" not in sortes:', 'if "archive" not in sortes:'), [(TB, "garde_19")], "test_garde_19"),
    M("G19-composition", V65, C65, ('if cles and cles <= {"puissance", "inclinaison"}:', "if cles:"), [(TB, "garde_19")], "test_garde_19"),
    M("G19-incomplet", V65, C65, ("if not isinstance(jeu[groupe], dict) or sorted(jeu[groupe]) != sorted(noms):", "if not isinstance(jeu[groupe], dict):"),
      [(TB, "garde_19")], "test_garde_19"),
    M("G18-garde", V65, C66, ('        if d["membres_d_archive"] != attendus or (archive and d["membres_d_archive"] == 0):', "        if False:"),
      [(TB, "garde_18")], "test_artefact_garde_18"),
    M("M3-canal-v64", V65, C66, ("    a_plantees = archive if archive_des_plantees is None else archive_des_plantees",
                                  "    a_plantees = {} if archive_des_plantees is None else archive_des_plantees"),
      [(TB, "JugeV66 and sain")], "test_sain_meme_calcul_que_v64_et_v65"),
    M("M3-hors-famille", V65, C66, ('        promue = bool(ev["promue"]) and log_e >= seuil', '        promue = bool(ev["promue"])'), [(TB, "seuil")],
      "test_seuil_hors_famille"),
    M("G20-bras", V65, C65, ("    if b != BRAS:\n        raise BrasRefuse", "    if False:\n        raise BrasRefuse"), [(TB, "garde_20_et_D2")],
      "test_garde_20_et_D2"),
    M("D2-generations", V65, C66, ('    if plan.get("generations") != GENERATIONS:', "    if False:"), [(TB, "garde_20_et_D2")], "test_garde_20_et_D2"),
    M("G21-ordre", V65, C65, ("ordre = sorted(retenues, key=lambda i: (-float(log_e_g1[i]), i))[:n]",
                              "ordre = sorted(retenues, key=lambda i: (float(log_e_g1[i]), i))[:n]"), [(TB, "copies_des_quatre")],
      "test_sain_copies_des_quatre_premieres_retenues_par_log_e"),
    M("G21-exiger", V65, C65, ('if src not in (heritage.get("retenues") or []) or not _egales(loi, (heritage.get("archive") or {}).get(src)):', "if False:"),
      [(TB, "copie_d_une_carte_non_retenue")], "test_artefact_copie_d_une_carte_non_retenue"),
    M("M4-g2-sans-selection", V65, C66, ("        sha2, _ = jouer_generation(d2, 2, monde, jeu, h2, vue_attendue,",
                                          "        sha2, _ = jouer_generation(d2, 2, monde, jeu, heritage_depart, vue_attendue,"),
      [(TB, "vues_servies_au_releve")], "test_sain_vues_servies_au_releve"),
    M("GO-coeur", V65, C65, ('    if reel and not (isinstance(go, dict) and isinstance(go.get("identifiant"), str) and go.get("plafond_lu_usd")):', "    if False:"),
      [(TB, "test_go")], "test_go"),
    M("PART-avant-appel", V65, C66, ("        exiger_part_avant_appel(compteur, p.relais, p.budget)\n", ""), [(TB, "Depense")],
      "test_artefact_arret_avant_l_appel_sous_la_part"),
    M("L-C5-incomplet", V65, LB, ('    partiel = bool(releve.get("arret")) or not releve.get("complet") or bool(manques)',
                                  '    partiel = bool(releve.get("arret")) or bool(manques)'), [(TL, "C5")], "test_C5_ne_masque_pas_une_breche"),
    M("L-C5-masque-C2", V65, LB, ('        if fausses_promues:\n            aussi.append("C2 (partielle)")', "        pass"), [(TL, "C5")],
      "test_C5_ne_masque_pas_une_breche"),
    M("L-ordre-C4-C2", V65, LB, ('    elif ecarts or copies_promues:\n        code = "C4"\n    elif fausses_promues:\n        code = "C2"',
                                 '    elif fausses_promues:\n        code = "C2"\n    elif ecarts or copies_promues:\n        code = "C4"'),
      [(TL, "prime_sur_C2")], "test_C4_prime_sur_C2"),
    M("L-C3-survit", V65, LB, ('vraies_survivantes = sorted(n for n, p in vraies_g1.items() if p["promue"] and p.get("verdict") == "survit")',
                               'vraies_survivantes = sorted(n for n, p in vraies_g1.items() if p["promue"])'), [(TL, "C3")], "test_C3_sans_dents"),
    M("L-C6-T-MAL", V65, LB, ('and t_mal["gardien"] == "refuse"', "and True"), [(TL, "C6")], "test_C6_instrument"),
    M("L-ordre-C3-C6", V65, LB, ('    elif not vraies_survivantes:\n        code = "C3"\n    elif not p4:\n        code = "C6"',
                                 '    elif not p4:\n        code = "C6"\n    elif not vraies_survivantes:\n        code = "C3"'),
      [(TL, "prime_sur_C6")], "test_C3_prime_sur_C6"),
    M("L-P6-empreinte", V65, LB, ('    if lu_a_part and (not ls.get("attendu") or ls.get("attendu") != ls.get("lu")):', "    if False:"),
      [(TL, "C4_lecture")], "test_C4_lecture_de_selection_et_vue_servie"),
    M("L-P6-membres", V65, LB, ('            if c.get("generation") == 2 and c.get("gardien") == "passe" and c.get("membres_d_archive") != attendus:',
                                "            if False:"), [(TL, "C4_lecture")], "test_C4_lecture_de_selection_et_vue_servie"),
    M("L-copie-promue", V65, LB, ('    elif ecarts or copies_promues:\n        code = "C4"', '    elif ecarts:\n        code = "C4"'), [(TL, "C4_copie")],
      "test_C4_copie_promue"),
    M("L-A1", V65, LB, ('    if lecture["code"] == "C1":  # « trop beau », d\'office', "    if False:"), [(TL, "A1_d_office")], "test_A1_d_office_sous_C1"),
    M("L-A2-diagnostic", V65, LB, ('"diagnostic": "jugée sans archive : défaut de chaîne" if not p.get("membres_d_archive")',
                                   '"diagnostic": "membre du nul promu : défaut numérique" if not p.get("membres_d_archive")'),
      [(TL, "A2_fausse")], "test_A2_fausse_promue"),
    M("L-A2-rejeu", V65, LB, ('    if monde is not None and sortie["audits"]["A2"]:', "    if False:"), [(TL, "A2_rejeu_dans")], "test_A2_rejeu_dans_la_lecture"),
    M("N-parts", V65, DL, ('    if centimes["plafond_kimi_usd"] + centimes["plafond_argon_usd"] != centimes["plafond_modeles_usd"]:', "    if False:"),
      [(TB, "plan_artefacts")], "test_plan_artefacts"),
    M("N-GO-montant", V65, DL, ('    if centimes["plafond_modeles_usd"] + centimes["plafond_machine_usd"] != centimes["go_montant_usd"]:', "    if False:"),
      [(TB, "plan_artefacts")], "test_plan_artefacts"),
    M("N-bras-plan", V65, DL, ('    if lignes["bras"] != "reel_seul":', "    if False:"), [(TB, "plan_artefacts")], "test_plan_artefacts"),
    M("N-commande-v6", V65, DL, ('        if sha256_fichier(p) != e["sha256"]:', "        if False:"), [(TB, "ConfigurationV6 and artefacts")],
      "test_artefacts"),
    M("N-machine-version", V65, DL, ("    if version is None or tuple(version) < BWRAP_MIN:", "    if version is None:"), [(TB, "garde_22_avant")],
      "test_garde_22_avant_la_sonde"),
    M("N-brouillon", V65, DL, ('or not NOM_PREREG.match(base) or "brouillon" in base:', 'or "brouillon_" in base:'), [(TB, "texte_artefacts")],
      "test_texte_artefacts"),
    M("N-bac-factice", V65, DL, ("            parent_bac, fabrique, description_bac = preparer_bac_v66(args.bac, args.utilisateur_bac)",
                                 '            parent_bac, fabrique, description_bac = preparer_bac_v66("factice", args.utilisateur_bac)'),
      [(TB, "bwrap_absent")], "test_artefact_bwrap_absent_refus_code_2_sans_repli_partout"),
    # --- neuves : CLV65-01 (complétude) -------------------------------------------------------------------------------------------
    M("N01a-generations-jouees", V66, LB, ('    if releve.get("generations_jouees") != [1, 2]:', "    if False:"), [(TL, "C5_releve_incomplet")],
      "test_C5_releve_incomplet"),
    M("N01b-etages", V66, LB, ("    if etages != [1, 2]:", "    if False:"), [(TL, "C5_releve_incomplet")], "test_C5_releve_incomplet"),
    M("N01c-plantee-une-fois", V66, LB, ("            if k != 1:", "            if k < 1:"), [(TL, "C5_releve_incomplet")], "test_C5_releve_incomplet"),
    M("N01d-nombre-de-copies", V66, LB, ("    if len(copies) != min(COPIES_MAX, len(retenues_g1)):", "    if False:"), [(TL, "C5_releve_incomplet")],
      "test_C5_releve_incomplet"),
    M("N01e-fausses-jugees", V66, LB, ("        if not _jugee(p):\n            manques.append(f\"{p.get('nom')} (génération",
                                        "        if False:\n            manques.append(f\"{p.get('nom')} (génération"),
      [(TL, "C5_releve_incomplet")], "test_C5_releve_incomplet"),
    M("N01f-log-W-present", V66, LB, ('isinstance(m, int) and not isinstance(m, bool) and p.get("log_richesse_max") is not None',
                                       "isinstance(m, int) and not isinstance(m, bool)"), [(TL, "C5_releve_incomplet")], "test_C5_releve_incomplet"),
    M("N01g-membres-generation-1", V66, LB, ('        if p.get("gardien") == "passe" and p.get("membres_d_archive") != attendus.get(1):', "        if False:"),
      [(TL, "C5_releve_incomplet")], "test_C5_releve_incomplet"),
    M("N01h-plantees-en-trop", V66, LB, ("    if en_trop:", "    if False:"), [(TL, "C5_releve_incomplet")], "test_C5_releve_incomplet"),
    M("N01i-vue-consignee", V66, LB, ('        if not isinstance((releve.get("vues_servies") or {}).get(g), dict):', "        if False:"),
      [(TL, "C5_releve_incomplet")], "test_C5_releve_incomplet"),
    M("N01j-selection-finale-relue", V66, LB, ('    if not isinstance(fin, dict) or fin.get("refus") is not None or fin.get("retenues") is None:', "    if False:"),
      [(TL, "C5_releve_incomplet")], "test_C5_releve_incomplet"),
    M("N01k-A1-log-W-absent", V66, LB, ('p.get("log_richesse_max") is not None and p["log_richesse_max"] <= MARGE_LOG_W for p in fausses)',
                                         '(p.get("log_richesse_max") is None or p["log_richesse_max"] <= MARGE_LOG_W) for p in fausses)'),
      [(TL, "A1_artefacts")], "test_A1_artefacts"),
    M("N01l-copie-source-retenue", V66, LB, ("        if c.get(\"source\") not in retenues_g1:\n            manques.append(f\"copie",
                                              "        if False:\n            manques.append(f\"copie"), [(TL, "C5_releve_incomplet")],
      "test_C5_releve_incomplet"),
    # --- CLV65-02 ---------------------------------------------------------------------------------------------------------------
    M("N02a-jugements-apres-l-etage", V66, C66,
      [('        releve["plantees"].append(e)\n        entrees_p[i] = e\n', "        entrees_p[i] = e\n"),
       ("    verdicts_p = T._verdicts(resume_p)\n", '    verdicts_p = T._verdicts(resume_p)\n    releve["plantees"].extend(entrees_p.values())\n')],
      [(TB, "arret_pendant_l_etage")], "test_artefact_arret_pendant_l_etage_jugements_presents"),
    M("N02b-refus-heritage-consigne", V66, C66, ('"refus": {"type": type(e).__name__, "motif": str(e)[:500]}, "vue": None,', '"refus": None, "vue": None,'),
      [(TB, "heritage_altere_C4")], "test_artefact_heritage_altere_C4_partielle"),
    M("N02c-empreinte-sur-disque", V66, C66, ('            releve["lecture_selection"] = {"attendu": sha1, "lu": empreinte_sur_disque(os.path.join(d1, bf.NOM_BILAN)),',
                                               '            releve["lecture_selection"] = {"attendu": sha1, "lu": sha1,'),
      [(TB, "empreinte_lue_differente")], "test_artefact_empreinte_lue_differente_de_l_ecrite"),
    M("N02d-refus-finale-consigne", V66, C66, ('"refus": {"type": type(e).__name__, "motif": str(e)[:500]}, "retenues": None}', '"refus": None, "retenues": None}'),
      [(TB, "relecture_finale_refusee")], "test_artefact_relecture_finale_refusee"),
    M("N02e-lecture-refus-heritage", V66, LB, ('    if ls.get("refus"):\n        ecarts.append(', "    if False:\n        ecarts.append("),
      [(TL, "heritage_refuse_sous_C5")], "test_C4_heritage_refuse_sous_C5"),
    M("N02f-lecture-refus-finale", V66, LB, ('    if isinstance(fin, dict) and fin.get("refus"):', "    if False:"),
      [(TB, "relecture_finale_refusee")], "test_artefact_relecture_finale_refusee"),
    M("N02g-lecture-incidents", V66, LB, ("    for i in incidents:\n        ecarts.append(", "    for i in []:\n        ecarts.append("),
      [(TL, "C4_lecture")], "test_C4_lecture_de_selection_et_vue_servie"),
    # --- CLV65-03 (garde 23) ----------------------------------------------------------------------------------------------------
    M("N03a-garde-23-identifiants", V66, C66, ("    if len(ids) != len(servis) or ids != sorted(ids_attendus):", "    if False:"),
      [(TB, "heritage_d_un_autre_contenu")], "test_artefact_heritage_d_un_autre_contenu"),
    M("N03b-garde-23-lois", V66, C66, ('        if not _egales(x.get("loi"), (archive or {}).get(x["identifiant"])):', "        if False:"),
      [(TB, "garde_23_avant")], "test_artefacts_garde_23_avant_l_appel"),
    M("N03c-garde-23-texte-recu", V66, C66, ("    if recu != sha_attendue:", "    if False:"), [(TB, "ne_sert_que_K1")],
      "test_artefact_la_generation_2_ne_sert_que_K1"),
    M("N03d-garde-23-appel-apres", V66, C66, ('"texte_recu_sha256": exiger_texte_recu(p, avant, sha_texte)})', '"texte_recu_sha256": sha_texte})'),
      [(TB, "ne_sert_que_K1")], "test_artefact_la_generation_2_ne_sert_que_K1"),
    M("N03e-garde-23-appel-avant", V66, C66, ("        servie = exiger_vue_servie(contexte, ids_attendus, archive, ids_plantees)",
                                               '        servie = {"identifiants": sorted(ids_attendus), "lois_sha256": "", "contexte_sha256": ""}'),
      [(TB, "heritage_d_un_autre_contenu")], "test_artefact_heritage_d_un_autre_contenu"),
    M("N03f-lecture-vue-g2", V66, LB, ('    if isinstance(v2, dict) and sorted(v2.get("identifiants") or []) != attendue:', "    if False:"),
      [(TL, "C4_lecture")], "test_C4_lecture_de_selection_et_vue_servie"),
    M("N03g-lecture-vue-g1", V66, LB, ('    v1 = vues.get("1")\n    if isinstance(v1, dict) and v1.get("identifiants") != list(ARCHIVE_DE_DEPART):\n        ecarts.append(',
                                        '    v1 = vues.get("1")\n    if False:\n        ecarts.append('),
      [(TL, "C4_lecture")], "test_C4_lecture_de_selection_et_vue_servie"),
    M("N03h-lecture-archive-g2", V66, LB, ("    if a2 is not None and sorted(a2) != attendue:", "    if False:"), [(TL, "C4_lecture")],
      "test_C4_lecture_de_selection_et_vue_servie"),
    M("N03i-lecture-plantee-retenue", V66, LB, ("        if set(ret or []) & plantes:", "        if False:"), [(TL, "C4_lecture")],
      "test_C4_lecture_de_selection_et_vue_servie"),
    # --- CLV65-05 (garde 7, « ni servies ») -------------------------------------------------------------------------------------
    M("N05a-garde-7-heritage-lu", V66, C66, ("            T.exiger_sans_temoin(h2, ids_plantees)  # garde 7", "            pass  # garde 7"),
      [(TB, "dans_l_heritage_lu")], "test_artefact_loi_plantee_dans_l_heritage_lu"),
    M("N05b-garde-7-relecture-finale", V66, C66, ("            T.exiger_sans_temoin(fin, ids_plantees)  # garde 7", "            pass  # garde 7"),
      [(TB, "a_la_relecture_finale")], "test_artefact_loi_plantee_a_la_relecture_finale"),
    M("N05c-ids-de-la-generation-2", V66, C66, ("        ids_plantees |= _ids_plantees(releve)\n", ""), [(TB, "a_la_relecture_finale")],
      "test_artefact_loi_plantee_a_la_relecture_finale"),
    M("N05d-garde-23-plantee-servie", V66, C66, ("    plantes = sorted(set(ids) & set(ids_plantees))", "    plantes = []"),
      [(TB, "garde_23_avant")], "test_artefacts_garde_23_avant_l_appel"),
    # --- CLV65-06 ---------------------------------------------------------------------------------------------------------------
    M("N06-which-du-module", V66, DL, ("    which = which or WHICH\n", "    which = which or shutil.which\n"), [(TB, "bwrap_absent")],
      "test_artefact_bwrap_absent_refus_code_2_sans_repli_partout"),
    # --- CLV65-07 (registre des GO) ---------------------------------------------------------------------------------------------
    M("N07a-extension-perimetre", V66, RG, ('            if not (perimetre.lower().startswith("extension") and typ', "            if not (True and typ"),
      [(TR, "cas_artefacts")], "test_cas_artefacts_et_sains"),
    M("N07b-extension-anterieure", V66, RG, ('and accorde_d >= premier["accorde"] and echeance_ok):', "and echeance_ok):"),
      [(TR, "cas_artefacts")], "test_cas_artefacts_et_sains"),
    M("N07c-extension-echeance", V66, RG, ('                               and echeance_d <= premier["echeance"]))', "                               ))"),
      [(TR, "cas_artefacts")], "test_cas_artefacts_et_sains"),
    M("N07d-extension-type", V66, RG, ('typ == premier["type"] and par == "Lazar"', 'True and par == "Lazar"'), [(TR, "cas_artefacts")],
      "test_cas_artefacts_et_sains"),
    M("N07e-extension-Lazar", V66, RG, ('typ == premier["type"] and par == "Lazar"', 'typ == premier["type"]'), [(TR, "cas_artefacts")],
      "test_cas_artefacts_et_sains"),
    M("N07f-GO-a-extension", V66, RG, ('    if g["extensions"]:', "    if False:"), [(TR, "artefacts_ligne")], "test_artefacts_ligne"),
    M("N07g-enveloppe-somme", V66, RG, ("    if round(sum(parts.values()) * 100) != round(total * 100):", "    if False:"),
      [(TR, "artefacts_enveloppe")], "test_artefacts_enveloppe"),
    M("N07h-enveloppe-nombre-etranger", V66, RG, ("    if len(NOMBRE.findall(dedans)) != len(parts) or not parts:", "    if not parts:"),
      [(TR, "artefacts_enveloppe")], "test_artefacts_enveloppe"),
    M("N07i-montant-exact", V66, RG, ("    if abs(valeur - requis) > 1e-9:", "    if False:"), [(TR, "artefacts_montant")], "test_artefacts_montant"),
    M("N07j-lanceur-lecteur-v66", V66, DL, ("                go = R.verifier_go_v66(args.go, args.registre_go, p[\"go_montant_usd\"], part=PART_DU_GO)",
                                             "                go = cfg.verifier_go_v56(args.go, args.registre_go, p[\"go_montant_usd\"])"),
      [(TB, "refus_nommes")], "test_refus_nommes"),
    M("N07k-part-organisme", V66, DL, ('PART_DU_GO = R.PART_PAR_DEFAUT', 'PART_DU_GO = "bailey"'), [(TB, "go_enveloppe")],
      "test_go_enveloppe_lu_par_le_lanceur"),
    M("N07l-part-demandee", V66, RG, ('    if cle not in parts:', "    if False:"), [(TR, "artefacts_enveloppe")], "test_artefacts_enveloppe"),
    # --- CLV65-08 (mesures) -----------------------------------------------------------------------------------------------------
    M("N08a-membre-dominant", V66, C66, ('                                        membre_dominant_final=ev.get("membre_dominant_final"))\n    mult',
                                          "                                        membre_dominant_final=None)\n    mult"),
      [(TB, "JugeV66 and sain")], "test_sain_meme_calcul_que_v64_et_v65"),
    M("N08b-recherche-hors-loi-gelee", V66, C66, ('        m["touches_hors_loi_gelee"] += T.chercher_loi_plantee(self._monde, hors, {}, ou)',
                                                   '        m["touches_hors_loi_gelee"] += T.chercher_loi_plantee(self._monde, "", {}, ou)'),
      [(TB, "etage_mesure")], "test_etage_mesure_artefact"),
    M("N08c-echo-de-la-loi", V66, C66, ("    for seg in sorted(set(dans), key=len, reverse=True):", "    for seg in []:"),
      [(TB, "consigne_sans_loi")], "test_consigne_sans_loi_gelee"),
    M("N08d-etage-mesure-branche", V66, C66, ('    etage = EtageMesure(adaptateur_etage, monde, recherche["etage"])', "    etage = adaptateur_etage"),
      [(TB, "mesures_au_releve")], "test_sain_mesures_au_releve"),
    M("N08e-wilson-au-releve", V66, LB, ('        f["wilson_95"] = {f"{a}/{b}": wilson(f[a], f[b]) for a, b in PARTS_WILSON}', '        f["wilson_95"] = {}'),
      [(TL, "fausse_decouverte_en_tete")], "test_oracle_mesures_wilson"),
    M("N08f-wilson-formule", V66, LB, ("    demi = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d", "    demi = z * math.sqrt(p * (1 - p) / n) / d"),
      [(TL, "wilson")], "test_wilson"),
    M("N08g-jetons-usage", V66, C66, ('            if isinstance(objet, dict) and isinstance(objet.get("usage"), dict):', "            if False:"),
      [(TB, "jetons")], "test_jetons"),
    M("N08h-lignes-de-tranche", V66, C66, ("    servis = {(round(z0, DECIMALES_TRANCHE), round(z1, DECIMALES_TRANCHE), g) for z0, z1, g in episodes_servis}",
                                            "    servis = set()"), [(TB, "lignes_de_tranche")], "test_lignes_de_tranche_artefact"),
    M("N08i-jetons-branches", V66, DL, ("                jetons.instrumenter(p_.ad, p_.relais)\n", "                pass\n"),
      [(TB, "verifier_seulement")], "test_verifier_seulement_roles_en_dernier_jetons_branches"),
    # --- CLV65-09 (garde 22) ----------------------------------------------------------------------------------------------------
    M("N09a-superutilisateur", V66, DL, ("    if euid != 0:", "    if False:"), [(TB, "garde_22_avant")], "test_garde_22_avant_la_sonde"),
    M("N09b-euid-du-processus", V66, DL, ("        exiger_machine(args.utilisateur_bac, version_bwrap(), os.geteuid())",
                                           "        exiger_machine(args.utilisateur_bac, version_bwrap(), 0)"),
      [(TB, "garde_22_cablee")], "test_garde_22_cablee"),
    M("N09c-identite-du-bac", V66, DL, ('    if utilisateur_bac is None or ident.get("uid") != int(utilisateur_bac):', "    if utilisateur_bac is None:"),
      [(TB, "garde_22_apres")], "test_garde_22_apres_la_sonde"),
    M("N09d-identite-cablee", V66, DL, ("            exiger_utilisateur_du_bac(description_bac, args.utilisateur_bac)\n            environnement",
                                         "            environnement"), [(TB, "garde_22_cablee")], "test_garde_22_cablee"),
    M("N09e-vrai-bac-sonde", V66, DL, ('    if d.get("factice") is not False or d.get("demande") != "reel" or not d.get("sonde"):', "    if False:"),
      [(TB, "garde_22_apres")], "test_garde_22_apres_la_sonde"),
    M("N09f-portes-avant-la-garde-22", V66, DL,
      [("            exiger_machine(args.utilisateur_bac, version_bwrap(), os.geteuid())  # garde 22, avant toute porte\n", ""),
       ("                                                                   transmettre=not args.verifier_seulement)  # portes : en dernier\n",
        "                                                                   transmettre=not args.verifier_seulement)  # portes : en dernier\n"
        "            exiger_machine(args.utilisateur_bac, version_bwrap(), os.geteuid())\n")],
      [(TB, "garde_22_cablee")], "test_garde_22_cablee"),
    # --- CLV65-10 (configuration) -----------------------------------------------------------------------------------------------
    M("N10a-chemin-absolu", V66, DL, ("or not chemin or os.path.isabs(chemin) or", "or not chemin or"), [(TB, "ConfigurationV6 and artefacts")],
      "test_artefacts"),
    M("N10b-chemin-point-point", V66, DL, (' or ".." in chemin.replace("\\\\", "/").split("/"):', ":"), [(TB, "ConfigurationV6 and artefacts")],
      "test_artefacts"),
    M("N10c-sous-le-dossier", V66, DL, ("    if os.path.commonpath([racine, p]) != racine or not os.path.isfile(p):", "    if not os.path.isfile(p):"),
      [(TB, "ConfigurationV6 and artefacts")], "test_artefacts"),
    M("N10d-pieces-relatives", V66, DL, ('    for nom, piece in sorted((conf.get("pieces") or {}).items()):', "    for nom, piece in []:"),
      [(TB, "ConfigurationV6 and artefacts")], "test_artefacts"),
    M("N10e-commande-resolue", V66, DL, ('        copie["fournisseurs"][n]["commande"] = [resolues[n] if x == cmds[n]["chemin"] else x for x in c]', "        pass"),
      [(TB, "ConfigurationV6 and sain")], "test_sain_dossier_complet"),
    M("N10f-cles-de-la-section", V66, DL, ("    if not isinstance(s, dict) or set(s) != CLES_SECTION:", "    if not isinstance(s, dict):"),
      [(TB, "ConfigurationV6 and artefacts")], "test_artefacts"),
    M("N10g-plafonds-et-parts", V66, DL, ("    if not egaux:", "    if False:"), [(TB, "ConfigurationV6 and artefacts")], "test_artefacts"),
    M("N10h-budget", V66, DL, ('    if float(((conf.get("budget") or {}).get("plafond_usd")) or 0) != plan["plafond_modeles_usd"]:', "    if False:"),
      [(TB, "ConfigurationV6 and artefacts")], "test_artefacts"),
    M("N10i-commande-lancee", V66, DL, ('        if c.count(cmds[n]["chemin"]) != 1:', "        if False:"), [(TB, "ConfigurationV6 and artefacts")],
      "test_artefacts"),
]

FAILED = re.compile(r"^(?:FAILED|ERROR|SUBFAILED)\S*.*?(\S+\.py::\S+)", re.M)  # échecs, erreurs, sous-essais en échec


def _pytest(dossier, fichier, k, collecte=False):
    """pytest sur une sélection, dossiers provisoires (TMPDIR et --basetemp) **dans** le dossier de la copie, retiré avec elle."""
    tmp = tempfile.mkdtemp(prefix="tmp-", dir=os.path.dirname(dossier))
    env = dict(os.environ, POLE_ESSAI_BAC_REEL_NON_JOUE="1", PYTHONDONTWRITEBYTECODE="1", TMPDIR=tmp)
    cmd = [sys.executable, "-I", "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", fichier, "-k", k]
    cmd += ["--collect-only"] if collecte else ["-rfE", "--basetemp", os.path.join(tmp, "pt")]
    try:
        return subprocess.run(cmd, cwd=dossier, capture_output=True, text=True, timeout=1800, env=env)
    finally:
        shutil.rmtree(tmp, True)


def essayer(dossier, essais):
    """(code, dernière ligne, essais en échec) : code 0 tout passe, 1 au moins un échec, autre : défaut (usage, rien collecté)."""
    echecs, derniere, pire = [], "", 0
    for fichier, k in essais:
        r = _pytest(dossier, fichier, k)
        derniere = (r.stdout.strip().splitlines() or [""])[-1]
        echecs += FAILED.findall(r.stdout)
        if r.returncode not in (0, 1):
            return r.returncode, derniere, echecs
        pire = max(pire, r.returncode)
    return pire, derniere, echecs


def copier():
    d = tempfile.mkdtemp(prefix="mutation-v66-")
    shutil.copytree(RACINE, os.path.join(d, "orchestrator"), ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    return d, os.path.join(d, "orchestrator")


def appliquer(o, m):
    """Applique les remplacements de la mutation dans la copie `o` ; rend None ou le motif d'un défaut du banc."""
    chemin = os.path.join(o, m["fichier"])
    with open(chemin, encoding="utf-8") as f:
        s = f.read()
    for avant, apres in m["paires"]:
        if s.count(avant) != 1:
            return f"texte d'origine trouvé {s.count(avant)} fois : {avant[:80]!r}"
        s = s.replace(avant, apres)
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(s)
    return None


def une(m):
    d, o = copier()
    try:
        defaut = appliquer(o, m)
        base = {"mutation": m["id"], "origine": m["origine"], "fichier": m["fichier"], "raison_attendue": m["raison"], "essais": m["essais"]}
        if defaut:
            return dict(base, issue="défaut du banc", motif=defaut)
        code, derniere, echecs = essayer(o, m["essais"])
        if code == 0:
            issue = "survit"
        elif code != 1:
            issue = "défaut du banc"
        elif any(m["raison"] in e for e in echecs):
            issue = "tuée"
        else:
            issue = "tuée pour une autre raison"
        return dict(base, issue=issue, echecs=echecs, derniere_ligne=derniere, code=code)
    finally:
        shutil.rmtree(d, True)


def principal(argv=None):
    a = argparse.ArgumentParser()
    a.add_argument("--processus", type=int, default=4)
    a.add_argument("--sortie")
    a.add_argument("--seulement")
    a.add_argument("--verifier-textes", action="store_true")
    x = a.parse_args(argv)
    debut = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    ids = [m["id"] for m in MUTATIONS]
    if len(set(ids)) != len(ids):
        print("défaut du banc : identifiants de mutation en double")
        return 2
    choisies = [m for m in MUTATIONS if not x.seulement or m["id"] in x.seulement.split(",")]
    d, o = copier()
    try:
        for m in choisies:  # chaque texte d'origine présent une seule fois, avant tout essai
            with open(os.path.join(o, m["fichier"]), encoding="utf-8") as f:
                s = f.read()
            for avant, _ in m["paires"]:
                if s.count(avant) != 1:
                    print(f"défaut du banc : {m['id']} : texte d'origine trouvé {s.count(avant)} fois")
                    return 2
        if x.verifier_textes:
            print(f"{len(choisies)} mutations : textes d'origine présents une fois chacun")
            return 0
        selections = sorted({e for m in choisies for e in m["essais"]})

        def saine(e):  # essais sains : chaque sélection passe, avec au moins un essai passé ; essais collectés
            r = _pytest(o, *e)
            return e, r.returncode, (r.stdout.strip().splitlines() or [""])[-1], _pytest(o, *e, collecte=True).stdout
        with ThreadPoolExecutor(max_workers=x.processus) as ex:
            saines = list(ex.map(saine, selections))
        collectes = {}
        for (fichier, k), code, derniere, collecte in saines:
            if code != 0 or " passed" not in derniere:
                print(f"essais sains en échec ou rien de passé sur la copie non mutée : {fichier} -k {k!r} : {derniere}")
                return 2
            collectes[(fichier, k)] = collecte
        for m in choisies:
            if not any(m["raison"] in collectes[e] for e in m["essais"]):
                print(f"défaut du banc : {m['id']} : raison attendue {m['raison']!r} absente des essais collectés")
                return 2
    finally:
        shutil.rmtree(d, True)
    with ThreadPoolExecutor(max_workers=x.processus) as ex:
        res = list(ex.map(une, choisies))
    for r in res:
        print(f"{r['mutation']:38s} {r['issue']:28s} {r.get('derniere_ligne') or r.get('motif')}")
    tuees = sum(r["issue"] == "tuée" for r in res)
    par = {}
    for r in res:
        par.setdefault(r["origine"], [0, 0])
        par[r["origine"]][0] += r["issue"] == "tuée"
        par[r["origine"]][1] += 1
    print("par origine : " + " ; ".join(f"{k} {v[0]}/{v[1]}" for k, v in sorted(par.items())))
    print(f"{tuees} tuées pour la raison attendue sur {len(res)} mutations")
    if x.sortie:
        with open(x.sortie, "w", encoding="utf-8") as f:
            json.dump({"debut_utc": debut, "fin_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                       "resultats": res, "tuees": tuees, "n": len(res), "par_origine": par}, f, ensure_ascii=False, indent=1)
    return 0 if tuees == len(res) else 1


if __name__ == "__main__":
    sys.exit(principal())
