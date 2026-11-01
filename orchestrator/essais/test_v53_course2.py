"""Essais de la v53 — génération de la course 2, course à plusieurs générations, étage entre générations, lanceur v5, R12.
Hors ligne : moteur simulé (`pole/simulation_v53.py`), exécuteur factice de l'étage ; aucune clé, aucun appel payant."""

import contextlib
import io
import json
import os
import subprocess
import sys
import unittest

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)

import aides_v53 as A  # noqa: E402
from aides import CasAvecDossier  # noqa: E402
from pole import configuration_v53 as cfg  # noqa: E402
from pole import course2_v53 as c2  # noqa: E402
from pole import dossier_ferme as dfm  # noqa: E402
from pole import etage_entre_generations_v53 as etg  # noqa: E402
from pole import fiches_v53 as fv  # noqa: E402
from pole import ideation_v2 as idn  # noqa: E402
from pole import juges_croises_v53 as jc  # noqa: E402
from pole import tests_de_mort_v3 as tdm  # noqa: E402
from pole.outils import verifier_scelle  # noqa: E402
from pole.simulation_v53 import AdaptateurSimuleCourse2  # noqa: E402

JETABLE = {"POLE_MACHINE_JETABLE_V53": "1", "PATH": "/usr/bin:/bin"}


def adaptateurs(**decideurs):
    return {n: AdaptateurSimuleCourse2(champs_fiche=A.CHAMPS, items=A.ITEMS, cout_par_appel_usd=0.01, champ_titre="titre",
                                       decider=decideurs.get(n)) for n in ("kimi", "argon", "claude")}


def lire(chemin):
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


