"""Banc de tricheurs contre le juge de v7 (juge v1 sans urne, nul des filles v2, nul d'archive, règle e-BH) — exploratoire.

Lignée conv-audit, 27 octobre 2026, écrit de 15:35 à 15:37 UTC (l'en-tête de la course de 15:38 portait par erreur
« 15:55 », corrigé après). Exploratoire (R-546) : **non décisif** ; la validation
décisive du juge suivra la règle d'arrêt commune du banc (au moins 1 000 répétitions par tricheur, graine neuve au
scellement, marge ε fixée avant, bornes avec correction de Holm), dans un préenregistrement scellé et contre-lu. Banc :
`docs/notes/pole-scientifique-automatique/banc-tricheurs-v1.md` sur `main` (`e0930d86…`), lignes T01 à T27 (partie 1).

Monde de chaque tricheur : sa propre loi (le pire cas : le tricheur a raison, mais n'apporte rien de neuf au-delà des
lois déjà connues : parents A, B ; survivantes de l'archive S1, S2). K = 3 issues, 2 traits, 2 sous-populations ; filles :
50 tirages de calibrage puis 200 d'évaluation, lecture aux instants 25, 50, …, 200, marge 2δ₀ = 0,02 ; fiches sans parent :
200 tirages, lecture continue (nul « v7 ») ou aux instants (nul « candidat ») ; ordre d'exécution secret partout.

Nuls comparés :
- « v7 » (aujourd'hui) : bibliothèque aveugle sans urne + marginale d'entraînement + nul d'archive (chaque survivante
  seule, et mélangée à l'uniforme sur une grille) ; pour une fille, en plus, le nul des filles v2 (formes de v0, membres
  ajustés sur les parents) ;
- « candidat » (`--nul-archive-ajuste`) : « v7 » + mise en commun linéaire ajustée de toutes les lois connues (parents et
  survivantes) avec toute loi aveugle fixe + chaque survivante tempérée et inclinée, ajustées ;
- « v1 » (artefact seulement) : nul des filles de v1 (formes de v0, sans membres ajustés).

Lignes (rôle ; lecture fixée avant l'exécution) :
- fatales sous « candidat » (taux ≤ α ; sous « v7 », mesurées, ouvertes si > α) : T02 copie cachée (½A + ½S1, fille) ;
  T03b survivante + loi aveugle tirée de Dirichlet (fiche sans parent) ; T04 mélange de deux survivantes (sans parent) ;
  T05s survivante tempérée et inclinée (sans parent) ;
- fatales sous « v7 » (taux ≤ α) : T01 parent + loi aveugle ; T03u survivante + uniforme ; T17s copie renommée d'une
  survivante ; T09g parent à puissance 6 ; T09l parent + loi aveugle à λ = 0,97 ; T12a parent déformé hors famille
  (oscillation) quand le monde est le parent (Ville : la vérité est au nul) ; nul exact (fille = parent A, monde A) ;
- mesurées (pas de seuil, lues) : T07 composition (mélange aveugle, puis puissance, puis inclinaison) sous « v7 » et
  « candidat » ; T12b parent déformé hors famille quand le monde est cette déformation (question de nouveauté, pas de
  validité : la fiche dit vrai) ;
- artefact requis (> α, sinon le banc n'a pas de dents) : T01 sous le nul « v1 » ;
- puissance (≥ 0,90 sous « v7 » et sous « candidat » ; perte du candidat ≤ 0,05) : fille neuve (A sur la
  sous-population 0, loi neuve ailleurs) ; fiche neuve sans parent (loi neuve, monde neuf) ;
- multiplicité, règle e-BH sur une génération (taux de l'événement « au moins une promue » ≤ α ; par fiche sans
  correction : mesuré) : T14 rafale de 10 variantes d'une loi fausse (monde aveugle) ; T15 20 copies d'une loi fausse ;
- puissance sous e-BH quand m grandit (lue) : T16, une fiche neuve vraie parmi m − 1 fiches fausses, m ∈ {1, 10, 40} ;
  v2 du banc (16:30 UTC, après la lecture v1 qui notait T16 « mal dimensionné ») : T16f, la même avec un effet faible (poids
  de la loi neuve × 0,3), m ∈ {1, 10, 40} — lecture : baisse de puissance avec m sous e-BH, rapportée (le déni de service).
Les tricheurs T11, T13, T24 à T26 sont sans objet ou fermés par construction dans les mondes de v7 ; T21 à T23 ne sont pas
décrits ; T14 à T16 portent sur la règle e-BH ; la partie 2 (amont du juge) n'est pas jouée ici. Voir la lecture.

Usage : python -I -B demonstrations/banc_tricheurs_v7.py DOSSIER_NEUF --graine G [--repetitions 200] [--processus 4]
        [--lignes nom1,nom2]
"""

