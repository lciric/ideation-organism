"""Mutations en mémoire des gardes nouvelles de la v54 (R5 : chaque garde neutralisée doit faire échouer son essai).

Aucun fichier n'est modifié : pour chaque mutation, le source de **la** fonction visée est lu (`inspect.getsource`), un
fragment exact y est remplacé (le fragment doit exister une fois : sinon la mutation est déclarée « non appliquée », jamais
ignorée), la fonction est recompilée dans l'espace de noms de son module, puis substituée partout où l'objet d'origine est
référencé (attribut de classe, attribut des modules `pole.*` et `essais.*`). Les essais visés sont joués ; la fonction
d'origine est remise en place. Une mutation « tuée » = au moins un essai visé en échec ou en erreur.

  python3 -B essais/mutations_v54.py        (depuis le dossier de livraison ; sortie : une ligne par mutation)
"""

import inspect
import io
import os
import sys
import tempfile
import textwrap
import unittest

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path[:0] = [RACINE, ICI]
sys.dont_write_bytecode = True

import aides  # noqa: E402

aides.BASE = tempfile.mkdtemp(prefix="pole-mutations-v54-")
import essais.aides as _ea  # noqa: E402

_ea.BASE = aides.BASE

from pole import bisociateur_v54, budget_v54, configuration_v54, course2_v54, etage_entre_generations_v54, fiches_v54  # noqa: E402,F401
from pole import gardes_e0_v54, mesures_v54, noyau_v54, prepilote_v54, suivi_roles_v54  # noqa: E402,F401

C = "essais.test_v54_corrections."
X = "essais.test_v54_annexe."
P = "essais.test_v54_prepilote."

