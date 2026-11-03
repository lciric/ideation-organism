"""Adaptateur de commande externe, version 64 (fichier neuf, R12) — tour fermé, étage 1 : décision du directeur sur TF-02
(« TF-02, options (a) et (c), décision du directeur, 3 novembre 2026 » ; l'option (c), sortie minimale par rôle, est dans les
commandes v3 de la session-depot ; ce module porte l'option (a)).

Constat TF-02 (session-depot, message n° 294, § 4, lecture du code des deux commandes, aucun appel) : quand le pire cas d'une
session dépasse son plafond (`PLAFOND_SESSION_USD`), la commande n'envoie rien et sort en **code 4**, sa dernière ligne JSON portant
`"envoye": false`. `AdaptateurCommandeExterne.lancer` (`pole/adaptateurs.py`, inchangé) lit tout code non nul comme « erreur » ;
l'étage v5 (`pole/tests_de_mort_v5.py`, inchangé) lève alors `EtageInterrompu` et la course entière s'arrêtait (code 3), après les
propositions payées — même pour le vérificateur, jamais décisif. Le relais Kimi par protocole du pôle lit déjà ce cas comme
« budget_depasse », rien envoyé (`pole/adaptateur_kimi_v53.py`, « pire cas au-dessus du plafond de session : rien envoyé ») ; la
commande externe s'y aligne ici.

Ce que ce module fait, et seulement cela :

1. `AdaptateurCommandeExterneV64` (au-dessus d'`AdaptateurCommandeExterneV56`, inchangée : recopie du modèle servi, porte
   « environnement ») : une sortie en **code 4** dont la dernière ligne non vide est un objet JSON portant `"envoye": false` (le
   booléen faux, et rien d'autre) est lue **« budget_depasse » pour cette session**, **coût compté 0** (rien envoyé ; le coût que
   la ligne déclare, un plancher, est dit au motif, jamais compté), marquée `rien_envoye` (`ResultatV64`). **Tout autre cas garde
   sa lecture** (celle de la v56) : autre code non nul, ligne sans `envoye`, `envoye` vrai ou autre que le booléen faux (0, « false
   »…), ligne illisible, délai dépassé, refus que la ligne dit (R-764 : statut « refus », jamais tu), commande non lancée.
   Le code de sortie est lu dans le motif d'erreur que rend la classe gelée (« commande externe : code N : … »,
   `pole/adaptateurs.py`, gelé par son empreinte) : essais sur une vraie commande locale qui sort en code 4 (sain et artefacts).
2. `rien_envoye(r)` : vrai seulement pour un `ResultatV64` marqué, de statut « budget_depasse » (cette lecture, ou la vérification
   préalable du cœur v64, `pole/tour_ferme_v64.AdaptateurEtageV64`).
3. **Barème prudent des commandes** (`prix_caractere_commande`, `bareme_depuis_configuration`) : prix d'un caractère d'entrée =
   prix d'entrée de la commande en dollars par million de jetons / 10⁶ / 3 (trois caractères par jeton : le barème prudent des
   commandes de la session-depot) ; lu dans la configuration, clé `fournisseurs.<relais>.prix_entree_usd_par_million_jetons`,
   réel fini > 0, **aucun défaut** (`BaremeAbsent`). Le cœur v64 le passe à l'étage (`prix_caractere_usd`, contrôle avant envoi de
   l'expérimentateur, `pole/tests_de_mort_v5.py` l. 468, inactif en v63) et l'applique au vérificateur.
4. `commandes_v64` : pour chaque relais nommé déclaré `commande_externe`, remplace l'adaptateur v56 construit par
   `ideation_v8.adaptateurs_reels_v56` (toutes ses vérifications jouées) par la v64 — même commande, même contrôle du modèle servi
   (exigé), même liste des modèles servis permis — et reconstruit sa porte de plafond sur l'adaptateur v64. Une entrée d'un autre
   type est laissée telle quelle (Kimi par protocole reste refusé par la garde des rôles du cœur, comme en v63).

Ce que la v64 ne change pas, dit : un « budget_depasse » d'un proposeur arrête la course (cœur, `ProposeurAdaptateur`, annexe A,
A.5) ; un code 4 venu d'une limite propre du relais (refus 402 de son plafond, 429 de son nombre d'appels : la commande les lit
aussi en code 4, rien parti) est lu de même (fin des tours de la carte pour ce rôle) : la session-depot doit s'assurer que ces
limites ne peuvent pas mordre pendant la course (annexe A, A.6 bis du brouillon 6).

Bibliothèque standard seule ; aucun réseau ici.
"""

