import os
import random
import unittest

from essais.aides import CasAvecDossier, fiche
from pole import selection_pari as sp
from pole.cycle import Budget, ConfigGeneration, Generation, mesure_qualite
from pole.fiche import FicheModifieeApresGel, RegistreGel
from pole.simulation import AdaptateurSimule, MondeSimule

VRAIE = "La moyenne des mesures d'essai est positive sous traitement"
FAUSSE = "Le nom du fichier change la moyenne des mesures d'essai"


class CasGeneration(CasAvecDossier):
    def adaptateur(self, **reglages):
        monde = MondeSimule(3, {VRAIE: True, FAUSSE: False})
        return AdaptateurSimule(graine=3, monde=monde, **reglages)

    def generation(self, fiches, adaptateur, numero=0, budget=20.0, registre=None, **config):
        self.registre = registre or getattr(self, "registre", None) or RegistreGel()
        self.budget = Budget(budget)
        cfg = ConfigGeneration(**config)
        return Generation(numero, adaptateur, cfg, self.tmp, self.registre, self.budget).executer(fiches)


class Verification(CasGeneration):
    def test_honnete_confirme(self):
        v, f = fiche("V1", enonce=VRAIE), fiche("F1", enonce=FAUSSE)
        r = self.generation([v, f], self.adaptateur())
        self.assertEqual((v.statut, f.statut), ("survit", "eliminee"))
        self.assertTrue(r["issues"]["V1"]["verification"]["confirme"])

    def test_tricheur_qui_change_le_test_rejete(self):
        f = fiche("F1", enonce=FAUSSE)
        self.generation([f], self.adaptateur(profils={"F1": "change_test"}))
        self.assertEqual(f.statut, "rejetee (test change)")

    def test_verdict_sans_calcul_infirme(self):
        f = fiche("F1", enonce=FAUSSE)
        r = self.generation([f], self.adaptateur(profils={"F1": "sans_calcul"}))
        self.assertEqual(f.statut, "indecise")
        self.assertTrue(r["issues"]["F1"]["desaccord"])

    def test_verificateur_du_meme_modele_refuse(self):
        ConfigGeneration(modele_experimentateur="a", modele_verificateur="b").valider()
        with self.assertRaises(ValueError):
            ConfigGeneration(modele_experimentateur="a", modele_verificateur="a").valider()

    def test_fiche_modifiee_apres_gel_jamais_executee(self):
        adaptateur, f = self.adaptateur(), fiche("V1", enonce=VRAIE)
        g = Generation(0, adaptateur, ConfigGeneration(), self.tmp, RegistreGel(), Budget(10))
        self.assertIsNone(g.geler(f))
        f.seuil = -10.0
        issue = g.traiter(f)
        self.assertEqual(issue["verdict_final"], "refusee (modifiee apres gel)")
        self.assertEqual(adaptateur.appels, [])


class SelectionEtBudget(CasGeneration):
    def test_selection_par_severite(self):
        severe = fiche("S1", enonce=VRAIE, severite_attendue=0.001, seuil=3.090232)
        rien = fiche("R1", enonce=VRAIE + " (presque rien)", severite_attendue=0.999, seuil=-3.090232)
        self.generation([severe, rien], self.adaptateur())
        self.assertEqual((severe.statut, rien.statut), ("survit", "survit"))
        self.assertAlmostEqual(severe.aptitude(), 6.907755, places=5)
        self.assertLess(rien.aptitude(), 0.01)

    def test_indecise_un_essai_de_plus_puis_retiree(self):
        f, adaptateur, registre = fiche("V1", enonce=VRAIE), self.adaptateur(p_echec=1.0), RegistreGel()
        self.generation([f], adaptateur, 0, registre=registre)
        self.assertEqual((f.statut, f.essais), ("indecise", 1))
        self.generation([f], adaptateur, 1, registre=registre)
        self.assertEqual((f.statut, f.essais), ("retiree", 2))

    def test_la_generation_s_arrete_au_plafond(self):
        fiches = [fiche(f"F{i}", enonce=f"{FAUSSE} {i}") for i in range(6)]
        r = self.generation(fiches, self.adaptateur(), budget=3.0, concurrence=2)
        lancees = [f for f in fiches if f.statut != "hors budget"]
        # réservation 1,5 par fiche (expérimentateur 1,0 + vérificateur 0,5) ; coût déclaré 0,55 par fiche :
        # vague 1 → 2 fiches (3,0 réservés), réglées à 1,1 ; vague 2 → une fiche de plus (2,6), la suivante dépasserait.
        self.assertEqual(len(lancees), 3)
        self.assertEqual(sum(f.statut == "hors budget" for f in fiches), 3)
        self.assertTrue(r["arret_budget"])
        self.assertLessEqual(self.budget.depense, 3.0)

    def test_budget_suffisant_tout_tourne(self):
        fiches = [fiche(f"F{i}", enonce=f"{FAUSSE} {i}") for i in range(6)]
        r = self.generation(fiches, self.adaptateur(), budget=20.0, concurrence=3)
        self.assertFalse(r["arret_budget"])
        self.assertNotIn("hors budget", {f.statut for f in fiches})


