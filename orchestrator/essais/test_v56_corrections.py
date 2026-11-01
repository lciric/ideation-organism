"""Essais de la v56 — corrections de la contre-lecture CL20 (CL20-01 à CL20-15) et interrupteur A21 « en attente de N5 ».
Hors ligne ; moteur simulé v56, et **vrai** adaptateur de commande externe sur une commande factice locale (interpréteur
courant, `-I`, aucun réseau, aucune clé) ; chaque garde neuve : un cas sain et un artefact (R5). Aucun fichier hors de l'arbre
n'est lu (CL20-15) ; tout est écrit dans un dossier temporaire."""

import copy
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
import unittest

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)

import aides_v56 as A  # noqa: E402
from aides import CasAvecDossier  # noqa: E402
from pole import adaptateurs_v56 as ad56  # noqa: E402
from pole import budget_v56 as bv  # noqa: E402
from pole import configuration_v56 as cfg  # noqa: E402
from pole import course2_v56 as c2  # noqa: E402
from pole import gardes_e0_v56 as ge  # noqa: E402
from pole import noyau_v56 as nv  # noqa: E402
from pole import prepilote_v56 as pp  # noqa: E402
from pole.adaptateurs import AdaptateurClaudeSDK, AdaptateurCommandeExterne  # noqa: E402
from pole.etage_entre_generations_v53 import MachineNonJetable  # noqa: E402
from pole.etage_entre_generations_v56 import exiger_machine_jetable_v56  # noqa: E402
from pole.noyau_v54 import NoeudArret  # noqa: E402
from pole.noyau_v55 import ModeleServiAbsent, controle_a2  # noqa: E402

ENV = {"PATH": os.defpath}  # environnement minimal explicite des portes (aucun nom de clé)
CHAMPS_JSON, ITEMS_JSON = json.dumps(A.CHAMPS), json.dumps(A.ITEMS)


def lire(chemin):
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


ARGON_SIMULE = r'''import json, os, sys
sys.path.insert(0, sys.argv[1])
from pole.simulation_v56 import AdaptateurSimuleV56
consigne = sys.stdin.read()
role, modele = os.environ.get("ROLE_POLE"), os.environ.get("MODELE_DEMANDE_POLE")
ad = AdaptateurSimuleV56(champs_fiche=json.loads(sys.argv[2]), items=json.loads(sys.argv[3]), cout_par_appel_usd=0.01, champ_titre="titre")
texte = ad.reponse(role, consigne, modele)
with open(sys.argv[4], "a", encoding="utf-8") as f:
    f.write(json.dumps({"etape": os.environ.get("ETAPE_POLE"), "plafond": os.environ.get("PLAFOND_ETAPE_USD"), "role": role}) + "\n")
o = {"texte": texte, "cout_usd": min(0.01, float(os.environ["PLAFOND_SESSION_USD"]))}
if sys.argv[5] == "servi":
    o["modele_servi"] = modele
print(json.dumps(o))
'''


class Base(CasAvecDossier):
    def conf_course(self, **modifs):
        return cfg.lire_configuration_v56(A.configuration(self.tmp, **modifs), base=self.tmp)

    def conf_pp(self, conf=None, **modifs):
        return cfg.lire_configuration_v56(A.avec_externes(self.tmp, conf or A.configuration_pre_pilote(self.tmp, **modifs)), base=self.tmp)

    def gen(self, conf=None, ad=None, nom="s", **kw):
        kw.setdefault("racine_sessions", os.path.join(self.tmp, "sessions-" + nom))
        return c2.GenerationV56(conf or self.conf_course(), os.path.join(self.tmp, nom), ad or A.adaptateurs(), **kw)

    def pp(self, conf=None, ad=None, nom="s", **kw):
        kw.setdefault("etage1", A.EtageUnFactice())
        kw.setdefault("racine_sessions", os.path.join(self.tmp, "sessions-" + nom))
        return pp.PrePiloteV56(conf or self.conf_pp(), os.path.join(self.tmp, nom), ad or A.adaptateurs(), **kw)

    def fin(self, nom="s"):
        return lire(os.path.join(self.tmp, nom, "manifeste-fin.json"))

    def relais(self, conf, **plafonds):
        for e in conf["budget"]["etapes"]:
            if e["nom"] in plafonds:
                e["plafond_relais_usd"] = plafonds[e["nom"]]
        return conf

    def argon_reel(self, servi=True, classe=ad56.AdaptateurCommandeExterneV56):
        script = os.path.join(self.tmp, "argon-simule.py")
        if not os.path.exists(script):
            with open(script, "w", encoding="utf-8") as f:
                f.write(ARGON_SIMULE)
        journal = os.path.join(self.tmp, f"journal-argon-{'servi' if servi else 'sans'}-{classe.__name__}.jsonl")
        cmd = [sys.executable, "-I", "-B", script, RACINE, CHAMPS_JSON, ITEMS_JSON, journal, "servi" if servi else "sans"]
        return classe(cmd, environnement={"PATH": os.defpath}, delai_s=120, exiger_modele_servi=True), journal


# --- CL20-01 : le vrai adaptateur de commande externe recopie le modèle servi ---------------------------------------------------


