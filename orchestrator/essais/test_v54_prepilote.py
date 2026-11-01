"""Essais de la v54 — pré-pilote (étapes É1 à É9b du brouillon 7), gardes A3, A5 à A8, A11, A13, A14, rejeu de la table R5 à
É0, squelettes qui refusent, lanceur v6, R12. Hors ligne ; moteur simulé v54 ; horloge injectée ; aucune clé."""

import contextlib
import hashlib
import io
import json
import os
import sys
import unittest

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)

import aides_v54 as A  # noqa: E402
from aides import CasAvecDossier  # noqa: E402
from pole import budget_v54 as bv  # noqa: E402
from pole import configuration_v54 as cfg  # noqa: E402
from pole import course2_v54 as c2  # noqa: E402
from pole import fiches_v54 as fv  # noqa: E402
from pole import gardes_e0_v54 as ge  # noqa: E402
from pole import prepilote_v54 as pp  # noqa: E402
from pole.noyau_v54 import NoeudArret  # noqa: E402
from pole.suivi_roles_v54 import BasculeInterdite  # noqa: E402

EXTERNES = ("8", "9", "10", "17", "19")


def lire(chemin):
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


class Horloge:
    """Horloge d'essai : chaque lecture avance d'un pas ; `retards` ajoute une durée à certains appels."""

    def __init__(self):
        self.t = 0.0

    def __call__(self):
        self.t += 0.001
        return self.t


def avec_externes(dossier, conf):
    for n in EXTERNES:
        conf["pieces"][f"garde_{n}"] = A.ecrire(os.path.join(dossier, "ext", f"g{n}.json"),
                                                json.dumps({"ligne": n, "cas_sain": "passe", "artefact": "arrete", "script_sha256": "f" * 64}))
    conf["prepilote"]["gardes_externes"] = {n: f"garde_{n}" for n in EXTERNES}
    return conf


class Base(CasAvecDossier):
    def conf(self, **modifs):
        return cfg.lire_configuration_v54(avec_externes(self.tmp, A.configuration_pre_pilote(self.tmp, **modifs)), base=self.tmp)

    def pp(self, conf=None, ad=None, **kw):
        kw.setdefault("etage1", A.EtageUnFactice())
        return pp.PrePiloteV54(conf or self.conf(), os.path.join(self.tmp, "s"), ad or A.adaptateurs(), **kw)

    def fin(self):
        return lire(os.path.join(self.tmp, "s", "manifeste-fin.json"))


