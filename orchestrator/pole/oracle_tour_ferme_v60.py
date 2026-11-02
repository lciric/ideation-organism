"""Oracle et classement des cartes du tour fermé, version 60 (fichier neuf, R12 ; tâches A2 et A4).

Préenregistrement : `prereg/preenregistrement-tour-ferme-v1-brouillon1.md`, section 3 (définitions gelées) et section 4.4
(intervalles). **Audit seulement** : rien de ce module n'est servi à un agent ni ne décide d'un verdict de la chaîne ; il dit,
après coup, si une carte promue puis survivante est une vraie ou une fausse découverte au regard de la loi plantée.

Sur les instances de l'oracle (les mêmes que `a_blanc_v59.oracle` : `random.Random(graine_de_tache(racine, "oracle|instances"))`,
`selection_pari.tirer_instances`, 4 000 instances), avec L* la loi plantée, m* sa marginale et q la loi d'une carte :

- G(q) = E_x Σ_k L*(k|x) [log q(k|x) − log m*(k)]  (nat par épisode) ;
- D(q) = E_x KL(L*(x) ‖ q(x)) ;
- G_arch(archive) = max(0 ; G de chaque loi de l'archive ; G de la mise en commun linéaire des lois de l'archive, de l'uniforme
  et des lois certaines, poids au maximum de vraisemblance attendue (EM) ; G de chaque loi de l'archive tempérée et inclinée,
  p(k) ∝ S(k)^a·exp(β_k), β_0 = 0, au maximum de vraisemblance attendue) ; ΔG = G − G_arch ;
- classement gelé (seuil g₀ = 0,02) : VD si promue puis survivante, G ≥ g₀ et ΔG ≥ g₀ ; VD* si de plus D ≤ 0,05 ; FD si promue
  puis survivante et (G < g₀ ou ΔG < g₀) ; toute PS du bras « recopie_melange » est une FD par construction ; « fausse promotion
  du juge » : promue et (G < g₀ ou ΔG < g₀), quel que soit le test de mort.

Intervalles : Wilson (score, bilatéral 95 %) et Newcombe (méthode 10) pour une différence de deux parts.
"""

import math
import random

import numpy as np
from scipy.optimize import minimize

from . import boucle_fermee_v59 as bf
from . import selection_pari as sp

VERSION = "oracle-tour-ferme-v60"
G0 = 0.02
D_PLANTEE = 0.05
N_ORACLE = 4000
PLANCHER = 1e-12
Z95 = 1.959963984540054


class OracleRefuse(ValueError):
    pass


def instances_oracle(racine, dim, n=N_ORACLE):
    rng = random.Random(bf.graine_de_tache(racine, "oracle|instances"))
    return sp.tirer_instances(rng, n, dim)


def matrice(loi, instances):
    """Probabilités (N × K) de la loi sur les instances, plancher 1e-12 puis renormalisées."""
    P = np.array([sp.proba(loi, x, [], 0) for x in instances], dtype=float)
    if P.ndim != 2 or not np.all(np.isfinite(P)):
        raise OracleRefuse("loi : probabilités non finies ou de forme inattendue")
    P = np.maximum(P, PLANCHER)
    return P / P.sum(axis=1, keepdims=True)


