"""Essais de la v53 — instruments (R5 : un cas sain et un artefact par garde). Tout hors ligne : faux relais Kimi local
(boucle locale), adaptateurs simulés ; aucune clé, aucun appel payant."""

import datetime
import hashlib
import http.server
import json
import os
import sys
import threading
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import aides_v53 as A  # noqa: E402
from aides import CasAvecDossier  # noqa: E402
from pole import adaptateur_kimi_v53 as ak  # noqa: E402
from pole import aiguilleur_v53 as ai  # noqa: E402
from pole import bisociateur_v53 as bis  # noqa: E402
from pole import budget_v53 as bud  # noqa: E402
from pole import coffre_v53 as cof  # noqa: E402
from pole import configuration_v53 as cfg  # noqa: E402
from pole import fiches_v53 as fv  # noqa: E402
from pole import graines_v53 as gr  # noqa: E402
from pole import juges_croises_v53 as jc  # noqa: E402
from pole import memoire_v53 as mem  # noqa: E402
from pole import tableau_v53 as tab  # noqa: E402
from pole.simulation_v53 import AdaptateurSimuleCourse2  # noqa: E402


def fiche(ident, case=("t", "b"), fournisseur="kimi", passe=1, **contenu):
    c = {"titre": f"Titre {ident}", "hypothese": f"Hypothèse de méthode {ident}", "axe": "1", "methode": "mesure"}
    c.update(contenu)
    return fv.preparer(c, A.CHAMPS, ident=ident, case=case, fournisseur=fournisseur, passe=passe)


def etapes(*specs):
    return [dict(zip(("nom", "attendu_usd", "reservation_usd", "role"), s[:4]), **(s[4] if len(s) > 4 else {})) for s in specs]


# --- configuration et A15 ---------------------------------------------------------------------------------------------------


class TestConfiguration(CasAvecDossier):
    def test_cas_sain_configuration_complete(self):
        conf = cfg.lire_configuration(A.ecrire_configuration(self.tmp))
        self.assertEqual(len(conf["empreinte_configuration"]), 64)

    def test_artefacts_parametre_manquant_marqueur_et_piece_alteree(self):
        """Refus de partir ; tous les manques listés en une fois ; aucun défaut codé."""
        with self.assertRaises(cfg.ConfigurationRefusee) as e:
            cfg.lire_configuration(A.ecrire_configuration(self.tmp, budget__plafond_usd=A.SUPPRIMER, garde_kimi__debordement_max="À REMPLIR",
                                                          agregation={"regle": "au_moins"}))
        m = str(e.exception)
        self.assertIn("budget.plafond_usd manquant", m)
        self.assertIn("À REMPLIR", m)
        self.assertIn("agregation.q", m)
        d2 = self.sous_dossier("b")
        chemin = A.ecrire_configuration(d2)
        with open(os.path.join(d2, "p", "juge.md"), "a", encoding="utf-8") as f:
            f.write(" ")
        with self.assertRaisesRegex(cfg.ConfigurationRefusee, "empreinte différente.*A16"):
            cfg.lire_configuration(chemin)

    def test_artefact_bras_sans_parametres(self):
        conf = A.configuration(self.tmp)
        conf["bisociateur"]["gu_krenn"].pop("actif_min_oeuvres")
        with self.assertRaisesRegex(cfg.ConfigurationRefusee, "actif_min_oeuvres manquant"):
            cfg.lire_configuration(conf, base=self.tmp)


class TestGoA15(CasAvecDossier):
    def registre(self, *lignes):
        chemin = os.path.join(self.tmp, "go.md")
        with open(chemin, "w", encoding="utf-8") as f:
            f.write("| id | accordé le | type | périmètre | plafond | échéance | accordé par | référence |\n|---|---|---|---|---|---|---|---|\n")
            for l in lignes:
                f.write(l + "\n")
        return chemin

    J = datetime.date(2026, 11, 2)

    def test_cas_sain_ligne_au_plafond(self):
        r = self.registre("| GO-2026-11-01-01 | 2026-11-01 | calcul | pré-pilote course 2 | 45 USD | 2026-11-05 | Lazar | mot direct |")
        g = cfg.verifier_go("GO-2026-11-01-01", r, 45.0, self.J)
        self.assertEqual(g["plafond_lu_usd"], 45.0)

    def test_artefacts_sans_go_absent_plafond_type_echeance_revocation(self):
        r = self.registre("| GO-2026-11-01-01 | 2026-11-01 | calcul | pré-pilote | 32 USD | 2026-11-05 | Lazar | x |",
                          "| GO-2026-11-01-02 | 2026-11-01 | dépôt distant | x | 45 USD | 2026-11-05 | Lazar | x |",
                          "| GO-2026-10-01-01 | 2026-10-01 | calcul | x | 45 USD | 2026-10-02 | Lazar | x |",
                          "| GO-2026-11-01-03 | 2026-11-01 | calcul | x | 45 USD | 2026-11-05 | Lazar | x |",
                          "| GO-2026-11-01-04 | 2026-11-01 | révocation | révoque GO-2026-11-01-03 | — | 2026-11-05 | Lazar | x |")
        for go_id, motif in ((None, "GO_ID"), ("GO-2026-11-09-09", "absent"), ("GO-2026-11-01-01", "ne couvre pas"),
                             ("GO-2026-11-01-02", "pas « calcul »"), ("GO-2026-10-01-01", "validité"), ("GO-2026-11-01-03", "révoqué")):
            with self.subTest(go_id=go_id), self.assertRaisesRegex(cfg.GoRefuse, motif):
                cfg.verifier_go(go_id, r, 45.0, self.J)