MUTATIONS = [
    ("CL18-01 consommation d'un juge omise", noyau_v54.Orchestre, "appel",
     "self.coffre.noter_consommation(etat[\"etape\"], role, cout,", "None if role.startswith('juge-') else self.coffre.noter_consommation(etat[\"etape\"], role, cout,",
     [C + "TestCL18_01JournalComplet"]),
    ("CL18-01 coût perdu sur exception (pas de pire cas)", noyau_v54.Orchestre, "appel", "cout = plafond if cout is None else cout",
     "cout = 0.0 if cout is None else cout", [C + "TestCL18_01JournalComplet"]),
    ("CL18-02 coupure ignorée par le budget", budget_v54.BudgetV54, "apres_etape", "if coupee or coupee_cout:", "if coupee_cout and not coupee:",
     [C + "TestCL18_02CoupureEtNoeud", C + "TestCL18_01JournalComplet"]),
    ("CL18-02 marque de coupure non posée", noyau_v54.Orchestre, "appel", "etat[\"coupee\"] = True", "pass",
     [C + "TestCL18_02CoupureEtNoeud", C + "TestCL18_01JournalComplet"]),
    ("CL18-02 nœud ignoré (course enchaîne)", noyau_v54.Orchestre, "c13_ou_noeud", "if e[\"c13_satisfaite\"]:", "if True:",
     [C + "TestCL18_02CoupureEtNoeud"]),
    ("CL18-03 égalité → « au moins »", configuration_v54, "verifier_go_v54", "if abs(valeur - float(montant_requis_usd)) > 1e-9:",
     "if valeur + 1e-9 < float(montant_requis_usd):", [C + "TestCL18_03LigneDeGo", P + "TestLanceurV6"]),
    ("CL18-03 plusieurs montants acceptés", configuration_v54, "verifier_go_v54", "if len(distincts) != 1:", "if False:",
     [C + "TestCL18_03LigneDeGo"]),
    ("CL18-03 « par lancement » accepté", configuration_v54, "verifier_go_v54", "if re.search(r\"par\\s+(lancement", "if False and re.search(r\"par\\s+(lancement",
     [C + "TestCL18_03LigneDeGo"]),
    ("CL18-03 portée ignorée (toujours N × S17)", configuration_v54, "montant_requis", "if portee == \"course\":", "if False:",
     [C + "TestCL18_03LigneDeGo"]),
    ("CL18-05 passeport sans recalcul", noyau_v54.AiguilleurV54, "a_passeport", " and e == fv.empreinte_contenu(fiche)", "",
     [C + "TestCL18_05Passeport"]),
    ("CL18-06 préfixe → mot entier", fiches_v54, "motif", "return re.compile(r\"(?<![0-9a-z])\" + re.escape(n))\n",
     "return re.compile(r\"(?<![0-9a-z])\" + re.escape(n) + r\"(?![0-9a-z])\")\n", [C + "TestCL18_06A4", P + "TestGardesE0"]),
    ("CL18-06 fiche exclue → toujours arrêt", noyau_v54.Orchestre, "servir", "if dans_fiche and self.a4_action == \"fiche_exclue\":", "if False:",
     [C + "TestCL18_06A4"]),
    ("CL18-08 entrée du bisociateur non filtrée", course2_v54.GenerationV54, "_entree_bisociateur", "(\"*\" in four or", "(True or",
     [C + "TestCL18_08Lectures"]),
    ("CL18-08 passe « tableau » toujours jugée", course2_v54.GenerationV54, "etape_passe_tableau", "if t[\"juger_passe_tableau\"]:", "if True:",
     [C + "TestCL18_08Lectures"]),
    ("CL18-10 refus technique compté au débordement", noyau_v54.GardeKimiV54, "noter", "if refus and self.mode == \"technique\":", "if False:",
     [C + "TestCL18_10GardeKimi"]),
    ("CL18-10 metteur toujours arrêté", course2_v54.GenerationV54, "_aiguiller", "if self.conf[\"garde_kimi\"][\"arret_metteur_fusion\"] and",
     "if", [C + "TestCL18_10GardeKimi"]),
    ("CL18-12 sessions non opaques", noyau_v54.Orchestre, "session", "d = os.path.join(self.sortie, \"sessions\", opaque)",
     "d = os.path.join(self.sortie, \"sessions\", *[str(x) for x in logique])", [C + "TestCL18_12Fuites"]),
    ("CL18-12 A4 sur l'entrée complète retirée", fiches_v54, "entree_une_fiche", "    garde(entree, etiquettes_interdites, mode, \"l'entrée complète (consigne figée comprise)\")\n", "",
     [C + "TestCL18_12Fuites"]),
    ("CL18-13 morceaux de nom de clé ignorés", etage_entre_generations_v54, "nom_de_cle", "or any(m in n for m in MORCEAUX_DE_CLE) or n.endswith(\"_KEY\")", "",
     [C + "TestCL18_13MachineJetable"]),
    ("CL18-14 kappa 1 sur marges constantes", mesures_v54, "kappa_cohen_v54", "return None if abs(1 - pe) < 1e-12 else", "return 1.0 if abs(1 - pe) < 1e-12 else",
     [C + "TestCL18_14Accords"]),
    ("CL18-14 verdict absent compté non notable", mesures_v54, "etalonner_juges_v54", "and v.get(i) is not None]\n        N = ", "]\n        N = ",
     [C + "TestCL18_14Accords"]),
    ("CL18-16 cumul écrêté", budget_v54.BudgetV54, "apres_etape", "self.cumul += float(cout_reel_usd)  # jamais écrêté (CL18-16)",
     "self.cumul = min(self.plafond, self.cumul + float(cout_reel_usd))", [C + "TestCL18_16Budget"]),
    ("CL18-16 M6b coupée fait tomber C13", budget_v54.BudgetV54, "apres_etape", "elif e[\"role\"] == \"protegee_hors_porte\":", "elif False:",
     [C + "TestCL18_16Budget"]),
    ("CL18-17 héritage sans garde A4", course2_v54.GenerationV54, "_heritage_garde", "if not trouvees:", "if True:",
     [C + "TestCL18_17Heritage"]),
    ("CL18-17 n compté toutes cases ensemble", bisociateur_v54, "choisir_paires_v54", "n_max = max((len(v) for v in par_case.values()), default=0)",
     "n_max = len(fiches)", [C + "TestCL18_17Heritage"]),
    ("I-1 nom de structure libre", bisociateur_v54, "valider_niche_v54", "if nom != ident:", "if False:",
     [X + "TestI1NomsDeStructures", P + "TestGardesE0"]),
    ("I-2 désaccord par valeur non éprouvé", bisociateur_v54, "garde_desaccord_v54", "if len(valeurs) > 1:", "if False:",
     [X + "TestI2Desaccord", P + "TestGardesE0"]),
    ("I-2 ordre non vérifié", course2_v54, "verifier_ordre_desaccord", "if l[\"horodatage\"] < horodatage_paires:", "if False:",
     [X + "TestI2Desaccord"]),
    ("I-3 seuils S28 de l'annexe non exigés", bisociateur_v54, "seuils_s28", "if not _reel(k) or not _reel(j):", "if False:",
     [X + "TestI3S28"]),
    ("I-4 définitions non vérifiées", bisociateur_v54, "lire_annexe_meta_v54", "if not isinstance(d, dict) or not all(isinstance(d.get(i), str) and d[i].strip() for i in ids):",
     "if False:", [X + "TestI4Definitions"]),
    ("I-4 consigne non vérifiée", bisociateur_v54, "lire_annexe_meta_v54", "        if manquants:\n            raise BisociationRefusee(\"A20/I-4 : identifiants",
     "        if False:\n            raise BisociationRefusee(\"A20/I-4 : identifiants", [X + "TestI4Definitions"]),
    ("I-5 règle de divergence ignorée", bisociateur_v54, "retenir_meta", "if regle_divergence == \"fiche_ecartee\":\n            return None\n        return l1[0], l1[1]",
     "return None", [X + "TestI5Divergence"]),
    ("I-6 poids négatif accepté", bisociateur_v54, "lire_annexe_meta_v54", "if not _reel(p[\"poids\"]) or p[\"poids\"] < 0:", "if not _reel(p[\"poids\"]):",
     [X + "TestI6Types"]),
    ("I-6 tables non contrôlées", bisociateur_v54, "lire_annexe_meta_v54", "if not _reel(p[table].get(b53._niche_cle(a, b))):", "if False:",
     [X + "TestI6Types"]),
    ("I-7 cause « niches indistinctes » perdue", course2_v54.GenerationV54, "_notes", "causes[\"meta\"] = (", "_ = (", [X + "TestI7I8Paires"]),
    ("I-8 paire reportée au bras suivant", bisociateur_v54, "choisir_paires_v54", "premier = ordre_bras[0] if ordre_bras else None",
     "premier = next((b for b in ordre_bras if any(q in notes_par_bras.get(b, {}) for q in paires)), ordre_bras[0] if ordre_bras else None)",
     [X + "TestI7I8Paires"]),
    ("I-9 une seule empreinte acceptée", bisociateur_v54, "lire_annexe_meta_v54", "if len(shas) < 2:", "if len(shas) < 1 and False:", [X + "TestI9I10Annexe"]),
    ("I-9 décision R-NNN non exigée", bisociateur_v54, "lire_annexe_meta_v54", "if not DECISION.search(p[\"approbation_lazar\"]):", "if False:",
     [X + "TestI9I10Annexe"]),
    ("I-10 profil vide accepté", bisociateur_v54, "verifier_non_vacuite", "    if not dans:\n", "    if False:\n", [X + "TestI9I10Annexe", X + "TestAnnexeReelle"]),
    ("I-10 jeu d'essai absent accepté", bisociateur_v54, "verifier_non_vacuite", "if not isinstance(jeu, dict) or len(jeu) < 2:", "if False:",
     [X + "TestI9I10Annexe"]),
    ("A3 échecs consécutifs sans arrêt", suivi_roles_v54.SuiviRoles, "apres", "elif r[\"consecutifs\"] >= self.echecs_max:", "elif False:",
     [P + "TestA3A11A14", P + "TestGardesE0"]),
    ("A3 délai ignoré", suivi_roles_v54.SuiviRoles, "apres", "coupe = duree > self.delai(fournisseur)", "coupe = False",
     [P + "TestA3A11A14", P + "TestGardesE0"]),
    ("A11 limite sans arrêt", suivi_roles_v54.SuiviRoles, "apres", "if modele in self.modeles_a11 and limite:", "if False:",
     [P + "TestA3A11A14", P + "TestGardesE0"]),
    ("A11 bascule acceptée", suivi_roles_v54.SuiviRoles, "apres", "if modele in self.modeles_a11 and modele_servi and modele_servi != modele:", "if False:",
     [P + "TestA3A11A14", P + "TestGardesE0"]),
    ("A14 jamais dépassée", suivi_roles_v54.SuiviRoles, "depassements_a14", "if r[\"appels\"] and", "if False and",
     [P + "TestA3A11A14", P + "TestGardesE0"]),
    ("A5 maximum d'exclus ignoré", prepilote_v54.PrePiloteV54, "_verifier_a5", "if n > self.pp[\"a5_exclus_max\"]:", "if False:",
     [P + "TestGardesTemoins"]),
    ("S6 ancres non contrôlées", prepilote_v54.PrePiloteV54, "_rendre", "if s6[\"ancres\"] + 1e-12 < self.pp[\"s6\"][\"ancres_min\"] or", "if False and",
     [P + "TestGardesTemoins"]),
    ("A8 longueur non contrôlée", prepilote_v54.PrePiloteV54, "_rendre", "if not ok_l:", "if False:", [P + "TestGardesTemoins"]),
    ("A6 ambigus ignorés", prepilote_v54.PrePiloteV54, "_boite_e5", "if not s20[\"passe\"]:", "if False:", [P + "TestGardesTemoins"]),
    ("A7 S19 ignorée", prepilote_v54.PrePiloteV54, "_boite_e5", "if s19.get(\"aire\") is not None and", "if False and", [P + "TestGardesTemoins"]),
    ("A13 squelettes non revérifiés", prepilote_v54.PrePiloteV54, "etape_e3_rendus", "if not verifier_scelle(", "if False and not verifier_scelle(",
     [P + "TestGardesTemoins"]),
    ("Ligne 31 source de M6b non cherchée", prepilote_v54, "garde_m6b", "if source.get(k) and normaliser_texte(source[k]) in plat:", "if False:",
     [P + "TestPrePiloteSain", P + "TestGardesE0"]),
    ("É0 table R5 sans refus", gardes_e0_v54, "rejouer_gardes", "    if manquantes or absentes:\n", "    if False:\n", [P + "TestGardesE0"]),
    ("DEP3 analyseur non exigé", prepilote_v54.PrePiloteV54, "__init__", "if etage1 is None or not callable(getattr(etage1, \"signaler\", None)):", "if False:",
     [P + "TestSquelettesEtConfiguration"]),
    ("DEP4 non exigée", configuration_v54, "verifier_dependances_lancement", "    if not present or not _chaine(nom):\n", "    if False:\n",
     [C + "TestCL18_09Specification", P + "TestLanceurV6"]),
    ("Plan du pré-pilote non imposé", prepilote_v54, "verifier_configuration_pre_pilote", "if tuple(noms) != attendu:", "if False:",
     [P + "TestSquelettesEtConfiguration"]),
]


