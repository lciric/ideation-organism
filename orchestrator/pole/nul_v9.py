"""Nul v9 du juge : le nul v8, plus les **recombinaisons par morceaux (un niveau) des lois connues**, comme membres ajustés.

Fichier neuf (R12) : aucun fichier existant n'est modifié ; le nul v8 (`pole/nul_v8.py`), le nul des filles v2
(`pole/nul_filles_v2.py`) et la sélection par pari (`pole/selection_pari.py`) sont importés tels quels. Brouillon de
conception, **non validé** : la validation est celle du préenregistrement
`prereg/preenregistrement-validation-nul-v9-brouillon1.md` (non scellé) ; la note de conception est
`prereg/rapport-redaction-nul-v9.md`.

Pourquoi : `pole/nul_v8.py` (lignes 83 à 90) déclare non couverte la recombinaison par morceaux de lois connues ; l'attaque
du 2 novembre l'a confirmé (monde W2 : S1 sur la sous-population 0, S2 sur la sous-population 1 ; fonction `carte` de
`pole/attaque_goodhart_v2.py`) : un proposeur modèle de langage qui lit la description du juge y trouve une loi promue qui
n'apporte rien au-delà de l'archive.

Membres ajoutés (type `ajuste_morceaux`, un par partition ; lois connues = celles de « ajuste_lineaire:archive » du nul v8 :
parents triés puis survivantes triées, au moins deux lois) :
- « morceaux:sous_population » : un morceau par valeur de la sous-population g ;
- « morceaux:seuil:z<j> » pour chaque trait j : deux morceaux, z_j ≤ s et z_j > s, **pour tout seuil réel s** (le seuil est
  ajusté avec le reste) ;
et, sur chaque morceau P, la loi m_P(x) = Σ_j a^P_j·L_j(x) + r, où les poids a^P ≥ 0 sont propres au morceau, le bruit
aveugle r ≥ 0 (un vecteur fixe sur les issues) est **commun à tous les morceaux**, et Σ_j a^P_j + Σ_k r_k = 1 pour chaque
morceau. La famille contient : chaque loi connue par morceaux (W2 : a^0 = S1, a^1 = S2, r = 0), tout si/sinon de deux lois
connues sur un seuil quelconque d'un trait, tout mélange de lois connues propre à chaque morceau, et chacune de ces lois
mélangée à une même loi aveugle fixe (« avec bruit »). Elle ne contient **aucune loi en escalier aveugle** : une loi aveugle
propre à chaque morceau (dépendance nouvelle à g ou à un seuil, qui serait une découverte) n'y est pas, parce que le bruit
est commun ; si r porte toute la masse sur un morceau, il la porte sur tous.

Calcul (valeur d'un membre à l'instant de lecture t, sur les t premières issues de la part d'évaluation, comme le nul v8) :
- le problème d'une partition fixée est concave (somme de logarithmes de fonctions linéaires) sur un polytope ; il est résolu
  par une méthode de points intérieurs (Newton avec barrière logarithmique et contraintes d'égalité couplées), par lots
  sur toutes les coupes d'un trait à la fois ;
- **la valeur rendue n'est jamais la valeur atteinte mais un certificat** : pour tout point x > 0,
  sup f ≤ f(x) + max_{v sommet} ∇f(x)·v − ∇f(x)·x, et ∇f(x)·x = t exactement (homogénéité) ; les sommets du polytope sont
  « une loi connue par morceau, r = 0 » et « r = δ_k, a = 0 » ; borne aussi par 0 (une log-vraisemblance est ≤ 0). Ce
  certificat (écart de Frank-Wolfe) est **exact**, sans hypothèse de convergence : un arrêt prématuré coûte en puissance,
  jamais en validité ;
- seuil réel quelconque : la vraisemblance ne dépend de s que par la partition des t instances observées, qui ne prend qu'au
  plus t + 1 valeurs (coupes entre valeurs distinctes du trait triées, plus les deux extrêmes) ; le sup sur s ∈ ℝ est donc le
  maximum sur ces coupes, chacune certifiée ;
- élagage certifié : une coupe dont le meilleur certificat est sous la meilleure valeur atteinte (par une coupe) ne peut pas
  porter le maximum ; elle garde son certificat, qui reste dans le maximum final (rendu = maximum, sur **toutes** les coupes,
  de leur meilleur certificat).

Argument de validité (court ; la version longue est dans le rapport de rédaction) :
1. Pour tout membre F du nul v9 et toute loi du monde P ∈ F (loi des issues sachant l'instance, sans mémoire), la valeur du
   membre à chaque instant lu domine log P(y_1..t | x_1..t) (certificat ci-dessus ; pour les membres log-linéaires du v8, à
   la marge de Newton près, réserve inchangée du v8). Le dénominateur, maximum des membres, la domine donc aussi :
   W_t ≤ Λ_t = q(y_1..t)/P(y_1..t), trajectoire par trajectoire.
2. Λ_t est une martingale de test sous P (positive, d'espérance 1) dans l'ordre du plan : q est la loi gelée avant les
   tirages, ou (pari à fraction) le mélange a priori, à poids fixés, de lois prévisibles ; un mélange à poids fixés de
   martingales de test **sous la même loi P** est une martingale de test. La richesse sous un membre reste donc sous une
   martingale de test : c'est une surmartingale positive majorée.
3. Ville : P(∃t lu : W_t ≥ 1/α) ≤ P(∃t : Λ_t ≥ 1/α) ≤ α, pour tout monde de tout membre, **quel que soit le nombre de
   membres** : le maximum ne coûte jamais de validité, seulement de la puissance.
4. Monotonie : 𝓝₉ ⊇ 𝓝₈ ; le dénominateur v9 domine celui du v8 sur les mêmes issues ; W(v9) ≤ W(v8) trajectoire par
   trajectoire ; toute promotion sous v9 en est une sous v8.
5. **Le mélange a priori n'est pas au dénominateur.** Un dénominateur log Σ_F π_F·exp(v_F) (mélange a priori sur les
   membres) ne domine qu'une fraction π_{F*} de la vraisemblance d'un monde de F* : W ≤ Λ/π_{F*} et la garantie tombe à
   α/π_{F*}. Le maximum la garde à α. Le mélange a priori a sa place au numérateur (pari à fraction, inchangé, point 2).

Classe **couverte** par le nul v9 (en plus de celle du v8) : toute loi qui, sur chaque morceau d'une partition à un niveau —
par sous-population, ou par seuil réel sur un seul trait —, est un mélange de lois connues propre au morceau, mélangé à une
même loi aveugle fixe pour tous les morceaux.
Classe **non couverte** (dite, non fermée ; la description publique du juge la dit, `NON_COUVERT_V9`) :
- profondeur 2 et plus (morceaux de morceaux : sous-population puis seuil, deux seuils, deux traits) ; seuils sur une
  combinaison de traits (coupes obliques) ; morceaux définis par l'historique ou par l'instant ;
- poids de mélange qui varient continûment avec l'instance (aiguillage doux) ;
- bruit aveugle propre à chaque morceau, et loi aveugle seule sur un morceau quand un autre porte une loi connue ;
- lois connues tempérées ou inclinées différemment par morceau (le v8 ne couvre la loi tempérée et inclinée que sur tout
  l'espace) ; compositions d'étapes ;
- produits de lois (sauf, pour une fille, le produit des deux parents, membre du v8) ; déformations non monotones ;
- lois hors de l'archive : témoins, fiches d'un autre espace, lois inconnues du pôle.
Une loi en escalier aveugle (loi fixe propre à chaque valeur de g ou à chaque côté d'un seuil) **reste promouvable** : elle
dit une dépendance que l'archive ne dit pas.

Garanties de code : `exiger_membres_v9` (garde : membres v8 intacts, chaque membre par morceaux présent une fois, lois
connues exactes, partition exacte) lève `NulV9Refuse` ; `evaluer_v9` refuse un membre inconnu ; aucune valeur de repli :
un membre dont le calcul échoue lève une exception (le juge rend alors « évaluation impossible », jamais une valeur muette).
"""