# --- budget (A1) -------------------------------------------------------------------------------------------------------------


class TestBudgetA1(unittest.TestCase):
    def test_cas_sain_tout_tient(self):
        b = bud.Budget(10.0, 9.0, etapes(("a", 1, 2, "protegee"), ("s", 1, 2, "sacrifiable", {"rang": 1})))
        for n in ("a", "s"):
            self.assertEqual(b.avant_etape(n)[0], bud.JOUER)
            self.assertEqual(b.apres_etape(n, 1.0), "jouee")
        self.assertTrue(b.etat()["c13_budget_satisfaite"])

    def test_aucun_defaut(self):
        for plafond, arret in ((None, "sans"), (10.0, None), (0, "sans"), (10.0, 11.0)):
            with self.subTest(plafond=plafond, arret=arret), self.assertRaises(bud.BudgetRefuse):
                bud.Budget(plafond, arret, etapes(("a", 1, 1, "protegee")))

    def test_projection_retire_puis_reduit_jamais_retiree_entiere(self):
        e = etapes(("p", 4, 4, "protegee"), ("f", 3, 3, "sacrifiable", {"rang": 1}),
                   ("m6", 4, 5, "reductible", {"rang": 2, "reduite": {"attendu_usd": 1, "reservation_usd": 2}}))
        b = bud.Budget(9.0, "sans", e)
        self.assertEqual(b.avant_etape("p")[0], bud.JOUER)
        b.apres_etape("p", 4.0)
        self.assertEqual(b.avant_etape("f")[0], bud.RETIREE)  # projection 4+3+4 > 9 → fusions retirées d'abord
        d, det = b.avant_etape("m6")
        self.assertEqual((d, det["reduite"]), (bud.JOUER, False))  # 4 + 5 = 9 tient sous 9 : non réduite
        # garde R5 ligne 11, cas sain : M6 non réduite dont la projection dépasse → réduite, puis lancée
        b2 = bud.Budget(8.0, "sans", e)
        b2.avant_etape("p")
        b2.apres_etape("p", 4.0)
        self.assertEqual(b2.avant_etape("f")[0], bud.RETIREE)
        d, det = b2.avant_etape("m6")
        self.assertEqual((d, det["reduite"]), (bud.JOUER, True))

    def test_artefacts_reduite_qui_ne_tient_pas_protegee_qui_ne_tient_pas_coupure(self):
        e = etapes(("p", 8, 8, "protegee"), ("m6", 4, 5, "reductible", {"rang": 1, "reduite": {"attendu_usd": 1, "reservation_usd": 2}}),
                   ("q", 1, 1, "protegee"))
        b = bud.Budget(9.0, "sans", e)
        b.avant_etape("p")
        b.apres_etape("p", 8.0)
        self.assertEqual(b.avant_etape("m6")[0], bud.NON_MESUREE)  # réduite, ne tient pas : jamais retirée entière
        self.assertEqual(b.etapes["m6"]["etat"], bud.NON_MESUREE)
        self.assertTrue(b.etapes["m6"]["reduite_appliquee"])
        self.assertEqual(b.avant_etape("q")[0], bud.JOUER)
        self.assertEqual(b.apres_etape("q", 3.0), bud.NON_MESUREE)  # le coût franchit S17 en route : coupée à S17
        self.assertEqual(b.cumul, 9.0)
        self.assertFalse(b.etat()["c13_budget_satisfaite"])

    def test_arret_d_etape_retire_les_retirables_et_reduit(self):
        e = etapes(("p", 1, 1, "protegee"), ("s", 1, 1, "sacrifiable", {"rang": 1}),
                   ("m6", 1, 1, "reductible", {"rang": 2, "reduite": {"attendu_usd": 0.5, "reservation_usd": 0.5}}))
        b = bud.Budget(10.0, 1.0, e)
        b.avant_etape("p")
        b.apres_etape("p", 1.0)
        self.assertEqual(b.avant_etape("s")[0], bud.RETIREE)
        d, det = b.avant_etape("m6")
        self.assertEqual((d, det["reduite"]), (bud.JOUER, True))

    def test_hors_porte_non_lancee_c13_inchangee(self):
        b = bud.Budget(2.0, "sans", etapes(("p", 2, 2, "protegee"), ("h", 1, 1, "protegee_hors_porte")))
        b.avant_etape("p")
        b.apres_etape("p", 2.0)
        self.assertEqual(b.avant_etape("h")[0], bud.NON_LANCEE_HORS_PORTE)
        self.assertTrue(b.etat()["c13_budget_satisfaite"])

    def test_rejeu_sur_les_seules_consommations(self):
        """Garde R5 ligne 30 (cas sain) : mêmes consommations, mêmes décisions ; artefact : une décision ne reçoit pas de verdict."""
        e = etapes(("p", 4, 4, "protegee"), ("f", 3, 3, "sacrifiable", {"rang": 1}), ("q", 1, 1, "protegee"))
        self.assertEqual(bud.rejouer(9.0, "sans", e, {"p": 4.0, "q": 1.0}), bud.rejouer(9.0, "sans", e, {"p": 4.0, "q": 1.0}))
        b = bud.Budget(9.0, "sans", e)
        b.avant_etape("p")
        with self.assertRaises(bud.BudgetRefuse):
            b.apres_etape("p", {"verdicts": {"juge": True}})


