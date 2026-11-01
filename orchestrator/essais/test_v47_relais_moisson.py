"""Essais de la version 47 : relais de moisson (`pole/relais_moisson.py`), lancé dans un autre processus devant un **amont
factice** local (Atom pour arXiv, JSON pour OpenAlex), comme `test_v6_relais_reel.py`. Aucun réseau : un garde-fou
d'essai refuse toute connexion hors de la boucle locale dans ce processus, et le relais refuse tout `--amont-factice`
hors de la boucle locale.

Cas sains : requête arXiv et OpenAlex relayées, réponse normalisée `{source, requete, n, horodatage, empreinte_brute,
resultats, empreinte}` (empreintes recalculées égales ; empreinte brute = SHA-256 des octets de l'amont), aucun en-tête
d'identité ni `mailto` sans courriel nommé (avec : les deux), journal sans clé, état. Artefacts (R5) : `/moisson/brave`
et toute autre route (404), méthode POST (404), paramètre en plus, `n` absent ou hors borne (400), jeton différent (401,
amont jamais appelé), gardes 1 à 3 refaites (retour à la ligne, adresse, forme de clé, 201 caractères, 26 mots : 400),
plafond par source et par jour (429), amont en panne, illisible ou injoignable (502), hôte non local et amont factice
non local refusés (code 2).
"""

import contextlib
import http.client
import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from essais.aides import BASE
from pole.moisson import JETON_MOISSON_FACTICE, empreinte_reponse
from pole.relais_moisson import lire_arxiv, lire_openalex, reconstruire_resume, url_amont, valider_amont_factice, valider_hote
from pole.relais import RelaisInvalide

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOTES_PERMIS = {"127.0.0.1", "::1", "localhost"}


@contextlib.contextmanager
def garde_fou_reseau():
    """Garde-fou d'essai : toute connexion sortante hors de la boucle locale est refusée dans ce processus."""
    original = socket.socket.connect

    def connecter(self, adresse):
        if isinstance(adresse, tuple) and adresse and adresse[0] not in HOTES_PERMIS:
            raise AssertionError(f"garde-fou d'essai : connexion hors boucle locale refusée ({adresse[0]!r})")
        return original(self, adresse)
    socket.socket.connect = connecter
    try:
        yield
    finally:
        socket.socket.connect = original


ATOM = ('<?xml version="1.0" encoding="UTF-8"?>\n<feed xmlns="http://www.w3.org/2005/Atom">\n'
        '<title>ArXiv Query</title>\n%s</feed>\n')
ENTREE = ('<entry>\n<id>http://arxiv.org/abs/%s</id>\n<published>2026-10-08T00:00:00Z</published>\n'
          '<title>%s</title>\n<summary>  %s\n</summary>\n%s</entry>\n')


