"""Essais de la v54 — corrections exigées par l'annexe du bras méta (brouillon 1, section 10, I-1 à I-10), et lecture du
format réel de l'annexe (bloc `parametres_bras_meta`, bloc `jeu_essai_non_vacuite`). Hors ligne ; moteur simulé v54."""

import json
import os
import re
import shutil
import sys
import unittest

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, ICI)

import aides_v54 as A  # noqa: E402
from aides import CasAvecDossier  # noqa: E402
from pole import bisociateur_v54 as b54  # noqa: E402
from pole import configuration_v54 as cfg  # noqa: E402
from pole import course2_v54 as c2  # noqa: E402
from pole.outils import ecrire_scelle, sha256_fichier  # noqa: E402

ANNEXE_REELLE = os.path.join(RACINE, *[os.pardir] * 4, "brouillons", "canal-reprise-releve-v1", "envois",
                             "pole-scientifique-automatique-v1", "pre-pilote-course-2-v1", "annexe-bras-meta-v1-brouillon1.md")


def lire(chemin):
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


class Base(CasAvecDossier):
    def conf(self, **modifs):
        return cfg.lire_configuration_v54(A.configuration(self.tmp, **modifs), base=self.tmp)

    def annexe(self, nom, **modifs):
        return A.annexe_meta(self.tmp, nom=nom, **modifs)

    def decl(self, annexe=None, **meta):
        conf = A.configuration(self.tmp)
        if annexe:
            conf["bisociateur"]["meta"]["annexe"] = annexe
        conf["bisociateur"]["meta"].update(meta)
        conf = cfg.lire_configuration_v54(conf, base=self.tmp)
        return c2.declarer_bras_v54(conf)[0]["meta"], conf


class TestI1NomsDeStructures(Base):
    def test_unitaire_nom_different_refuse(self):
        n, s, aff = b54.valider_niche_v54({"niche": "n1_seq", "structures": ["me_cusum", {"type": "om_martingale", "nom": "om_martingale"}],
                                           "affirmation_centrale": "a"}, A.NICHES, A.STRUCTURES)
        self.assertEqual(s, frozenset({("me_cusum", "me_cusum"), ("om_martingale", "om_martingale")}))
        self.assertEqual(aff, "a")
        with self.assertRaisesRegex(b54.BisociationRefusee, "I-1"):
            b54.valider_niche_v54({"niche": "n1_seq", "structures": [{"type": "me_cusum", "nom": "CUSUM"}]}, A.NICHES, A.STRUCTURES)
        with self.assertRaisesRegex(b54.BisociationRefusee, "hors liste"):
            b54.valider_niche_v54({"niche": "n1_seq", "structures": ["me_inconnue"]}, A.NICHES, A.STRUCTURES)

    def test_generation_compte_les_refus_aucune_baisse_silencieuse(self):
        ad = A.adaptateurs()
        orig = ad["claude"].reponse

        def rep(role, consigne, modele):
            t = orig(role, consigne, modele)
            if "## Lecture : niches" in consigne:
                o = json.loads(t)
                o["structures"] = [{"type": o["structures"][0], "nom": "autre nom"}]
                t = json.dumps(o)
            return t
        ad["claude"].reponse = rep
        g = c2.GenerationV54(self.conf(), os.path.join(self.tmp, "s"), ad)
        g.executer()
        fin = lire(os.path.join(self.tmp, "s", "manifeste-fin.json"))
        self.assertEqual(fin["refus_lectures"]["meta"], 8)  # 4 fiches × 2 lecteurs, chacune refusée nommément
        self.assertTrue(any(e["evenement"] == "lecture-rejetee" and "I-1" in e["motif"] for e in fin["evenements"]))
        self.assertEqual(fin["c12"]["causes"].get("non produit (aucune paire éligible)"), 1)


