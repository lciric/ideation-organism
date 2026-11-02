"""Essais de la v60 — réserve par empreinte des données tenues à l'écart (`pole/reserve_tenue_a_l_ecart_v60.py`) et sa ligne
de commande (`demonstrations/reserve_tenue_a_l_ecart_v60.py`). Tâche A3 du tour fermé ; préenregistrement
`prereg/preenregistrement-tour-ferme-v1-brouillon1.md`, sections 5.2 et 7 (garde 11).

Hors ligne : aucun réseau, aucun modèle, aucune donnée réelle (épisodes synthétiques). Chaque garde : un cas sain et un
artefact (R5)."""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)

from pole import reserve_tenue_a_l_ecart_v60 as R  # noqa: E402
from pole.outils import ecrire_json_scelle, sha256_fichier  # noqa: E402


def episodes_synthetiques(taches=30, par_tache=3):
    return {"instances": [{"identifiant": f"t{t:03d}/e{e}", "tache": f"tache-{t:03d}", "z": [0.1 * t, -0.2 * e], "g": e % 2,
                           "issues": {"3B:RIGOR": (t + e) % 3, **({"8B:NOVELTY": e % 2} if t % 2 else {})}}
                          for t in range(taches) for e in range(par_tache)]}


class Base(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="essai-v60-reserve-")
        self.addCleanup(shutil.rmtree, self.d, True)
        self.entree = os.path.join(self.d, "episodes.json")
        with open(self.entree, "w", encoding="utf-8") as f:
            json.dump(episodes_synthetiques(), f)

    def reserver(self, nom="sortie", **kw):
        return R.reserver(self.entree, os.path.join(self.d, nom), **kw)


class Regle(Base):
    def test_regle_explicite_et_deterministe(self):
        for t in ("tache-000", "2506.01290v2", "x"):
            attendu = int(hashlib.sha256(("tour-ferme-v1|tenue-a-l-ecart|" + t).encode()).hexdigest(), 16) % 3 == 0
            self.assertEqual(R.tache_reservee(t), attendu)
        with self.assertRaises(R.ReserveRefusee):
            R.tache_reservee("")

    def test_reserve_saine_par_taches_entieres(self):
        r = self.reserver()
        s = os.path.join(self.d, "sortie")
        m = R.verifier_reserve(s, r["manifeste_sha256"])
        with open(os.path.join(s, R.NOM_T), encoding="utf-8") as f:
            t = json.load(f)["episodes"]
        with open(os.path.join(s, R.NOM_RESTE), encoding="utf-8") as f:
            reste = json.load(f)["episodes"]
        self.assertTrue(t and reste)
        self.assertTrue(all(R.tache_reservee(e["tache"]) for e in t))
        self.assertFalse(any(R.tache_reservee(e["tache"]) for e in reste))
        self.assertFalse({e["tache"] for e in t} & {e["tache"] for e in reste})
        self.assertEqual(len(t) + len(reste), 90)
        self.assertEqual(m["comptes"]["entree"]["episodes"], 90)
        self.assertEqual(m["entree_sha256"], sha256_fichier(self.entree))
        self.assertEqual(m["comptes"]["tenue_a_l_ecart"]["episodes"] % 3, 0)  # trois épisodes par tâche, tâches entières

    def test_ordre_de_l_entree_sans_effet(self):
        r1 = self.reserver("s1")
        objet = episodes_synthetiques()
        objet["instances"].reverse()
        with open(self.entree, "w", encoding="utf-8") as f:
            json.dump(objet, f)
        r2 = self.reserver("s2")
        self.assertEqual(r1["fichiers"][R.NOM_TACHES], r2["fichiers"][R.NOM_TACHES])
        self.assertNotEqual(r1["entree_sha256"], r2["entree_sha256"])


class GardesEntree(Base):
    def test_sortie_existante_refusee(self):
        os.makedirs(os.path.join(self.d, "sortie"))
        with self.assertRaises(R.ReserveRefusee):
            self.reserver()

    def test_lien_symbolique_refuse(self):
        lien = os.path.join(self.d, "lien.json")
        os.symlink(self.entree, lien)
        with self.assertRaises(R.ReserveRefusee):
            R.reserver(lien, os.path.join(self.d, "sortie"))
        self.reserver()  # cas sain : le fichier régulier passe

    def test_identifiant_en_double_refuse(self):
        objet = episodes_synthetiques()
        objet["instances"][5]["identifiant"] = objet["instances"][4]["identifiant"]
        with open(self.entree, "w", encoding="utf-8") as f:
            json.dump(objet, f)
        with self.assertRaises(R.ReserveRefusee):
            self.reserver()
        self.assertFalse(os.path.exists(os.path.join(self.d, "sortie")))

    def test_tache_absente_refusee(self):
        objet = episodes_synthetiques()
        del objet["instances"][7]["tache"]
        with open(self.entree, "w", encoding="utf-8") as f:
            json.dump(objet, f)
        with self.assertRaises(R.ReserveRefusee):
            self.reserver()

    def test_reserve_degeneree_refusee(self):
        objet = {"instances": [{"identifiant": "a", "tache": "seule"}, {"identifiant": "b", "tache": "seule"}]}
        with open(self.entree, "w", encoding="utf-8") as f:
            json.dump(objet, f)
        with self.assertRaises(R.ReserveRefusee):
            self.reserver()

    def test_liste_nue_et_cles_injectees(self):
        objet = [{"id": f"e{k}", "task": f"t{k // 2}"} for k in range(60)]
        with open(self.entree, "w", encoding="utf-8") as f:
            json.dump(objet, f)
        r = self.reserver(cle_tache="task", cle_identifiant="id")
        R.verifier_reserve(os.path.join(self.d, "sortie"), r["manifeste_sha256"])