# --- coffre (A21) et graines (R9) --------------------------------------------------------------------------------------------


class TestCoffreA21(CasAvecDossier):
    def test_cas_sain_lecture_apres_fin(self):
        c = cof.Coffre(os.path.join(self.tmp, "c"))
        c.deposer("verdicts-x", {"v": 1})
        c.noter_consommation("juges", "juge", 0.1, modele_servi="m")
        self.assertEqual(len(c.consommations()), 1)
        c.declarer_fin_e9()
        self.assertEqual(c.ouvrir("verdicts-x"), {"v": 1})
        self.assertEqual(c.journal()["incidents"], [])

    def test_artefacts_lecture_avant_fin_et_consommation_portant_un_verdict(self):
        c = cof.Coffre(os.path.join(self.tmp, "c"))
        c.deposer("verdicts-x", {"v": 1})
        with self.assertRaises(cof.LectureAvantFinE9):
            c.ouvrir("verdicts-x")
        self.assertEqual(len(c.journal()["incidents"]), 1)
        with self.assertRaises(ValueError):
            c.noter_consommation("juges", "juge", 0.1, verdict=True)
        with self.assertRaises(Exception):
            cof.Coffre(os.path.join(self.tmp, "c"))  # jamais réutilisé


class TestGraines(unittest.TestCase):
    def test_cas_sain_seedsequence_meme_cle_que_le_depot(self):
        g1, g2 = gr.Graines(20261101), gr.Graines(20261101)
        self.assertEqual(g1.permutation("t", 10), g2.permutation("t", 10))
        self.assertNotEqual(g1.jeton_opaque("a"), g1.jeton_opaque("b"))
        attendu = int.from_bytes(hashlib.sha256(b"pp2-partition").digest()[:8], "big")
        self.assertEqual(gr.cle_de_tache("pp2-partition"), attendu)
        self.assertIn("t", g1.manifeste()["taches"])

    def test_artefacts_racine_et_numpy_trop_ancien(self):
        with self.assertRaises(gr.GrainesRefusees):
            gr.Graines(-1)
        import numpy
        vrai = numpy.__version__
        try:
            numpy.__version__ = "1.24.9"
            with self.assertRaisesRegex(gr.GrainesRefusees, "1.25"):
                gr.Graines(1)
        finally:
            numpy.__version__ = vrai


# --- adaptateur Kimi par voie protocole (faux relais local) -------------------------------------------------------------------


class FauxRelaisKimi:
    """Faux relais Kimi v4 sur la boucle locale : réponses programmées, requêtes enregistrées (en-têtes, corps)."""

    def __init__(self):
        self.reponses, self.requetes = [], []
        moi = self

        class G(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_POST(self):
                corps = self.rfile.read(int(self.headers.get("Content-Length", 0)))
                moi.requetes.append({"chemin": self.path, "entetes": dict(self.headers), "corps": json.loads(corps)})
                statut, objet = moi.reponses.pop(0)
                donnees = json.dumps(objet, ensure_ascii=False).encode("utf-8")  # comme le relais v4
                self.send_response(statut)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(donnees)))
                self.end_headers()
                self.wfile.write(donnees)

        self.serveur = http.server.ThreadingHTTPServer(("127.0.0.1", 0), G)
        self.url = f"http://127.0.0.1:{self.serveur.server_address[1]}"
        threading.Thread(target=self.serveur.serve_forever, daemon=True).start()

    def fermer(self):
        self.serveur.shutdown()
        self.serveur.server_close()


def reponse_ok(texte="{\"fiches\": []}", modele="kimi-k3.1-pro", fin="stop", usage=True):
    o = {"model": modele, "choices": [{"index": 0, "message": {"content": texte}, "finish_reason": fin}]}
    if usage:
        o["usage"] = {"prompt_tokens": 1000, "completion_tokens": 500}
    return 200, o


