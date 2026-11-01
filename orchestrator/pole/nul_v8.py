"""Nul v8 du juge : le nul d'archive **ajusté** devient le seul nul du juge, partout (décision du directeur, 1er novembre 2026).

Fichier neuf (R12) : aucun fichier existant n'est modifié. Ce module
- construit la configuration du juge (`ConfigGeneration` de `pole/cycle.py`) avec le nul v8 imposé
  (`configuration_nul_v8`) et **refuse**, par l'exception nommée `NulV8Refuse`, toute configuration qui ne le porte pas
  (`exiger_nul_v8`) — aucun repli silencieux vers le nul de v7 ;
- rend les membres d'archive du nul v8 aux bancs qui construisent leur bibliothèque eux-mêmes (`membres_archive_v8`), par
  la fonction même du juge de production, `cycle.membres_de_l_archive(..., ajuste=True)`, jamais par une copie ; la garde
  `exiger_membres_ajustes` vérifie que chaque membre ajusté attendu est présent et intact.

Nul v8 d'une fiche (non témoin) = bibliothèque aveugle du juge v1 + nul des filles v2 pour une fille (parents seuls, formes
de v0, membres ajustés sur les parents) + nul d'archive (chaque survivante de même espace, seule et mélangée à l'uniforme sur
une grille) + **membres ajustés sur l'archive** :
- « ajuste_lineaire:archive » : mise en commun linéaire de toutes les lois connues (les deux parents d'une fille, les
  survivantes) et de toute loi aveugle fixe, Σ_j π_j·L_j + Σ_k ρ_k·δ_k (poids sur le simplexe, δ_k la loi certaine de
  l'issue k), au maximum de vraisemblance ;
- « ajuste_log:archive:<survivante> » : chaque survivante tempérée et inclinée, p(k) ∝ S(k)^a·exp(β_k), au maximum de
  vraisemblance ;
lus aux instants fixés d'avance sous l'empreinte de l'engagement, pour toute fiche (évaluateur du nul des filles v2).
Archive vide et fiche sans parent : rien de connu à ajuster, le nul v8 se réduit à la bibliothèque aveugle (comme v7).
Les témoins restent jugés sans membres d'archive (`cycle.Generation.geler`, inchangé).
Portée de « partout » : les entrées v8 (démonstrations v8, banc v8) et tout code qui construit son juge par
`configuration_nul_v8` ou le passe à `exiger_nul_v8`. La ligne de commande de v7 (`pole/pole.py`, commitée, inchangée) fait
déjà du nul ajusté son défaut mais accepte encore `--sans-nul-archive` et `--sans-nul-archive-ajuste` : une entrée v8 qui
les refuse reste à écrire.

Argument de validité (pourquoi l'erreur de première espèce est conservée).
1. Forme de la richesse, la même en v7 et en v8 : log W_t = log q(y_1..t) − max_{m ∈ 𝓝} log p̂_m(y_1..t), où q est la loi
   engagée par la fiche — gelée **avant** le tirage des issues fraîches (le gel précède les tirages, dont la graine dérive de
   l'empreinte de l'engagement gelé : `selection_pari.tirer_frais`) — et où chaque membre ajusté entre au dénominateur à son
   maximum de vraisemblance, plus sa marge d'optimisation.
2. Monotonie. La bibliothèque v8 contient celle de v7 (𝓝₈ ⊇ 𝓝₇) : pour une même suite d'issues, max sur 𝓝₈ ≥ max sur 𝓝₇,
   donc W_t(v8) ≤ W_t(v7) à chaque instant ; la lecture aux instants fixés ne retient qu'une partie des instants de la
   lecture continue ; la règle de marge des filles (gain moyen ≥ 2·δ₀ sur la meilleure enveloppe ; tous les membres ajustés
   comptent parmi les enveloppes) ne fait que retirer des promotions. **Élargir la bibliothèque de nuls ajustée sur les
   tirages frais ne peut que réduire la richesse W_t** : trajectoire par trajectoire, toute promotion sous v8 en est une
   sous v7. Le taux d'erreur de première espèce est donc conservé pour toute loi déjà couverte par v7, et **seul le prix en
   puissance est à mesurer** (le dénominateur monte aussi sous l'alternative) — objet du préenregistrement
   `prereg/preenregistrement-validation-nul-v8-v1.md`.
3. Extension aux familles ajoutées (inférence universelle). Si la loi du monde P (sachant l'instance) appartient à une
   famille de 𝓝₈, le maximum de vraisemblance de cette famille domine P(y_1..t) à chaque instant de lecture, donc
   W_t(v8) ≤ q(y_1..t) / P(y_1..t), rapport de vraisemblance qui, à plan d'instances et ordre d'exécution fixés, est une
   martingale positive d'espérance 1 sous P ; l'inégalité de Ville borne par α la probabilité d'une promotion
   (W ≥ 1/α à l'un des instants lus). C'est l'argument du rapport de vraisemblance scindé de l'inférence universelle
   (Wasserman, Ramdas et Balakrishnan, 2020, « Universal inference », PNAS).
4. **Sur quelles données le nul est ajusté, et la condition de l'inférence universelle.** Chaque membre ajusté
   (« ajuste_lineaire:archive », « ajuste_log:archive:<survivante> », et pour une fille les membres ajustés du nul des
   filles v2) est ajusté, à chaque instant de lecture t, **sur les t premières issues de la part d'évaluation des tirages
   frais — exactement celles sur lesquelles le numérateur est évalué à cet instant** (`nul_filles_v2.evaluer_v2` : le cache
   des probabilités est construit sur `issues[c:]`, et `valeurs_ajustees` ajuste sur ses t premières lignes). Il n'y a
   **pas de part séparée pour le nul** : la part de calibrage d'une fille (ses c premiers tirages) ne sert qu'au poids
   calibré du membre « melange_parents » des formes de v0 (`selection_pari.calibrer`), jamais aux membres ajustés. Ce n'est
   pas une entorse à la condition de l'inférence universelle : dans le rapport scindé, le maximum de vraisemblance du nul
   est calculé **sur la part même où le rapport est évalué** — c'est ce qui le fait dominer la vraisemblance de la vraie
   loi —, et c'est l'**alternative**, au numérateur, qui doit être estimée hors de cette part. Ici le numérateur est la loi
   gelée avant les tirages : la « part séparée » de l'alternative est tout ce qui a précédé le gel. Une loi engagée qui lit
   l'historique des issues (« moyenne_glissante », « sans_remise ») ou le pari à fraction (mélange avec la marginale en ligne
   des issues précédentes) reste prévisible — chaque facteur ne dépend que des issues passées — : c'est la variante
   séquentielle (estimateur courant au numérateur), valide aussi. **La condition est respectée.**
5. Réserves (dites, non cachées) :
   - la garantie de Ville ne vaut que si la loi du monde est dans une famille du nul (ou dominée par lui) ; pour un
     tricheur de la classe couverte, le refus est plus fort : sa loi est elle-même un membre, donc W_t ≤ 1 à chaque instant
     quel que soit le monde (classe linéaire : par construction, aux arrondis flottants près) ;
   - marges d'optimisation : l'écart de Frank-Wolfe du membre linéaire est une borne exacte (problème concave sur le
     simplexe) ; sans convergence, un membre log-linéaire prend la borne triviale 0, exacte aussi (une log-vraisemblance est
     ≤ 0), mais qui interdit toute promotion à cet instant (prix en puissance) ; **convergé, il ajoute le décrément de
     Newton au carré (≤ 0,25), borne de l'écart à l'optimum démontrée pour les fonctions autoconcordantes — ce que la
     log-vraisemblance du logit multinomial n'est pas au sens strict (elle l'est au sens « généralisé ») : pour les membres
     log-linéaires, « valeur calculée ≥ vrai maximum » tient au second ordre près de l'optimum, sans preuve** ; paramètres
     bornés à [−60 ; 60] : la famille log-linéaire est celle de cette boîte ;
   - le nul d'archive d'une fiche ne contient que les survivantes de son espace (moniteur, nombre d'issues, dimension), hors
     elle-même et ses parents ; les témoins n'en reçoivent jamais (`cycle.Generation.geler`) ;
   - la garantie est par fiche ; la multiplicité entre fiches reste celle de la règle e-BH, inchangée.

Classe d'attaque **couverte** (la loi du tricheur est un membre du nul v8) :
- recombinaisons **linéaires** de lois connues : chaque loi connue seule, tout mélange de lois connues (parents d'une
  fille, survivantes), tout mélange de lois connues avec une loi aveugle fixe quelconque (indépendante de l'instance) —
  banc : T01, T02, T03u, T03b, T04, T09l, T17s, nul exact ;
- recombinaisons **log-linéaires** d'**une** loi connue : chaque survivante, et chaque parent d'une fille, tempéré et
  incliné (S(k)^a·exp(β_k), donc aussi son produit par une loi aveugle fixe) — banc : T05s, T09g ; pour une fille, en plus,
  le produit des deux parents tempéré et incliné (A(k)^a·B(k)^b·exp(β_k), membre « ajuste_log:AB » du nul des filles v2) et
  les formes de v0 (enveloppe harmonique, si/sinon des deux parents sur les partitions déclarées).
Classe **non couverte** (dite, non fermée : l'argument ne la borne pas, seul le banc la mesure) :
- recombinaisons **par morceaux** (si/sinon par sous-population ou par seuil d'un trait) qui mettent en jeu une survivante,
  et plus généralement des poids de mélange qui dépendent de l'instance ;
- **produits de plus de deux lois**, et produits de deux lois autres que les deux parents d'une fille (deux survivantes, un
  parent et une survivante) ;
- compositions d'étapes (mélange aveugle, puis puissance, puis inclinaison : T07, mesurée seulement) et toute autre
  déformation d'une loi connue (oscillation non monotone : T12 ; question de nouveauté quand le monde est cette déformation) ;
- lois hors de l'archive : témoins, fiches d'un autre espace (nombre d'issues, dimension, moniteur), lois inconnues du pôle.
"""

