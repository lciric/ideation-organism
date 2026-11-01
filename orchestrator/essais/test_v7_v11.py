"""Essais de la version 11 de v7 : corrections de la contre-lecture du code écrit sous Opus (C1 à C6, C9, C10)."""

import json
import math
import os
import random
import sys
import unittest

from essais.aides import CasAvecDossier, fiche
from essais.test_memoire_v4 import VRAIE, issue_testee
from essais.test_v6_relais_reel import JETON_FACTICE  # noqa: F401 (import de contrôle : le relais reste testé ailleurs)
from pole import selection_pari as sp
from pole.adaptateurs import construire_options, lectures_interdites_par_defaut
from pole.cycle import Generation, appliquer_multiplicite
from pole.memoire import Memoire
from pole.relais_reel import CHEMINS_PERMIS, CHEMINS_REFUSES

RELAIS = "http://127.0.0.1:8765/v1"


class BacASableLectures(CasAvecDossier):
    """C6 : le bac à sable borne désormais les lectures (par défaut : le dossier de la course) et échoue dur s'il manque."""

    def test_lectures_interdites_par_defaut_et_echec_dur(self):
        dossier = os.path.join(self.tmp, "G0-F01", "experience")
        os.makedirs(dossier)
        o = construire_options(dossier, 1.0, 5, url_relais=RELAIS)
        s = o["sandbox"]
        self.assertTrue(s["failIfUnavailable"])
        self.assertEqual(s["filesystem"]["denyRead"], [os.path.normpath(self.tmp)])
        self.assertEqual(s["filesystem"]["allowRead"], [os.path.normpath(dossier)])
        self.assertEqual(s["filesystem"]["denyWrite"], [os.path.normpath(self.tmp)])
        self.assertEqual(s["filesystem"]["allowWrite"], [os.path.normpath(dossier)])
        self.assertEqual(lectures_interdites_par_defaut(dossier), [os.path.normpath(self.tmp)])

    def test_interdits_explicites_et_dossier_hors_interdits_refuse(self):
        dossier = os.path.join(self.tmp, "course", "G0-F01", "experience")
        os.makedirs(dossier)
        banque = os.path.join(self.tmp, "banque")
        o = construire_options(dossier, 1.0, 5, url_relais=RELAIS,
                               interdire_lecture=[os.path.join(self.tmp, "course"), banque])
        self.assertEqual(o["sandbox"]["filesystem"]["denyRead"], [os.path.join(self.tmp, "course"), banque])
        for interdits in ([], ["relatif"], [banque]):  # vide, relatif, ou ne couvrant pas le dossier de l'agent
            with self.subTest(interdits=interdits), self.assertRaises(ValueError):
                construire_options(dossier, 1.0, 5, url_relais=RELAIS, interdire_lecture=interdits)


class ReservationParRole(unittest.TestCase):
    """C1 : un rôle simulé d'un adaptateur mixte ne réserve rien ; la simulation pure réserve le plafond."""

    def test_reserve_suit_le_role_effectif(self):
        class Stub:
            pass

        class Mixte:
            roles_reels = frozenset(["proposeur"])

        g = Stub()
        g.adaptateur = Mixte()
        self.assertEqual(Generation._reserve_role(g, "experimentateur", 1.0), 0.0)
        self.assertEqual(Generation._reserve_role(g, "verificateur", 0.5), 0.0)
        self.assertEqual(Generation._reserve_role(g, "proposeur", 1.5), 1.5)
        g.adaptateur = Stub()  # simulation pure : pas de roles_reels
        self.assertEqual(Generation._reserve_role(g, "experimentateur", 1.0), 1.0)


