"""Banc de mutations du code v67 (écart 1, option 2) : le banc v66 entier porté (ses 133 mutations, essais du lanceur et du cœur
rejoués par `essais/test_boucle_reelle_v67.py`, qui rejoue la suite v66 contre le lanceur v67 ; les mutations du lanceur v66
appliquées à sa copie v67), et les mutations neuves des changements v67 (garde 24, délai passé à l'adaptateur, rôles réels v67,
blocs v67, manifeste).

Même machinerie que le banc v66 (`essais/mutations_boucle_reelle_v66.py`, chargé tel quel : copie neuve de `orchestrator/`,
remplacements textuels présents une seule fois, essais sains d'abord, issue « tuée » seulement pour la raison attendue) ; seule la
liste `MUTATIONS` est remplacée.

  POLE_ESSAI_BAC_REEL_NON_JOUE=1 python3 -I -B essais/mutations_boucle_reelle_v67.py [--processus 4] [--sortie RESULTAT.json]
      [--seulement ID,ID] [--verifier-textes]
Codes : ceux du banc v66 (0 toutes tuées pour la raison attendue ; 1 au moins une autre issue ; 2 défaut du banc).
"""

import importlib.util
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("mutations_boucle_reelle_v66_pour_v67", os.path.join(ICI, "mutations_boucle_reelle_v66.py"))
BANC = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(BANC)
M = BANC.M

DL66, DL67, AC67 = "demonstrations/boucle_reelle_v66.py", "demonstrations/boucle_reelle_v67.py", "pole/adaptateur_commande_v67.py"
TB66, TB67 = "essais/test_boucle_reelle_v66.py", "essais/test_boucle_reelle_v67.py"
NV = "neuve v67"


def porter(m):
    """Une mutation du banc v66 portée : le lanceur v66 devient sa copie v67 ; les essais du lanceur et du cœur sont ceux du
    fichier v67 (même sélection -k, mêmes noms d'essais)."""
    return dict(m, id="P-" + m["id"], origine="banc v66 porté (" + m["origine"] + ")",
                fichier=DL67 if m["fichier"] == DL66 else m["fichier"],
                essais=[(TB67 if f == TB66 else f, k) for f, k in m["essais"]])


