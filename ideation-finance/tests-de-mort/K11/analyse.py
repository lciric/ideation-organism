#!/usr/bin/env python3
"""K11 -- statistique principale et analyses secondaires (preinscription, section 6), a partir de K11_analyse.csv.

- recalcule les 12 rendements de chaque ligne de P avec un SECOND code (Newton, dates de coupon generees
  autrement que dans construire.py) et rapporte ecart_max_rdt_pb ;
- calcule E et V avec ces rendements, puis les statistiques de la section 6 ;
- execute les controles de schema 5.3 (code de construire.py) pour schema_ok ;
- ecrit temoin.json (champs de "champs_verification") et figure.png.
Usage : python3 -I analyse.py
"""
import csv
import datetime as dt
import json
import math
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
FICHIER = os.path.join(ICI, "K11_analyse.csv")
X3 = ("jm5", "j", "jp5")


# ------------------------------------------------------------------ second code de rendement (5.2)
def dates_coupon(M, d):
    """Liste croissante des T_k > d, et L = dernier T_k <= d. M est toujours un 15."""
    T = []
    a, m = M.year, M.month
    while True:
        t = dt.date(a, m, M.day)
        if t <= d:
            return t, T[::-1]
        T.append(t)
        m -= 6
        if m <= 0:
            m += 12
            a -= 1


def rendement2(P, c, M, d):
    L, futurs = dates_coupon(M, d)
    N = futurs[0]
    n = len(futurs)
    w = (N - d).days / (N - L).days
    ai = (c / 2.0) * ((d - L).days / (N - L).days)
    tgt = P + ai
    flux = [(c / 2.0 + (100.0 if j == n - 1 else 0.0), j + w) for j in range(n)]

    def f(y):
        b = 1.0 + y / 200.0
        return sum(F * b ** (-e) for F, e in flux) - tgt

    def fp(y):
        b = 1.0 + y / 200.0
        return sum(-e * F * b ** (-e - 1) / 200.0 for F, e in flux)

    y = c if c > 0 else 3.0
    for _ in range(200):
        dy = f(y) / fp(y)
        y -= dy
        if abs(dy) < 1e-13:
            break
    assert abs(f(y)) < 1e-8, (P, c, M, d)
    return y


# ------------------------------------------------------------------ statistiques
def moyenne_et(rows, col):
    """Moyenne et erreur type groupee par mois (section 6)."""
    v = [(r["mois"], r[col]) for r in rows if r[col] is not None]
    N = len(v)
    if N == 0:
        return None, None, 0, 0
    m = sum(x for _, x in v) / N
    g = {}
    for mo, x in v:
        g[mo] = g.get(mo, 0.0) + (x - m)
    G = len(g)
    et = (1.0 / N) * math.sqrt(G / (G - 1) * sum(s * s for s in g.values())) if G > 1 else float("nan")
    return m, et, N, G


def ecart_type(rows, col):
    v = [r[col] for r in rows if r[col] is not None]
    m = sum(v) / len(v)
    return math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))


