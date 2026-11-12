#!/usr/bin/env python3
"""H13 — construit H13_analyse.csv à partir de donnees/ seul, selon la préinscription (sections 4 et 5).

Usage :
    python3 construire.py --emploi-seul   # étapes 1 à 6 : écrit emploi_intermediaire.csv (aucun taux lu)
    python3 construire.py                 # étapes 1 à 7 : réécrit l'intermédiaire, puis H13_analyse.csv

Aucun accès réseau. Aucune valeur n'est retouchée à la main.
"""
import datetime
import hashlib
import os
import re
import sys

import numpy as np
import pandas as pd

ICI = os.path.dirname(os.path.abspath(__file__))
DON = os.path.join(ICI, "donnees")
INTER = os.path.join(ICI, "emploi_intermediaire.csv")
SORTIE = os.path.join(ICI, "H13_analyse.csv")
JOURNAL = os.path.join(ICI, "journal.md")
LOT = 12

COLONNES = [
    "date_publication", "mois_reference", "n_mois_nouveaux", "date_millesime_precedent", "date_millesime_3e",
    "emploi_1re_k", "emploi_3e_k", "rev_m1_k", "rev_m2_k", "tendance_12m_k", "d_chomage_pt", "revision_large",
    "extreme", "date_veille", "date_avant_veille", "dgs2_j", "dgs2_veille", "dgs2_avant_veille", "sveny02_j",
    "sveny02_veille", "complet", "principal",
]
COL_EMPLOI = COLONNES[:13]


def note(texte):
    quand = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(JOURNAL, "a", encoding="utf-8") as f:
        f.write(f"- {quand} — {texte}\n")
    print(texte)


def sha(chemin):
    return hashlib.sha256(open(chemin, "rb").read()).hexdigest()


# ---------------------------------------------------------------- D1, D2, D3
def dates_d1():
    h = open(os.path.join(DON, "D1_PAYEMS_downloaddata.html"), encoding="utf-8").read()
    i = h.index('name="form[selected_vintage_dates][]"')
    j = h.index("</select>", i)
    return sorted(set(re.findall(r'<option value="(\d{4}-\d{2}-\d{2})"', h[i:j])))


