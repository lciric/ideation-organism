"""Essais de la v55 — corrections de la contre-lecture CL19 (CL19-01 à CL19-13), sans décision de Lazar. Hors ligne ; moteur
simulé v55 ; aucune clé ; chaque essai lit la vraie sortie du code. Chaque garde : un cas sain et un artefact."""

import copy
import hashlib
import json
import os
import sys
import unittest

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)

import aides_v55 as A  # noqa: E402
from aides import CasAvecDossier  # noqa: E402
from pole import bisociateur_v54 as b54  # noqa: E402
from pole import bisociateur_v55 as b55  # noqa: E402
from pole import budget_v54 as bv  # noqa: E402
from pole import configuration_v55 as cfg  # noqa: E402
from pole import course2_v55 as c2  # noqa: E402
from pole import gardes_e0_v54 as ge54  # noqa: E402
from pole import gardes_e0_v55 as ge  # noqa: E402
from pole import prepilote_v54 as pp54  # noqa: E402
from pole import prepilote_v55 as pp  # noqa: E402
from pole.coffre_v53 import LectureAvantFinE9  # noqa: E402
from pole.coffre_v55 import CoffreV55, SortieDeGardeRefusee  # noqa: E402
from pole.etage_entre_generations_v53 import MachineNonJetable  # noqa: E402
from pole.etage_entre_generations_v55 import exiger_machine_jetable_v55  # noqa: E402
from pole.fiches_v54 import EtiquetteDansEntree  # noqa: E402
from pole.noyau_v54 import NoeudArret  # noqa: E402
from pole.noyau_v55 import ModeleServiAbsent, SessionsMalPlacees  # noqa: E402
from pole.outils import ecrire_json_scelle  # noqa: E402


def lire(chemin):
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def metteur(ad, transforme):
    """Le metteur en forme simulé de chaque fournisseur passe par `transforme(texte, consigne)`."""
    for x in ad.values():
        orig = x.reponse

        def rep(role, consigne, modele, orig=orig):
            t = orig(role, consigne, modele)
            return transforme(t, consigne) if "## Éléments à mettre en forme" in consigne else t
        x.reponse = rep
    return ad


class Base(CasAvecDossier):
    def conf_course(self, **modifs):
        return cfg.lire_configuration_v54(A.configuration(self.tmp, **modifs), base=self.tmp)

    def conf_pp(self, conf=None, **modifs):
        return cfg.lire_configuration_v54(A.avec_externes(self.tmp, conf or A.configuration_pre_pilote(self.tmp, **modifs)), base=self.tmp)

    def gen(self, conf=None, ad=None, nom="s", **kw):
        kw.setdefault("racine_sessions", os.path.join(self.tmp, "sessions-" + nom))
        return c2.GenerationV55(conf or self.conf_course(), os.path.join(self.tmp, nom), ad or A.adaptateurs(), **kw)

    def pp(self, conf=None, ad=None, nom="s", **kw):
        kw.setdefault("etage1", A.EtageUnFactice())
        kw.setdefault("racine_sessions", os.path.join(self.tmp, "sessions-" + nom))
        return pp.PrePiloteV55(conf or self.conf_pp(), os.path.join(self.tmp, nom), ad or A.adaptateurs(), **kw)

    def fin(self, nom="s"):
        return lire(os.path.join(self.tmp, nom, "manifeste-fin.json"))


# --- CL19-01 : source ou annexe absente, sans arrêt ------------------------------------------------------------------------


class TestCL19_01SourcesAbsentes(Base):
    def test_cas_sain_source_et_annexe_presentes(self):
        conf = self.conf_course()
        decl, params = c2.declarer_bras_v55(conf)
        self.assertTrue(decl["gu_krenn"]["produit"] and decl["meta"]["produit"])
        t = {x["ligne"]: x for x in ge.rejouer_gardes_v55(conf, decl, params)}
        self.assertEqual((t["20"]["statut"], t["22b"]["statut"], t["21"]["statut"]), (ge.REJOUEE,) * 3)

    def test_a19_source_absente_bras_non_produit_compte_sans_arret(self):
        conf = self.conf_course()
        conf["bisociateur"]["gu_krenn"]["source"]["sha256"] = "0" * 64
        decl, params = c2.declarer_bras_v55(conf)
        self.assertEqual(decl["gu_krenn"]["cause"], c2.CAUSE_SOURCE_ABSENTE)
        with self.assertRaisesRegex(ge54.GardesE0Refusees, "ligne 20 \\(non rejouée"):  # le défaut de la v54 (CL19-01)
            ge54.rejouer_gardes(conf, decl, params)
        t = {x["ligne"]: x for x in ge.rejouer_gardes_v55(conf, decl, params)}
        self.assertEqual(t["20"]["statut"], ge.SANS_OBJET)
        self.assertEqual(t["21"]["statut"], ge.REJOUEE)
        g = self.gen(conf)
        g.executer()
        fin = self.fin()
        self.assertIsNone(fin["noeud"])
        self.assertEqual(fin["c12"]["causes"].get(c2.CAUSE_SOURCE_ABSENTE), 1)
        self.assertFalse(fin["bras"]["gu_krenn"]["produit"])

    def test_artefact_gu_krenn_non_produit_sans_cause_refuse(self):
        conf = self.conf_course()
        conf["bisociateur"]["gu_krenn"]["source"]["sha256"] = "0" * 64
        decl, params = c2.declarer_bras_v55(conf)
        decl["gu_krenn"]["cause"] = "autre chose"
        with self.assertRaisesRegex(ge.GardesE0Refusees, "ligne 20 \\(non rejouée : bras Gu-Krenn non produit sans cause"):
            ge.rejouer_gardes_v55(conf, decl, params)

    def test_a20_annexe_absente_bras_meta_non_produit_sans_arret(self):
        conf = self.conf_course()
        conf["bisociateur"]["meta"]["annexe"]["chemin"] = os.path.join(self.tmp, "absente.md")
        decl, params = c2.declarer_bras_v55(conf)
        self.assertEqual(decl["meta"]["cause"], c2.CAUSE_ANNEXE)
        self.assertIn("absente", decl["meta"]["motif"])
        t = {x["ligne"]: x for x in ge.rejouer_gardes_v55(conf, decl, params)}
        self.assertEqual({t[n]["statut"] for n in ("22b", "23", "24")}, {ge.SANS_OBJET})
        self.gen(conf).executer()
        fin = self.fin()
        self.assertIsNone(fin["noeud"])
        self.assertEqual(fin["c12"]["causes"].get(c2.CAUSE_ANNEXE), 1)

    def test_lanceur_v7_source_absente_part(self):
        conf = A.configuration(self.tmp)
        conf["bisociateur"]["gu_krenn"]["source"]["sha256"] = "0" * 64
        ch = os.path.join(self.tmp, "conf.json")
        with open(ch, "w", encoding="utf-8") as f:
            json.dump(conf, f, ensure_ascii=False)
        code, out, err = TestLanceurV7.lancer(self, ["--course-2", ch, os.path.join(self.tmp, "x"), "--generations", "1",
                                                      "--verifier-seulement"])
        self.assertEqual(code, 0, err)
        o = json.loads(out)
        self.assertEqual({x["ligne"]: x["statut"] for x in o["table_r5_e0"]}["20"], ge.SANS_OBJET)