class AmontMoissonFactice:
    """Amont factice : `/arxiv` (Atom) et `/openalex` (JSON à index inversé) ; consigne chaque requête ; `panne` :
    « 500 », « illisible »."""

    def __init__(self, panne=None):
        self.requetes, self.panne = [], panne
        amont = self

        class Gestionnaire(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *args):
                pass

            def _repondre(self, statut, octets, type_contenu):
                self.send_response(statut)
                self.send_header("Content-Type", type_contenu)
                self.send_header("Content-Length", str(len(octets)))
                self.end_headers()
                self.wfile.write(octets)

            def do_GET(self):
                p = urllib.parse.urlsplit(self.path)
                params = urllib.parse.parse_qs(p.query)
                amont.requetes.append({"chemin": p.path, "params": params, "en_tetes": {k.lower(): v for k, v in self.headers.items()}})
                if amont.panne == "500":
                    return self._repondre(500, b"panne", "text/plain")
                if amont.panne == "illisible":
                    return self._repondre(200, b"<<pas du xml ni du json", "text/plain")
                if p.path == "/arxiv":
                    n = int(params.get("max_results", ["5"])[0])
                    q = params.get("search_query", [""])[0]
                    entrees = "".join(ENTREE % (f"26{k:02d}.{10000 + k:05d}v1", f"Titre {k} pour {q}", f"Résumé {k} de la notice.",
                                                "<author><name>A. Un</name></author><author><name>B. Deux</name></author>\n")
                                      for k in range(1, n + 1))
                    octets = (ATOM % entrees).encode("utf-8")
                    amont.derniers_octets = octets
                    return self._repondre(200, octets, "application/atom+xml")
                if p.path == "/openalex":
                    n = int(params.get("per-page", ["5"])[0])
                    q = params.get("search", [""])[0]
                    resultats = [{"id": f"https://openalex.org/W{4000000000 + k}", "doi": f"https://doi.org/10.1/{k}",
                                  "title": f"Œuvre {k} pour {q}", "publication_date": "2026-05-10",
                                  "authorships": [{"author": {"display_name": "C. Trois"}}, {"author": {"display_name": "D. Quatre"}}],
                                  "abstract_inverted_index": {"Résumé": [0], "inversé": [1], "reconstruit": [2], "ici": [3]}}
                                 for k in range(1, n + 1)]
                    octets = json.dumps({"meta": {"count": n}, "results": resultats}).encode("utf-8")
                    amont.derniers_octets = octets
                    return self._repondre(200, octets, "application/json")
                return self._repondre(404, b"{}", "application/json")

        self.serveur = ThreadingHTTPServer(("127.0.0.1", 0), Gestionnaire)
        self.serveur.daemon_threads = True
        self.url = f"http://127.0.0.1:{self.serveur.server_address[1]}"
        self.fil = threading.Thread(target=self.serveur.serve_forever, daemon=True)
        self.fil.start()

    def arreter(self):
        self.serveur.shutdown()
        self.serveur.server_close()