class TestI2Desaccord(Base):
    def test_desaccord_lu_apres_les_paires_journal_au_coffre_hors_score(self):
        g = c2.GenerationV54(self.conf(), os.path.join(self.tmp, "s"), A.adaptateurs())
        g.executer()
        j = g.coffre.ouvrir("pp2-desaccord-paires")
        p = g.coffre.ouvrir("pp2-paires-par-bras")
        self.assertTrue(j["lignes"])
        self.assertLessEqual(len(j["lignes"]), 3)
        self.assertEqual(j["lignes"][0]["paire"], p["paires"]["meta"][0])  # la paire retenue d'abord
        self.assertTrue(all(l["horodatage"] >= p["horodatage"] for l in j["lignes"]))
        self.assertTrue(all(set(l["reponses"].values()) <= set(b54.REPONSES_DESACCORD) for l in j["lignes"]))
        lect = g.coffre.ouvrir("pp2-lectures-etiquettes")["meta"]
        self.assertTrue(all(isinstance(v[2], str) for d in lect.values() for v in d.values()))  # affirmation centrale gardée

    def test_artefact_score_qui_varie_avec_le_desaccord(self):
        p = A.parametres_meta()

        def triche(pp, na, nb, sa, sb, desaccord=None):
            return b54.score_meta(pp, na, nb, sa, sb) * (2 if desaccord == "oui" else 1) + (0.1 if desaccord == "oui" else 0)

        def triche_kw(pp, na, nb, sa, sb, **kw):
            return b54.score_meta(pp, na, nb, sa, sb) + (1 if kw.get("desaccord") == "non" else 0)

        def honnete_kw(pp, na, nb, sa, sb, **kw):
            return b54.score_meta(pp, na, nb, sa, sb)
        self.assertTrue(b54.garde_desaccord_v54(b54.score_meta, p, "n1_seq", "n2_act", set(), set()))
        self.assertTrue(b54.garde_desaccord_v54(honnete_kw, p, "n1_seq", "n2_act", set(), set()))
        for f in (triche, triche_kw):
            with self.subTest(f.__name__), self.assertRaisesRegex(b54.BisociationRefusee, "désaccord entre dans le score"):
                b54.garde_desaccord_v54(f, p, "n1_seq", "n2_act", set(), set())

    def test_artefact_ordre_lecture_avant_les_paires(self):
        with self.assertRaisesRegex(b54.BisociationRefusee, "antérieure"):
            c2.verifier_ordre_desaccord("2026-10-31T10:00:00.000001+00:00", [{"horodatage": "2026-10-31T09:59:59.000000+00:00"}])
        self.assertTrue(c2.verifier_ordre_desaccord("2026-10-31T10:00:00+00:00", [{"horodatage": "2026-10-31T10:00:01+00:00"}]))


class TestI3S28(Base):
    def test_s28_calcule_et_seuils_de_l_annexe_ou_de_la_configuration(self):
        g = c2.GenerationV54(self.conf(), os.path.join(self.tmp, "s"), A.adaptateurs())
        g.executer()
        acc = lire(os.path.join(self.tmp, "s", "accords.json"))["s28"]
        self.assertEqual(acc["seuils"]["source"], "annexe")
        self.assertTrue(acc["lisible"])
        d, _ = self.decl(s28={"kappa_min": 0.9, "jaccard_min": 0.9})
        self.assertEqual(d["s28"]["source"], "configuration")
        sans = self.annexe("sans-s28.md", accord_min_niche_kappa=None)
        d, _ = self.decl(annexe=sans)
        self.assertFalse(d["produit"])
        self.assertIn("I-3", d["motif"])

    def test_accord_illisible_marque_sans_retirer_le_bras(self):
        l1 = {"a": ("n1", frozenset({("x", "x")})), "b": ("n2", frozenset())}
        l2 = {"a": ("n2", frozenset({("y", "y")})), "b": ("n1", frozenset())}
        r = b54.accord_s28(l1, l2, {"kappa_min": 0.4, "jaccard_min": 0.3})
        self.assertFalse(r["lisible"])
        self.assertIn("niches non lisibles", r["marque"])
        r = b54.accord_s28({"a": ("n1", frozenset()), "b": ("n1", frozenset())}, {"a": ("n1", frozenset()), "b": ("n1", frozenset())},
                           {"kappa_min": 0.4, "jaccard_min": 0.3})
        self.assertTrue(r["degenere"])


class TestI4Definitions(Base):
    def test_definitions_servies_au_lecteur(self):
        ad = A.adaptateurs()
        vues = []
        ad["claude"].decider = lambda r, c, m, n: (vues.append(c) if "## Lecture : niches" in c else None)
        c2.GenerationV54(self.conf(), os.path.join(self.tmp, "s"), ad).executer()
        self.assertTrue(vues and all("définition de n1_seq" in c and "définition de me_cusum" in c for c in vues))

    def test_artefacts_definitions_absentes_ou_consigne_incomplete(self):
        p = A.parametres_meta()
        p["definitions_niches"].pop("n2_act")
        d, _ = self.decl(annexe=self.annexe("def.md", definitions_niches=p["definitions_niches"]))
        self.assertFalse(d["produit"])
        self.assertIn("I-4", d["motif"])
        d, _ = self.decl(definitions="consigne")
        self.assertFalse(d["produit"])
        self.assertIn("absents de la consigne", d["motif"])
        conf = A.configuration(self.tmp)
        conf["pieces"]["consigne_lecteur"] = A.ecrire(os.path.join(self.tmp, "p", "lecteur-ids.md"),
                                                      "Lecteur (essai). Grille : " + ", ".join(A.NICHES + A.STRUCTURES))
        conf["bisociateur"]["meta"]["definitions"] = "consigne"
        conf = cfg.lire_configuration_v54(conf, base=self.tmp)
        self.assertTrue(c2.declarer_bras_v54(conf)[0]["meta"]["produit"])