class RegleEBHCorrigee(unittest.TestCase):
    """C5 : le filtre de marge agit avant le tri (e = 0), m est fixé avant les issues."""

    @staticmethod
    def issue(traj, marge=None):
        pari = {"trajectoire_log_w": traj}
        if marge is not None:
            pari["marge_atteinte"] = marge
        return {"verdict_final": "survit", "pari": pari}

    def test_fille_sans_marge_ne_compte_pas_dans_k_etoile(self):
        # m = 3 : seuils log(3/(0,05·k)) = 4,09 / 3,40 / 3,00 pour k = 1, 2, 3.
        # F1 (fille, marge non atteinte) à 4,1 et N1 (nulle) à 3,6 : avec l'ancienne règle, k* = 2 retenait {F1, N1} puis
        # F1 était rétrogradée après coup : N1 promue grâce à une fille filtrée. Corrigé : F1 vaut e = 0, k* = 0.
        issues = {"F1": self.issue([4.1], marge=False), "N1": self.issue([3.6]), "N2": self.issue([0.1])}
        r = appliquer_multiplicite(issues, 0.05)
        self.assertEqual(r["retenues"], [])
        self.assertEqual(issues["N1"]["verdict_final"], "eliminee")
        self.assertIsNone(issues["F1"]["pari"]["multiplicite"]["log_e"])
        # avec la marge atteinte, F1 est bien retenue, et N1 avec elle (k* = 2)
        issues = {"F1": self.issue([4.1], marge=True), "N1": self.issue([3.6]), "N2": self.issue([0.1])}
        r = appliquer_multiplicite(issues, 0.05)
        self.assertEqual(sorted(r["retenues"]), ["F1", "N1"])

    def test_m_fixe_avant_les_issues(self):
        issues = {"F1": self.issue([4.0])}
        self.assertEqual(appliquer_multiplicite(dict(issues), 0.05)["m"], 1)
        r = appliquer_multiplicite(dict(issues), 0.05, m_fixe=5)  # quatre fiches non jugées (e = 0) comptent dans m
        self.assertEqual(r["m"], 5)
        self.assertEqual(r["retenues"], [])  # log(5/0,05) = 4,6 > 4,0
        with self.assertRaises(ValueError):
            appliquer_multiplicite(dict(issues), 0.05, m_fixe=0)


class SignatureAvecMoniteur(unittest.TestCase):
    """C4 : la même loi sur deux moniteurs ne partage ni classe ni héritage ; la transposition de moniteur est jugeable."""

    def test_meme_loi_autre_moniteur_autre_classe(self):
        rng = random.Random(4)
        a = sp.loi_softmax_aleatoire(rng, force=1.5)
        m = Memoire(graine=1)
        def fp(ident, moniteur):
            return fiche(ident, enonce=VRAIE, loi_predictive=a, severite_attendue=0.05, seuil=20.0,
                         espace_instances={"nombre_issues": 3, "dimension": 2, "moniteur": moniteur})
        f1 = fp("F1", "M0")
        f1.statut = "eliminee"
        m.indexer(f1, issue_testee(2.0), 0)
        meme, autre = fp("F2", "M0"), fp("F3", "M1")
        self.assertEqual(m.chercher_classe(meme)[0], "F1")
        self.assertIsNone(m.chercher_classe(autre)[0])
        self.assertTrue(math.isinf(Memoire.divergence_moyenne(m.signature(meme), m.signature(autre))))
        m.nouvelle_generation()
        self.assertTrue(m.garde_redite(autre)["accepte"])
        self.assertIsNone(m.heritage("F3"))  # aucun héritage d'un autre moniteur


class RelaisCheminsV11(unittest.TestCase):
    """C10 : seuls les messages sont relayés ; les lots (`batches`) sont refusés."""

    def test_chemins(self):
        self.assertEqual(CHEMINS_PERMIS, ("/v1/messages",))
        self.assertIn("/v1/messages/batches", CHEMINS_REFUSES)
        permis = lambda c: c.startswith(CHEMINS_PERMIS) and not c.startswith(CHEMINS_REFUSES)  # noqa: E731
        self.assertTrue(permis("/v1/messages"))
        self.assertTrue(permis("/v1/messages?beta=true"))
        self.assertFalse(permis("/v1/messages/batches"))
        self.assertFalse(permis("/v1/complete"))
        self.assertFalse(permis("/v1/"))


