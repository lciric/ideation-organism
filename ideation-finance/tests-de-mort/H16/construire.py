#!/usr/bin/env python3
"""H16 — construit analyse_H16.csv à partir de donnees/ seul (préinscription §§ 4 et 5).

Usage : python3 -I construire.py
Lit   : donnees/Dataset_EA-MPD.xlsx, DCOILBRENTEU.csv, DEXUSEU.csv, feds200628.csv, Europe_3_Factors_Daily_CSV.zip
Écrit : analyse_H16.csv, construire.log (journal : filtres, contrôles, lignes brutes de trois réunions tirées au sort)
Aucune valeur n'est imputée ni reportée ; aucun prédicteur n'utilise une observation du jour de la réunion ou d'après.
"""
import bisect
import csv
import datetime as dt
import io
import math
import os
import sys
import zipfile

import numpy as np
import openpyxl

ICI = os.path.dirname(os.path.abspath(__file__))
DON = os.path.join(ICI, "donnees")
SORTIE = os.path.join(ICI, "analyse_H16.csv")
JOURNAL = os.path.join(ICI, "construire.log")

DATE_MAX = dt.date(2025, 10, 30)      # base figée à cette date (§ 4.1, A10)
DATE_FIN_ESTIM = dt.date(2009, 12, 3)  # dernière réunion « estimation »
PLANCHER = 0.25                         # point de base (A7)
HORIZON = 60                            # observations valides
RETARD_MAX = 10                         # jours calendaires (§ 4.3, règle ii)
GRAINE_TIRAGE = 16                      # tirage au sort des trois réunions citées dans le compte rendu

COLONNES = ["rang", "date_reunion", "date_reunion_prec", "d_ois1y_pb", "sigma16_pb", "cible_norm",
            "cible_prec_norm", "act_eu_60j_pct", "brent_60j_pct", "eurusd_60j_pct", "us2a_60j_pp",
            "date_fin_act", "date_fin_brent", "date_fin_eurusd", "date_fin_us2a", "echantillon"]

_lignes_journal = []


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    _lignes_journal.append(s)


# --------------------------------------------------------------------------- lecture des fichiers bruts
def lire_eampd():
    """Feuille « Monetary Event Window » : colonnes date (1) et OIS_1Y (6). Renvoie [(date, valeur|None)], et le journal des filtres."""
    wb = openpyxl.load_workbook(os.path.join(DON, "Dataset_EA-MPD.xlsx"), read_only=True, data_only=True)
    ws = wb["Monetary Event Window"]
    lignes = list(ws.iter_rows(min_row=1, max_col=60, values_only=True))
    entete = lignes[0]
    assert entete[0] == "date", entete[:3]
    assert entete[5] == "OIS_1Y", entete[:8]
    n_brut = len(lignes) - 1
    reunions, n_vides, n_texte = [], 0, 0
    for r in lignes[1:]:
        d = r[0]
        if d is None or (isinstance(d, str) and d.strip() == ""):
            n_vides += 1
            continue
        if isinstance(d, dt.datetime):
            date = d.date()
        elif isinstance(d, dt.date):
            date = d
        elif isinstance(d, str):
            date = dt.datetime.strptime(d.strip(), "%d/%m/%Y").date()  # texte jj/mm/aaaa (rangs 300 à 315)
            n_texte += 1
        else:
            raise ValueError(f"date illisible : {d!r}")
        v = r[5]
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(float(v)):
            v = None  # donnée manquante : pas d'imputation
        else:
            v = float(v)
        reunions.append((date, v))
    n_dates = len(reunions)
    reunions = [x for x in reunions if x[0] <= DATE_MAX]
    n_apres = n_dates - len(reunions)
    reunions.sort(key=lambda x: x[0])
    dates = [x[0] for x in reunions]
    assert len(set(dates)) == len(dates), "doublon de date dans EA-MPD"
    log(f"EA-MPD : {n_brut} lignes sous l'en-tête ; {n_vides} lignes sans date écartées ; {n_dates} réunions datées "
        f"(dont {n_texte} dates en texte jj/mm/aaaa) ; {n_apres} réunions postérieures au {DATE_MAX} écartées ; "
        f"{len(reunions)} réunions retenues ; OIS_1Y manquant : {sum(1 for x in reunions if x[1] is None)}")
    return reunions


