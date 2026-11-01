"""Relais de moisson (v47, option (A) : arXiv et OpenAlex, métadonnées et résumés seulement) : un petit serveur local
tenu par le noyau, **séparé du relais de clé Anthropic** (`relais_reel.py`, dont le périmètre `CHEMINS_PERMIS =
("/v1/messages",)` a été fixé par les contre-lectures C10 et F-C7 : aucune route n'y est ajoutée).

Il tourne dans **son propre processus** (`python -I -m pole.relais_moisson …`), n'écoute que sur la boucle locale, exige le
jeton factice propre de la moisson (`x-jeton-moisson`), ne sert que `GET /moisson/arxiv?q=&n=`, `GET /moisson/openalex?q=&n=`
et `GET /moisson/etat` ; toute autre route rend 404 (dont `/moisson/brave`) ; tout paramètre hors `q` et `n` est refusé ;
les gardes 1 à 3 de la garde de fuite sont refaites ici ; un **plafond de requêtes par source et par jour**, indépendant
de l'orchestrateur, est tenu. La réponse est normalisée : `{source, requete, n, horodatage, empreinte_brute, resultats,
empreinte}` (SHA-256 des octets de l'amont, puis du JSON normalisé canonique). Journal JSON par ligne, sans clé.

v49 (CL13-09) : le plafond « par jour » est **persistant** (`--dossier-compteur`, un fichier scellé par jour UTC,
`compteur-AAAA-MM-JJ.json` et son `.sha256`, réécrit à chaque requête réservée ou refusée) : relancer le relais le même jour ne
remet plus le compteur à zéro ; un fichier dont le sceau est faux, ou illisible, **empêche le démarrage** (aucun repli).
Sans amont factice (amont réel), `--dossier-compteur` est obligatoire ; arXiv est interrogé en https.

Aucune clé en option (A). Le **courriel de politesse** d'OpenAlex est une option (`--courriel-politesse`), vide par
défaut : tant que Lazar n'en a pas nommé un, le relais n'envoie **aucun en-tête d'identité** (ni `User-Agent`, ni `mailto`).

Les adresses d'amont sont codées par source (`AMONTS`, formats et conditions d'accès **SUPPOSÉS**, à relire au
branchement par session-depot) mais **remplaçables par `--amont-factice URL`** pour les essais : une adresse de la boucle
locale seulement, qui sert `/arxiv` et `/openalex` avec les mêmes paramètres. Ce dépôt n'appelle jamais un amont réel :
ses essais (`essais/test_v47_relais_moisson.py`) lancent ce relais devant un amont factice local.
"""

if __name__ == "__main__" and not __package__:  # `python -I pole/relais_moisson.py …` : le paquet n'est pas sur le chemin
    import os as _os
    import runpy as _runpy
    import sys as _sys
    _ICI = _os.path.dirname(_os.path.abspath(__file__))
    _sys.path[:] = [p for p in _sys.path if _os.path.abspath(p or _os.curdir) != _ICI]
    _sys.path.insert(0, _os.path.dirname(_ICI))
    _runpy.run_module("pole.relais_moisson", run_name="__main__", alter_sys=True)
    raise SystemExit(0)

import argparse
import datetime
import hashlib
import http.client
import json
import os
import re
import sys
import threading
import time
import urllib.parse
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .moisson import JETON_MOISSON_FACTICE, MAX_RESULTATS_PAR_REQUETE, SOURCES, GardeFuite, construire_reponse
from .relais import HOTES_LOCAUX, RelaisInvalide

# Adresses des amonts (SUPPOSÉES, de mémoire ; à relire au branchement) : arXiv, interface Atom ; OpenAlex, JSON.
# v49 (CL13-09) : arXiv en https (la v47 l'interrogeait en clair : requêtes lisibles et modifiables en route)
AMONTS = {"arxiv": "https://export.arxiv.org/api/query", "openalex": "https://api.openalex.org/works"}
PLAFOND_PAR_SOURCE_PAR_JOUR_DEFAUT = 200  # SUPPOSÉ ; ≈ 12 requêtes par course (note § 6)
DELAI_AMONT_S = 30
TAILLE_MAX_AMONT = 5_000_000
CHEMINS = {f"/moisson/{s}" for s in SOURCES}
CHEMIN_ETAT = "/moisson/etat"
ATOM = "{http://www.w3.org/2005/Atom}"
VERSION = "0.1"


