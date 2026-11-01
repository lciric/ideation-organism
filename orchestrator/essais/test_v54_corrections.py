"""Essais de la v54 — corrections de la contre-lecture CL18 (CL18-01 à CL18-17). Hors ligne : moteur simulé v54 ; aucune
clé, aucun appel payant ; chaque essai lit la vraie sortie du code (jamais des nombres écrits à la main pour une sortie de
run : classe R-545)."""

import json
import os
import sys
import unittest

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)

import aides_v54 as A  # noqa: E402
from aides import CasAvecDossier  # noqa: E402
from pole import bisociateur_v54 as b54  # noqa: E402
from pole import budget_v54 as bv  # noqa: E402
from pole import configuration_v54 as cfg  # noqa: E402
from pole import course2_v54 as c2  # noqa: E402
from pole import fiches_v54 as fv  # noqa: E402
from pole import mesures_v54 as mz  # noqa: E402
from pole.aiguilleur_v53 import SansPasseport  # noqa: E402
from pole.etage_entre_generations_v53 import MachineNonJetable  # noqa: E402
from pole.etage_entre_generations_v54 import exiger_machine_jetable_v54  # noqa: E402
from pole.noyau_v54 import NoeudArret  # noqa: E402
from pole.simulation_v54 import AdaptateurSimuleV54  # noqa: E402

JETABLE = {"POLE_MACHINE_JETABLE_V54": "1", "PATH": "/usr/bin:/bin"}


def lire(chemin):
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


class Comptant(AdaptateurSimuleV54):
    """Moteur simulé qui garde, pour chaque appel, la marque du rôle lue dans la consigne (essai seulement)."""

    def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
        r = super().lancer(role, consigne, dossier, budget_usd, max_tours, modele)
        self.appels[-1]["juge"] = "JUGE" in consigne and "## La fiche" in consigne
        self.appels[-1]["dossier"] = dossier
        self.appels[-1]["consigne"] = consigne
        return r


def comptants(cout=0.01, **dec):
    return {n: Comptant(champs_fiche=A.CHAMPS, items=A.ITEMS, cout_par_appel_usd=cout, champ_titre="titre", decider=dec.get(n))
            for n in ("kimi", "argon", "claude")}


class Base(CasAvecDossier):
    def conf(self, **modifs):
        return cfg.lire_configuration_v54(A.configuration(self.tmp, **modifs), base=self.tmp)

    def generation(self, conf=None, ad=None, nom="s", **kw):
        g = c2.GenerationV54(conf or self.conf(), os.path.join(self.tmp, nom), ad or comptants(), **kw)
        return g


