"""Relais de clé tenu par le noyau : interface, contrôles et simulation. Aucun relais réel n'est écrit ici.

Exigence (second ajout, point 5) : l'adaptateur réel ne met jamais la clé dans l'environnement de l'agent. La variable du
point d'accès de l'interface de programmation (`ANTHROPIC_BASE_URL`) est pointée vers un relais local, tenu par le noyau
(autre processus, idéalement autre utilisateur ou autre conteneur), qui ajoute la vraie clé aux requêtes sortantes.
L'agent ne reçoit qu'un jeton factice, que le relais remplace. Le code de l'orchestrateur ne lit jamais de valeur de
clé : il vérifie seulement l'**absence des noms** de variables de clé dans son propre environnement.
"""

import urllib.parse

VARIABLE_POINT_ACCES = "ANTHROPIC_BASE_URL"
VARIABLE_CLE = "ANTHROPIC_API_KEY"
JETON_FACTICE = "relais-local-sans-cle"
NOMS_DE_CLE = (
    "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "CLAUDE_CODE_OAUTH_TOKEN", "OPENAI_API_KEY", "GOOGLE_API_KEY",
    "GEMINI_API_KEY", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN", "GITHUB_TOKEN", "GH_TOKEN", "HF_TOKEN",
)
HOTES_LOCAUX = {"127.0.0.1", "localhost", "::1"}


class RelaisInvalide(ValueError):
    pass


class CleDansEnvironnement(RuntimeError):
    """Une variable de clé est présente dans l'environnement de l'orchestrateur : la clé doit rester dans le relais."""


def valider_url_relais(url):
    """Le relais doit être local (boucle locale) : rien ne part vers un hôte distant avec le jeton factice."""
    if not isinstance(url, str) or not url:
        raise RelaisInvalide("adresse du relais manquante")
    parties = urllib.parse.urlsplit(url)
    if parties.scheme not in ("http", "https"):
        raise RelaisInvalide(f"schéma non permis pour le relais : {parties.scheme!r}")
    if parties.hostname not in HOTES_LOCAUX:
        raise RelaisInvalide(f"le relais doit être local (127.0.0.1, localhost ou ::1), reçu {parties.hostname!r}")
    if parties.username or parties.password:
        raise RelaisInvalide("aucun identifiant dans l'adresse du relais")
    return url


def variables_agent(url_relais):
    """Variables passées à l'agent : point d'accès vers le relais, jeton factice à la place de la clé."""
    return {VARIABLE_POINT_ACCES: valider_url_relais(url_relais), VARIABLE_CLE: JETON_FACTICE}


def noms_de_cle_presents(environnement):
    """Noms (jamais les valeurs) des variables de clé présentes dans un environnement donné."""
    return [nom for nom in NOMS_DE_CLE if nom in environnement]


class Relais:
    """Interface du relais tenu par le noyau."""

    url = None

    def transmettre(self, requete):
        raise NotImplementedError


class RelaisSimule(Relais):
    """Simulation pour les essais : remplace le jeton factice par la clé détenue, ne la rend jamais à l'appelant."""

    def __init__(self, cle_detenue, url="http://127.0.0.1:8787"):
        self.url = valider_url_relais(url)
        self._cle = cle_detenue
        self.journal = []

    def transmettre(self, requete):
        en_tetes = dict(requete.get("en_tetes", {}))
        recu = en_tetes.get("x-api-key")
        if recu not in (None, JETON_FACTICE):
            raise RelaisInvalide("jeton inattendu : l'agent ne doit présenter que le jeton factice")
        sortante = dict(requete, en_tetes=dict(en_tetes, **{"x-api-key": self._cle}))
        self.journal.append({"chemin": requete.get("chemin"), "cle_ajoutee": sortante["en_tetes"]["x-api-key"] == self._cle})
        return {"statut": 200, "en_tetes_vus_par_l_agent": {k: ("[CAVIARDÉ]" if k == "x-api-key" else v)
                                                            for k, v in sortante["en_tetes"].items()}}