# --- CL19-02 : rien d'ouvert après un nœud ---------------------------------------------------------------------------------


class TestCL19_02RienApresNoeud(Base):
    def _verifier_rien_ouvert(self, g, nom="s"):
        fin = self.fin(nom)
        quoi = [a["quoi"] for a in fin["coffre"]["acces"]]
        self.assertFalse(fin["coffre"]["fin_e9"])
        self.assertNotIn("fin_e9", quoi)
        self.assertNotIn("ouverture", quoi)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, nom, "analyse-m1.json")))
        self.assertFalse(os.path.exists(os.path.join(self.tmp, nom, "classement.json")))
        self.assertTrue(any(e["evenement"] == "noeud-rien-ouvert" for e in fin["evenements"]))
        self.assertTrue(os.path.isfile(os.path.join(g.coffre.dossier, g.tache("cle-sessions") + ".json")))
        return fin

    def test_cas_sain_fin_e9_et_analyse(self):
        g = self.pp()
        g.executer()
        fin = self.fin()
        self.assertTrue(fin["coffre"]["fin_e9"])
        self.assertTrue(os.path.isfile(os.path.join(self.tmp, "s", "analyse-m1.json")))

    def test_artefact_plafond_bas_noeud_rien_ouvert(self):
        g = self.pp(self.conf_pp(A.configuration_pre_pilote(self.tmp, plafond=25.0)), A.adaptateurs(cout=2.0))
        with self.assertRaisesRegex(NoeudArret, "C13"):
            g.executer()
        fin = self._verifier_rien_ouvert(g)
        self.assertIn(bv.NON_MESUREE, fin["etapes"].values())
        self.assertNotIn("e5_relecteur", fin["etapes"])

    def test_artefact_noeud_e5_rien_ouvert_et_attestation(self):
        ad = A.adaptateurs()
        ad["claude"].decider = lambda r, c, m, n: ({"texte": json.dumps({"notable": True, "item": None, "defaut_present": True})}
                                                   if "RELECTEUR" in c else None)
        g = self.pp(ad=ad)
        with self.assertRaisesRegex(NoeudArret, "A6"):
            g.executer()
        self._verifier_rien_ouvert(g)
        att = lire(os.path.join(self.tmp, "s", pp.ATTESTATION_V1))
        self.assertEqual((att["version_temoins_epuisee"], att["noeud"]), (1, "É5bis"))

    def test_artefact_course_noeud_rien_ouvert(self):
        conf = self.conf_course(budget__plafond_usd=0.5, budget__arret_etape_usd="sans")
        with self.assertRaises(NoeudArret):
            c2.executer_course_v55(conf, os.path.join(self.tmp, "c"), A.adaptateurs(cout=0.2), nombre_generations=2, go={},
                                   racine_sessions=os.path.join(self.tmp, "sess-c"))
        fin = lire(os.path.join(self.tmp, "c", "generation-1", "manifeste-fin.json"))
        self.assertFalse(fin["coffre"]["fin_e9"])
        self.assertNotIn("ouverture", [a["quoi"] for a in fin["coffre"]["acces"]])
        for f in ("classement.json", "memoire.json", "fiches.json"):
            self.assertFalse(os.path.exists(os.path.join(self.tmp, "c", "generation-1", f)), f)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "c", "generation-2")))


# --- CL19-03 : clé des classes ---------------------------------------------------------------------------------------------