def lire_fred(nom, colonne):
    """CSV FRED : observation_date,<colonne>. Renvoie (dates, valeurs) des observations valides, et les lignes brutes par date."""
    dates, vals, brutes = [], [], {}
    n_tot = n_manq = 0
    with open(os.path.join(DON, nom), newline="") as f:
        lect = csv.reader(f)
        entete = next(lect)
        assert entete == ["observation_date", colonne], entete
        for r in lect:
            if not r:
                continue
            n_tot += 1
            d = dt.date.fromisoformat(r[0])
            brutes[d] = ",".join(r)
            x = r[1].strip()
            if x in ("", ".", "NA"):
                n_manq += 1
                continue
            dates.append(d)
            vals.append(float(x))
    assert dates == sorted(dates) and len(set(dates)) == len(dates)
    log(f"{nom} : {n_tot} lignes de données, {n_manq} manquantes, {len(dates)} valides, de {dates[0]} à {dates[-1]}")
    return dates, vals, brutes


def lire_sveny02():
    """Courbe Gürkaynak-Sack-Wright : 9 lignes de préambule, en-tête ligne 10, colonne SVENY02, manquant = NA."""
    dates, vals, brutes = [], [], {}
    n_tot = n_manq = 0
    with open(os.path.join(DON, "feds200628.csv"), newline="") as f:
        lect = csv.reader(f)
        for _ in range(9):
            next(lect)
        entete = next(lect)
        assert entete[0] == "Date", entete[:2]
        k = entete.index("SVENY02")
        assert k == 69, k  # 70e colonne
        for r in lect:
            if not r or not r[0].strip():
                continue
            n_tot += 1
            d = dt.date.fromisoformat(r[0])
            x = r[k].strip()
            brutes[d] = f"{r[0]},…,SVENY02={r[k]}"
            if x in ("", "NA"):
                n_manq += 1
                continue
            dates.append(d)
            vals.append(float(x))
    ordre = sorted(range(len(dates)), key=lambda i: dates[i])
    dates = [dates[i] for i in ordre]
    vals = [vals[i] for i in ordre]
    assert len(set(dates)) == len(dates)
    log(f"feds200628.csv : {n_tot} lignes de données, {n_manq} SVENY02 manquants (NA), {len(dates)} valides, "
        f"de {dates[0]} à {dates[-1]}")
    return dates, vals, brutes


def lire_french():
    """Europe_3_Factors_Daily.csv : 6 lignes de préambule, en-tête ligne 7 ; r = Mkt-RF + RF (en %) ; manquant = -99.99."""
    z = zipfile.ZipFile(os.path.join(DON, "Europe_3_Factors_Daily_CSV.zip"))
    noms = z.namelist()
    assert noms == ["Europe_3_Factors_Daily.csv"], noms
    texte = z.read(noms[0]).decode("latin-1")
    lignes = texte.splitlines()
    log(f"Ken French : millésime = {lignes[0].strip()!r}")
    entete = [c.strip() for c in lignes[6].split(",")]
    assert entete == ["", "Mkt-RF", "SMB", "HML", "RF"], entete
    dates, vals, brutes = [], [], {}
    n_tot = n_manq = 0
    for l in lignes[7:]:
        c = [x.strip() for x in l.split(",")]
        if len(c) < 5 or not (len(c[0]) == 8 and c[0].isdigit()):
            if l.strip():
                log(f"Ken French : ligne non reconnue ignorée : {l!r}")
            continue
        n_tot += 1
        d = dt.datetime.strptime(c[0], "%Y%m%d").date()
        brutes[d] = l
        mkt, rf = float(c[1]), float(c[4])
        if mkt <= -99.0 or rf <= -99.0:
            n_manq += 1
            continue
        dates.append(d)
        vals.append(mkt + rf)
    assert dates == sorted(dates) and len(set(dates)) == len(dates)
    log(f"Ken French : {n_tot} lignes de données, {n_manq} manquantes (-99.99), {len(dates)} valides, "
        f"de {dates[0]} à {dates[-1]}")
    return dates, vals, brutes


