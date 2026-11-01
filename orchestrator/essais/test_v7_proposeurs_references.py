"""Essais de la version 0.7.0, version 7 : proposeur enfichable, références gratuites, monde de la grammaire, partie de
développement distincte du calibrage.

Cas sains : les lois aléatoires passent la porte du gabarit ; le chercheur mécanique retrouve, sur la partie de
développement, les traits d'une structure plantée (interaction) ; la boucle tourne avec un proposeur de référence sans
appeler d'agent ; le monde de la grammaire sert une partie de développement distincte du calibrage. Artefacts (R5) : un
agent ne peut pas déclarer une stratégie de référence ; le proposeur mécanique sans phase exploratoire est refusé ; une
banque sans partie de développement le dit (`meme_partie_que_le_connu`).
"""

import json
import os
import sys
import unittest

from essais.test_cycle import CasGeneration
from pole import selection_pari as sp
from pole.cycle import ConfigGeneration
from pole.monde_banque import MondeBanque
from pole.outils import ecrire_json_scelle
from pole.pole import executer_pole
from pole.proposeur import PropositionRefusee, valider_proposition
from pole.proposeurs_references import propositions_aleatoires, propositions_mecaniques
from pole.simulation import AdaptateurSimule, MondeSimule

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "exemples"))
from generer_monde_grammaire_v1 import fiches_de_temoins, generer_monde  # noqa: E402


def _traits(loi, d=4):
    if loi["type"] == "softmax":
        return {t for t in range(d) if any(abs(l[t]) > 1e-9 for l in loi["poids"])}
    if loi["type"] == "par_sous_population":
        return set().union(*(_traits(l, d) for l in loi["lois"].values()))
    if loi["type"] == "si_sinon":
        return _traits(loi["si"], d) | _traits(loi["sinon"], d) | {loi["condition"].get("indice")}
    return set()


class MondeGrammaire(CasGeneration):
    def _monde(self, structures=None, graine=20261101):
        banque, temoins, verite = generer_monde(graine, structures=structures)
        chemin = os.path.join(self.tmp, f"banque-{graine}.json")
        ecrire_json_scelle(chemin, banque)
        return chemin, banque, temoins, verite

    def test_monde_parties_et_temoins(self):
        chemin, banque, temoins, verite = self._monde()
        parties = [l["partie"] for l in banque["instances"]]
        self.assertEqual((parties.count("calibrage"), parties.count("developpement"), parties.count("epreuve")), (150, 300, 450))
        for t in temoins:
            sp.valider_loi(t["loi"], 3, 4)
        dev = MondeBanque(chemin, 3).donnees_developpement()
        self.assertEqual(dev["partie"], "developpement")
        self.assertFalse(dev["meme_partie_que_le_connu"])
        self.assertEqual(len(dev["instances"]), 300)

    def test_banque_sans_developpement_le_dit(self):
        _, banque, _, _ = self._monde()
        for l in banque["instances"]:
            if l["partie"] == "developpement":
                l["partie"] = "epreuve"
        chemin = os.path.join(self.tmp, "sans-dev.json")
        ecrire_json_scelle(chemin, banque)
        dev = MondeBanque(chemin, 3).donnees_developpement()
        self.assertEqual(dev["partie"], "calibrage")
        self.assertTrue(dev["meme_partie_que_le_connu"])

    def test_aleatoire_passe_la_porte_et_reste_reserve_aux_references(self):
        chemin, *_ = self._monde()
        monde = MondeBanque(chemin, 3)
        props = propositions_aleatoires(monde.description_publique(), 8, 5, 1)
        self.assertEqual(len(props), 8)
        for i, p in enumerate(props, 1):
            fiche = valider_proposition(p, monde, 0.05, f"R{i}", "reference-aleatoire", references=True)
            self.assertTrue(fiche.source.startswith("proposeur:aleatoire_au_gabarit"))
        with self.assertRaises(PropositionRefusee):
            valider_proposition(props[0], monde, 0.05, "R9", "simule-e")
        self.assertEqual(props, propositions_aleatoires(monde.description_publique(), 8, 5, 1), "déterministe")

    def test_mecanique_retrouve_une_interaction_sur_le_developpement(self):
        chemin, _, _, verite = self._monde(structures=["interaction", "monotone", "sous_population"])
        monde = MondeBanque(chemin, 3)
        props = propositions_mecaniques(monde.description_publique(), monde.donnees_developpement(), 12)
        self.assertTrue(props)
        for p in props:
            valider_proposition(p, monde, 0.05, "M", "reference-mecanique", references=True)
        cible = verite["M0"]
        trouvees = [p for p in props if p["moniteur"] == "M0" and {cible["i"], cible["j"]} <= _traits(p["loi_predictive"])]
        self.assertTrue(trouvees, [(p["moniteur"], sorted(_traits(p["loi_predictive"]))) for p in props])

    def test_mecanique_sans_exploration_refuse(self):
        with self.assertRaises(ValueError):
            ConfigGeneration(selection="pari", proposeur="mecanique").valider()
        with self.assertRaises(ValueError):
            ConfigGeneration(selection="pari", proposeur="inconnu").valider()

    def test_boucle_avec_proposeur_de_reference_sans_agent(self):
        chemin, banque, temoins, _ = self._monde()
        monde = MondeBanque(chemin, 3, tranches=2)  # v11 : une tranche par génération (héritage de la preuve)
        population = [valider_proposition(p, monde, 0.05, f"P{i}", "reference-aleatoire", references=True)
                      for i, p in enumerate(propositions_aleatoires(monde.description_publique(), 4, 11, 0), 1)]
        adaptateur = AdaptateurSimule(graine=3, monde=MondeSimule(3))
        config = ConfigGeneration(selection="pari", taille_plan=120, taille_plan_filles=120, urne=False, part_calibrage=12,
                                  multiplicite="e-bh", temoins_sans_agent=True, propositions_par_generation=6,
                                  proposeur="aleatoire", budget_generation_usd=100.0).valider()
        racine = os.path.join(self.tmp, "course")
        bilan = executer_pole(population, fiches_de_temoins(temoins, 4, 3), adaptateur, config, 2, 500.0, racine,
                              monde_noyau=monde, temoins_par_generation=3)
        self.assertEqual(bilan["generations_executees"], 2, bilan["arret"])
        with open(os.path.join(racine, "journal", "generation-00.json"), encoding="utf-8") as f:
            prop = json.load(f)["proposeur"]
        self.assertEqual(prop["genre"], "aleatoire")
        self.assertEqual(prop["cout"], 0.0)
        self.assertGreater(prop["acceptees"], 0)
        self.assertNotIn("proposeur", {a["role"] for a in adaptateur.appels}, "aucun agent proposeur appelé")
        self.assertTrue(os.path.isfile(os.path.join(racine, "archive", "generations", "generation-00", "traces-proposeur",
                                                    "propositions-reference.json")))