class TestCL19_03CleDesClasses(Base):
    def test_cas_sain_deux_lectures_journalisees_comptes_seulement(self):
        g = self.pp()
        g.executer()
        fin = self.fin()
        self.assertFalse(hasattr(g, "_cle_classes"))
        self.assertTrue(all("classe" not in f for f in g.fonds))
        lect = [a for a in fin["coffre"]["acces"] if a["quoi"] == "lecture_par_programme"]
        self.assertEqual([(a["nom"], a["role"]) for a in lect], [("pp2-cle-classes", pp.ROLE_E3), ("pp2-cle-classes", pp.ROLE_E5)])
        for a in lect:
            self.assertFalse(a["apres_fin_e9"])
            self.assertTrue(a["horodatage"] and a["raison"])
            self.assertTrue(all(v is None or isinstance(v, (bool, int, float)) for v in a["sortie"].values()))
        self.assertEqual(fin["coffre"]["lectures_non_soldees"], [])
        self.assertTrue(all(not isinstance(v, list) for v in fin["e5"].values()))
        self.assertNotIn("primaires_non_ambigus", json.dumps(fin))
        quoi = [a["quoi"] for a in fin["coffre"]["acces"]]
        self.assertTrue(all(q != "ouverture" for q in quoi[:quoi.index("fin_e9")]))

    def test_artefact_lecture_non_declaree_incident(self):
        g = self.pp()
        g.coffre.deposer(g.tache("cle-classes"), {"t1": {"classe": "P"}})
        with self.assertRaisesRegex(LectureAvantFinE9, "non déclarée"):
            g.coffre.lire_pour_garde(g.tache("cle-classes"), "un-autre-role", "essai")
        self.assertEqual(len(g.coffre.incidents), 1)
        cf = CoffreV55(os.path.join(self.tmp, "cf"), lectures_permises=[("k", "r")])
        cf.deposer("k", {"t1": {"classe": "P"}})
        jeton, _ = cf.lire_pour_garde("k", "r", "essai")
        with self.assertRaisesRegex(SortieDeGardeRefusee, "seuls des comptes"):
            cf.noter_sortie_garde(jeton, {"primaires": ["t1"]})

    def test_e6_ordre_par_identifiant(self):
        g = self.pp()
        g.executer()
        e6 = [c.split("/")[-1] for c in g.sessions.values() if c.startswith("juges/e6/juge-kimi/")]
        self.assertEqual(e6, sorted(e6))
        self.assertGreater(len(e6), 3)

    def test_e9_liste_reduite_scellee_cle_d_anteriorite_jamais_lue(self):
        conf = A.configuration_pre_pilote(self.tmp)
        e9 = next(e for e in conf["budget"]["etapes"] if e["nom"] == "e9_anteriorite")
        e9.update(attendu_usd=58.0, reservation_usd=65.0)
        g = self.pp(self.conf_pp(conf))
        lues = []
        orig = g.piece
        g.piece = lambda nom: (lues.append(nom), orig(nom))[1]
        g.executer()
        fin = self.fin()
        self.assertTrue(fin["budget"]["etapes"]["e9_anteriorite"]["reduite"])
        self.assertNotIn("anteriorite_cle", lues)
        self.assertEqual(sorted(n[len("verdicts-e9-"):-5] for n in os.listdir(g.coffre.dossier)
                                if n.startswith("verdicts-e9-") and n.endswith(".json")), ["a0", "a2"])

    def test_artefact_liste_reduite_mal_formee_ou_non_scellee(self):
        conf = A.configuration_pre_pilote(self.tmp)
        conf["pieces"]["liste_reduite_e9"] = A.piece_scellee(os.path.join(self.tmp, "l2"), "l.json", {"idents": ["a0"]})
        with self.assertRaisesRegex(cfg.ConfigurationRefusee, "2 identifiants distincts"):
            pp.verifier_configuration_pre_pilote_v55(cfg.lire_configuration_v54(conf, base=self.tmp))
        conf = A.configuration_pre_pilote(self.tmp)
        conf["pieces"]["liste_reduite_e9"] = A.ecrire(os.path.join(self.tmp, "l3", "l.json"), json.dumps({"idents": ["a0", "a2"]}))
        with self.assertRaisesRegex(cfg.ConfigurationRefusee, "non scellée"):
            pp.verifier_configuration_pre_pilote_v55(cfg.lire_configuration_v54(conf, base=self.tmp))


# --- CL19-04 : sessions hors d'atteinte du coffre --------------------------------------------------------------------------


class TestCL19_04Sessions(Base):
    def test_cas_sain_sessions_hors_de_la_sortie(self):
        g = self.gen()
        vus = []
        orig = g.session
        g.session = lambda *l: (vus.append(orig(*l)), vus[-1])[1]
        g.executer()
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "s", "sessions")))
        self.assertTrue(g.sessions and vus)
        self.assertEqual(self.fin()["sessions"]["rangement"]["retires_vides"], len(g.sessions))  # moteur simulé : aucune trace
        self.assertFalse(os.path.exists(g.base_sessions))
        for d in vus:
            self.assertEqual(os.path.dirname(d), g.racine_sessions)
            self.assertFalse(os.path.realpath(d).startswith(os.path.realpath(os.path.join(self.tmp, "s")) + os.sep))
            for k in (1, 2):
                self.assertFalse(os.path.exists(os.path.join(d, *[".."] * k, "coffre")))

    def test_par_defaut_dossier_temporaire_neuf(self):
        g = c2.GenerationV55(self.conf_course(), os.path.join(self.tmp, "s"), A.adaptateurs())
        self.assertTrue(os.path.basename(g.base_sessions).startswith("pole-sessions-v55-"))
        import shutil
        shutil.rmtree(g.base_sessions)

    def test_artefacts_racine_sous_la_sortie_ou_parente_ou_lien(self):
        with self.assertRaisesRegex(SessionsMalPlacees, "sous la sortie"):
            self.gen(racine_sessions=os.path.join(self.tmp, "s", "sess"))
        with self.assertRaisesRegex(SessionsMalPlacees, "sortie sous la racine"):
            self.gen(nom="s2", racine_sessions=self.tmp)
        os.symlink(os.path.join(self.tmp), os.path.join(self.tmp, "lien"))
        with self.assertRaisesRegex(SessionsMalPlacees, "lien symbolique"):
            self.gen(nom="s3", racine_sessions=os.path.join(self.tmp, "lien", "x"))