class TestCL20_01AdaptateurReel(Base):
    M = "gemini-4-argon"

    def lancer(self, classe, objet):
        cmd = A.commande_factice(self.tmp, "cmd-" + hashlib.sha256(json.dumps(objet).encode()).hexdigest()[:8], objet)
        return classe(cmd, environnement={"PATH": os.defpath}, delai_s=60, exiger_modele_servi=True).lancer(
            "juge_ideation", "consigne", self.tmp, 1.0, 1, modele=self.M)

    def test_cas_sain_modele_servi_recopie(self):
        r = self.lancer(ad56.AdaptateurCommandeExterneV56, {"texte": "t", "cout_usd": 0.01, "modele_servi": self.M})
        self.assertEqual((r.statut, r.modele_servi), ("ok", self.M))
        self.assertTrue(controle_a2(r.statut, r.modele_servi, self.M))
        r = self.lancer(ad56.AdaptateurCommandeExterneV56, {"texte": "t", "cout_usd": 0.01, "modele_servi": self.M + "-20261031"})
        self.assertEqual((r.statut, r.modele_servi), ("ok", self.M + "-20261031"))  # suffixe de date strict admis

    def test_artefact_adaptateur_v55_perd_le_modele_servi(self):
        r = self.lancer(AdaptateurCommandeExterne, {"texte": "t", "cout_usd": 0.01, "modele_servi": self.M})
        self.assertEqual((r.statut, r.modele_servi), ("ok", None))  # le défaut reproduit par CL20
        with self.assertRaises(ModeleServiAbsent):
            controle_a2(r.statut, r.modele_servi, self.M)

    def test_artefact_modele_servi_absent_ou_different(self):
        r = ad56.AdaptateurCommandeExterneV56(A.commande_factice(self.tmp, "sans", {"texte": "t", "cout_usd": 0.01}),
                                              environnement={"PATH": os.defpath}, delai_s=60).lancer(
            "juge_ideation", "c", self.tmp, 1.0, 1, modele=self.M)
        self.assertEqual((r.statut, r.modele_servi), ("ok", None))
        r = self.lancer(ad56.AdaptateurCommandeExterneV56, {"texte": "t", "cout_usd": 0.01, "modele_servi": "autre-modele"})
        self.assertEqual(r.statut, "refus")
        self.assertEqual(r.texte_brut, None)

    def test_e0_ligne_1_sur_le_vrai_adaptateur(self):
        self.assertEqual(ge.ligne_1_adaptateur_reel(), (True, True))

    def test_flux_complet_argon_par_le_vrai_adaptateur(self):
        argon, journal = self.argon_reel(servi=True)
        ad = A.adaptateurs()
        ad["argon"] = argon
        g = self.gen(ad=ad, portes={"argon": ad56.PortePlafondEnvironnement(argon)})
        res = g.executer()
        fin = self.fin()
        self.assertIsNone(fin["arret"])
        self.assertIsNone(fin["noeud"])
        self.assertEqual(fin["roles_arretes_a2"], {})
        self.assertEqual(fin["juges_absents"]["juge-argon"], 0)
        self.assertEqual(fin["modele_servi_juges"]["juge-argon"], self.M)
        self.assertTrue(res)
        with open(journal, encoding="utf-8") as f:
            lignes = [json.loads(x) for x in f]
        self.assertTrue(lignes)
        durs = fin["budget"]["plafonds_durs_usd"]
        for x in lignes:  # le plafond dur de l'étape, le même pour chaque appel de l'étape (CL20-02)
            self.assertEqual(x["plafond"], f"{durs[x['etape']]:.2f}")

    def test_flux_complet_artefact_adaptateur_v55(self):
        argon, _ = self.argon_reel(servi=True, classe=AdaptateurCommandeExterne)
        ad = A.adaptateurs()
        ad["argon"] = argon
        porte = ad56.PortePlafondCommande(A.porte_factice(self.tmp, "porte-argon"), 30, environnement=ENV)
        g = self.gen(ad=ad, portes={"argon": porte})
        g.executer()
        fin = self.fin()
        self.assertIsNone(fin["arret"])  # CL20-12 : arrêt du rôle, pas de l'exécution
        self.assertIn("prop-argon", fin["roles_arretes_a2"])
        self.assertIn("A2", fin["roles_arretes_a2"]["prop-argon"])


# --- CL20-02 : règle d'A1 du brouillon 10 ------------------------------------------------------------------------------------------