class Mixte(unittest.TestCase):
    """v7, version 9 : vrais agents pour certains rôles seulement."""

    def test_routage_par_role_et_roles_invalides(self):
        from pole.adaptateurs import AdaptateurMixte

        class Enregistreur:
            def __init__(self, nom):
                self.nom, self.appels = nom, []

            def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
                self.appels.append(role)
                return self.nom

        reel, simule = Enregistreur("reel"), Enregistreur("simule")
        reel.bac_a_sable = {"actif": True}
        m = AdaptateurMixte(reel, simule, ["proposeur"])
        for role in ("experimentateur", "verificateur", "proposeur", "synthese", "recombinaison"):
            m.lancer(role, "c", "/tmp", 1.0, 3)
        self.assertEqual(reel.appels, ["proposeur"])
        self.assertEqual(simule.appels, ["experimentateur", "verificateur", "synthese", "recombinaison"])
        self.assertEqual(m.bac_a_sable, {"actif": True})
        for roles in ([], ["inconnu"], ["proposeur", "pirate"]):
            with self.subTest(roles=roles), self.assertRaises(ValueError):
                AdaptateurMixte(reel, simule, roles)

    def test_cout_simule_jamais_compte_dans_le_compte_reel(self):
        """v10 : un rôle simulé dans un adaptateur mixte déclare 0 USD au pôle ; son coût simulé est gardé à part."""
        from pole.adaptateurs import AdaptateurMixte, Resultat

        class Fixe:
            def __init__(self, cout):
                self.cout = cout

            def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
                return Resultat("fini", [], self.cout)

        reel, simule = Fixe(0.77), Fixe(0.40)
        m = AdaptateurMixte(reel, simule, ["proposeur"])
        r_sim = m.lancer("experimentateur", "c", "/tmp", 1.0, 3)
        self.assertEqual(r_sim.cout_declare_usd, 0.0)
        self.assertEqual(r_sim.cout_simule_usd, 0.40)
        r_reel = m.lancer("proposeur", "c", "/tmp", 1.0, 3)
        self.assertEqual(r_reel.cout_declare_usd, 0.77)
        self.assertEqual(r_reel.cout_simule_usd, 0.0)



class RepetitionDuel(CasGeneration):
    def test_seul_le_proposeur_passe_par_le_relais(self):
        """Chemin d'un duel payé (proposeur réel, autres rôles simulés), avec le faux moteur et le relais réel."""
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demonstrations"))
        import repetition_duel_v7
        rapport = repetition_duel_v7.executer(os.path.join(self.tmp, "repetition"), 3)
        self.assertTrue(rapport["tout_tenu"], {k: v for k, v in rapport["verifications"].items() if not v["tenu"]})


    def test_roles_reels_refuses_hors_monde_tenu_par_le_noyau(self):
        from pole.pole import principal
        from essais.aides import fiche_dict
        chemin = os.path.join(self.tmp, "population.json")
        ecrire_json_scelle(chemin, [fiche_dict("F1"), fiche_dict("F2", temoin="vraie"), fiche_dict("F3", temoin="fausse")])
        code = principal(["--population", chemin, "--temoins", chemin, "--sortie", os.path.join(self.tmp, "s"),
                          "--roles-reels", "proposeur"])
        self.assertEqual(code, 2, "sans moteur réel")
        code = principal(["--population", chemin, "--temoins", chemin, "--sortie", os.path.join(self.tmp, "s2"),
                          "--moteur", "claude-sdk", "--confirmer-moteur-reel", "--roles-reels", "proposeur",
                          "--url-relais", "http://127.0.0.1:9"])
        self.assertEqual(code, 2, "sans monde tenu par le noyau")


if __name__ == "__main__":
    unittest.main()