import copy
import math

import numpy as np

from . import nul_filles_v2 as nf
from . import nul_v8
from . import selection_pari as sp
from .outils import empreinte_objet, sha256_fichier

VERSION_NUL = "nul-v9"
TYPE_MORCEAUX = "ajuste_morceaux"
TYPES_AJUSTES_V9 = tuple(nf.TYPES_AJUSTES) + (TYPE_MORCEAUX,)
PREFIXE_MORCEAUX = "morceaux:"
MEMBRE_SOUS_POPULATION = "morceaux:sous_population"
# Points intérieurs : paliers de la barrière, pas de Newton au plus par palier, précision visée du maximum certifié.
PALIERS_MU = (1e-2, 1e-4, 1e-6, 1e-8)
PAS_MAX_PAR_PALIER = 30
DECREMENT_ARRET = 1e-9
FRACTION_AU_BORD = 0.99
DEPART_CENTRE = 0.1  # part du centre du polytope dans le point de départ (le reste : ajustement sans coupure)
TOLERANCE_ELAGAGE = 1e-9
TOLERANCE_GROUPE = 1e-3  # précision visée du maximum certifié d'une question (membre, instant), en logarithme naturel ;
# coût en puissance au plus 10⁻³ (jamais en validité : la valeur rendue reste la plus haute borne certifiée)