# --------------------------------------------------------------------------- prédicteurs (§ 4.3)
def position(dates, D):
    """Indice i de la dernière observation valide de date STRICTEMENT inférieure à D ; -1 s'il n'y en a pas."""
    return bisect.bisect_left(dates, D) - 1


def predicteur(dates, vals, D, genre):
    """Renvoie (valeur|None, date_fin|None, i). genre ∈ {'somme_log', 'log_ratio', 'difference'}."""
    i = position(dates, D)
    if i < 0:
        return None, None, i
    date_fin = dates[i]
    assert date_fin < D  # antériorité stricte : rien du jour de la réunion ni d'après
    if (D - date_fin).days > RETARD_MAX or i - HORIZON < 0:
        return None, date_fin, i  # règle (ii) : prédicteur manquant ; la date de v[i] reste écrite (règle i)
    if genre == "somme_log":
        x = 100.0 * math.fsum(math.log1p(vals[j] / 100.0) for j in range(i - HORIZON + 1, i + 1))
    elif genre == "log_ratio":
        x = 100.0 * math.log(vals[i] / vals[i - HORIZON])
    elif genre == "difference":
        x = vals[i] - vals[i - HORIZON]
    else:
        raise ValueError(genre)
    return x, date_fin, i


def f(x):
    """Nombre → texte : 17 chiffres significatifs, notation scientifique (au moins huit chiffres significatifs écrits)."""
    return "" if x is None else f"{x:.16e}"