class TestCL18_01JournalComplet(Base):
    def _verifier(self, g, ad):
        cons = g.coffre.consommations()
        appels = [c for c in cons if c["role"] not in ("coupure", "a14")]
        tous = [a for x in ad.values() for a in x.appels]
        self.assertEqual(len(appels), len(tous))  # une consommation par appel, rien d'omis
        self.assertAlmostEqual(sum(c["cout_usd"] for c in appels), sum(a["cout"] for a in tous), places=9)
        juges = {j["etiquette"] for j in g.conf["juges"]}
        self.assertEqual(sum(1 for c in appels if c["role"] in juges), sum(1 for a in tous if a["juge"]))
        self.assertGreater(sum(1 for c in appels if c["role"] in juges), 0)
        self.assertAlmostEqual(g.budget.etat()["cumul_usd"], round(sum(a["cout"] for a in tous), 6), places=6)
        b = g.conf["budget"]
        dec, etat = bv.rejouer_consommations(b["plafond_usd"], b["arret_etape_usd"], b["etapes"], cons)
        self.assertEqual(dec, g.budget.decisions())  # rejeu sur la vraie sortie du run, pas sur des nombres écrits à la main
        self.assertEqual(etat["etapes"], g.budget.etat()["etapes"])
        for c in appels:
            self.assertTrue({"fournisseur", "modele_demande", "modele_servi", "statut", "duree_s"} <= set(c))

    def test_cas_sain_journal_egal_a_la_sortie_reelle(self):
        ad = comptants()
        g = self.generation(ad=ad)
        g.executer()
        self._verifier(g, ad)

    def test_coupure_rejouee_sur_les_consommations(self):
        ad = comptants(cout=0.4)
        conf = self.conf(budget__plafond_usd=6.0, budget__arret_etape_usd="sans")
        g = self.generation(conf, ad)
        g.executer()
        self.assertIn(bv.NON_MESUREE, g.etapes_etat.values())
        self.assertTrue(any(c.get("coupure") for c in g.coffre.consommations()))
        self._verifier(g, ad)

    def test_cout_garde_quand_une_garde_leve_apres_l_appel(self):
        def argon(role, consigne, modele, n):
            if "JUGE" in consigne and n > 3:
                return {"modele_servi": "gemini-4-argon-autre"}
        ad = comptants(argon=argon)
        g = self.generation(ad=ad)
        from pole.juges_croises_v53 import VersionServieChangee
        with self.assertRaises(VersionServieChangee):
            g.executer()
        tous = [a for x in ad.values() for a in x.appels]
        fin = lire(os.path.join(self.tmp, "s", "manifeste-fin.json"))
        self.assertAlmostEqual(fin["budget"]["cumul_usd"], round(sum(a["cout"] for a in tous), 6), places=6)

    def test_artefact_exception_de_l_adaptateur_compte_le_pire_cas(self):
        ad = comptants()

        def casse(role, consigne, modele, n):
            if "JUGE" in consigne:
                raise OSError("relais tombé")
        ad["argon"].decider = casse
        g = self.generation(ad=ad)
        with self.assertRaises(OSError):
            g.executer()
        cons = [c for c in g.coffre.consommations() if c["statut"] == "exception"]
        self.assertEqual(len(cons), 1)
        self.assertTrue(cons[0]["cout_inconnu"])
        self.assertEqual(cons[0]["cout_usd"], g.conf["plafonds_session"]["juge"])


class TestCL18_02CoupureEtNoeud(Base):
    def test_cas_sain_course_enchaine_deux_generations(self):
        bilan = c2.executer_course_v54(self.conf(), os.path.join(self.tmp, "c"), comptants(), nombre_generations=2, go={"essai": 1})
        self.assertEqual([b["noeud"] for b in bilan], [None, None])
        self.assertTrue(all(b["c13_satisfaite"] for b in bilan))

    def test_artefact_protegee_coupee_non_mesuree_et_course_arretee(self):
        conf = self.conf(budget__plafond_usd=6.0, budget__arret_etape_usd="sans")
        with self.assertRaises(NoeudArret):
            c2.executer_course_v54(conf, os.path.join(self.tmp, "c"), comptants(cout=0.4), nombre_generations=2, go={"essai": 1})
        fin = lire(os.path.join(self.tmp, "c", "generation-1", "manifeste-fin.json"))
        coupee = [n for n, e in fin["etapes"].items() if e == bv.NON_MESUREE]
        self.assertEqual(len(coupee), 1)
        # l'étape déclarée non mesurée est celle où un appel n'a pas été lancé faute de reste (coupée en route, pas « jouée »)
        self.assertTrue(any(e["evenement"] == "coupure-budget" and e["etape"] == coupee[0] for e in fin["evenements"]))
        self.assertTrue(any(j["quoi"] == "coupee" and j["etape"] == coupee[0] and j["signalee"] for j in fin["budget"]["journal"]))
        self.assertNotEqual(fin["etapes"][coupee[0]], "jouee")
        self.assertFalse(fin["budget"]["c13_budget_satisfaite"])
        self.assertIn("C13", fin["noeud"])
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "c", "generation-2")))
        bilan = lire(os.path.join(self.tmp, "c", "bilan-course.json"))
        self.assertIn("C13", bilan["noeud"])
        etapes_apres = c2.ETAPES[c2.ETAPES.index(coupee[0]) + 1:]
        self.assertTrue(all(e not in fin["etapes"] for e in etapes_apres))  # rien lancé après le nœud

    def test_budget_coupee_signalee_et_cumul_pile_au_plafond(self):
        et = [{"nom": "p", "attendu_usd": 1, "reservation_usd": 1, "role": "protegee"},
              {"nom": "h", "attendu_usd": 1, "reservation_usd": 1, "role": "protegee_hors_porte"},
              {"nom": "s", "attendu_usd": 1, "reservation_usd": 1, "role": "sacrifiable", "rang": 1}]
        b = bv.BudgetV54(10.0, "sans", et)
        b.avant_etape("p")
        self.assertEqual(b.apres_etape("p", 2.0), "jouee")
        b2 = bv.BudgetV54(2.0, "sans", et[:1])
        b2.avant_etape("p")
        self.assertEqual(b2.apres_etape("p", 2.0), "jouee")  # pile au plafond, travail fini : jouée
        b3 = bv.BudgetV54(2.0, "sans", et[:1])
        b3.avant_etape("p")
        self.assertEqual(b3.apres_etape("p", 2.0, coupee=True), bv.NON_MESUREE)  # pile au plafond, travail restant : coupée
        b4 = bv.BudgetV54(2.0, "sans", et[:1])
        b4.avant_etape("p")
        self.assertEqual(b4.apres_etape("p", 0.5, coupee=True), bv.NON_MESUREE)


