"""Essais de la v52 : mode « juges seulement » (décision R-805), adaptateur de bascule déclarée, relais v2. Aucun appel payant,
aucune clé, aucun réseau : moteurs simulés de l'orchestrateur, faux adaptateurs, faux kit, amont factice local.

La course arrêtée de chaque essai est une **vraie** course de la v51 (`pole/ideation_v2.executer_ideation`, moteur simulé), arrêtée
comme la course 1, tentative 2 : refus (`stop_reason = refusal`) du juge Fable, premier juge, après les passes des proposeurs ; sa
consigne mise à l'écart sert de témoin de reconstruction.

Cas sain (lanceur v3, moteur simulé) ; artefacts : fiches altérées (sceau faux, rescellées, empreinte attendue fausse), consigne
de la course altérée, témoin mal classé (code 4), refus d'Opus avec bascule déclarée (repli consigné ; aussi par le faux kit à
travers l'adaptateur de bascule), refus d'Opus sans bascule (arrêt), bascules non déclarées (événement de repli du kit, modèle
servi autre, modèle de repli servi en silence, paire non autorisée, refus du repli : arrêt), refus d'Argon (arrêt), budgets,
attestation, relais (modèles permis exacts, v2 exigé), relais v2 en processus (opus 4.6 permis, autre modèle 403, barème borné).
"""

import contextlib
import hashlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import unittest
from unittest import mock

from essais.aides import CasAvecDossier
from essais.test_v7_ideation_v2 import FauxAdaptateur, fiche_brute, notes_pour
from pole import ideation_v2 as idn
from pole import juges_seulement_v1 as js
from pole.adaptateurs import ModeleNonPermis, Resultat
from pole.adaptateurs_v2 import AdaptateurClaudeSDKBascule, verifier_bascules, verifier_modele_reel_ou_repli
from pole.outils import ecrire_json_scelle, sha256_fichier, verifier_scelle

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OPUS, REPLI, FABLE, ARGON = "claude-opus-5-5", "claude-opus-4-6", "claude-fable-5-1", "gemini-4-argon"