class TestAdaptateurKimi(CasAvecDossier):
    def setUp(self):
        super().setUp()
        self.relais = FauxRelaisKimi()
        self.addCleanup(self.relais.fermer)

    def ad(self, **kw):
        r = dict(modele="kimi-k3.1-pro", prix_entree=2.0, prix_sortie=10.0, max_sortie_jetons=4096, sortie_min_jetons=256, delai_s=30.0)
        r.update(kw)
        return ak.AdaptateurKimiProtocole(self.relais.url, **r)

    def test_cas_sain_cout_lu_modele_servi_aucune_cle_aucun_outil(self):
        self.relais.reponses.append(reponse_ok("bonjour"))
        r = self.ad().lancer("proposeur_ideation", "consigne", self.tmp, 1.0, 1, modele="kimi-k3.1-pro")
        self.assertEqual((r.statut, r.texte_final, r.modele_servi), ("ok", "bonjour", "kimi-k3.1-pro"))
        self.assertAlmostEqual(r.cout_declare_usd, (1000 * 2 + 500 * 10) / 1e6)
        q = self.relais.requetes[0]
        self.assertEqual(q["chemin"], "/v1/chat/completions")
        self.assertNotIn("Authorization", q["entetes"])
        self.assertNotIn("tools", q["corps"])
        self.assertNotIn("stream", q["corps"])
        self.assertEqual(q["corps"]["model"], "kimi-k3.1-pro")

    def test_artefacts_modele_servi_refus_relais_filtre_tronque_usage(self):
        cas = [(reponse_ok(modele="kimi-k2"), "refus"), ((403, {"erreur": "modèle non permis"}), "refus"),
               ((402, {"erreur": "plafond"}), "budget_depasse"), ((502, {"erreur": "modèle servi différent"}), "refus"),
               (reponse_ok(fin="content_filter"), "refus"), (reponse_ok(fin="length"), "erreur"),
               (reponse_ok(usage=False), "erreur"), (reponse_ok(texte="  "), "erreur")]
        for rep, statut in cas:
            with self.subTest(rep=rep):
                self.relais.reponses.append(rep)
                r = self.ad().lancer("juge_ideation", "consigne", self.tmp, 1.0, 1)
                self.assertEqual(r.statut, statut)
                self.assertEqual(r.texte_final, "")
        # pire cas au-dessus du plafond : rien envoyé
        n = len(self.relais.requetes)
        r = self.ad().lancer("juge_ideation", "x" * 10000, self.tmp, 0.0001, 1)
        self.assertEqual(r.statut, "budget_depasse")
        self.assertEqual(len(self.relais.requetes), n)

    def test_artefacts_reglages_sans_defaut_et_url_non_locale(self):
        with self.assertRaises(ak.ReglageKimiRefuse):
            ak.AdaptateurKimiProtocole("http://exemple.org:80", modele="m", prix_entree=1, prix_sortie=1, max_sortie_jetons=10,
                                       sortie_min_jetons=1, delai_s=1)
        with self.assertRaises(TypeError):
            ak.AdaptateurKimiProtocole(self.relais.url, modele="m")
        with self.assertRaises(ak.ReglageKimiRefuse):
            self.ad(prix_entree=None)
        with self.assertRaises(ValueError):
            self.ad().lancer("experimentateur", "c", self.tmp, 1.0, 1)


# --- aiguilleur, garde de Kimi --------------------------------------------------------------------------------------------------


def simule(**kw):
    r = dict(champs_fiche=A.CHAMPS, items=A.ITEMS, cout_par_appel_usd=0.01)
    r.update(kw)
    return AdaptateurSimuleCourse2(**r)


class TestAiguilleur(CasAvecDossier):
    def aig(self, decider=None):
        return ai.Aiguilleur(simule(decider=decider), etiquette="a", modele="m", consigne_figee="AIGUILLEUR", etiquettes_interdites=A.INTERDITES,
                             plafond_session_usd=0.5, journal_dossier=os.path.join(self.tmp, "aig"))

    def test_cas_sain_passeport(self):
        a = self.aig()
        f = fiche("f1")
        self.assertEqual(a.classer(f)[0], "niveau_methode")
        self.assertTrue(a.exiger_passeport(f, "un juge"))

    def test_artefacts_concret_journal_sans_contenu_refus_vaut_aiguillage_a17(self):
        secret = "CONTENU-CONCRET-QUI-NE-DOIT-JAMAIS-ETRE-COPIE"
        a = self.aig(lambda role, consigne, modele, n: {"texte": json.dumps({"classe": "concret", "categorie": "C2"})} if n == 0 else
                     {"statut": "erreur"})
        f1, f2 = fiche("f1", methode=secret), fiche("f2")
        self.assertEqual(a.classer(f1)[0], "concret")
        self.assertEqual(a.classer(f2)[0], "concret")  # refus de l'aiguilleur : vaut aiguillage
        self.assertEqual(a.refus, 1)
        a.sceller_journal()
        with open(os.path.join(self.tmp, "aig", "journal-aiguillage.json"), encoding="utf-8") as f:
            self.assertNotIn(secret, f.read())
        with self.assertRaises(ai.SansPasseport):
            a.exiger_passeport(f1, "un juge")
        f3 = fiche("f3")
        with self.assertRaises(ai.SansPasseport):
            a.exiger_passeport(f3, "le tableau")  # jamais passée par l'aiguilleur
        # contenu modifié après l'aiguillage : le passeport ne vaut plus
        a2 = ai.Aiguilleur(simule(), etiquette="a", modele="m", consigne_figee="AIGUILLEUR", etiquettes_interdites=A.INTERDITES,
                           plafond_session_usd=0.5, journal_dossier=os.path.join(self.tmp, "aig2"))
        f4 = fiche("f4")
        a2.classer(f4)
        f4b = dict(f4, empreinte="0" * 64)
        self.assertFalse(a2.a_passeport(f4b))

    def test_garde_kimi_s12(self):
        g = ai.GardeKimi(0.10)
        for i in range(10):
            g.noter(fiche(f"k{i}"), "niveau_methode")
        self.assertTrue(g.verifier())
        g.noter(fiche("k10"), "concret")
        g.noter(fiche("k11"), "concret")
        with self.assertRaises(ai.DebordementKimi):
            g.verifier()
        with self.assertRaises(ValueError):
            ai.GardeKimi(None)

    def test_etalonnage_seuils_injectes(self):
        dec = {"c1": "concret", "c2": "a_corriger", "m1": "niveau_methode", "m2": "concret"}
        att = {"c1": "concret", "c2": "concret", "m1": "niveau_methode", "m2": "niveau_methode"}
        r = ai.etalonner(dec, att, rappel_min=0.9, fausses_alertes_max=0.1)
        self.assertEqual((r["rappel"], r["fausses_alertes"], r["etalonne"]), (1.0, 0.5, False))
        with self.assertRaises(ValueError):
            ai.etalonner(dec, att, rappel_min=None, fausses_alertes_max=0.1)