class TestCL18_03LigneDeGo(Base):
    def reg(self, *lignes):
        return A.registre_go(self.tmp, *lignes)

    def test_cas_sain_montant_exact(self):
        r = self.reg(A.ligne_go("GO-2026-10-31-09", "45 USD"))
        g = cfg.verifier_go_v54("GO-2026-10-31-09", r, 45.0)
        self.assertEqual(g["plafond_lu_usd"], 45.0)

    def test_artefacts_montant_different_plus_grand_identifiant_absent(self):
        cas = {"montant différent": (A.ligne_go("GO-2026-10-31-09", "44 USD"), "GO-2026-10-31-09", "pas exactement"),
               "montant plus grand": (A.ligne_go("GO-2026-10-31-09", "150 USD"), "GO-2026-10-31-09", "plus grand"),
               "identifiant absent": (A.ligne_go("GO-2026-10-31-09", "45 USD"), "GO-2026-10-31-10", "absent"),
               "identifiant non exact": (A.ligne_go("GO-2026-10-31-09", "45 USD"), "GO-2026-10-31-9", "identifiant"),
               "plusieurs montants (libellé du registre)": (A.ligne_go("GO-2026-10-31-09",
                                                                      "10 USD par lancement, dans les 150 USD de GO-2026-10-04-08 prolongé (GO-2026-10-20-06)"),
                                                            "GO-2026-10-31-09", "plusieurs montants"),
               "un montant plus grand avec mention (libellé du registre)": (A.ligne_go("GO-2026-10-31-09",
                                                                                      "150 USD, plafond de GO-2026-10-04-08 inchangé"),
                                                                            "GO-2026-10-31-09", "pas exactement"),
               "par lancement": (A.ligne_go("GO-2026-10-31-09", "45 USD par lancement"), "GO-2026-10-31-09", "par lancement"),
               "autre monnaie": (A.ligne_go("GO-2026-10-31-09", "45 EUR"), "GO-2026-10-31-09", "USD exigé"),
               "type": (A.ligne_go("GO-2026-10-31-09", "45 USD", typ="revendication", echeance="2099-12-31"), "GO-2026-10-31-09", "type"),
               "révoqué": (A.ligne_go("GO-2026-10-31-09", "45 USD") + A.ligne_go("GO-2026-10-31-11", "—", typ="révocation",
                                                                                  perimetre="révocation de GO-2026-10-31-09"),
                           "GO-2026-10-31-09", "révoqué")}
        for quoi, (ligne, ident, motif) in cas.items():
            with self.subTest(quoi):
                r = A.registre_go(self.sous_dossier(quoi.replace(" ", "_")[:20]), ligne)
                with self.assertRaisesRegex(cfg.GoRefuse, motif):
                    cfg.verifier_go_v54(ident, r, 45.0)

    def test_montant_requis_selon_la_portee_choix_1(self):
        conf = self.conf(budget__plafond_usd=45.0)
        self.assertEqual(cfg.montant_requis(conf, 1), 45.0)
        self.assertEqual(cfg.montant_requis(conf, 2, 5.0), 95.0)  # par génération : N × S17 + (N − 1) × étage
        conf2 = self.conf(budget__plafond_usd=45.0, budget__portee_plafond="course")
        self.assertEqual(cfg.montant_requis(conf2, 3, 5.0), 45.0)
        with self.assertRaises(cfg.ConfigurationRefusee):
            self.conf(budget__portee_plafond="À REMPLIR")


