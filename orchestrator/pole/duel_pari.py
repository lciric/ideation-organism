"""Duel des trois bras de sélection sur une population à vérité connue, avec étalonnage A/A (simulation).

Bras 1 : sélecteur mécanique ex ante, sans appel de modèle — il choisit dans un réservoir les instances où p_h s'écarte
le plus (divergence de Kullback-Leibler) de la référence aveugle la meilleure sur la part d'entraînement ; promotion
par pari (W_T ≥ 1/α, nul 𝓛 plus la marginale d'entraînement).
Bras 2 : bras 1 plus un réfutateur simulé, d'une « autre famille ». Modèle de simulation : le réfutateur voit la part
d'entraînement (jamais la vérité ni les tirages frais) ; pour chaque sous-population il calcule la moyenne de
log p_h(x|z) − log q_ent(x) sur l'entraînement, retient la sous-population la plus défavorable à l'hypothèse et y
propose T/2 instances supplémentaires, celles où p_h s'écarte le plus de q_ent. Bras 2 voit donc 1,5 T instances.
Bras 3 (témoin faible) : T instances tirées au hasard ; promotion si le score moyen log p_h − log q_ent est positif.
A/A : le bras 1 deux fois, mêmes réglages, graines différentes : l'écart mesure le plancher de bruit.
"""

import math
import random

from . import selection_pari as sp
from .controles_pari import borne_wilson
from .outils import graine_derivee

TYPES = ("vraie", "fausse", "biais_sous_population", "couvert_net_vrai", "couvert_net_faux")
VERITE = {"vraie": True, "fausse": False, "biais_sous_population": False, "couvert_net_vrai": True,
          "couvert_net_faux": False}


def population(graine, par_type=40, k=3, dimension=2):
    rng = random.Random(graine_derivee(graine, "population-duel"))
    reference = sp.tirer_instances(rng, 2000, dimension)
    hypotheses = []
    for genre in TYPES:
        for i in range(par_type):
            loi = sp.loi_softmax_aleatoire(rng, k, dimension)
            pi = {"type": "fixe", "probas": sp.moyenne_loi(loi, reference)}
            pi1 = {"type": "fixe", "probas": sp.moyenne_loi(loi, [x for x in reference if x["g"] == 1])}
            h = {"identifiant": f"{genre}-{i:02d}", "type": genre, "verite": VERITE[genre], "loi": loi, "monde": loi}
            if genre == "fausse":
                h["monde"] = pi
            elif genre == "biais_sous_population":
                h["monde"] = {"type": "par_sous_population", "lois": {"0": loi, "1": pi1}}
            elif genre.startswith("couvert"):
                epsilon = 0.05 if i % 2 == 0 else 0.2
                h["epsilon"] = epsilon
                h["loi"] = {"type": "melange", "composantes": [pi, loi], "poids": [1 - epsilon, epsilon]}
                h["monde"] = loi if genre == "couvert_net_vrai" else pi
            hypotheses.append(h)
    return hypotheses


def _frequences(issues, k):
    return [(issues.count(i) + 0.5) / (len(issues) + 0.5 * k) for i in range(k)]


def _refutateur(loi, entrainement, issues_ent, q_ent, reservoir, nombre):
    moyennes = {}
    for g in sorted({x["g"] for x in entrainement}):
        ecarts = [math.log(sp.proba(loi, x, [], 0)[y]) - math.log(q_ent[y])
                  for x, y in zip(entrainement, issues_ent) if x["g"] == g]
        if ecarts:
            moyennes[g] = sum(ecarts) / len(ecarts)
    pire = min(moyennes, key=lambda g: (moyennes[g], g))
    return sp.selection_divergence(loi, [x for x in reservoir if x["g"] == pire], q_ent, nombre), pire