# --- étiquettes interdites (A4) -------------------------------------------------------------------------------------------------


class TestEtiquettesA4(unittest.TestCase):
    def test_cas_sain_et_artefacts(self):
        self.assertTrue(fv.garde_etiquettes("une fiche de niveau méthode", A.INTERDITES))
        for mot in ("Témoin", "EXPLORATOIRE", "la fusion de deux", "bras méta", "Gu-Krenn"):
            with self.subTest(mot=mot), self.assertRaises(fv.EtiquetteDansEntree):
                fv.garde_etiquettes(f"texte {mot} ici", A.INTERDITES)
        with self.assertRaises(fv.FicheRefusee):
            fv.preparer({"titre": "x", "hypothese": "y", "axe": "1", "methode": "m", "classe": "P"}, A.CHAMPS, ident="i",
                        case=("t", "b"), fournisseur="k", passe=1)
        with self.assertRaises(fv.FicheRefusee):
            fv.preparer({"titre": "x"}, A.CHAMPS, ident="i", case=("t", "b"), fournisseur="k", passe=1)


# --- juges croisés -------------------------------------------------------------------------------------------------------------


class TestJugesCroises(CasAvecDossier):
    def preparer_juges(self, decider=None):
        coffre = cof.Coffre(os.path.join(self.tmp, "coffre"))
        sims = {n: simule(decider=decider) for n in ("kimi", "argon", "claude")}
        juges = [{"etiquette": f"j-{n}", "modele": f"m-{n}", "fournisseur": n, "consigne": "cj"} for n in ("kimi", "argon", "claude")]
        j = jc.JugesCroises(sims, juges, {"cj": "JUGE consigne figée"}, items=A.ITEMS, etiquettes_interdites=A.INTERDITES,
                            plafond_session_usd=0.5, graines=gr.Graines(1), coffre=coffre, dossier=os.path.join(self.tmp, "j"))
        aig = ai.Aiguilleur(simule(), etiquette="a", modele="m", consigne_figee="AIGUILLEUR", etiquettes_interdites=A.INTERDITES,
                            plafond_session_usd=0.5, journal_dossier=os.path.join(self.tmp, "aig"))
        return j, aig, sims, coffre

    def test_cas_sain_trois_juges_une_fiche_par_appel_aveugles(self):
        j, aig, sims, coffre = self.preparer_juges()
        fs = [fiche(f"f{i}") for i in range(3)]
        for f in fs:
            aig.classer(f)
            j.juger(f, aig, "passe1")
        for n, s in sims.items():
            self.assertEqual(len(s.appels), 3)  # un appel par fiche
        for f in fs:
            self.assertTrue(os.path.exists(os.path.join(coffre.dossier, f"verdicts-passe1-{f['ident']}.json")))
        with self.assertRaises(cof.LectureAvantFinE9):
            coffre.ouvrir(f"verdicts-passe1-{fs[0]['ident']}")

    def test_aucun_juge_ne_voit_les_notes_des_autres(self):
        vues = []
        j, aig, sims, coffre = self.preparer_juges(lambda role, consigne, modele, n: vues.append(consigne) or None)
        f = fiche("f1")
        aig.classer(f)
        j.juger(f, aig, "passe1")
        consignes_juges = [c for c in vues if "JUGE" in c]
        self.assertEqual(len(consignes_juges), 3)
        for c in consignes_juges:
            self.assertNotIn('"items"', c)
            self.assertNotIn("K1", c)
            self.assertEqual(c.count("## La fiche"), 1)
        idents = [c.split('"identifiant": "')[1].split('"')[0] for c in consignes_juges]
        self.assertEqual(len(set(idents)), 3)  # identifiant opaque propre à chaque juge

    def test_artefacts_sans_passeport_et_version_servie_changee(self):
        j, aig, sims, coffre = self.preparer_juges()
        f = fiche("f1")
        with self.assertRaises(ai.SansPasseport):
            j.juger(f, aig, "passe1")
        aig.classer(f)
        j.juger(f, aig, "passe1")
        sims["argon"].modele_servi = "m-argon-v2"
        f2 = fiche("f2")
        aig.classer(f2)
        with self.assertRaises(jc.VersionServieChangee):
            j.juger(f2, aig, "fusions")

    def test_agregation_parametree(self):
        v = {"a": {"notable": True, "x": 1.0}, "b": {"notable": True, "x": 1.0}, "c": {"notable": False, "x": 0.6}}
        self.assertTrue(jc.agreger(v, "au_moins", 2)["notable"])
        self.assertFalse(jc.agreger(v, "au_moins", 3)["notable"])
        self.assertFalse(jc.agreger(v, "unanimite")["notable"])
        self.assertTrue(jc.agreger(v, "majorite_stricte")["notable"])
        absents = dict(v, b=None, c=None)  # un seul juge lisible, notable
        self.assertTrue(jc.agreger(absents, "majorite_stricte")["notable"])
        self.assertFalse(jc.agreger(absents, "unanimite")["notable"])  # un absent fait tomber l'unanimité
        self.assertFalse(jc.agreger(absents, "au_moins", 2)["notable"])
        with self.assertRaises(ValueError):
            jc.agreger(v, "au_moins")
        with self.assertRaises(ValueError):
            jc.agreger(v, "moyenne")
        self.assertIsNone(jc.lire_verdict('{"items": {"K1": true}}', A.ITEMS))
        self.assertIsNone(jc.lire_verdict('{"items": {"K1": 1, "K2": true, "K3": true, "K4": true, "K5": true}}', A.ITEMS))

    def test_etalonnage_m1(self):
        att = {"p1": "P", "p2": "P", "n1": "N", "n2": "N"}
        parfait = {"p1": True, "p2": True, "n1": False, "n2": False}
        r = jc.etalonner_juges({"a": parfait, "b": parfait, "c": dict(parfait, n2=True)}, att, exactitude_min=0.8, rappel_min=0.7,
                               plancher_echec=0.7, fleiss_min=0.45, cohen_min=0.35, accord_plancher=0.3)
        self.assertEqual(r["par_juge"]["a"]["exactitude_equilibree"], 1.0)
        self.assertEqual(r["par_juge"]["c"]["exactitude_equilibree"], 0.75)
        self.assertFalse(r["par_juge"]["c"]["etalonne"])
        self.assertAlmostEqual(r["cohen"]["a|b"], 1.0)
        self.assertAlmostEqual(r["cohen"]["a|c"], 0.5)
        with self.assertRaises(ValueError):
            jc.etalonner_juges({"a": parfait}, att, exactitude_min=None, rappel_min=0.7, plancher_echec=0.7, fleiss_min=0.45,
                               cohen_min=0.35, accord_plancher=0.3)