class TestI5Divergence(unittest.TestCase):
    def test_regle_configurable(self):
        l1, l2 = ("n1", frozenset({("a", "a")})), ("n2", frozenset({("b", "b")}))
        self.assertIsNone(b54.retenir_meta(l1, l2, "fiche_ecartee", "union"))
        self.assertEqual(b54.retenir_meta(l1, l2, "premier_lecteur", "union"), l1)
        m = ("n1", frozenset({("a", "a"), ("b", "b")}))
        self.assertEqual(b54.retenir_meta(m, l1, "fiche_ecartee", "intersection"), ("n1", frozenset({("a", "a")})))
        self.assertEqual(b54.retenir_meta(m, l1, "fiche_ecartee", "union")[1], m[1])


class TestI6Types(Base):
    def test_artefacts_types_et_signes(self):
        cas = {"poids négatif": {"poids": -2}, "seuil textuel": {"seuil_communication_faible": "faible"},
               "table non numérique": {"communication": {"n1_seq|n2_act": "1", "n1_seq|n3_ano": 3, "n2_act|n3_ano": 0}},
               "nombre_min nul": {"structure_forte": {"nombre_min": 0, "types": ["me_cusum"]}},
               "types hors grille": {"structure_forte": {"nombre_min": 1, "types": ["inconnu"]}},
               "bande textuelle": {"bande": ["2", "3"]}, "niches en double": {"niches": ["n1_seq", "n1_seq", "n2_act", "n3_ano"]}}
        for i, (quoi, modif) in enumerate(cas.items()):
            with self.subTest(quoi):
                d, _ = self.decl(annexe=self.annexe(f"i6-{i}.md", **modif))
                self.assertFalse(d["produit"])
                self.assertIn("non produit (annexe non conforme)", d["cause"])
                # refusée par le contrôle de type, pas par une garde suivante (les niches en double tombent déjà au contrôle v53 des
                # tables, qui exige une valeur par paire de niches distinctes)
                self.assertIn("A20" if quoi == "niches en double" else "I-6", d["motif"])


class TestI7I8Paires(Base):
    def test_niches_indistinctes_comptees_c12(self):
        ad = A.adaptateurs()
        orig = ad["claude"].reponse

        def rep(role, consigne, modele):
            t = orig(role, consigne, modele)
            if "## Lecture : niches" in consigne:
                o = json.loads(t)
                o["niche"] = "n1_seq"
                t = json.dumps(o)
            return t
        ad["claude"].reponse = rep
        c2.GenerationV54(self.conf(), os.path.join(self.tmp, "s"), ad).executer()
        fin = lire(os.path.join(self.tmp, "s", "manifeste-fin.json"))
        self.assertEqual(fin["non_produits"]["meta"], "non produit (niches indistinctes sur ce lot)")
        self.assertEqual(fin["c12"]["causes"], {"non produit (niches indistinctes sur ce lot)": 1})

    def _deux(self):
        from pole.gardes_e0_v54 import _Aig, _fiche
        f1, f2 = _fiche("f1", {"t": 1}), _fiche("f2", {"t": 2})
        return f1, f2, _Aig({"f1": f1["empreinte"], "f2": f2["empreinte"]}), b54.cle_paire("f1", "f2")

    def test_n_egal_2_bras_de_priorite_1(self):
        f1, f2, aig, q = self._deux()
        choix, np_ = b54.choisir_paires_v54([f1, f2], {"meta": {q: ((1, 1.5), "profil")}, "basique": {q: (0.3, None)}},
                                            ["basique", "meta"], 1, aig, {"meta": {q: 0.5}, "basique": {q: 0.1}})
        self.assertEqual(choix, {"basique": [q], "meta": []})
        self.assertEqual(np_, {"meta": "non produit (effectif)"})
        choix, np_ = b54.choisir_paires_v54([f1, f2], {"meta": {}, "basique": {q: (0.3, None)}}, ["meta", "basique"], 1, aig,
                                            {"meta": {}, "basique": {q: 0.1}})
        self.assertEqual(choix, {"meta": [], "basique": []})  # le bras de priorité 1 ne la note pas : pas de report au suivant
        self.assertEqual(np_["meta"], "non produit (paire non notable par le bras de priorité 1)")
        self.assertEqual(np_["basique"], "non produit (effectif)")