class TestCL20_02Budget(Base):
    PLAN = ge.PLAN_11

    def test_cas_sain_plafond_dur_au_lancement(self):
        b = bv.BudgetV56(10.0, "sans", copy.deepcopy(self.PLAN))
        d, det = b.avant_etape("p")
        self.assertEqual((d, det["plafond_dur_usd"], det["souple"]), (bv.JOUER, 6.5, True))  # max(2 ; 10 − 0 − 3,5)
        b.apres_etape("p", 3.0)  # au-delà du relais (2) sous le plafond dur : jouée, réserve de M7
        self.assertTrue(b.journal[-1]["au_dela_du_plafond_de_relais"])
        d, det = b.avant_etape("s")
        self.assertEqual((det["plafond_dur_usd"], det["souple"]), (1.5, False))  # retirable : relais fixe

    def test_cas_sain_protegee_ne_peut_affamer_les_suivantes(self):
        b = bv.BudgetV56(5.0, "sans", copy.deepcopy(self.PLAN))
        _, det = b.avant_etape("p")
        self.assertEqual(b.etapes["s"]["etat"], bv.RETIREE)  # projection : 0 + 2 + (1 + 2 + 0,5) > 5 → la sacrifiable sort
        self.assertEqual(det["plafond_dur_usd"], 2.5)  # max(2 ; 5 − 0 − (2 + 0,5)) : l'attendu des restantes reste réservé
        self.assertLessEqual(det["plafond_dur_usd"] + 2.0 + 0.5, 5.0 + 1e-9)

    def test_cas_sain_generation_plafonds_rejoues(self):
        g = self.gen()
        g.executer()
        fin = self.fin()
        cons = lire(os.path.join(self.tmp, "s", "consommations.json"))["consommations"]
        b = self.conf_course()["budget"]
        _, etat, plafonds = bv.rejouer_consommations_v56(b["plafond_usd"], b["arret_etape_usd"], b["etapes"], cons)
        self.assertEqual(plafonds, fin["budget"]["plafonds_durs_usd"])
        self.assertEqual(fin["relais"]["transmissions"], len(plafonds) * 3)
        self.assertIn("plafond dur", fin["budget"]["regle"])

    def test_artefact_reservation_refusee(self):
        conf = A.configuration(self.tmp)
        conf["budget"]["etapes"][0]["reservation_usd"] = 1.0
        with self.assertRaisesRegex(cfg.ConfigurationRefusee, "reservation_usd refusée"):
            cfg.lire_configuration_v56(conf, base=self.tmp)

    def test_artefact_phrase_dep4_refusee(self):
        conf = A.configuration(self.tmp)
        conf.setdefault("dependances", {})["dep4_phrase"] = "réservation"
        with self.assertRaisesRegex(cfg.ConfigurationRefusee, "dep4_phrase"):
            cfg.lire_configuration_v56(conf, base=self.tmp)

    def test_artefact_relais_reel_sans_porte(self):
        argon, _ = self.argon_reel()
        ad = A.adaptateurs()
        ad["argon"] = argon
        with self.assertRaisesRegex(ad56.RelaisSansPlafond, "A15"):
            self.gen(ad=ad)
        with self.assertRaisesRegex(ad56.RelaisSansPlafond, "noyau"):
            self.gen(ad=ad, nom="s2", portes={"argon": ad56.PortePlafondNoyau()})

    def test_cas_sain_porte_commande(self):
        p = ad56.PortePlafondCommande(A.porte_factice(self.tmp, "porte-ok"), 30, environnement=ENV)
        self.assertEqual(p.transmettre("juges", 12.345)["plafond_usd"], 12.34)

    def test_artefacts_porte_commande(self):
        faux = ad56.PortePlafondCommande(A.porte_factice(self.tmp, "porte-faux", accuse={"etape": "juges", "plafond_usd": 12.33}), 30, environnement=ENV)
        with self.assertRaisesRegex(ad56.RelaisSansPlafond, "accuse"):
            faux.transmettre("juges", 12.34)
        autre = ad56.PortePlafondCommande(A.porte_factice(self.tmp, "porte-autre", accuse={"etape": "x", "plafond_usd": 12.34}), 30, environnement=ENV)
        with self.assertRaisesRegex(ad56.RelaisSansPlafond, "autre étape"):
            autre.transmettre("juges", 12.34)
        code = ad56.PortePlafondCommande(A.porte_factice(self.tmp, "porte-code", code=3), 30, environnement=ENV)
        with self.assertRaisesRegex(ad56.RelaisSansPlafond, "code 3"):
            code.transmettre("juges", 1.0)
        lent = os.path.join(self.tmp, "porte-lente.py")
        with open(lent, "w", encoding="utf-8") as f:
            f.write("import time\ntime.sleep(30)\n")
        with self.assertRaisesRegex(ad56.RelaisSansPlafond, "délai"):
            ad56.PortePlafondCommande([sys.executable, "-I", lent], 0.5, environnement=ENV).transmettre("juges", 1.0)

    def test_artefact_porte_qui_accuse_faux_arrete_avant_tout_appel(self):
        argon, _ = self.argon_reel()
        ad = A.adaptateurs()
        ad["argon"] = argon
        faux = ad56.PortePlafondCommande(A.porte_factice(self.tmp, "porte-f", accuse={"etape": "proposition", "plafond_usd": 0.5}), 30, environnement=ENV)
        g = self.gen(ad=ad, portes={"argon": faux})
        with self.assertRaises(ad56.RelaisSansPlafond):
            g.executer()
        fin = self.fin()
        self.assertIn("A15", fin["arret"])
        self.assertEqual(fin["etapes"]["proposition"], bv.NON_MESUREE)
        self.assertEqual(fin["budget"]["cumul_usd"], 0.0)

    def test_artefact_plafond_different_du_second_programme(self):
        g = self.gen()
        orig = g.budget.plafond_dur
        g.budget.plafond_dur = lambda nom: (orig(nom)[0] + 0.01, orig(nom)[1])
        with self.assertRaisesRegex(bv.PlafondDeRelaisFaux, "11a"):
            g.executer()
        self.assertIn("PlafondDeRelaisFaux", self.fin()["arret"])

    def test_artefact_second_programme_et_formule_independante(self):
        orig_r, orig_p = nv.rejouer_consommations_v56, nv.plafond_independant

        def rejeu_faux(*a, **k):
            d, e, p = orig_r(*a, **k)
            return d, e, {n: v + 0.01 for n, v in p.items()}
        try:
            nv.rejouer_consommations_v56 = rejeu_faux
            with self.assertRaisesRegex(bv.PlafondDeRelaisFaux, "second programme"):
                self.gen(nom="a").executer()
            nv.rejouer_consommations_v56 = orig_r
            nv.plafond_independant = lambda *a, **k: (orig_p(*a, **k)[0] + 0.01, orig_p(*a, **k)[1])
            with self.assertRaisesRegex(bv.PlafondDeRelaisFaux, "formule indépendante"):
                self.gen(nom="b").executer()
        finally:
            nv.rejouer_consommations_v56, nv.plafond_independant = orig_r, orig_p

    def test_artefact_porte_injectee_qui_accuse_un_autre_plafond(self):
        class PorteFausse:
            def transmettre(self, etape, plafond):
                return {"etape": etape, "plafond_usd": plafond - 0.01, "par": "essai"}
        argon, _ = self.argon_reel()
        ad = A.adaptateurs()
        ad["argon"] = argon
        with self.assertRaisesRegex(ad56.RelaisSansPlafond, "accusé du relais"):
            self.gen(ad=ad, portes={"argon": PorteFausse()}).executer()
        self.assertEqual(self.fin()["budget"]["cumul_usd"], 0.0)

    def test_artefact_relais_qui_ne_tient_pas_son_plafond(self):
        from pole.adaptateurs import Resultat
        ad = A.adaptateurs()
        orig = ad["claude"].lancer

        def lancer(role, consigne, dossier, budget_usd, max_tours, modele=None):
            r = orig(role, consigne, dossier, budget_usd, max_tours, modele=modele)
            return Resultat(r.texte_final, [], 100.0, r.statut, texte_brut=r.texte_brut, modele_servi=r.modele_servi)
        ad["claude"].lancer = lancer
        with self.assertRaisesRegex(bv.CumulAuDelaDeS17, "11a"):
            self.gen(ad=ad).executer()
        fin = self.fin()
        self.assertIn("CumulAuDelaDeS17", fin["arret"])
        self.assertGreater(fin["budget"]["cumul_usd"], 50.0)  # jamais écrêté

    def test_coupure_d_une_protegee_non_mesure_et_noeud(self):
        conf = A.configuration(self.tmp)
        self.relais(conf, proposition=0.01)
        attendu = sum(e["attendu_usd"] for e in conf["budget"]["etapes"][1:])
        conf["budget"].update(plafond_usd=round(attendu + 0.01, 6), arret_etape_usd="sans")
        g = self.gen(cfg.lire_configuration_v56(conf, base=self.tmp))
        g.executer()
        fin = self.fin()
        self.assertEqual(fin["budget"]["plafonds_durs_usd"]["proposition"], 0.01)
        self.assertEqual(fin["etapes"]["proposition"], bv.NON_MESUREE)
        self.assertIn("C13", fin["noeud"])

    def test_cas_sain_e0_lignes_11a_11b(self):
        self.assertEqual(ge.ligne_11a(), (True, True))
        self.assertEqual(ge.ligne_11b(), (True, True))

    def test_e9_entiere_coupee_lue_reduite_ou_non_mesuree(self):
        def lancer(relais, nom):
            conf = A.configuration_pre_pilote(os.path.join(self.tmp, nom + "-c"))
            self.relais(conf, e9_anteriorite=relais)
            os.makedirs(os.path.join(self.tmp, nom + "-c"), exist_ok=True)
            conf = cfg.lire_configuration_v56(A.avec_externes(os.path.join(self.tmp, nom + "-c"), conf), base=self.tmp)
            g = self.pp(conf, nom=nom)
            try:
                g.executer()
            except NoeudArret:
                pass
            return self.fin(nom), lire(os.path.join(self.tmp, nom, "consommations.json"))["consommations"]
        fin, cons = lancer(0.025, "lue")  # les deux fiches de la réduction vérifiées, puis coupure
        self.assertEqual(fin["etapes"]["e9_anteriorite"], "jouee")
        self.assertTrue(fin["budget"]["etapes"]["e9_anteriorite"]["reduite"])
        self.assertTrue(any(c.get("lue_reduite") is True for c in cons))
        fin, _ = lancer(0.01, "non")  # une seule fiche de la réduction vérifiée : « non mesuré (budget) »
        self.assertEqual(fin["etapes"]["e9_anteriorite"], bv.NON_MESUREE)
        self.assertIn("C13", fin["noeud"])


