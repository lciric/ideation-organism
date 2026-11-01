"""Essais de la version 0.7.0 : le nul étendu à l'archive (« go » de Lazar du 27 octobre, 15:27).

Artefact (R5) : la copie cachée — une fiche sans parents déclarés qui recopie une survivante mélangée à la loi uniforme —
est promue sans le nul d'archive et éliminée avec lui. Cas sain : une fiche vraiment nouvelle (un autre trait
informatif) reste promue avec le nul d'archive (le prix en puissance est mesuré : richesse avec et sans). Les témoins ne
reçoivent jamais les membres d'archive.
"""

import math
import os
import random
import unittest

from essais.aides import fiche
from essais.test_cycle import CasGeneration
from pole.cycle import Budget, ConfigGeneration, Generation, membres_de_l_archive
from pole.fiche import RegistreGel
from pole.memoire import Memoire
from pole.monde_banque import MondeBanque
from pole.outils import ecrire_json_scelle
from pole.simulation import AdaptateurSimule, MondeSimule


def banque_deux_effets(chemin, n=420, graine=9):
    """Trois traits ; l'issue suit 1,6·z0 + 1,6·z2 (deux effets indépendants) ; z1 est du bruit."""
    rng = random.Random(graine)
    instances = []
    for i in range(n):
        z = [round(rng.gauss(0, 1), 6) for _ in range(3)]
        p2 = 1 / (1 + math.exp(-(1.6 * z[0] + 1.6 * z[2])))
        issue = 2 if rng.random() < p2 else (0 if rng.random() < 0.6 else 1)
        instances.append({"identifiant": f"i{i:03d}", "z": z, "g": i % 2, "issues": {"A": issue},
                          "partie": "calibrage" if i % 3 == 0 else "epreuve"})
    ecrire_json_scelle(chemin, {"nom": "deux-effets", "traits": ["e0", "bruit", "e2"], "sous_populations": 2,
                                "moniteurs": {"A": {"nombre_issues": 3, "coupes": [0, 1], "instances": n}},
                                "instances": instances})


def loi(j, force=1.2, d=3, k=3):
    poids = [[0.0] * d for _ in range(k)]
    for c in range(k):
        poids[c][j] = force * (c - (k - 1) / 2)
    return {"type": "softmax", "poids": poids, "biais": [0.0] * k}


def fiche_a(identifiant, l, enonce, **modifs):
    return fiche(identifiant, enonce=enonce, loi_predictive=l, severite_attendue=0.05, seuil=20.0,
                 espace_instances={"nombre_issues": 3, "dimension": 3, "sous_populations": 2, "moniteur": "A"}, **modifs)


class NulArchive(CasGeneration):
    def _course(self, nul_archive, dossier):
        chemin = os.path.join(self.tmp, "banque.json")
        if not os.path.exists(chemin):
            banque_deux_effets(chemin)
        monde = MondeBanque(chemin, 7, nul_informe=False)
        adaptateur = AdaptateurSimule(graine=3, monde=MondeSimule(3))
        cfg = ConfigGeneration(selection="pari", taille_plan=120, taille_plan_filles=120, urne=False, part_calibrage=12,
                               nul_archive=nul_archive)
        memoire = Memoire(active=True, graine=0)
        registre = RegistreGel()
        s = fiche_a("S1", loi(0), "L'issue croît avec le trait e0")
        g0 = Generation(0, adaptateur, cfg, os.path.join(self.tmp, dossier), registre, Budget(10), memoire=memoire,
                        monde_noyau=monde)
        r0 = g0.executer([s])
        memoire.indexer(s, r0["issues"]["S1"], 0)
        self.assertEqual(s.statut, "survit", r0["issues"]["S1"].get("motif"))
        copie = fiche_a("C1", {"type": "melange", "composantes": [loi(0), {"type": "fixe", "probas": [1, 1, 1]}],
                               "poids": [0.7, 0.3]}, "Les notes hautes accompagnent un premier descripteur élevé")
        neuve = fiche_a("N1", loi(2), "L'issue croît avec le trait e2")
        temoin = fiche_a("TV", {"type": "melange", "composantes": [loi(0), {"type": "fixe", "probas": [1, 1, 1]}],
                                "poids": [0.7, 0.3]}, "Témoin vrai voisin de la survivante", temoin="vraie")
        g1 = Generation(1, adaptateur, cfg, os.path.join(self.tmp, dossier), registre, Budget(10), memoire=memoire,
                        monde_noyau=monde)
        r1 = g1.executer([copie, neuve, temoin])
        return g1, r1, copie, neuve, temoin

    def test_copie_cachee_eliminee_avec_le_nul_d_archive_et_promue_sans(self):
        _, r_sans, copie_sans, neuve_sans, _ = self._course(False, "sans")
        g, r_avec, copie_avec, neuve_avec, temoin = self._course(True, "avec")
        self.assertEqual(copie_sans.statut, "survit", "sans le nul d'archive, la copie cachée passe : le trou existe")
        self.assertEqual(copie_avec.statut, "eliminee", r_avec["issues"]["C1"].get("motif"))
        self.assertTrue(str(r_avec["issues"]["C1"]["pari"]["membre_dominant_final"]).startswith("archive"))
        self.assertEqual(neuve_avec.statut, "survit", "une fiche vraiment nouvelle reste promue")
        prix = r_sans["issues"]["N1"]["pari"]["log_richesse_max"] - r_avec["issues"]["N1"]["pari"]["log_richesse_max"]
        self.assertGreaterEqual(prix, -1e-9, "agrandir le nul ne peut qu'abaisser la richesse")
        noms_temoin = [m["nom"] for m in g.engagements["TV"].engagement["bibliotheque"]]
        self.assertFalse(any(n.startswith("archive") for n in noms_temoin), "jamais de membre d'archive pour un témoin")
        self.assertTrue(any(m["nom"] == "archive:S1" for m in g.engagements["C1"].engagement["bibliotheque"]))

    def test_membres_de_l_archive_filtrent_l_espace(self):
        memoire = Memoire(active=True, graine=0)
        s = fiche_a("S1", loi(0), "x")
        s.statut = "survit"
        memoire.index["S1"] = {"statut": "survit", "temoin": False, "loi_predictive": loi(0),
                               "espace_instances": s.espace_instances}
        memoire.index["S2"] = {"statut": "survit", "temoin": False, "loi_predictive": loi(0),
                               "espace_instances": dict(s.espace_instances, moniteur="B")}
        autre = fiche_a("F2", loi(2), "y")
        self.assertEqual([m["nom"] for m in membres_de_l_archive(autre, memoire)], ["archive:S1", "archive_couvert:S1"])
        self.assertEqual(membres_de_l_archive(s, memoire), [], "jamais elle-même")
        self.assertEqual(membres_de_l_archive(autre, Memoire(active=False)), [])


if __name__ == "__main__":
    unittest.main()