class SousPopulationParDefaut(unittest.TestCase):
    """C10 : le chercheur mécanique donne une loi par défaut à `par_sous_population` ; une sous-population absente du
    développement est évaluée sans erreur."""

    def test_defaut_present_et_evaluable(self):
        import os
        import tempfile
        from essais.aides import BASE
        from exemples.generer_monde_grammaire_v1 import generer_monde
        from pole.monde_banque import MondeBanque
        from pole.outils import ecrire_json_scelle
        from pole.proposeurs_references import propositions_mecaniques
        os.makedirs(BASE, exist_ok=True)
        tmp = tempfile.mkdtemp(dir=BASE)
        banque, _, _ = generer_monde(20261103, structures=["sous_population", "sous_population", "monotone"])
        chemin = os.path.join(tmp, "banque.json")
        ecrire_json_scelle(chemin, banque)
        monde = MondeBanque(chemin, 3)
        props = propositions_mecaniques(monde.description_publique(), monde.donnees_developpement(), 12)
        vues = 0
        for p in props:
            loi = p.get("loi_predictive")
            if isinstance(loi, dict) and loi.get("type") == "par_sous_population":
                vues += 1
                self.assertIn("defaut", loi)
                self.assertIsNotNone(loi["defaut"])
                table = sp.proba(loi, {"z": [0.1, -0.2, 0.3, 0.0], "g": 999}, [], 0)  # sous-population jamais vue
                self.assertAlmostEqual(sum(table), 1.0, places=6)
        self.assertGreater(vues, 0, "aucune loi par sous-population proposée par le chercheur mécanique sur ce monde")




class CanalDeTexteFiltre(unittest.TestCase):
    """C6 du socle : les leçons ne transportent ni issues recopiées ni vocabulaire du noyau."""

    def test_lignes_du_noyau_et_listes_de_nombres_retirees(self):
        from pole.memoire import Memoire, filtrer_canal_de_texte
        texte = ("Les lois sur deux traits semblent plus robustes.\n"
                 "Issues observées : 0, 1, 2, 2, 1, 0, 1, 2, 0, 1\n"
                 "log W cumulé de la classe : 3,42\n"
                 "La richesse finale a dépassé le seuil.\n"
                 "Préférer les softmax à force modérée (1 à 2).")
        propre = filtrer_canal_de_texte(texte)
        self.assertEqual(propre.splitlines(), ["Les lois sur deux traits semblent plus robustes.",
                                               "Préférer les softmax à force modérée (1 à 2)."])
        m = Memoire(graine=1)
        self.assertNotIn("log W", m.ajouter_lecon(0, texte))
        self.assertNotIn("Issues", m.texte_consigne("recombinaison"))


class VuePubliqueSansTemoin(unittest.TestCase):
    """C5 du socle : l'énoncé servi aux agents ne dit plus « Témoin vrai : »."""

    def test_prefixe_neutralise(self):
        f = fiche("T1", enonce="Témoin vrai : la loi exacte du moniteur M0 (monotone)", temoin="vraie")
        self.assertEqual(f.vue_publique()["enonce"], "la loi exacte du moniteur M0 (monotone)")
        self.assertNotIn("temoin", f.vue_publique())
        g = fiche("T2", enonce="Témoin faux : l'issue suivrait le trait de bruit", temoin="fausse")
        self.assertFalse(g.vue_publique()["enonce"].lower().startswith("témoin"))
        self.assertEqual(f.vue_complete_gelee()["enonce"], "Témoin vrai : la loi exacte du moniteur M0 (monotone)")




