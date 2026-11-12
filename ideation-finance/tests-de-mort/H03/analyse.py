#!/usr/bin/env python3
"""H03 — statistique principale et analyses secondaires, à partir de H03_analyse.csv seul.

Suit la préinscription, section 5 (contrôles de schéma) et section 6 (étapes 1 à 6, S1, S2, S3).
Écrit temoin.json (témoin de l'expérimentateur), analyse_details.json, analyse_lignes.csv et figure.png.
Aucun verdict n'est écrit.

Usage : python3 analyse.py
"""
import csv
import json
import math
import os
import re
import sys

import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__))
FICHIER = os.path.join(ICI, "H03_analyse.csv")

COLONNES = ["millesime", "t_millesime", "mois_titre", "t_premier_F", "horizon", "cible", "t_cible",
            "projection", "millesime_precedent", "projection_precedente", "millesime_realise",
            "t_lecture", "realise", "revision", "erreur"]
LETTRE_TRIM = {"W": 1, "S": 2, "G": 3, "A": 4}
QUANTILE_T = {11: 1.8125, 10: 1.8331, 9: 1.8595, 8: 1.8946, 7: 1.9432, 6: 2.0150, 5: 2.1318}
T_MIN, T_MAX = 8016, 8103
EPS = 1e-12
CHAMPS = ["n_violations_schema", "n_obs_evaluees", "n_blocs", "r_moyen", "et_r_moyen", "borne_basse_ic90",
          "borne_haute_ic90", "marge_indecision", "r_hors_episode", "rapport_eqm_geo", "conflit_gardes",
          "n_obs_h4_2020", "rapport_eqm_h4_2020", "p_dm_hln_h4_2020", "rapport_eqm_global",
          "rapport_eqm_hors_2021_2022", "taux_amelioration", "part_b_positif", "r_moyen_h1", "r_moyen_h2",
          "r_moyen_h3", "r_moyen_h4", "r_moyen_placebo", "et_r_placebo", "n_blocs_placebo"]


# ----------------------------------------------------------------------------------------------
# Section 5 — contrôles de schéma
# ----------------------------------------------------------------------------------------------
def liste_millesimes():
    codes = []
    for annee in range(1999, 2026):
        for lettre in "WSGA":
            codes.append(f"{lettre}{annee % 100:02d}")
    return codes + ["W26", "S26", "G26"]


def t_du_code(code):
    aa = int(code[1:])
    annee = 1900 + aa if aa == 99 else 2000 + aa
    return 4 * annee + (LETTRE_TRIM[code[0]] - 1)


RE_ENTIER = re.compile(r"^-?\d+$")
RE_DEC1 = re.compile(r"^-?\d+(\.\d)?$")


def _entier(txt):
    return int(txt) if RE_ENTIER.match(txt or "") else None


