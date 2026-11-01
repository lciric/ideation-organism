import json
import math
import os
import unittest

from essais.aides import CasAvecDossier, fiche, fiche_dict
from pole.fiche import Fiche, FicheInvalide, FicheModifieeApresGel, RegistreGel, ecrire_fiche_gelee, verifier_fichier_fiche
from pole.outils import sha256_fichier


class Validation(unittest.TestCase):
    def test_fiche_saine_acceptee(self):
        self.assertEqual(fiche().identifiant, "F1")

    def test_fiches_invalides_refusees(self):
        cas = [dict(severite_attendue=1.0), dict(severite_attendue=0.0), dict(severite_attendue=1.2),
               dict(prediction={"signe": "?", "valeur": 0.5}), dict(prediction={"signe": "+", "valeur": 0}),
               dict(temoin="peut-etre"), dict(domaines=[]), dict(identifiant="../evasion"), dict(seuil=float("nan")),
               dict(parents=["A", "B"])]
        for modif in cas:
            with self.subTest(modif=modif), self.assertRaises(FicheInvalide):
                Fiche.depuis_dict(fiche_dict(**modif)).valider()

    def test_champ_inconnu_refuse(self):
        with self.assertRaises(FicheInvalide):
            Fiche.depuis_dict(dict(fiche_dict(), champ_invente=1))


class Gel(CasAvecDossier):
    def test_empreinte_canonique_stable(self):
        a = fiche()
        b = Fiche.depuis_dict(dict(reversed(list(fiche_dict().items()))))
        self.assertEqual(a.empreinte(), b.empreinte())
        a.statut, a.essais = "survit", 3
        self.assertEqual(a.empreinte(), b.empreinte(), "le statut et les essais ne sont pas dans l'empreinte")

    def test_temoin_hors_de_la_vue_publique_mais_gele(self):
        a, b = fiche(), fiche(temoin="fausse")
        self.assertNotIn("temoin", a.vue_publique())
        self.assertEqual(a.empreinte(), b.empreinte(), "un témoin est indiscernable pour l'expérimentateur")
        self.assertNotEqual(a.empreinte_complete(), b.empreinte_complete())

    def test_fiche_inchangee_passe_la_verification(self):
        registre, f = RegistreGel(), fiche()
        registre.geler(f)
        self.assertTrue(registre.verifier(f))

    def test_fiche_modifiee_apres_gel_refusee(self):
        registre, f = RegistreGel(), fiche()
        registre.geler(f)
        f.seuil = 0.0
        with self.assertRaises(FicheModifieeApresGel):
            registre.verifier(f)
        with self.assertRaises(FicheModifieeApresGel):
            registre.geler(f)

    def test_verite_de_temoin_changee_apres_gel_refusee(self):
        registre, f = RegistreGel(), fiche(temoin="fausse")
        registre.geler(f)
        f.temoin = "vraie"
        with self.assertRaises(FicheModifieeApresGel):
            registre.verifier(f)

    def test_fichier_gele_est_l_empreinte(self):
        f = fiche()
        empreinte = ecrire_fiche_gelee(f, self.tmp)
        chemin = os.path.join(self.tmp, "fiche.json")
        self.assertEqual(empreinte, f.empreinte())
        self.assertEqual(sha256_fichier(chemin), f.empreinte())
        self.assertTrue(verifier_fichier_fiche(chemin, empreinte))
        with open(chemin, "w", encoding="utf-8") as sortie:
            json.dump(dict(f.vue_publique(), seuil=-1), sortie)
        self.assertFalse(verifier_fichier_fiche(chemin, empreinte))


class Aptitude(unittest.TestCase):
    def test_fiche_qui_ne_predit_rien(self):
        f = fiche(severite_attendue=0.999, seuil=-3.09)
        self.assertLess(f.aptitude(), 0.01)

    def test_aptitude_est_la_severite_jamais_l_ampleur(self):
        self.assertAlmostEqual(fiche(severite_attendue=0.001).aptitude(), -math.log(0.001))
        grand, petit = fiche(prediction={"signe": "+", "valeur": 9.0}), fiche(prediction={"signe": "+", "valeur": 0.1})
        self.assertEqual(grand.aptitude(), petit.aptitude())


if __name__ == "__main__":
    unittest.main()