class CleDuRelaisHorsDeProc(unittest.TestCase):
    """F-C7 : la clé lue dans un fichier à lecture unique n'entre jamais dans l'environnement du relais."""

    def test_lecture_unique_et_mode(self):
        import stat
        import tempfile
        from pole.relais_reel import RelaisInvalide, lire_cle_fichier
        from essais.aides import BASE
        os.makedirs(BASE, exist_ok=True)
        d = tempfile.mkdtemp(dir=BASE)
        chemin = os.path.join(d, "cle")
        with open(chemin, "w", encoding="utf-8") as f:
            f.write("FACTICE-sans-valeur\n")
        os.chmod(chemin, 0o644)
        with self.assertRaises(RelaisInvalide):  # lisible par d'autres : refusé
            lire_cle_fichier(chemin)
        os.chmod(chemin, stat.S_IRUSR | stat.S_IWUSR)
        self.assertEqual(lire_cle_fichier(chemin), "FACTICE-sans-valeur")
        self.assertFalse(os.path.exists(chemin))  # supprimé après lecture
        with self.assertRaises(RelaisInvalide):
            lire_cle_fichier(chemin)

    def test_demonstration_proc(self):
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demonstrations"))
        import verification_cle_proc_v7 as v
        resultats, code = v.demonstration()
        self.assertEqual(code, 0, resultats)
        self.assertEqual(resultats["par_fichier"]["noms_dans_proc"], [])
        self.assertEqual(resultats["par_environnement"]["noms_dans_proc"], ["ANTHROPIC_API_KEY"])




class SeuilDeFusionAuGabarit(unittest.TestCase):
    """F-C4 (iii), v12 : avec une référence tirée au gabarit du monde, les lois du gabarit ne fusionnent plus par dizaines."""

    def test_fausses_fusions_au_gabarit(self):
        from exemples.generer_monde_grammaire_v2 import generer_monde
        from pole.memoire import Memoire
        from pole.proposeurs_references import generateur_reference_au_gabarit, propositions_aleatoires
        from pole.monde_banque import MondeBanque
        import tempfile
        from essais.aides import BASE
        os.makedirs(BASE, exist_ok=True)
        tmp = tempfile.mkdtemp(dir=BASE)
        banque, _, _ = generer_monde(20261104)
        chemin = os.path.join(tmp, "banque.json")
        from pole.outils import ecrire_json_scelle
        ecrire_json_scelle(chemin, banque)
        description = MondeBanque(chemin, 3).description_publique()
        lois = [p["loi_predictive"] for p in propositions_aleatoires(description, 60, 5, 0)]
        monit = [p["moniteur"] for p in propositions_aleatoires(description, 60, 5, 0)]

        def fp(ident, loi, moniteur):
            return fiche(ident, enonce=VRAIE, loi_predictive=loi, severite_attendue=0.05, seuil=20.0,
                         espace_instances={"nombre_issues": 3, "dimension": 4, "moniteur": moniteur})

        taux = {}
        for nom, gen in (("defaut", None), ("gabarit", generateur_reference_au_gabarit(description))):
            m = Memoire(graine=1, generateur_reference=gen)
            for i in range(30):  # archive : 30 lois du gabarit, éliminées
                f = fp(f"A{i}", lois[i], monit[i])
                f.statut = "eliminee"
                m.indexer(f, issue_testee(-1.0), 0)
            fusions = sum(m.chercher_classe(fp(f"N{i}", lois[i], monit[i]))[0] is not None for i in range(30, 60))
            taux[nom] = fusions / 30
        self.assertLessEqual(taux["gabarit"], 0.15, taux)  # 5 % par fiche visé ; borne large
        self.assertLessEqual(taux["gabarit"], taux["defaut"], taux)




class BanqueV3Temoins(unittest.TestCase):
    """Banque v3 (v14) : témoins vrais établis par confirmation croisée sur le développement, témoins faux par permutation."""

    def test_sur_un_monde_de_la_grammaire(self):
        import tempfile
        from essais.aides import BASE
        from exemples.generer_monde_grammaire_v1 import generer_monde
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "exemples"))
        import construire_banque_t05_v3 as b3
        os.makedirs(BASE, exist_ok=True)
        banque, _, _ = generer_monde(20261105, structures=["monotone", "combinaison", "sous_population"])
        fiches, bilan = b3.fabriquer_temoins(banque, 20261105, nombre_max=6, par_recherche=30)
        self.assertGreaterEqual(bilan["vrais_confirmes"], 1, bilan)        # des structures vraies, confirmées sur B
        self.assertLessEqual(bilan["faux_permutation_confirmes"], 1, bilan)  # la permutation détruit le lien (≤ 1 sur 30 au hasard)
        vrais = [f for f in fiches if f["temoin"] == "vraie"]
        self.assertTrue(all("gain de confirmation" in f["source"] for f in vrais))
        self.assertTrue(all(not f["enonce"].lower().startswith("témoin") for f in fiches))