def main():
    reunions = lire_eampd()
    n = len(reunions)
    series = {
        "act": lire_french() + ("somme_log",),
        "brent": lire_fred("DCOILBRENTEU.csv", "DCOILBRENTEU") + ("log_ratio",),
        "eurusd": lire_fred("DEXUSEU.csv", "DEXUSEU") + ("log_ratio",),
        "us2a": lire_sveny02() + ("difference",),
    }
    col_pred = {"act": "act_eu_60j_pct", "brent": "brent_60j_pct", "eurusd": "eurusd_60j_pct", "us2a": "us2a_60j_pp"}

    dates = [r[0] for r in reunions]
    d_ois = [r[1] for r in reunions]

    # Cible normalisée (§ 5, A7)
    sigma, cible, plancher_actif = [None] * n, [None] * n, [False] * n
    for k in range(n):  # k = rang - 1
        if k + 1 <= 16:
            continue
        prec = d_ois[k - 16:k]
        if any(v is None for v in prec):
            continue  # cible manquante dans la fenêtre : pas d'imputation
        s = float(np.std(np.array(prec, dtype=float), ddof=1))
        sigma[k] = max(s, PLANCHER)
        plancher_actif[k] = s < PLANCHER
        if d_ois[k] is not None:
            cible[k] = d_ois[k] / sigma[k]

    lignes, indices = [], []
    for k in range(n):
        rang, D = k + 1, dates[k]
        L = {c: "" for c in COLONNES}
        L["rang"] = str(rang)
        L["date_reunion"] = D.isoformat()
        L["date_reunion_prec"] = dates[k - 1].isoformat() if k > 0 else ""
        L["d_ois1y_pb"] = f(d_ois[k])
        L["sigma16_pb"] = f(sigma[k])
        L["cible_norm"] = f(cible[k])
        cprec = cible[k - 1] if rang > 17 else None
        L["cible_prec_norm"] = f(cprec)
        vals_pred, idx = {}, {}
        for cle, (sd, sv, _br, genre) in series.items():
            x, dfin, i = predicteur(sd, sv, D, genre)
            vals_pred[cle] = x
            idx[cle] = i
            L[col_pred[cle]] = f(x)
            L["date_fin_" + cle] = dfin.isoformat() if dfin is not None else ""
        if rang <= 17:
            ech = "rodage"
        elif cible[k] is None or cprec is None or any(v is None for v in vals_pred.values()):
            ech = "exclue"
        elif D <= DATE_FIN_ESTIM:
            ech = "estimation"
        else:
            ech = "evaluation"
        L["echantillon"] = ech
        lignes.append(L)
        indices.append(idx)

    with open(SORTIE, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLONNES, lineterminator="\n")
        w.writeheader()
        w.writerows(lignes)

    # ----------------------------------------------------------------------- journal des filtres
    eff = {e: sum(1 for L in lignes if L["echantillon"] == e) for e in ("rodage", "estimation", "evaluation", "exclue")}
    log(f"Lignes écrites : {len(lignes)} ; effectifs : {eff}")
    log(f"Repères : rang 1 = {dates[0]}, rang 17 = {dates[16]}, rang 18 = {dates[17]}, rang 168 = {dates[167]}, "
        f"rang 169 = {dates[168]}, rang {n} = {dates[-1]}")
    for cle in series:
        manq = [L["rang"] for L in lignes if L[col_pred[cle]] == ""]
        log(f"Prédicteur {col_pred[cle]} manquant aux rangs : {manq if manq else 'aucun'}")
    util = [k for k in range(n) if lignes[k]["echantillon"] in ("estimation", "evaluation")]
    log(f"Plancher de 0,25 pb actif : {sum(plancher_actif)} réunions de rang ≥ 17 "
        f"(rangs {[k + 1 for k in range(n) if plancher_actif[k]]}) ; dont lignes utilisables : "
        f"{sum(plancher_actif[k] for k in util)} ; dont évaluation : "
        f"{sum(plancher_actif[k] for k in util if lignes[k]['echantillon'] == 'evaluation')}")
    for cle in series:
        sd = series[cle][0]
        ecarts = [(dates[k] - sd[indices[k][cle]]).days for k in util]
        log(f"Retard (jours calendaires entre date_fin_{cle} et la réunion), lignes utilisables : "
            f"min {min(ecarts)}, max {max(ecarts)}")
        assert min(ecarts) >= 1

    # ----------------------------------------------------------------------- contrôle d'antériorité par force brute
    # Recalcul indépendant (sans bisect) : la dernière observation valide < D, par balayage, pour chaque ligne utilisable.
    for cle, (sd, sv, _br, genre) in series.items():
        for k in util:
            D = dates[k]
            cand = [d for d in sd if d < D]
            assert cand[-1].isoformat() == lignes[k]["date_fin_" + cle]
            assert all(d >= D for d in sd[len(cand):])
    log("Contrôle d'antériorité par balayage complet : réussi pour les quatre séries sur toutes les lignes utilisables.")

    # ----------------------------------------------------------------------- trois réunions tirées au sort
    rng = np.random.default_rng(GRAINE_TIRAGE)
    tirage = sorted(int(x) for x in rng.choice(util, size=3, replace=False))
    log(f"\nTrois réunions tirées au sort parmi les {len(util)} lignes utilisables "
        f"(numpy default_rng({GRAINE_TIRAGE}).choice, sans remise) : rangs {[k + 1 for k in tirage]}")
    for k in tirage:
        D, L = dates[k], lignes[k]
        log(f"\n--- rang {k + 1}, réunion du {D} ({L['echantillon']}) ---")
        log(f"  EA-MPD : OIS_1Y = {d_ois[k]!r} pb ; 16 précédentes = {d_ois[k - 16:k]} ; sigma16 = {sigma[k]!r} ; "
            f"cible_norm = {cible[k]!r} ; cible_prec_norm = {cible[k - 1]!r}")
        for cle, (sd, sv, br, genre) in series.items():
            i = indices[k][cle]
            log(f"  {col_pred[cle]} = {L[col_pred[cle]]}")
            if genre == "somme_log":
                log(f"    première des 60 lignes (j = i−59) : {br[sd[i - 59]]!r}")
                log(f"    dernière des 60 lignes (j = i)    : {br[sd[i]]!r}")
            else:
                log(f"    ligne v[i−60] : {br[sd[i - 60]]!r}")
                log(f"    ligne v[i]    : {br[sd[i]]!r}")
            suiv = sd[i + 1] if i + 1 < len(sd) else None
            log(f"    observation valide suivante (non utilisée) : {suiv} (≥ {D} : {suiv is None or suiv >= D})")

    with open(JOURNAL, "w", encoding="utf-8") as fh:
        fh.write("\n".join(_lignes_journal) + "\n")


if __name__ == "__main__":
    sys.exit(main())