def evaluer_hypothese(h, bras, graine, tirages=120, reservoir=600, entrainement=100, alpha=0.05, k=3, dimension=2):
    rng = random.Random(graine_derivee(graine, "duel", bras, h["identifiant"]))
    pool = sp.tirer_instances(rng, reservoir, dimension)
    ent = sp.tirer_instances(rng, entrainement, dimension)
    issues_ent = []
    for t, x in enumerate(ent):
        issues_ent.append(sp.tirer_categorie(rng, sp.proba(h["monde"], x, issues_ent, t)))
    q_ent = _frequences(issues_ent, k)
    biblio = list(sp.BIBLIOTHEQUE_STANDARD) + [{"nom": "marginale_entrainement", "type": "fixe", "probas": q_ent}]
    if bras == 3:
        plan = rng.sample(pool, tirages)
    else:
        plan = sp.selection_divergence(h["loi"], pool, q_ent, tirages)
        if bras == 2:
            supplement, _ = _refutateur(h["loi"], ent, issues_ent, q_ent, pool, tirages // 2)
            plan = plan + supplement
            rng.shuffle(plan)
    gele = sp.geler_engagement(sp.construire_engagement(h["identifiant"], h["loi"], plan, k, alpha, biblio, "horizon"))
    frais = sp.tirer_frais(gele, h["monde"], graine_derivee(graine, "duel-frais", bras, h["identifiant"]))
    if bras == 3:
        score = sum(math.log(sp.proba(h["loi"], x, [], 0)[y]) - math.log(q_ent[y])
                    for x, y in zip(plan, frais["issues"])) / len(plan)
        return score > 0
    return sp.evaluer(gele, frais)["promue"]


def mesurer(hypotheses, bras, graine, **reglages):
    promues = {h["identifiant"]: evaluer_hypothese(h, bras, graine, **reglages) for h in hypotheses}
    fausses = [h for h in hypotheses if not h["verite"]]
    vraies = [h for h in hypotheses if h["verite"]]
    par_type = {}
    for genre in TYPES:
        groupe = [h for h in hypotheses if h["type"] == genre]
        par_type[genre] = sum(promues[h["identifiant"]] for h in groupe) / len(groupe)
    elim = sum(not promues[h["identifiant"]] for h in fausses)
    gard = sum(promues[h["identifiant"]] for h in vraies)
    return {"bras": bras, "fausses_eliminees": elim / len(fausses), "vraies_gardees": gard / len(vraies),
            "nombre_fausses": len(fausses), "nombre_vraies": len(vraies), "taux_de_promotion_par_type": par_type}


def executer_duel(graine=20261026, par_type=40, **reglages):
    hypotheses = population(graine, par_type)
    bras = {n: mesurer(hypotheses, n, graine_derivee(graine, "course", n), **reglages) for n in (1, 2, 3)}
    aa = mesurer(hypotheses, 1, graine_derivee(graine, "course-A/A"), **reglages)
    plancher = {m: round(abs(bras[1][m] - aa[m]), 9) for m in ("fausses_eliminees", "vraies_gardees")}
    ecart = {m: round(abs(bras[1][m] - bras[2][m]), 9) for m in ("fausses_eliminees", "vraies_gardees")}
    egal = all(ecart[m] <= plancher[m] for m in ecart)
    superflu = bras[1]["fausses_eliminees"] >= 0.95 and egal
    return {"parametres": dict(graine_maitresse=graine, hypotheses_par_type=par_type, **reglages),
            "bras": bras, "aa": aa, "plancher_de_bruit_aa": plancher, "ecart_bras1_bras2": ecart,
            "erreur_type_binomiale_fausses": math.sqrt(0.25 / bras[1]["nombre_fausses"]),
            "regle_d_arret": {"bras1_elimine_95": bras[1]["fausses_eliminees"] >= 0.95,
                              "bras1_egal_bras2_au_bruit_pres": egal, "refutateur_superflu": superflu},
            "borne_haute_95_promotion_fausses_bras1": borne_wilson(
                round((1 - bras[1]["fausses_eliminees"]) * bras[1]["nombre_fausses"]), bras[1]["nombre_fausses"])}


def rapport_markdown(d, horodatage):
    b, p, r = d["bras"], d["parametres"], d["regle_d_arret"]
    lignes = ["# Duel des trois bras de sélection (simulation à vérité connue)\n",
              f"Horodatage : {horodatage['valeur']} ({horodatage['source']}). Graine maîtresse {p['graine_maitresse']} ; "
              f"{p['hypotheses_par_type']} hypothèses par type ({', '.join(TYPES)}).",
              "Simulation seulement ; le réfutateur est un modèle simulé décrit dans `pole/duel_pari.py`.\n",
              "| bras | fausses éliminées | vraies gardées | " + " | ".join(f"promues : {t}" for t in TYPES) + " |",
              "|---|---|---|" + "---|" * len(TYPES)]
    for nom, m in (("1 mécanique", b[1]), ("2 mécanique + réfutateur", b[2]), ("3 score moyen", b[3]), ("1 bis (A/A)", d["aa"])):
        lignes.append(f"| {nom} | {m['fausses_eliminees']:.3f} | {m['vraies_gardees']:.3f} | "
                      + " | ".join(f"{m['taux_de_promotion_par_type'][t]:.3f}" for t in TYPES) + " |")
    lignes.append(f"\nPlancher de bruit A/A : {d['plancher_de_bruit_aa']} ; écart bras 1 – bras 2 : {d['ecart_bras1_bras2']}.")
    lignes.append(f"Règle d'arrêt : bras 1 élimine ≥ 95 % des fausses : {r['bras1_elimine_95']} ; bras 1 égale le bras 2 au "
                  f"bruit près : {r['bras1_egal_bras2_au_bruit_pres']} → réfutateur superflu : **{r['refutateur_superflu']}** "
                  "(en simulation, avec ce modèle de réfutateur ; un plancher estimé sur une seule paire A/A est fragile).")
    return "\n".join(lignes) + "\n"