class TestCL18_05Passeport(Base):
    def test_contenu_modifie_apres_aiguillage_perd_son_passeport(self):
        g = self.generation()
        g.passe1 = []
        for nom in ("proposition", "aiguillage"):
            g.jouer_etape(nom, getattr(g, "etape_" + nom))
        f = next(f for f in g.passe1 if g.aiguilleur.a_passeport(f))
        f["contenu"]["hypothese"] = "contenu changé après le passage"  # l'empreinte stockée n'est pas touchée
        self.assertFalse(g.aiguilleur.a_passeport(f))
        with self.assertRaises(SansPasseport):
            g.aiguilleur.exiger_passeport(f, "un juge")


class TestCL18_06A4(Base):
    def test_prefixe_attrape_pluriels_et_derives_mot_entier_non(self):
        for t in ("des témoins", "deux fusions", "fusionnée", "protocole exploratoires", "bisociations", "selon Gu et Krenn"):
            with self.subTest(t):
                self.assertTrue(fv.trouver(t, A.INTERDITES, "prefixe"))
        self.assertFalse(fv.trouver("des témoins", A.INTERDITES, "mot_entier"))
        self.assertFalse(fv.trouver("une méthode de mesure", A.INTERDITES, "prefixe"))

    def _kimi_temoin(self):
        def kimi(role, consigne, modele, n):
            if "## Case" in consigne and "## Tableau minimal" not in consigne:  # passe 1 seulement
                return {"texte": json.dumps({"fiches": [{"titre": "Groupe témoin apparié", "hypothese": "h", "axe": "1", "methode": "m"},
                                                        {"titre": "Méthode", "hypothese": "h2", "axe": "2", "methode": "m2"}]})}
        return kimi

    def test_action_fiche_exclue_la_generation_continue(self):
        conf = self.conf(a4={"mode": "prefixe", "action": "fiche_exclue"})
        g = self.generation(conf, comptants(kimi=self._kimi_temoin()))
        g.executer()
        fin = lire(os.path.join(self.tmp, "s", "manifeste-fin.json"))
        self.assertIsNone(fin["arret"])
        self.assertEqual(len(fin["exclues_a4"]), 1)
        self.assertEqual(list(fin["exclues_a4"].values())[0]["etiquettes"], ["témoin"])

    def test_action_arret(self):
        g = self.generation(ad=comptants(kimi=self._kimi_temoin()))
        with self.assertRaises(fv.EtiquetteDansEntree):
            g.executer()