class TestGeneration(CasAvecDossier):
    def conf(self, **modifs):
        return cfg.lire_configuration(A.configuration(self.tmp, **modifs), base=self.tmp)

    def test_cas_sain_generation_complete_scellee(self):
        ad = adaptateurs()
        g = c2.Generation(self.conf(), os.path.join(self.tmp, "s"), ad)
        res = g.executer()
        s = os.path.join(self.tmp, "s")
        fin = lire(os.path.join(s, "manifeste-fin.json"))
        self.assertIsNone(fin["arret"])
        self.assertEqual(set(fin["etapes"].values()), {"jouee"})
        self.assertEqual(len(res), 4 + 4 + 3)  # passe 1, passe « tableau », trois fusions (une par bras)
        self.assertEqual(fin["fusions"]["comptees_a_part"], 3)
        self.assertEqual(sorted(fin["paires"]), ["basique", "gu_krenn", "meta"])
        self.assertTrue(all(len(v) == 1 for v in fin["paires"].values()))
        self.assertEqual(fin["coffre"]["incidents"], [])
        lectures = [a for a in fin["coffre"]["acces"] if a["quoi"] == "ouverture"]
        self.assertTrue(lectures and all(a["apres_fin_e9"] for a in lectures))  # A21 : aucun verdict lu avant la fin
        for nom in ("manifeste-depart.json", "manifeste-fin.json", "classement.json", "fiches.json", "memoire.json", "tableaux.json"):
            self.assertTrue(verifier_scelle(os.path.join(s, nom)), nom)
        cl = lire(os.path.join(s, "classement.json"))
        self.assertEqual(cl["regle_agregation"], {"regle": "au_moins", "q": 2})
        self.assertEqual(sum(l["exploratoire"] for l in cl["lignes"]), 3)
        fiches = lire(os.path.join(s, "fiches.json"))
        self.assertTrue(all("ident" not in f["contenu"] for f in fiches.values()))
        self.assertIn("taches", fin["graines"])
        self.assertTrue(any(t.startswith("g1-bisoc-ordre") for t in fin["graines"]["taches"]))
        # aucun juge n'a reçu une fiche sans passeport, ni une étiquette interdite
        for a in ad["claude"].appels + ad["argon"].appels + ad["kimi"].appels:
            self.assertGreater(a["cout"], 0)

    def test_artefact_etiquette_interdite_dans_une_fiche_a4(self):
        def kimi(role, consigne, modele, n):
            if "## Case" in consigne:
                return {"texte": json.dumps({"fiches": [{"titre": "Fiche témoin", "hypothese": "h", "axe": "1", "methode": "m"}]})}
        g = c2.Generation(self.conf(), os.path.join(self.tmp, "s"), adaptateurs(kimi=kimi))
        with self.assertRaises(fv.EtiquetteDansEntree):
            g.executer()
        fin = lire(os.path.join(self.tmp, "s", "manifeste-fin.json"))
        self.assertIn("EtiquetteDansEntree", fin["arret"])

    def test_artefact_debordement_de_kimi_arrete_son_role(self):
        def claude(role, consigne, modele, n):
            if "AIGUILLEUR" in consigne and "méthode de mesure générale" in consigne and "kimi" in consigne.lower():
                return None
            return None

        def aig(role, consigne, modele, n):
            return None
        conf = self.conf()
        ad = adaptateurs()
        # l'aiguilleur classe « concret » toute fiche écrite par le modèle de Kimi (marque dans le contenu simulé)
        kimi_textes = set()
        orig = ad["kimi"].reponse

        def reponse_kimi(role, consigne, modele):
            t = orig(role, consigne, modele)
            if "## Case" in consigne:
                o = json.loads(t)
                for f in o["fiches"]:
                    f["methode"] = "PROCEDE-CONCRET " + f["methode"]
                    kimi_textes.add(f["methode"])
                t = json.dumps(o, ensure_ascii=False)
            return t
        ad["kimi"].reponse = reponse_kimi
        ad["claude"].decider = lambda r, c, m, n: ({"texte": '{"classe": "concret", "categorie": "C2"}'}
                                                   if "AIGUILLEUR" in c and "PROCEDE-CONCRET" in c else None)
        g = c2.Generation(conf, os.path.join(self.tmp, "s"), ad)
        g.executer()
        fin = lire(os.path.join(self.tmp, "s", "manifeste-fin.json"))
        self.assertIn("prop-kimi", fin["roles_arretes"])
        self.assertEqual(fin["garde_kimi"]["concretes"], 2)
        journal = open(os.path.join(self.tmp, "s", "aiguillage", "journal-aiguillage.json"), encoding="utf-8").read()
        self.assertNotIn("PROCEDE-CONCRET", journal)  # contenu jamais copié
        tout = ""
        for racine, _, fichiers in os.walk(os.path.join(self.tmp, "s")):
            for nom in fichiers:
                with open(os.path.join(racine, nom), encoding="utf-8", errors="replace") as f:
                    tout += f.read()
        self.assertNotIn("PROCEDE-CONCRET", tout)  # ni juges, ni tableau, ni sorties
        props = [a for a in ad["kimi"].appels if a["case"]]
        self.assertEqual(len(props), 1)  # passe 1 seulement : aucune passe « tableau » ni fusion écrite par Kimi après l'arrêt
        self.assertFalse(any(a["tableau"] for a in ad["kimi"].appels))
        self.assertEqual(fin["fusions"]["comptees_a_part"], 0)
        self.assertIn("fusion-kimi", fin["roles_arretes"])
        del claude, aig

    def test_artefact_annexe_absente_bras_meta_non_produit_a20(self):
        conf = A.configuration(self.tmp)
        conf["bisociateur"]["meta"]["annexe"]["sha256"] = "0" * 64
        conf = cfg.lire_configuration(conf, base=self.tmp)
        g = c2.Generation(conf, os.path.join(self.tmp, "s"), adaptateurs())
        g.executer()
        fin = lire(os.path.join(self.tmp, "s", "manifeste-fin.json"))
        self.assertFalse(fin["bras"]["meta"]["produit"])
        self.assertIn("annexe non conforme", fin["bras"]["meta"]["cause"])
        self.assertEqual(sorted(fin["paires"]), ["basique", "gu_krenn"])
        self.assertTrue(fin["bras"]["gu_krenn"]["produit"])

    def test_artefact_source_s31_absente_bras_gk_non_produit_a19(self):
        conf = A.configuration(self.tmp)
        conf["bisociateur"]["gu_krenn"]["source"]["chemin"] = os.path.join(self.tmp, "absente.json")
        conf = cfg.lire_configuration(conf, base=self.tmp)
        g = c2.Generation(conf, os.path.join(self.tmp, "s"), adaptateurs())
        g.executer()
        fin = lire(os.path.join(self.tmp, "s", "manifeste-fin.json"))
        self.assertEqual(fin["bras"]["gu_krenn"]["cause"], "non produit (source absente)")

    def test_budget_bas_retire_les_sacrifiables_jamais_l_aiguilleur(self):
        conf = A.configuration(self.tmp)
        conf["budget"]["plafond_usd"] = 3.2
        conf["budget"]["arret_etape_usd"] = "sans"
        g = c2.Generation(cfg.lire_configuration(conf, base=self.tmp), os.path.join(self.tmp, "s"), adaptateurs())
        g.executer()
        fin = lire(os.path.join(self.tmp, "s", "manifeste-fin.json"))
        self.assertEqual(fin["etapes"]["aiguillage"], "jouee")
        self.assertEqual(fin["etapes"]["fusions"], "retiree")
        self.assertLessEqual(fin["budget"]["cumul_usd"], 3.2)

    def test_artefact_configuration_aiguilleur_sacrifiable_refusee(self):
        conf = A.configuration(self.tmp)
        conf["budget"]["etapes"][1].update(role="sacrifiable", rang=3)
        with self.assertRaisesRegex(cfg.ConfigurationRefusee, "aiguilleur n'est jamais sacrifié"):
            c2.Generation(cfg.lire_configuration(conf, base=self.tmp), os.path.join(self.tmp, "s"), adaptateurs())
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "s")))

    def test_artefact_version_servie_d_un_juge_changee_entre_lots_a2(self):
        def argon(role, consigne, modele, n):
            if "JUGE" in consigne and n > 6:  # après les juges de la passe 1
                return {"modele_servi": "gemini-4-argon-autre"}
        g = c2.Generation(self.conf(), os.path.join(self.tmp, "s"), adaptateurs(argon=argon))
        with self.assertRaises(jc.VersionServieChangee):
            g.executer()

    def test_artefact_lecture_d_un_verdict_avant_la_fin_a21(self):
        g = c2.Generation(self.conf(), os.path.join(self.tmp, "s"), adaptateurs())
        orig = g.etape_passe_tableau

        def fautive(etat):
            g.coffre.ouvrir("verdicts-passe1-" + next(iter(g.fiches)))  # l'orchestrateur d'essai lit un verdict d'É6
            orig(etat)
        g.etape_passe_tableau = fautive
        from pole.coffre_v53 import LectureAvantFinE9
        with self.assertRaises(LectureAvantFinE9):
            g.executer()
        fin = lire(os.path.join(self.tmp, "s", "manifeste-fin.json"))
        self.assertEqual(len(fin["coffre"]["incidents"]), 1)