PHRASES_MEMBRES_V9 = {
    TYPE_MORCEAUX: ("chaque recombinaison par morceaux, à un niveau, des lois connues : un morceau par sous-population, ou "
                    "les deux côtés de tout seuil réel d'un seul trait ; sur chaque morceau un mélange des lois connues propre "
                    "au morceau, plus un bruit aveugle fixe commun à tous les morceaux ; poids et seuil ajustés au maximum de "
                    "vraisemblance sur ces mêmes issues"),
}
NON_COUVERT_V9 = (
    "morceaux de morceaux (profondeur 2 : sous-population puis seuil, deux seuils, deux traits) et seuils sur une "
    "combinaison de traits",
    "poids de mélange qui varient continûment avec les traits (aiguillage doux)",
    "bruit aveugle propre à chaque morceau, ou loi aveugle seule sur un morceau",
    "lois connues tempérées ou inclinées différemment selon le morceau, compositions d'étapes",
    "produits de lois connues, déformations non monotones",
)


class NulV9Refuse(ValueError):
    """Juge sans le nul v9 : membre par morceaux absent ou altéré, membre ajusté inconnu."""


class CalculMorceauxImpossible(RuntimeError):
    """Le calcul d'un membre par morceaux n'a pas pu produire de certificat (jamais remplacé par une valeur muette)."""


# --- membres -------------------------------------------------------------------------------------------------------------
def partition_seuil(indice):
    return {"type": "seuil", "indice": int(indice)}


def membres_morceaux(lois_connues, dimension):
    """Membres par morceaux d'une fiche dont les lois connues sont `lois_connues` (ordre de « ajuste_lineaire:archive »).

    Moins de deux lois connues : aucun membre (avec une seule loi connue et un bruit commun, chaque morceau porte la même
    loi : c'est le membre linéaire du v8)."""
    lois = [copy.deepcopy(l) for l in lois_connues]
    if len(lois) < 2:
        return []
    membres = [{"nom": MEMBRE_SOUS_POPULATION, "type": TYPE_MORCEAUX, "lois": copy.deepcopy(lois),
                "partition": {"type": "sous_population"}}]
    for j in range(int(dimension)):
        membres.append({"nom": f"{PREFIXE_MORCEAUX}seuil:z{j}", "type": TYPE_MORCEAUX, "lois": copy.deepcopy(lois),
                        "partition": partition_seuil(j)})
    return membres


def lois_connues(survivantes, lois_parents=None):
    """Lois connues d'une fiche, dans l'ordre du membre linéaire du v8 : parents triés, puis survivantes triées hors
    parents (`cycle.membres_de_l_archive`)."""
    parents = dict(lois_parents or {})
    return [parents[n] for n in sorted(parents)] + [survivantes[i] for i in sorted(survivantes) if i not in parents]


def membres_archive_v9(survivantes, lois_parents=None, nombre_issues=3, dimension=2, moniteur=None):
    """Membres d'archive du nul v9 : ceux du nul v8 (`nul_v8.membres_archive_v8`, gardés par sa garde), plus les membres par
    morceaux sur les mêmes lois connues ; la garde `exiger_membres_v9` vérifie le tout."""
    v8 = nul_v8.membres_archive_v8(survivantes, lois_parents, nombre_issues, dimension, moniteur)
    membres = v8 + membres_morceaux(lois_connues(survivantes, lois_parents), dimension)
    return exiger_membres_v9(membres, survivantes, lois_parents, dimension)


def exiger_membres_v9(membres, survivantes, lois_parents=None, dimension=2):
    """Garde : les membres du v8 sont intacts (`nul_v8.exiger_membres_ajustes`, `NulV8Refuse` traduit en `NulV9Refuse`), et,
    dès deux lois connues, chaque membre par morceaux (sous-population, puis un seuil par trait) est présent exactement une
    fois avec les lois connues exactes et sa partition exacte ; aucun membre par morceaux de trop. Rend `membres`."""
    try:
        nul_v8.exiger_membres_ajustes([m for m in membres if m.get("type") != TYPE_MORCEAUX], survivantes, lois_parents)
    except nul_v8.NulV8Refuse as e:
        raise NulV9Refuse(f"nul v9 : membres du nul v8 absents ou altérés ({e})") from e
    connues = lois_connues(survivantes, lois_parents)
    attendus = membres_morceaux(connues, dimension)
    presents = [m for m in membres if m.get("type") == TYPE_MORCEAUX or str(m.get("nom", "")).startswith(PREFIXE_MORCEAUX)]
    defauts = []
    for a in attendus:
        trouves = [m for m in presents if m.get("nom") == a["nom"]]
        if len(trouves) != 1:
            defauts.append(f"{a['nom']} présent {len(trouves)} fois")
            continue
        m = trouves[0]
        if m.get("type") != TYPE_MORCEAUX or m.get("lois") != a["lois"] or m.get("partition") != a["partition"]:
            defauts.append(f"{a['nom']} altéré (type, lois connues ou partition)")
    noms_attendus = {a["nom"] for a in attendus}
    defauts += [f"{m.get('nom')} inattendu" for m in presents if m.get("nom") not in noms_attendus]
    if defauts:
        raise NulV9Refuse(f"nul v9 : membre(s) par morceaux absent(s) ou altéré(s) : {', '.join(defauts)}")
    return membres