# --- tableau minimal (A18) ---------------------------------------------------------------------------------------------------------


class TestTableauA18(CasAvecDossier):
    def test_cas_sain_et_artefacts(self):
        aig = ai.Aiguilleur(simule(decider=lambda r, c, m, n: {"texte": '{"classe": "concret"}'} if "f3" in c else None),
                            etiquette="a", modele="m", consigne_figee="AIGUILLEUR", etiquettes_interdites=A.INTERDITES,
                            plafond_session_usd=0.5, journal_dossier=os.path.join(self.tmp, "aig"))
        fs = [fiche("f1", hypothese="ligne un\nligne deux " + "x" * 300), fiche("f2"), fiche("f3"), fiche("f4", case=("t", "autre"))]
        for f in fs:
            aig.classer(f)
        par = {f["ident"]: f for f in fs}
        t = tab.construire(fs, ("t", "b"), aig, champ_titre="titre", champ_resume="hypothese", longueur_max_titre=20, longueur_max_resume=50)
        self.assertEqual([e["ident"] for e in t["entrees"]], ["f1", "f2"])
        self.assertTrue(all(len(e["resume"]) <= 50 and "\n" not in e["resume"] for e in t["entrees"]))
        self.assertTrue(tab.verifier_tableau(t, ("t", "b"), aig, par, longueur_max_titre=20, longueur_max_resume=50))
        self.assertNotIn("ident", tab.texte_servi(t))
        artefacts = [dict(t, entrees=t["entrees"] + [{"case": ["t", "autre"], "ident": "f4", "titre": "x", "resume": "y"}]),
                     dict(t, entrees=[{"case": ["t", "b"], "ident": "f3", "titre": "x", "resume": "y"}]),
                     dict(t, entrees=[{"case": ["t", "b"], "ident": "f2", "titre": "x", "resume": "y" * 3000}]),
                     dict(t, entrees=[{"case": ["t", "b"], "ident": "f2", "titre": "x", "resume": "y", "fiche": {}}])]
        for art in artefacts:
            with self.subTest(art=str(art)[:80]), self.assertRaises(tab.TableauRefuse):
                tab.verifier_tableau(art, ("t", "b"), aig, par, longueur_max_titre=20, longueur_max_resume=50)
        with self.assertRaises(tab.TableauRefuse):
            tab.construire(fs, ("t", "b"), aig, champ_titre="titre", champ_resume="hypothese", longueur_max_titre=None, longueur_max_resume=5)