class LectureCouche1Bis(unittest.TestCase):
    """v16 : la lecture P3 (ii) de bout en bout sur une banque v3 tirée de la grammaire (témoins établis et par permutation)."""

    def test_de_bout_en_bout(self):
        import tempfile
        from essais.aides import BASE
        from exemples.generer_monde_grammaire_v1 import generer_monde
        from pole.outils import ecrire_json_scelle
        racine = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, os.path.join(racine, "exemples"))
        sys.path.insert(0, os.path.join(racine, "demonstrations"))
        import construire_banque_t05_v3 as b3
        import demo_couche1bis_v7 as demo
        os.makedirs(BASE, exist_ok=True)
        tmp = tempfile.mkdtemp(dir=BASE)
        banque, _, _ = generer_monde(20261106, structures=["monotone", "combinaison", "sous_population"])
        fiches, bilan = b3.fabriquer_temoins(banque, 20261106, nombre_max=3, par_recherche=20)
        self.assertGreater(bilan["vrais_confirmes"], 0)
        self.assertTrue(any(f["temoin"] == "fausse" for f in fiches))
        ecrire_json_scelle(os.path.join(tmp, "banque.json"), banque)
        ecrire_json_scelle(os.path.join(tmp, "temoins.json"), fiches)
        lecture = demo.executer(os.path.join(tmp, "banque.json"), os.path.join(tmp, "temoins.json"), os.path.join(tmp, "course"),
                                generations=2, propositions=8)
        self.assertEqual(lecture["generations"], 2, lecture["arret"])
        self.assertEqual(lecture["L1_temoins_faux_promus"], [])
        self.assertIn(lecture["L2_etat_dents"], ("dents", "pas de dents"))




class MoniteursPlantes(unittest.TestCase):
    """v17 : moniteurs plantés sur les traits réels (lois à seuil non linéaires), témoins vrais et faux plantés."""

    def test_planter_et_temoins(self):
        from exemples.generer_monde_grammaire_v1 import generer_monde
        racine = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, os.path.join(racine, "exemples"))
        import construire_banque_t05_v3 as b3
        banque, _, _ = generer_monde(20261107, structures=["monotone", "monotone", "monotone"])
        banque["traits"] = list(banque["traits"][:-1]) + ["bruit"]  # le dernier trait joue le bruit
        plantes = b3.planter(banque, 2, 20261107)
        self.assertEqual([p["moniteur"] for p in plantes], ["plante:0", "plante:1"])
        self.assertTrue(all(l["issues"]["plante:0"] in (0, 1, 2) for l in banque["instances"]))
        self.assertNotIn("loi", json.dumps(banque["moniteurs"]["plante:0"]))  # la loi n'est pas dans la banque
        fiches, bilan = b3.fabriquer_temoins(banque, 20261107, nombre_max=2, par_recherche=10, plantes=plantes)
        ids = {f["identifiant"]: f["temoin"] for f in fiches}
        self.assertEqual((ids.get("TVP01"), ids.get("TFP01")), ("vraie", "fausse"))
        self.assertEqual(len(bilan["plantes"]), 2)