# --- calcul : points intérieurs par lots, certificats de Frank-Wolfe ----------------------------------------------------
def _probas_aux_issues(L, Y, M, actif, x, J):
    """m[i, c] = Σ_p M[p,i,c]·(L_i·a^p_c) + actif[i,c]·r_c[y_i], et 1 sur les instances hors de la coupe (log 1 = 0)."""
    P = M.shape[0]
    m = actif * (Y @ x[:, P * J:].T) + (1.0 - actif)
    for p in range(P):
        m = m + M[p] * (L @ x[:, p * J:(p + 1) * J].T)
    return m


def _certificats(L, Y, M, actif, x, J):
    """(f, certificat) par coupe : f(x) = Σ_i log m_i ; certificat = min(0, f + max(0, V − t_c)), V = max des valeurs du
    gradient aux sommets du polytope (une loi connue par morceau, ou r = δ_k), t_c = nombre d'instances de la coupe."""
    P = M.shape[0]
    m = _probas_aux_issues(L, Y, M, actif, x, J)
    inv = actif / m
    f = np.log(m).sum(axis=0)
    V = np.zeros(x.shape[0])
    for p in range(P):
        V = V + (L.T @ (M[p] * inv)).T.max(axis=1)
    V = np.maximum(V, (Y.T @ inv).T.max(axis=1))
    return f, np.minimum(0.0, f + np.maximum(0.0, V - actif.sum(axis=0)))