# --- CL19-05 : ligne de GO et DEP4 -----------------------------------------------------------------------------------------


class TestCL19_05LigneDeGo(Base):
    def go(self, plafond, requis, nom):
        reg = A.registre_go(self.sous_dossier(nom), A.ligne_go("GO-2026-10-31-09", plafond))
        return cfg.verifier_go_v55("GO-2026-10-31-09", reg, requis)

    def test_cas_sain_montants_exacts(self):
        for k, (plafond, requis) in enumerate((("45 USD", 45), ("1 045 USD", 1045), ("1 045 USD", 1045), ("1 045 USD", 1045),
                                               ("1 045,50 USD", 1045.5), ("45 USD, plafond de GO-2026-10-20-06 inchangé", 45))):
            with self.subTest(plafond):
                self.assertEqual(self.go(plafond, requis, f"s{k}")["plafond_lu_usd"], requis)

    def test_artefacts_lectures_qui_echouaient_vers_l_acceptation(self):
        cas = (("1 045 USD", 45, "pas exactement"), ("10-45 USD", 45, "nombre étranger"), ("≈ 45 USD", 45, "approché"),
               ("~45 USD", 45, "approché"), ("environ 45 USD", 45, "approché"), ("jusqu'à 45 USD par génération", 45, "par unité"),
               ("45 USD par étape", 45, "par unité"), ("45 USD (alerte à 36 USD)", 45, "plusieurs montants"),
               ("45 USD, 3 essais", 45, "nombre étranger"), ("$45", 45, "aucun montant"))
        for k, (plafond, requis, motif) in enumerate(cas):
            with self.subTest(plafond):
                with self.assertRaisesRegex(cfg.GoRefuse, motif):
                    self.go(plafond, requis, f"a{k}")
        from pole import configuration_v54 as c54  # la v54 lisait « 1 045 USD » comme 45 (constat CL19-05)
        reg = A.registre_go(self.sous_dossier("v54"), A.ligne_go("GO-2026-10-31-09", "1 045 USD"))
        self.assertEqual(c54.verifier_go_v54("GO-2026-10-31-09", reg, 45)["plafond_lu_usd"], 45)

    def test_dep4_phrase_exigee(self):
        conf = A.configuration(self.tmp)
        conf["pieces"]["dep4"] = A.ecrire(os.path.join(self.tmp, "p", "dep4.md"), "Confirmation DEP4 (essai) : le relais coupe à S17.")
        conf["dependances"] = {"dep4": "dep4"}
        c = cfg.lire_configuration_v54(conf, base=self.tmp)
        self.assertTrue(any("dep4_phrase" in m for m in cfg.verifier_dependances_lancement_v55(c)))
        c["dependances"]["dep4_phrase"] = "phrase absente de la pièce"
        self.assertTrue(any("ne contient pas la phrase" in m for m in cfg.verifier_dependances_lancement_v55(c)))
        c["dependances"]["dep4_phrase"] = "le relais coupe à S17"
        self.assertEqual(cfg.verifier_dependances_lancement_v55(c), [])


# --- CL19-06 : résultats externes et seconde version de témoins ------------------------------------------------------------