class TestI9I10Annexe(Base):
    def test_artefacts_contre_lecture_approbation(self):
        cas = {"une seule empreinte": {"contre_lecture": "contre-lue, rapport " + "c" * 64},
               "sans décision": {"approbation_lazar": "approuvée par Lazar le 31 octobre"},
               "marqueur": {"approbation_lazar": "À REMPLIR"}, "mot de remplissage": {"contre_lecture": "à faire"}}
        for i, (quoi, modif) in enumerate(cas.items()):
            with self.subTest(quoi):
                d, _ = self.decl(annexe=self.annexe(f"i9-{i}.md", **modif))
                self.assertFalse(d["produit"])

    def test_non_vacuite_rejouee_a_e0(self):
        d, _ = self.decl()
        self.assertEqual(d["non_vacuite_e0"], {"argmax": ["e1", "e2"], "dans_profil": 1, "hors_profil": 4, "meme_niche": 1,
                                               "score_argmax": 1.5})
        cas = {"jeu absent": ({}, "jeu_essai_non_vacuite absent"),
               "profil vide": ({"e1": {"niche": "n1_seq", "structures": []}, "e3": {"niche": "n3_ano", "structures": []}}, "profil vide"),
               "tout dans le profil": ({"e1": {"niche": "n1_seq", "structures": ["me_cusum"]}, "e2": {"niche": "n2_act", "structures": ["me_cusum"]}},
                                       "toutes les paires")}
        for i, (quoi, (jeu, motif)) in enumerate(cas.items()):
            with self.subTest(quoi):
                d, _ = self.decl(annexe=A.annexe_meta(self.tmp, nom=f"i10-{i}.md", jeu=jeu))
                self.assertFalse(d["produit"])
                self.assertIn("I-10", d["motif"])
                self.assertIn(motif, d["motif"])


class TestAnnexeReelle(CasAvecDossier):
    """Lecture du brouillon 1 réel (bloc de configuration à son format) : refus tant que les deux champs portent « À REMPLIR » ;
    copie d'essai remplie (deux empreintes, une décision) acceptée ; non-vacuité recalculée par le code : 5 paires dans le
    profil, 36 hors profil, 4 de même niche, argmax e01–e04 à 2,0 (chiffres écrits par l'auteur de l'annexe, section 6,
    retrouvés ici par la vraie fonction)."""

    def setUp(self):
        super().setUp()
        if not os.path.isfile(ANNEXE_REELLE):
            self.skipTest("ESSAI SUR L'ANNEXE RÉELLE NON JOUÉ : brouillon 1 hors de la livraison")

    def test_format_reel(self):
        copie = os.path.join(self.tmp, "annexe-reelle.md")
        shutil.copyfile(ANNEXE_REELLE, copie)
        shutil.copyfile(ANNEXE_REELLE + ".sha256", copie + ".sha256")
        with open(copie + ".sha256", encoding="utf-8") as f:
            ligne = f.read()
        with open(copie + ".sha256", "w", encoding="utf-8") as f:
            f.write(ligne.split()[0] + "  " + os.path.basename(copie) + "\n")
        texte = open(copie, encoding="utf-8").read()
        ids = " ".join(re.findall(r"`((?:n\d_|om_|me_|jd_|pr_)[a-z_]+)`", texte))
        with self.assertRaisesRegex(b54.BisociationRefusee, "contre_lecture"):
            b54.lire_annexe_meta_v54(copie, sha256_fichier(copie), definitions="consigne", texte_consigne_lecteur=ids)
        rempli = texte.replace('"contre_lecture": "À REMPLIR"', f'"contre_lecture": "essai : relu {"d" * 64}, rapport {"e" * 64}"')
        rempli = rempli.replace('"approbation_lazar": "À REMPLIR"', '"approbation_lazar": "essai : R-999"')
        c2_ = os.path.join(self.tmp, "annexe-remplie.md")
        ecrire_scelle(c2_, rempli)
        p, jeu = b54.lire_annexe_meta_v54(c2_, sha256_fichier(c2_), definitions="consigne", texte_consigne_lecteur=ids)
        r = b54.verifier_non_vacuite(p, jeu)
        self.assertEqual((r["dans_profil"], r["hors_profil"], r["meme_niche"]), (5, 36, 4))
        self.assertEqual((r["argmax"], r["score_argmax"]), (["e01", "e04"], 2.0))
        self.assertEqual(b54.seuils_s28(p, "annexe"), {"kappa_min": 0.4, "jaccard_min": 0.3, "source": "annexe"})
        with self.assertRaisesRegex(b54.BisociationRefusee, "I-4"):
            b54.lire_annexe_meta_v54(c2_, sha256_fichier(c2_), definitions="annexe")


if __name__ == "__main__":
    unittest.main()