from types import SimpleNamespace

from .cycle import ConfigGeneration, membres_de_l_archive
from .memoire import Memoire
from .outils import sha256_fichier

VERSION_NUL = "nul-v8"
# Réglages du juge que le nul v8 impose ; toute valeur contraire est refusée (jamais remplacée en silence).
REGLAGES_NUL_V8 = {"selection": "pari", "nul_filles": "v2", "nul_archive": True, "nul_archive_ajuste": True}
MEMBRE_LINEAIRE = "ajuste_lineaire:archive"
FICHE_JUGEE = "__fiche-jugee-nul-v8__"  # identifiant de la fiche jugée dans la mémoire construite par `membres_archive_v8`


class NulV8Refuse(ValueError):
    """Juge sans le nul v8 : configuration sans nul ajusté (ou réglage du nul contraire), membre ajusté absent ou altéré."""


def _conforme(valeur, attendu):
    return type(valeur) is type(attendu) and valeur == attendu  # 1 n'est pas True, « V2 » n'est pas « v2 »


def _ecarts(lire, presentes):
    return {cle: lire(cle) for cle, attendu in REGLAGES_NUL_V8.items() if cle in presentes and not _conforme(lire(cle), attendu)}


def configuration_nul_v8(**reglages):
    """`ConfigGeneration` du juge sous le nul v8 : les autres réglages passent tels quels ; ceux du nul sont imposés.

    Un réglage du nul donné avec une autre valeur (par exemple `nul_archive_ajuste=False`, `nul_archive=False`,
    `nul_filles="v0"` ou `"v2_souple"`, `selection="seuil"`) lève `NulV8Refuse` : on ne construit pas le juge sans le nul
    ajusté, et on ne corrige pas la demande en silence. La configuration rendue est validée puis repassée à la garde.
    """
    ecarts = _ecarts(reglages.get, reglages)
    if ecarts:
        raise NulV8Refuse(f"nul v8 : réglage(s) contraire(s) au nul ajusté refusé(s) : {ecarts} (imposés : {REGLAGES_NUL_V8})")
    config = ConfigGeneration(**dict(reglages, **REGLAGES_NUL_V8)).valider()
    return exiger_nul_v8(config)