class TestCL19_06Externes(Base):
    def table(self, conf):
        decl, params = c2.declarer_bras_v55(conf)
        return ge.rejouer_gardes_v55(conf, decl, params, plan="pre_pilote", etage1=A.EtageUnFactice())

    def test_cas_sain_resultats_scelles_lies_au_script(self):
        t = {x["ligne"]: x for x in self.table(self.conf_pp())}
        self.assertEqual({t[n]["statut"] for n in A.EXTERNES}, {ge.REJOUEE})

    def test_artefacts_forme_seule_refusee(self):
        base = A.configuration_pre_pilote(self.tmp)
        cas = (({"9": {"script_sha256": "f" * 64}}, "ligne 9 \\(ÉCHEC : script du résultat"),
               ({"10": {"identifiant": "autre"}}, "ligne 10 \\(ÉCHEC : ligne ou identifiant"),
               ({"17": {"script": "inconnu"}}, "ligne 17 \\(ÉCHEC : script du résultat"))
        for k, (alt, motif) in enumerate(cas):
            with self.subTest(motif):
                d = self.sous_dossier(f"x{k}")
                conf = cfg.lire_configuration_v54(A.avec_externes(d, copy.deepcopy(base), **alt), base=self.tmp)
                with self.assertRaisesRegex(ge.GardesE0Refusees, motif):
                    self.table(conf)
        conf = A.avec_externes(self.sous_dossier("ns"), copy.deepcopy(base))
        os.remove(conf["pieces"]["garde_8"]["chemin"] + ".sha256")
        with self.assertRaisesRegex(ge.GardesE0Refusees, "ligne 8 \\(ÉCHEC : résultat externe non scellé"):
            self.table(cfg.lire_configuration_v54(conf, base=self.tmp))

    def test_seconde_version_exige_l_attestation_de_la_premiere(self):
        conf = A.configuration_pre_pilote(self.tmp)
        conf["prepilote"]["temoins"]["version"] = 2
        with self.assertRaisesRegex(cfg.ConfigurationRefusee, "sortie_v1 exigée"):
            pp.verifier_configuration_pre_pilote_v55(cfg.lire_configuration_v54(conf, base=self.tmp))
        ad = A.adaptateurs()
        ad["claude"].decider = lambda r, c, m, n: ({"texte": json.dumps({"notable": True, "item": None, "defaut_present": True})}
                                                   if "RELECTEUR" in c else None)
        with self.assertRaises(NoeudArret):
            self.pp(ad=ad, nom="v1").executer()
        att = os.path.join(self.tmp, "v1", pp.ATTESTATION_V1)
        conf["pieces"]["attestation_v1"] = {"chemin": att, "sha256": hashlib.sha256(open(att, "rb").read()).hexdigest()}
        conf["prepilote"]["temoins"]["sortie_v1"] = "attestation_v1"
        self.assertTrue(pp.verifier_configuration_pre_pilote_v55(cfg.lire_configuration_v54(conf, base=self.tmp)))
        faux = A.piece_scellee(os.path.join(self.tmp, "faux"), "att.json", {"version": pp.VERSION, "version_temoins_epuisee": 2,
                                                                            "noeud": "É5bis"})
        conf["pieces"]["attestation_v1"] = faux
        with self.assertRaisesRegex(cfg.ConfigurationRefusee, "attestation d'un nœud"):
            pp.verifier_configuration_pre_pilote_v55(cfg.lire_configuration_v54(conf, base=self.tmp))


# --- CL19-07 : S6 ---------------------------------------------------------------------------------------------------------


class TestCL19_07S6(Base):
    SQ = {"ancres": ["valeur 12", "seuil 0,3"], "couples": [["défaut A", "défaut B"]]}

    def test_cas_sain_et_artefacts_unitaires(self):
        r = lambda t: {"contenu": {"a": t, "b": "défaut A", "c": "défaut B"}}  # noqa: E731
        self.assertEqual(pp.controle_ancres_v55(r("valeur 12 ; seuil 0,3."), self.SQ), {"ancres": 1.0, "couples": 1.0, "nombres_ajoutes": 0})
        for t in ("valeur 123 ; seuil 0,3", "valeur 12 ; seuil 0,35", "valeur 125 ; seuil 0,3", "valeur 12x ; seuil 0,3",
                  "contrevaleur 12 ; seuil 0,3", "valeur 12.5 ; seuil 0,3", "valeur 12,5 ; seuil 0,3"):
            with self.subTest(t):
                self.assertEqual(pp.controle_ancres_v55(r(t), self.SQ)["ancres"], 0.5)
        self.assertEqual(pp54.controle_ancres(r("valeur 123 ; seuil 0,35"), self.SQ)["ancres"], 1.0)  # le défaut v54
        self.assertEqual(pp.controle_ancres_v55(r("valeur 12 ; seuil 0,3 ; 40 cas"), self.SQ)["nombres_ajoutes"], 1)

    def test_artefact_extension_d_un_nombre_dans_le_flux(self):
        ad = metteur(A.adaptateurs(), lambda t, c: t.replace(" : valeur 7", " : valeur 77"))
        g = self.pp(ad=ad)
        with self.assertRaisesRegex(NoeudArret, "A5"):
            g.executer()
        self.assertTrue(any("fidélité sous S6" in m for m in self.fin()["exclus"].values()))

    def test_artefact_nombre_ajoute_dans_le_flux(self):
        def ajoute(t, c):
            o = json.loads(t)
            o["fiches"][0]["methode"] += " sur 999 cas"
            return json.dumps(o, ensure_ascii=False)
        g = self.pp(ad=metteur(A.adaptateurs(), ajoute))
        with self.assertRaisesRegex(NoeudArret, "A5"):
            g.executer()
        self.assertTrue(any("nombre(s) ajouté(s)" in m for m in self.fin()["exclus"].values()))


# --- CL19-08 : gardes rejouées avec leur artefact ; type d'exception -------------------------------------------------------