# --- CL20-03 : spécification scellée -----------------------------------------------------------------------------------------------


class TestCL20_03Specification(Base):
    def conf_spec(self, **kw):
        conf = A.configuration(self.tmp)
        conf["specification"] = A.specification(self.tmp, **kw)
        return cfg.lire_configuration_v56(conf, base=self.tmp)

    def test_cas_sain_scellee_et_ecrite_au_manifeste(self):
        conf = self.conf_spec()
        spec = cfg.verifier_specification_v56(conf)
        self.assertTrue(spec["conforme"])
        decl, params = c2.declarer_bras_v56(conf)
        t = {x["ligne"]: x["statut"] for x in ge.rejouer_gardes_v56(conf, decl, params, specification=spec)}
        self.assertEqual(t["29"], ge.REJOUEE)
        self.gen(conf, specification=spec).executer()
        dep = lire(os.path.join(self.tmp, "s", "manifeste-depart.json"))
        self.assertEqual(dep["specification"]["preenregistrement"]["sha256"], conf["specification"]["preenregistrement"]["sha256"])
        self.assertNotIn("brouillon 7", json.dumps(dep["specification"], ensure_ascii=False))

    def test_artefacts(self):
        conf = self.conf_spec(nom="a.md")
        with open(conf["specification"]["preenregistrement"]["chemin"], "a", encoding="utf-8") as f:
            f.write("!")
        self.assertIn("empreinte", cfg.verifier_specification_v56(conf)["motif"])
        self.assertIn("non scellé", cfg.verifier_specification_v56(self.conf_spec(nom="b.md", sceller=False))["motif"])
        self.assertIn("non gelé", cfg.verifier_specification_v56(self.conf_spec(nom="c.md", marqueur=True))["motif"])
        self.assertIn("ne cite pas", cfg.verifier_specification_v56(self.conf_spec(nom="d.md", cite=False))["motif"])
        conf = self.conf_spec(nom="e.md", marqueur=True)
        decl, params = c2.declarer_bras_v56(conf)
        with self.assertRaisesRegex(ge.GardesE0Refusees, "ligne 29"):
            ge.rejouer_gardes_v56(conf, decl, params, specification=cfg.verifier_specification_v56(conf))
        self.assertEqual(ge.ligne_29_specification(self.conf_spec(nom="f.md"), {"conforme": True}), (True, True))


# --- CL20-04 : arrêt propre sur signal ---------------------------------------------------------------------------------------------


def tuer_a(k, sig=signal.SIGTERM):
    def decider(role, consigne, modele, n):
        if n == k:
            os.kill(os.getpid(), sig)
        return None
    return decider