class TestPrePiloteSain(Base):
    def test_cas_sain_toutes_les_etapes(self):
        ad = A.adaptateurs()
        g = self.pp(ad=ad)
        res = g.executer()
        fin = self.fin()
        self.assertEqual(list(fin["etapes"]), list(pp.PLAN))
        self.assertEqual(set(fin["etapes"].values()), {"jouee"})
        self.assertIsNone(fin["noeud"])
        self.assertEqual((fin["fonds"], fin["rendus"]), (10, 10))
        self.assertEqual(fin["e5"]["s18"]["aire"], None)  # 2 fiches de Kimi < 6 : non évaluée (réserve)
        self.assertTrue(res["temoins_primaires_juges"] > 0)
        acces = [a["quoi"] for a in fin["coffre"]["acces"]]
        fin_e9 = acces.index("fin_e9")
        depots = [a["nom"] for a in fin["coffre"]["acces"][:fin_e9] if a["quoi"] == "depot"]
        self.assertTrue(any(n.startswith("verdicts-e9b-") for n in depots))  # fin de la phase de mesure après É9b
        self.assertTrue(all(a["apres_fin_e9"] for a in fin["coffre"]["acces"] if a["quoi"] == "ouverture"))
        self.assertTrue(any(e["evenement"] == "m6b-fiche-arretee" and e["ident"] == "m1" for e in fin["evenements"]))  # ligne 31
        self.assertFalse(os.path.exists(os.path.join(g.coffre.dossier, "verdicts-e9b-m1.json")))
        cle = g.coffre.ouvrir("pp2-cle-classes")
        compte = {}
        for v in cle.values():
            compte[v["classe"]] = compte.get(v["classe"], 0) + 1
            compte["m-" + v["metteur"]] = compte.get("m-" + v["metteur"], 0) + 1
        self.assertEqual(compte, {"P": 4, "N1": 2, "N2": 2, "C": 1, "G": 1, "m-kimi": 3, "m-argon": 3, "m-tiers": 4})
        taches = set(fin["graines"]["taches"])
        self.assertTrue({"pp2-classes-axes", "pp2-indices", "pp2-fournisseurs", "pp2-partition", "pp2-bisoc-ordre"} <= taches)
        squelettes = lire(os.path.join(self.tmp, "s", "temoins", "squelettes.json"))
        self.assertNotIn("classe", json.dumps(squelettes))
        cons = g.coffre.consommations()
        b = g.conf["budget"]
        dec, _ = bv.rejouer_consommations(b["plafond_usd"], b["arret_etape_usd"], b["etapes"], cons)
        self.assertEqual(dec, g.budget.decisions())
        self.assertEqual(len([c for c in cons if c["role"] not in ("coupure", "a14")]), sum(len(x.appels) for x in ad.values()))

    def test_m6_reduite_par_la_regle_d_a1(self):
        conf = A.configuration_pre_pilote(self.tmp)
        e9 = next(e for e in conf["budget"]["etapes"] if e["nom"] == "e9_anteriorite")
        e9.update(attendu_usd=58.0, reservation_usd=65.0)  # la projection dépasse S17 = 60 : fusions retirées (rang 1), M6 réduite (rang 2)
        g = self.pp(cfg.lire_configuration_v54(avec_externes(self.tmp, conf), base=self.tmp))
        g.executer()
        fin = self.fin()
        self.assertTrue(fin["budget"]["etapes"]["e9_anteriorite"]["reduite"])
        self.assertEqual(fin["etapes"]["e7c_fusions"], "retiree")
        self.assertEqual(fin["etapes"]["e9_anteriorite"], "jouee")
        self.assertTrue(any(e["evenement"] == "e9-reduite" and e["fiches"] == 2 for e in fin["evenements"]))
        self.assertIn("pp2-reduction-e9", fin["graines"]["taches"])