def maximiser_par_lots(L, Y, M, groupes, x0, points_a_certifier=()):
    """Maximum certifié de f_c(x) = Σ_i log(Σ_p M[p,i,c]·(L_i·a^p) + r_{y_i}) pour chaque coupe c, sur le polytope
    {a^p ≥ 0, r ≥ 0, Σ_j a^p_j + Σ_k r_k = 1 pour chaque morceau p}.

    `L` (n, J) : probabilités des lois connues aux issues observées ; `Y` (n, K) : issues en indicatrices ; `M` (P, n, C) :
    appartenance (0 ou 1) de chaque instance à chaque morceau, pour chaque coupe (une instance hors de tout morceau n'est
    pas dans la coupe : instants de lecture) ; `groupes` (C,) : étiquette de la question à laquelle la coupe appartient
    (membre et instant) — l'élagage se fait dans chaque groupe ; `x0` (C, P·J + K) : départs admissibles strictement
    positifs ; `points_a_certifier` : autres points admissibles (C, P·J + K) dont les certificats sont pris avant le
    premier pas (par exemple l'ajustement sans coupure lui-même). Rend (bornes, valeurs atteintes, diagnostic) par coupe.
    Chaque borne est un certificat (écart de Frank-Wolfe) : elle domine le vrai maximum de sa coupe **quel que soit l'état
    de convergence** ; les coupes élaguées (borne sous la meilleure valeur atteinte de leur groupe) gardent leur dernière
    borne ; un groupe dont la plus haute borne est à moins de `TOLERANCE_GROUPE` de sa meilleure valeur atteinte est
    terminé (sa réponse, la plus haute borne, est connue à cette précision près)."""
    n, J = L.shape
    K = Y.shape[1]
    P, _, C = M.shape
    q = P * J + K
    groupes = np.asarray(groupes, dtype=int)
    x = np.array(x0, dtype=float)
    if x.shape != (C, q) or not np.all(np.isfinite(x)) or not np.all(x > 0):
        raise CalculMorceauxImpossible("départ du calcul par morceaux non admissible")
    B = np.zeros((P, q))
    for p in range(P):
        B[p, p * J:(p + 1) * J] = 1.0
        B[p, P * J:] = 1.0
    if np.abs(x @ B.T - 1.0).max() > 1e-9:
        raise CalculMorceauxImpossible("départ du calcul par morceaux hors des contraintes")
    actif_tout = M.sum(axis=0)
    if actif_tout.max() > 1.0 + 1e-12:
        raise CalculMorceauxImpossible("une instance appartient à deux morceaux d'une même coupe")
    LL = (L[:, :, None] * L[:, None, :]).reshape(n, J * J)
    LY = (L[:, :, None] * Y[:, None, :]).reshape(n, J * K)
    diag_q, diag_k = np.arange(q), np.arange(K)
    nb_groupes = int(groupes.max()) + 1 if C else 0
    bornes = np.full(C, np.inf)
    atteintes = np.full(C, -np.inf)
    meilleure = np.full(nb_groupes, -np.inf)
    for point in [x] + [np.asarray(p, dtype=float) for p in points_a_certifier]:
        if point.shape != (C, q) or not np.all(np.isfinite(point)) or np.any(point < 0) or np.abs(point @ B.T - 1.0).max() > 1e-9:
            raise CalculMorceauxImpossible("point à certifier non admissible")
        mp = _probas_aux_issues(L, Y, M, actif_tout, point, J)
        if np.all(mp > 0):
            f0, b0 = _certificats(L, Y, M, actif_tout, point, J)
            bornes = np.minimum(bornes, b0)
            atteintes = np.maximum(atteintes, f0)
            np.maximum.at(meilleure, groupes, f0)
    actives = np.arange(C)
    pas_total = 0

    def restantes(actives):
        """Coupes encore à travailler : ni élaguées, ni dans un groupe terminé."""
        haute = np.full(nb_groupes, -np.inf)
        np.maximum.at(haute, groupes, bornes)
        termine = haute - meilleure <= TOLERANCE_GROUPE
        garde = (bornes[actives] >= meilleure[groupes[actives]] - TOLERANCE_ELAGAGE) & ~termine[groupes[actives]]
        return garde
    actives = actives[restantes(actives)]
    for mu in PALIERS_MU:
        for _ in range(PAS_MAX_PAR_PALIER):
            if not len(actives):
                break
            xa, Ma, actif, Ca = x[actives], M[:, :, actives], actif_tout[:, actives], len(actives)
            m = _probas_aux_issues(L, Y, Ma, actif, xa, J)
            if not np.all(m > 0):
                raise CalculMorceauxImpossible("probabilité nulle dans un membre par morceaux")
            inv = actif / m
            W2 = inv / m
            f = np.log(m).sum(axis=0)
            g = np.empty((Ca, q))
            H = np.zeros((Ca, q, q))
            V = np.zeros(Ca)
            for p in range(P):
                sl = slice(p * J, (p + 1) * J)
                g[:, sl] = (L.T @ (Ma[p] * inv)).T
                V = V + g[:, sl].max(axis=1)
                Wp = (Ma[p] * W2).T
                H[:, sl, sl] = -(Wp @ LL).reshape(Ca, J, J)
                hr = -(Wp @ LY).reshape(Ca, J, K)
                H[:, sl, P * J:] = hr
                H[:, P * J:, sl] = np.transpose(hr, (0, 2, 1))
            g[:, P * J:] = (Y.T @ inv).T
            H[:, P * J + diag_k, P * J + diag_k] = -(W2.T @ Y)
            V = np.maximum(V, g[:, P * J:].max(axis=1))
            certificat = np.minimum(0.0, f + np.maximum(0.0, V - actif.sum(axis=0)))
            bornes[actives] = np.minimum(bornes[actives], certificat)
            atteintes[actives] = np.maximum(atteintes[actives], f)
            np.maximum.at(meilleure, groupes[actives], f)
            garde = restantes(actives)
            if not garde.any():
                actives = actives[garde]
                break
            if not garde.all():
                actives, xa, Ma, Ca = actives[garde], xa[garde], Ma[:, :, garde], int(garde.sum())
                f, g, H = f[garde], g[garde], H[garde]
            g = g + mu / xa
            H[:, diag_q, diag_q] -= mu / xa ** 2
            KKT = np.zeros((Ca, q + P, q + P))
            KKT[:, :q, :q] = H
            KKT[:, :q, q:] = -B.T[None]
            KKT[:, q:, :q] = B[None]
            rhs = np.zeros((Ca, q + P, 1))
            rhs[:, :q, 0] = -g
            try:
                dx = np.linalg.solve(KKT, rhs)[:, :q, 0]
            except np.linalg.LinAlgError:
                dx = np.stack([np.linalg.lstsq(KKT[c], rhs[c], rcond=None)[0][:q, 0] for c in range(Ca)])
            if not np.all(np.isfinite(dx)):
                break  # les certificats déjà calculés restent valides ; on n'avance plus dans ce palier
            dec = (g * dx).sum(axis=1)
            pas_total += 1
            if dec.max() < DECREMENT_ARRET:
                break
            neg = dx < 0
            amax = np.where(neg, -xa / np.where(neg, dx, -1.0), np.inf).min(axis=1)
            pas = np.minimum(1.0, FRACTION_AU_BORD * amax)
            F0 = f + mu * np.log(xa).sum(axis=1)
            fait = dec <= 0  # aucune montée possible : la coupe garde son point
            actif_a = actif_tout[:, actives]
            for _ in range(40):
                xn = xa + pas[:, None] * dx
                mn = _probas_aux_issues(L, Y, Ma, actif_a, xn, J)
                with np.errstate(divide="ignore", invalid="ignore"):
                    Fn = np.log(mn).sum(axis=0) + mu * np.log(xn).sum(axis=1)
                ok = ~fait & np.all(xn > 0, axis=1) & np.all(mn > 0, axis=0) & (Fn >= F0 + 1e-4 * pas * dec)
                xa = np.where(ok[:, None], xn, xa)
                fait |= ok
                if fait.all():
                    break
                pas = np.where(fait, pas, 0.5 * pas)
            x[actives] = xa
    if len(actives):
        f, b = _certificats(L, Y, M[:, :, actives], actif_tout[:, actives], x[actives], J)
        bornes[actives] = np.minimum(bornes[actives], b)
        atteintes[actives] = np.maximum(atteintes[actives], f)
    if not np.all(np.isfinite(bornes)):
        raise CalculMorceauxImpossible("certificat non fini")
    return bornes, atteintes, {"pas": pas_total, "coupes": int(C), "coupes_restantes": int(len(actives))}