import argparse
import concurrent.futures
import json
import math
import os
import random
import sys
import time

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)

from pole import nul_filles_v2 as nf  # noqa: E402
from pole import selection_pari as sp  # noqa: E402
from pole.controles_pari import _dirichlet, _fixe, _frequences, borne_wilson  # noqa: E402
from pole.cycle import appliquer_multiplicite, instants_reguliers  # noqa: E402
from pole.outils import ecrire_json_scelle, graine_derivee, manifeste  # noqa: E402

K, DIM, TIRAGES, CALIBRAGE, ALPHA, DELTA0 = 3, 2, 200, 50, 0.05, 0.01
INSTANTS = nf.INSTANTS_PAR_DEFAUT
UNIFORME = [1.0] * K


def _monde_lois(rng):
    a, b, s1, s2, neuve = (sp.loi_softmax_aleatoire(rng, K, DIM) for _ in range(5))
    return {"A": a, "B": b, "S1": s1, "S2": s2, "N": neuve}


def _transformee(base, **etapes):
    loi = {"type": "transformee", "base": base}
    loi.update({k: v for k, v in etapes.items() if v is not None})
    return loi


def scenario(nom, rng):
    """(genre, loi de la fiche, loi du monde, lois) ; genre « fille » (parents A, B) ou « fraiche » (sans parent)."""
    L = _monde_lois(rng)
    A, S1, S2, N = L["A"], L["S1"], L["S2"], L["N"]
    q = _dirichlet(rng, K, 1.0)
    if nom == "T01":
        loi = {"type": "melange", "composantes": [A, _fixe(q)], "poids": [0.5, 0.5]}
        return "fille", loi, loi, L
    if nom == "T02":
        loi = {"type": "melange", "composantes": [A, S1], "poids": [0.5, 0.5]}
        return "fille", loi, loi, L
    if nom == "T03u":
        loi = {"type": "melange", "composantes": [S1, _fixe(UNIFORME)], "poids": [0.5, 0.5]}
        return "fraiche", loi, loi, L
    if nom == "T03b":
        loi = {"type": "melange", "composantes": [S1, _fixe(q)], "poids": [0.5, 0.5]}
        return "fraiche", loi, loi, L
    if nom == "T04":
        pi = rng.uniform(0.3, 0.7)
        loi = {"type": "melange", "composantes": [S1, S2], "poids": [pi, 1 - pi]}
        return "fraiche", loi, loi, L
    if nom == "T05s":
        loi = _transformee(S1, puissance=rng.uniform(0.5, 1.5), inclinaison=[0.0] + [rng.gauss(0.0, 0.7) for _ in range(K - 1)])
        return "fraiche", loi, loi, L
    if nom == "T07":
        loi = _transformee(A, melange_aveugle={"lambda": 0.5, "probas": q}, puissance=rng.uniform(0.5, 1.5),
                           inclinaison=[0.0] + [rng.gauss(0.0, 0.7) for _ in range(K - 1)])
        return "fille", loi, loi, L
    if nom == "T09g":
        loi = _transformee(A, puissance=6.0)
        return "fille", loi, loi, L
    if nom == "T09l":
        loi = {"type": "melange", "composantes": [A, _fixe(q)], "poids": [0.03, 0.97]}
        return "fille", loi, loi, L
    if nom in ("T12a", "T12b"):
        osc = {"amplitude": 1.5, "frequence": 8.0, "trait": rng.randrange(DIM), "issue": rng.randrange(K),
               "phase": rng.uniform(0, 2 * math.pi)}
        loi = _transformee(A, oscillation=osc)
        return "fille", loi, (A if nom == "T12a" else loi), L
    if nom == "T17s":
        return "fraiche", S1, S1, L
    if nom == "nul_exact":
        return "fille", A, A, L
    if nom == "fille_neuve":
        loi = {"type": "si_sinon", "condition": {"sous_population": 0}, "si": A, "sinon": N}
        monde = {"type": "par_sous_population", "lois": {"0": A, "1": N}}
        return "fille", loi, monde, L
    if nom == "fraiche_neuve":
        return "fraiche", N, N, L
    raise ValueError(nom)