class TestCL19_08Artefacts(Base):
    def test_arrete_exige_le_type_et_le_motif(self):
        def leve(e):
            raise e
        self.assertTrue(ge._arrete(lambda: leve(b54.BisociationRefusee("hors grille")), b54.BisociationRefusee, "hors grille"))
        self.assertFalse(ge._arrete(lambda: leve(KeyError("x")), b54.BisociationRefusee))
        self.assertFalse(ge._arrete(lambda: leve(b54.BisociationRefusee("autre")), b54.BisociationRefusee, "hors grille"))
        self.assertFalse(ge._arrete(lambda: None, Exception))

    def test_ligne_21_artefacts_reels(self):
        conf = self.conf_course()
        decl, params = c2.declarer_bras_v55(conf)
        self.assertTrue(c2.verifier_bascule_gk(decl, copy.deepcopy(decl)))
        with self.assertRaisesRegex(c2.BasculeGuKrennInterdite, "absente"):
            c2.verifier_bascule_gk({"basique": {}}, decl)
        d2 = copy.deepcopy(decl)
        d2["gu_krenn"]["mode"] = "modèle"
        with self.assertRaisesRegex(c2.BasculeGuKrennInterdite, "changée"):
            c2.verifier_bascule_gk(decl, d2)
        orig = ge.verifier_bascule_gk
        ge.verifier_bascule_gk = lambda *a: True  # garde neutralisée : la ligne 21 doit échouer à É0
        try:
            with self.assertRaisesRegex(ge.GardesE0Refusees, "ligne 21 \\(ÉCHEC"):
                ge.rejouer_gardes_v55(conf, decl, params)
        finally:
            ge.verifier_bascule_gk = orig

    def test_ligne_21_declaration_changee_en_route_arret(self):
        g = self.gen()
        orig = g.etape_aiguillage

        def change(etat):
            orig(etat)
            g.bras_decl["gu_krenn"] = dict(g.bras_decl["gu_krenn"], mode="modèle")
        g.etape_aiguillage = change
        with self.assertRaisesRegex(c2.BasculeGuKrennInterdite, "changée après É0"):
            g.executer()

    def test_ligne_22b_artefacts_reels(self):
        conf = self.conf_course()
        decl, params = c2.declarer_bras_v55(conf)
        orig = ge.b55.lire_annexe_meta_v55
        ge.b55.lire_annexe_meta_v55 = lambda *a, **k: (params["meta"], None)  # lecture neutralisée
        try:
            with self.assertRaisesRegex(ge.GardesE0Refusees, "ligne 22b \\(ÉCHEC"):
                ge.rejouer_gardes_v55(conf, decl, params)
        finally:
            ge.b55.lire_annexe_meta_v55 = orig


# --- CL19-09 : I-9 et spécification ----------------------------------------------------------------------------------------


class TestCL19_09Annexe(Base):
    def decl(self, conf):
        return c2.declarer_bras_v55(cfg.lire_configuration_v54(conf, base=self.tmp))[0]["meta"]

    def test_cas_sain_brouillon_relu_et_rapport_recalcules(self):
        self.assertTrue(self.decl(A.configuration(self.tmp))["produit"])

    def test_artefacts_empreintes_factices_r000_difference(self):
        conf = A.configuration(self.tmp)
        d = self.sous_dossier("f")
        an = A.A54.annexe_meta(d, nom="factice.md", contre_lecture=f"brouillon relu {'0' * 64} ; rapport {'1' * 64}")
        conf["bisociateur"]["meta"]["annexe"].update(chemin=an["chemin"], sha256=an["sha256"])
        self.assertIn("ne cite pas l'empreinte", self.decl(conf)["motif"])
        conf = A.configuration(self.tmp)
        conf["bisociateur"]["meta"]["annexe"].pop("brouillon_relu")
        self.assertIn("brouillon relu non fourni", self.decl(conf)["motif"])
        conf = A.avec_annexe_v55(A.configuration(self.tmp), self.sous_dossier("r0"))
        m = conf["bisociateur"]["meta"]["annexe"]
        an = A.A54.annexe_meta(self.sous_dossier("r0b"), nom="r000.md", approbation_lazar="R-000",
                               contre_lecture=f"essai {m['brouillon_relu']['sha256']} {m['rapport_contre_lecture']['sha256']}")
        m.update(chemin=an["chemin"], sha256=an["sha256"])
        self.assertIn("non nul", self.decl(conf)["motif"])
        conf = A.avec_annexe_v55(A.configuration(self.tmp), self.sous_dossier("pd"))
        m = conf["bisociateur"]["meta"]["annexe"]
        an = A.A54.annexe_meta(self.sous_dossier("pdb"), nom="poids.md", poids=0.9, approbation_lazar="R-901",
                               contre_lecture=f"essai {m['brouillon_relu']['sha256']} {m['rapport_contre_lecture']['sha256']}")
        m.update(chemin=an["chemin"], sha256=an["sha256"])
        self.assertIn("paramètres de l'annexe différents", self.decl(conf)["motif"])

    def test_specification_recalculee_au_lancement(self):
        self.assertTrue(cfg.verifier_specification(RACINE)["conforme"] in (True, None))
        self.assertIsNone(cfg.verifier_specification(self.tmp)["conforme"])
        conf = A.configuration(self.tmp)
        ch = os.path.join(self.tmp, "conf.json")
        with open(ch, "w", encoding="utf-8") as f:
            json.dump(conf, f, ensure_ascii=False)
        code, _, err = TestLanceurV7.lancer(self, ["--course-2", ch, os.path.join(self.tmp, "x"), "--generations", "1", "--moteur",
                                                    "reel", "--registre-go", "x"], depart=self.tmp)
        self.assertEqual(code, 2)
        self.assertIn("CL19-09", err)


# --- CL19-10 : écarts déclarés, A2, causes de C12 ---------------------------------------------------------------------------


