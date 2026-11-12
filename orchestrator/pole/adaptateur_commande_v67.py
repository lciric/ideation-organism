"""Commandes externes de la course réelle, version 67 (fichier neuf, R12 ; `adaptateur_commande_v64.py` reste intact) — écart 1
au texte scellé de la course réelle de l'organisme (sortie du proposeur), option 2 décidée par le directeur (R-2426,
GO-2026-11-12-06).

Constat (écart 1, brouillon 1, section 2) : `adaptateur_commande_v64.commandes_v64` remplace l'adaptateur v56 que
`ideation_v8.adaptateurs_reels_v56` a construit **avec** `fournisseurs.<nom>.delai_s` par un adaptateur v64 construit **sans** ce
délai : la classe gelée (`pole/adaptateurs.py`, `AdaptateurCommandeExterne.DELAI_COMMANDE_S` = 1 800) tue alors le groupe de
processus de toute commande au bout de 1 800 s, quel que soit le délai de la configuration. À la course 2 du 12 novembre 2026,
le proposeur Kimi raisonnait encore après 46 711 jetons (1 553 s) : aucune borne de sortie plus haute ne sert sous ce délai.

Ce que ce module fait, et seulement cela :

1. `verifier_delais_v67(conf, noms)` — **garde 24 (neuve)**, avant tout appel et toute porte : pour chaque relais nommé déclaré
   `commande_externe`, `fournisseurs.<nom>.delai_s` est un réel fini, > 0 et ≤ `DELAI_MAX_S` (7 200 s, le délai que nomme
   GO-2026-11-12-06) ; la commande porte **une seule fois** l'option `--delai-s` suivie d'un réel fini > 0, et ce délai de la
   commande est inférieur au délai de l'adaptateur d'au moins `MARGE_MIN_S` (30 s), pour que la commande s'arrête d'elle-même
   (code 6, coût compté au pire cas réservé, ligne `fin` écrite au registre de dépense) avant que l'adaptateur ne tue son groupe.
   Tout manque : `DelaiRefuse` (refus nommé, aucun repli). Rend {nom: {"adaptateur_s", "commande_s"}}.
2. `commandes_v67(conf, adaptateurs, portes, noms)` : exactement `commandes_v64`, sauf que l'adaptateur v64 reçoit
   `delai_s = fournisseurs.<nom>.delai_s` (vérifié par la garde 24, jouée d'abord). Même commande, même contrôle du modèle servi
   (exigé), mêmes modèles servis permis, porte de plafond reconstruite sur l'adaptateur neuf ; une entrée d'un autre type est
   laissée telle quelle ; `RelaisNonCommande` si un relais déclaré `commande_externe` n'a pas été construit en commande v56.

Ce que la v67 ne change pas : la lecture du code 4 (`AdaptateurCommandeExterneV64`), le barème prudent, `rien_envoye`, les
commandes v6, les relais (le délai du relais Kimi, `--delai-amont-s`, est une option de lancement du relais, dite au texte et à la
consigne du poste : la garde 24 ne la voit pas). Bibliothèque standard seule ; aucun réseau ici.
"""

import math

from .adaptateur_commande_v64 import AdaptateurCommandeExterneV64, RelaisNonCommande
from .adaptateurs_v56 import AdaptateurCommandeExterneV56, porte_depuis_configuration

VERSION = "adaptateur-commande-v67"
DELAI_MAX_S = 7200.0
MARGE_MIN_S = 30.0
OPTION_DELAI = "--delai-s"


class DelaiRefuse(ValueError):
    """Garde 24 : délai de l'adaptateur absent, invalide ou au-delà de `DELAI_MAX_S`, ou délai de la commande absent, en double,
    invalide ou pas assez en deçà du délai de l'adaptateur : refus avant tout appel."""


def _reel_positif(v):
    """Le réel fini > 0 que porte un nombre JSON (int ou float, jamais un booléen ni une chaîne) ; None sinon."""
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return None
    x = float(v)
    return x if math.isfinite(x) and x > 0 else None


def verifier_delais_v67(conf, noms=("kimi", "argon")):
    """Garde 24 (point 1 de l'en-tête) ; rend {nom: {"adaptateur_s": float, "commande_s": float}} ; lève `DelaiRefuse`."""
    sortie = {}
    for nom in noms:
        f = ((conf or {}).get("fournisseurs") or {}).get(nom) or {}
        if f.get("type") != "commande_externe":
            continue
        adaptateur = _reel_positif(f.get("delai_s"))
        if adaptateur is None or adaptateur > DELAI_MAX_S:
            raise DelaiRefuse(f"garde 24 : fournisseurs.{nom}.delai_s = {f.get('delai_s')!r} : réel fini, > 0 et ≤ {DELAI_MAX_S:g} s "
                              "exigé : refus avant tout appel")
        c = f.get("commande")
        if not isinstance(c, list) or c.count(OPTION_DELAI) != 1 or c.index(OPTION_DELAI) + 1 >= len(c):
            raise DelaiRefuse(f"garde 24 : la commande de {nom} doit porter {OPTION_DELAI} une seule fois, suivi de sa valeur : refus "
                              "avant tout appel")
        brut = c[c.index(OPTION_DELAI) + 1]
        commande = None
        if isinstance(brut, str):
            try:
                commande = _reel_positif(float(brut))
            except ValueError:
                commande = None
        if commande is None:
            raise DelaiRefuse(f"garde 24 : {OPTION_DELAI} de {nom} = {brut!r} : réel fini > 0 exigé : refus avant tout appel")
        if commande > adaptateur - MARGE_MIN_S:
            raise DelaiRefuse(f"garde 24 : délai de la commande de {nom} ({commande:g} s) pas inférieur d'au moins {MARGE_MIN_S:g} s "
                              f"au délai de l'adaptateur ({adaptateur:g} s) : la commande ne s'arrêterait pas d'elle-même : refus "
                              "avant tout appel")
        sortie[nom] = {"adaptateur_s": adaptateur, "commande_s": commande}
    return sortie


def commandes_v67(conf, adaptateurs, portes, noms=("kimi", "argon")):
    """`commandes_v64` avec le délai de la configuration passé à l'adaptateur (point 2 de l'en-tête) ; garde 24 jouée d'abord."""
    verifier_delais_v67(conf, noms)
    adaptateurs, portes = dict(adaptateurs), dict(portes)
    for nom in noms:
        f = ((conf or {}).get("fournisseurs") or {}).get(nom) or {}
        if f.get("type") != "commande_externe":
            continue
        if not isinstance(adaptateurs.get(nom), AdaptateurCommandeExterneV56):
            raise RelaisNonCommande(f"relais {nom} : commande externe v56 attendue, trouvé {type(adaptateurs.get(nom)).__name__}")
        ad = AdaptateurCommandeExterneV64(f["commande"], delai_s=float(f["delai_s"]), exiger_modele_servi=True,
                                          modeles_servis_permis=f.get("modeles_servis_permis"))
        adaptateurs[nom] = ad
        portes[nom] = porte_depuis_configuration(nom, f.get("porte_plafond"), ad)
    return adaptateurs, portes


__all__ = ("VERSION", "DELAI_MAX_S", "MARGE_MIN_S", "OPTION_DELAI", "DelaiRefuse", "verifier_delais_v67", "commandes_v67")