class TestGardesTemoins(Base):
    def _metteur(self, transforme):
        ad = A.adaptateurs()
        for x in ad.values():
            orig = x.reponse

            def rep(role, consigne, modele, orig=orig):
                t = orig(role, consigne, modele)
                return transforme(t) if "## Éléments à mettre en forme" in consigne else t
            x.reponse = rep
        return ad

    def test_artefact_a5_ancres_perdues_refait_puis_exclu_puis_arret(self):
        def perd(t):
            o = json.loads(t)
            o["fiches"][0]["methode"] = o["fiches"][0]["methode"].replace("ancre-", "ANCRE MODIFIÉE ")
            return json.dumps(o, ensure_ascii=False)
        g = self.pp(ad=self._metteur(perd))
        with self.assertRaisesRegex(NoeudArret, "A5"):
            g.executer()
        fin = self.fin()
        self.assertEqual(fin["etapes"]["e3_rendus"], "jouee")
        self.assertNotIn("e4_aiguillage", fin["etapes"])
        self.assertTrue(sum(1 for e in fin["evenements"] if e["evenement"] == "rendu-refait") >= 3)
        self.assertTrue(all("A5" in m for m in fin["exclus"].values()))

    def test_artefact_a8_rendu_trop_court(self):
        def court(t):
            o = json.loads(t)
            o["fiches"][0]["methode"] = o["fiches"][0]["methode"][:2500]
            return json.dumps(o, ensure_ascii=False)
        g = self.pp(ad=self._metteur(court))
        with self.assertRaises(NoeudArret):
            g.executer()
        self.assertTrue(any("A8" in m for m in self.fin()["exclus"].values()))

    def test_artefact_a6_ambigus_arret_avant_les_juges(self):
        ad = A.adaptateurs()
        ad["claude"].decider = lambda r, c, m, n: ({"texte": json.dumps({"notable": True, "item": None, "defaut_present": True})}
                                                   if "RELECTEUR" in c else None)
        g = self.pp(ad=ad)
        with self.assertRaisesRegex(NoeudArret, "A6"):
            g.executer()
        fin = self.fin()
        self.assertNotIn("e6_juges", fin["etapes"])
        self.assertIn("É5bis", fin["noeud"])
        self.assertFalse(any(c["role"].startswith("juge-") for c in g.coffre.consommations()))  # aucun juge appelé

    def test_artefact_a7_s19_forme_lisible(self):
        conf = A.configuration_pre_pilote(self.tmp)
        conf["prepilote"]["controles_forme"]["s19_aire_max"] = 0.65
        ad = A.adaptateurs()
        for x in ad.values():  # tous les metteurs : P longues, N courtes (par la présence d'un couple de défaut)
            o = x.reponse

            def rep(role, consigne, modele, o=o):
                t = o(role, consigne, modele)
                if "## Éléments à mettre en forme" in consigne:
                    f = json.loads(t)
                    m = f["fiches"][0]["methode"]
                    f["fiches"][0]["methode"] = m[:3600] if "defaut-a-" in consigne else m + "x" * 2500
                    t = json.dumps(f, ensure_ascii=False)
                return t
            x.reponse = rep
        g = self.pp(cfg.lire_configuration_v54(avec_externes(self.tmp, conf), base=self.tmp), ad)
        with self.assertRaisesRegex(NoeudArret, "A7 : S19"):
            g.executer()

    def test_seconde_version_de_temoins_epuisee(self):
        conf = A.configuration_pre_pilote(self.tmp)
        conf["prepilote"]["temoins"]["version"] = 2
        ad = A.adaptateurs()
        ad["claude"].decider = lambda r, c, m, n: ({"texte": json.dumps({"notable": True, "item": None, "defaut_present": True})}
                                                   if "RELECTEUR" in c else None)
        g = self.pp(cfg.lire_configuration_v54(avec_externes(self.tmp, conf), base=self.tmp), ad)
        with self.assertRaisesRegex(NoeudArret, "C5 non satisfaite"):
            g.executer()

    def test_artefact_a13_squelettes_modifies(self):
        g = self.pp()
        orig = g.etape_e3_rendus

        def fautif(etat):
            with open(os.path.join(self.tmp, "s", "temoins", "squelettes.json"), "a", encoding="utf-8") as f:
                f.write(" ")
            orig(etat)
        g.etape_e3_rendus = fautif
        with self.assertRaisesRegex(NoeudArret, "A13"):
            g.executer()