class TestCL19_10Ecarts(Base):
    def test_a2_modele_servi_absent_arret(self):
        g = self.gen(ad=A.adaptateurs(kimi=lambda r, c, m, n: {"modele_servi": None}))
        with self.assertRaisesRegex(ModeleServiAbsent, "A2"):
            g.executer()

    def test_cas_sain_modele_servi_lu(self):
        self.gen().executer()
        self.assertIsNone(self.fin()["arret"])

    def test_causes_iii_iv_de_m9(self):
        g = self.gen()
        l = [x["etiquette"] for x in g.conf["lecteurs_etiquettes"]]
        g.etiquettes = {b: {l[0]: {}, l[1]: {}} for b in ("meta", "gu_krenn")}
        fiches = [{"ident": "fa", "contenu": {}, "meta": {"case": ["t", "b"]}}, {"ident": "fb", "contenu": {}, "meta": {"case": ["t", "b"]}}]
        _, _, causes = g._notes(fiches)
        self.assertEqual(causes["meta"], "non produit (moins de 2 fiches étiquetées)")
        self.assertEqual(causes["gu_krenn"], "non produit (moins de 2 fiches notables)")


# --- CL19-11 : machine jetable ---------------------------------------------------------------------------------------------


class TestCL19_11MachineJetable(unittest.TestCase):
    def test_noms(self):
        base = {"POLE_MACHINE_JETABLE_V54": "1", "PATH": "/usr/bin"}
        self.assertTrue(exiger_machine_jetable_v55(dict(base, TOKENIZERS_PARALLELISM="false")))
        for nom in ("GH_PAT", "OPENAI_KEY_FILE", "SSH_AUTH_SOCK", "AUTH", "NPM_CONFIG__AUTH", "ANTHROPIC_API_KEY", "MON_TOKEN"):
            with self.subTest(nom):
                with self.assertRaisesRegex(MachineNonJetable, nom):
                    exiger_machine_jetable_v55(dict(base, **{nom: "x"}))


# --- CL19-12 ---------------------------------------------------------------------------------------------------------------


class TestCL19_12Mineurs(Base):
    def test_entree_de_rendu_gardee_entiere(self):
        conf = A.configuration_pre_pilote(self.tmp)
        conf["pieces"]["consigne_rendu"] = A.ecrire(os.path.join(self.tmp, "pp", "rendu-fautif.md"), "Mets en forme ce témoin (essai).")
        g = self.pp(self.conf_pp(conf))
        with self.assertRaisesRegex(EtiquetteDansEntree, "entrée complète d'un rendu"):
            g.executer()

    def test_relecteur_muet_non_relu_pas_ambigu(self):
        ad = A.adaptateurs()
        ad["claude"].decider = lambda r, c, m, n: ({"texte": "illisible"} if "RELECTEUR" in c else None)
        conf = A.configuration_pre_pilote(self.tmp)
        conf["arrets"]["a3_echecs_consecutifs"] = 99
        conf["arrets"]["a14_part_max"] = 1.0
        g = self.pp(self.conf_pp(conf), ad)
        with self.assertRaisesRegex(NoeudArret, "A6 : P primaires 0"):
            g.executer()
        e5 = self.fin()["e5"]
        self.assertEqual(e5["ambigus"], 0)
        self.assertEqual(e5["non_relus"], 10)

    def test_coherence_d_g(self):
        conf = cfg.lire_configuration_v54(A.configuration_pre_pilote(self.tmp), base=self.tmp)
        conf["decisions_a15"] = {k: "mot de Lazar (essai)" for k in ("confidentialite", "d_f", "d_h", "d_i", "d_j", "go_lancement")}
        conf["decisions_a15"]["d_g"] = "(a) texte de base"
        self.assertTrue(any("CL19-12" in m for m in cfg.verifier_dependances_lancement_v55(conf, "pre_pilote")))
        conf["decisions_a15"]["d_g"] = "(b) configuration recommandée"
        self.assertFalse(any("CL19-12" in m for m in cfg.verifier_dependances_lancement_v55(conf, "pre_pilote")))


# --- CL19-13 : couverture -------------------------------------------------------------------------------------------------


class TestCL19_13Couverture(Base):
    def test_s18_evaluee_dans_le_flux(self):
        conf = A.configuration_pre_pilote(self.tmp)
        conf["prepilote"]["controles_forme"]["s18_effectif_min"] = 2
        conf["prepilote"]["controles_forme"]["s18_aire_max"] = 1.0
        g = self.pp(self.conf_pp(conf))
        g.executer()
        self.assertIsNotNone(self.fin()["e5"]["s18"]["aire"])

    def test_reprise_apres_a8_reussie(self):
        compte = {}

        def court_au_premier(t, c):
            compte[c] = compte.get(c, 0) + 1
            if compte[c] > 1:
                return t
            o = json.loads(t)
            o["fiches"][0]["methode"] = o["fiches"][0]["methode"][:2500]
            return json.dumps(o, ensure_ascii=False)
        g = self.pp(ad=metteur(A.adaptateurs(), court_au_premier))
        g.executer()
        fin = self.fin()
        g_ = A.configuration_pre_pilote(self.sous_dossier("c"))["prepilote"]["temoins"]["classes"]["G"]  # G : exemptée d'A8
        self.assertEqual(sum(1 for e in fin["evenements"] if e["evenement"] == "rendu-refait"), 10 - g_)
        self.assertEqual(fin["rendus"], 10)
        self.assertFalse(any("A8" in m for m in fin["exclus"].values()))


# --- lanceur v7, R12 -------------------------------------------------------------------------------------------------------