class Oracle:
    """Oracle d'un monde planté : L* et ses instances, fixées une fois."""

    def __init__(self, loi_plantee, racine, dim, n=N_ORACLE):
        self.instances = instances_oracle(racine, dim, n)
        self.P = matrice(loi_plantee, self.instances)
        self.marg = self.P.mean(axis=0)
        self.K = self.P.shape[1]

    def _esperance_log(self, Q):
        return float(np.mean(np.sum(self.P * np.log(Q), axis=1)))

    def gain_matrice(self, Q):
        return self._esperance_log(Q) - float(np.sum(self.marg * np.log(self.marg)))

    def gain(self, loi):
        return self.gain_matrice(matrice(loi, self.instances))

    def divergence(self, loi):
        Q = matrice(loi, self.instances)
        return float(np.mean(np.sum(self.P * (np.log(self.P) - np.log(Q)), axis=1)))

    def melange_ajuste(self, lois, iterations=500, tol=1e-10):
        """G de la mise en commun linéaire (lois de l'archive, uniforme, lois certaines), poids par EM sur l'espérance."""
        comps = [matrice(l, self.instances) for l in lois]
        comps.append(np.full_like(self.P, 1.0 / self.K))
        for k in range(self.K):
            c = np.full_like(self.P, PLANCHER)
            c[:, k] = 1.0
            comps.append(c / c.sum(axis=1, keepdims=True))
        C = np.stack(comps)  # J × N × K
        pi = np.full(len(comps), 1.0 / len(comps))
        avant = -np.inf
        for _ in range(iterations):
            M = np.tensordot(pi, C, axes=1)  # N × K
            R = pi[:, None, None] * C / M[None]
            pi = np.einsum("nk,jnk->j", self.P, R) / self.P.shape[0]
            pi = np.maximum(pi, 0.0)
            pi /= pi.sum()
            valeur = self._esperance_log(np.tensordot(pi, C, axes=1))
            if valeur - avant < tol:
                break
            avant = valeur
        return self.gain_matrice(np.tensordot(pi, C, axes=1)), pi

    def temperee_inclinee(self, loi):
        """G de la loi tempérée et inclinée au maximum de vraisemblance attendue, p(k) ∝ S(k)^a·exp(β_k), β_0 = 0."""
        L = np.log(matrice(loi, self.instances))

        def moins_vrais(theta):
            a, beta = theta[0], np.concatenate([[0.0], theta[1:]])
            Z = a * L + beta[None, :]
            Z -= Z.max(axis=1, keepdims=True)
            logq = Z - np.log(np.exp(Z).sum(axis=1, keepdims=True))
            return -float(np.mean(np.sum(self.P * logq, axis=1)))

        r = minimize(moins_vrais, np.concatenate([[1.0], np.zeros(self.K - 1)]), method="L-BFGS-B",
                     bounds=[(0.0, 10.0)] + [(-20.0, 20.0)] * (self.K - 1))
        return -float(r.fun) - float(np.sum(self.marg * np.log(self.marg))), r.x

    def gain_archive(self, archive):
        """G_arch : meilleur gain connu de l'archive dans la classe du nul v8 calculée à l'oracle (0 si archive vide)."""
        lois = list(archive.values()) if isinstance(archive, dict) else list(archive)
        if not lois:
            return 0.0
        candidats = [0.0] + [self.gain(l) for l in lois] + [self.melange_ajuste(lois)[0]]
        candidats += [self.temperee_inclinee(l)[0] for l in lois]
        return max(candidats)

    def mesurer(self, loi, archive):
        g, d, ga = self.gain(loi), self.divergence(loi), self.gain_archive(archive)
        return {"gain_nat": round(g, 6), "divergence_nat": round(d, 6), "gain_archive_nat": round(ga, 6),
                "delta_gain_nat": round(g - ga, 6)}


def classer(*, promue, survit, gain_nat, delta_gain_nat, divergence_nat, bras):
    """Classement gelé d'une carte non témoin (section 3 du préenregistrement). Rend un dictionnaire de drapeaux."""
    for nom, v in (("gain_nat", gain_nat), ("delta_gain_nat", delta_gain_nat), ("divergence_nat", divergence_nat)):
        if not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(v):
            raise OracleRefuse(f"{nom} : nombre fini attendu (reçu {v!r})")
    ps = bool(promue) and bool(survit)
    informative = gain_nat >= G0 and delta_gain_nat >= G0
    fd = ps and (bras == "recopie_melange" or not informative)
    vd = ps and not fd
    return {"promue_puis_survivante": ps, "vraie_decouverte": vd, "loi_plantee_retrouvee": vd and divergence_nat <= D_PLANTEE,
            "fausse_decouverte": fd, "fausse_promotion_du_juge": bool(promue) and not informative,
            "informative_et_nouvelle": informative}


def wilson(x, n, z=Z95):
    """Intervalle de Wilson (score) bilatéral ; (0, 1) si n = 0."""
    if isinstance(x, bool) or isinstance(n, bool) or not (isinstance(x, int) and isinstance(n, int)) or not 0 <= x <= n:
        raise OracleRefuse(f"Wilson : entiers 0 ≤ x ≤ n attendus (reçu {x!r}, {n!r})")
    if n == 0:
        return (0.0, 1.0)
    p, d = x / n, 1 + z * z / n
    c, h = (p + z * z / (2 * n)) / d, z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def newcombe(x1, n1, x2, n2, z=Z95):
    """Intervalle de Newcombe (méthode 10, hybride de Wilson) pour p1 − p2."""
    if n1 == 0 or n2 == 0:
        raise OracleRefuse("Newcombe : deux effectifs non nuls attendus")
    p1, p2 = x1 / n1, x2 / n2
    l1, u1 = wilson(x1, n1, z)
    l2, u2 = wilson(x2, n2, z)
    d = p1 - p2
    return (d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2))


__all__ = ("Oracle", "classer", "wilson", "newcombe", "instances_oracle", "matrice", "OracleRefuse", "G0", "D_PLANTEE",
           "VERSION")