class TestA3A11A14(Base):
    def test_artefact_a3_echecs_consecutifs_puis_a14(self):
        ad = A.adaptateurs()
        ad["claude"].decider = lambda r, c, m, n: ({"statut": "erreur"} if "JUGE" in c and m == "claude-opus-5-5" else None)
        g = self.pp(ad=ad)
        g.executer()
        fin = self.fin()
        r = fin["suivi_roles"]["roles"]["juge-opus"]
        self.assertIn("A3", r["arrete"])
        self.assertEqual(r["appels"], 3)
        self.assertGreater(g.appels_sautes["juge-opus"], 0)
        self.assertEqual(fin["etapes"]["e6_juges"], bv.NON_MESUREE_TECHNIQUE)
        self.assertIn("C13", fin["noeud"])
        self.assertNotIn("e7a_passe_tableau", fin["etapes"])
        self.assertTrue(any(c.get("technique") for c in g.coffre.consommations()))

    def test_artefact_a3_appel_coupe_par_le_delai(self):
        h = Horloge()
        ad = A.adaptateurs()

        def lent(r, c, m, n):
            if "RELECTEUR" in c:
                h.t += 400.0  # au-delà des 300 s du fournisseur « * »
            return None
        ad["claude"].decider = lent
        g = self.pp(ad=ad, horloge=h)
        with self.assertRaisesRegex(NoeudArret, "A6"):  # relecteur arrêté : tous les témoins ambigus, arrêt avant les juges
            g.executer()
        r = self.fin()["suivi_roles"]["roles"]["relecteur"]
        self.assertEqual(r["coupes"], 3)
        self.assertIn("A3", r["arrete"])

    def test_cas_sain_a14_dix_pour_cent_continue(self):
        ad = A.adaptateurs()
        vu = {"n": 0}

        def un_sur_dix(r, c, m, n):
            if "JUGE" in c and m == "gemini-4-argon":
                vu["n"] += 1
                if vu["n"] == 5:
                    return {"texte": "illisible"}
        ad["argon"].decider = un_sur_dix
        g = self.pp(ad=ad)
        g.executer()
        fin = self.fin()
        r = fin["suivi_roles"]["roles"]["juge-argon"]
        self.assertEqual(r["inexploitables"], 1)
        self.assertLessEqual(r["inexploitables"] / r["appels"], 0.10)
        self.assertEqual(fin["etapes"]["e6_juges"], "jouee")

    def test_artefact_a11_refus_compte_limite_attente_sans_bascule(self):
        ad = A.adaptateurs()
        vu = {"n": 0}

        def opus(r, c, m, n):
            if "JUGE" in c and m == "claude-opus-5-5":
                vu["n"] += 1
                return {"statut": "refus"} if vu["n"] == 1 else ({"statut": "limite"} if vu["n"] == 2 else None)
        ad["claude"].decider = opus
        g = self.pp(ad=ad)
        g.executer()
        r = self.fin()["suivi_roles"]["roles"]["juge-opus"]
        self.assertEqual(r["refus_a11"], 2)
        self.assertIn("A11", r["arrete"])
        ad2 = A.adaptateurs()
        ad2["claude"].decider = lambda r_, c, m, n: ({"modele_servi": "claude-opus-4-6"} if "JUGE" in c and m == "claude-opus-5-5" else None)
        os.rename(os.path.join(self.tmp, "s"), os.path.join(self.tmp, "s-1"))
        with self.assertRaises(BasculeInterdite):
            self.pp(ad=ad2).executer()


class TestSquelettesEtConfiguration(Base):
    def test_etage_1_absent_refus(self):
        with self.assertRaisesRegex(pp.EtageUnAbsent, "DEP3"):
            pp.PrePiloteV54(self.conf(), os.path.join(self.tmp, "s"), A.adaptateurs(), etage1=None)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "s")))

    def test_lots_du_bras_d_attaque_refuses(self):
        with self.assertRaisesRegex(cfg.ConfigurationRefusee, "bras d'attaque"):
            self.pp(cfg.lire_configuration_v54(avec_externes(self.tmp, A.configuration_pre_pilote(self.tmp, prepilote__concrets="lot")),
                                               base=self.tmp))

    def test_plan_et_roles_imposes(self):
        conf = A.configuration_pre_pilote(self.tmp, prepilote__d_g="a")
        with self.assertRaisesRegex(cfg.ConfigurationRefusee, "plan exigé"):
            self.pp(cfg.lire_configuration_v54(conf, base=self.tmp))
        conf = A.configuration_pre_pilote(self.tmp)
        conf["budget"]["etapes"][3]["role"] = "sacrifiable"
        conf["budget"]["etapes"][3]["rang"] = 9
        with self.assertRaisesRegex(cfg.ConfigurationRefusee, "e4_aiguillage doit être « protegee »"):
            self.pp(cfg.lire_configuration_v54(conf, base=self.tmp))
        with self.assertRaisesRegex(cfg.ConfigurationRefusee, "prepilote.L1"):
            self.pp(cfg.lire_configuration_v54(A.configuration_pre_pilote(self.tmp, prepilote__L1="À REMPLIR"), base=self.tmp))