def lire_lots(serie, prefixe, dates):
    """Lit les lots ALFRED ; contrôle l'en-tête de chacun (n colonnes, dans l'ordre demandé)."""
    cadres = []
    for k in range((len(dates) + LOT - 1) // LOT):
        sous = dates[k * LOT:(k + 1) * LOT]
        chemin = os.path.join(DON, f"{prefixe}_lot_{k + 1:02d}.csv")
        c = pd.read_csv(chemin, dtype=str, keep_default_na=False)
        attendu = ["observation_date"] + [f"{serie}_{d.replace('-', '')}" for d in sous]
        if list(c.columns) != attendu:
            raise SystemExit(f"{chemin} : en-tête inattendu")
        c = c.set_index("observation_date")
        c.columns = sous
        cadres.append(c)
    tout = pd.concat(cadres, axis=1).sort_index()
    tout = tout.replace("", np.nan).astype(float)
    return tout


def mois_plus(m, k):
    """m est un indice entier de mois (année*12 + mois-1)."""
    return m + k


def idx_mois(chaine):  # 'AAAA-MM-01' -> entier
    return int(chaine[:4]) * 12 + int(chaine[5:7]) - 1


def cle_mois(i):  # entier -> 'AAAA-MM-01'
    return f"{i // 12:04d}-{i % 12 + 1:02d}-01"


def construire_emploi():
    toutes = dates_d1()
    fen = [d for d in toutes if "1989-12-01" <= d <= "2026-03-31"]
    bilan = {"d1_total": len(toutes), "d1_fenetre": len(fen), "d1_premiere": fen[0]}

    pay = lire_lots("PAYEMS", "D2_PAYEMS", fen)
    # niveaux entiers ?
    v = pay.values[~np.isnan(pay.values)]
    if not np.all(v == np.round(v)):
        raise SystemExit("PAYEMS : niveaux non entiers")

    def L(j, d):  # niveau du mois j (indice entier) dans le millésime d
        try:
            return pay.at[cle_mois(j), d]
        except KeyError:
            return np.nan

    def D(j, d):  # variation mensuelle à l'intérieur du seul millésime d
        return L(j, d) - L(j - 1, d)

    fin = {d: idx_mois(pay[d].last_valid_index()) for d in fen}

    # Étape 2 : publications et corrections
    pubs, corrections = [], []
    for k, d in enumerate(fen):
        if k == 0 or fin[d] > fin[fen[k - 1]]:
            pubs.append(d)
        else:
            corrections.append(d)
    prec = {pubs[k]: pubs[k - 1] for k in range(1, len(pubs))}
    bilan["n_publications_total"] = len(pubs)
    bilan["corrections"] = corrections

    # D3 : chômage aux dates de publication
    unr = lire_lots("UNRATE", "D3_UNRATE", pubs)

    def U(j, d):
        try:
            return unr.at[cle_mois(j), d]
        except KeyError:
            return np.nan

    # Étape 5 : publications de révision large
    large = {}
    for w in pubs[1:]:
        p = prec[w]
        mp = fin[p]
        large[w] = int(any(L(j, w) != L(j, p) for j in range(mp - 11, mp - 1)))  # j = m'-11 … m'-2
    bilan["publications_revision_large"] = [w for w in pubs if large.get(w, 0) == 1]

    # Étape 3 et 4
    lignes = []
    cible = [d for d in pubs if "1990-01-01" <= d <= "2025-12-31"]
    for v_ in cible:
        p = prec[v_]
        m, mp = fin[v_], fin[p]
        a1 = D(m, v_)
        v3 = next((w for w in pubs if w > v_ and fin[w] >= m + 2), None)
        a3 = D(m, v3) if v3 is not None else np.nan
        r1 = D(mp, v_) - D(mp, p)
        r2 = D(mp - 1, v_) - D(mp - 1, p)
        douze = [D(j, p) for j in range(mp - 11, mp + 1)]
        tend = float(np.median(douze)) if not any(np.isnan(douze)) else np.nan
        du = U(m, v_) - U(m - 1, v_)
        if not np.isnan(du):
            du = round(du, 1)  # les deux taux ont une décimale : retire le seul artefact binaire de la soustraction
        borne = v3 if v3 is not None else pubs[-1]
        rl = int(any(large.get(w, 0) == 1 for w in pubs if v_ <= w <= borne))
        ext = int(abs(a1) > 1000 or (not np.isnan(a3) and abs(a1 - a3) > 500))
        lignes.append({
            "date_publication": v_, "mois_reference": cle_mois(m)[:7], "n_mois_nouveaux": m - mp,
            "date_millesime_precedent": p, "date_millesime_3e": v3 if v3 is not None else "",
            "emploi_1re_k": a1, "emploi_3e_k": a3, "rev_m1_k": r1, "rev_m2_k": r2,
            "tendance_12m_k": tend, "d_chomage_pt": du, "revision_large": rl, "extreme": ext,
        })
    e = pd.DataFrame(lignes, columns=COL_EMPLOI)
    for c in ["emploi_1re_k", "emploi_3e_k", "rev_m1_k", "rev_m2_k"]:
        e[c] = e[c].astype("Int64")
    bilan["n_lignes"] = len(e)
    return e, bilan


def ecrire(df, chemin):
    df.to_csv(chemin, index=False, encoding="utf-8", lineterminator="\n")


# ---------------------------------------------------------------- D4, D5
def ajouter_taux(e):
    d4 = pd.read_csv(os.path.join(DON, "D4_DGS2.csv"), dtype=str, keep_default_na=False)
    if list(d4.columns) != ["observation_date", "DGS2"]:
        raise SystemExit("D4 : colonnes inattendues")
    d4 = d4[d4["DGS2"].str.strip() != ""]
    float(d4["DGS2"].iloc[0])
    C = sorted(d4["observation_date"])
    dgs = dict(zip(d4["observation_date"], d4["DGS2"]))  # chaînes recopiées telles quelles
    pos = {d: i for i, d in enumerate(C)}

    sven = {}
    chemin5 = os.path.join(DON, "D5_feds200628.csv")
    d5_present = os.path.exists(chemin5)
    if d5_present:
        lignes = open(chemin5, encoding="utf-8", errors="replace").read().splitlines()
        deb = next(i for i, l in enumerate(lignes) if l.startswith("Date"))
        ent = lignes[deb].split(",")
        k = ent.index("SVENY02")
        for l in lignes[deb + 1:]:
            ch = l.split(",")
            if len(ch) > k and ch[k] not in ("NA", ""):
                sven[ch[0]] = ch[k]

    import bisect
    veille, avant, j, jv, jav, sj, sv = [], [], [], [], [], [], []
    for d in e["date_publication"]:
        i = bisect.bisect_left(C, d)  # nombre de dates de C strictement avant d
        dv, dav = C[i - 1], C[i - 2]
        veille.append(dv)
        avant.append(dav)
        j.append(dgs.get(d, ""))
        jv.append(dgs[dv])
        jav.append(dgs[dav])
        sj.append(sven.get(d, ""))
        sv.append(sven.get(dv, ""))
    a = e.copy()
    a["date_veille"], a["date_avant_veille"] = veille, avant
    a["dgs2_j"], a["dgs2_veille"], a["dgs2_avant_veille"] = j, jv, jav
    a["sveny02_j"], a["sveny02_veille"] = sj, sv
    present = lambda c: a[c].notna() & (a[c].astype(str) != "")  # noqa: E731
    comp = np.ones(len(a), dtype=bool)
    for c in ["emploi_3e_k", "rev_m1_k", "rev_m2_k", "tendance_12m_k", "d_chomage_pt", "dgs2_j", "dgs2_veille",
              "dgs2_avant_veille"]:
        comp &= present(c).values
    a["complet"] = comp.astype(int)
    a["principal"] = ((a["complet"] == 1) & (a["n_mois_nouveaux"] == 1) & (a["revision_large"] == 0)
                      & (a["extreme"] == 0)).astype(int)
    return a[COLONNES], d5_present


# ---------------------------------------------------------------- contrôles de schéma (section 5)
def controles(chemin):
    a = pd.read_csv(chemin, dtype=str, keep_default_na=False)
    r = {}
    r[1] = list(a.columns) == COLONNES
    num = lambda c: pd.to_numeric(a[c].replace("", np.nan))  # noqa: E731
    dp = pd.to_datetime(a["date_publication"])
    r[2] = (425 <= len(a) <= 435 and a["date_publication"].is_unique and bool((dp.diff().dropna() > pd.Timedelta(0)).all())
            and a["date_publication"].min() >= "1990-01-01" and a["date_publication"].max() <= "2025-12-31")
    mr = pd.to_datetime(a["mois_reference"] + "-01")
    ecart = (dp - mr).dt.days
    r[3] = bool((mr.diff().dropna() > pd.Timedelta(0)).all()) and bool(ecart.between(28, 110).all())
    r[4] = (set(a["n_mois_nouveaux"]) <= {"1", "2"}
            and all(set(a[c]) <= {"0", "1"} for c in ["revision_large", "extreme", "complet", "principal"]))
    r[5] = (bool((a["date_millesime_precedent"] < a["date_publication"]).all())
            and bool(((a["date_millesime_3e"] == "") | (a["date_millesime_3e"] > a["date_publication"])).all())
            and bool((a["date_avant_veille"] < a["date_veille"]).all())
            and bool((a["date_veille"] < a["date_publication"]).all()))
    a1, a3 = num("emploi_1re_k"), num("emploi_3e_k")
    ext = ((a1.abs() > 1000) | (a3.notna() & ((a1 - a3).abs() > 500))).astype(int)
    comp = np.ones(len(a), dtype=bool)
    for c in ["emploi_3e_k", "rev_m1_k", "rev_m2_k", "tendance_12m_k", "d_chomage_pt", "dgs2_j", "dgs2_veille",
              "dgs2_avant_veille"]:
        comp &= (a[c] != "").values
    prin = comp & (a["n_mois_nouveaux"] == "1").values & (a["revision_large"] == "0").values & (ext == 0).values
    r[6] = (bool((ext.astype(str) == a["extreme"]).all()) and bool((comp.astype(int).astype(str) == a["complet"]).all())
            and bool((prin.astype(int).astype(str) == a["principal"]).all()))
    taux = pd.concat([num(c) for c in ["dgs2_j", "dgs2_veille", "dgs2_avant_veille", "sveny02_j", "sveny02_veille"]])
    taux = taux.dropna()
    r[7] = bool((a1.abs() <= 25000).all()) and bool((num("d_chomage_pt").dropna().abs() <= 11).all()) \
        and bool(taux.between(0, 12).all())
    l = a[a["date_publication"] == "1990-02-02"]
    r[8] = (len(l) == 1 and l["mois_reference"].iloc[0] == "1990-01" and l["emploi_1re_k"].iloc[0] == "275"
            and l["date_millesime_3e"].iloc[0] == "1990-04-06" and l["emploi_3e_k"].iloc[0] == "361")
    ej = (num("dgs2_j") - num("sveny02_j")).abs().dropna()
    ev = (num("dgs2_veille") - num("sveny02_veille")).abs().dropna()
    ok9 = bool((ej <= 0.75).all()) and bool((ev <= 0.75).all())
    if len(l) == 1 and l["sveny02_veille"].iloc[0] != "" and l["sveny02_j"].iloc[0] != "":
        ok9 = ok9 and abs(float(l["sveny02_veille"].iloc[0]) - 8.1466) <= 0.0001 \
            and abs(float(l["sveny02_j"].iloc[0]) - 8.2234) <= 0.0001
    r[9] = ok9
    r = {k: bool(v) for k, v in r.items()}
    return r, {"max_ecart_j": float(ej.max()) if len(ej) else None, "max_ecart_veille": float(ev.max()) if len(ev) else None,
               "n_paires_j": int(len(ej)), "n_paires_veille": int(len(ev))}


def main():
    emploi_seul = "--emploi-seul" in sys.argv
    e, bilan = construire_emploi()
    print("Bilan étapes 1-5 :")
    for k, v in bilan.items():
        if isinstance(v, list) and len(v) > 12:
            print(f"  {k} : {len(v)} dates")
        else:
            print(f"  {k} : {v}")
    ancien = sha(INTER) if os.path.exists(INTER) else None
    ecrire(e, INTER)
    h = sha(INTER)
    if emploi_seul:
        d4 = os.path.exists(os.path.join(DON, "D4_DGS2.csv"))
        d5 = os.path.exists(os.path.join(DON, "D5_feds200628.csv"))
        note(f"Étape 6 : `emploi_intermediaire.csv` écrit ({len(e)} lignes), sha256 `{h}`. "
             f"D4 présent dans donnees/ : {'oui' if d4 else 'non'} ; D5 présent : {'oui' if d5 else 'non'}.")
        return
    if ancien is not None and ancien != h:
        note(f"ATTENTION : `emploi_intermediaire.csv` reconstruit diffère de la version précédente ({ancien} -> {h}).")
    a, d5_present = ajouter_taux(e)
    ecrire(a, SORTIE)
    r, info = controles(SORTIE)
    print("Contrôles de schéma :", r)
    print("Alignement DGS2/SVENY02 :", info)
    note(f"Étape 7 : `H13_analyse.csv` écrit ({len(a)} lignes), sha256 `{sha(SORTIE)}` ; intermédiaire sha256 `{h}` "
         f"(identique à l'étape 6 : {'oui' if ancien == h else 'non'}) ; D5 présent : {'oui' if d5_present else 'non'} ; "
         f"contrôles de schéma 1 à 9 : {'tous passent' if all(r.values()) else 'ÉCHEC ' + str([k for k, v in r.items() if not v])}.")


if __name__ == "__main__":
    main()