class Temoins(CasGeneration):
    def temoins(self):
        return fiche("T1", enonce=VRAIE, temoin="vraie"), fiche("T2", enonce=FAUSSE, temoin="fausse")

    def test_pole_honnete(self):
        v, f = self.temoins()
        q = self.generation([v, f], self.adaptateur())["qualite"]
        self.assertEqual((v.statut, f.statut), ("survit", "eliminee"))
        self.assertEqual((q["taux_fausses_gardees"], q["taux_vraies_eliminees"]), (0.0, 0.0))

    def test_pole_complaisant_la_mesure_le_dit(self):
        v, f = self.temoins()
        adaptateur = self.adaptateur(profils={"T1": "sans_calcul", "T2": "sans_calcul"}, verificateur="complaisant")
        q = self.generation([v, f], adaptateur)["qualite"]
        self.assertEqual((v.statut, f.statut), ("survit", "survit"))
        self.assertEqual(q["taux_fausses_gardees"], 1.0)

    def test_verite_de_temoin_alteree_detectee(self):
        v, f = self.temoins()
        self.generation([v, f], self.adaptateur())
        f.temoin = "vraie"
        with self.assertRaises(FicheModifieeApresGel):
            mesure_qualite([v, f], self.registre)


class SelectionParPari(CasGeneration):
    def fiche_pari(self, identifiant, enonce, loi, **modifs):
        return fiche(identifiant, enonce=enonce, loi_predictive=loi, severite_attendue=0.05, seuil=20.0,
                     espace_instances={"nombre_issues": 3, "dimension": 2}, **modifs)

    def lois(self):
        rng = random.Random(8)
        return sp.loi_softmax_aleatoire(rng, force=2.0), sp.loi_softmax_aleatoire(rng, force=2.0)

    def test_pari_honnete_calcule_par_l_orchestrateur(self):
        a, b = self.lois()
        v, f = self.fiche_pari("V1", VRAIE, a), self.fiche_pari("F1", FAUSSE, b)
        r = self.generation([v, f], self.adaptateur(), selection="pari", taille_plan=80)
        self.assertEqual((v.statut, f.statut), ("survit", "eliminee"))
        self.assertTrue(r["issues"]["V1"]["pari"]["promue"])
        with open(os.path.join(self.tmp, "archive", "generations", "generation-00", "V1", "traces-experience", "consigne.txt"),
                  encoding="utf-8") as f_consigne:
            consigne = f_consigne.read()
        self.assertIn("Tu ne calcules aucune richesse", consigne)

    def test_pari_tirages_fabriques_infirmes(self):
        a, _ = self.lois()
        f = self.fiche_pari("F1", FAUSSE, a)
        self.generation([f], self.adaptateur(profils={"F1": "sans_calcul"}), selection="pari", taille_plan=80)
        self.assertEqual(f.statut, "indecise")

    def test_pari_loi_changee_rejetee(self):
        a, _ = self.lois()
        f = self.fiche_pari("F1", FAUSSE, a)
        self.generation([f], self.adaptateur(profils={"F1": "change_test"}), selection="pari", taille_plan=80)
        self.assertEqual(f.statut, "rejetee (test change)")

    def test_pari_severite_autre_que_alpha_refusee(self):
        a, _ = self.lois()
        f = fiche("F1", enonce=VRAIE, loi_predictive=a, severite_attendue=0.01)
        self.generation([f], self.adaptateur(), selection="pari")
        self.assertEqual(f.statut, "refusee (invalide)")

    def test_fille_copie_d_un_parent_eliminee(self):
        a, b = self.lois()
        copie = self.fiche_pari("C1", VRAIE, a, parents=["PA", "PB"], ce_que_la_fille_predit_de_plus="rien de neuf")
        g = Generation(0, self.adaptateur(), ConfigGeneration(selection="pari", taille_plan=80), self.tmp, RegistreGel(),
                       Budget(10), lois_connues={"PA": a, "PB": b})
        r = g.executer([copie])
        self.assertEqual(copie.statut, "eliminee", r["issues"]["C1"].get("motif"))
        self.assertLessEqual(r["issues"]["C1"]["pari"]["gain_moyen_sur_meilleure_enveloppe"], 1e-9)


if __name__ == "__main__":
    unittest.main()