def _ajustement_sans_coupure(G, w0=None, iterations=300):
    """Poids approchés du mélange sans coupure (lois connues et lois certaines δ_k), par espérance-maximisation bornée en
    itérations : il ne sert que de point de départ (la valeur du membre vient des certificats)."""
    t, nb = G.shape
    w = np.full(nb, 1.0 / nb) if w0 is None else np.maximum(np.asarray(w0, dtype=float), 1e-6)
    w = w / w.sum()
    for _ in range(iterations):
        grad = G.T @ (1.0 / (G @ w))
        if grad.max() - t < 1e-6:
            break
        w = w * grad / t
        w = w / w.sum()
    return w


def _depart(J, K, P, w_global, centre=DEPART_CENTRE):
    """Point admissible : (1 − centre) × ajustement sans coupure (même mélange sur chaque morceau) + centre × centre du
    polytope ; strictement positif dès que `centre` > 0 (départ des points intérieurs), l'ajustement lui-même sinon (point
    certifié avant le premier pas)."""
    a, r = np.asarray(w_global[:J], dtype=float), np.asarray(w_global[J:], dtype=float)
    s = a.sum() + r.sum()
    glob = np.concatenate([np.tile(a / s, P), r / s])
    milieu = np.concatenate([np.full(P * J, 0.5 / J), np.full(K, 0.5 / K)])
    return (1.0 - centre) * glob + centre * milieu


def _coupes(partition, instances, t, valeurs_g):
    """Masques (P, n, C) des coupes de la partition à l'instant t (instances 0..t−1 de la part d'évaluation) et étiquettes.

    Sous-population : une seule coupe, un morceau par valeur de g de la part d'évaluation (`valeurs_g`, triées ; un morceau
    sans instance à l'instant t ne compte pas). Seuil sur le trait j : une coupe par partition {z_j ≤ s}, {z_j > s} que
    réalise un seuil réel, soit s = −∞ puis s = chaque valeur distincte de z_j parmi les t instances."""
    n = len(instances)
    dedans = (np.arange(n) < t).astype(float)
    if partition.get("type") == "sous_population":
        g = np.array([str(inst.get("g")) for inst in instances])
        M = np.stack([((g == v).astype(float) * dedans)[:, None] for v in valeurs_g])
        return M, [{"sous_populations": list(valeurs_g)}]
    if partition.get("type") == "seuil":
        j = partition["indice"]
        z = np.array([float(inst["z"][j]) for inst in instances])
        seuils = np.concatenate([[-np.inf], np.unique(z[:t])])
        lo = (z[:, None] <= seuils[None, :]).astype(float) * dedans[:, None]
        hi = dedans[:, None] - lo
        return np.stack([lo, hi]), [{"seuil": None if not np.isfinite(s) else float(s)} for s in seuils]
    raise NulV9Refuse(f"partition inconnue : {partition!r}")