# --- mémoire anti-redite (M3) -------------------------------------------------------------------------------------------------------


class TestMemoire(unittest.TestCase):
    def test_cas_sain_idees_distinctes(self):
        m = mem.Memoire(methode="bardeaux", seuil=0.6, taille_bardeau=3)
        a = fiche("a", hypothese="mesurer la dérive des sondes linéaires sur dix familles de modèles ouverts")
        b = fiche("b", hypothese="comparer des moniteurs boîte noire sur les traces d'agents en environnement simulé", axe="2",
                  titre="Autre", methode="tout autre protocole de lecture")
        self.assertEqual(m.detecter([a, b])["paires"], [])

    def test_artefacts_redite_intra_lot_inter_fournisseurs_et_contre_memoire(self):
        m = mem.Memoire(methode="bardeaux", seuil=0.6, taille_bardeau=3)
        a = fiche("a", fournisseur="kimi")
        b = fv.preparer(dict(a["contenu"]), A.CHAMPS, ident="b", case=("t", "b"), fournisseur="argon", passe=1)
        r = m.detecter([a, b])
        self.assertEqual(r["redites"], ["b"])
        self.assertTrue(r["paires"][0]["inter_fournisseurs"])
        m.ajouter_memoire([a], 1)
        c = fv.preparer(dict(a["contenu"]), A.CHAMPS, ident="c", case=("t", "b"), fournisseur="kimi", passe=1)
        r2 = m.detecter([c])
        self.assertTrue(r2["paires"][0]["contre_memoire"])
        with self.assertRaises(mem.MemoireRefusee):
            mem.Memoire(methode="plongement", seuil=0.6)
        with self.assertRaises(mem.MemoireRefusee):
            mem.Memoire(methode="bardeaux", seuil=None, taille_bardeau=3)


# --- bisociateur ------------------------------------------------------------------------------------------------------------------