class TestCL20_04Signal(Base):
    def verifier_arret(self, nom, motif):
        fin = self.fin(nom)
        self.assertIn(motif, fin["arret"])
        self.assertTrue(os.path.exists(os.path.join(self.tmp, nom, "empreintes-sortie.txt")))
        self.assertTrue(os.path.exists(os.path.join(self.tmp, nom, "consommations.json")))
        self.assertTrue(os.path.exists(os.path.join(self.tmp, nom, "fusions-inachevees.json")))
        base = os.path.join(self.tmp, "sessions-" + nom)
        vides = [r for r, ds, fs in os.walk(base) if not ds and not fs] if os.path.isdir(base) else []
        self.assertEqual(vides, [])  # aucun dossier de session orphelin
        return fin

    def test_cas_sain_aucun_signal(self):
        avant = signal.getsignal(signal.SIGTERM)
        self.gen().executer()
        fin = self.fin()
        self.assertIsNone(fin["arret"])
        self.assertEqual(fin["signaux"]["recu"], None)
        self.assertTrue(fin["signaux"]["installe"])
        self.assertIs(signal.getsignal(signal.SIGTERM), avant)

    def test_artefact_sigterm_pendant_un_appel(self):
        ad = A.adaptateurs(claude=tuer_a(5))
        with self.assertRaises(nv.ArretParSignal):
            self.gen(ad=ad).executer()
        fin = self.verifier_arret("s", "SIGTERM")
        self.assertEqual(fin["signaux"]["recu"], "SIGTERM")

    def test_artefact_interruption_clavier(self):
        def decider(role, consigne, modele, n):
            if n == 3:
                raise KeyboardInterrupt
        with self.assertRaises(KeyboardInterrupt):
            self.gen(ad=A.adaptateurs(kimi=decider)).executer()
        self.verifier_arret("s", "interruption clavier")

    def test_artefact_sigint_pre_pilote(self):
        with self.assertRaises(nv.ArretParSignal):
            self.pp(ad=A.adaptateurs(claude=tuer_a(9, signal.SIGINT))).executer()
        self.verifier_arret("s", "SIGINT")

    def test_artefact_sigterm_par_pid_depuis_l_exterieur(self):
        pret = os.path.join(self.tmp, "pret")
        script = os.path.join(self.tmp, "enfant.py")
        with open(script, "w", encoding="utf-8") as f:
            f.write(f"""import os, sys, time
sys.path[:0] = [{RACINE!r}, {ICI!r}]
import aides_v56 as A
from pole import configuration_v56 as cfg, course2_v56 as c2
t = {self.tmp!r}
def decider(role, consigne, modele, n):
    if n == 12:
        open({pret!r}, "w").close()
        time.sleep(60)
conf = cfg.lire_configuration_v56(A.configuration(os.path.join(t, "conf-enfant")), base=t)
c2.GenerationV56(conf, os.path.join(t, "enfant"), A.adaptateurs(claude=decider), racine_sessions=os.path.join(t, "sessions-enfant")).executer()
""")
        os.makedirs(os.path.join(self.tmp, "conf-enfant"))
        p = subprocess.Popen([sys.executable, "-I", "-B", script], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        fin_attente = time.monotonic() + 120
        while not os.path.exists(pret) and p.poll() is None and time.monotonic() < fin_attente:
            time.sleep(0.05)
        self.assertTrue(os.path.exists(pret), p.stderr.read().decode() if p.poll() is not None else "délai")
        os.kill(p.pid, signal.SIGTERM)  # R10 : par identifiant de processus
        p.wait(60)
        p.stderr.close()
        self.assertNotEqual(p.returncode, 0)
        fin = self.verifier_arret("enfant", "SIGTERM")
        self.assertIsNone(fin["noeud"])


# --- CL20-05 : fusions inachevées archivées, jamais dans l'héritage ---------------------------------------------------------------


class TestCL20_05Fusions(Base):
    def canaux(self, g, res, nom="s"):
        fusions = {f["ident"] for f in g.fusions}
        cl = {l["ident"] for l in lire(os.path.join(self.tmp, nom, "classement.json"))["lignes"]}
        fi = set(lire(os.path.join(self.tmp, nom, "fiches.json")))
        mem = {f["ident"] for f, _ in g.memoire.anciennes}
        her = json.loads(g.texte_heritage(res))
        etage = {l["ident"] for l in res}  # entrée de l'étage : les lignes du classement
        return fusions, cl, fi, mem, her, etage

    def test_cas_sain_fusions_completes_reviennent(self):
        g = self.gen()
        res = g.executer()
        fusions, cl, fi, mem, her, etage = self.canaux(g, res)
        self.assertEqual(len(fusions), 3)
        self.assertTrue(fusions <= cl and fusions <= fi and fusions <= mem and fusions <= etage)
        self.assertEqual(len(her), len(res))
        self.assertEqual(lire(os.path.join(self.tmp, "s", "fusions-inachevees.json"))["fusions"], [])
        self.assertEqual(self.fin()["fusions"]["completes"], 3)

    def _coupe(self, relais, nom):
        conf = self.relais(A.configuration(os.path.join(self.tmp, nom + "-c")), fusions=relais)
        g = self.gen(cfg.lire_configuration_v56(conf, base=self.tmp), nom=nom)
        res = g.executer()
        return g, res

    def test_artefacts_etape_coupee_rien_ne_revient(self):
        for relais, cause in ((0.0, "non écrite"), (0.02, "sans passeport"), (0.04, "non jugée"), (0.07, "jugée en partie"),
                              (0.13, "complète avant la coupure")):
            with self.subTest(relais=relais):
                nom = f"c{int(relais * 100)}"
                g, res = self._coupe(relais, nom)
                fusions, cl, fi, mem, her, etage = self.canaux(g, res, nom)
                self.assertFalse(fusions & (cl | fi | mem | etage))
                self.assertEqual(len(her), len(res))
                arch = lire(os.path.join(self.tmp, nom, "fusions-inachevees.json"))["fusions"]
                self.assertEqual(len(arch), 3)
                self.assertTrue(any(cause in x["cause"] for x in arch), [x["cause"] for x in arch])
                self.assertTrue(all("bras" not in x for x in arch))
                self.assertEqual(self.fin(nom)["etapes"]["fusions"], bv.RETIREE)

    def test_artefact_fusion_incoherente_archivee(self):
        consigne = "Consigne de fusion (essai)."

        def decider(role, c, modele, n):
            if c.startswith(consigne):
                return {"texte": "pas une fiche"}
            return None
        g = self.gen(ad=A.adaptateurs(kimi=decider))
        res = g.executer()
        arch = lire(os.path.join(self.tmp, "s", "fusions-inachevees.json"))["fusions"]
        self.assertTrue(arch)
        self.assertTrue(all(x["cause"].startswith("non écrite (sortie inexploitable") or x["cause"].startswith("incohérente")
                            for x in arch))
        self.assertFalse({f["ident"] for f in g.fusions} & {l["ident"] for l in res})

    def test_artefact_fusion_jugee_en_partie_dans_une_etape_jouee(self):
        g = self.gen()
        orig, drapeau = g.etape_fusions, []

        def etape(etat):
            drapeau.append(True)
            return orig(etat)
        g.etape_fusions = etape
        dec = g.ad["argon"].decider = lambda role, c, m, n: {"statut": "erreur"} if drapeau and role == "juge_ideation" else None
        self.assertIsNotNone(dec)
        res = g.executer()
        arch = lire(os.path.join(self.tmp, "s", "fusions-inachevees.json"))["fusions"]
        self.assertTrue(arch and all("jugée en partie (2 verdict(s) sur 3)" in x["cause"] for x in arch), arch)
        self.assertFalse({f["ident"] for f in g.fusions} & {l["ident"] for l in res})

    def test_entree_du_bisociateur_sans_fusion(self):
        g = self.gen()
        g.executer()
        self.assertTrue(g._entree_bisociateur())  # cas sain : les fiches de la passe 1 y sont
        g.passe1.append(g.fusions[0])  # artefact : une fusion (munie d'un passeport) glissée dans la passe 1
        self.assertFalse([f for f in g._entree_bisociateur() if f["meta"].get("origine") == "fusion"])


# --- CL20-06 : lecture interdite du bac du kit ---------------------------------------------------------------------------------


class TestCL20_06LectureInterdite(Base):
    URL = "http://127.0.0.1:8765"

    def test_cas_sain_sortie_et_coffre_interdits(self):
        base, sortie = self.sous_dossier("base"), os.path.join(self.tmp, "sortie")
        ad = AdaptateurClaudeSDK(self.URL, interdire_lecture=[base, sortie])
        vu = ad56.verifier_lecture_interdite(ad, sortie, os.path.join(base, "sessions"))
        self.assertEqual(set(vu), set(ad56.ROLES_KIT_DU_POLE))
        self.assertIn(sortie, vu["juge_ideation"])

    def test_artefacts(self):
        base, sortie = self.sous_dossier("base"), os.path.join(self.tmp, "sortie")
        for interdits in (None, [base]):
            with self.subTest(interdits=interdits), self.assertRaisesRegex(ad56.LectureNonInterdite, "CL20-06"):
                ad56.verifier_lecture_interdite(AdaptateurClaudeSDK(self.URL, interdire_lecture=interdits), sortie,
                                                os.path.join(base, "sessions"))
        ad = A.adaptateurs()
        ad["claude"] = AdaptateurClaudeSDK(self.URL)
        porte = ad56.PortePlafondCommande(A.porte_factice(self.tmp, "porte-claude"), 30, environnement=ENV)
        with self.assertRaises(ad56.LectureNonInterdite):
            self.gen(ad=ad, portes={"claude": porte})
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "sessions-s", "sessions")))  # sessions rangées

    def test_lanceur_passe_base_et_sortie(self):
        L = TestLanceurV8.module()
        base, sortie = self.sous_dossier("b"), os.path.join(self.tmp, "o")
        porte = {"type": "commande", "commande": A.porte_factice(self.tmp, "p"), "delai_s": 5}
        conf = {"fournisseurs": {"claude": {"type": "claude_sdk", "url_relais": self.URL, "porte_plafond": porte},
                                 "argon": {"type": "commande_externe", "commande": ["/bin/true"], "porte_plafond": {"type": "environnement"}}}}
        ads, portes = L.adaptateurs_reels_v56(conf, sortie, base)
        self.assertEqual(ads["claude"].interdire_lecture, [os.path.realpath(base), os.path.realpath(sortie)])
        self.assertIsInstance(ads["argon"], ad56.AdaptateurCommandeExterneV56)
        self.assertIsInstance(portes["argon"], ad56.PortePlafondEnvironnement)
        del conf["fournisseurs"]["claude"]["porte_plafond"]
        with self.assertRaisesRegex(ad56.RelaisSansPlafond, "A15"):
            L.adaptateurs_reels_v56(conf, sortie, base)


