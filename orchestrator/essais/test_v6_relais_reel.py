"""Essais de la version 0.6.0, pièce 2 : relais de clé réel, lancé dans un autre processus avec une **clé factice** dans
son seul environnement, devant un **amont factice** local qui vérifie la clé reçue. Aucune vraie clé, aucun réseau.

Cas sains : jeton factice remplacé par la clé, réponse JSON relayée, flux d'événements relayé morceau par morceau,
usage lu et converti en dollars, journal écrit sans la clé. Artefacts (R5) : autre jeton (401, amont jamais appelé),
chemin hors `/v1/` (404), plafond atteint (402), hôte non local refusé, variable de clé absente (code 2), amont
injoignable (502) ; la clé n'apparaît ni dans le journal ni sur la sortie du relais.
"""

import http.client
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest

from essais.aides import BASE
from essais.faux_sdk.amont_factice import CLE_FACTICE, AmontFactice
from pole.relais import JETON_FACTICE, RelaisInvalide
from pole.relais_reel import (BAREME_INCONNU, LecteurUsageFlux, cout_usd, lire_cle, tarif_du_modele,
                              usage_d_une_reponse_json, valider_hote)

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


MODELES_PERMIS_ESSAIS = "claude-opus-5-5,claude-fable-5-1"  # v47 (R-764, barrière 3) : liste vide = tout refusé


