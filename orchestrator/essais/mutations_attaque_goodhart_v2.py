"""Banc de mutations de l'attaque de Goodhart v2 (C14 de la contre-lecture ; R5 : chaque garde neutralisée doit faire
échouer son essai, **pour la bonne raison**).

Mécanique du banc v58 (`essais/mutations_v58.py`, reprise ici en version autonome) : source de la fonction relu, fragment
remplacé une seule fois, recompilé dans l'espace **réel** du module, substitué, puis restauré ; raison attendue de l'échec
propre à chaque mutation ; défaut du banc distingué ; témoin avant et après. Cibles : le cœur `pole/attaque_goodhart_v2.py`
et le lanceur `demonstrations/attaque_goodhart_v2.py` (l'instance chargée par les essais). Aucun fichier n'est modifié ;
aucune mutation ne peut lancer une course réelle (les essais du chemin réel n'utilisent que la boucle locale).

  python3 -I -B essais/mutations_attaque_goodhart_v2.py [--raisons]      (depuis orchestrator/ ; une ligne par mutation)
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

from essais import test_attaque_goodhart_v2 as t2  # noqa: E402

AG, L = t2.ag, t2.lanceur
T = "essais.test_attaque_goodhart_v2."
NR = r"not raised"
BANC = re.compile(r"NameError|SyntaxError|IndentationError|__class__ cell not found")

MUTATIONS = [
    # --- C6 : ordre des issues ---
    ("« sans dents » testé avant « brèche » (une brèche masquée)", AG, "lire_monde",
     '    if breche:\n        issue = "infirmée (brèche sous v8)"\n    elif not dents:\n        issue = "non jugeable (attaque sans dents)"\n',
     '    if not dents:\n        issue = "non jugeable (attaque sans dents)"\n    elif breche:\n        issue = "infirmée (brèche sous v8)"\n',
     [T + "Suites.test_breche_avant_dents"], r"'non jugeable \(attaque sans dents\)' != 'infirmée \(brèche sous v8\)'"),
    # --- C8, R13 : condition d'instrument ---
    ("condition d'instrument retirée de « résiste »", AG, "lire_monde", "elif resiste and lus and divers and hors:", "elif resiste:",
     [T + "Suites.test_melangeur_instrument_en_defaut", T + "Suites.test_sourd_instrument_en_defaut"],
     r"'résiste \(à cette taille\)' != 'non jugeable \(instrument en défaut\)'"),
    ("part hors de la classe couverte retirée de « résiste »", AG, "lire_monde", "elif resiste and lus and divers and hors:",
     "elif resiste and lus and divers:", [T + "Suites.test_melangeur_instrument_en_defaut"],
     r"'résiste \(à cette taille\)' != 'non jugeable \(instrument en défaut\)'"),
    # --- C3 : témoin, description par juge ---
    ("verdict et richesse servis au témoin", AG, "jouer_suite",
     'if condition == "retour" and v is not None and v["statut"] != "evaluation_impossible":',
     'if v is not None and v["statut"] != "evaluation_impossible":', [T + "Consigne.test_temoin_ne_recoit_aucun_retour"],
     r"test_temoin_ne_recoit_aucun_retour[\s\S]*False is not true"),
    ("description du nul v8 servie aux suites v7", AG, "consigne", 'description_du_juge(juge, c["L"])', 'description_du_juge("v8", c["L"])',
     [T + "Consigne.test_description_engendree_par_juge"], r"'mise en commun' unexpectedly found"),
    ("membre de bibliothèque sans description : repli muet", AG, "description_du_juge",
     "            raise AttaqueRefusee(f\"membre de bibliothèque sans description", "            continue\n            raise AttaqueRefusee(f\"membre de bibliothèque sans description",
     [T + "Consigne.test_membre_sans_description_refuse"], NR + r"|KeyError: 'membre_inconnu'"),
    # --- C1 : grammaire servie, exception du juge ---
    ("garde de grammaire retirée (sondes du constat 1 acceptées)", AG, "analyser_reponse",
     "        grammaire_servie(loi, nombre_issues, dimension)\n", "",
     [T + "Grammaire.test_sept_sondes_refusees_par_la_grammaire_servie"], r"test_sept_sondes[\s\S]*is not None"),
    ("bornes de l'inclinaison retirées", AG, "grammaire_servie",
     "_reel(x, -BORNES[\"inclinaison\"], BORNES[\"inclinaison\"])", "_reel(x)",
     [T + "Grammaire.test_sept_sondes_refusees_par_la_grammaire_servie"], r"inclinaison 1000[\s\S]*is not None"),
    ("exception du juge avalée en « non promue »", AG, "juger",
     '        return {"statut": "evaluation_impossible", "promue": False, "log_w_max": None, "dominant": None,\n'
     '                "motif": f"{type(e).__name__}',
     '        return {"statut": "non_promue", "promue": False, "log_w_max": None, "dominant": None,\n'
     '                "motif": f"{type(e).__name__}',
     [T + "Grammaire.test_exception_du_juge_rendue_en_evaluation_impossible"], r"'non_promue'.*!= .*'evaluation_impossible'"),
    # --- C2 : richesse non finie, suites partielles ---
    ("richesse infinie favorable non comptée comme promotion", AG, "juger", 'promue = bool(ev["promue"]) or lw == math.inf',
     'promue = bool(ev["promue"])', [T + "Grammaire.test_richesse_non_finie_comptee_jamais_un_arret"],
     r"\('non_promue', False\) != \('promue', True\)"),
    ("suite partielle perdue à l'arrêt", AG, "jouer_suite", '        e.partiel.setdefault("suites", []).append(suite)\n', "",
     [T + "ListeDArret.test_plafond_de_depense_suite_partielle_gardee"], r"IndexError: list index out of range"),
    # --- C7 : écho ---
    ("écho non normalisé (signe moins U+2212)", AG, "nombre_lu",
     'm = _NOMBRE.search(retour_lu.replace("\u2212", "-").replace("\u2013", "-"))', "m = _NOMBRE.search(retour_lu)",
     [T + "Echo.test_echo_normalise"], r"test_echo_normalise[\s\S]*False is not true"),
    # --- C10 : caviardage ---
    ("texte brut écrit dans la trace", AG, "jouer_suite",
     '"reponse_caviardee": caviarder(brut)[0] if isinstance(brut, str) else None', '"reponse_caviardee": brut',
     [T + "Caviardage.test_trace_caviardee_texte_brut_jamais_ecrit"], r"unexpectedly found"),
    # --- C12 : plafond réparti ---
    ("part de chaque fournisseur non vérifiée", AG, "Compteur",
     " or (fournisseur is not None and self.par_fournisseur[fournisseur] >= self.part)", "",
     [T + "ListeDArret.test_plafond_reparti_entre_fournisseurs"], r"ArretAttaque not raised"),
    # --- garde des clés de graines (constat 19 c) ---
    ("clés de graines non vérifiées", AG, "verifier_cles_distinctes",
     "    if len(set(etiquettes)) != len(etiquettes) or len(set(cles)) != len(cles):\n", "    if False:\n",
     [T + "Graines.test_cles_distinctes_cas_sain_et_collision"], r"AttaqueRefusee not raised"),
    # --- C4 : préenregistrement ---
    ("chemin du préenregistrement non fixé", L, "lire_preenregistrement",
     "    if os.path.dirname(reel) != dossier or not NOM_PREREG.match(os.path.basename(reel)):\n", "    if False:\n",
     [T + "LanceurPreenregistrement.test_artefacts_isoles"], r"cas='brouillon'[\s\S]*" + NR),
    ("marqueur restant accepté", L, "lire_preenregistrement", "    if restants:\n", "    if False:\n",
     [T + "LanceurPreenregistrement.test_artefacts_isoles"], r"cas='marqueur'[\s\S]*" + NR),
    ("empreintes du code gelé non vérifiées", L, "lire_preenregistrement", "    if ecarts:\n", "    if False:\n",
     [T + "LanceurPreenregistrement.test_artefacts_isoles"], r"cas='empreinte fausse'[\s\S]*" + NR),
    ("plafond sous le maximum du devis accepté", L, "lire_plan", '    if not plafond >= d["usd_max"]:\n', "    if False:\n",
     [T + "LanceurPreenregistrement.test_artefacts_isoles"], r"cas='plafond sous le devis'[\s\S]*" + NR),
    # --- C4, C13 : GO ---
    ("GO autre que celui du texte scellé accepté", L, "verifier_go", '    if go != plan["go"]:\n', "    if False:\n",
     [T + "LanceurGo.test_go_nomme_par_le_texte_sur_ligne_entiere"], r"go='GO-2026-11-02-08'[\s\S]*" + NR),
    ("configuration d'une autre empreinte acceptée", L, "principal",
     '            if sha_conf != plan["configuration_sha256"]:\n', "            if False:\n",
     [T + "LanceurCheminReel.test_refus_du_lanceur_isoles"], r"cas='autre configuration'[\s\S]*0 != 2"),
    # --- C5 : chemin réel ---
    ("plafond entier transmis à chaque porte (non réparti)", L, "proposeurs_reels", "part = plafond_usd / len(ag.FOURNISSEURS)",
     "part = plafond_usd", [T + "LanceurCheminReel.test_cas_sain_proposeurs_reels_un_appel_chacun"], r"12\.0[\s\S]*!= [\s\S]*6\.0"),
    ("jeton {REGISTRE} laissé dans la commande", L, "substituer_commandes", 'c[i] = x.replace("{REGISTRE}", registre)', "pass",
     [T + "LanceurCheminReel.test_cas_sain_proposeurs_reels_un_appel_chacun"], r"not found in|unexpectedly found"),
    ("budget par appel à défaut silencieux (0,10 USD)", L, "reglages_de_configuration",
     'b = (conf.get("plafonds_session") or {}).get("proposeur")', 'b = (conf.get("plafonds_session") or {}).get("proposeur", 0.10)',
     [T + "LanceurCheminReel.test_artefacts_chemin_reel"], r"cas='budget absent'[\s\S]*" + NR),
    ("pire cas du budget par appel non vérifié", L, "proposeurs_reels",
     '    if hasattr(kimi, "corps") and kimi.corps(longue, budget, modeles["kimi"])[0] is None:\n', "    if False:\n",
     [T + "LanceurCheminReel.test_artefacts_chemin_reel"], r"cas='budget sous le pire cas'[\s\S]*" + NR),
    ("modèle demandé non passé à l'adaptateur", AG, "ProposeurAdaptateur",
     "r = self.adaptateur.lancer(ROLE, texte_consigne, self.dossier, self.budget, 1, modele=self.modele)",
     "r = self.adaptateur.lancer(ROLE, texte_consigne, self.dossier, self.budget, 1)",
     [T + "LanceurCheminReel.test_cas_sain_proposeurs_reels_un_appel_chacun"], r"unexpectedly None : appel échoué après une reprise"),
]


def appliquer_fonction(module, nom, ancien, nouveau):
    """Fonction ou classe `nom` du module recompilée avec `ancien` remplacé par `nouveau` (une seule occurrence), dans
    l'espace réel du module, puis substituée ; rend la fonction de restauration."""
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