# --- CL20-07 : D-i ; N5 : interrupteur A21 -------------------------------------------------------------------------------------


class TestCL20_07DiEtN5(Base):
    def test_cas_sain_d_i_1(self):
        self.assertTrue(pp.verifier_configuration_pre_pilote_v56(self.conf_pp()))

    def test_artefacts_d_i(self):
        for v, motif in ((2, "non codée"), (3, "non codée"), (None, "d_i"), (True, "d_i")):
            with self.subTest(d_i=v), self.assertRaisesRegex(cfg.ConfigurationRefusee, motif):
                pp.verifier_configuration_pre_pilote_v56(self.conf_pp(prepilote__d_i=v))
        conf = self.conf_pp()
        conf["decisions_a15"] = {k: "oui (essai)" for k in ("confidentialite", "d_f", "d_h", "d_j", "go_lancement")}
        conf["decisions_a15"].update(d_g="(b) essai", d_i="(2) essai")
        m = cfg.verifier_dependances_lancement_v56(conf, "pre_pilote")
        self.assertTrue(any("CL20-07" in x for x in m))
        conf["decisions_a15"]["d_i"] = "(1) essai"
        self.assertFalse(any("CL20-07" in x for x in cfg.verifier_dependances_lancement_v56(conf, "pre_pilote")))

    def test_n5_defaut_comportement_v55(self):
        self.pp().executer()
        dep = lire(os.path.join(self.tmp, "s", "manifeste-depart.json"))
        self.assertIn("programme_journalise", dep["a21_lecture"])
        self.assertIn("N5", dep["a21_lecture"])
        self.assertTrue(pp.verifier_configuration_pre_pilote_v56(self.conf_pp(prepilote__a21_lecture="programme_journalise")))

    def test_n5_artefacts(self):
        with self.assertRaisesRegex(cfg.ConfigurationRefusee, "en attente de N5"):
            pp.verifier_configuration_pre_pilote_v56(self.conf_pp(prepilote__a21_lecture="stricte"))
        with self.assertRaisesRegex(cfg.ConfigurationRefusee, "a21_lecture"):
            pp.verifier_configuration_pre_pilote_v56(self.conf_pp(prepilote__a21_lecture="autre"))


# --- CL20-08 : M6b écrite par le rédacteur en É1 ; CL20-09 ----------------------------------------------------------------------


class TestCL20_08M6b(Base):
    def test_cas_sain_flux_complet(self):
        vues = []

        def espion(role, c, modele, n):
            if "VERIFICATEUR M6b" in c or "## Source M6b" in c:
                vues.append(c)
        g = self.pp(ad=A.adaptateurs(claude=espion))
        g.executer()
        fiches = lire(os.path.join(self.tmp, "s", "temoins", "m6b-fiches.json"))
        self.assertEqual(len(fiches), 4)
        self.assertEqual(self.fin()["m6b"]["fiches_ecrites_e1"], 4)
        verif = [c for c in vues if "VERIFICATEUR M6b" in c]
        self.assertEqual(len(verif), 4)
        self.assertFalse(any("Titre Source Numéro" in c or "10.0/src" in c for c in verif))  # ligne 31 sur le flux complet
        self.assertEqual(sum("## Source M6b" in c for c in vues), 4)
        self.assertFalse([e for e in g.evenements if e["evenement"] == "m6b-fiche-arretee"])
        self.assertTrue(any(c["etape"] == "e1_redacteur" and c["role"] == "redacteur"
                            for c in lire(os.path.join(self.tmp, "s", "consommations.json"))["consommations"]))

    def test_artefact_source_citee_dans_la_fiche(self):
        def decider(role, c, modele, n):
            if "## Source M6b" in c:
                titre = json.loads(c.split("```json\n")[-1].split("\n```")[0])["titre"]
                return {"texte": json.dumps({"fiche_m6b": {"titre": "x", "idee": "reprise de " + titre,
                                                           "references": [{"titre": f"r{k}"} for k in range(5)]}})}
        g = self.pp(ad=A.adaptateurs(claude=decider))
        g.executer()
        self.assertEqual(len([e for e in g.evenements if e["evenement"] == "m6b-fiche-arretee"]), 4)

    def test_artefact_fiche_mal_formee(self):
        def decider(role, c, modele, n):
            if "## Source M6b" in c:
                return {"texte": json.dumps({"fiche_m6b": {"titre": "x", "references": [{"titre": "r"}]}})}
        g = self.pp(ad=A.adaptateurs(claude=decider))
        g.executer()
        self.assertEqual(len([e for e in g.evenements if e["evenement"] == "m6b-fiche-non-ecrite"]), 4)
        self.assertEqual(self.fin()["m6b"]["fiches_ecrites_e1"], 0)

    def test_artefact_fiches_ecrites_hors_du_pre_pilote(self):
        conf = A.configuration_pre_pilote(self.tmp)
        conf["prepilote"]["m6b"]["fiches"] = "m6b_fiches"
        with self.assertRaisesRegex(cfg.ConfigurationRefusee, "CL20-08"):
            pp.verifier_configuration_pre_pilote_v56(self.conf_pp(conf))

    def test_artefact_fiches_modifiees_avant_e9b(self):
        g = self.pp()
        orig = g.etape_e9b_m6b

        def e9b(etat):
            with open(os.path.join(self.tmp, "s", "temoins", "m6b-fiches.json"), "a", encoding="utf-8") as f:
                f.write(" ")
            return orig(etat)
        g.etape_e9b_m6b = e9b
        with self.assertRaisesRegex(NoeudArret, "A13"):
            g.executer()

    def test_cl20_09_aucune_copie_de_la_cle_apres_e3(self):
        g = self.pp()
        vu, orig = [], g._rendre

        def rendre(etat, f, essai):
            vu.append(hasattr(g, "_exempts_a8"))
            return orig(etat, f, essai)
        g._rendre = rendre
        g.executer()
        self.assertTrue(vu and all(vu))  # présente pendant É3 (cas sain de l'exemption)
        self.assertFalse(hasattr(g, "_exempts_a8"))  # retirée après