def valider_hote(hote):
    if hote not in HOTES_LOCAUX:
        raise RelaisInvalide(f"le relais de moisson n'écoute que sur la boucle locale, reçu {hote!r}")
    return hote


def valider_amont_factice(url):
    """`--amont-factice` : http sur la boucle locale seulement (les essais ne quittent jamais la machine)."""
    p = urllib.parse.urlsplit(url)
    if p.scheme != "http" or p.hostname not in HOTES_LOCAUX or p.query or p.fragment:
        raise RelaisInvalide(f"--amont-factice : adresse http de la boucle locale attendue, reçu {url!r}")
    return url.rstrip("/")


def url_amont(source, requete, n, amont_factice=None, courriel=None):
    """L'adresse interrogée pour une source (formats SUPPOSÉS)."""
    if amont_factice:
        base = amont_factice + "/" + source
    else:
        base = AMONTS[source]
    if source == "arxiv":
        params = {"search_query": "all:" + requete, "start": 0, "max_results": int(n)}
    else:
        params = {"search": requete, "per-page": int(n),
                  "select": "id,doi,title,authorships,publication_date,abstract_inverted_index"}
        if courriel:
            params["mailto"] = courriel
    return base + "?" + urllib.parse.urlencode(params)


def lire_arxiv(octets):
    """Flux Atom d'arXiv → résultats normalisés (identifiant sans le préfixe d'adresse, titre, auteurs, date, résumé, lien
    de la notice)."""
    racine = ET.fromstring(octets)
    resultats = []
    for e in racine.findall(ATOM + "entry"):
        ident = (e.findtext(ATOM + "id") or "").strip()
        identifiant = ident.rsplit("/abs/", 1)[-1] if "/abs/" in ident else ident.rsplit("/", 1)[-1]
        auteurs = ", ".join((a.findtext(ATOM + "name") or "").strip() for a in e.findall(ATOM + "author"))
        resultats.append({"identifiant": identifiant, "titre": e.findtext(ATOM + "title") or "", "auteurs": auteurs,
                          "date": (e.findtext(ATOM + "published") or "")[:10], "resume": e.findtext(ATOM + "summary") or "",
                          "lien": ident})
    return resultats


def reconstruire_resume(index_inverse):
    """OpenAlex sert le résumé en index inversé {mot: [positions]} (SUPPOSÉ) : reconstruit dans l'ordre des positions."""
    if not isinstance(index_inverse, dict):
        return ""
    positions = []
    for mot, pos in index_inverse.items():
        if isinstance(pos, list):
            positions += [(p, mot) for p in pos if isinstance(p, int)]
    return " ".join(m for _, m in sorted(positions))


def lire_openalex(octets):
    objet = json.loads(octets.decode("utf-8"))
    resultats = []
    for w in (objet.get("results") or []) if isinstance(objet, dict) else []:
        if not isinstance(w, dict):
            continue
        ident = str(w.get("id") or "")
        identifiant = ident.rsplit("/", 1)[-1]
        auteurs = ", ".join(str(((a or {}).get("author") or {}).get("display_name") or "") for a in (w.get("authorships") or [])
                            if isinstance(a, dict))
        resultats.append({"identifiant": identifiant, "titre": str(w.get("title") or ""), "auteurs": auteurs,
                          "date": str(w.get("publication_date") or "")[:10],
                          "resume": reconstruire_resume(w.get("abstract_inverted_index")), "lien": ident})
    return resultats


LECTEURS = {"arxiv": lire_arxiv, "openalex": lire_openalex}


class CompteurInvalide(RelaisInvalide):
    """Le fichier du compteur journalier est illisible ou son sceau est faux : le relais ne démarre pas (aucun repli)."""


