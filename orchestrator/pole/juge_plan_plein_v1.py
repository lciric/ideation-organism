"""Juge à plan pleine épreuve, v1 (fichier neuf, R12 ; lecture du lot T0.5 à graines neuves, option (c) de Lazar).

Le juge gelé de la courbe de puissance (`demonstrations/puissance_juge_banque_v1.py`, `config_du_juge`) plafonne le plan à
120 instances : au-delà, le nombre d'épisodes d'épreuve ne change que le choix des 120 instances, jamais leur nombre. Le
juge à plan pleine épreuve prend, pour chaque fiche, **toutes** les instances d'épreuve qui portent une issue pour son
moniteur (le réservoir entier) ; tout le reste est inchangé.

Réglages communs aux deux bras (ceux de `config_du_juge` de la courbe, plus le nul v8) : sélection par pari, juge v1 sans
urne (ordre secret), nul des filles v2, nul d'archive **ajusté** (nul v8, `pole/nul_v8.py` : la configuration passe par
`configuration_nul_v8`, qui refuse tout réglage contraire), règle e-BH, α = 0,05, témoins jugés sans agents, politique de
redite « refus », graine du juge 20261027. Seule `taille_plan` diffère :
- bras « plein » : `taille_plan` = nombre d'instances de la partie d'épreuve de la banque (≥ tout réservoir de moniteur) ;
- bras « gelé » : `taille_plan` = 120 (le juge de la courbe, bras de comparaison).

Gardes (R5, essayées dans `essais/test_lecture_t05_graines_neuves_v1.py`) :
- `configuration_plan_plein` refuse (`PlanPleinRefuse`) une taille de plan plus petite que l'épreuve, une épreuve vide ;
- `verifier_plan_plein` refuse un engagement dont le plan n'est pas le réservoir entier (aucun repli silencieux) ;
- `verifier_archive_vide` refuse toute fiche qui recevrait des membres d'archive : la lecture est une génération unique,
  archive vide, fiches sans parents ; le nul v8 s'y réduit à la bibliothèque aveugle (plus le membre « connu » sous le
  monde informé) — la lecture ne mesure donc rien du nul v8 lui-même, et le dit.
"""

from .cycle import membres_de_l_archive
from .memoire import Memoire
from .nul_v8 import configuration_nul_v8, exiger_nul_v8
from .outils import sha256_fichier

GRAINE_DU_JUGE = 20261027  # celle de la courbe de puissance et des démonstrations
TAILLE_PLAN_GELE = 120
ALPHA = 0.05

# Réglages communs (hors nul v8, imposé par `configuration_nul_v8`, et hors taille du plan).
REGLAGES_COMMUNS = {"juge": "v1", "urne": False, "graine": GRAINE_DU_JUGE, "alpha": ALPHA, "taille_plan_filles": 120,
                    "instants_filles": 6, "part_calibrage": 12, "budget_generation_usd": 200.0, "concurrence": 4,
                    "multiplicite": "e-bh", "temoins_sans_agent": True, "propositions_par_generation": 0,
                    "exploration_developpement": False, "politique_redite": "refus"}


class PlanPleinRefuse(ValueError):
    """Juge « plein » demandé avec un plan plus petit que l'épreuve, ou plan d'un engagement qui n'est pas le réservoir."""


def _config(taille_plan):
    return exiger_nul_v8(configuration_nul_v8(taille_plan=int(taille_plan), **REGLAGES_COMMUNS))


def configuration_plan_plein(taille_epreuve, taille_plan=None):
    """Configuration du bras « plein ». `taille_epreuve` = nombre d'instances de la partie d'épreuve de la banque.
    `taille_plan` (facultatif) : refusé s'il est plus petit que l'épreuve (on ne réduit jamais le plan en silence)."""
    if not isinstance(taille_epreuve, int) or isinstance(taille_epreuve, bool) or taille_epreuve < 1:
        raise PlanPleinRefuse(f"épreuve vide ou taille invalide : {taille_epreuve!r}")
    if taille_plan is None:
        taille_plan = taille_epreuve
    if not isinstance(taille_plan, int) or isinstance(taille_plan, bool) or taille_plan < taille_epreuve:
        raise PlanPleinRefuse(f"plan pleine épreuve : taille_plan ({taille_plan!r}) plus petite que l'épreuve "
                              f"({taille_epreuve}) : refusé")
    return _config(taille_plan)


def configuration_plan_gele():
    """Configuration du bras « gelé » (plan de 120 instances, juge de la courbe de puissance, nul v8)."""
    return _config(TAILLE_PLAN_GELE)


def verifier_plan_plein(gele, reservoir):
    """Garde du bras « plein » : le plan gelé contient exactement les instances du réservoir (mêmes traits, même nombre)."""
    plan = gele.engagement["instances"]
    cle = lambda i: (tuple(i["z"]), i.get("g"))  # noqa: E731
    if len(plan) != len(reservoir) or sorted(map(cle, plan)) != sorted(map(cle, reservoir)):
        raise PlanPleinRefuse(f"plan de {len(plan)} instances pour un réservoir de {len(reservoir)} : le plan ne prend pas "
                              "toute l'épreuve")
    return gele


def verifier_archive_vide(fiche, config):
    """Garde : génération unique, archive vide — aucun membre d'archive (nul v8) pour aucune fiche ; rend []."""
    membres = membres_de_l_archive(fiche, Memoire(active=True, graine=0), config.nul_archive_ajuste, None)
    if membres:
        raise PlanPleinRefuse(f"membres d'archive inattendus pour {fiche.identifiant} : {[m.get('nom') for m in membres]}")
    return membres


def description():
    """Provenance pour les rapports."""
    import os
    from . import nul_v8
    return {"module": "pole/juge_plan_plein_v1.py", "sha256": sha256_fichier(os.path.abspath(__file__)),
            "nul_v8": nul_v8.description(), "reglages_communs": dict(REGLAGES_COMMUNS), "taille_plan_gele": TAILLE_PLAN_GELE}