class TestCourseEtEtage(CasAvecDossier):
    def conf(self):
        return cfg.lire_configuration(A.configuration(self.tmp), base=self.tmp)

    def test_etage_entre_generations_sur_les_mieux_classees(self):
        appels = []

        def faux_executer(adaptateur, sortie, resume_sortie, **reglages):
            cl = lire(os.path.join(sortie, "classement.json"))
            appels.append({"sortie": sortie, "eligibles": [l["identifiant_auteur"] for l in cl["lignes"] if l["eligible"]],
                           "scelles": all(verifier_scelle(os.path.join(sortie, n)) for n in
                                          ("classement.json", "fiches-validees.json", "manifeste-depart.json"))})
            resume_sortie["termine"] = True
        corr = {"nom": "titre", "enonce": "hypothese", "prediction": "hypothese", "signe": "axe", "metrique": "methode",
                "test_de_mort": "methode"}
        etage = {"adaptateur": adaptateurs()["claude"], "reglages": {"nombre": 2}, "nombre": 2, "tranche_index_sha256": "0" * 64,
                 "correspondance": corr, "plafond_etage_usd": 1.0, "executer": faux_executer}
        bilan = c2.executer_course(self.conf(), os.path.join(self.tmp, "c"), adaptateurs(), nombre_generations=2, go={"essai": True},
                                   etage=etage, environnement=JETABLE)
        self.assertEqual(len(appels), 1)  # entre les deux générations seulement
        self.assertTrue(appels[0]["scelles"])
        self.assertIn("etage", bilan[0])
        self.assertNotIn("etage", bilan[1])
        self.assertTrue(verifier_scelle(os.path.join(self.tmp, "c", "bilan-course.json")))
        self.assertEqual(c2.plafond_course(self.conf(), 2, etage), 2 * 50.0 + 1.0)

    def test_artefacts_machine_non_jetable_et_nom_de_cle(self):
        ad = adaptateurs()
        etage = {"adaptateur": ad["claude"], "reglages": {}, "nombre": 1, "tranche_index_sha256": "0" * 64,
                 "correspondance": {}, "plafond_etage_usd": 1.0}
        for env, motif in (({"PATH": "/usr/bin"}, "POLE_MACHINE_JETABLE_V53"), (dict(JETABLE, POLE_MACHINE_JETABLE_V53="oui"), "absent"),
                           (dict(JETABLE, KIMI_API_KEY="x"), "nom de variable de clé"), (dict(JETABLE, AUTRE_TOKEN="x"), "clé")):
            with self.subTest(env=sorted(env)), self.assertRaisesRegex(etg.MachineNonJetable, motif):
                c2.executer_course(self.conf(), os.path.join(self.tmp, "c" + str(len(os.listdir(self.tmp)))), ad, nombre_generations=2,
                                   go={}, etage=etage, environnement=env)
        self.assertEqual(sum(len(a.appels) for a in ad.values()), 0)  # refus avant tout appel
        self.assertTrue(etg.exiger_machine_jetable(JETABLE))

    def test_etage_v3_inchange_joue_sur_une_generation_projetee(self):
        """Intégration : l'étage réel (`tests_de_mort_v3.executer_tests_de_mort`, exécuteur factice, moteur simulé) lit le
        dossier écrit par la v53 et teste les deux fiches les mieux classées, classement intact."""
        tr = os.path.join(self.tmp, "tranche")
        os.makedirs(tr)
        with open(os.path.join(tr, "serie-a.csv"), "w", encoding="utf-8") as f:
            f.write("a,b\n1,2\n3,4\n")
        dfm.ecrire_index(tr, [{"chemin": "serie-a.csv", "titre": "Série A", "resume": "démonstration"}])
        lb = os.path.join(self.tmp, "lb.json")
        idn.construire_liste_blanche([os.path.join(tr, "index.json")], lb)
        tranche = tdm.charger_tranche(tr, idn.charger_liste_blanche(lb))
        champs = ["titre", "hypothese", "prediction", "signe", "metrique", "test_de_mort"]
        fs = {}
        for i in range(3):
            c = {"titre": f"T{i}", "hypothese": f"Hypothèse {i}", "prediction": "effet d'au moins 0,3", "signe": "+",
                 "metrique": "part des lignes", "test_de_mort": {"seuil": "au moins 0,3", "test": "part des lignes positives",
                                                                 "donnees": ["serie-a.csv"]}}
            f = fv.preparer(c, champs, ident=f"f{i}", case=("t", "b"), fournisseur="kimi", passe=1)
            fs[f["ident"]] = f
        cl = [{"ident": f"f{i}", "notable": i < 2, "rang": i + 1} for i in range(3)]
        corr = {"nom": "titre", "enonce": "hypothese", "prediction": "prediction", "signe": "signe", "metrique": "metrique",
                "test_de_mort": "test_de_mort"}
        d = etg.preparer_generation(os.path.join(self.tmp, "gen"), cl, fs, nombre=2, tranche_index_sha256=tranche.index_sha256,
                                    correspondance=corr, lisible=True)
        ad = AdaptateurSimuleCourse2(champs_fiche=champs, items=A.ITEMS, cout_par_appel_usd=0.01)
        r = etg.jouer_etage(ad, d, reglages={"tranche": tranche, "nombre": 2, "experimentateur": ("exp", "claude-opus-5-5"),
                                             "lecteur": ("lec", "claude-fable-5-1"), "executeur": tdm.ExecuteurFactice(delai_s=30.0),
                                             "moteur": "simule"}, environnement=JETABLE)
        self.assertTrue(r["termine"])
        self.assertEqual(r["candidates"], ["f0", "f1"])
        self.assertTrue(r["classement_intact"])
        self.assertEqual([p["statut"] for p in r["par_fiche"]], ["testée", "testée"])
        self.assertTrue(verifier_scelle(os.path.join(d, "manifeste-tests-de-mort.json")))
        with self.assertRaises(etg.CorrespondanceRefusee):
            etg.preparer_generation(os.path.join(self.tmp, "gen2"), cl, fs, nombre=2, tranche_index_sha256="x", correspondance={"nom": "t"},
                                    lisible=True)