class TestCL18_07Graines(Base):
    def test_noms_de_taches_du_brouillon_7(self):
        g = self.generation()
        g.executer()
        taches = set(lire(os.path.join(self.tmp, "s", "manifeste-fin.json"))["graines"]["taches"])
        self.assertTrue({"pp2-bisoc-ordre", "pp2-bisoc-gk", "pp2-bisoc-meta", "pp2-bisoc-n"} <= taches)
        self.assertFalse(any("ordre-fusion" in t for t in taches))
        self.assertTrue(any(t.startswith("pp2-anonymisation-") for t in taches))


class TestCL18_08Lectures(Base):
    def test_entree_kimi_seulement_et_passe_tableau_non_jugee(self):
        ad = comptants()
        conf = self.conf(bisociateur__fournisseurs_entree=["kimi"], tableau__juger_passe_tableau=False)
        g = self.generation(conf, ad)
        g.executer()
        kimi = {f["ident"] for f in g.passe1 if f["meta"]["fournisseur"] == "kimi"}
        paires = g.coffre.ouvrir("pp2-paires-par-bras")["paires"]
        for ps in paires.values():
            for q in ps:
                self.assertTrue(set(q.split("|")) <= kimi)
        self.assertNotIn("passe2", g.lots_juges)
        self.assertTrue(g.passe2)


class TestCL18_10GardeKimi(Base):
    def _refus_kimi(self):
        ad = comptants()
        orig = ad["kimi"].reponse

        def rep(role, consigne, modele):
            t = orig(role, consigne, modele)
            if "## Case" in consigne:
                o = json.loads(t)
                for f in o["fiches"]:
                    f["methode"] = "MARQUE-KIMI " + f["methode"]
                t = json.dumps(o, ensure_ascii=False)
            return t
        ad["kimi"].reponse = rep
        ad["claude"].decider = lambda r, c, m, n: ({"texte": "réponse illisible"} if "AIGUILLEUR" in c and "MARQUE-KIMI" in c else None)
        return ad

    def test_refus_technique_n_arrete_pas_kimi(self):
        conf = self.conf(garde_kimi__refus_aiguilleur="technique")
        g = self.generation(conf, self._refus_kimi())
        g.executer()
        fin = lire(os.path.join(self.tmp, "s", "manifeste-fin.json"))
        self.assertNotIn("prop-kimi", fin["roles_arretes"])
        self.assertEqual(fin["garde_kimi"]["refus_comptes_techniques"], 2)

    def test_refus_debordement_arrete_kimi_et_metteur_selon_choix_7(self):
        for arret_mf, attendu in ((True, True), (False, False)):
            with self.subTest(arret_metteur_fusion=arret_mf):
                d = self.sous_dossier(f"c{arret_mf}")
                conf = cfg.lire_configuration_v54(A.configuration(d, garde_kimi__arret_metteur_fusion=arret_mf), base=d)
                g = c2.GenerationV54(conf, os.path.join(d, "s"), self._refus_kimi())
                g.executer()
                fin = lire(os.path.join(d, "s", "manifeste-fin.json"))
                self.assertIn("prop-kimi", fin["roles_arretes"])
                self.assertEqual("fusion-kimi" in fin["roles_arretes"], attendu)


class TestCL18_09Specification(unittest.TestCase):
    def test_un_seul_fichier_de_specification_cite_brouillon_7(self):
        self.assertIn("brouillon7", cfg.SPECIFICATION)
        chemin = os.path.join(RACINE, *[os.pardir] * 4, cfg.SPECIFICATION)
        if not os.path.isfile(chemin):
            self.skipTest("ESSAI SUR LE BROUILLON 7 NON JOUÉ : fichier hors de la livraison")
        import hashlib
        with open(chemin, "rb") as f:
            self.assertEqual(hashlib.sha256(f.read()).hexdigest(), cfg.SPECIFICATION_SHA256)

    def test_dep4_exige_au_lancement_reel(self):
        conf = {"pieces": {}}
        self.assertTrue(any("confirmation de DEP4" in m for m in cfg.verifier_dependances_lancement(conf)))
        self.assertTrue(any("decisions_a15" in m for m in cfg.verifier_dependances_lancement(conf, "pre_pilote")))