class TraitsInternes(unittest.TestCase):
    """v18 : traits internes = composantes principales ajustées sur le seul calibrage."""

    def test_projection_ajustee_sur_le_calibrage_seul(self):
        import tempfile
        import numpy as np
        from essais.aides import BASE
        racine = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, os.path.join(racine, "exemples"))
        import construire_banque_t05_v3 as b3
        os.makedirs(BASE, exist_ok=True)
        tmp = tempfile.mkdtemp(dir=BASE)
        rng = np.random.default_rng(np.random.SeedSequence(20261027))
        parties = ["calibrage"] * 6 + ["developpement"] * 3 + ["epreuve"] * 3

        def banque():
            return {"traits": ["a", "bruit"], "instances": [{"identifiant": f"t{i}/e0", "partie": p, "z": [0.0, 0.0], "g": 0, "issues": {}}
                                                           for i, p in enumerate(parties)]}

        tableaux = {f"t{i}__e0|15": rng.normal(size=(1, 10, 16)).astype(np.float16) for i in range(12)}
        chemin = os.path.join(tmp, "v.npz")
        np.savez(chemin, **tableaux)
        b = banque()
        b3.ajouter_traits_internes(b, [chemin], 15, 2)
        self.assertEqual(b["traits"], ["a", "bruit", "interne_c15_pc1", "interne_c15_pc2"])
        self.assertEqual(len(b["instances"][0]["z"]), 4)
        # changer un vecteur d'épreuve ne change pas la projection des instances de calibrage (ajustée sur le calibrage seul)
        tableaux["t11__e0|15"] = (tableaux["t11__e0|15"] * 50).astype(np.float16)
        chemin2 = os.path.join(tmp, "v2.npz")
        np.savez(chemin2, **tableaux)
        b2 = banque()
        b3.ajouter_traits_internes(b2, [chemin2], 15, 2)
        self.assertEqual([l["z"] for l in b["instances"][:9]], [l["z"] for l in b2["instances"][:9]])
        with self.assertRaises(ValueError):  # une instance sans vecteur est refusée
            b3.ajouter_traits_internes(banque(), [chemin], 7, 2)




class NotationsSupplementaires(unittest.TestCase):
    """v19 : notations sans épisodes (e2) ajoutées ; une notation en double est refusée (R5 : cas sain et artefact)."""

    def test_e2_ajoute_et_double_refuse(self):
        import tempfile
        from essais.aides import BASE
        racine_code = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, os.path.join(racine_code, "exemples"))
        import construire_banque_t05_v3 as b3
        os.makedirs(BASE, exist_ok=True)
        tmp = tempfile.mkdtemp(dir=BASE)
        racine = os.path.join(tmp, "main")
        os.makedirs(os.path.join(racine, os.path.dirname(b3.EPISODES)))
        taches = [f"t{i}" for i in range(40)]
        fiches = [{"episode": f"{t}/e{k}", "tache": t, "jetons_par_action": [10 + k, 12, 9], "bilan": {"actions_valides": 3}}
                  for t in taches for k in range(3)]
        json.dump({"resultat": {"fiches": fiches}}, open(os.path.join(racine, b3.EPISODES), "w"))
        notes = {r: (i % 4) + 1 for i, r in enumerate(b3.RUBRIQUES)}

        def ecrire(dossier, ks, juge):
            os.makedirs(dossier, exist_ok=True)
            ns = [{"cle": f"juge-{juge}/{t}/e{k}/passe-0", "notes": dict(notes, BALANCE=(int(t[1:]) + k) % 3 + 1)}
                  for t in taches for k in ks]
            chemin = os.path.join(dossier, f"notations-{juge}-decisives.json")
            json.dump({"resultat": {"notations": ns}}, open(chemin, "w"))
            return chemin

        base = {j: ecrire(os.path.join(tmp, "base"), (0, 1), j) for j in ("8B", "3B")}
        for j in ("8B", "3B"):
            ecrire(os.path.join(tmp, "e2"), (2,), j)
        banque = b3.construire(racine, 7, notations=base, notations_supplementaires=[os.path.join(tmp, "e2")])
        self.assertEqual(len(banque["instances"]), 120)
        self.assertEqual(banque["sous_populations"], 3)
        for j in ("8B", "3B"):
            ecrire(os.path.join(tmp, "double"), (1,), j)  # e1 déjà noté : artefact
        with self.assertRaises(ValueError):
            b3.construire(racine, 7, notations=base, notations_supplementaires=[os.path.join(tmp, "double")])


if __name__ == "__main__":
    unittest.main()