def lanceur_v3():
    spec = importlib.util.spec_from_file_location("ideation_v3_lanceur", os.path.join(RACINE, "demonstrations", "ideation_v3.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def notes_temoins_ok(idents, consigne):
    """Juge scripté qui respecte le critère gelé des témoins (les reconnaît à leur nom dans la consigne)."""
    bloc = json.loads(re.search(r"```json\n(\[.*\])\n```", consigne, re.S).group(1))
    sur, doublons, par_nom = {}, [], {f["nom"]: f["identifiant"] for f in bloc}
    for f in bloc:
        if f["nom"] == "Verbeux vide":
            sur[f["identifiant"]] = {"avantage": 1, "originalite": 1, "falsifiabilite": 0}
        if f["nom"] == "Assuré occupé":
            sur[f["identifiant"]] = {"avantage": 1, "originalite": 0}
    if "Jumeau" in par_nom and "Sobre fort" in par_nom:
        doublons.append([par_nom["Jumeau"], par_nom["Sobre fort"]])
    objet = notes_pour(idents, 2, **sur)
    objet["doublons"] = doublons
    return objet


def refus(modele, evenement="result.stop_reason", servi=None, cout=0.3):
    servi = modele if servi is None else servi
    return Resultat("", [], cout, "refus", "refus (R-764) : le message de résultat porte stop_reason = refusal",
                    refus={"motif": "stop_reason = refusal" if "stop_reason" in evenement else "repli du kit",
                           "modele_demande": modele, "modele_servi": servi, "evenement": evenement}, modele_servi=servi)


class CourseQuiRefuseAuJugeFable(FauxAdaptateur):
    """La course de la v51 : proposeurs normaux, juge Fable qui refuse (comme la course 1, tentative 2)."""

    def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
        if role == "juge_ideation" and os.path.basename(dossier) == "juge-fable":
            self.appels.append({"role": role, "dossier": dossier, "modele": modele})
            return refus(modele)
        return super().lancer(role, consigne, dossier, budget_usd, max_tours, modele=modele)


class JugeScenario:
    """Faux juge du mode : par modèle demandé, un comportement — « ok » (notes conformes aux témoins, modèle servi = demandé),
    « refus » (stop_reason), « repli-kit » (événement de repli du kit, autre modèle), « servi:<m> » (session ok mais servie par
    <m>), « temoins-ko » (notes plates : témoins mal classés). Rend « OK » à l'appel de contrôle."""

    def __init__(self, nom="faux-juge", **par_modele):
        self.nom, self.par_modele, self.appels = nom, par_modele, []

    def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
        self.appels.append({"role": role, "modele": modele, "dossier": dossier,
                            "consigne_sha256": hashlib.sha256(consigne.encode()).hexdigest()})
        if consigne.startswith(idn.APPEL_DE_CONTROLE_CONSIGNE):
            return Resultat("OK", [], 0.01, "ok", modele_servi=modele)
        mode = self.par_modele.get(modele, "ok")
        if mode == "refus":
            return refus(modele)
        if mode == "repli-kit":
            return refus(modele, evenement="system.model_refusal_fallback", servi="claude-sonnet-5-5")
        idents = sorted(set(re.findall(r'"identifiant": "(T\d\d)"', consigne)))
        objet = notes_pour(idents, 2) if mode == "temoins-ko" else notes_temoins_ok(idents, consigne)
        servi = mode.split(":", 1)[1] if mode.startswith("servi:") else modele
        return Resultat("```json\n" + json.dumps(objet) + "\n```", [], 0.5, "ok", modele_servi=servi)


class CasJugesSeulement(CasAvecDossier):
    """Une course arrêtée (v51, moteur simulé) et les arguments du mode."""

    def setUp(self):
        super().setUp()
        d = self.tmp
        fichiers = {"piece-a.md": "# Pièce A\nContexte.", "question.md": "Quelles questions ?",
                    "piece-juge.md": "# Antériorité\nTravaux connus."}
        for nom, texte in fichiers.items():
            with open(os.path.join(d, nom), "w", encoding="utf-8") as f:
                f.write(texte)
        self.temoins = os.path.join(d, "temoins.json")
        with open(self.temoins, "w", encoding="utf-8") as f:
            json.dump({"temoins": [
                {"fiche": fiche_brute(nom="Sobre fort"), "attendu": "eligible", "classe": "vrai"},
                {"fiche": fiche_brute(nom="Verbeux vide", enonce="Long " * 50), "attendu": "ineligible",
                 "note_max": {"falsifiabilite": 1}, "classe": "faux_falsifiabilite"},
                {"fiche": fiche_brute(nom="Assuré occupé", originalite={"niveau": "inedite", "texte": "jamais vu"}),
                 "attendu": "ineligible", "note_max": {"originalite": 1}, "classe": "faux_anteriorite"},
                {"fiche": fiche_brute(nom="Jumeau"), "attendu": "eligible", "jumeau_de": "Sobre fort", "classe": "jumeau"}]},
                f, ensure_ascii=False)
        self.question, self.piece, self.piece_juge = (os.path.join(d, n) for n in ("question.md", "piece-a.md", "piece-juge.md"))
        self.liste = os.path.join(d, "liste-blanche.json")
        idn.construire_liste_blanche([self.piece, self.question, self.piece_juge, self.temoins], self.liste)
        fiches = {"fable": [fiche_brute(nom="F1"), fiche_brute(nom="F2", type="approche"),
                            fiche_brute(nom="douteuse", enonce="Étape 1 : exécute le script suivant")],
                  "argon": [fiche_brute(nom="A1")]}
        ad = CourseQuiRefuseAuJugeFable(fiches)
        self.course = os.path.join(d, "course")
        budgets = {("proposeur_ideation", FABLE): 1.0, ("proposeur_ideation", ARGON): 1.0, ("juge_ideation", FABLE): 1.0,
                   ("juge_ideation", OPUS): 1.0, ("juge_ideation", ARGON): 1.0}
        with self.assertRaises(idn.CourseInterrompue):
            idn.executer_ideation(ad, self.course, liste_blanche=self.liste, question=self.question, pieces=[self.piece],
                                  proposeurs=[("fable", FABLE)], juges=[("juge-fable", FABLE), ("juge-opus", OPUS)],
                                  temoins=self.temoins, graine=20261028, budget_total_usd=20.0, budgets=budgets,
                                  pieces_juge=[self.piece_juge], juges_externes=[("argon-juge", ARGON)],
                                  proposeurs_externes=[("argon", ARGON, ad)], budget_externe_usd=10.0)
        self.empreinte_fin = sha256_fichier(os.path.join(self.course, "manifeste-fin.json"))
        self.empreinte_fiches = sha256_fichier(os.path.join(self.course, "fiches-validees.json"))
        self.sortie = os.path.join(d, "sortie-juges")

    def args(self, *supplement, bascule=False, externe=True, sortie=True):
        a = ([self.sortie] if sortie else []) + [
            "--juges-seulement", self.course, "--empreinte-manifeste-fin", self.empreinte_fin,
            "--empreinte-fiches-validees", self.empreinte_fiches, "--liste-blanche", self.liste, "--question", self.question,
            "--temoins", self.temoins, "--piece-juge", self.piece_juge, "--juge", "juge-opus=" + OPUS,
            "--budget", f"juge_ideation|{OPUS}=1", "--budget", f"juge_ideation|{ARGON}=1", "--budget-total-usd", "3",
            "--budget-externe-usd", "1.2"]
        if externe:
            a += ["--juge-externe", "argon-juge=" + ARGON]
        if bascule:
            a += ["--bascule-declaree", f"{OPUS}={REPLI}", "--budget", f"juge_ideation|{REPLI}=1"]
        return a + list(supplement)

    def jouer(self, argv, adaptateur=None, externe=None):
        """Le lanceur v3 ; avec `adaptateur`, les adaptateurs du mode sont remplacés (scénarios)."""
        lanceur = lanceur_v3()
        if adaptateur is not None:
            def fabriquer(args, plan, sortie):
                return adaptateur, {e: (externe or adaptateur) for e, _ in plan["juges_externes"]}, None, {}, None
            lanceur.fabriquer_adaptateurs = fabriquer
        sortie, erreurs = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(erreurs):
            code = lanceur.principal(argv)
        return code, sortie.getvalue(), erreurs.getvalue()

    def fin(self):
        chemin = os.path.join(self.sortie, "manifeste-fin-juges.json")
        self.assertTrue(verifier_scelle(chemin))
        with open(chemin, encoding="utf-8") as f:
            return json.load(f)["reglages"]

    def assert_sortie_scellee(self):
        """Chaque fichier de la sortie a son compagnon juste ; la liste des empreintes couvre tout."""
        self.assertTrue(verifier_scelle(os.path.join(self.sortie, "empreintes-sortie.txt")))
        with open(os.path.join(self.sortie, "empreintes-sortie.txt"), encoding="utf-8") as f:
            listes = {l.split("  ", 1)[1]: l.split("  ", 1)[0] for l in f.read().splitlines()}
        for racine, _, fichiers in os.walk(self.sortie):
            for nom in fichiers:
                rel = os.path.relpath(os.path.join(racine, nom), self.sortie)
                if rel.startswith("empreintes-sortie.txt"):
                    continue
                self.assertEqual(listes.get(rel), sha256_fichier(os.path.join(self.sortie, rel)), rel)
                if not nom.endswith(".sha256"):
                    self.assertTrue(verifier_scelle(os.path.join(racine, nom)), rel)


class TestCourseArreteeFixture(CasJugesSeulement):
    def test_la_course_d_essai_est_arretee_comme_la_course_1(self):
        with open(os.path.join(self.course, "manifeste-fin.json"), encoding="utf-8") as f:
            fin = json.load(f)["reglages"]
        self.assertEqual(fin["statut_course"]["statut"], "refus")
        self.assertEqual(fin["statut_course"]["etiquette"], "juge-fable")
        self.assertTrue(os.path.isfile(os.path.join(self.course, js.ECART, "juges", "traces-juge-fable", "consigne.md")))
        self.assertFalse(os.path.exists(os.path.join(self.course, "classement.json")))


class TestCasSain(CasJugesSeulement):
    def test_cas_sain_moteur_simule(self):
        avant = {n: sha256_fichier(os.path.join(self.course, n)) for n in js.FICHIERS_SCELLES_COURSE}
        code, sortie, erreurs = self.jouer(self.args("--horodatage", "jeudi 30 octobre 2026"))
        self.assertEqual(code, 0, erreurs)
        bilan = json.loads(sortie)
        self.assertTrue(bilan["classement_lisible_L2_L4"])
        self.assertEqual(bilan["fiches_notees"], 3)  # F1, F2, A1 ; la fiche en quarantaine n'est jamais servie
        self.assertEqual(bilan["bascules"], [])
        self.assertEqual(sorted(bilan["juges"]), ["argon-juge", "juge-opus"])
        # la course reste intacte (R12)
        self.assertEqual(avant, {n: sha256_fichier(os.path.join(self.course, n)) for n in js.FICHIERS_SCELLES_COURSE})
        with open(os.path.join(self.sortie, "manifeste-depart-juges.json"), encoding="utf-8") as f:
            depart = json.load(f)["reglages"]
        self.assertEqual(depart["course_arretee"]["empreintes"]["fiches-validees.json"], self.empreinte_fiches)
        self.assertTrue(depart["reconstruction_des_consignes"]["juge-fable"]["identique"])
        self.assertEqual(depart["fiches_servies"], 3)
        self.assertEqual(depart["temoins_servis"], 4)
        with open(os.path.join(self.sortie, "noyau", "cles-anonymisation-par-juge.json"), encoding="utf-8") as f:
            cles = json.load(f)
        servis = set(cles["juge-opus"].values())
        self.assertEqual(len(servis), 7)
        self.assertFalse(any(i.startswith("fable-p1-03") for i in servis))  # « douteuse » (quarantaine)
        with open(os.path.join(self.sortie, "classement.json"), encoding="utf-8") as f:
            classement = json.load(f)
        self.assertTrue(classement["lisible_L2_L4"])
        self.assertEqual(len(classement["lignes"]), 3)
        fin = self.fin()
        self.assertEqual(fin["statut"]["statut"], "ok")
        self.assertTrue(fin["journal"]["cout_fictif"])
        self.assertIn("claude-opus-5-5", json.dumps(fin["journal"]["controles"]))
        self.assert_sortie_scellee()

    def test_verifier_seulement_sans_ecriture(self):
        code, sortie, erreurs = self.jouer(self.args("--verifier-seulement", sortie=False, bascule=True))
        self.assertEqual(code, 0, erreurs)
        plan = json.loads(sortie)
        self.assertTrue(plan["sans_appel"])
        self.assertTrue(plan["reconstruction_des_consignes_de_la_course"]["juge-fable"]["identique"])
        self.assertEqual(plan["modeles_claude_du_relais"], [REPLI, OPUS])
        self.assertEqual(plan["sommes_des_plafonds"]["claude"], 2.4)  # 2 contrôles à 0,2 + juge 1 + repli 1
        self.assertIn("argon-juge", plan["attestation_a_signer"]["consignes_en_attente_sha256"])
        self.assertNotIn("F1", sortie)  # jamais le contenu d'une fiche
        self.assertFalse(os.path.exists(self.sortie))

    def test_sans_juges_seulement_le_lanceur_v3_est_la_v2(self):
        argv = ["--mesurer-consignes", "--liste-blanche", self.liste, "--question", self.question, "--piece", self.piece,
                "--temoins", self.temoins, "--piece-juge", self.piece_juge]
        code3, sortie3, _ = self.jouer(argv)
        spec = importlib.util.spec_from_file_location("v2_pour_essai", os.path.join(RACINE, "demonstrations", "ideation_v2.py"))
        v2 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(v2)
        flux = io.StringIO()
        with contextlib.redirect_stdout(flux):
            code2 = v2.principal(argv)
        self.assertEqual((code3, sortie3), (code2, flux.getvalue()))
        for option in (["--bascule-declaree", f"{OPUS}={REPLI}"], ["--verifier-seulement"], ["--empreinte-fiches-validees", "0" * 64]):
            with self.assertRaises(SystemExit):
                self.jouer(argv + option)


class TestFichesAlterees(CasJugesSeulement):
    def _refuse(self, motif):
        code, _, erreurs = self.jouer(self.args())
        self.assertEqual(code, 2)
        self.assertIn(motif, erreurs)
        self.assertFalse(os.path.exists(self.sortie), "refus avant toute écriture")

    def test_fiches_alterees_sceau_faux(self):
        chemin = os.path.join(self.course, "fiches-validees.json")
        with open(chemin, "a", encoding="utf-8") as f:
            f.write(" ")
        self._refuse("sceau faux")

    def test_fiches_alterees_puis_rescellees(self):
        chemin = os.path.join(self.course, "fiches-validees.json")
        with open(chemin, encoding="utf-8") as f:
            fiches = json.load(f)
        fiches[0]["enonce"] = fiches[0]["enonce"] + " (altéré)"
        os.remove(chemin)
        os.remove(chemin + ".sha256")
        ecrire_json_scelle(chemin, fiches)
        self.assertTrue(verifier_scelle(chemin))
        self._refuse("fiches-validees.json : empreinte")

    def test_fiche_alteree_avec_empreinte_attendue_mise_a_jour(self):
        """Même si l'opérateur donne la nouvelle empreinte, la fiche ne repasse pas le gabarit à son empreinte."""
        chemin = os.path.join(self.course, "fiches-validees.json")
        with open(chemin, encoding="utf-8") as f:
            fiches = json.load(f)
        fiches[1]["piege"] = "piège changé après la course"
        os.remove(chemin)
        os.remove(chemin + ".sha256")
        ecrire_json_scelle(chemin, fiches)
        self.empreinte_fiches = sha256_fichier(chemin)
        self._refuse("empreinte recalculée")

    def test_empreinte_attendue_du_manifeste_de_fin_fausse(self):
        self.empreinte_fin = "0" * 64
        self._refuse("manifeste-fin.json : empreinte")

    def test_consigne_de_la_course_alteree(self):
        chemin = os.path.join(self.course, js.ECART, "juges", "traces-juge-fable", "consigne.md")
        with open(chemin, "a", encoding="utf-8") as f:
            f.write("\najout")
        self._refuse("sceau faux")
        with open(chemin + ".sha256", "w", encoding="utf-8") as f:
            f.write(sha256_fichier(chemin) + "  consigne.md\n")
        self._refuse("reconstruite")

    def test_juges_ou_temoins_hors_de_la_course(self):
        for argv, motif in ((self.args()[:-2] + ["--juge-externe", "autre-juge=" + ARGON], "pas un juge externe"),
                            ([a if a != "juge-opus=" + OPUS else "juge-x=" + OPUS for a in self.args()], "pas un juge Claude")):
            code, _, erreurs = self.jouer(argv)
            self.assertEqual(code, 2)
            self.assertIn(motif, erreurs)
        # pièce des juges retirée : la liste ne correspond plus à celle de la course
        argv = self.args()
        i = argv.index("--piece-juge")
        del argv[i:i + 2]
        code, _, erreurs = self.jouer(argv)
        self.assertEqual(code, 2)
        self.assertIn("pièces des juges", erreurs)


class TestTemoins(CasJugesSeulement):
    def test_temoin_mal_classe_code_4(self):
        juge = JugeScenario(**{OPUS: "temoins-ko"})
        code, sortie, erreurs = self.jouer(self.args(), adaptateur=juge, externe=JugeScenario())
        self.assertEqual(code, 4, erreurs)
        bilan = json.loads(sortie)
        self.assertFalse(bilan["classement_lisible_L2_L4"])
        self.assertEqual(bilan["temoins_ok_par_juge"], {"juge-opus": False, "argon-juge": True})
        self.assertNotIn("retenues", bilan)
        with open(os.path.join(self.sortie, "classement.json"), encoding="utf-8") as f:
            self.assertFalse(json.load(f)["lisible_L2_L4"])
        self.assert_sortie_scellee()


class TestBascule(CasJugesSeulement):
    def test_refus_d_opus_avec_bascule_declaree(self):
        juge = JugeScenario(**{OPUS: "refus", REPLI: "ok"})
        code, sortie, erreurs = self.jouer(self.args(bascule=True), adaptateur=juge, externe=JugeScenario())
        self.assertEqual(code, 0, erreurs)
        bilan = json.loads(sortie)
        self.assertEqual(bilan["bascules"], [{"etiquette": "juge-opus", "modele_declare": OPUS, "modele_repli": REPLI,
                                              "modele_servi": REPLI}])
        self.assertEqual(bilan["modele_servi_par_juge"]["juge-opus"]["servi"], REPLI)
        sessions = [a for a in juge.appels if a["role"] == "juge_ideation" and os.sep + "controles" + os.sep not in a["dossier"]]
        self.assertEqual([a["modele"] for a in sessions], [OPUS, REPLI])
        self.assertEqual(sessions[0]["consigne_sha256"], sessions[1]["consigne_sha256"], "même consigne")
        self.assertIn("juges-bascule", sessions[1]["dossier"])
        fin = self.fin()
        b = fin["bascules"][0]
        self.assertEqual(b["refus_initial"]["evenement"], "result.stop_reason")
        self.assertEqual(b["refus_initial"]["modele_servi"], OPUS)
        self.assertIn("R-805", b["autorisation"])
        self.assertEqual(len(fin["refus_modele"]), 1)
        self.assertTrue(os.path.isdir(os.path.join(self.sortie, js.ECART, "juges", "traces-juge-opus")))
        self.assertFalse(os.path.exists(os.path.join(self.sortie, "juges", "juge-opus")))
        # coût de la session refusée compté (0,3) ; contrôles des deux modèles Claude joués (repli compris)
        self.assertAlmostEqual(fin["journal"]["cout_total_usd"], 0.02 + 0.3 + 0.5)
        self.assertEqual(sorted(k for k in fin["journal"]["controles"] if not k.startswith("externe:")), [REPLI, OPUS])
        with open(os.path.join(self.sortie, "noyau", "modeles.json"), encoding="utf-8") as f:
            self.assertEqual(json.load(f)["par_juge"]["juge-opus"]["servi"], REPLI)
        self.assert_sortie_scellee()

    def _arret(self, argv, juge, externe=None, motif="refus (R-764)"):
        code, _, erreurs = self.jouer(argv, adaptateur=juge, externe=externe or JugeScenario())
        self.assertEqual(code, 2, erreurs)
        self.assertIn(motif, erreurs)
        fin = self.fin()
        self.assertTrue(fin["erreur"])
        self.assertFalse(os.path.exists(os.path.join(self.sortie, "classement.json")))
        self.assert_sortie_scellee()
        return fin

    def test_refus_d_opus_sans_bascule_arret(self):
        juge = JugeScenario(**{OPUS: "refus"})
        fin = self._arret(self.args(), juge, motif="aucune bascule déclarée")
        self.assertEqual(fin["statut"]["statut"], "refus")
        self.assertEqual(fin["bascules"], [])
        self.assertNotIn(REPLI, [a["modele"] for a in juge.appels])
        self.assertTrue(os.path.isdir(os.path.join(self.sortie, js.ECART, "juges", "juge-opus")))

    def test_repli_du_kit_non_declare_arret(self):
        """Événement de repli du kit vers un autre modèle : arrêt, même avec une bascule déclarée."""
        juge = JugeScenario(**{OPUS: "repli-kit"})
        fin = self._arret(self.args(bascule=True), juge, motif="changement de modèle non déclaré")
        self.assertEqual(fin["bascules"], [])
        self.assertEqual(fin["refus_modele"][0]["modele_servi"], "claude-sonnet-5-5")
        self.assertFalse(os.path.exists(os.path.join(self.sortie, "juges-bascule")))

    def test_modele_servi_autre_arret(self):
        for servi in ("claude-sonnet-5-5", REPLI):  # le modèle de repli servi en silence n'est pas une bascule déclarée
            with self.subTest(servi=servi):
                shutil.rmtree(self.sortie, ignore_errors=True)
                juge = JugeScenario(**{OPUS: "servi:" + servi})
                fin = self._arret(self.args(bascule=True), juge, motif="changement de modèle non déclaré")
                self.assertEqual(fin["refus_modele"][0]["evenement"], "resultat.modele_servi")
                self.assertEqual(fin["bascules"], [])

    def test_refus_du_repli_arret(self):
        juge = JugeScenario(**{OPUS: "refus", REPLI: "refus"})
        fin = self._arret(self.args(bascule=True), juge, motif="modèle de repli")
        self.assertEqual(len(fin["refus_modele"]), 2)
        self.assertEqual(fin["bascules"][0]["refus_du_repli"]["modele_demande"], REPLI)

    def test_bascule_non_autorisee_refusee_avant_tout(self):
        for paire in (f"{OPUS}=claude-sonnet-5-5", f"{FABLE}={REPLI}", f"{OPUS}={OPUS}", f"{ARGON}={REPLI}"):
            with self.subTest(paire=paire):
                argv = self.args() + ["--bascule-declaree", paire, "--budget", f"juge_ideation|{paire.split('=')[1]}=1"]
                code, _, erreurs = self.jouer(argv, adaptateur=JugeScenario())
                self.assertEqual(code, 2)
                self.assertFalse(os.path.exists(self.sortie))
        with self.assertRaises(ModeleNonPermis):
            verifier_bascules({OPUS: "claude-sonnet-5-5"})

    def test_refus_d_argon_arret(self):
        externe = JugeScenario(**{ARGON: "refus"})
        fin = self._arret(self.args(bascule=True), JugeScenario(), externe=externe, motif="jamais de bascule pour un juge externe")
        self.assertEqual(fin["statut"]["etiquette"], "argon-juge")
        self.assertEqual(fin["bascules"], [])
        self.assertTrue(os.path.exists(os.path.join(self.sortie, "notes-par-juge-partielles.json")))


class TestBudgetsEtGardes(CasJugesSeulement):
    def test_somme_des_plafonds(self):
        argv = self.args(bascule=True)
        argv[argv.index("--budget-total-usd") + 1] = "2.3"  # 0,4 de contrôles + 1 + 1 de repli = 2,4
        code, _, erreurs = self.jouer(argv, adaptateur=JugeScenario())
        self.assertEqual(code, 2)
        self.assertIn("somme des plafonds Claude", erreurs)
        argv = self.args()
        argv[argv.index("--budget-externe-usd") + 1] = "1.1"
        code, _, erreurs = self.jouer(argv, adaptateur=JugeScenario())
        self.assertIn("somme des plafonds externes", erreurs)
        argv = self.args() + ["--bascule-declaree", f"{OPUS}={REPLI}"]  # repli sans plafond
        code, _, erreurs = self.jouer(argv, adaptateur=JugeScenario())
        self.assertEqual(code, 2)
        self.assertIn("aucun plafond par session", erreurs)

    def test_plafond_par_session_compte(self):
        """Une session refusée qui coûte plus que prévu fait arrêter avant la session de repli (total tenu)."""
        class Cher(JugeScenario):
            def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
                r = super().lancer(role, consigne, dossier, budget_usd, max_tours, modele=modele)
                if r.statut == "refus":
                    r.cout_declare_usd = 2.5
                return r
        fin = TestBascule._arret(self, self.args(bascule=True), Cher(**{OPUS: "refus"}), motif="plafond total Claude")
        self.assertEqual(fin["statut"]["statut"], "plafond")

    def test_options_de_course_refusees(self):
        for option in (["--proposeur", "fable=" + FABLE], ["--piece", self.piece], ["--seconde-passe"],
                       ["--bras-rapporte-differe"], ["--tests-de-mort", "1"]):
            with self.assertRaises(SystemExit):
                self.jouer(self.args(*option))
        with self.assertRaises(SystemExit):  # liste explicite de juges exigée
            self.jouer([a for a in self.args(externe=False) if a not in ("--juge", "juge-opus=" + OPUS)])


class TestMoteurReelSimuleDansLeCoeur(CasJugesSeulement):
    """Le cœur avec `moteur="claude-sdk"` (adaptateurs factices qui en portent les noms) : attestation et relais."""

    def plan(self, bascule=True):
        budgets = {("juge_ideation", OPUS): 1.0, ("juge_ideation", ARGON): 1.0, ("juge_ideation", REPLI): 1.0}
        return js.preparer_juges_seulement(self.course, empreinte_manifeste_fin=self.empreinte_fin,
                                           empreinte_fiches_validees=self.empreinte_fiches, liste_blanche=self.liste,
                                           question=self.question, pieces_juge=[self.piece_juge], temoins=self.temoins,
                                           juges=[("juge-opus", OPUS)], juges_externes=[("argon-juge", ARGON)],
                                           budgets=budgets, budget_total_usd=3.0, budget_externe_usd=1.2,
                                           bascules={OPUS: REPLI} if bascule else None)

    def attestation(self, plan, **modifs):
        a = {"lecteur": "Lazar", "lu_le": "2026-10-30", "fiches_validees_sha256": self.empreinte_fiches,
             "consignes_en_attente_sha256": {"argon-juge": plan["consignes"]["argon-juge"]["sha256"]}}
        a.update(modifs)
        chemin = os.path.join(self.tmp, f"attestation-{len(os.listdir(self.tmp))}.json")
        ecrire_json_scelle(chemin, a)
        return chemin

    def relais(self, **modifs):
        etat = {"plafond_usd": 20.0, "reserve_par_appel_usd": 4.0, "depense_usd": 0.0, "appels": 0,
                "modeles_permis": [OPUS, REPLI], "version_relais": "0.7.0",
                "bareme_modeles_permis": {OPUS: {}, REPLI: {}}}
        etat.update(modifs)
        compteur = {"n": 0}

        def lire():
            compteur["n"] += 1
            return dict(etat, appels=compteur["n"], depense_usd=etat["depense_usd"] + 0.01 * compteur["n"])
        return lire

    def jouer_coeur(self, plan, **kw):
        juge, ext = JugeScenario(nom="claude-sdk", **kw.pop("scenario", {})), JugeScenario(nom="commande-externe")
        return js.executer_juges_seulement(plan, self.sortie, juge, {"argon-juge": ext}, moteur="claude-sdk",
                                           exiger_attestation=True, exiger_modele_servi_claude=True, **kw)

    def test_attestation_exigee_et_verifiee(self):
        plan = self.plan()
        with self.assertRaisesRegex(js.JugesSeulementRefuse, "attestation de lecture humaine"):
            self.jouer_coeur(plan, lire_etat_relais=self.relais())
        with self.assertRaisesRegex(js.JugesSeulementRefuse, "consigne du juge externe"):
            self.jouer_coeur(plan, lire_etat_relais=self.relais(),
                             attestation_lecture_humaine=self.attestation(plan, consignes_en_attente_sha256={"argon-juge": "0" * 64}))
        with self.assertRaisesRegex(js.JugesSeulementRefuse, "fiches validées"):
            self.jouer_coeur(plan, lire_etat_relais=self.relais(),
                             attestation_lecture_humaine=self.attestation(plan, fiches_validees_sha256="1" * 64))
        self.assertFalse(os.path.exists(self.sortie))
        res = self.jouer_coeur(plan, lire_etat_relais=self.relais(), attestation_lecture_humaine=self.attestation(plan),
                               scenario={OPUS: "refus"})
        self.assertTrue(res["lisible"])
        self.assertEqual(res["journal"]["bascules"][0]["modele_servi"], REPLI)

    def test_relais_modeles_permis_exacts_et_v2(self):
        plan = self.plan()
        att = self.attestation(plan)
        for modifs, motif in (({"modeles_permis": [OPUS]}, "modèles permis"),
                              ({"modeles_permis": [OPUS, REPLI, FABLE]}, "modèles permis"),
                              ({"version_relais": None}, "relais v2 exigé"),
                              ({"bareme_modeles_permis": {OPUS: {}}}, "relais v2 exigé"),
                              ({"plafond_usd": 6.0}, "somme des plafonds Claude"),
                              ({"depense_usd": float("nan")}, "non fini")):
            with self.subTest(modifs=modifs):
                with self.assertRaisesRegex(js.JugesSeulementRefuse, motif):
                    self.jouer_coeur(plan, lire_etat_relais=self.relais(**modifs), attestation_lecture_humaine=att)
                self.assertFalse(os.path.exists(self.sortie))
        sans = self.plan(bascule=False)  # sans bascule : relais v1 accepté, modèles permis = Opus seul
        res = self.jouer_coeur(sans, lire_etat_relais=self.relais(modeles_permis=[OPUS], version_relais=None),
                               attestation_lecture_humaine=self.attestation(sans))
        self.assertTrue(res["lisible"])

    def test_modele_servi_non_lu_arret(self):
        plan = self.plan(bascule=False)

        class Muet(JugeScenario):
            def lancer(self, *a, **k):
                r = super().lancer(*a, **k)
                r.modele_servi = None
                return r
        with self.assertRaisesRegex(idn.CourseInterrompue, "modèle servi non lu"):
            js.executer_juges_seulement(plan, self.sortie, Muet(nom="claude-sdk"), {"argon-juge": JugeScenario(nom="commande-externe")},
                                        moteur="claude-sdk", exiger_modele_servi_claude=True,
                                        lire_etat_relais=self.relais(modeles_permis=[OPUS], version_relais=None),
                                        attestation_lecture_humaine=self.attestation(plan), exiger_attestation=True)

    def test_adaptateur_simule_refuse_sur_moteur_reel(self):
        plan = self.plan(bascule=False)
        with self.assertRaisesRegex(js.JugesSeulementRefuse, "commande externe"):
            js.executer_juges_seulement(plan, self.sortie, JugeScenario(nom="claude-sdk"), {"argon-juge": JugeScenario()},
                                        moteur="claude-sdk")


class FauxKitJuge:
    """Faux module du kit pour `AdaptateurClaudeSDKBascule` : par modèle demandé, un scénario de messages."""
    from essais.test_v7_ideation_v2 import FauxKitRefus as _K
    TextBlock, AssistantMessage, SystemMessage, ResultMessage, ClaudeSDKError = (
        _K.TextBlock, _K.AssistantMessage, _K.SystemMessage, _K.ResultMessage, _K.ClaudeSDKError)

    class ClaudeAgentOptions:
        def __init__(self, **reglages):
            self.__dict__.update(reglages)

    class HookMatcher:
        def __init__(self, matcher=None, hooks=()):
            self.matcher, self.hooks = matcher, list(hooks)

    def __init__(self, par_modele):
        self.par_modele, self.modeles = par_modele, []

    async def query(self, prompt, options):
        self.modeles.append(options.model)
        self.options = options
        mode = self.par_modele.get(options.model, "ok")
        if prompt.startswith(idn.APPEL_DE_CONTROLE_CONSIGNE):  # l'appel de contrôle rend « OK » (le refus vient au juge)
            yield self.AssistantMessage([self.TextBlock("OK")], options.model)
            yield self.ResultMessage("success", "OK", 0.01)
            return
        else:
            idents = sorted(set(re.findall(r'"identifiant": "(T\d\d)"', prompt)))
            texte = "```json\n" + json.dumps(notes_temoins_ok(idents, prompt)) + "\n```"
        if mode == "refus":
            yield self.AssistantMessage([], options.model, stop_reason="refusal")
            return
        if mode == "repli-kit":
            yield self.SystemMessage("model_refusal_fallback", {"fallback_model": REPLI})
            yield self.AssistantMessage([self.TextBlock(texte)], REPLI)
            return
        yield self.AssistantMessage([self.TextBlock(texte)], options.model)
        yield self.ResultMessage("success", texte, 0.4)


class TestAdaptateurDeBascule(CasJugesSeulement):
    def adaptateur(self, replis=(REPLI,)):
        return AdaptateurClaudeSDKBascule("http://127.0.0.1:8787", replis=replis, environnement={}, arme=True,
                                          interdire_lecture=[self.tmp], delai_s=30)

    def test_modeles_permis(self):
        self.assertEqual(verifier_modele_reel_ou_repli(REPLI, (REPLI,)), REPLI)
        with self.assertRaises(ModeleNonPermis):
            verifier_modele_reel_ou_repli(REPLI, ())
        with self.assertRaises(ModeleNonPermis):
            verifier_modele_reel_ou_repli(REPLI + "-mini", (REPLI,))  # noms exacts, jamais par préfixe
        with self.assertRaises(ModeleNonPermis):
            self.adaptateur(replis=("claude-sonnet-5-5",))
        sans_repli = self.adaptateur(replis=())
        with mock.patch("pole.adaptateurs_v2.importer_sdk", side_effect=AssertionError("jamais importé")):
            with self.assertRaises(ModeleNonPermis):
                sans_repli.lancer("juge_ideation", "x", self.sous_dossier("a"), 1.0, 2, modele=REPLI)

    def test_bascule_de_bout_en_bout_par_le_faux_kit(self):
        """Le cœur, l'adaptateur de bascule et le lecteur de refus du kit (inchangé) : refus d'Opus, session neuve sur 4.6."""
        kit = FauxKitJuge({OPUS: "refus"})
        plan = TestMoteurReelSimuleDansLeCoeur.plan(self)
        relais = TestMoteurReelSimuleDansLeCoeur.relais(self)
        att = TestMoteurReelSimuleDansLeCoeur.attestation(self, plan)
        with mock.patch("pole.adaptateurs_v2.importer_sdk", return_value=kit):
            res = js.executer_juges_seulement(plan, self.sortie, self.adaptateur(), {"argon-juge": JugeScenario(nom="commande-externe")},
                                              moteur="claude-sdk", lire_etat_relais=relais, attestation_lecture_humaine=att,
                                              exiger_attestation=True, exiger_modele_servi_claude=True)
        self.assertTrue(res["lisible"])
        self.assertEqual(kit.modeles, [REPLI, OPUS, OPUS, REPLI])  # contrôles (ordre trié), juge refusé, juge de repli
        self.assertIsNone(kit.options.fallback_model)
        b = res["journal"]["bascules"][0]
        self.assertEqual((b["refus_initial"]["evenement"], b["modele_servi"]), ("assistant.stop_reason", REPLI))

    def test_repli_du_kit_dans_la_session_arret(self):
        kit = FauxKitJuge({OPUS: "repli-kit"})
        plan = TestMoteurReelSimuleDansLeCoeur.plan(self)
        with mock.patch("pole.adaptateurs_v2.importer_sdk", return_value=kit):
            with self.assertRaisesRegex(idn.CourseInterrompue, "changement de modèle non déclaré"):
                js.executer_juges_seulement(plan, self.sortie, self.adaptateur(), {"argon-juge": JugeScenario(nom="commande-externe")},
                                            moteur="claude-sdk", lire_etat_relais=TestMoteurReelSimuleDansLeCoeur.relais(self),
                                            attestation_lecture_humaine=TestMoteurReelSimuleDansLeCoeur.attestation(self, plan),
                                            exiger_attestation=True, exiger_modele_servi_claude=True)
        self.assertEqual(kit.modeles, [REPLI, OPUS, OPUS])  # aucune session de repli ouverte


class TestRelaisV2(unittest.TestCase):
    def test_bareme_inconnu_borne_haute(self):
        from pole import relais_reel, relais_reel_v2
        self.assertEqual(relais_reel_v2.tarif_du_modele(REPLI), relais_reel_v2.BAREME_INCONNU)
        for v1, v2 in zip(relais_reel.BAREME_INCONNU, relais_reel_v2.BAREME_INCONNU):
            self.assertGreaterEqual(v2, v1)
        for tarif in relais_reel_v2.BAREME_USD_PAR_MILLION.values():  # chaque composante inconnue borne le barème connu
            self.assertTrue(all(i >= t for i, t in zip(relais_reel_v2.BAREME_INCONNU, tarif)))
        self.assertLess(relais_reel.BAREME_INCONNU[3], 0.5)  # la v1 : lecture de cache plus basse que 10 % d'une entrée à 5

    def test_relais_v2_en_processus(self):
        from essais.faux_sdk.amont_factice import CLE_FACTICE, AmontFactice
        from essais.test_v6_relais_reel import appeler
        amont = AmontFactice()
        self.addCleanup(amont.arreter)
        argv = [sys.executable, "-I", "-B", os.path.join(RACINE, "pole", "relais_reel_v2.py"), "--port", "0", "--amont", amont.url,
                "--plafond-usd", "1", "--reserve-par-appel", "0.001", "--modeles-permis", f"{OPUS},{REPLI}"]
        proc = subprocess.Popen(argv, env={"PATH": os.environ.get("PATH", ""), "ANTHROPIC_API_KEY": CLE_FACTICE},
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.addCleanup(lambda: (proc.kill(), proc.communicate(timeout=10)))
        ligne = proc.stdout.readline()
        self.assertTrue(ligne.startswith("relais prêt sur "), ligne)
        self.assertIn(REPLI, proc.stdout.readline())  # barème inconnu dit au démarrage
        url = ligne.split()[3]
        statut, _, octets = appeler(url, "/relais/etat", None, methode="GET")
        etat = json.loads(octets)
        self.assertEqual((statut, etat["version_relais"], etat["modeles_permis"]), (200, "0.7.0", [OPUS, REPLI]))
        self.assertTrue(etat["bareme_modeles_permis"][REPLI]["source"].startswith("inconnu"))
        statut, _, _ = appeler(url, "/v1/messages", {"model": REPLI, "messages": []})
        self.assertEqual(statut, 200)
        statut, _, octets = appeler(url, "/v1/messages", {"model": "claude-sonnet-5-5", "messages": []})
        self.assertEqual(statut, 403)
        statut, _, octets = appeler(url, "/relais/etat", None, methode="GET")
        etat = json.loads(octets)
        self.assertEqual((etat["appels"], etat["refus_modele"]), (2, 1))
        self.assertGreater(etat["depense_usd"], 0)
        self.assertEqual(len(amont.requetes), 1, "le modèle refusé n'atteint jamais l'amont")


if __name__ == "__main__":
    unittest.main()