def controles_schema(chemin):
    """Retourne {numéro du contrôle (1..11): nombre de manquements constatés}."""
    viol = {k: 0 for k in range(1, 12)}
    with open(chemin, encoding="utf-8", newline="") as f:
        lecteur = csv.reader(f)
        entete = next(lecteur)
        brut = [l for l in lecteur]
    # 1
    if entete != COLONNES:
        viol[1] += 1
        if not all(c in entete for c in COLONNES):
            for k in range(2, 12):
                viol[k] += 1  # sans les colonnes, rien ne peut être contrôlé
            return viol
    lignes = [dict(zip(entete, l)) for l in brut]
    figes = set(liste_millesimes())
    t_code = {c: t_du_code(c) for c in figes}
    code_t = {t: c for c, t in t_code.items()}
    # 2
    couples = [(l["millesime"], l["horizon"]) for l in lignes]
    if len(lignes) != 444:
        viol[2] += 1
    if len(set(couples)) != len(couples):
        viol[2] += 1
    if set(couples) != {(c, str(h)) for c in figes for h in (1, 2, 3, 4)}:
        viol[2] += 1
    if {l["millesime"] for l in lignes} != figes:
        viol[2] += 1

    def dec_ok(txt):
        if txt == "":
            return True
        if not RE_DEC1.match(txt):
            return False
        return -5 <= float(txt) <= 15

    proj_par = {}
    for l in lignes:
        proj_par[(l["millesime"], l["horizon"])] = l["projection"]
    realise_par_cible = {}
    for l in lignes:
        code, h = l["millesime"], _entier(l["horizon"])
        tm, tc = _entier(l["t_millesime"]), _entier(l["t_cible"])
        # 3
        ok3 = code in t_code and tm is not None and tm == t_code[code] and h in (1, 2, 3, 4) \
            and tc is not None and tc == tm + h and l["cible"] == f"{tc // 4}-Q{tc % 4 + 1}"
        if not ok3:
            viol[3] += 1
        # 4
        if l["mois_titre"] != "":
            m = _entier(l["mois_titre"])
            if m is None or tm is None or m != 3 * (tm % 4 + 1):
                viol[4] += 1
        # 5
        if l["t_premier_F"] != "":
            tf = _entier(l["t_premier_F"])
            if tf is None or tm is None or not (tm - 2 <= tf <= tm + 1):
                viol[5] += 1
        # 6
        if not (dec_ok(l["projection"]) and dec_ok(l["projection_precedente"]) and dec_ok(l["realise"])):
            viol[6] += 1
        # 7
        def diff_ok(res, a, b):
            vide_attendu = (a == "" or b == "")
            if (res == "") != vide_attendu:
                return False
            if res == "":
                return True
            try:
                return abs(float(res) - (float(a) - float(b))) <= 1e-6
            except ValueError:
                return False
        if not (diff_ok(l["revision"], l["projection"], l["projection_precedente"])
                and diff_ok(l["erreur"], l["realise"], l["projection"])):
            viol[7] += 1
        # 8
        vides = [l["t_lecture"] == "", l["millesime_realise"] == "", l["realise"] == ""]
        if any(vides) and not all(vides):
            viol[8] += 1
        elif not any(vides):
            tl = _entier(l["t_lecture"])
            if tl is None or tc is None or (tl - tc) not in (2, 3, 4) or tl > 8106 \
                    or code_t.get(tl) != l["millesime_realise"]:
                viol[8] += 1
        # 9
        attendu_prec = code_t.get(tm - 1, "") if tm is not None else None
        if l["millesime_precedent"] != attendu_prec or ((l["millesime_precedent"] == "") != (code == "W99")):
            viol[9] += 1
        # 10
        cle = l["t_cible"]
        val = (l["realise"], l["t_lecture"])
        if cle in realise_par_cible and realise_par_cible[cle] != val:
            viol[10] += 1
        realise_par_cible.setdefault(cle, val)
        # 11
        if h in (1, 2, 3):
            if l["millesime_precedent"] == "":
                autre = ""
            else:
                autre = proj_par.get((l["millesime_precedent"], str(h + 1)))
            a, b = l["projection_precedente"], autre
            if b is None:
                viol[11] += 1
            elif a == "" or b == "":
                if a != b:
                    viol[11] += 1
            elif abs(float(a) - float(b)) > 1e-9:
                viol[11] += 1
    return viol


# ----------------------------------------------------------------------------------------------
# Section 6 — statistique
# ----------------------------------------------------------------------------------------------
def charger(chemin):
    with open(chemin, encoding="utf-8", newline="") as f:
        lignes = list(csv.DictReader(f))

    def num(x):
        return float(x) if x != "" else float("nan")
    d = {
        "millesime": [l["millesime"] for l in lignes],
        "cible": [l["cible"] for l in lignes],
        "t_millesime": np.array([int(l["t_millesime"]) for l in lignes]),
        "horizon": np.array([int(l["horizon"]) for l in lignes]),
        "t_cible": np.array([int(l["t_cible"]) for l in lignes]),
        "t_lecture": np.array([num(l["t_lecture"]) for l in lignes]),
        "revision": np.array([num(l["revision"]) for l in lignes]),
        "erreur": np.array([num(l["erreur"]) for l in lignes]),
    }
    return d