class TestGardesE0(Base):
    def test_course_toutes_les_lignes_rejouees(self):
        conf = cfg.lire_configuration_v54(A.configuration(self.tmp), base=self.tmp)
        decl, params = c2.declarer_bras_v54(conf)
        t = ge.rejouer_gardes(conf, decl, params)
        self.assertEqual({x["ligne"] for x in t if x["statut"] == "rejouée"}, set(ge.LIGNES_COURSE) | {"4"})

    def test_pre_pilote_externes_exigees(self):
        conf = self.conf()
        decl, params = c2.declarer_bras_v54(conf)
        t = ge.rejouer_gardes(conf, decl, params, plan="pre_pilote", etage1=A.EtageUnFactice())
        self.assertTrue(all(x["statut"] == "rejouée" for x in t))
        self.assertEqual({x["ligne"] for x in t} >= set(ge.LIGNES_PRE_PILOTE), True)
        conf2 = cfg.lire_configuration_v54(A.configuration_pre_pilote(self.tmp), base=self.tmp)
        with self.assertRaisesRegex(ge.GardesE0Refusees, "ligne 9"):
            ge.rejouer_gardes(conf2, decl, params, plan="pre_pilote", etage1=A.EtageUnFactice())
        with self.assertRaisesRegex(ge.GardesE0Refusees, "ligne 6 \\(non rejouée"):
            ge.rejouer_gardes(conf, decl, params, plan="pre_pilote", etage1=None)

    def test_artefact_garde_neutralisee_echec_a_e0(self):
        conf = cfg.lire_configuration_v54(A.configuration(self.tmp), base=self.tmp)
        decl, params = c2.declarer_bras_v54(conf)
        orig = fv.trouver
        fv.trouver = lambda *a, **k: []
        try:
            with self.assertRaisesRegex(ge.GardesE0Refusees, "ligne 2 \\(ÉCHEC"):
                ge.rejouer_gardes(conf, decl, params)
        finally:
            fv.trouver = orig


