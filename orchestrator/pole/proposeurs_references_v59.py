"""Proposeurs de référence de la tâche A4, version 59 (fichier neuf, R12) — scriptés, sans modèle, sans réseau, sans dépense.

`pole/proposeurs_references.py` (v7) a un proposeur « aléatoire » (graines par `random` et `graine_derivee`, d'avant R9) et un
chercheur « mécanique », mais **aucun proposeur qui recopie ou mélange des lois déjà promues**. La version 59 donne les deux
bras de référence de A4 :

- « aleatoire » : `nombre` lois tirées au hasard dans la grammaire du monde planté (softmax sur un ou deux traits, poids
  gaussiens d'écart-type 1,2 bornés à ±4, biais nuls : le gabarit de `propositions_aleatoires` de la v7), graine par
  `SeedSequence` dérivée de la tâche (R9) ; il ne lit rien de l'héritage (la vue est vérifiée, jamais utilisée) ;
- « recopie_melange » : des cartes construites **seulement** à partir des lois de l'archive servies par la vue (lois retenues
  par la sélection scellée des générations précédentes) : copie sous un autre nom, mélange ½–½ avec l'uniforme, mélange de
  deux lois retenues, loi retenue tempérée et inclinée. Archive vide : aucune carte, motif rendu (jamais de repli).

Les deux reçoivent la **vue** de `boucle_fermee_v59.vue_pour_proposeur` et la repassent à `exiger_vue_sans_verdict` : un
proposeur de référence ne voit jamais un verdict du juge, une richesse, une promotion ni un compte. Chaque carte porte le même
test de mort préenregistré (gain moyen de log-score sur la marginale de la tranche, bloc `statistique`), comme les cartes
scriptées du mode à blanc.
"""

import random

from .boucle_fermee_v59 import exiger_vue_sans_verdict, graine_de_tache

VERSION = "proposeurs-references-v59"
BRAS = ("aleatoire", "recopie_melange")
K, DIM = 3, 2
BORNE = 4.0
ECART_TYPE = 1.2
TEST_DE_MORT = {"seuil": "au moins 0,02", "donnees": ["episodes.csv"],
                "test": ("gain moyen par épisode du log-score de la loi sur la marginale empirique de la tranche (nat), calculé "
                         "sur episodes.csv"),
                "statistique": {"fichier": "gains.csv", "colonne": "gain", "statistique": "moyenne"}}


def _borner(x):
    return max(-BORNE, min(BORNE, round(float(x), 6)))


def _prefixe(tache):
    """« …|generation=2 » → « G2 » (préfixe des identifiants de cartes)."""
    return tache.split("|")[-1].replace("generation=", "G")


def carte(identifiant, titre, loi, source, *, test_de_mort=None, hypothese=None):
    """Une carte au gabarit du mode à blanc (champs fermés)."""
    return {"identifiant": identifiant, "titre": titre,
            "hypothese": hypothese or f"{titre} : la loi prédictive annoncée décrit l'issue mieux que la marginale",
            "prediction": f"gain moyen de log-score {(test_de_mort or TEST_DE_MORT)['seuil']} nat par épisode", "signe": "+",
            "metrique": "richesse W du pari (juge) ; gain moyen de log-score (test de mort)", "loi_predictive": loi,
            "test_de_mort": dict(test_de_mort or TEST_DE_MORT), "source": source}


def loi_aleatoire(rng):
    traits = sorted(rng.sample(range(DIM), rng.choice([1, 2])))
    poids = [[0.0] * DIM for _ in range(K)]
    for c in range(K):
        for t in traits:
            poids[c][t] = _borner(rng.gauss(0.0, ECART_TYPE))
    return {"type": "softmax", "poids": poids, "biais": [0.0] * K}


def proposer_aleatoire(vue, nombre, racine, tache):
    """`nombre` lois tirées dans la grammaire du monde ; la vue est vérifiée (aucun verdict), jamais lue. Rend (cartes, motif)."""
    exiger_vue_sans_verdict(vue)
    rng = random.Random(graine_de_tache(racine, f"{tache}|proposeur=aleatoire"))
    return [carte(f"{_prefixe(tache)}-ALEA-{i + 1:02d}", f"Référence aléatoire n° {i + 1}", loi_aleatoire(rng), "aleatoire")
            for i in range(nombre)], None


def proposer_recopie_melange(vue, nombre, racine, tache):
    """Cartes faites des seules lois de la vue (archive des retenues) ; archive vide → ([], motif). Rend (cartes, motif)."""
    exiger_vue_sans_verdict(vue)
    lois = [(x["identifiant"], x["loi"]) for x in vue.get("lois_retenues") or []]
    if not lois:
        return [], "héritage vide : aucune loi retenue à recopier ni à mélanger (aucune carte, aucun repli)"
    rng = random.Random(graine_de_tache(racine, f"{tache}|proposeur=recopie_melange"))
    prefixe = _prefixe(tache)
    uniforme = {"type": "fixe", "probas": [1.0 / K] * K}
    candidats = []
    for ident, loi in lois:
        candidats.append((f"copie de {ident} sous un autre nom", loi))
        candidats.append((f"{ident} mélangée ½–½ à l'uniforme", {"type": "melange", "composantes": [loi, uniforme],
                                                                  "poids": [0.5, 0.5]}))
        candidats.append((f"{ident} tempérée et inclinée", {"type": "transformee", "base": loi,
                                                            "puissance": round(rng.uniform(0.6, 1.4), 6),
                                                            "inclinaison": [0.0] + [round(rng.gauss(0.0, 0.5), 6) for _ in range(K - 1)]}))
    for (a, la), (b, lb) in zip(lois, lois[1:]):
        pi = round(rng.uniform(0.3, 0.7), 6)
        candidats.append((f"mélange de {a} et {b}", {"type": "melange", "composantes": [la, lb], "poids": [pi, 1 - pi]}))
    return [carte(f"{prefixe}-COPIE-{i + 1:02d}", f"Référence recopie ou mélange n° {i + 1} ({quoi})", loi, "recopie_melange")
            for i, (quoi, loi) in enumerate(candidats[:nombre])], None


__all__ = ("proposer_aleatoire", "proposer_recopie_melange", "carte", "loi_aleatoire", "TEST_DE_MORT", "VERSION", "BRAS")