def regle_recursive(d, r):
    """Étape 2 pour toutes les lignes complètes (sans borne sur t_cible).

    r : vecteur des révisions utilisées (révision, ou révision décalée pour le placebo).
    Retourne complet, n_A, S_rr, b, c, applicable (n_A >= 8 et S_rr > 1e-12).
    """
    n = len(r)
    e = d["erreur"]
    complet = ~np.isnan(r) & ~np.isnan(e)
    n_a = np.zeros(n, dtype=int)
    s_rr = np.full(n, np.nan)
    b = np.full(n, np.nan)
    c = np.full(n, np.nan)
    applicable = np.zeros(n, dtype=bool)
    for i in range(n):
        if not complet[i]:
            continue
        a = complet & (d["horizon"] == d["horizon"][i]) & (d["t_lecture"] <= d["t_millesime"][i])
        assert not a[i]
        n_a[i] = int(a.sum())
        if n_a[i] == 0:
            continue
        ra, ea = r[a], e[a]
        rb, eb = ra.mean(), ea.mean()
        s_rr[i] = float(((ra - rb) ** 2).sum())
        if n_a[i] >= 8 and s_rr[i] > EPS:
            applicable[i] = True
            b[i] = float(((ra - rb) * (ea - eb)).sum() / s_rr[i])
            c[i] = b[i] * r[i]
    return complet, n_a, s_rr, b, c, applicable


def stat_blocs(k_bloc, c, e, masque, n_min):
    """R_k et Q_k par bloc, pour les lignes du masque ; bloc retenu si >= n_min lignes et sommes > 1e-12."""
    res = {}
    for k in range(11):
        m = masque & (k_bloc == k)
        nk = int(m.sum())
        scc = float((c[m] ** 2).sum())
        see = float((e[m] ** 2).sum())
        valide = nk >= n_min and scc > EPS and see > EPS
        item = {"n": nk, "valide": bool(valide), "somme_c2": scc, "somme_e2": see}
        if valide:
            item["R"] = float((c[m] * e[m]).sum() / math.sqrt(scc * see))
            item["Q"] = float(((e[m] - c[m]) ** 2).sum() / see)
        res[k] = item
    return res


def moyenne_et(blocs):
    """Étape 5 : R̄, ET, bornes. Retourne un dict ; conventions si K < 5."""
    ks = [k for k in sorted(blocs) if blocs[k]["valide"]]
    K = len(ks)
    if K < 5:
        return {"K": K, "r_moyen": 0.0, "et": 0.0, "bas": 0.0, "haut": 0.0, "g0": None, "g1": None, "q": None}
    R = {k: blocs[k]["R"] for k in ks}
    rbar = sum(R.values()) / K
    g0 = sum((R[k] - rbar) ** 2 for k in ks) / (K - 1)
    g1 = sum((R[k] - rbar) * (R[k + 1] - rbar) for k in ks if (k + 1) in R) / (K - 1)
    et = math.sqrt((g0 + 2 * max(g1, 0.0)) / K)
    q = QUANTILE_T[K]
    return {"K": K, "r_moyen": rbar, "et": et, "bas": rbar - q * et, "haut": rbar + q * et,
            "g0": g0, "g1": g1, "q": q}