def exiger_nul_v8(config):
    """Garde : rend `config` si elle porte le nul v8, lève `NulV8Refuse` sinon (aucun repli)."""
    if not isinstance(config, ConfigGeneration):
        raise NulV8Refuse(f"nul v8 : une ConfigGeneration est attendue, reçu {type(config).__name__}")
    ecarts = _ecarts(lambda cle: getattr(config, cle, None), REGLAGES_NUL_V8)
    if ecarts:
        raise NulV8Refuse(f"nul v8 : juge configuré sans le nul ajusté : {ecarts} (imposés : {REGLAGES_NUL_V8})")
    return config.valider()


def membres_archive_v8(survivantes, lois_parents=None, nombre_issues=3, dimension=2, moniteur=None):
    """Membres d'archive du nul v8 pour une fiche jugée : fille si `lois_parents` donne deux lois, sans parent sinon.

    `survivantes` : {identifiant: loi} des survivantes de l'archive, toutes dans l'espace (nombre d'issues, dimension,
    moniteur) de la fiche. Les membres sont ceux du juge de production : `cycle.membres_de_l_archive` avec `ajuste=True`,
    sur une mémoire où chaque survivante est indexée « survit » (une survivante qui porte le nom d'un parent en est exclue,
    comme en production). La garde `exiger_membres_ajustes` vérifie le résultat.
    """
    lois_parents = dict(lois_parents or {})
    if len(lois_parents) not in (0, 2):
        raise ValueError("lois_parents : aucune (fiche sans parent) ou exactement deux (fille)")
    if FICHE_JUGEE in survivantes:
        raise ValueError(f"identifiant de survivante réservé : {FICHE_JUGEE}")
    espace = {"nombre_issues": int(nombre_issues), "dimension": int(dimension), "moniteur": moniteur}
    memoire = Memoire(active=True, graine=0)
    for ident in sorted(survivantes):
        memoire.index[ident] = {"statut": "survit", "temoin": None, "loi_predictive": survivantes[ident],
                                "espace_instances": dict(espace)}
    fiche = SimpleNamespace(identifiant=FICHE_JUGEE, parents=sorted(lois_parents), espace_instances=dict(espace))
    membres = membres_de_l_archive(fiche, memoire, ajuste=True, lois_parents=lois_parents or None)
    return exiger_membres_ajustes(membres, survivantes, lois_parents)