class TestLanceurV6(CasAvecDossier):
    def lancer(self, argv, env=None, etage1=None):
        import importlib.util
        spec = importlib.util.spec_from_file_location("ideation_v6_essai", os.path.join(RACINE, "demonstrations", "ideation_v6.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        err, out = io.StringIO(), io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
            code = m.principal(argv, environnement=env if env is not None else {"PATH": "/usr/bin"}, etage1=etage1)
        return code, out.getvalue(), err.getvalue(), m

    def ecrire_conf(self, conf, nom="conf.json"):
        chemin = os.path.join(self.tmp, nom)
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(conf, f, ensure_ascii=False)
        return chemin

    def test_sans_option_rend_la_main_au_lanceur_v5(self):
        _, _, _, m = self.lancer(["--course-2", "x", "y", "--generations", "1", "--verifier-seulement"])
        self.assertTrue(m.base.__file__.endswith("ideation_v5.py"))

    def test_course_verifier_simule_et_a15(self):
        conf = A.configuration(self.tmp, budget__plafond_usd=45.0, budget__arret_etape_usd=40.0)
        ch = self.ecrire_conf(conf)
        sortie = os.path.join(self.tmp, "sortie")
        code, out, err, _ = self.lancer(["--course-2", ch, sortie, "--generations", "1", "--verifier-seulement"])
        self.assertEqual(code, 0, err)
        o = json.loads(out)
        self.assertEqual(o["montant_requis_go_usd"], 45.0)
        self.assertTrue(all(x["statut"] == "rejouée" for x in o["table_r5_e0"]))
        self.assertFalse(os.path.exists(sortie))
        code, out, err, _ = self.lancer(["--course-2", ch, sortie, "--generations", "1", "--moteur", "simule"])
        self.assertEqual(code, 0, err)
        reel = ["--course-2", ch, sortie, "--generations", "1", "--moteur", "reel", "--registre-go"]
        code, _, err, _ = self.lancer(reel + [A.registre_go(self.tmp, A.ligne_go("GO-2026-10-31-09", "45 USD"))],
                                      env={"PATH": "/usr/bin", "GO_ID": "GO-2026-10-31-09"})
        self.assertEqual(code, 2)
        self.assertIn("confirmation de DEP4", err)
        conf["pieces"]["dep4"] = A.ecrire(os.path.join(self.tmp, "p", "dep4.md"), "Confirmation DEP4 (essai).")
        conf["dependances"] = {"dep4": "dep4"}
        ch2 = self.ecrire_conf(conf, "conf2.json")
        reel2 = ["--course-2", ch2, os.path.join(self.tmp, "sortie2"), "--generations", "1", "--moteur", "reel", "--registre-go"]
        for plafond, motif in (("150 USD", "plus grand"), ("10 USD par lancement, dans les 150 USD", "plusieurs montants"),
                               ("45 USD", "--confirmer-moteur-reel")):
            with self.subTest(plafond):
                d = self.sous_dossier(plafond[:6].replace(" ", "_"))
                code, _, err, _ = self.lancer(reel2 + [A.registre_go(d, A.ligne_go("GO-2026-10-31-09", plafond))],
                                              env={"PATH": "/usr/bin", "GO_ID": "GO-2026-10-31-09"})
                self.assertEqual(code, 2)
                self.assertIn(motif, err)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "sortie2")))

    def test_pre_pilote_sans_etage_1_puis_simule(self):
        conf = avec_externes(self.tmp, A.configuration_pre_pilote(self.tmp))
        ch = self.ecrire_conf(conf)
        sortie = os.path.join(self.tmp, "sortie-pp")
        code, _, err, _ = self.lancer(["--pre-pilote", ch, sortie, "--verifier-seulement"])
        self.assertEqual(code, 2)
        self.assertIn("DEP3", err)
        code, out, err, _ = self.lancer(["--pre-pilote", ch, sortie, "--verifier-seulement"], etage1=A.EtageUnFactice())
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["montant_requis_go_usd"], 60.0)
        self.assertFalse(os.path.exists(sortie))
        code, out, err, _ = self.lancer(["--pre-pilote", ch, sortie, "--moteur", "simule"], etage1=A.EtageUnFactice())
        self.assertEqual(code, 0, err)
        self.assertTrue(os.path.isfile(os.path.join(sortie, "analyse-m1.json")))
        code, _, err, _ = self.lancer(["--pre-pilote", ch, os.path.join(self.tmp, "pp2"), "--moteur", "reel", "--registre-go", "x"],
                                      etage1=A.EtageUnFactice())
        self.assertIn("decisions_a15", err)


class TestR12(unittest.TestCase):
    def test_aucun_fichier_de_la_v53_modifie(self):
        """Chaque empreinte de la liste v53 (copiée dans la livraison) tient sur l'arbre v54."""
        liste = os.path.join(RACINE, "EMPREINTES-orchestrateur-pole-v7-v53.txt")
        n = 0
        with open(liste, encoding="utf-8") as f:
            for ligne in f:
                sha, rel = ligne.rstrip("\n").split("  ", 1)
                with open(os.path.join(RACINE, rel), "rb") as g:
                    self.assertEqual(hashlib.sha256(g.read()).hexdigest(), sha, rel)
                n += 1
        self.assertGreater(n, 350)


if __name__ == "__main__":
    unittest.main()