def analyse(chemin=FICHIER):
    from scipy import stats

    viol = controles_schema(chemin)
    d = charger(chemin)
    n = len(d["erreur"])
    e = d["erreur"]
    r = d["revision"]
    k_bloc = (d["t_cible"] - T_MIN) // 8
    fenetre = (d["t_cible"] >= T_MIN) & (d["t_cible"] <= T_MAX)

    # --- principal -----------------------------------------------------------------------------
    complet, n_a, s_rr, b, c, applicable = regle_recursive(d, r)
    evalue = complet & fenetre & applicable
    blocs = stat_blocs(k_bloc, c, e, evalue, 16)
    m5 = moyenne_et(blocs)
    K = m5["K"]
    valides = [k for k in sorted(blocs) if blocs[k]["valide"]]

    t = {}
    t["n_violations_schema"] = sum(1 for v in viol.values() if v > 0)
    t["n_obs_evaluees"] = int(evalue.sum())
    t["n_blocs"] = K
    t["r_moyen"] = m5["r_moyen"]
    t["et_r_moyen"] = m5["et"]
    t["borne_basse_ic90"] = m5["bas"]
    t["borne_haute_ic90"] = m5["haut"]
    t["marge_indecision"] = min(-t["borne_basse_ic90"], t["borne_haute_ic90"] - 0.22)
    if K < 5:
        t["r_hors_episode"] = 0.0
        t["rapport_eqm_geo"] = 1.0
    else:
        hors = [blocs[k]["R"] for k in valides if k not in (8, 9)]
        # convention non écrite dans la préinscription : 0 si aucun bloc valide hors épisode
        t["r_hors_episode"] = sum(hors) / len(hors) if hors else 0.0
        t["rapport_eqm_geo"] = math.exp(sum(math.log(max(blocs[k]["Q"], 1e-6)) for k in valides) / K)
    t["conflit_gardes"] = int(t["borne_basse_ic90"] > 0 and (t["r_hors_episode"] <= 0 or t["rapport_eqm_geo"] >= 1))

    # --- S1 : test de la fiche (horizon 4, millésimes >= 2020-Q1) ---------------------------------
    m1 = complet & applicable & (d["horizon"] == 4) & (d["t_millesime"] >= 8080)
    idx = np.where(m1)[0]
    idx = idx[np.argsort(d["t_millesime"][idx], kind="stable")]
    n1 = len(idx)
    s1 = {"n": n1}
    t["n_obs_h4_2020"] = n1
    if n1 == 0:
        t["rapport_eqm_h4_2020"] = 1.0
        t["p_dm_hln_h4_2020"] = 1.0
    else:
        e1, c1 = e[idx], c[idx]
        t["rapport_eqm_h4_2020"] = float(((e1 - c1) ** 2).sum() / (e1 ** 2).sum())
        dd = e1 ** 2 - (e1 - c1) ** 2
        dbar = dd.mean()
        gam = [float(((dd[j:] - dbar) * (dd[:n1 - j] - dbar)).sum() / n1) for j in range(4)]
        V = (gam[0] + 2 * (gam[1] + gam[2] + gam[3])) / n1
        s1.update({"d_moyen": float(dbar), "gamma": gam, "V": V,
                   "millesimes": [d["millesime"][i] for i in idx]})
        if n1 < 8 or V <= 0:
            t["p_dm_hln_h4_2020"] = 1.0
        else:
            dm = dbar / math.sqrt(V)
            dm_star = dm * math.sqrt((n1 + 1 - 8 + 12 / n1) / n1)
            t["p_dm_hln_h4_2020"] = float(stats.t.sf(dm_star, n1 - 1))
            s1.update({"DM": float(dm), "DM_etoile": float(dm_star)})

    # --- S2 : lecture en clair ---------------------------------------------------------------------
    ee, cc, bb = e[evalue], c[evalue], b[evalue]
    tc = d["t_cible"][evalue]
    t["rapport_eqm_global"] = float(((ee - cc) ** 2).sum() / (ee ** 2).sum()) if len(ee) else 1.0
    h2122 = ~((tc >= 8084) & (tc <= 8091))
    t["rapport_eqm_hors_2021_2022"] = float(((ee[h2122] - cc[h2122]) ** 2).sum() / (ee[h2122] ** 2).sum()) \
        if h2122.any() else 1.0
    G = int((np.abs(ee - cc) < np.abs(ee) - 1e-9).sum())
    P = int((np.abs(ee - cc) > np.abs(ee) + 1e-9).sum())
    t["taux_amelioration"] = G / (G + P) if (G + P) > 0 else 0.5
    t["part_b_positif"] = float((bb > 0).mean()) if len(bb) else 0.0
    par_horizon = {}
    for h in (1, 2, 3, 4):
        bh = stat_blocs(k_bloc, c, e, evalue & (d["horizon"] == h), 4)
        retenus = [k for k in sorted(bh) if bh[k]["valide"]]
        t[f"r_moyen_h{h}"] = sum(bh[k]["R"] for k in retenus) / len(retenus) if retenus else 0.0
        # lecture alternative (non retenue) : seulement les blocs valides au sens de l'étape 3
        ret2 = [k for k in retenus if blocs[k]["valide"]]
        par_horizon[h] = {
            "blocs": {str(k): bh[k] for k in bh}, "n_blocs_retenus": len(retenus),
            "r_moyen_blocs_valides_etape3_seulement": sum(bh[k]["R"] for k in ret2) / len(ret2) if ret2 else 0.0,
            "part_b_positif": float((b[evalue & (d["horizon"] == h)] > 0).mean())
            if (evalue & (d["horizon"] == h)).any() else None,
        }

    # --- S3 : placebo --------------------------------------------------------------------------------
    rev_par = {(int(d["t_millesime"][i]), int(d["horizon"][i])): r[i] for i in range(n)}
    r_pl = np.array([rev_par.get((int(d["t_millesime"][i]) - 8, int(d["horizon"][i])), float("nan"))
                     for i in range(n)])
    complet_p, n_a_p, s_rr_p, b_p, c_p, applicable_p = regle_recursive(d, r_pl)
    evalue_p = complet_p & fenetre & applicable_p
    blocs_p = stat_blocs(k_bloc, c_p, e, evalue_p, 16)
    m5p = moyenne_et(blocs_p)
    t["r_moyen_placebo"] = m5p["r_moyen"]
    t["et_r_placebo"] = m5p["et"]
    t["n_blocs_placebo"] = m5p["K"]

    temoin = {}
    for champ in CHAMPS:
        v = t[champ]
        temoin[champ] = int(v) if isinstance(v, (int, np.integer)) else float(v)

    details = {
        "controles_schema_manquements_par_controle": {str(k): v for k, v in viol.items()},
        "filtres": {
            "n_lignes": n,
            "n_completes": int(complet.sum()),
            "n_completes_dans_fenetre_8016_8103": int((complet & fenetre).sum()),
            "n_fenetre_n_A_inferieur_8": int((complet & fenetre & (n_a < 8)).sum()),
            "n_fenetre_S_rr_trop_petit": int((complet & fenetre & (n_a >= 8) & ~(s_rr > EPS)).sum()),
            "n_evaluees": int(evalue.sum()),
            "n_evaluees_par_horizon": {str(h): int((evalue & (d["horizon"] == h)).sum()) for h in (1, 2, 3, 4)},
            "n_A_min_max_sur_evaluees": [int(n_a[evalue].min()), int(n_a[evalue].max())] if evalue.any() else None,
        },
        "blocs": {str(k): dict(blocs[k], libelle=f"{2004 + 2 * k}-{2005 + 2 * k}") for k in blocs},
        "etape5": m5,
        "S1": s1,
        "S2": {"G": G, "P": P, "n_egalite": int(len(ee) - G - P), "par_horizon": par_horizon,
               "b_min": float(bb.min()) if len(bb) else None, "b_max": float(bb.max()) if len(bb) else None,
               "b_mediane": float(np.median(bb)) if len(bb) else None},
        "S3": {"n_completes_placebo": int(complet_p.sum()), "n_evaluees_placebo": int(evalue_p.sum()),
               "blocs": {str(k): blocs_p[k] for k in blocs_p}, "etape5": m5p,
               "rapport_r_sur_et": (m5p["r_moyen"] / m5p["et"]) if m5p["et"] else None},
        "temoin": temoin,
    }
    lignes = []
    for i in range(n):
        lignes.append({
            "millesime": d["millesime"][i], "horizon": int(d["horizon"][i]), "cible": d["cible"][i],
            "revision": "" if np.isnan(r[i]) else repr(float(r[i])),
            "erreur": "" if np.isnan(e[i]) else repr(float(e[i])),
            "complete": int(complet[i]), "dans_fenetre": int(fenetre[i]), "n_A": int(n_a[i]),
            "S_rr": "" if np.isnan(s_rr[i]) else repr(float(s_rr[i])),
            "b": "" if np.isnan(b[i]) else repr(float(b[i])),
            "c": "" if np.isnan(c[i]) else repr(float(c[i])),
            "evaluee": int(evalue[i]), "bloc": int(k_bloc[i]) if fenetre[i] else "",
            "revision_placebo": "" if np.isnan(r_pl[i]) else repr(float(r_pl[i])),
            "c_placebo": "" if np.isnan(c_p[i]) else repr(float(c_p[i])),
            "evaluee_placebo": int(evalue_p[i]),
        })
    return temoin, details, lignes


