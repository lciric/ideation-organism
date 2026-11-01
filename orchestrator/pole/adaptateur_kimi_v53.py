"""Adaptateur Kimi K3.1 Pro **par voie protocole** (v53, R-634 à R-643 : Kimi proposeur, juge et metteur en fusion).

Même contrat que les adaptateurs du pôle (`Adaptateur.lancer(role, consigne, dossier, budget_usd, max_tours, modele) ->
Resultat`) ; même contrat de bout que la commande de session-depot (`relais-kimi-v1/commande_kimi_v1.py`), mais **dans le
processus du noyau** : le noyau parle directement le protocole compatible OpenAI au **relais Kimi local v4** de session-depot
(`relais_kimi_v4.py` : `POST /v1/chat/completions` sans flux côté client, réponse `chat.completion` entière ;
`GET /relais/etat`). **Aucune clé ici** : le relais tient la clé, la liste des modèles permis, la barrière du modèle servi
(502 sur écart) et son plafond ; le noyau n'envoie aucun en-tête d'autorisation, n'utilise aucun mandataire (boucle locale
seulement) et n'active aucun outil (`tools` jamais envoyé : la recherche Web reste coupée, R-629 ne vaut pas ici).

Garde avant envoi (même hypothèse que le relais et la commande) : pire cas = (octets du corps + 1024) × prix d'entrée +
max_tokens × prix de sortie ≤ plafond de la session ; `max_tokens` = min(maximum injecté, ce que le reste paie) ; sous le
minimum injecté : refus sans envoi. **Prix, maximum et minimum de sortie, délai : injectés, aucun défaut.**

Coût : prompt_tokens × prix d'entrée + completion_tokens × prix de sortie (cache non déduit : borne haute) ; usage absent
après envoi → pire cas (marqué `cout_inconnu`) ; refus du relais avant l'amont (400, 402, 403, 411, 413, 429) → 0 dépensé
(plancher 1e-6 compté, comme la commande).

Refus (R-764, statut « refus ») : modèle servi ≠ modèle demandé (noms exacts ; suffixe de date strict admis, comme
`modele_conforme`), 502 du relais pour modèle servi différent, `finish_reason` = `content_filter`. Erreur : réponse vide,
tronquée (`length`), illisible, délai. Aucune bascule, aucun repli.
"""

import json
import math
import urllib.error
import urllib.parse
import urllib.request

from .adaptateurs import Adaptateur, Resultat, modele_conforme
from .caviardage import caviarder

VERSION = "adaptateur-kimi-protocole-v53"
ROLES_PERMIS = ("proposeur_ideation", "juge_ideation", "fusion_ideation")
REFUS_AVANT_AMONT = (400, 402, 403, 411, 413, 429)
PLANCHER = 1e-6


class ReglageKimiRefuse(ValueError):
    pass


def _reel_positif(v):
    return not isinstance(v, bool) and isinstance(v, (int, float)) and math.isfinite(v) and v > 0


def valider_url_relais_kimi(url):
    u = urllib.parse.urlsplit(url or "")
    if u.scheme != "http" or u.hostname not in ("127.0.0.1", "localhost") or u.path not in ("", "/") or u.query:
        raise ReglageKimiRefuse("relais Kimi : http://127.0.0.1:PORT seulement (le relais local tient la clé)")
    return url.rstrip("/")