def _marginale_entrainement(rng, monde):
    entrainement = sp.tirer_instances(rng, 100, DIM)
    return _frequences([sp.tirer_categorie(rng, sp.proba(monde, x, [], 0)) for x in entrainement], K)


def membres_archive(L, nul, parents=None):
    membres = []
    for nom in ("S1", "S2"):
        membres.append({"nom": f"archive:{nom}", "type": "loi", "loi": L[nom]})
        membres.append({"nom": f"archive_couvert:{nom}", "type": "melange_lois", "lois": [L[nom], _fixe(UNIFORME)],
                        "grille": list(sp.GRILLE_MELANGE)})
        if nul == "candidat":
            membres.append({"nom": f"ajuste_log:archive:{nom}", "type": "ajuste_log", "lois": [L[nom]]})
    if nul == "candidat":
        lois = [parents[n] for n in sorted(parents or {})] + [L["S1"], L["S2"]]
        membres.append({"nom": "ajuste_lineaire:archive", "type": "ajuste_lineaire", "lois": lois})
    return membres


def juger(genre, loi, monde, L, nul, rng, graine, cle, r):
    """Évaluation d'une fiche comme dans v7 (ordre secret, tirages frais du monde) ; rend le résultat de l'évaluateur."""
    q_ent = _marginale_entrainement(rng, monde)
    standard = list(sp.BIBLIOTHEQUE_STANDARD) + [{"nom": "marginale_entrainement", "type": "fixe", "probas": q_ent}]
    noyau = graine_derivee(graine, cle, r, "noyau")
    if genre == "fille":
        parents = {"A": L["A"], "B": L["B"]}
        instances = sp.tirer_instances(rng, CALIBRAGE + TIRAGES, DIM)
        biblio = sp.bibliotheque_fille(parents, DIM, standard, q_ent, nombre_issues=K)
        if nul in ("v7", "candidat"):
            biblio = biblio + nf.membres_de_variante("v2", parents) + membres_archive(L, nul, parents)
        gele = sp.geler_engagement(nf.construire_engagement_v2("fille", loi, instances, K, ALPHA, biblio, CALIBRAGE, DELTA0,
                                                               INSTANTS))
        tirages = sp.tirer_frais(gele, monde, graine_derivee(graine, cle, r, "frais"), graine_noyau=noyau)
        return nf.evaluer_v2(gele, tirages, graine_noyau=noyau)
    instances = sp.tirer_instances(rng, TIRAGES, DIM)
    biblio = standard + membres_archive(L, nul)
    if nul == "candidat":
        gele = sp.geler_engagement(nf.construire_engagement_v2("fiche", loi, instances, K, ALPHA, biblio, 0, None,
                                                               instants_reguliers(TIRAGES, len(INSTANTS))))
        tirages = sp.tirer_frais(gele, monde, graine_derivee(graine, cle, r, "frais"), graine_noyau=noyau)
        return nf.evaluer_v2(gele, tirages, graine_noyau=noyau)
    gele = sp.geler_engagement(sp.construire_engagement("fiche", loi, instances, K, ALPHA, biblio, "continu",
                                                        plan_execution="ordre_secret"))
    tirages = sp.tirer_frais(gele, monde, graine_derivee(graine, cle, r, "frais"), graine_noyau=noyau)
    return sp.evaluer(gele, tirages, graine_noyau=noyau)