NEUVES = [
    M("N01-garde-24-non-jouee-dans-commandes", NV, AC67, ("    verifier_delais_v67(conf, noms)\n    adaptateurs, portes", "    adaptateurs, portes"),
      [(TB67, "garde_24_avant_tout_remplacement")], "test_artefact_garde_24_avant_tout_remplacement"),
    M("N02-delai-non-passe", NV, AC67, ('delai_s=float(f["delai_s"]), exiger_modele_servi=True', "exiger_modele_servi=True"),
      [(TB67, "CommandesV67")], "test_sain_delai_de_la_configuration"),
    M("N03-plafond-de-7200-s", NV, AC67, ("if adaptateur is None or adaptateur > DELAI_MAX_S:", "if adaptateur is None:"),
      [(TB67, "Garde24")], "test_artefacts"),
    M("N04-marge-de-30-s", NV, AC67, ("if commande > adaptateur - MARGE_MIN_S:", "if commande > adaptateur:"),
      [(TB67, "Garde24")], "test_artefacts"),
    M("N05-marge-bornes-exactes", NV, AC67, ("if commande > adaptateur - MARGE_MIN_S:", "if commande >= adaptateur - MARGE_MIN_S:"),
      [(TB67, "Garde24")], "test_sain_bornes_exactes"),
    M("N06-option-en-double", NV, AC67, ("c.count(OPTION_DELAI) != 1", "c.count(OPTION_DELAI) < 1"), [(TB67, "Garde24")], "test_artefacts"),
    M("N07-autre-type-non-ignore-dans-la-garde", NV, AC67,
      ('            continue\n        adaptateur = _reel_positif(f.get("delai_s"))', '            pass\n        adaptateur = _reel_positif(f.get("delai_s"))'),
      [(TB67, "Garde24")], "test_sain_entree_d_un_autre_type_ignoree"),
    M("N08-valeur-de-commande-non-chaine-admise", NV, AC67, ("        if isinstance(brut, str):\n            try:\n                commande = _reel_positif(float(brut))",
                                                             "        if True:\n            try:\n                commande = _reel_positif(float(brut))"),
      [(TB67, "Garde24")], "test_artefacts"),
    M("N09-roles-par-commandes-v64", NV, DL67, ("AC67.commandes_v67(conf2, adaptateurs, portes)", "L64.AC.commandes_v64(conf2, adaptateurs, portes)"),
      [(TB67, "RolesReelsV67")], "test_sain_delais_aux_adaptateurs_aucune_porte"),
    M("N10-lanceur-par-roles-reels-v64", NV, DL67, ("= roles_reels_v67(conf_resolue,", "= L64.roles_reels(conf_resolue,"),
      [(TB67, "BrancheReelle and verifier_seulement_roles")], "test_verifier_seulement_roles_en_dernier_jetons_branches"),
    M("N11-lanceur-sans-garde-24", NV, DL67, ("            section, conf_resolue, delais = verifier_configuration_v67(conf, p, dossier_conf)",
                                              "            (section, conf_resolue), delais = verifier_configuration_v66(conf, p, dossier_conf), {}"),
      [(TB67, "BrancheReelleGarde24")], "test_artefact_garde_24_code_2"),
    M("N12-verifier-configuration-v67-sans-garde-24", NV, DL67, ("        delais = AC67.verifier_delais_v67(conf)\n", "        delais = {}\n"),
      [(TB67, "ConfigurationEtGarde24AuLanceur")], "test_artefact_garde_24"),
    M("N13-fermeture-sans-adaptateur-v67", NV, DL67, ('"demonstrations/lire_boucle_reelle_v66.py", "pole/adaptateur_commande_v67.py",',
                                                      '"demonstrations/lire_boucle_reelle_v66.py",'),
      [(TB67, "Fermeture")], "test_bloc_gele_egal_a_la_fermeture_statique"),
    M("N14-bloc-plan-v66", NV, DL67, ('DEBUT_PLAN, FIN_PLAN = "<!-- plan-gele-v67 : début -->", "<!-- plan-gele-v67 : fin -->"',
                                      'DEBUT_PLAN, FIN_PLAN = "<!-- plan-gele-v66 : début -->", "<!-- plan-gele-v66 : fin -->"'),
      [(TB67, "BlocsNonInterchangeables")], "test_plan_v66_dans_un_texte_v67_refuse"),
    M("N15-bloc-empreintes-v66", NV, DL67, ('DEBUT_EMPREINTES, FIN_EMPREINTES = "<!-- empreintes-du-code-v67 : début -->", "<!-- empreintes-du-code-v67 : fin -->"',
                                            'DEBUT_EMPREINTES, FIN_EMPREINTES = "<!-- empreintes-du-code-v66 : début -->", "<!-- empreintes-du-code-v66 : fin -->"'),
      [(TB67, "BlocsNonInterchangeables")], "test_texte_v66_refuse_par_v67"),
    M("N16-delais-hors-du-manifeste", NV, DL67, ("boucle_reelle_v66=section, delais_v67=delais, bac=", "boucle_reelle_v66=section, bac="),
      [(TB67, "BrancheReelleGarde24")], "test_sain_verifier_seulement_delais_au_manifeste"),
    M("N17-refus-de-la-garde-24-non-nomme-dans-les-roles", NV, DL67, ("    except (L64.AC.RelaisNonCommande, AC67.DelaiRefuse) as x:",
                                                                     "    except L64.AC.RelaisNonCommande as x:"),
      [(TB67, "RolesReelsV67")], "test_artefact_garde_24_dans_les_roles"),
    M("N18-lanceur-hors-du-manifeste", NV, DL67, ('"version": B.VERSION, "lanceur": LANCEUR, ', '"version": B.VERSION, '),
      [(TB67, "ManifesteV67")], "test_lanceur_au_manifeste"),
]

BANC.MUTATIONS = [porter(m) for m in BANC.MUTATIONS] + NEUVES


if __name__ == "__main__":
    sys.exit(BANC.principal())