def _remplacer_partout(ancien, nouveau):
    for nom, mod in list(sys.modules.items()):
        if mod is None or not (nom.startswith("pole") or nom.startswith("essais") or nom.startswith("aides")):
            continue
        for k, v in list(vars(mod).items()):
            if v is ancien:
                setattr(mod, k, nouveau)


def appliquer(cible, nom, ancien, nouveau):
    brut = inspect.getattr_static(cible, nom)
    est_static = isinstance(brut, staticmethod)
    f = brut.__func__ if est_static else (brut if not isinstance(cible, type) else getattr(cible, nom))
    f = getattr(f, "__func__", f)
    src = textwrap.dedent(inspect.getsource(f))
    if src.count(ancien) != 1:
        raise LookupError(f"fragment trouvé {src.count(ancien)} fois")
    mod = sys.modules[f.__module__]
    espace = dict(vars(mod))
    exec(compile(src.replace(ancien, nouveau), f"<mutation {f.__qualname__}>", "exec"), espace)
    g = espace[f.__name__]
    if isinstance(cible, type):
        setattr(cible, nom, staticmethod(g) if est_static else g)
    else:
        _remplacer_partout(f, g)

    def restaurer():
        if isinstance(cible, type):
            setattr(cible, nom, brut)
        else:
            _remplacer_partout(g, f)
    return restaurer


