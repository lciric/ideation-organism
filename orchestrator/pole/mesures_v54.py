"""Mesures du pré-pilote, version 54 (programmes, 0 USD) : accords des juges (CL18-14), étalonnage M1 avec verdicts absents,
contrôles de forme S18 et S19 (A7, table R5 ligne 27), règle des ambigus et des effectifs (S20, A6, ligne 26).

- `kappa_cohen_v54`, `kappa_fleiss_v54` : quand l'accord attendu vaut 1 (marges constantes : tous « non notable »,
  par exemple), l'accord est **non défini** (`None`, avec la mention), jamais 1 (v53 rendait 1,0).
- `etalonner_juges_v54` : un verdict absent (`None`) n'est jamais compté notable ni non notable ; il est retiré des parts de
  ce juge et compté (`absents`) ; les kappas se calculent sur les témoins où tous les juges ont rendu un verdict (les autres
  sont comptés). Seuils S1 à S4 injectés.
- `aire_forme` : régression logistique sur trois indices (longueur en caractères, nombre de chiffres, nombre de champs
  repérés), validation croisée **par fond** (un fond tenu à l'écart à la fois), aire sous la courbe par la statistique de
  Mann et Whitney (égalités comptées 1/2) ; plus l'aire de la longueur seule (équivalent du test de rang de Wilcoxon,
  rapporté). La pénalité de crête est injectée (aucun défaut).
"""

import itertools

VERSION = "mesures-pre-pilote-v54"


def kappa_cohen_v54(a, b):
    n = len(a)
    if n == 0 or len(b) != n:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return None if abs(1 - pe) < 1e-12 else (po - pe) / (1 - pe)


def kappa_fleiss_v54(table):
    if not table:
        return None
    n_j = len(table[0])
    if n_j < 2 or any(len(t) != n_j for t in table):
        return None
    N = len(table)
    p1 = sum(sum(t) for t in table) / (N * n_j)
    pe = p1 ** 2 + (1 - p1) ** 2
    if abs(1 - pe) < 1e-12:
        return None
    pbar = sum((sum(t) * (sum(t) - 1) + (n_j - sum(t)) * (n_j - sum(t) - 1)) / (n_j * (n_j - 1)) for t in table) / N
    return (pbar - pe) / (1 - pe)


def etalonner_juges_v54(notables, attendus, *, exactitude_min, rappel_min, plancher_echec, fleiss_min, cohen_min, accord_plancher):
    """`notables` {juge: {ident: bool | None}} ; `attendus` {ident: "P" | "N"}."""
    seuils = {"exactitude_min": exactitude_min, "rappel_min": rappel_min, "plancher_echec": plancher_echec,
              "fleiss_min": fleiss_min, "cohen_min": cohen_min, "accord_plancher": accord_plancher}
    for nom, v in seuils.items():
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not -1 <= v <= 1:
            raise ValueError(f"{nom} : seuil injecté exigé, aucun défaut")
    ids = sorted(attendus)
    par_juge = {}
    for j, v in notables.items():
        P = [i for i in ids if attendus[i] == "P" and v.get(i) is not None]
        N = [i for i in ids if attendus[i] == "N" and v.get(i) is not None]
        rappel = sum(bool(v[i]) for i in P) / len(P) if P else None
        spec = sum(not v[i] for i in N) / len(N) if N else None
        ee = (rappel + spec) / 2 if rappel is not None and spec is not None else None
        par_juge[j] = {"rappel_P": rappel, "specificite_N": spec, "exactitude_equilibree": ee,
                       "absents": sum(1 for i in ids if v.get(i) is None),
                       "defaillant": ee is not None and ee < plancher_echec,
                       "etalonne": ee is not None and ee + 1e-12 >= exactitude_min and rappel + 1e-12 >= rappel_min}
    juges = sorted(notables)
    complets = [i for i in ids if all(notables[j].get(i) is not None for j in juges)]
    table = [[bool(notables[j][i]) for j in juges] for i in complets]
    fleiss = kappa_fleiss_v54(table)
    cohen = {f"{a}|{b}": kappa_cohen_v54([bool(notables[a][i]) for i in complets], [bool(notables[b][i]) for i in complets])
             for a, b in itertools.combinations(juges, 2)}
    defini = fleiss is not None and all(c is not None for c in cohen.values())
    accord_ok = defini and fleiss + 1e-12 >= fleiss_min and all(c + 1e-12 >= cohen_min for c in cohen.values())
    return {"par_juge": par_juge, "fleiss": fleiss, "cohen": cohen, "accord_defini": defini,
            "accord": "non défini (marges constantes)" if not defini else ("satisfait" if accord_ok else "non satisfait"),
            "accord_satisfait": accord_ok, "accord_en_echec": fleiss is not None and fleiss < accord_plancher,
            "temoins_exclus_des_kappas": len(ids) - len(complets),
            "porte_juges": all(p["etalonne"] for p in par_juge.values()) and accord_ok, "seuils": seuils}


