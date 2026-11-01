"""Essais de la version 0.6.0, pièce 3 : la répétition générale (adaptateur réel, relais réel, amont factice, faux
moteur) sur une génération. Cas sain : tout tenu. Artefact (R5) : un relais au plafond presque nul refuse les agents, et
la répétition le voit (la course ne va pas au bout, le relais n'a rien servi)."""

import os
import sys
import unittest

from essais.aides import CasAvecDossier

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "demonstrations"))

import repetition_generale_v6 as rg  # noqa: E402


class RepetitionGenerale(CasAvecDossier):
    def test_cas_sain_une_generation_tout_tenu(self):
        rapport = rg.executer(self.sous_dossier("sain"), generations=1, horodatage_fourni="essai")
        self.assertTrue(rapport["tout_tenu"], {k: v for k, v in rapport["verifications"].items() if not v["tenu"]})
        v = rapport["verifications"]
        self.assertEqual(v["4_relais"]["agents_lances"], v["4_relais"]["servis"])
        self.assertGreater(v["4_relais"]["agents_lances"], 0)
        self.assertEqual(v["5_garde_des_outils"]["refus"], 3 * v["4_relais"]["agents_lances"])
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "sain", "repetition-generale-v6.json.sha256")))

    def test_artefact_relais_au_plafond_nul(self):
        rapport = rg.executer(self.sous_dossier("plafond"), generations=1, horodatage_fourni="essai", plafond_relais=1e-9)
        self.assertFalse(rapport["tout_tenu"])
        v = rapport["verifications"]
        self.assertFalse(v["4_relais"]["tenu"])
        self.assertEqual(v["4_relais"]["servis"], 0)
        self.assertFalse(v["1_course_au_bout"]["tenu"], "des fiches restent indécises quand le relais refuse")


if __name__ == "__main__":
    unittest.main()