def figure(details, chemin):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    encre, encre2, grille = "#0b0b0b", "#52514e", "#dddcd6"
    bleu, gris = "#2a78d6", "#8a8984"
    blocs = details["blocs"]
    m5 = details["etape5"]
    fig, ax = plt.subplots(figsize=(11, 5.6), dpi=160)
    fig.patch.set_facecolor("#fcfcfb")
    ax.set_facecolor("#fcfcfb")
    xs = list(range(11))
    if m5["K"] >= 5:
        ax.axhspan(m5["bas"], m5["haut"], color=bleu, alpha=0.13, lw=0, zorder=1)
        ax.axhline(m5["r_moyen"], color=bleu, lw=2, zorder=2)
    ax.axhline(0, color=encre, lw=1, zorder=2)
    ax.axhline(0.22, color=encre2, lw=1, ls=(0, (4, 3)), zorder=2)
    for k in xs:
        bk = blocs[str(k)]
        if bk["valide"]:
            ax.bar(k, bk["R"], width=0.55, color=bleu if k not in (8, 9) else "#1a4f93", zorder=3,
                   edgecolor="#fcfcfb", linewidth=1)
            dy = 0.035 if bk["R"] >= 0 else -0.035
            ax.text(k, bk["R"] + dy, f"{bk['R']:+.2f}".replace(".", ","), ha="center",
                    va="bottom" if bk["R"] >= 0 else "top", fontsize=9, color=encre, zorder=4)
        else:
            ax.text(k, 0.03, "bloc\nnon valide", ha="center", va="bottom", fontsize=8, color=gris)
    ax.set_xticks(xs)
    ax.set_xticklabels([f"{blocs[str(k)]['libelle']}\n(n = {blocs[str(k)]['n']})" for k in xs], fontsize=8.5,
                       color=encre2)
    ax.set_ylim(-1.05, 1.05)
    ax.set_xlim(-0.6, 12.6)
    ax.set_ylabel("R_k : corrélation non centrée correction × erreur, dans le bloc", fontsize=9, color=encre2)
    ax.set_xlabel("Bloc de deux ans (trimestres cibles) ; n = lignes évaluées", fontsize=9, color=encre2)
    ax.tick_params(axis="y", labelsize=8.5, colors=encre2)
    ax.yaxis.grid(True, color=grille, lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(grille)
    if m5["K"] >= 5:
        fr = lambda v: f"{v:+.3f}".replace(".", ",")
        ax.text(10.75, m5["r_moyen"], f"R̄ = {fr(m5['r_moyen'])}\nIC 90 % :\n[{fr(m5['bas'])} ; {fr(m5['haut'])}]",
                fontsize=9, color=encre, va="center", ha="left",
                bbox=dict(facecolor="#fcfcfb", edgecolor="none", pad=1.5))
    ax.text(12.55, 0.235, "0,22 : plus petit effet prédit", fontsize=8, color=encre2, va="bottom", ha="right")
    ax.text(12.55, -0.015, "0 : aucune prévisibilité", fontsize=8, color=encre2, va="top", ha="right")
    ax.set_title("H03 — Statistique principale bloc par bloc (barres), moyenne R̄ (trait) et son intervalle à 90 % "
                 "(bande)\nBlocs 2020-2021 et 2022-2023 en bleu foncé (épisode exclu de la garde r_hors_episode)",
                 fontsize=10, color=encre, loc="left")
    fig.tight_layout()
    fig.savefig(chemin, facecolor=fig.get_facecolor())
    plt.close(fig)


def main():
    temoin, details, lignes = analyse(FICHIER)
    with open(os.path.join(ICI, "temoin.json"), "w", encoding="utf-8") as f:
        json.dump(temoin, f, ensure_ascii=False, indent=1)
    with open(os.path.join(ICI, "analyse_details.json"), "w", encoding="utf-8") as f:
        json.dump(details, f, ensure_ascii=False, indent=1)
    with open(os.path.join(ICI, "analyse_lignes.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(lignes)
    figure(details, os.path.join(ICI, "figure.png"))
    for k, v in temoin.items():
        print(f"{k} = {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