def jouer(noms):
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(n) for n in noms)
    r = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
    return r.testsRun, len(r.failures) + len(r.errors)


def principal():
    for n in {x for m in MUTATIONS for x in m[5]}:
        unittest.defaultTestLoader.loadTestsFromName(n)  # importe les modules d'essai avant toute mutation
    temoin = jouer(sorted({x for m in MUTATIONS for x in m[5]}))
    print(f"témoin (aucune mutation) : {temoin[0]} essais, {temoin[1]} en échec")
    tuees, total, non_appliquees = 0, 0, 0
    for libelle, cible, nom, ancien, nouveau, essais in MUTATIONS:
        total += 1
        try:
            restaurer = appliquer(cible, nom, ancien, nouveau)
        except (LookupError, OSError, TypeError) as e:
            non_appliquees += 1
            print(f"NON APPLIQUÉE  {libelle} : {e}")
            continue
        try:
            n, echecs = jouer(essais)
        finally:
            restaurer()
        tuees += echecs > 0
        print(f"{'tuée' if echecs else 'SURVIVANTE'}  {libelle} : {echecs}/{n} essais en échec")
    apres = jouer(sorted({x for m in MUTATIONS for x in m[5]}))
    print(f"mutations : {total} ; tuées : {tuees} ; survivantes : {total - tuees - non_appliquees} ; non appliquées : {non_appliquees}")
    print(f"témoin après restauration : {apres[0]} essais, {apres[1]} en échec")
    return 0 if tuees == total and temoin[1] == 0 and apres[1] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(principal())