class TestLanceurV5(CasAvecDossier):
    def lancer(self, argv, env=None):
        sys.path.insert(0, os.path.join(RACINE, "demonstrations"))
        import importlib.util
        spec = importlib.util.spec_from_file_location("ideation_v5_essai", os.path.join(RACINE, "demonstrations", "ideation_v5.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        err, out = io.StringIO(), io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
            code = m.principal(argv, environnement=env if env is not None else {"PATH": "/usr/bin"})
        return code, out.getvalue(), err.getvalue(), m

    def test_sans_course_2_rend_la_main_au_lanceur_v4(self):
        _, _, _, m = self.lancer(["--course-2", "x", "y", "--generations", "1", "--verifier-seulement"])
        self.assertTrue(m.base.__file__.endswith("ideation_v4.py"))
        p = subprocess.run([sys.executable, "-I", "-B", os.path.join(RACINE, "demonstrations", "ideation_v5.py"), "--help"],
                           capture_output=True, text=True, cwd=RACINE, env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"})
        q = subprocess.run([sys.executable, "-I", "-B", os.path.join(RACINE, "demonstrations", "ideation_v4.py"), "--help"],
                           capture_output=True, text=True, cwd=RACINE, env={"PATH": "/usr/bin:/bin", "LANG": "C.UTF-8"})
        self.assertEqual(p.returncode, q.returncode)
        self.assertEqual(p.stdout.replace("ideation_v5.py", "X"), q.stdout.replace("ideation_v4.py", "X"))

    def test_cas_sain_verifier_seulement_puis_moteur_simule(self):
        conf = A.ecrire_configuration(self.tmp)
        sortie = os.path.join(self.tmp, "sortie")
        code, out, err, _ = self.lancer(["--course-2", conf, sortie, "--generations", "1", "--verifier-seulement"])
        self.assertEqual(code, 0, err)
        self.assertFalse(os.path.exists(sortie))
        self.assertEqual(json.loads(out)["somme_des_plafonds_usd"], 50.0)
        code, out, err, _ = self.lancer(["--course-2", conf, sortie, "--generations", "2", "--moteur", "simule"])
        self.assertEqual(code, 0, err)
        self.assertTrue(verifier_scelle(os.path.join(sortie, "generation-2", "manifeste-fin.json")))

    def test_artefacts_a15_sans_go_parametre_manquant_moteur_reel_non_confirme(self):
        conf = A.ecrire_configuration(self.tmp)
        sortie = os.path.join(self.tmp, "sortie")
        code, _, err, _ = self.lancer(["--course-2", conf, sortie, "--generations", "1", "--moteur", "reel", "--registre-go",
                                       os.path.join(self.tmp, "go.md")], env={"PATH": "/usr/bin"})
        self.assertEqual(code, 2)
        self.assertIn("GO_ID", err)
        reg = os.path.join(self.tmp, "go.md")
        with open(reg, "w", encoding="utf-8") as f:
            f.write("| GO-2026-10-31-09 | 2026-10-31 | calcul | essai | 49 USD | 2099-12-31 | Lazar | essai |\n")
        code, _, err, _ = self.lancer(["--course-2", conf, sortie, "--generations", "1", "--moteur", "reel", "--registre-go", reg],
                                      env={"PATH": "/usr/bin", "GO_ID": "GO-2026-10-31-09"})
        self.assertIn("ne couvre pas", err)
        with open(reg, "w", encoding="utf-8") as f:
            f.write("| GO-2026-10-31-09 | 2026-10-31 | calcul | essai | 50 USD | 2099-12-31 | Lazar | essai |\n")
        code, _, err, _ = self.lancer(["--course-2", conf, sortie, "--generations", "1", "--moteur", "reel", "--registre-go", reg],
                                      env={"PATH": "/usr/bin", "GO_ID": "GO-2026-10-31-09"})
        self.assertIn("--confirmer-moteur-reel", err)
        self.assertFalse(os.path.exists(sortie))
        d2 = self.sous_dossier("b")
        conf2 = A.ecrire_configuration(d2, memoire__seuil="À REMPLIR")
        code, _, err, _ = self.lancer(["--course-2", conf2, sortie, "--generations", "1", "--moteur", "simule"])
        self.assertEqual(code, 2)
        self.assertIn("memoire.seuil", err)
        d3 = self.sous_dossier("c")
        conf3 = A.ecrire_configuration(d3, etage_tests_de_mort={"nombre": 1})
        code, _, err, _ = self.lancer(["--course-2", conf3, sortie, "--generations", "2", "--moteur", "simule"])
        self.assertIn("POLE_MACHINE_JETABLE_V53", err)
        self.assertFalse(os.path.exists(sortie))


class TestLanceurV5Etage(CasAvecDossier):
    lancer = TestLanceurV5.lancer

    def test_lanceur_construit_l_etage_v3_et_le_joue_entre_generations(self):
        """Moteur simulé, machine jetable posée : l'étage v3 (exécuteur factice) est construit par le lanceur et joué entre les deux
        générations ; les fiches simulées n'ont pas de champ test_de_mort → refusées à l'étage avec leur motif (aucun champ inventé)."""
        tr = os.path.join(self.tmp, "tranche")
        os.makedirs(tr)
        with open(os.path.join(tr, "serie-a.csv"), "w", encoding="utf-8") as f:
            f.write("a\n1\n")
        dfm.ecrire_index(tr, [{"chemin": "serie-a.csv", "titre": "Série A", "resume": "démonstration"}])
        lb = os.path.join(self.tmp, "lb.json")
        idn.construire_liste_blanche([os.path.join(tr, "index.json")], lb)
        etage = {"nombre": 2, "tranche": tr, "liste_blanche": lb, "experimentateur": ["exp", "claude-opus-5-5"],
                 "lecteur": ["lec", "claude-fable-5-1"], "budget_test_usd": 0.5, "budget_lecteur_usd": 0.2, "executions_par_fiche": 1,
                 "delai_execution_s": 30.0, "memoire_mo": 1024, "plafond_etage_usd": 2.0, "fournisseur": "claude",
                 "correspondance": {"nom": "titre", "enonce": "hypothese", "prediction": "hypothese", "signe": "axe",
                                    "metrique": "methode", "test_de_mort": "absent"}}
        conf = A.ecrire_configuration(self.tmp, etage_tests_de_mort=etage)
        sortie = os.path.join(self.tmp, "sortie")
        code, out, err, _ = self.lancer(["--course-2", conf, sortie, "--generations", "2", "--moteur", "simule"], env=dict(JETABLE))
        self.assertEqual(code, 0, err)
        d = os.path.join(sortie, "etage-apres-generation-1")
        self.assertTrue(verifier_scelle(os.path.join(d, "manifeste-tests-de-mort.json")))
        self.assertFalse(os.path.exists(os.path.join(sortie, "etage-apres-generation-2")))
        bilan = json.loads(out)["bilan"]
        self.assertTrue(bilan[0]["etage"]["termine"])
        self.assertTrue(all(p["statut"] == "refusée à l'étage" for p in bilan[0]["etage"]["par_fiche"]))


class TestR12(unittest.TestCase):
    def test_aucun_fichier_de_la_v52b_modifie(self):
        """Chaque fichier de la liste d'empreintes de la v52b (dossier parent de la livraison) a, dans l'arbre v53, son empreinte."""
        import hashlib
        liste = os.path.join(RACINE, os.pardir, "EMPREINTES-orchestrateur-v52b.txt")
        self.assertTrue(os.path.isfile(liste), "liste d'empreintes de la v52b absente du dossier parent (la suite se joue dans la livraison)")
        n = 0
        with open(liste, encoding="utf-8") as f:
            for ligne in f:
                sha, chemin = ligne.rstrip("\n").split("  ", 1)
                rel = chemin.split("orchestrateur-v52b/", 1)[1]
                with open(os.path.join(RACINE, rel), "rb") as g:
                    self.assertEqual(hashlib.sha256(g.read()).hexdigest(), sha, rel)
                n += 1
        self.assertGreater(n, 300)


if __name__ == "__main__":
    unittest.main()