class TestCL18_12Fuites(Base):
    def test_sessions_opaques_et_nature_neutre(self):
        ad = comptants()
        g = self.generation(ad=ad)
        g.executer()
        noms = os.listdir(os.path.join(self.tmp, "s", "sessions"))
        self.assertTrue(noms and all(len(n) == 16 and all(c in "0123456789abcdef" for c in n) for n in noms))
        for a in [a for x in ad.values() for a in x.appels]:
            self.assertNotIn("vocabulaire_gk", a["consigne"])
            for mot in ("fusions", "passe1", "juges"):
                self.assertNotIn(mot, os.path.relpath(a["dossier"], self.tmp).split(os.sep)[2:])
        cles = g.coffre.ouvrir("pp2-cle-sessions")
        self.assertTrue(any(v.startswith("juges/") for v in cles.values()))

    def test_artefact_mot_interdit_dans_une_consigne_figee_arret(self):
        conf = A.configuration(self.tmp)
        conf["pieces"]["consigne_juge"] = A.ecrire(os.path.join(self.tmp, "p", "juge-fautif.md"), "JUGE : note cette fusion.")
        conf = cfg.lire_configuration_v54(conf, base=self.tmp)
        g = self.generation(cfg.lire_configuration_v54(A.configuration(self.tmp, a4={"mode": "prefixe", "action": "fiche_exclue"},
                                                                       pieces=conf["pieces"]), base=self.tmp))
        with self.assertRaisesRegex(fv.EtiquetteDansEntree, "entrée complète"):
            g.executer()


class TestCL18_13MachineJetable(unittest.TestCase):
    def test_noms_de_cle_refuses_et_cas_sain(self):
        self.assertTrue(exiger_machine_jetable_v54(JETABLE))
        for nom in ("AWS_ACCESS_KEY_ID", "GOOGLE_APPLICATION_CREDENTIALS", "DB_PASSWORD", "MON_TOKEN", "UNE_SSH_KEY", "KIMI_API_KEY"):
            with self.subTest(nom), self.assertRaisesRegex(MachineNonJetable, nom):
                exiger_machine_jetable_v54(dict(JETABLE, **{nom: "x"}))
        with self.assertRaises(MachineNonJetable):
            exiger_machine_jetable_v54({"POLE_MACHINE_JETABLE_V53": "1"})


class TestCL18_14Accords(unittest.TestCase):
    def test_kappas_non_definis_sur_marges_constantes(self):
        self.assertIsNone(mz.kappa_cohen_v54([False] * 5, [False] * 5))
        self.assertIsNone(mz.kappa_fleiss_v54([[False, False, False]] * 5))
        self.assertAlmostEqual(mz.kappa_cohen_v54([True, False, True, False], [True, False, False, False]), 0.5)

    def test_etalonnage_avec_verdicts_absents(self):
        att = {"p1": "P", "p2": "P", "n1": "N", "n2": "N"}
        nota = {"a": {"p1": True, "p2": None, "n1": False, "n2": False}, "b": {"p1": True, "p2": True, "n1": False, "n2": True}}
        r = mz.etalonner_juges_v54(nota, att, exactitude_min=0.8, rappel_min=0.7, plancher_echec=0.7, fleiss_min=0.4,
                                   cohen_min=0.3, accord_plancher=0.2)
        self.assertEqual(r["par_juge"]["a"]["absents"], 1)
        self.assertEqual(r["par_juge"]["a"]["rappel_P"], 1.0)
        self.assertEqual(r["temoins_exclus_des_kappas"], 1)
        r2 = mz.etalonner_juges_v54({"a": {"p1": False, "n1": False}, "b": {"p1": False, "n1": False}}, {"p1": "P", "n1": "N"},
                                    exactitude_min=0.8, rappel_min=0.7, plancher_echec=0.7, fleiss_min=0.4, cohen_min=0.3,
                                    accord_plancher=0.2)
        self.assertEqual(r2["accord"], "non défini (marges constantes)")
        self.assertFalse(r2["porte_juges"])