class AdaptateurKimiProtocole(Adaptateur):
    nom = "kimi-protocole"

    def __init__(self, url_relais, *, modele, prix_entree, prix_sortie, max_sortie_jetons, sortie_min_jetons, delai_s,
                 ouvreur=None):
        self.base = valider_url_relais_kimi(url_relais)
        if not isinstance(modele, str) or not modele:
            raise ReglageKimiRefuse("modèle Kimi : nom exact exigé (aucun défaut)")
        for nom, v in (("prix_entree", prix_entree), ("prix_sortie", prix_sortie), ("delai_s", delai_s)):
            if not _reel_positif(v):
                raise ReglageKimiRefuse(f"{nom} : réel > 0 exigé, aucun défaut (reçu {v!r})")
        for nom, v in (("max_sortie_jetons", max_sortie_jetons), ("sortie_min_jetons", sortie_min_jetons)):
            if isinstance(v, bool) or not isinstance(v, int) or v < 1:
                raise ReglageKimiRefuse(f"{nom} : entier ≥ 1 exigé, aucun défaut (reçu {v!r})")
        if sortie_min_jetons > max_sortie_jetons:
            raise ReglageKimiRefuse("sortie_min_jetons > max_sortie_jetons")
        self.modele = modele
        self.pe, self.ps = float(prix_entree), float(prix_sortie)
        self.maxi, self.mini = max_sortie_jetons, sortie_min_jetons
        self.delai_s = float(delai_s)
        # boucle locale : jamais de mandataire (ProxyHandler vide) ; `ouvreur` injectable par les essais (faux relais)
        self.ouvreur = ouvreur or urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def description(self):
        return {"version": VERSION, "url_relais": self.base, "modele": self.modele, "prix_entree_usd_par_mtok": self.pe,
                "prix_sortie_usd_par_mtok": self.ps, "max_sortie_jetons": self.maxi, "sortie_min_jetons": self.mini,
                "delai_s": self.delai_s, "outils": "aucun (tools jamais envoyé)"}

    def _max_tokens(self, octets, plafond):
        reste = plafond - (octets + 1024) * self.pe / 1e6
        n = min(self.maxi, int(reste * 1e6 / self.ps)) if reste > 0 else 0
        return n if n >= self.mini else None

    def corps(self, consigne, plafond, modele):
        n = None
        for _ in range(4):  # point fixe : le corps grandit avec le chiffre de max_tokens
            c = json.dumps({"model": modele, "messages": [{"role": "user", "content": consigne}],
                            "max_tokens": n or self.maxi}, ensure_ascii=False).encode("utf-8")
            n2 = self._max_tokens(len(c), plafond)
            if n2 is None:
                return None, None, None
            if n2 == n:
                break
            n = n2
        c = json.dumps({"model": modele, "messages": [{"role": "user", "content": consigne}], "max_tokens": n},
                       ensure_ascii=False).encode("utf-8")
        pire = (len(c) + 1024) * self.pe / 1e6 + n * self.ps / 1e6
        if pire > plafond + 1e-12:
            return None, None, None
        return c, n, pire

    def lire_etat_relais(self):
        with self.ouvreur.open(urllib.request.Request(self.base + "/relais/etat", method="GET"), timeout=30) as r:
            return json.loads(r.read())

    def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
        if role not in ROLES_PERMIS:
            raise ValueError(f"l'adaptateur Kimi ne joue que {ROLES_PERMIS}, pas {role!r}")
        modele = modele or self.modele
        if modele != self.modele:
            return Resultat("", [], PLANCHER, "refus", f"modèle demandé {modele!r} ≠ modèle de l'adaptateur {self.modele!r}",
                            refus={"modele_demande": modele, "modele_servi": None, "evenement": "kimi.modele_non_permis"})
        if not _reel_positif(budget_usd):
            raise ValueError("plafond de session : réel > 0")
        if not isinstance(consigne, str) or not consigne.strip():
            return Resultat("", [], PLANCHER, "erreur", "consigne vide : rien envoyé")
        corps, n, pire = self.corps(consigne, float(budget_usd), modele)
        if corps is None:
            return Resultat("", [], PLANCHER, "budget_depasse", "pire cas au-dessus du plafond de session : rien envoyé")
        req = urllib.request.Request(self.base + "/v1/chat/completions", data=corps, method="POST",
                                     headers={"Content-Type": "application/json", "Content-Length": str(len(corps))})
        try:
            with self.ouvreur.open(req, timeout=self.delai_s) as rep:
                brut = rep.read()
        except urllib.error.HTTPError as e:
            texte = e.read()[:2000].decode("utf-8", "replace")
            if e.code in REFUS_AVANT_AMONT:
                statut = "budget_depasse" if e.code == 402 else ("refus" if e.code == 403 else "erreur")
                refus = {"modele_demande": modele, "modele_servi": None, "evenement": "relais.modele_non_permis"} if e.code == 403 else None
                return Resultat("", [], PLANCHER, statut, f"relais Kimi HTTP {e.code} avant l'amont : " + caviarder(texte)[0][:300],
                                refus=refus)
            try:
                corps_erreur = json.loads(texte)
            except ValueError:
                corps_erreur = {}
            erreur_dite = str(corps_erreur.get("erreur", "")) if isinstance(corps_erreur, dict) else ""
            if e.code == 502 and ("modèle servi" in erreur_dite or (isinstance(corps_erreur, dict) and "modele_servi" in corps_erreur)):
                return Resultat("", [], pire, "refus", "refus (R-764) : le relais a vu un modèle servi différent (502)",
                                refus={"modele_demande": modele, "modele_servi": None, "evenement": "relais.modele_servi"},
                                cout_inconnu=True, depense_modele_non_autorise_usd=pire)
            return Resultat("", [], pire, "erreur", f"relais Kimi HTTP {e.code} : " + caviarder(texte)[0][:300], cout_inconnu=True)
        except urllib.error.URLError as e:
            if isinstance(e.reason, ConnectionRefusedError):
                return Resultat("", [], PLANCHER, "erreur", "relais Kimi injoignable (connexion refusée) : rien envoyé")
            return Resultat("", [], pire, "erreur", "relais Kimi : " + str(e.reason)[:200], cout_inconnu=True)
        except (TimeoutError, OSError) as e:
            return Resultat("", [], pire, "erreur", "relais Kimi : " + type(e).__name__, cout_inconnu=True)
        try:
            objet = json.loads(brut)
            choix = objet["choices"][0]
            texte = choix["message"].get("content") or ""
            fin = choix.get("finish_reason")
        except (ValueError, KeyError, IndexError, TypeError, AttributeError):
            return Resultat("", [], pire, "erreur", "réponse du relais Kimi illisible", cout_inconnu=True)
        servi = objet.get("model")
        usage = objet.get("usage") or {}
        p, c = usage.get("prompt_tokens"), usage.get("completion_tokens")
        if all(isinstance(x, int) and not isinstance(x, bool) and x >= 0 for x in (p, c)):
            cout, inconnu = max((p * self.pe + c * self.ps) / 1e6, PLANCHER), False
        else:
            cout, inconnu = pire, True
        if not isinstance(servi, str) or not modele_conforme(modele, servi):
            return Resultat("", [], cout, "refus", f"refus (R-764) : modèle servi {servi!r} ≠ {modele!r}",
                            refus={"modele_demande": modele, "modele_servi": servi if isinstance(servi, str) else None,
                                   "evenement": "kimi.modele_servi"}, modele_servi=servi if isinstance(servi, str) else None,
                            depense_modele_non_autorise_usd=cout, cout_inconnu=inconnu)
        if fin == "content_filter":
            return Resultat("", [], cout, "refus", "refus dit par le modèle (finish_reason content_filter)",
                            refus={"modele_demande": modele, "modele_servi": servi, "evenement": "kimi.content_filter"},
                            modele_servi=servi, cout_inconnu=inconnu)
        if inconnu:
            return Resultat("", [], cout, "erreur", "usage absent : pire cas compté", cout_inconnu=True, modele_servi=servi)
        if fin == "length":
            return Resultat("", [], cout, "erreur", "réponse tronquée (finish_reason length)", modele_servi=servi)
        if not texte.strip():
            return Resultat("", [], cout, "erreur", "réponse vide", modele_servi=servi)
        if cout > float(budget_usd) + 1e-12:
            return Resultat(caviarder(texte)[0], [], cout, "budget_depasse", "coût au-dessus du plafond de session",
                            texte_brut=texte, modele_servi=servi)
        return Resultat(caviarder(texte)[0], [], cout, "ok", texte_brut=texte, modele_servi=servi)