class CompteurJournalier:
    """Plafond de requêtes par source et par jour (UTC), indépendant de l'orchestrateur. v49 (CL13-09) : avec `dossier`, le
    compteur du jour est **persistant** — `compteur-AAAA-MM-JJ.json` et son `.sha256` (format de sha256sum), écrits de façon
    atomique (fichier provisoire puis renommage) à chaque changement ; relancé le même jour, le relais relit le fichier
    (sceau vérifié ; sceau faux ou fichier illisible : `CompteurInvalide`, le relais ne démarre pas). Sans `dossier` (essais,
    amont factice), le compteur reste en mémoire seulement."""

    def __init__(self, plafond, dossier=None):
        self.plafond = int(plafond)
        self.dossier = dossier
        self.jour, self.appels, self.refus = None, {s: 0 for s in SOURCES}, {s: 0 for s in SOURCES}
        self._verrou = threading.Lock()
        if dossier is not None:
            os.makedirs(dossier, exist_ok=True)
            with self._verrou:
                self._aujourd_hui()

    @staticmethod
    def _maintenant_jour():
        return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

    def _chemin(self, jour):
        return os.path.join(self.dossier, f"compteur-{jour}.json")

    def _charger(self, jour):
        """Le compteur du jour sur disque, ou None s'il n'existe pas ; `CompteurInvalide` si le sceau ou le contenu est faux."""
        chemin = self._chemin(jour)
        if not os.path.exists(chemin) and not os.path.exists(chemin + ".sha256"):
            return None
        try:
            with open(chemin, "rb") as f:
                octets = f.read()
            with open(chemin + ".sha256", encoding="utf-8") as f:
                attendue = f.read().split()[0]
            if hashlib.sha256(octets).hexdigest() != attendue:
                raise CompteurInvalide(f"compteur journalier {chemin} : sceau faux (le fichier a été modifié) : le relais ne démarre pas")
            objet = json.loads(octets.decode("utf-8"))
            appels, refus = objet["appels"], objet["refus"]
            if objet.get("jour") != jour or set(appels) != set(SOURCES) or set(refus) != set(SOURCES) \
                    or any(isinstance(v, bool) or not isinstance(v, int) or v < 0 for v in list(appels.values()) + list(refus.values())):
                raise CompteurInvalide(f"compteur journalier {chemin} : contenu invalide")
            return {s: appels[s] for s in SOURCES}, {s: refus[s] for s in SOURCES}
        except CompteurInvalide:
            raise
        except (OSError, ValueError, KeyError, IndexError, TypeError, UnicodeDecodeError) as e:
            raise CompteurInvalide(f"compteur journalier {chemin} : illisible ({type(e).__name__}) : le relais ne démarre pas") from e

    def _ecrire(self):
        if self.dossier is None:
            return
        chemin = self._chemin(self.jour)
        octets = (json.dumps({"jour": self.jour, "appels": self.appels, "refus": self.refus}, sort_keys=True, ensure_ascii=False,
                             indent=1) + "\n").encode("utf-8")
        for cible, contenu in ((chemin, octets), (chemin + ".sha256",
                                                    f"{hashlib.sha256(octets).hexdigest()}  {os.path.basename(chemin)}\n".encode("utf-8"))):
            provisoire = cible + ".provisoire"
            with open(provisoire, "wb") as f:
                f.write(contenu)
                f.flush()
                os.fsync(f.fileno())
            os.replace(provisoire, cible)

    def _aujourd_hui(self):
        jour = self._maintenant_jour()
        if jour != self.jour:
            self.jour, self.appels, self.refus = jour, {s: 0 for s in SOURCES}, {s: 0 for s in SOURCES}
            if self.dossier is not None:
                lu = self._charger(jour)
                if lu is not None:
                    self.appels, self.refus = lu
                else:
                    self._ecrire()
        return jour

    def reserver(self, source):
        with self._verrou:
            self._aujourd_hui()
            if self.appels[source] + 1 > self.plafond:
                self.refus[source] += 1
                self._ecrire()
                return False
            self.appels[source] += 1
            self._ecrire()
            return True

    def refuser(self, source):
        with self._verrou:
            self._aujourd_hui()
            if source in self.refus:
                self.refus[source] += 1
                self._ecrire()

    def etat(self):
        with self._verrou:
            jour = self._aujourd_hui()
            return {"jour": jour, "plafond_par_source_par_jour": self.plafond, "appels": dict(self.appels), "refus": dict(self.refus),
                    "persistant": self.dossier is not None}