def exiger_membres_ajustes(membres, survivantes, lois_parents=None):
    """Garde : chaque survivante retenue (hors parents) a ses trois membres (« archive: », « archive_couvert: »,
    « ajuste_log:archive: » sur sa seule loi) et, dès qu'une loi est connue, la mise en commun « ajuste_lineaire:archive »
    porte exactement les lois connues (parents triés, puis survivantes triées). Lève `NulV8Refuse` sinon ; rend `membres`."""
    parents = dict(lois_parents or {})
    retenues = [i for i in sorted(survivantes) if i not in parents]
    par_nom = {}
    for m in membres:
        par_nom.setdefault(m.get("nom"), []).append(m)
    defauts = []
    for ident in retenues:
        for prefixe in ("archive", "archive_couvert"):
            if len(par_nom.get(f"{prefixe}:{ident}", ())) != 1:
                defauts.append(f"{prefixe}:{ident}")
        log = par_nom.get(f"ajuste_log:archive:{ident}", ())
        if len(log) != 1 or log[0].get("type") != "ajuste_log" or log[0].get("lois") != [survivantes[ident]]:
            defauts.append(f"ajuste_log:archive:{ident}")
    connues = [parents[n] for n in sorted(parents)] + [survivantes[i] for i in retenues]
    lineaire = par_nom.get(MEMBRE_LINEAIRE, ())
    if connues and (len(lineaire) != 1 or lineaire[0].get("type") != "ajuste_lineaire" or lineaire[0].get("lois") != connues):
        defauts.append(MEMBRE_LINEAIRE)
    if not connues and lineaire:
        defauts.append(f"{MEMBRE_LINEAIRE} sans loi connue")
    if defauts:
        raise NulV8Refuse(f"nul v8 : membre(s) ajusté(s) absent(s) ou altéré(s) : {', '.join(defauts)}")
    return membres


def description():
    """Provenance du nul pour les rapports : version, réglages imposés, empreinte de ce module."""
    return {"nul": VERSION_NUL, "module": "pole/nul_v8.py", "sha256": sha256_fichier(__file__),
            "reglages_imposes": dict(REGLAGES_NUL_V8)}