def lancer_relais(amont_url, journal, plafond=200, courriel=None, hote="127.0.0.1", dossier_compteur=None):
    env = {"PATH": os.environ.get("PATH", "")}
    argv = [sys.executable, "-I", "-B", os.path.join(RACINE, "pole", "relais_moisson.py"), "--hote", hote, "--port", "0",
            "--amont-factice", amont_url, "--journal", journal, "--plafond-par-source-par-jour", str(plafond)]
    if courriel:
        argv += ["--courriel-politesse", courriel]
    if dossier_compteur:  # v49 (CL13-09)
        argv += ["--dossier-compteur", dossier_compteur]
    proc = subprocess.Popen(argv, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    ligne = proc.stdout.readline()
    if not ligne.startswith("relais de moisson prêt sur "):
        proc.kill()
        sortie, erreurs = proc.communicate(timeout=10)
        return proc, None, ligne + sortie + erreurs
    return proc, ligne.split()[5], ligne


def appeler(url, chemin, jeton=JETON_MOISSON_FACTICE, methode="GET"):
    p = urllib.parse.urlsplit(url)
    connexion = http.client.HTTPConnection(p.hostname, p.port, timeout=10)
    connexion.request(methode, chemin, headers={"x-jeton-moisson": jeton} if jeton is not None else {})
    reponse = connexion.getresponse()
    octets = reponse.read()
    connexion.close()
    return reponse.status, octets


def requete(source, q, n=5, **extra):
    return f"/moisson/{source}?" + urllib.parse.urlencode(dict({"q": q, "n": n}, **extra))


class TestRelaisMoisson(unittest.TestCase):
    def setUp(self):
        os.makedirs(BASE, exist_ok=True)
        self.tmp = tempfile.mkdtemp(dir=BASE)
        self.garde = garde_fou_reseau()
        self.garde.__enter__()
        self.amont = AmontMoissonFactice()
        self.journal = os.path.join(self.tmp, "journal-moisson.jsonl")
        self.proc, self.url, self.premiere = lancer_relais(self.amont.url, self.journal)
        self.assertIsNotNone(self.url, self.premiere)

    def tearDown(self):
        self.proc.kill()
        self.proc.communicate(timeout=10)
        self.amont.arreter()
        self.garde.__exit__(None, None, None)

    def _journal(self, au_moins=1):
        limite = time.time() + 3.0
        while True:
            entrees = []
            if os.path.exists(self.journal):
                with open(self.journal, encoding="utf-8") as f:
                    entrees = [json.loads(l) for l in f if l.strip()]
            if len(entrees) >= au_moins or time.time() > limite:
                return entrees

    def test_garde_fou_d_essai(self):
        """Le garde-fou refuse une connexion hors boucle locale (aucun paquet ne part : l'adresse est de documentation)."""
        s = socket.socket()
        try:
            with self.assertRaisesRegex(AssertionError, "hors boucle locale"):
                s.connect(("198.51.100.1", 80))
        finally:
            s.close()

    def test_cas_sain_arxiv(self):
        statut, octets = appeler(self.url, requete("arxiv", "monitor transfer diffuse sabotage", 3))
        self.assertEqual(statut, 200, octets)
        objet = json.loads(octets)
        self.assertEqual(sorted(objet), ["empreinte", "empreinte_brute", "horodatage", "n", "requete", "resultats", "source"])
        self.assertEqual((objet["source"], objet["requete"], objet["n"]), ("arxiv", "monitor transfer diffuse sabotage", 3))
        self.assertEqual(empreinte_reponse(objet), objet["empreinte"])
        import hashlib
        self.assertEqual(objet["empreinte_brute"], hashlib.sha256(self.amont.derniers_octets).hexdigest())
        self.assertEqual(len(objet["resultats"]), 3)
        r = objet["resultats"][0]
        self.assertEqual(r["identifiant"], "2601.10001v1")
        self.assertEqual(r["titre"], "Titre 1 pour all:monitor transfer diffuse sabotage")
        self.assertEqual(r["auteurs"], "A. Un, B. Deux")
        self.assertEqual((r["date"], r["resume"]), ("2026-10-08", "Résumé 1 de la notice."))
        self.assertEqual(r["lien"], "http://arxiv.org/abs/2601.10001v1")
        # amont : chemin /arxiv, paramètres de la forme arXiv (SUPPOSÉE), aucun en-tête d'identité
        q = self.amont.requetes[-1]
        self.assertEqual(q["chemin"], "/arxiv")
        self.assertEqual(q["params"], {"search_query": ["all:monitor transfer diffuse sabotage"], "start": ["0"], "max_results": ["3"]})
        self.assertNotIn("user-agent", q["en_tetes"])
        self.assertNotIn("mailto", json.dumps(q["params"]))
        # journal : sans clé, avec les empreintes
        entrees = self._journal()
        self.assertEqual((entrees[-1]["source"], entrees[-1]["statut"], entrees[-1]["resultats"], entrees[-1]["identite_envoyee"]),
                         ("arxiv", 200, 3, False))
        self.assertEqual(entrees[-1]["empreinte"], objet["empreinte"])
        statut, octets = appeler(self.url, "/moisson/etat")
        etat = json.loads(octets)
        self.assertEqual((statut, etat["appels"]["arxiv"], etat["courriel_politesse_defini"], etat["amont_factice"]), (200, 1, False, True))

    def test_cas_sain_openalex_et_courriel_de_politesse(self):
        statut, octets = appeler(self.url, requete("openalex", "quickest change detection", 2))
        self.assertEqual(statut, 200, octets)
        objet = json.loads(octets)
        self.assertEqual(empreinte_reponse(objet), objet["empreinte"])
        r = objet["resultats"][0]
        self.assertEqual((r["identifiant"], r["auteurs"], r["date"]), ("W4000000001", "C. Trois, D. Quatre", "2026-05-10"))
        self.assertEqual(r["resume"], "Résumé inversé reconstruit ici")
        self.assertEqual(r["lien"], "https://openalex.org/W4000000001")
        q = self.amont.requetes[-1]
        self.assertEqual(q["chemin"], "/openalex")
        self.assertNotIn("mailto", q["params"])
        self.assertNotIn("user-agent", q["en_tetes"])
        # avec un courriel nommé (jamais ici par Lazar : factice) : mailto et User-Agent envoyés
        journal2 = os.path.join(self.tmp, "journal-2.jsonl")
        proc2, url2, ligne2 = lancer_relais(self.amont.url, journal2, courriel="politesse@exemple.invalid")
        try:
            self.assertIsNotNone(url2, ligne2)
            statut, octets = appeler(url2, requete("openalex", "quickest change detection", 1))
            self.assertEqual(statut, 200, octets)
            q = self.amont.requetes[-1]
            self.assertEqual(q["params"]["mailto"], ["politesse@exemple.invalid"])
            self.assertIn("mailto:politesse@exemple.invalid", q["en_tetes"]["user-agent"])
            statut, octets = appeler(url2, "/moisson/etat")
            self.assertTrue(json.loads(octets)["courriel_politesse_defini"])
        finally:
            proc2.kill()
            proc2.communicate(timeout=10)

    def test_artefacts_routes_parametres_jeton_et_gardes(self):
        avant = len(self.amont.requetes)
        cas = [("/moisson/brave?q=monitor+diffus&n=5", 404), ("/moisson/semantic-scholar?q=monitor&n=5", 404),
               ("/autre", 404), ("/v1/messages", 404), ("/moisson/arxiv?q=monitor+diffus&n=5&x=1", 400),
               ("/moisson/arxiv?q=monitor+diffus", 400), ("/moisson/arxiv?q=monitor+diffus&n=9", 400),
               ("/moisson/arxiv?q=monitor+diffus&n=0", 400), ("/moisson/arxiv?q=monitor+diffus&n=5&n=3", 400),
               (requete("arxiv", "monitor\ndiffus"), 400), (requete("arxiv", "voir https://exemple.org"), 400),
               (requete("arxiv", "clé " + "sk-" + "ant-" + "abcdefghijklmnop"), 400), (requete("arxiv", "x" * 201), 400),
               (requete("arxiv", " ".join(["mot"] * 26)), 400), (requete("arxiv", "ab"), 400),
               (requete("arxiv", "jeton " + JETON_MOISSON_FACTICE), 400), (requete("arxiv", "a@b"), 400)]
        for chemin, attendu in cas:
            statut, octets = appeler(self.url, chemin)
            self.assertEqual(statut, attendu, (chemin, octets))
        statut, _ = appeler(self.url, requete("arxiv", "monitor diffus"), jeton="autre")
        self.assertEqual(statut, 401)
        statut, _ = appeler(self.url, requete("arxiv", "monitor diffus"), jeton=None)
        self.assertEqual(statut, 401)
        statut, _ = appeler(self.url, requete("arxiv", "monitor diffus"), methode="POST")
        self.assertEqual(statut, 404)
        self.assertEqual(len(self.amont.requetes), avant, "aucun artefact n'atteint l'amont")
        entrees = self._journal(au_moins=len(cas))
        self.assertTrue(any(e.get("statut") == 404 for e in entrees))
        self.assertTrue(any(e.get("statut") == 401 for e in entrees))
        self.assertTrue(any("règle 2" in (e.get("motif") or "") for e in entrees))
        self.assertTrue(any("règle 3" in (e.get("motif") or "") for e in entrees))
        self.assertTrue(any("règle 1" in (e.get("motif") or "") for e in entrees))

    def test_plafond_par_source_et_par_jour(self):
        journal = os.path.join(self.tmp, "journal-plafond.jsonl")
        proc, url, ligne = lancer_relais(self.amont.url, journal, plafond=2)
        try:
            self.assertIsNotNone(url, ligne)
            statuts = [appeler(url, requete("arxiv", f"monitor diffus {k}", 1))[0] for k in range(3)]
            self.assertEqual(statuts, [200, 200, 429])
            self.assertEqual(appeler(url, requete("openalex", "monitor diffus", 1))[0], 200)  # plafond par source
            statut, octets = appeler(url, "/moisson/etat")
            etat = json.loads(octets)
            self.assertEqual((etat["appels"]["arxiv"], etat["refus"]["arxiv"], etat["appels"]["openalex"]), (2, 1, 1))
        finally:
            proc.kill()
            proc.communicate(timeout=10)

    def test_amont_en_panne_illisible_injoignable(self):
        for panne, motif in (("500", "statut 500"), ("illisible", "illisible")):
            amont = AmontMoissonFactice(panne=panne)
            journal = os.path.join(self.tmp, f"journal-{panne}.jsonl")
            proc, url, ligne = lancer_relais(amont.url, journal)
            try:
                self.assertIsNotNone(url, ligne)
                statut, octets = appeler(url, requete("arxiv", "monitor diffus", 1))
                self.assertEqual(statut, 502, octets)
                self.assertIn(motif, json.loads(octets)["erreur"])
            finally:
                proc.kill()
                proc.communicate(timeout=10)
                amont.arreter()
        amont = AmontMoissonFactice()
        url_amont = amont.url
        amont.arreter()  # injoignable
        journal = os.path.join(self.tmp, "journal-injoignable.jsonl")
        proc, url, ligne = lancer_relais(url_amont, journal)
        try:
            self.assertIsNotNone(url, ligne)
            statut, octets = appeler(url, requete("openalex", "monitor diffus", 1))
            self.assertEqual(statut, 502, octets)
            self.assertIn("injoignable", json.loads(octets)["erreur"])
        finally:
            proc.kill()
            proc.communicate(timeout=10)

    def test_hote_et_amont_factice_non_locaux_refuses(self):
        for argv_sup in (["--hote", "0.0.0.0"], ["--amont-factice", "http://exemple.invalid"], ["--amont-factice", "https://127.0.0.1:1"]):
            argv = [sys.executable, "-I", "-B", os.path.join(RACINE, "pole", "relais_moisson.py"), "--port", "0"]
            if argv_sup[0] != "--amont-factice":
                argv += ["--amont-factice", self.amont.url]
            r = subprocess.run(argv + argv_sup, env={"PATH": os.environ.get("PATH", "")}, capture_output=True, text=True, timeout=30)
            self.assertEqual(r.returncode, 2, (argv_sup, r.stdout, r.stderr))
            self.assertIn("erreur", r.stderr)
        with self.assertRaises(RelaisInvalide):
            valider_hote("10.0.0.1")
        with self.assertRaises(RelaisInvalide):
            valider_amont_factice("http://exemple.invalid/x")
        self.assertEqual(valider_amont_factice("http://127.0.0.1:9/"), "http://127.0.0.1:9")


class TestLecteursAmont(unittest.TestCase):
    """Lecteurs des amonts (formats SUPPOSÉS) et adresses interrogées."""

    def test_url_amont(self):
        self.assertEqual(url_amont("arxiv", "a b", 3), "https://export.arxiv.org/api/query?search_query=all%3Aa+b&start=0&max_results=3")  # v49 (CL13-09) : https
        u = url_amont("openalex", "a b", 2)
        self.assertTrue(u.startswith("https://api.openalex.org/works?search=a+b&per-page=2&select="))
        self.assertNotIn("mailto", u)
        self.assertIn("mailto=x%40y.invalid", url_amont("openalex", "a", 1, courriel="x@y.invalid"))
        self.assertEqual(url_amont("arxiv", "a", 1, amont_factice="http://127.0.0.1:9"),
                         "http://127.0.0.1:9/arxiv?search_query=all%3Aa&start=0&max_results=1")

    def test_lecteurs(self):
        atom = (ATOM % (ENTREE % ("2610.12445v1", "Caught in the Act", "Un résumé.", "<author><name>O. H.</name></author>"))).encode("utf-8")
        r = lire_arxiv(atom)
        self.assertEqual(r[0]["identifiant"], "2610.12445v1")
        self.assertEqual(r[0]["titre"], "Caught in the Act")
        self.assertEqual(reconstruire_resume({"b": [1], "a": [0]}), "a b")
        self.assertEqual(reconstruire_resume(None), "")
        self.assertEqual(lire_openalex(b'{"results": [{"id": "https://openalex.org/W1", "title": "T"}]}')[0]["identifiant"], "W1")
        self.assertEqual(lire_openalex(b'{"results": []}'), [])


if __name__ == "__main__":
    unittest.main()