def detail_morceaux_groupe(membres, cache, issues, instants):
    """Valeurs certifiées des membres par morceaux `membres` (mêmes lois connues) à chaque instant de lecture, calculées en
    un lot : {nom: {t: {valeur, atteinte, ecart_residuel, coupe, coupes, coupes_restantes, pas}}}. `ecart_residuel` =
    valeur − meilleure valeur atteinte (≥ 0) : prix en puissance de l'optimisation, jamais en validité."""
    if not membres:
        return {}
    lois = membres[0]["lois"]
    for m in membres:
        if m.get("type") != TYPE_MORCEAUX or m.get("lois") != lois:
            raise NulV9Refuse("calcul par morceaux en lot : membres de type ou de lois connues différents")
    y = np.array(issues, dtype=int)
    n = len(issues)
    instances = cache.instances
    tables = [np.array(cache.probas(l), dtype=float) for l in lois]
    J, K = len(tables), tables[0].shape[1]
    L = np.stack([tab[np.arange(n), y] for tab in tables], axis=1)
    Y = np.zeros((n, K))
    Y[np.arange(n), y] = 1.0
    G = np.concatenate([L, Y], axis=1)
    departs, w = {}, None
    for t in instants:
        w = _ajustement_sans_coupure(G[:t], w)
        departs[t] = w
    valeurs_g = sorted({str(inst.get("g")) for inst in instances})
    lots = {}
    for membre in membres:
        for t in instants:
            M, etiquettes = _coupes(membre["partition"], instances, t, valeurs_g)
            lots.setdefault(M.shape[0], []).append((membre["nom"], t, M, etiquettes))
    sortie = {m["nom"]: {} for m in membres}
    for P, questions in sorted(lots.items()):
        M = np.concatenate([qu[2] for qu in questions], axis=2)
        groupes = np.concatenate([np.full(qu[2].shape[2], i) for i, qu in enumerate(questions)])
        x0 = np.concatenate([np.tile(_depart(J, K, P, departs[qu[1]]), (qu[2].shape[2], 1)) for qu in questions])
        xg = np.concatenate([np.tile(_depart(J, K, P, departs[qu[1]], centre=0.0), (qu[2].shape[2], 1)) for qu in questions])
        bornes, atteintes, diag = maximiser_par_lots(L, Y, M, groupes, x0, points_a_certifier=(xg,))
        for i, (nom, t, Mq, etiquettes) in enumerate(questions):
            sel = np.flatnonzero(groupes == i)
            c = int(np.argmax(bornes[sel]))
            valeur, atteinte = float(bornes[sel].max()), float(atteintes[sel].max())
            sortie[nom][t] = {"valeur": valeur, "atteinte": atteinte, "ecart_residuel": max(0.0, valeur - atteinte),
                              "coupe": etiquettes[c], "coupes": int(len(sel)), "pas": diag["pas"]}
    return sortie


def valeurs_morceaux_groupe(membres, cache, issues, instants):
    return {nom: {t: d["valeur"] for t, d in par_t.items()}
            for nom, par_t in detail_morceaux_groupe(membres, cache, issues, instants).items()}


def valeurs_ajustees_v9(membres, cache, issues, nombre_issues, instants):
    """Valeurs des membres ajustés : les types du nul des filles v2 par `nul_filles_v2.valeurs_ajustees` (inchangé), les
    membres par morceaux en lots (un lot par liste de lois connues) ; tout autre type est refusé. Rend {nom: {t: valeur}}."""
    sortie, groupes = {}, {}
    for m in membres:
        if m["type"] in nf.TYPES_AJUSTES:
            sortie[m["nom"]] = nf.valeurs_ajustees(m, cache, issues, nombre_issues, instants)
        elif m["type"] == TYPE_MORCEAUX:
            groupes.setdefault(empreinte_objet(m["lois"]), []).append(m)
        else:
            raise NulV9Refuse(f"membre ajusté inconnu : {m['type']!r}")
    for lot in groupes.values():
        sortie.update(valeurs_morceaux_groupe(lot, cache, issues, instants))
    return sortie


# --- évaluation (copie de `nul_filles_v2.evaluer_v2`, un seul changement : la liste des types ajustés) -------------------
def evaluer_v9(gele, tirages, graine_noyau=None):
    """Comme `nul_filles_v2.evaluer_v2` (mêmes gardes, même lecture aux instants fixés, même règle de marge des filles), avec
    les membres par morceaux comptés parmi les membres ajustés (et donc parmi les enveloppes d'une fille). Sans membre par
    morceaux, le résultat est celui de `evaluer_v2`, valeur pour valeur (essai `EvaluateurV9.test_identique_a_v2_sans_morceaux`)."""
    if empreinte_objet(gele.engagement) != gele.empreinte:
        raise sp.EngagementModifie("le test a changé depuis son gel")
    if not isinstance(tirages, dict) or tirages.get("empreinte_engagement") != gele.empreinte:
        raise sp.TiragesNonLies("tirages sans lien avec l'empreinte de cet engagement")
    sp.verifier_plan_execution(gele, tirages, graine_noyau)
    return evaluer_sur_issues(gele.engagement, tirages.get("issues"), gele.empreinte)