class TestBisociateur(CasAvecDossier):
    def aig_avec(self, fs):
        aig = ai.Aiguilleur(simule(), etiquette="a", modele="m", consigne_figee="AIGUILLEUR", etiquettes_interdites=A.INTERDITES,
                            plafond_session_usd=0.5, journal_dossier=os.path.join(self.tmp, "aig" + str(len(os.listdir(self.tmp)))))
        for f in fs:
            aig.classer(f)
        return aig

    def test_regle_des_paires_n_moins_de_2_egal_2_et_au_moins_3(self):
        fs = [fiche(f"f{i}") for i in range(4)]
        aig = self.aig_avec(fs)
        notes = {b: {bis.cle_paire(a["ident"], c["ident"]): (float(i + j), None) for i, a in enumerate(fs) for j, c in enumerate(fs) if i < j}
                 for b in ("meta", "gu_krenn", "basique")}
        dep = {b: {} for b in notes}
        ch, np_ = bis.choisir_paires(fs[:1], notes, ["meta", "gu_krenn", "basique"], 1, aig, dep)
        self.assertEqual(set(np_.values()), {"non produit (effectif)"})
        ch, np_ = bis.choisir_paires(fs[:2], notes, ["gu_krenn", "meta", "basique"], 1, aig, dep)
        self.assertEqual(sum(len(v) for v in ch.values()), 1)
        self.assertEqual(len(ch["gu_krenn"]), 1)
        ch, np_ = bis.choisir_paires(fs, notes, ["basique", "meta", "gu_krenn"], 1, aig, dep)
        toutes = [p for v in ch.values() for p in v]
        self.assertEqual(len(toutes), 3)
        self.assertEqual(len(set(toutes)), 3)  # deux bras jamais sur la même paire

    def test_artefacts_paire_mal_formee(self):
        fs = [fiche("f1"), fiche("f2", case=("t", "autre")), fiche("f3")]
        aig = self.aig_avec(fs[:2])
        with self.assertRaises(bis.BisociationRefusee):
            bis.verifier_paire(fs[0], fs[0], aig)
        with self.assertRaises(bis.BisociationRefusee):
            bis.verifier_paire(fs[0], fs[1], aig)
        with self.assertRaises(ai.SansPasseport):
            bis.verifier_paire(fs[0], fs[2], aig)

    def test_annexe_meta_a20(self):
        a = A.annexe_meta(self.tmp)
        p = bis.lire_annexe_meta(a["chemin"], a["sha256"])
        self.assertEqual(p["niches"], ["n1", "n2", "n3"])
        with self.assertRaisesRegex(bis.BisociationRefusee, "absente"):
            bis.lire_annexe_meta(os.path.join(self.tmp, "rien.md"), a["sha256"])
        with self.assertRaisesRegex(bis.BisociationRefusee, "empreinte différente"):
            bis.lire_annexe_meta(a["chemin"], "0" * 64)
        d2 = self.sous_dossier("ns")
        b = A.annexe_meta(d2, sceller=False)
        with self.assertRaisesRegex(bis.BisociationRefusee, "non scellée"):
            bis.lire_annexe_meta(b["chemin"], b["sha256"])
        d3 = self.sous_dossier("sans-approbation")
        c = A.annexe_meta(d3, approbation_lazar="À REMPLIR")
        with self.assertRaisesRegex(bis.BisociationRefusee, "approbation_lazar"):
            bis.lire_annexe_meta(c["chemin"], c["sha256"])

    def test_score_meta_desaccord_hors_score_et_meme_niche(self):
        a = A.annexe_meta(self.tmp)
        p = bis.lire_annexe_meta(a["chemin"], a["sha256"])
        s_commune = {("objet_mathematique", "graphe")}
        self.assertEqual(bis.score_meta(p, "n1", "n2", s_commune, s_commune), 1.5)  # c=0,1 faible, s=1 forte, e=2 dans la bande
        self.assertEqual(bis.score_meta(p, "n1", "n3", s_commune, s_commune), 0.0)
        self.assertTrue(bis.garde_desaccord_hors_score(bis.score_meta, p, "n1", "n2", s_commune, s_commune))
        fautif = lambda p, na, nb, sa, sb, desaccord="non": bis.score_meta(p, na, nb, sa, sb) + (1 if desaccord == "oui" else 0)  # noqa: E731
        with self.assertRaisesRegex(bis.BisociationRefusee, "R-638"):
            bis.garde_desaccord_hors_score(fautif, p, "n1", "n2", s_commune, s_commune)
        with self.assertRaisesRegex(bis.BisociationRefusee, "même niche"):
            bis.score_meta(p, "n1", "n1", s_commune, s_commune)

    def test_substitut_gu_krenn_s31(self):
        s = A.source_gk(self.tmp)
        src = bis.SourceGuKrenn(s["chemin"], s["sha256"], oeuvres_min_vocabulaire=5, date_debut="2015-01-01", date_coupure="2026-06-30",
                                actif_depuis="2023-07-01", actif_min_oeuvres=5)
        self.assertEqual(src.note(["c2", "c3"], ["c5", "c6"]), 1.0)  # jamais reliées, actives
        self.assertEqual(src.note(["c1", "c2"], ["c4", "c5"]), 0.75)  # c1–c4 reliés
        self.assertIsNone(src.note(["c1"], ["c4", "c5"]))
        with self.assertRaisesRegex(bis.BisociationRefusee, "hors vocabulaire"):
            src.note(["c1", "zz"], ["c4", "c5"])
        with self.assertRaisesRegex(bis.BisociationRefusee, "empreinte"):
            bis.SourceGuKrenn(s["chemin"], "0" * 64, oeuvres_min_vocabulaire=5, date_debut="2015-01-01", date_coupure="2026-06-30",
                              actif_depuis="2023-07-01", actif_min_oeuvres=5)

    def test_score_basique_et_etiquettes(self):
        fa, fb = fiche("a", axe="1"), fiche("b", axe="2")
        conc = {"a": {"x", "y"}, "b": {"y", "z"}}
        s = bis.score_basique(fa, fb, conc, lambda f: f["contenu"]["axe"], 8.5, 0.05)
        self.assertAlmostEqual(s, (1 - 0.25) ** 8.5 * (1 / 3 + 0.05))
        self.assertEqual(bis.score_basique(fa, fiche("c", axe="1"), {"a": {"x"}, "c": {"x"}}, lambda f: f["contenu"]["axe"], 8.5, 0.05), 0.0)
        self.assertEqual(bis.valider_etiquettes(["a", "b"], ["a", "b", "c"]), ["a", "b"])
        with self.assertRaises(bis.BisociationRefusee):
            bis.valider_etiquettes(["a", "hors"], ["a", "b"])
        with self.assertRaises(bis.BisociationRefusee):
            bis.valider_niche({"niche": "n9", "structures": []}, ["n1"], ["methode"])
        self.assertEqual(bis.accord_jaccard({"f": ["a", "b"], "g": []}, {"f": ["a"], "g": []}), {"jaccard_moyen": 0.5, "n": 1, "exclues": 1})
        self.assertTrue(bis.kappa_niches({"f": "n1", "g": "n1"}, {"f": "n1", "g": "n1"})["degenere"])

    def test_entree_de_fusion_aveugle(self):
        fa, fb = fiche("a"), fiche("b")
        e = bis.entree_fusion("Consigne de mise en commun.", fa, fb, A.INTERDITES)
        for mot in ("meta", "gu_krenn", "basique", '"ident"', "case"):
            self.assertNotIn(mot, e)
        with self.assertRaises(fv.EtiquetteDansEntree):
            bis.entree_fusion("c", fiche("x", methode="bras méta"), fb, A.INTERDITES)


if __name__ == "__main__":
    unittest.main()