import json
import math
import re
from dataclasses import dataclass

from .adaptateurs import Resultat
from .adaptateurs_v56 import AdaptateurCommandeExterneV56, porte_depuis_configuration

VERSION = "adaptateur-commande-v64"
CODE_RIEN_ENVOYE = 4
CARACTERES_PAR_JETON_COMMANDES = 3  # barème prudent des commandes de la session-depot (message n° 294, § 4)
CLE_BAREME = "prix_entree_usd_par_million_jetons"
MOTIF_CODE = re.compile(r"^commande externe : code (-?\d+) : ")
LECTURE_CODE_4 = ("v64 (TF-02, option a) : code 4 dont la dernière ligne porte « envoye » : false → « budget_depasse » pour cette "
                  "session, coût compté 0, marqué rien_envoye ; tout autre code non nul : lecture de la v56 (erreur)")


@dataclass
class ResultatV64(Resultat):
    """Le résultat d'une session (`pole/adaptateurs.Resultat`, mêmes champs), plus `rien_envoye` : la session n'a rien envoyé au
    modèle (code 4 « rien envoyé » de la commande, ou vérification préalable du cœur v64)."""
    rien_envoye: bool = False


class BaremeAbsent(ValueError):
    """La configuration ne porte pas le prix d'entrée d'une commande (barème prudent) : refus avant tout appel."""


class RelaisNonCommande(ValueError):
    """`commandes_v64` : un relais nommé n'a pas été construit en commande externe v56."""


def rien_envoye(r):
    """Vrai si la session n'a rien envoyé (`ResultatV64` marqué, statut « budget_depasse ») ; faux pour tout autre résultat."""
    return isinstance(r, ResultatV64) and r.rien_envoye is True and r.statut == "budget_depasse"


def derniere_ligne_json(sortie_octets):
    """L'objet JSON de la dernière ligne non vide de la sortie standard, s'il est un dictionnaire ; None sinon (lecture large :
    `texte` et `cout_usd` ne sont pas exigés ici — la lecture stricte reste celle de la classe gelée)."""
    lignes = [l for l in sortie_octets.decode("utf-8", "replace").splitlines() if l.strip()]
    if not lignes:
        return None
    try:
        objet = json.loads(lignes[-1])
    except (ValueError, RecursionError):
        return None
    return objet if isinstance(objet, dict) else None


def code_de_sortie(r):
    """Le code de sortie non nul que porte le motif d'erreur rendu par la classe gelée (« commande externe : code N : … ») ; None
    s'il n'y en a pas (sortie 0, délai dépassé, commande non lancée)."""
    m = MOTIF_CODE.match(str(getattr(r, "erreur", "") or ""))
    return int(m.group(1)) if m else None


class AdaptateurCommandeExterneV64(AdaptateurCommandeExterneV56):
    """La commande externe v56, plus la lecture du code 4 « rien envoyé » (point 1 de l'en-tête du module)."""

    nom = "commande-externe-v64"

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._brute = None

    def lire_derniere_ligne(self, sortie_octets):  # garde aussi la ligne brute (lecture large) le temps de l'appel
        self._brute = derniere_ligne_json(sortie_octets)
        return super().lire_derniere_ligne(sortie_octets)

    def description(self):
        d = super().description()
        d["version_v64"] = VERSION
        d["lecture_code_4"] = LECTURE_CODE_4
        return d

    def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
        self._brute = None
        r = super().lancer(role, consigne, dossier, budget_usd, max_tours, modele=modele)
        brute, self._brute = self._brute, None
        if r.statut == "erreur" and code_de_sortie(r) == CODE_RIEN_ENVOYE and isinstance(brute, dict) and brute.get("envoye") is False:
            declare = brute.get("cout_usd")
            return ResultatV64("", [], 0.0, "budget_depasse",
                               f"commande externe : code {CODE_RIEN_ENVOYE}, rien envoyé (dernière ligne : « envoye » : false ; coût "
                               f"déclaré {declare!r}, non compté) : lu « budget_depasse » pour cette session (v64, TF-02)",
                               rien_envoye=True)
        return r