def evaluer_sur_issues(e, issues, empreinte=None):
    """Le calcul de `evaluer_v9` **sans les gardes d'engagement et de tirages** : pour les bancs et les essais seulement
    (évaluer, sur les mêmes issues, la bibliothèque du v9 et celle du v8 : comparaison appariée, monotonie). Le juge
    passe toujours par `evaluer_v9`."""
    instants = e.get("instants_lecture")
    k, instances = e["nombre_issues"], e["instances"]
    if not isinstance(issues, list) or len(issues) != len(instances) or not all(
            isinstance(x, int) and not isinstance(x, bool) and 0 <= x < k for x in issues):
        raise sp.TiragesNonLies("issues absentes, mal formées ou en nombre différent du plan gelé")
    c = e.get("part_calibrage", 0)
    n = len(instances) - c
    if not instants or instants[-1] != n or instants != sorted(set(instants)) or instants[0] < 1:
        raise nf.InstantsInvalides("instants de lecture absents ou non conformes dans l'engagement")
    bibliotheque = sp.calibrer(e["bibliotheque"], issues[:c], instances[:c])
    ordinaires = [m for m in bibliotheque if m["type"] not in TYPES_AJUSTES_V9]
    ajustes = [m for m in bibliotheque if m["type"] in TYPES_AJUSTES_V9]
    issues, instances = issues[c:], instances[c:]
    cache = sp.Cache(issues, instances)
    numerateur = sp.trajectoire_numerateur(e, issues, instances, cache)
    par_membre = sp.trajectoires(ordinaires, issues, instances, k, cache)
    par_ajuste = valeurs_ajustees_v9(ajustes, cache, issues, k, instants)
    log_w, dominants = [], []
    for t in instants:
        candidats = [(traj[t - 1], nom) for nom, traj in par_membre.items()] + [(v[t], nom) for nom, v in par_ajuste.items()]
        meilleur, nom = max(candidats, key=lambda c: (c[0], c[1]))
        log_w.append(numerateur[t - 1] - meilleur)
        dominants.append(nom)
    seuil = math.log(1.0 / e["alpha"])
    i_promotion = next((i for i, v in enumerate(log_w) if v >= seuil), None)
    promue = i_promotion is not None
    resultat = {"log_richesse_finale": log_w[-1], "log_richesse_max": max(log_w), "seuil_log": seuil,
                "log_richesse_arretee": log_w[i_promotion] if promue else log_w[-1],
                "trajectoire_log_w": [round(v, 6) for v in log_w],
                "t_promotion": instants[i_promotion] if promue else None, "instants_lecture": list(instants),
                "nombre_tirages": n, "part_calibrage": c, "membre_dominant_final": dominants[-1],
                "plan_execution": sp.plan_execution_de(e), "empreinte_engagement": empreinte}
    enveloppes = {m["nom"]: par_membre[m["nom"]][-1] for m in ordinaires if m.get("enveloppe")}
    enveloppes.update({nom: v[n] for nom, v in par_ajuste.items()})
    if e.get("delta0") is not None and enveloppes:
        meilleure = max(enveloppes, key=lambda nom: (enveloppes[nom], nom))
        gain = (numerateur[-1] - enveloppes[meilleure]) / n
        resultat.update(meilleure_enveloppe=meilleure, gain_moyen_sur_meilleure_enveloppe=gain,
                        marge_requise=2 * e["delta0"], marge_atteinte=gain >= 2 * e["delta0"])
        promue = promue and gain >= 2 * e["delta0"]
    resultat["promue"] = promue
    if not promue:
        resultat["t_promotion"] = None
    return resultat


def sans_morceaux(engagement):
    """Copie de l'engagement dont la bibliothèque a perdu ses membres par morceaux : c'est la bibliothèque du nul v8 de la
    même fiche (comparaison appariée des bancs, sur les mêmes issues)."""
    e = copy.deepcopy(engagement)
    e["bibliotheque"] = [m for m in e["bibliotheque"] if m.get("type") != TYPE_MORCEAUX]
    return e


# --- appartenance (essais et bancs) ------------------------------------------------------------------------------------------
def log_vraisemblance(loi, issues, instances):
    """log P(y_1..t | x_1..t) d'une loi sans mémoire sur les issues (pour vérifier « valeur du membre ≥ vraisemblance du
    monde » dans les essais et les bancs)."""
    return [float(v) for v in sp.trajectoire_loi(loi, issues, instances)]


def description():
    """Provenance du nul pour les rapports : version, module et empreinte, nul v8 sous-jacent, classe non couverte."""
    return {"nul": VERSION_NUL, "module": "pole/nul_v9.py", "sha256": sha256_fichier(__file__), "nul_v8": nul_v8.description(),
            "paliers_mu": list(PALIERS_MU), "pas_max_par_palier": PAS_MAX_PAR_PALIER, "non_couvert": list(NON_COUVERT_V9)}