class Verification(Base):
    def test_donnees_alterees_avec_sceau_juste_refusees(self):
        r = self.reserver()
        s = os.path.join(self.d, "sortie")
        chemin = os.path.join(s, R.NOM_T)
        with open(chemin, encoding="utf-8") as f:
            t = json.load(f)
        t["episodes"][0]["issues"] = {"3B:RIGOR": 2}
        os.remove(chemin)
        os.remove(chemin + ".sha256")
        ecrire_json_scelle(chemin, t)  # sceau compagnon juste, empreinte ≠ manifeste
        with self.assertRaises(R.ReserveRefusee):
            R.verifier_reserve(s, r["manifeste_sha256"])

    def test_tache_reservee_deplacee_au_reste_refusee(self):
        r = self.reserver()
        s = os.path.join(self.d, "sortie")
        with open(os.path.join(s, R.NOM_T), encoding="utf-8") as f:
            t = json.load(f)
        with open(os.path.join(s, R.NOM_RESTE), encoding="utf-8") as f:
            reste = json.load(f)
        with open(os.path.join(s, R.NOM_MANIFESTE), encoding="utf-8") as f:
            m = json.load(f)
        reste["episodes"].append(t["episodes"].pop())  # artefact rendu cohérent : fichiers et manifeste rescellés
        for nom, obj in ((R.NOM_T, t), (R.NOM_RESTE, reste)):
            os.remove(os.path.join(s, nom))
            os.remove(os.path.join(s, nom) + ".sha256")
            m["fichiers"][nom] = ecrire_json_scelle(os.path.join(s, nom), obj)
        os.remove(os.path.join(s, R.NOM_MANIFESTE))
        os.remove(os.path.join(s, R.NOM_MANIFESTE) + ".sha256")
        sha_m = ecrire_json_scelle(os.path.join(s, R.NOM_MANIFESTE), m)
        with self.assertRaises(R.ReserveRefusee) as c:
            R.verifier_reserve(s, sha_m)
        self.assertIn("reste appartient à une tâche réservée", str(c.exception))
        with self.assertRaises(R.ReserveRefusee):
            R.verifier_reserve(s, r["manifeste_sha256"])  # l'empreinte du préenregistrement ne concorde plus

    def test_liste_des_taches_incoherente_refusee(self):
        self.reserver()
        s = os.path.join(self.d, "sortie")
        with open(os.path.join(s, R.NOM_TACHES), encoding="utf-8") as f:
            taches = json.load(f)
        with open(os.path.join(s, R.NOM_MANIFESTE), encoding="utf-8") as f:
            m = json.load(f)
        taches["taches"] = taches["taches"][1:]  # artefact rendu cohérent : fichier et manifeste rescellés
        for nom, obj in ((R.NOM_TACHES, taches),):
            os.remove(os.path.join(s, nom))
            os.remove(os.path.join(s, nom) + ".sha256")
            m["fichiers"][nom] = ecrire_json_scelle(os.path.join(s, nom), obj)
        os.remove(os.path.join(s, R.NOM_MANIFESTE))
        os.remove(os.path.join(s, R.NOM_MANIFESTE) + ".sha256")
        sha_m = ecrire_json_scelle(os.path.join(s, R.NOM_MANIFESTE), m)
        with self.assertRaises(R.ReserveRefusee) as c:
            R.verifier_reserve(s, sha_m)
        self.assertIn("liste des tâches réservées incohérente", str(c.exception))

    def test_empreinte_du_manifeste_differente_refusee(self):
        r = self.reserver()
        with self.assertRaises(R.ReserveRefusee):
            R.verifier_reserve(os.path.join(self.d, "sortie"), "0" * 64)
        R.verifier_reserve(os.path.join(self.d, "sortie"), r["manifeste_sha256"])

    def test_taches_reservees_dans_un_contexte(self):
        self.reserver()
        with open(os.path.join(self.d, "sortie", R.NOM_TACHES), encoding="utf-8") as f:
            taches = json.load(f)["taches"]
        self.assertEqual(R.taches_reservees_dans("contexte sans tâche réservée", taches), [])
        self.assertEqual(R.taches_reservees_dans(f"… épisode de {taches[0]} …", taches), [taches[0]])


class LigneDeCommande(Base):
    def test_sortie_sans_contenu_et_codes(self):
        cmd = [sys.executable, "-I", "-B", os.path.join(RACINE, "demonstrations", "reserve_tenue_a_l_ecart_v60.py")]
        p = subprocess.run(cmd + [self.entree, os.path.join(self.d, "sortie")], capture_output=True, text=True, timeout=60)
        self.assertEqual(p.returncode, 0, p.stderr)
        r = json.loads(p.stdout)
        self.assertEqual(len(r["manifeste_sha256"]), 64)
        self.assertNotIn("t000/e0", p.stdout)  # aucun identifiant d'épisode imprimé
        self.assertNotIn("issues\":", p.stdout.replace("episodes_par_moniteur", ""))
        p2 = subprocess.run(cmd + [self.entree, os.path.join(self.d, "sortie")], capture_output=True, text=True, timeout=60)
        self.assertEqual(p2.returncode, 2)  # sortie existante : refus
        self.assertIn("arret", p2.stderr)


if __name__ == "__main__":
    unittest.main()