def lancer_relais(amont_url, plafond, journal, cle=CLE_FACTICE, variable="ANTHROPIC_API_KEY", reserve=0.001,
                  modeles_permis=MODELES_PERMIS_ESSAIS):
    env = {"PATH": os.environ.get("PATH", "")}
    if cle is not None:
        env[variable] = cle
    argv = [sys.executable, "-I", "-B", os.path.join(RACINE, "pole", "relais_reel.py"), "--port", "0",
            "--amont", amont_url, "--plafond-usd", str(plafond), "--journal", journal, "--reserve-par-appel", str(reserve)]
    if modeles_permis is not None:
        argv += ["--modeles-permis", modeles_permis]
    proc = subprocess.Popen(argv, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    ligne = proc.stdout.readline()
    if not ligne.startswith("relais prêt sur "):
        proc.kill()
        sortie, erreurs = proc.communicate(timeout=10)
        return proc, None, ligne + sortie + erreurs
    return proc, ligne.split()[3], ligne


def appeler(url, chemin, corps, jeton=JETON_FACTICE, methode="POST"):
    hote, port = url.replace("http://", "").split(":")
    connexion = http.client.HTTPConnection(hote, int(port), timeout=10)
    en_tetes = {"Content-Type": "application/json", "x-api-key": jeton}
    donnees = json.dumps(corps).encode() if corps is not None else None
    connexion.request(methode, chemin, body=donnees, headers=en_tetes)
    reponse = connexion.getresponse()
    octets = reponse.read()
    connexion.close()
    return reponse.status, dict(reponse.getheaders()), octets


class RelaisEnProcessus(unittest.TestCase):
    def setUp(self):
        os.makedirs(BASE, exist_ok=True)
        self.tmp = tempfile.mkdtemp(dir=BASE)
        self.amont = AmontFactice()
        self.journal = os.path.join(self.tmp, "journal-relais.jsonl")
        self.proc, self.url, self.premiere_ligne = lancer_relais(self.amont.url, 0.05, self.journal)
        self.assertIsNotNone(self.url, self.premiere_ligne)

    def tearDown(self):
        self.proc.kill()
        sortie, erreurs = self.proc.communicate(timeout=10)
        self.assertNotIn(CLE_FACTICE, self.premiere_ligne + sortie + erreurs, "la clé ne sort jamais du relais")
        self.amont.arreter()

    def _journal(self, au_moins=1):
        """Entrées du journal ; le relais l'écrit juste après avoir fini de répondre : on attend (au plus 3 s)."""
        limite = time.time() + 3.0
        while True:
            entrees = []
            if os.path.exists(self.journal):
                with open(self.journal, encoding="utf-8") as f:
                    entrees = [json.loads(ligne) for ligne in f if ligne.strip()]
            if len(entrees) >= au_moins or time.time() > limite:
                return entrees
            time.sleep(0.02)

    def test_cas_sain_json_cle_ajoutee_usage_compte_journal_sans_cle(self):
        statut, en_tetes, octets = appeler(self.url, "/v1/messages", {"model": "claude-opus-5-5", "messages": []})
        self.assertEqual(statut, 200, octets)
        self.assertEqual(json.loads(octets)["content"][0]["text"], "bonjour")
        self.assertEqual(self.amont.requetes[-1]["cle"], CLE_FACTICE, "l'amont a reçu la clé, pas le jeton factice")
        self.assertNotIn(CLE_FACTICE, json.dumps(dict(en_tetes)) + octets.decode())
        entrees = self._journal()
        self.assertEqual(entrees[-1]["statut"], 200)
        self.assertEqual(entrees[-1]["usage"], {"input_tokens": 1000, "output_tokens": 200})
        self.assertAlmostEqual(entrees[-1]["cout_usd"], (1000 * 4.0 + 200 * 20.0) / 1e6, places=9)
        with open(self.journal, encoding="utf-8") as f:
            self.assertNotIn(CLE_FACTICE, f.read())
        statut, _, octets = appeler(self.url, "/relais/etat", None, methode="GET")
        self.assertEqual(statut, 200)
        self.assertEqual(json.loads(octets)["appels"], 1)

    def test_cas_sain_flux_relaye_et_usage_lu(self):
        hote, port = self.url.replace("http://", "").split(":")
        connexion = http.client.HTTPConnection(hote, int(port), timeout=10)
        connexion.request("POST", "/v1/messages", body=json.dumps({"model": "claude-fable-5-1", "stream": True}).encode(),
                          headers={"Content-Type": "application/json", "x-api-key": JETON_FACTICE})
        reponse = connexion.getresponse()
        self.assertEqual(reponse.status, 200)
        self.assertIn("text/event-stream", reponse.getheader("Content-Type"))
        morceaux = []
        while True:
            morceau = reponse.read(64)
            if not morceau:
                break
            morceaux.append(morceau)
        connexion.close()
        texte = b"".join(morceaux).decode()
        self.assertIn("message_stop", texte)
        self.assertGreater(len(morceaux), 1, "relayé en plusieurs morceaux")
        derniere = self._journal()[-1]
        self.assertTrue(derniere["en_flux"])
        self.assertEqual(derniere["modele"], "claude-fable-5-1")
        self.assertEqual(derniere["usage"], {"input_tokens": 1000, "output_tokens": 200})
        self.assertAlmostEqual(derniere["cout_usd"], (1000 * 10.0 + 200 * 50.0) / 1e6, places=9)

    def test_artefact_autre_jeton_refuse_sans_appel_amont(self):
        statut, _, octets = appeler(self.url, "/v1/messages", {"model": "claude-opus-5-5"}, jeton="sk-ant-autre-chose")
        self.assertEqual(statut, 401, octets)
        self.assertEqual(self.amont.requetes, [])
        statut, _, _ = appeler(self.url, "/v1/messages", {"model": "claude-opus-5-5"}, jeton=CLE_FACTICE)
        self.assertEqual(statut, 401, "même la vraie clé présentée par un agent est refusée : seul le jeton factice passe")
        self.assertEqual(self.amont.requetes, [])

    def test_artefact_chemin_hors_v1_refuse(self):
        statut, _, _ = appeler(self.url, "/autre/chemin", {"model": "claude-opus-5-5"})
        self.assertEqual(statut, 404)
        self.assertEqual(self.amont.requetes, [])

    def test_artefact_plafond_atteint(self):
        # 0,05 USD de plafond ; un appel Fable à 1 000 / 200 jetons coûte 0,02 USD : le troisième est refusé
        for i in range(2):
            statut, _, _ = appeler(self.url, "/v1/messages", {"model": "claude-fable-5-1"})
            self.assertEqual(statut, 200)
            self._journal(au_moins=i + 1)  # v14 : attendre le règlement de l'appel avant le suivant (essai intermittent sous charge)
        statut, _, _ = appeler(self.url, "/v1/messages", {"model": "claude-fable-5-1"})
        self.assertEqual(statut, 200, "le plafond n'est pas encore atteint (0,04 < 0,05)")
        self._journal(au_moins=3)
        statut, _, octets = appeler(self.url, "/v1/messages", {"model": "claude-fable-5-1"})
        self.assertEqual(statut, 402, octets)
        self.assertEqual(len(self.amont.requetes), 3, "l'amont n'est plus appelé une fois le plafond atteint")
        self.assertEqual(self._journal(au_moins=4)[-1]["statut"], 402)


class ReserveParAppel(unittest.TestCase):
    def test_artefact_appels_simultanes_ne_franchissent_pas_le_plafond(self):
        """Quatre appels lancés en même temps, plafond 0,03 USD, réserve 0,02 : un seul peut partir (vu par la répétition
        générale avant correction : les quatre partaient)."""
        import threading
        os.makedirs(BASE, exist_ok=True)
        journal = os.path.join(tempfile.mkdtemp(dir=BASE), "j.jsonl")
        amont = AmontFactice()
        proc, url, sortie = lancer_relais(amont.url, 0.03, journal, reserve=0.02)
        self.assertIsNotNone(url, sortie)
        statuts = []
        try:
            def appel():
                statuts.append(appeler(url, "/v1/messages", {"model": "claude-fable-5-1"})[0])
            fils = [threading.Thread(target=appel) for _ in range(4)]
            for f in fils:
                f.start()
            for f in fils:
                f.join(timeout=15)
        finally:
            proc.kill()
            proc.communicate(timeout=10)
            amont.arreter()
        self.assertEqual(sorted(statuts), [200, 402, 402, 402])
        self.assertEqual(len(amont.requetes), 1)


class RelaisSansCleOuAmontInjoignable(unittest.TestCase):
    def test_artefact_variable_de_cle_absente(self):
        os.makedirs(BASE, exist_ok=True)
        journal = os.path.join(tempfile.mkdtemp(dir=BASE), "j.jsonl")
        proc, url, sortie = lancer_relais("http://127.0.0.1:1", 1.0, journal, cle=None)
        self.assertIsNone(url)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("aucune clé", sortie)

    def test_artefact_amont_injoignable(self):
        os.makedirs(BASE, exist_ok=True)
        journal = os.path.join(tempfile.mkdtemp(dir=BASE), "j.jsonl")
        proc, url, sortie = lancer_relais("http://127.0.0.1:1", 1.0, journal)
        self.assertIsNotNone(url, sortie)
        try:
            statut, _, octets = appeler(url, "/v1/messages", {"model": "claude-opus-5-5"})
            self.assertEqual(statut, 502, octets)
        finally:
            proc.kill()
            proc.communicate(timeout=10)


class FonctionsPures(unittest.TestCase):
    def test_tarifs_et_couts(self):
        self.assertEqual(tarif_du_modele("claude-opus-5-5-20260601"), (4.0, 20.0, 5.0, 0.20))
        self.assertEqual(tarif_du_modele("modele-inconnu"), BAREME_INCONNU)
        self.assertAlmostEqual(cout_usd("claude-haiku-5-5", {"input_tokens": 1_000_000, "output_tokens": 0}), 0.10)
        self.assertAlmostEqual(cout_usd("claude-sonnet-5-5", {"cache_read_input_tokens": 1_000_000}), 0.10)
        self.assertEqual(cout_usd("claude-opus-5-5", None), 0.0)
        self.assertGreaterEqual(cout_usd("inconnu", {"input_tokens": 1}), cout_usd("claude-opus-5-5", {"input_tokens": 1}),
                                "un modèle inconnu est compté au tarif le plus haut, jamais au plus bas")

    def test_lecture_usage(self):
        self.assertEqual(usage_d_une_reponse_json(b'{"model": "m", "usage": {"input_tokens": 3}}'), ("m", {"input_tokens": 3}))
        self.assertEqual(usage_d_une_reponse_json(b"pas du json"), (None, None))
        lecteur = LecteurUsageFlux()
        flux = (b'event: message_start\ndata: {"type": "message_start", "message": {"model": "m", "usage": '
                b'{"input_tokens": 10, "output_tokens": 1}}}\n\ndata: {"type": "message_del')
        lecteur.avaler(flux[:40])
        lecteur.avaler(flux[40:])
        lecteur.avaler(b'ta", "usage": {"output_tokens": 7}}\n\n')
        self.assertEqual((lecteur.modele, lecteur.usage), ("m", {"input_tokens": 10, "output_tokens": 7}))

    def test_hote_local_et_lecture_de_cle(self):
        self.assertEqual(valider_hote("127.0.0.1"), "127.0.0.1")
        with self.assertRaises(RelaisInvalide):
            valider_hote("0.0.0.0")
        environnement = {"ANTHROPIC_API_KEY": "x", "AUTRE": "y"}
        self.assertEqual(lire_cle(environnement, "ANTHROPIC_API_KEY"), "x")
        self.assertNotIn("ANTHROPIC_API_KEY", environnement, "effacée de l'environnement après lecture")
        with self.assertRaises(RelaisInvalide):
            lire_cle(environnement, "ANTHROPIC_API_KEY")


if __name__ == "__main__":
    unittest.main()
