"""Porte PACE contre pari apparié contre acceptation gloutonne — course simulée sur processeur, zéro dépense, aucun agent ;
bras de référence du juge figé ; jamais une sélection d'agent (N-053) ; exploratoire, non préenregistré.

Monde (`pole.porte_pace.simuler_suite`, réglages [INFÉRÉ] dits dans le module) : une référence fixe d'exactitude 0,35, des
suites de m = 20 candidats notés sur le même jeu de développement réutilisé (n = 40 comme dans PACE, p.6 ; puis 120) et
sur le même jeu d'audit (n = 120, p.6), qui n'étiquette que les décisions. Quatre régimes :

- « nulle » : tous les candidats ont l'exactitude de la référence ;
- « gain » : un témoin planté à +0,35 (contrôle positif, p.6), les autres à un gain tiré dans [−0,10 ; 0] (aucun meilleur) ;
- « honnête avec garde » (version 40, CL39-10) : comme « gain », mais tous les candidats portent la garde δ = 0,05 avec des
  écarts de faux positifs d'espérance nulle (P(±1) = 0,1) : cas sain de la garde, dont la ligne mesure la **puissance** ;
- « tricheur » : comme « honnête avec garde », mais le témoin tire en plus des faux positifs (excès moyen 0,15 > δ) ; seule
  la garde de notre bras le voit.

Après chaque table, une ligne « puissance de la garde » met côte à côte le témoin honnête validé par notre bras et le
tricheur refusé : le refus seul ne prouve pas que la garde discrimine (lecture dans la docstring de `pole/porte_pace.py`).

Bras : porte PACE (λ = 0,5, seuil 1/α, par candidat, p.4) ; notre pari apparié (mélange sur Λ, arrêt à m/α, e-BH sur la
suite, garde δ quand elle est fournie) ; glouton (score de développement strictement supérieur). Une ligne par régime et
par bras ; compteurs sommés sur les répétitions.

Usage : python3 -B demonstrations/porte_pace_v1.py [--graine 20261029] [--repetitions 200] [--m 20] [--n-dev 40 120]
"""

import argparse
import os
import statistics
import sys
import time

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)

import random  # noqa: E402

from pole import porte_pace as pp  # noqa: E402

REGIMES = pp.REGIMES  # ("nulle", "gain", "honnete_garde", "tricheur")
NOMS = {"pace": "PACE", "pari_apparie": "pari apparié", "glouton": "glouton"}
NOMS_REGIMES = {"nulle": "nulle", "gain": "gain", "honnete_garde": "honnête avec garde", "tricheur": "tricheur"}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--graine", type=int, default=20261029)
    p.add_argument("--repetitions", type=int, default=200)
    p.add_argument("--m", type=int, default=20)
    p.add_argument("--n-dev", type=int, nargs="+", default=[40, 120])
    a = p.parse_args(argv)
    debut = time.time()
    _, methode = pp.graines(a.graine, 1)
    print(f"Porte PACE, bras de référence — graine {a.graine} ({methode}), {a.repetitions} suites par ligne, "
          f"m = {a.m} candidats, audit n = 120, référence 0,35, ρ = 0,5, développement réutilisé")
    print(f"{pp.USAGE}")
    entete = (f"{'régime':<18} {'n_dev':>5} {'bras':<13} {'valid./suite':>12} {'fausses/suite':>13} {'suites≥1 fausse':>15} "
              f"{'témoin validé':>13} {'faux audit':>10} {'nuis. audit':>11} {'coût/cand.':>10} {'arrêt méd.':>10}")
    lignes = []
    for i_n, n_dev in enumerate(a.n_dev):
        print()
        print(entete)
        print("-" * len(entete))
        par_regime = {}
        for regime in REGIMES:
            i_r = ("nulle", "gain", "tricheur", "honnete_garde").index(regime)  # graines d'avant la v40 inchangées
            graines, _ = pp.graines([a.graine, i_n, i_r], a.repetitions)
            res = [pp.comparer(pp.simuler_suite(random.Random(g), regime, m=a.m, n_dev=n_dev)) for g in graines]
            t = pp.agreger(res)
            for b in pp.BRAS:
                k = t[b]
                s = k["suites"]
                ligne = {"regime": regime, "n_dev": n_dev, "bras": b, "validations_par_suite": k["validations"] / s,
                         "fausses_verite_par_suite": k["fausses_verite"] / s, "suites_avec_fausse": k["suites_avec_fausse"] / s,
                         "temoin_valide": (k["temoins_valides"] / k["temoins"]) if k["temoins"] else None,
                         "fausses_audit": k["fausses_audit"], "nuisibles_audit": k["nuisibles_audit"],
                         "cout_par_candidat": k["cout_total"] / (s * a.m),
                         "arret_median": statistics.median(k["etapes"]) if k["etapes"] else None}
                lignes.append(ligne)
                par_regime[(regime, b)] = ligne
                tv = "—" if ligne["temoin_valide"] is None else f"{100 * ligne['temoin_valide']:.0f} %"
                am = "—" if ligne["arret_median"] is None else f"{ligne['arret_median']:.0f}"
                print(f"{NOMS_REGIMES[regime]:<18} {n_dev:>5} {NOMS[b]:<13} {ligne['validations_par_suite']:>12.3f} "
                      f"{ligne['fausses_verite_par_suite']:>13.3f} {100 * ligne['suites_avec_fausse']:>14.1f}% {tv:>13} "
                      f"{ligne['fausses_audit']:>10} {ligne['nuisibles_audit']:>11} {ligne['cout_par_candidat']:>10.1f} {am:>10}")
        h = par_regime[("honnete_garde", "pari_apparie")]["temoin_valide"]
        t = par_regime[("tricheur", "pari_apparie")]["temoin_valide"]
        print(f"puissance de la garde δ = 0,05 (notre bras, n_dev = {n_dev}) : témoin honnête validé {100 * h:.1f} % des suites"
              f" ; tricheur refusé {100 * (1 - t):.1f} % — PACE valide le tricheur "
              f"{100 * par_regime[('tricheur', 'pace')]['temoin_valide']:.1f} %")
    print()
    print("Lecture : « fausses » = validations de candidats de gain réel ≤ 0 (vérité du simulateur) ; « faux audit » /"
          " « nuis. audit » = validations étiquetées ≤ 0 / < 0 par le jeu d'audit (p.6), sommées sur les suites ;"
          " « suites≥1 fausse » = taux de famille observé (PACE ne le borne pas, p.5 ; notre bras le borne par e-BH)."
          " La garde δ = 0,05 a peu de puissance à ces tailles : le témoin honnête n'est qu'à 0,05 du nul de la garde contre"
          " un écart-type de 0,45 par unité, et même sans bruit elle ne peut franchir m/α = 400 avant 166 unités ; il lui"
          " faut de l'ordre de mille unités honnêtes (docstring de pole/porte_pace.py).")
    print(f"Durée : {time.time() - debut:.1f} s")
    return lignes


if __name__ == "__main__":
    main()