def fabriquer_gestionnaire(compteur, journal, verrou_journal, amont_factice=None, courriel=None):
    garde = GardeFuite(fragments_interdits=())  # règles 1 à 3 seulement, refaites ici

    def ecrire_journal(entree):
        if journal is None:
            return
        with verrou_journal:
            with open(journal, "a", encoding="utf-8") as f:
                f.write(json.dumps(entree, ensure_ascii=False, sort_keys=True) + "\n")

    class Gestionnaire(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"
        server_version = "RelaisMoisson/" + VERSION

        def log_message(self, format, *args):  # noqa: A002 — signature imposée par la bibliothèque standard
            pass

        def _json(self, statut, objet):
            corps = json.dumps(objet, ensure_ascii=False).encode("utf-8")
            self.send_response(statut)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(corps)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(corps)
            self.close_connection = True

        def do_POST(self):
            return self._json(404, {"erreur": "méthode non servie"})

        def do_GET(self):
            debut = time.time()
            p = urllib.parse.urlsplit(self.path)
            if p.path == CHEMIN_ETAT:
                return self._json(200, dict(compteur.etat(), courriel_politesse_defini=bool(courriel),
                                            amont_factice=bool(amont_factice), sources=list(SOURCES), version=VERSION))
            if p.path not in CHEMINS:  # dont /moisson/brave
                ecrire_journal({"quand": debut, "chemin": p.path, "statut": 404, "motif": "route non servie"})
                return self._json(404, {"erreur": "route non servie (sources : arxiv, openalex)"})
            source = p.path.rsplit("/", 1)[-1]
            if self.headers.get("x-jeton-moisson") != JETON_MOISSON_FACTICE:
                compteur.refuser(source)
                ecrire_journal({"quand": debut, "source": source, "statut": 401, "motif": "jeton différent du jeton factice"})
                return self._json(401, {"erreur": "le relais de moisson n'accepte que le jeton factice du noyau"})
            params = urllib.parse.parse_qs(p.query, keep_blank_values=True)
            if set(params) != {"q", "n"} or any(len(v) != 1 for v in params.values()):
                compteur.refuser(source)
                ecrire_journal({"quand": debut, "source": source, "statut": 400, "motif": "paramètres : q et n seulement"})
                return self._json(400, {"erreur": "paramètres refusés : q et n seulement, une valeur chacun"})
            q, n = params["q"][0], params["n"][0]
            if not re.fullmatch(r"[1-9]\d*", n) or int(n) > MAX_RESULTATS_PAR_REQUETE:
                compteur.refuser(source)
                ecrire_journal({"quand": debut, "source": source, "statut": 400, "motif": f"n hors de [1, {MAX_RESULTATS_PAR_REQUETE}]"})
                return self._json(400, {"erreur": f"n : entier de 1 à {MAX_RESULTATS_PAR_REQUETE}"})
            n = int(n)
            motif = garde.verifier(q, regles=(1, 2, 3))
            if motif:
                compteur.refuser(source)
                ecrire_journal({"quand": debut, "source": source, "statut": 400, "motif": motif, "taille_requete": len(q)})
                return self._json(400, {"erreur": "requête refusée par la garde du relais (règles 1 à 3)"})
            if not compteur.reserver(source):
                ecrire_journal({"quand": debut, "source": source, "statut": 429, "motif": "plafond par source et par jour atteint",
                                **compteur.etat()})
                return self._json(429, {"erreur": "plafond de requêtes par source et par jour atteint", **compteur.etat()})
            url = url_amont(source, q, n, amont_factice, courriel)
            parties = urllib.parse.urlsplit(url)
            en_tetes = {"Accept-Encoding": "identity", "Host": parties.netloc}
            if courriel:  # identité envoyée seulement si Lazar a nommé un courriel
                en_tetes["User-Agent"] = f"relais-moisson-pole/{VERSION} (mailto:{courriel})"
            connexion = (http.client.HTTPSConnection if parties.scheme == "https" else http.client.HTTPConnection)(
                parties.hostname, parties.port, timeout=DELAI_AMONT_S)
            try:
                connexion.request("GET", parties.path + "?" + parties.query, headers=en_tetes)
                reponse = connexion.getresponse()
                octets = reponse.read(TAILLE_MAX_AMONT + 1)
                statut_amont = reponse.status
            except (OSError, http.client.HTTPException) as e:
                connexion.close()
                ecrire_journal({"quand": debut, "source": source, "statut": 502, "motif": "amont injoignable : " + type(e).__name__,
                                "requete": q, "n": n})
                return self._json(502, {"erreur": "amont injoignable : " + type(e).__name__})
            finally:
                connexion.close()
            if statut_amont != 200 or len(octets) > TAILLE_MAX_AMONT:
                ecrire_journal({"quand": debut, "source": source, "statut": 502, "motif": f"amont : statut {statut_amont}, "
                                f"{len(octets)} octets", "requete": q, "n": n})
                return self._json(502, {"erreur": f"amont : statut {statut_amont}"})
            try:
                resultats = LECTEURS[source](octets)
            except (ET.ParseError, ValueError, UnicodeDecodeError, AttributeError, TypeError) as e:
                ecrire_journal({"quand": debut, "source": source, "statut": 502, "motif": "amont : réponse illisible : " + type(e).__name__,
                                "requete": q, "n": n})
                return self._json(502, {"erreur": "amont : réponse illisible"})
            objet = construire_reponse(source, q, n, octets, resultats)
            ecrire_journal({"quand": debut, "duree_s": round(time.time() - debut, 3), "source": source, "statut": 200, "requete": q,
                            "n": n, "octets_amont": len(octets), "resultats": len(objet["resultats"]),
                            "empreinte_brute": objet["empreinte_brute"], "empreinte": objet["empreinte"],
                            "identite_envoyee": bool(courriel)})
            return self._json(200, objet)

    return Gestionnaire


def servir(hote, port, plafond_par_source_par_jour, journal=None, amont_factice=None, courriel=None, pret=None, dossier_compteur=None):
    valider_hote(hote)
    if amont_factice:
        amont_factice = valider_amont_factice(amont_factice)
    elif not dossier_compteur:  # v49 (CL13-09) : l'amont réel exige un plafond journalier persistant
        raise RelaisInvalide("amont réel : --dossier-compteur est obligatoire (plafond par jour persistant, sinon un redémarrage "
                             "le remettrait à zéro)")
    compteur = CompteurJournalier(plafond_par_source_par_jour, dossier_compteur)
    gestionnaire = fabriquer_gestionnaire(compteur, journal, threading.Lock(), amont_factice, courriel or None)
    serveur = ThreadingHTTPServer((hote, port), gestionnaire)
    serveur.daemon_threads = True
    url = f"http://{hote}:{serveur.server_address[1]}"
    if pret is not None:
        pret.url = url
        pret.set()
    print(f"relais de moisson prêt sur {url} (sources {', '.join(SOURCES)} ; amont "
          f"{'factice ' + amont_factice if amont_factice else 'réel (SUPPOSÉ)'} ; plafond {plafond_par_source_par_jour} par "
          f"source et par jour, {'persistant dans ' + dossier_compteur if dossier_compteur else 'en mémoire seulement'} ; "
          f"identité {'envoyée' if courriel else 'non envoyée'})", flush=True)
    try:
        serveur.serve_forever()
    finally:
        serveur.server_close()
    return url


def analyseur():
    a = argparse.ArgumentParser(prog="relais_moisson", description="Relais de moisson local tenu par le noyau (arXiv, OpenAlex).")
    a.add_argument("--hote", default="127.0.0.1")
    a.add_argument("--port", type=int, default=8788, help="0 : port libre choisi par le système")
    a.add_argument("--plafond-par-source-par-jour", type=int, default=PLAFOND_PAR_SOURCE_PAR_JOUR_DEFAUT)
    a.add_argument("--journal", help="journal des appels (JSON par ligne, sans clé)")
    a.add_argument("--dossier-compteur", default=None,
                   help="v49 : dossier du compteur journalier persistant (un fichier scellé par jour UTC) ; obligatoire avec "
                        "l'amont réel")
    a.add_argument("--amont-factice", default=None, help="essais : adresse http de la boucle locale qui remplace les amonts "
                                                         "(/arxiv, /openalex)")
    a.add_argument("--courriel-politesse", default="", help="courriel de politesse d'OpenAlex ; vide (défaut) : aucun en-tête "
                                                            "d'identité n'est envoyé — à nommer par Lazar")
    return a


def principal(argv=None):
    args = analyseur().parse_args(argv)
    try:
        if not (args.plafond_par_source_par_jour >= 1):
            raise RelaisInvalide("plafond par source et par jour : entier ≥ 1")
        servir(args.hote, args.port, args.plafond_par_source_par_jour, args.journal, args.amont_factice, args.courriel_politesse,
               dossier_compteur=args.dossier_compteur)
    except RelaisInvalide as erreur:
        print(f"erreur : {erreur}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(principal())