class TestLanceurV7(CasAvecDossier):
    def lancer(self, argv, env=None, etage1=None, depart=None):
        import contextlib
        import importlib.util
        import io
        spec = importlib.util.spec_from_file_location("ideation_v7_essai", os.path.join(RACINE, "demonstrations", "ideation_v7.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        err, out = io.StringIO(), io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
            code = m.principal(argv, environnement=env if env is not None else {"PATH": "/usr/bin"}, etage1=etage1,
                               depart_specification=depart)
        return code, out.getvalue(), err.getvalue()

    def test_course_et_pre_pilote_simules(self):
        conf = A.configuration(self.tmp)
        conf["simulation"] = {"cout_par_appel_usd": 0.01}
        ch = os.path.join(self.tmp, "c.json")
        with open(ch, "w", encoding="utf-8") as f:
            json.dump(conf, f, ensure_ascii=False)
        code, out, err = self.lancer(["--course-2", ch, os.path.join(self.tmp, "sc"), "--generations", "2", "--moteur", "simule"])
        self.assertEqual(code, 0, err)
        conf = A.avec_externes(self.tmp, A.configuration_pre_pilote(self.tmp))
        conf["simulation"] = {"cout_par_appel_usd": 0.01}
        ch = os.path.join(self.tmp, "p.json")
        with open(ch, "w", encoding="utf-8") as f:
            json.dump(conf, f, ensure_ascii=False)
        code, _, err = self.lancer(["--pre-pilote", ch, os.path.join(self.tmp, "sp"), "--verifier-seulement"])
        self.assertEqual(code, 2)
        self.assertIn("DEP3", err)
        code, out, err = self.lancer(["--pre-pilote", ch, os.path.join(self.tmp, "sp"), "--moteur", "simule"], etage1=A.EtageUnFactice())
        self.assertEqual(code, 0, err)
        self.assertTrue(os.path.isfile(os.path.join(self.tmp, "sp", "analyse-m1.json")))

    def test_ligne_de_go_v55_au_lanceur(self):
        conf = A.configuration(self.tmp, budget__plafond_usd=45.0, budget__arret_etape_usd=40.0)
        conf["pieces"]["dep4"] = A.ecrire(os.path.join(self.tmp, "p", "dep4.md"), "DEP4 confirmée (essai).")
        conf["dependances"] = {"dep4": "dep4", "dep4_phrase": "DEP4 confirmée"}
        ch = os.path.join(self.tmp, "c.json")
        with open(ch, "w", encoding="utf-8") as f:
            json.dump(conf, f, ensure_ascii=False)
        for k, (plafond, motif) in enumerate((("1 045 USD", "pas exactement"), ("10-45 USD", "nombre étranger"),
                                              ("45 USD", "--confirmer-moteur-reel"))):
            with self.subTest(plafond):
                reg = A.registre_go(self.sous_dossier(f"g{k}"), A.ligne_go("GO-2026-10-31-09", plafond))
                code, _, err = self.lancer(["--course-2", ch, os.path.join(self.tmp, "s"), "--generations", "1", "--moteur", "reel",
                                            "--registre-go", reg], env={"PATH": "/usr/bin", "GO_ID": "GO-2026-10-31-09"},
                                           depart=RACINE)
                self.assertEqual(code, 2)
                if cfg.verifier_specification(RACINE)["conforme"]:
                    self.assertIn(motif, err)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "s")))


class TestBancMutationsV55(Base):
    """CL19-08 : le banc recompile une méthode qui appelle `super()` sans perdre `__class__` ; il classe la raison de l'échec."""

    def test_super_conserve_et_raison_verifiee(self):
        import aides
        import essais.aides as ea
        avant = (aides.BASE, ea.BASE)
        try:
            import mutations_v55 as M
        finally:
            aides.BASE, ea.BASE = avant
        frag = "super().__init__(conf, sortie, adaptateurs, numero=1, go=go, horloge=horloge)"
        restaurer = M.appliquer(pp54.PrePiloteV54, "__init__", frag, frag + "  # recompilée")
        try:
            g = self.pp()  # PrePiloteV55 → PrePiloteV54.__init__ recompilé → super() : aucune erreur de cellule
            self.assertTrue(os.path.isdir(g.coffre.dossier))
            with self.assertRaisesRegex(pp.EtageUnAbsent, "DEP3"):
                self.pp(nom="s2", etage1=None)
        finally:
            restaurer()
        self.assertEqual(M.classer([], "x"), "SURVIVANTE")
        self.assertEqual(M.classer([("t", "RuntimeError: super(): __class__ cell not found")], "EtageUnAbsent not raised"),
                         "DÉFAUT DU BANC")
        self.assertEqual(M.classer([("t", "AssertionError: autre chose")], "EtageUnAbsent not raised"), "TUÉE POUR UNE AUTRE RAISON")
        self.assertEqual(M.classer([("t", "AssertionError: EtageUnAbsent not raised")], "EtageUnAbsent not raised"), "tuée")


class TestR12V55(unittest.TestCase):
    def test_aucun_fichier_de_la_v54_modifie(self):
        liste = os.path.join(RACINE, "EMPREINTES-orchestrateur-pole-v7-v54.txt")
        n = 0
        with open(liste, encoding="utf-8") as f:
            for ligne in f:
                sha, rel = ligne.rstrip("\n").split("  ", 1)
                with open(os.path.join(RACINE, rel), "rb") as g:
                    self.assertEqual(hashlib.sha256(g.read()).hexdigest(), sha, rel)
                n += 1
        self.assertEqual(n, 387)


if __name__ == "__main__":
    unittest.main()
_ = ecrire_json_scelle