def ligne_simple(graine, nom, nul, repetitions):
    cle = f"banc-v7|{nom}|{nul}"
    promues, maxima, dominants = 0, [], {}
    for r in range(repetitions):
        rng = random.Random(graine_derivee(graine, cle, r))
        genre, loi, monde, L = scenario(nom, rng)
        ev = juger(genre, loi, monde, L, nul, rng, graine, cle, r)
        promues += bool(ev["promue"])
        maxima.append(ev["log_richesse_max"])
        d = ev.get("membre_dominant_final")
        dominants[d] = dominants.get(d, 0) + 1
    maxima.sort()
    return {"promues": promues, "repetitions": repetitions, "taux": promues / repetitions,
            "borne_haute_wilson": borne_wilson(promues, repetitions),
            "log_w_max_mediane": round(maxima[len(maxima) // 2], 3), "log_w_max_99e": round(maxima[int(0.99 * (len(maxima) - 1))], 3),
            "dominants": dict(sorted(dominants.items(), key=lambda x: -x[1])[:4])}


def _issue_pour_ebh(ev):
    return {"verdict_final": "survit" if ev["promue"] else "eliminee", "motif": "", "pari": dict(ev)}


def ligne_multiplicite(graine, nom, m, repetitions):
    """T14 (variantes), T15 (copies) : m fiches fausses, monde aveugle ; T16 : une fiche vraie parmi m − 1 fausses."""
    cle = f"banc-v7|{nom}|m{m}"
    au_moins_une_par_fiche = au_moins_une_ebh = vraie_par_fiche = vraie_ebh = 0
    for r in range(repetitions):
        rng = random.Random(graine_derivee(graine, cle, r))
        fausse = sp.loi_softmax_aleatoire(rng, K, DIM)
        neuve = sp.loi_softmax_aleatoire(rng, K, DIM)
        aveugle = _fixe(_dirichlet(rng, K, 5.0))
        issues = {}
        for i in range(m):
            sous = random.Random(graine_derivee(graine, cle, r, i))
            if nom == "T14":
                loi = {"type": "softmax", "biais": list(fausse["biais"]),
                       "poids": [[w + sous.gauss(0.0, 0.3) for w in ligne] for ligne in fausse["poids"]]}
                monde = aveugle
            elif nom == "T15":
                loi, monde = fausse, aveugle
            elif nom in ("T16", "T16f"):
                vraie = neuve if nom == "T16" else {"type": "softmax", "biais": list(neuve["biais"]),
                                                     "poids": [[0.3 * w for w in ligne] for ligne in neuve["poids"]]}
                monde = vraie
                loi = vraie if i == 0 else sp.loi_softmax_aleatoire(sous, K, DIM)
            else:
                raise ValueError(nom)
            L = {"S1": sp.loi_softmax_aleatoire(sous, K, DIM), "S2": sp.loi_softmax_aleatoire(sous, K, DIM)}
            issues[f"F{i:03d}"] = _issue_pour_ebh(juger("fraiche", loi, monde, L, "v7", sous, graine, cle, f"{r}|{i}"))
        par_fiche = {i for i, x in issues.items() if x["verdict_final"] == "survit"}
        appliquer_multiplicite(issues, ALPHA)
        ebh = {i for i, x in issues.items() if x["verdict_final"] == "survit"}
        if nom in ("T16", "T16f"):
            vraie_par_fiche += "F000" in par_fiche
            vraie_ebh += "F000" in ebh
        else:
            au_moins_une_par_fiche += bool(par_fiche)
            au_moins_une_ebh += bool(ebh)
    if nom in ("T16", "T16f"):
        return {"m": m, "repetitions": repetitions, "puissance_par_fiche": vraie_par_fiche / repetitions,
                "puissance_e_bh": vraie_ebh / repetitions}
    return {"m": m, "repetitions": repetitions, "au_moins_une_par_fiche": au_moins_une_par_fiche / repetitions,
            "au_moins_une_e_bh": au_moins_une_ebh / repetitions,
            "borne_haute_wilson_e_bh": borne_wilson(au_moins_une_ebh, repetitions)}


LIGNES = (
    [(n, "candidat", "fatal_candidat") for n in ("T02", "T03b", "T04", "T05s")]
    + [(n, "v7", "mesure_v7") for n in ("T02", "T03b", "T04", "T05s")]
    + [(n, "v7", "fatal_v7") for n in ("T01", "T03u", "T17s", "T09g", "T09l", "T12a", "nul_exact")]
    + [("T07", "v7", "mesure"), ("T07", "candidat", "mesure"), ("T12b", "v7", "mesure")]
    + [("T01", "v1", "artefact_requis")]
    + [(n, nul, "puissance") for n in ("fille_neuve", "fraiche_neuve") for nul in ("v7", "candidat")]
    + [("T14", 10, "multiplicite"), ("T15", 20, "multiplicite"), ("T16", 1, "puissance_m"), ("T16", 10, "puissance_m"),
       ("T16", 40, "puissance_m"), ("T16f", 1, "puissance_m"), ("T16f", 10, "puissance_m"), ("T16f", 40, "puissance_m")])


def executer(arguments):
    graine, nom, reglage, role, repetitions = arguments
    debut = time.time()
    if role in ("multiplicite", "puissance_m"):
        res = ligne_multiplicite(graine, nom, reglage,
                                 repetitions if nom not in ("T16", "T16f") or reglage < 40 else max(20, repetitions // 2))
    else:
        res = ligne_simple(graine, nom, reglage, repetitions)
    return {"ligne": nom, "reglage": reglage, "role": role, "duree_s": round(time.time() - debut, 1), **res}


def lire(resultats):
    lecture = {}
    for x in resultats:
        cle = f"{x['ligne']}|{x['reglage']}"
        if x["role"] in ("fatal_candidat", "fatal_v7"):
            lecture[cle] = "tenu (≤ α)" if x["taux"] <= ALPHA else "CÈDE (> α)"
        elif x["role"] == "mesure_v7":
            lecture[cle] = "ouvert dans v7 (> α)" if x["taux"] > ALPHA else "fermé dans v7 (≤ α)"
        elif x["role"] == "artefact_requis":
            lecture[cle] = "vu (> α) : le banc a des dents" if x["taux"] > ALPHA else "NON VU : banc sans dents"
        elif x["role"] == "puissance":
            lecture[cle] = "tenu (≥ 0,90)" if x["taux"] >= 0.90 else "puissance manquante (< 0,90)"
        elif x["role"] == "multiplicite":
            lecture[cle] = "tenu sous e-BH (≤ α)" if x["au_moins_une_e_bh"] <= ALPHA else "CÈDE sous e-BH (> α)"
        else:
            lecture[cle] = "lu"
    perte = {}
    for n in ("fille_neuve", "fraiche_neuve"):
        t = {x["reglage"]: x["taux"] for x in resultats if x["ligne"] == n}
        if "v7" in t and "candidat" in t:
            perte[n] = round(t["v7"] - t["candidat"], 4)
            lecture[f"{n}|perte_du_candidat"] = "tenu (≤ 0,05)" if perte[n] <= 0.05 else "perte trop forte (> 0,05)"
    return lecture, perte


def principal(argv=None):
    a = argparse.ArgumentParser()
    a.add_argument("dossier")
    a.add_argument("--graine", type=int, required=True)
    a.add_argument("--repetitions", type=int, default=200)
    a.add_argument("--processus", type=int, default=4)
    a.add_argument("--lignes", help="sous-ensemble : noms séparés par des virgules (essai)")
    args = a.parse_args(argv)
    if os.path.exists(args.dossier) and os.listdir(args.dossier):
        raise FileExistsError(args.dossier)
    os.makedirs(args.dossier, exist_ok=True)
    lignes = [l for l in LIGNES if not args.lignes or l[0] in args.lignes.split(",")]
    ecrire_json_scelle(os.path.join(args.dossier, "manifeste.json"), manifeste(
        banc="banc-tricheurs-v7", graine=args.graine, repetitions=args.repetitions, lignes=[list(l) for l in lignes]))
    debut = time.time()
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.processus) as pool:
        resultats = list(pool.map(executer, [(args.graine, n, reglage, role, args.repetitions) for n, reglage, role in lignes]))
    lecture, perte = lire(resultats)
    rapport = {"graine": args.graine, "repetitions": args.repetitions, "duree_s": round(time.time() - debut, 1),
               "lecture": lecture, "perte_de_puissance_du_candidat": perte, "resultats": resultats}
    ecrire_json_scelle(os.path.join(args.dossier, "banc-tricheurs-v7.json"), rapport)
    print(json.dumps({"lecture": lecture, "duree_s": rapport["duree_s"]}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(principal())