# --- contrôles de forme (S18, S19 ; A7) ------------------------------------------------------------------------------------------


def indices_forme(texte, nombre_champs):
    return [float(len(texte)), float(sum(c.isdigit() for c in texte)), float(nombre_champs)]


def aire_mann_whitney(scores_pos, scores_neg):
    if not scores_pos or not scores_neg:
        return None
    gagne = 0.0
    for p in scores_pos:
        for q in scores_neg:
            gagne += 1.0 if p > q else (0.5 if p == q else 0.0)
    return gagne / (len(scores_pos) * len(scores_neg))


def _logistique(X, y, ridge, iterations=100):
    import numpy as np
    X = np.asarray(X, float)
    y = np.asarray(y, float)
    mu, sd = X.mean(0), X.std(0)
    sd[sd == 0] = 1.0
    Z = np.hstack([np.ones((len(X), 1)), (X - mu) / sd])
    w = np.zeros(Z.shape[1])
    R = ridge * np.eye(Z.shape[1])
    R[0, 0] = 0.0
    for _ in range(iterations):
        p = 1 / (1 + np.exp(-np.clip(Z @ w, -30, 30)))
        g = Z.T @ (p - y) + R @ w
        H = Z.T @ (Z * (p * (1 - p))[:, None]) + R + 1e-9 * np.eye(Z.shape[1])
        pas = np.linalg.solve(H, g)
        w -= pas
        if float(np.max(np.abs(pas))) < 1e-10:
            break
    return lambda Xn: 1 / (1 + np.exp(-np.clip(np.hstack([np.ones((len(Xn), 1)), (np.asarray(Xn, float) - mu) / sd]) @ w, -30, 30)))


def aire_forme(elements, *, ridge):
    """`elements` : [{groupe (fond), classe (1 ou 0), indices [3 réels]}]. Validation croisée par groupe. Rend {aire,
    aire_longueur, n1, n0}."""
    if isinstance(ridge, bool) or not isinstance(ridge, (int, float)) or not ridge > 0:
        raise ValueError("controles_forme.ridge : réel > 0 injecté, aucun défaut")
    pos = [e for e in elements if e["classe"] == 1]
    neg = [e for e in elements if e["classe"] == 0]
    if len(pos) < 2 or len(neg) < 2:
        return {"aire": None, "aire_longueur": None, "n1": len(pos), "n0": len(neg), "motif": "effectifs insuffisants"}
    groupes = sorted({e["groupe"] for e in elements})
    pred = {}
    for g in groupes:
        app = [e for e in elements if e["groupe"] != g]
        tst = [e for e in elements if e["groupe"] == g]
        if len({e["classe"] for e in app}) < 2:
            continue
        f = _logistique([e["indices"] for e in app], [e["classe"] for e in app], ridge)
        for e, p in zip(tst, f([e["indices"] for e in tst])):
            pred[id(e)] = float(p)
    aire = aire_mann_whitney([pred[id(e)] for e in pos if id(e) in pred], [pred[id(e)] for e in neg if id(e) in pred])
    aire_l = aire_mann_whitney([e["indices"][0] for e in pos], [e["indices"][0] for e in neg])
    return {"aire": None if aire is None else round(aire, 6), "aire_longueur": round(aire_l, 6), "n1": len(pos), "n0": len(neg)}


def regle_s20(classes_primaires, ambigus, *, ambigus_max, p_min, n_min):
    """S20 / A6 : `classes_primaires` {ident: "P" | "N1".."N4"} ; `ambigus` ensemble d'identifiants. Rend {passe, motif, …}."""
    restants = {i: c for i, c in classes_primaires.items() if i not in ambigus}
    n_amb = sum(1 for i in classes_primaires if i in ambigus)
    p = sum(1 for c in restants.values() if c == "P")
    n = sum(1 for c in restants.values() if c.startswith("N"))
    motifs = []
    if n_amb > ambigus_max:
        motifs.append(f"{n_amb} ambigus > {ambigus_max}")
    if p < p_min:
        motifs.append(f"P primaires {p} < {p_min}")
    if n < n_min:
        motifs.append(f"N primaires {n} < {n_min}")
    return {"passe": not motifs, "ambigus": n_amb, "p_primaires": p, "n_primaires": n, "motif": " ; ".join(motifs) or None}