class TestCL18_15Essais(Base):
    def test_trois_paires_a_n_egal_2_refusees(self):
        with self.assertRaisesRegex(b54.BisociationRefusee, "n = 2"):
            b54.verifier_paires_globales({"a": [("x", "y")], "b": [("x", "z")], "c": [("y", "z")]}, 2)

    def test_a18_au_niveau_generation(self):
        g = self.generation()
        import pole.course2_v54 as mod
        orig = mod.construire

        def fautif(*a, **k):
            t = orig(*a, **k)
            if t["entrees"]:
                t["entrees"][0]["case"] = ["autre-texte", "autre-bras"]
            return t
        mod.construire = fautif
        try:
            g.executer()
        finally:
            mod.construire = orig
        fin = lire(os.path.join(self.tmp, "s", "manifeste-fin.json"))
        self.assertTrue(any(e["evenement"] == "passe-tableau-arretee" and "A18" in e["motif"] for e in fin["evenements"]))

    def test_la_suite_n_ecrit_pas_dans_l_arbre(self):
        import aides
        self.assertFalse(self.tmp.startswith(RACINE))
        self.assertFalse(aides.BASE.startswith(RACINE))
        self.assertTrue(sys.dont_write_bytecode)


class TestCL18_16Budget(unittest.TestCase):
    def test_cumul_jamais_ecrete_et_m6b_coupee_hors_porte(self):
        et = [{"nom": "p", "attendu_usd": 1, "reservation_usd": 1, "role": "protegee"},
              {"nom": "h", "attendu_usd": 1, "reservation_usd": 1, "role": "protegee_hors_porte"}]
        b = bv.BudgetV54(3.0, "sans", et)
        b.avant_etape("p")
        b.apres_etape("p", 1.0)
        b.avant_etape("h")
        self.assertEqual(b.apres_etape("h", 2.5), bv.NON_MESUREE_HORS_PORTE)
        e = b.etat()
        self.assertAlmostEqual(e["cumul_usd"], 3.5)
        self.assertAlmostEqual(e["depassement_s17_usd"], 0.5)
        self.assertTrue(e["c13_satisfaite"])
        self.assertEqual(e["reserves_hors_porte"], ["h"])


class TestCL18_17Heritage(Base):
    def test_heritage_sous_garde_a4(self):
        g = self.generation(heritage_texte=json.dumps([{"titre": "Fusion de deux fiches", "resume": "r", "notable": True},
                                                       {"titre": "Idée", "resume": "r", "notable": False}]))
        with self.assertRaisesRegex(fv.EtiquetteDansEntree, "héritage"):
            g.executer()
        conf = self.conf(a4={"mode": "prefixe", "action": "fiche_exclue"})
        g2 = self.generation(conf, nom="s2", heritage_texte=json.dumps([{"titre": "Fusion", "resume": "r", "notable": True},
                                                                         {"titre": "Idée", "resume": "r", "notable": False}]))
        self.assertEqual(json.loads(g2._heritage_garde()), [{"titre": "Idée", "resume": "r", "notable": False}])

    def test_n_par_case_et_departage_absent(self):
        f1 = {"ident": "a", "meta": {"case": ["t", "1"]}}
        f2 = {"ident": "b", "meta": {"case": ["t", "2"]}}
        choix, np_ = b54.choisir_paires_v54([f1, f2], {}, ["meta"], 1, None, {})
        self.assertEqual(np_, {"meta": "non produit (effectif)"})
        with self.assertRaisesRegex(b54.BisociationRefusee, "départage"):
            b54.choisir_paires_v54([f1, f2], {"meta": {}}, ["meta"], 1, None, {})


if __name__ == "__main__":
    unittest.main()