def prix_caractere_commande(prix_entree_usd_par_million_jetons):
    """Prix d'un caractère d'entrée au barème prudent des commandes : prix d'entrée (dollars par million de jetons) / 10⁶ / 3 ;
    réel fini > 0 exigé (`BaremeAbsent`)."""
    v = prix_entree_usd_par_million_jetons
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v <= 0:
        raise BaremeAbsent(f"prix d'entrée par million de jetons : réel fini > 0, aucun défaut (reçu {v!r})")
    return float(v) / 1e6 / CARACTERES_PAR_JETON_COMMANDES


def bareme_depuis_configuration(conf, nom):
    """Le barème prudent de la commande du relais `nom`, lu dans `fournisseurs.<nom>.prix_entree_usd_par_million_jetons` ;
    rend {prix_entree_usd_par_million_jetons, caracteres_par_jeton, prix_caractere_usd} ; lève `BaremeAbsent` sinon."""
    f = ((conf or {}).get("fournisseurs") or {}).get(nom)
    v = f.get(CLE_BAREME) if isinstance(f, dict) else None
    try:
        prix = prix_caractere_commande(v)
    except BaremeAbsent:
        raise BaremeAbsent(f"configuration : fournisseurs.{nom}.{CLE_BAREME} exigé (prix d'entrée de la commande du relais en "
                           f"dollars par million de jetons, celui de son barème prudent ; réel fini > 0, aucun défaut ; reçu {v!r})"
                           ) from None
    return {CLE_BAREME: float(v), "caracteres_par_jeton": CARACTERES_PAR_JETON_COMMANDES, "prix_caractere_usd": prix}


def commandes_v64(conf, adaptateurs, portes, noms=("kimi", "argon")):
    """Copies de `adaptateurs` et `portes` où chaque relais nommé déclaré `commande_externe` passe à la v64 (même commande, modèle
    servi exigé, mêmes modèles servis permis ; porte reconstruite sur l'adaptateur v64) ; les autres entrées restent telles quelles.
    Lève `RelaisNonCommande` si un relais déclaré `commande_externe` n'a pas été construit en commande externe v56."""
    adaptateurs, portes = dict(adaptateurs), dict(portes)
    for nom in noms:
        f = ((conf or {}).get("fournisseurs") or {}).get(nom) or {}
        if f.get("type") != "commande_externe":
            continue
        if not isinstance(adaptateurs.get(nom), AdaptateurCommandeExterneV56):
            raise RelaisNonCommande(f"relais {nom} : commande externe v56 attendue, trouvé {type(adaptateurs.get(nom)).__name__}")
        ad = AdaptateurCommandeExterneV64(f["commande"], exiger_modele_servi=True, modeles_servis_permis=f.get("modeles_servis_permis"))
        adaptateurs[nom] = ad
        portes[nom] = porte_depuis_configuration(nom, f.get("porte_plafond"), ad)
    return adaptateurs, portes


__all__ = ("AdaptateurCommandeExterneV64", "ResultatV64", "BaremeAbsent", "RelaisNonCommande", "rien_envoye", "derniere_ligne_json",
           "code_de_sortie", "prix_caractere_commande", "bareme_depuis_configuration", "commandes_v64", "CODE_RIEN_ENVOYE",
           "CARACTERES_PAR_JETON_COMMANDES", "CLE_BAREME", "LECTURE_CODE_4", "VERSION")