def main():
    with open(FICHIER, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    fl = lambda s: float(s) if s != "" else None
    P = [r for r in rows if r["dans_p"] == "1"]

    # ---- recalcul des rendements (second code) et de E, V
    ecart_max = 0.0
    for r in P:
        d = {"jm5": dt.date.fromisoformat(r["date_jm5"]), "j": dt.date.fromisoformat(r["date_adjudication"]),
             "jp5": dt.date.fromisoformat(r["date_jp5"])}
        titres = {"a": (fl(r["taux_coupon_pct"]), dt.date.fromisoformat(r["date_echeance"]))}
        for k in (1, 2, 3):
            titres[f"t{k}"] = (fl(r[f"coupon_t{k}_pct"]), dt.date.fromisoformat(r[f"echeance_t{k}"]))
        titres["pa"] = (fl(r["coupon_pa_pct"]), dt.date.fromisoformat(r["echeance_pa"]))
        y = {}
        for t, (c, M) in titres.items():
            for x in X3:
                p = fl(r[f"prix_{t}_{x}"])
                y[(t, x)] = None if p is None else rendement2(p, c, M, d[x])
                if t != "pa":
                    ecart_max = max(ecart_max, abs(y[(t, x)] - fl(r[f"rdt_{t}_{x}_pct"])))
        E = {x: 100 * (y[("a", x)] - (y[("t1", x)] + y[("t2", x)] + y[("t3", x)]) / 3) for x in X3}
        r["V"] = 2 * E["j"] - E["jm5"] - E["jp5"]
        r["MONTEE"] = E["j"] - E["jm5"]
        r["DETENTE"] = E["j"] - E["jp5"]
        if all(y[("pa", x)] is not None for x in X3):
            Ep = {x: 100 * (y[("pa", x)] - (y[("t1", x)] + y[("t2", x)] + y[("t3", x)]) / 3) for x in X3}
            r["VPA"] = 2 * Ep["j"] - Ep["jm5"] - Ep["jp5"]
        else:
            r["VPA"] = None
        r["PCARTE"] = None
        hy = fl(r["rdt_limite_pct"])
        if hy is not None:
            dv = sum(y[(f"t{k}", "j")] - y[(f"t{k}", "jm5")] for k in (1, 2, 3)) / 3
            r["PCARTE"] = 100 * ((hy - y[("a", "jm5")]) - dv)
        r["Vfichier"] = fl(r["v_pb"])
        r["annee_i"] = int(r["annee"])
        r["ech_i"] = int(r["echeance"])
    ecart_max_rdt_pb = 100 * ecart_max
    ecart_v_fichier = max(abs(r["V"] - r["Vfichier"]) for r in P)

    apres = [r for r in P if r["periode"] == "apres"]
    avant1030 = [r for r in P if r["periode"] == "avant" and r["ech_i"] in (10, 30)]
    apres1030 = [r for r in apres if r["ech_i"] in (10, 30)]

    m, et, n_apres, g_apres = moyenne_et(apres, "V")
    L, U = m - 1.645 * et, m + 1.645 * et
    marge = min(-L, U - 0.5)
    s23, _, n_s23, _ = moyenne_et([r for r in apres if r["annee_i"] != 2023], "V")
    s30, _, n_s30, _ = moyenne_et([r for r in apres if r["ech_i"] != 30], "V")
    minrob = min(s23, s30)
    alerte_rob = 1 if (L > 0 and U >= 0.5 and minrob <= 0) else 0
    mav, etav, n_av, g_av = moyenne_et(avant1030, "V")
    map_, etap, n_ap1030, g_ap1030 = moyenne_et(apres1030, "V")
    baisse = mav - map_
    etb = math.sqrt(etav ** 2 + etap ** 2)
    binf_b = baisse - 1.645 * etb
    alerte_instr = 1 if (U < 0.5 and binf_b <= 0) else 0

    import construire
    res, _ = construire.controles(construire.calendrier_c(), construire.charger_d1())
    schema_ok = construire.schema_ok(res)  # lecture litterale du controle 5 (voir ecarts.md)
    schema_ok_alt = construire.schema_ok(res, alternative=True)
    n_figes = sum(int(r["n_temoins_figes"]) for r in P)

    temoin = {
        "schema_ok": schema_ok,
        "n_apres": n_apres,
        "n_grappes_apres": g_apres,
        "n_avant_1030": n_av,
        "n_grappes_avant_1030": g_av,
        "n_temoins_figes": n_figes,
        "ecart_max_rdt_pb": ecart_max_rdt_pb,
        "v_moyen_apres_pb": m,
        "erreur_type_apres_pb": et,
        "borne_inf_90_apres_pb": L,
        "borne_sup_90_apres_pb": U,
        "marge_zone_grise": marge,
        "v_moyen_apres_sans_2023_pb": s23,
        "v_moyen_apres_sans_30_pb": s30,
        "min_robustesse_pb": minrob,
        "alerte_robustesse": alerte_rob,
        "v_moyen_avant_1030_pb": mav,
        "erreur_type_avant_1030_pb": etav,
        "v_moyen_apres_1030_pb": map_,
        "erreur_type_apres_1030_pb": etap,
        "baisse_1030_pb": baisse,
        "erreur_type_baisse_pb": etb,
        "borne_inf_90_baisse_pb": binf_b,
        "alerte_instrument": alerte_instr,
    }
    with open(os.path.join(ICI, "temoin.json"), "w", encoding="utf-8") as f:
        json.dump(temoin, f, indent=2)
        f.write("\n")

    print("== Controles de schema :", {k: int(v) for k, v in res.items()})
    print(f"   schema_ok litteral = {schema_ok} ; schema_ok en lecture alternative (5bis) = {schema_ok_alt}")
    print("== Temoin (statistique principale et regle)")
    for k, v in temoin.items():
        print(f"  {k} = {v}")
    print(f"  (comptes : P = {len(P)} ; P_apres,10/30 = {n_ap1030} en {g_ap1030} mois ; sans 2023 = {n_s23} ; sans 30 = {n_s30})")
    print(f"  (ecart max entre V du fichier et V du second code : {ecart_v_fichier:.3e} pb)")
    m1, e1, _, _ = moyenne_et([dict(r, Vf=r["Vfichier"]) for r in apres], "Vf")
    print(f"  (V moyen apres avec les V du fichier : {m1!r}, ET {e1!r})")

    def ligne(nom, rs, col):
        mm, ee, nn, gg = moyenne_et(rs, col)
        if mm is None:
            print(f"  {nom:45s} n = 0")
        else:
            print(f"  {nom:45s} moyenne = {mm:8.4f}  ET = {ee:7.4f}  n = {nn:3d}  mois = {gg:3d}")
        return mm, ee, nn, gg

    print("== S1 (descriptif) : p_carte_pb, mesure de la fiche au rendement limite")
    ligne("P_apres", apres, "PCARTE")
    ligne("P_avant,10/30", avant1030, "PCARTE")
    print("== S2 (descriptif) : montee, detente, V du premier ancien")
    for nom, rs in (("P_apres", apres), ("P_avant,10/30", avant1030)):
        ligne(f"montee_pb {nom}", rs, "MONTEE")
        ligne(f"detente_pb {nom}", rs, "DETENTE")
        ligne(f"v_pa_pb {nom}", rs, "VPA")
    print("== S3 (descriptif)")
    for a in range(2022, 2027):
        ligne(f"V apres, annee {a}", [r for r in apres if r["annee_i"] == a], "V")
    for e in (10, 20, 30):
        ligne(f"V apres, echeance {e}", [r for r in apres if r["ech_i"] == e], "V")
    ligne("V apres, sans 2023 et sans 30 ans", [r for r in apres if r["annee_i"] != 2023 and r["ech_i"] != 30], "V")
    ligne("V des 20 ans d'avant 2022", [r for r in P if r["periode"] == "avant" and r["ech_i"] == 20], "V")
    for e in (10, 30):
        ligne(f"V avant, echeance {e}", [r for r in avant1030 if r["ech_i"] == e], "V")
    print(f"  ecart-type de V (n-1) : P_apres = {ecart_type(apres, 'V'):.4f} ; P_avant,10/30 = {ecart_type(avant1030, 'V'):.4f}")
    print("== Descriptif complementaire (hors preinscription) : V par annee, toutes echeances de P")
    par_annee = []
    for a in range(2010, 2027):
        rs = [r for r in P if r["annee_i"] == a]
        mm, ee, nn, gg = ligne(f"V annee {a}", rs, "V")
        par_annee.append((a, mm, ee, nn))

    # ---- figure
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    bleu, orange, encre, gris = "#2a78d6", "#eb6834", "#2b2b2b", "#8a8a85"
    fig, ax = plt.subplots(figsize=(9, 5), dpi=150)
    for a, mm, ee, nn in par_annee:
        col = orange if a >= 2022 else bleu
        ax.errorbar(a, mm, yerr=1.645 * ee, fmt="o", ms=6, color=col, ecolor=col, elinewidth=1.6, capsize=3)
        ax.text(a, 0.02, f"n={nn}", transform=ax.get_xaxis_transform(), ha="center", fontsize=7, color=gris)
    ax.axhline(0, color="#c3c2b7", lw=1)
    ax.axhline(0.5, color="#c3c2b7", lw=1, ls=":")
    ax.text(2009.6, 0.55, "0,5 pb", fontsize=7, color=gris, va="bottom")
    ax.axvline(2021.5, color=encre, lw=1, ls="--")
    ax.text(2021.6, ax.get_ylim()[1], " 2022 : coupure", fontsize=8, color=encre, va="top")
    # moyennes de periode avec IC a 90 %
    ax.hlines(mav, 2009.7, 2021.3, color=bleu, lw=2)
    ax.fill_between([2009.7, 2021.3], mav - 1.645 * etav, mav + 1.645 * etav, color=bleu, alpha=0.12, lw=0)
    ax.hlines(m, 2021.7, 2026.3, color=orange, lw=2)
    ax.fill_between([2021.7, 2026.3], L, U, color=orange, alpha=0.15, lw=0)
    ax.set_xlim(2009.5, 2026.5)
    ax.set_xticks(range(2010, 2027))
    ax.tick_params(axis="x", labelrotation=45, labelsize=8)
    ax.tick_params(axis="y", labelsize=8)
    ax.set_ylabel("V = 2E(J) − E(J−5) − E(J+5), pb", fontsize=9)
    ax.set_title("K11 — V moyen par année (toutes échéances de P), IC à 90 % groupé par mois", fontsize=10)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color="#e1e0d9", lw=0.6)
    ax.set_axisbelow(True)
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    ax.legend(handles=[Line2D([], [], color=bleu, marker="o", lw=0, label="année 2010-2021, toutes échéances de P"),
                       Line2D([], [], color=orange, marker="o", lw=0, label="année 2022-2026, toutes échéances de P"),
                       Patch(color=bleu, alpha=0.3, label=f"2010-2021, 10 et 30 ans : {mav:.2f} pb [{mav - 1.645 * etav:.2f} ; {mav + 1.645 * etav:.2f}]"),
                       Patch(color=orange, alpha=0.3, label=f"μ_après (statistique principale) : {m:.2f} pb [{L:.2f} ; {U:.2f}]")],
              loc="lower left", bbox_to_anchor=(0.0, 0.06), fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(ICI, "figure.png"))


if __name__ == "__main__":
    main()