# --- CL20-10, CL20-11 : déclaration des bras ; causes de M9 -----------------------------------------------------------------------


class TestCL20_10_11Bras(Base):
    def test_cas_sain_substitut(self):
        decl, _ = c2.declarer_bras_v56(self.conf_course())
        self.assertTrue(decl["gu_krenn"]["produit"] and decl["meta"]["produit"] and decl["basique"]["produit"])

    def test_source_absente_reste_legitime(self):
        conf = self.conf_course()
        conf["bisociateur"]["gu_krenn"]["source"]["sha256"] = "0" * 64
        decl, _ = c2.declarer_bras_v56(conf)
        self.assertEqual(decl["gu_krenn"]["cause"], c2.CAUSE_SOURCE_ABSENTE)

    def test_artefacts_mode(self):
        with self.assertRaisesRegex(cfg.ConfigurationRefusee, "non branché"):
            self.conf_course(bisociateur__gu_krenn__mode="modele")
        with self.assertRaisesRegex(cfg.ConfigurationRefusee, "« substitut » exigé"):
            self.conf_course(bisociateur__gu_krenn__mode=A.SUPPRIMER)

    def test_artefacts_erreur_interne_arrete(self):
        from pole import bisociateur_v53 as b53
        from pole import bisociateur_v54 as b54
        conf = self.conf_course()
        orig = b53.SourceGuKrenn
        b53.SourceGuKrenn = lambda *a, **k: (_ for _ in ()).throw(KeyError("x"))
        try:
            with self.assertRaisesRegex(c2.ErreurInterneBras, "gu_krenn.*KeyError"):
                c2.declarer_bras_v56(conf)
        finally:
            b53.SourceGuKrenn = orig
        orig = b54.verifier_non_vacuite
        b54.verifier_non_vacuite = lambda *a, **k: (_ for _ in ()).throw(TypeError("y"))
        try:
            with self.assertRaisesRegex(c2.ErreurInterneBras, "meta.*TypeError"):
                c2.declarer_bras_v56(conf)
        finally:
            b54.verifier_non_vacuite = orig

    def test_annexe_de_forme_fautive_non_conforme(self):
        from pole import gardes_e0_v55 as g55
        from pole.configuration_v53 import chemin_piece
        conf = self.conf_course()
        d = self.sous_dossier("annexe-fautive")
        copie, sha = g55._annexe_modifiee(d, chemin_piece(conf, conf["bisociateur"]["meta"]["annexe"]["chemin"]), niches="pas une liste")
        conf["bisociateur"]["meta"]["annexe"].update(chemin=copie, sha256=sha)
        decl, _ = c2.declarer_bras_v56(conf)
        self.assertEqual(decl["meta"]["cause"], c2.CAUSE_ANNEXE)
        self.assertIn("forme", decl["meta"]["motif"])

    def test_cl20_11_causes(self):
        g = self.gen()
        g.executer()
        l1, l2 = (l["etiquette"] for l in g.conf["lecteurs_etiquettes"])
        elig = [g.fiches[i] for i in g.ordre if g.fiches[i]["meta"].get("origine") != "fusion"][:3]
        ids = [f["ident"] for f in elig]
        g.etiquettes = {"basique": {l1: {ids[0]: ["a"], ids[1]: ["b"]}, l2: {}}, "gu_krenn": {l1: {}, l2: {}}}
        _, _, causes = g._notes(elig)
        self.assertNotIn("basique", causes)  # cas sain : deux fiches étiquetées
        self.assertEqual(causes["gu_krenn"], c2.CAUSE_GK_NOTABLES)  # (iii)
        g.etiquettes = {"basique": {l1: {ids[0]: ["a"]}, l2: {}}}
        _, _, causes = g._notes(elig)
        self.assertEqual(causes["basique"], c2.CAUSE_BASIQUE)  # (iv)
        self.assertNotIn("moins de 2 fiches étiquetées", json.dumps({k: v for k, v in causes.items() if k == "meta"}, ensure_ascii=False))


# --- CL20-12 : A2 arrête le rôle -----------------------------------------------------------------------------------------------


class TestCL20_12A2Role(Base):
    def test_cas_sain(self):
        self.gen().executer()
        self.assertEqual(self.fin()["roles_arretes_a2"], {})

    def test_artefact_modele_servi_absent_arrete_le_role(self):
        dec = lambda role, c, m, n: {"modele_servi": None} if role == "proposeur_ideation" else None  # noqa: E731
        self.gen(ad=A.adaptateurs(argon=dec)).executer()
        fin = self.fin()
        self.assertIsNone(fin["arret"])
        self.assertIn("prop-argon", fin["roles_arretes_a2"])
        self.assertNotIn("juge-argon", fin["roles_arretes_a2"])

    def test_artefact_version_de_juge_changee_arrete_le_role(self):
        compte = []

        def dec(role, c, m, n):
            if role == "juge_ideation":
                compte.append(1)
                if len(compte) > 2:
                    return {"modele_servi": m + "-autre"}
        g = self.gen(ad=A.adaptateurs(argon=dec))
        g.executer()
        fin = self.fin()
        self.assertIsNone(fin["arret"])
        self.assertIn("juge-argon", fin["roles_arretes_a2"])


# --- CL20-13, CL20-14 ------------------------------------------------------------------------------------------------------


class TestCL20_13_14(Base):
    SQ = {"ancres": ["valeur 12", "seuil 0,3"], "couples": [["défaut A", "défaut B"]]}

    def ctl(self, a):
        return pp.controle_ancres_v56({"contenu": {"a": a, "b": "défaut A", "c": "défaut B"}}, self.SQ)

    def test_numerotation_cas_sain(self):
        for texte in ("1. valeur 12\n2. seuil 0,3", "- 1) valeur 12 ; 2) seuil 0,3", "liste : 1. valeur 12 ; 2. seuil 0,3"):
            with self.subTest(texte=texte):
                r = self.ctl(texte)
                self.assertEqual((r["ancres"], r["nombres_ajoutes"]), (1.0, 0))
                self.assertEqual(r["numerotation"], 2)

    def test_numerotation_artefacts(self):
        self.assertEqual(self.ctl("1. valeur 12 ; seuil 0,3 ; 7 cas")["nombres_ajoutes"], 1)
        self.assertEqual(self.ctl("valeur 12 ; seuil 0,3 en 2026.")["nombres_ajoutes"], 1)
        self.assertEqual(self.ctl("valeur 12. seuil 0,3 ; 1.5 de plus")["nombres_ajoutes"], 1)

    def test_machine_jetable_liste_blanche(self):
        sain = {"PATH": "/usr/bin", "HOME": "/root", "TOKENIZERS_PARALLELISM": "false", "POLE_MACHINE_JETABLE_V56": "1"}
        self.assertTrue(exiger_machine_jetable_v56(sain))
        self.assertTrue(exiger_machine_jetable_v56(dict(sain, MON_REGLAGE="x"), permis_en_plus=["MON_REGLAGE"]))
        for nom in ("NETRC", "MYSERVICE_APIKEY", "X_PASSPHRASE", "KUBECONFIG", "DOCKER_CONFIG", "GIT_ASKPASS", "KEYFILE", "JWT",
                    "CI_JOB_JWT", "BEARER", "COOKIE", "INCONNU"):
            with self.subTest(nom=nom), self.assertRaisesRegex(MachineNonJetable, "liste blanche"):
                exiger_machine_jetable_v56(dict(sain, **{nom: "x"}))
        with self.assertRaisesRegex(MachineNonJetable, "V56=1 absent"):
            exiger_machine_jetable_v56(dict(sain, POLE_MACHINE_JETABLE_V56="0", POLE_MACHINE_JETABLE_V54="1"))
        with self.assertRaisesRegex(MachineNonJetable, "aucun motif"):
            exiger_machine_jetable_v56(sain, permis_en_plus=["MON_*"])
        with self.assertRaisesRegex(MachineNonJetable, "nom de clé"):
            exiger_machine_jetable_v56(dict(sain, GH_TOKEN="x"), permis_en_plus=["GH_TOKEN"])


# --- table R5 du pré-pilote, lanceur v8 -------------------------------------------------------------------------------------


class TestLanceurV8(Base):
    @staticmethod
    def module():
        import importlib.util
        spec = importlib.util.spec_from_file_location("ideation_v8_essai", os.path.join(RACINE, "demonstrations", "ideation_v8.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m

    def lancer(self, argv, env=None, etage1=None):
        import contextlib
        import io
        m = self.module()
        err, out = io.StringIO(), io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
            code = m.principal(argv, environnement=env if env is not None else {"PATH": "/usr/bin"}, etage1=etage1)
        return code, out.getvalue(), err.getvalue()

    def ecrire_conf(self, conf, nom):
        conf["simulation"] = {"cout_par_appel_usd": 0.01}
        ch = os.path.join(self.tmp, nom)
        with open(ch, "w", encoding="utf-8") as f:
            json.dump(conf, f, ensure_ascii=False)
        return ch

    def test_course_et_pre_pilote_simules(self):
        ch = self.ecrire_conf(A.configuration(self.tmp), "c.json")
        code, out, err = self.lancer(["--course-2", ch, os.path.join(self.tmp, "sc"), "--generations", "2", "--moteur", "simule"])
        self.assertEqual(code, 0, err)
        self.assertEqual(len(json.loads(out)["bilan"]), 2)
        ch = self.ecrire_conf(A.avec_externes(self.tmp, A.configuration_pre_pilote(self.tmp)), "p.json")
        code, out, err = self.lancer(["--pre-pilote", ch, os.path.join(self.tmp, "sp"), "--moteur", "simule"], etage1=A.EtageUnFactice())
        self.assertEqual(code, 0, err)
        self.assertTrue(json.loads(out)["m1"])

    def test_verifier_seulement_table_v56(self):
        conf = A.avec_externes(self.tmp, A.configuration_pre_pilote(self.tmp))
        conf["specification"] = A.specification(self.tmp)
        ch = self.ecrire_conf(conf, "p.json")
        code, out, err = self.lancer(["--pre-pilote", ch, os.path.join(self.tmp, "x"), "--verifier-seulement"], etage1=A.EtageUnFactice())
        self.assertEqual(code, 0, err)
        o = json.loads(out)
        t = {x["ligne"]: x["statut"] for x in o["table_r5_e0"]}
        self.assertEqual({t[n] for n in ("1", "5", "11a", "11b", "29")}, {ge.REJOUEE})
        self.assertNotIn("11", t)
        self.assertTrue(o["specification"]["conforme"])

    def test_moteur_reel_refuse_sans_specification_conforme(self):
        ch = self.ecrire_conf(A.configuration(self.tmp), "c.json")
        code, _, err = self.lancer(["--course-2", ch, os.path.join(self.tmp, "x"), "--generations", "1", "--moteur", "reel",
                                    "--confirmer-moteur-reel", "--registre-go", "go.md"])
        self.assertEqual(code, 2)
        self.assertIn("CL20-03", err)

    def test_moteur_reel_refuse_sans_porte(self):
        conf = A.configuration(self.tmp)
        conf["specification"] = A.specification(self.tmp)
        conf["fournisseurs"] = {"argon": {"type": "commande_externe", "commande": ["/bin/true"]}}
        ch = self.ecrire_conf(conf, "c.json")
        code, _, err = self.lancer(["--course-2", ch, os.path.join(self.tmp, "x"), "--generations", "1", "--moteur", "reel",
                                    "--confirmer-moteur-reel", "--registre-go", "go.md"])
        self.assertEqual(code, 2)
        self.assertIn("porte_plafond manquant", err)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "x")))


# --- CL20-15, R12 -----------------------------------------------------------------------------------------------------------


class TestR12V56(unittest.TestCase):
    def test_aucun_fichier_de_la_v55_modifie(self):
        liste = os.path.join(RACINE, "EMPREINTES-orchestrateur-pole-v7-v55.txt")
        if not os.path.exists(liste):
            self.skipTest("liste v55 absente de l'arbre (archive seule : voir le LISEZMOI v56, CL20-15)")
        n = 0
        with open(liste, encoding="utf-8") as f:
            for ligne in f:
                sha, rel = ligne.rstrip("\n").split("  ", 1)
                with open(os.path.join(RACINE, rel), "rb") as g:
                    self.assertEqual(hashlib.sha256(g.read()).hexdigest(), sha, rel)
                n += 1
        self.assertEqual(n, 406)


if __name__ == "__main__":
    unittest.main()
