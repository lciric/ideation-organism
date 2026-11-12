#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F04-bis — construction du fichier d'analyse.

Reconstruit `F04-bis_analyse.csv` à partir des seuls fichiers bruts de `donnees/` :
  A  = donnees/F04_analyse.csv                 (copie octet pour octet de tests-de-mort/F04/F04_analyse.csv)
  B  = donnees/fy2021-mc-vs-hs-combined.csv    (fichier des deux méthodes, Trésor)
  C  = donnees/DGS10.csv                       (copie du fichier brut du premier test ; sert uniquement à
                                                compter les jours du calendrier C, aucun taux n'en est tiré)

Toutes les valeurs sont recopiées comme chaînes de caractères : aucun arrondi, aucun reformatage.
Lancer :  python3 -I construire.py
"""
import csv
import datetime as dt
import hashlib
import io
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
DON = os.path.join(ICI, "donnees")
CHEMIN_A = os.path.join(DON, "F04_analyse.csv")
CHEMIN_B = os.path.join(DON, "fy2021-mc-vs-hs-combined.csv")
CHEMIN_C = os.path.join(DON, "DGS10.csv")
CHEMIN_A_ORIGINE = os.path.join(ICI, "..", "F04", "F04_analyse.csv")
SORTIE = os.path.join(ICI, "F04-bis_analyse.csv")
JOURNAL = os.path.join(ICI, "construire_journal.json")

DEBUT = dt.date(2020, 10, 1)
FIN = dt.date(2021, 9, 30)

COLONNES_B_ATTENDUES = (
    ["date"]
    + [f"nominal_hs_cmt_{k}" for k in ("1mo", "2mo", "3mo", "6mo", "1yr", "2yr", "3yr", "5yr", "7yr", "10yr", "20yr", "30yr")]
    + [f"nominal_mc_cmt_{k}" for k in ("1mo", "2mo", "3mo", "6mo", "1yr", "2yr", "3yr", "5yr", "7yr", "10yr", "20yr", "30yr")]
    + [f"real_hs_cmt_{k}" for k in ("5yr", "7yr", "10yr", "20yr", "30yr")]
    + [f"real_mc_cmt_{k}" for k in ("5yr", "7yr", "10yr", "20yr", "30yr")]
)
COLONNES_B_UTILISEES = ["date"] + [f"nominal_{m}_cmt_{e}yr" for m in ("hs", "mc") for e in (10, 20, 30)]

COLONNES_SORTIE = [
    "id_ligne", "cusip", "terme_api", "echeance", "date_adjudication", "mois",
    "date_j", "date_jm5", "date_jp5",
    "cmt_jm5", "cmt_j", "cmt_jp5",
    "gsw_jm5", "gsw_j", "gsw_jp5",
    "hs_jm5", "hs_j", "hs_jp5",
    "mc_jm5", "mc_j", "mc_jp5",
    "dans_exercice", "complet", "fenetre_propre",
]
TAUX = COLONNES_SORTIE[9:21]
SUFFIXES = ("jm5", "j", "jp5")


def sha256(chemin):
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def arret(message):
    print("ARRÊT : " + message, file=sys.stderr)
    sys.exit(1)


def est_nombre(s):
    try:
        x = float(s)
    except (TypeError, ValueError):
        return False
    return x == x and abs(x) != float("inf")


def lire_date_b(texte, ordre):
    """ordre = 'MJ' (mois/jour/année) ou 'JM' (jour/mois/année). Renvoie une date ou None."""
    morceaux = texte.strip().split("/")
    if len(morceaux) != 3 or not all(m.isdigit() for m in morceaux):
        return None
    a, b, an = (int(m) for m in morceaux)
    mois, jour = (a, b) if ordre == "MJ" else (b, a)
    try:
        return dt.date(an, mois, jour)
    except ValueError:
        return None


def main():
    journal = {"date_construction_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

    # ---------------------------------------------------------------- fichiers
    for chemin in (CHEMIN_A, CHEMIN_B, CHEMIN_C):
        if not os.path.isfile(chemin) or os.path.getsize(chemin) == 0:
            arret(f"fichier absent ou vide : {chemin} (pas de source de remplacement)")
    journal["sha256"] = {os.path.basename(c): sha256(c) for c in (CHEMIN_A, CHEMIN_B, CHEMIN_C)}
    if os.path.isfile(CHEMIN_A_ORIGINE):
        journal["sha256_A_origine_F04"] = sha256(CHEMIN_A_ORIGINE)
        if journal["sha256_A_origine_F04"] != journal["sha256"]["F04_analyse.csv"]:
            arret("la copie de A dans donnees/ diffère de tests-de-mort/F04/F04_analyse.csv")

    # ---------------------------------------------------------------- fichier B
    brut = open(CHEMIN_B, "rb").read()
    journal["B_marque_ordre_octets"] = int(brut[:3] == b"\xef\xbb\xbf")
    journal["B_fins_de_ligne_CRLF"] = brut.count(b"\r\n")
    journal["B_fins_de_ligne_LF_total"] = brut.count(b"\n")
    lignes_b = list(csv.reader(io.StringIO(brut.decode("utf-8-sig"), newline="")))
    entete_b = lignes_b[0]
    donnees_b = [l for l in lignes_b[1:] if any(c.strip() for c in l)]
    journal["B_n_colonnes"] = len(entete_b)
    journal["B_n_lignes_donnees"] = len(donnees_b)
    if entete_b != COLONNES_B_ATTENDUES:
        arret("les colonnes de B diffèrent de celles lues par le rédacteur (35 colonnes attendues)")
    for c in COLONNES_B_UTILISEES:
        if entete_b.count(c) != 1:
            arret(f"colonne de B absente ou en double : {c}")
    idx = {c: entete_b.index(c) for c in COLONNES_B_UTILISEES}

    # Format des dates : on retient la lecture pour laquelle TOUTES les dates tombent dans l'exercice.
    lectures_valides = []
    for ordre in ("MJ", "JM"):
        dates = [lire_date_b(l[idx["date"]], ordre) for l in donnees_b]
        if all(d is not None and DEBUT <= d <= FIN for d in dates):
            lectures_valides.append(ordre)
    journal["B_lectures_de_date_valides"] = lectures_valides
    if len(lectures_valides) != 1:
        arret(f"format de date de B : {len(lectures_valides)} lecture(s) valide(s) ; le fichier d'analyse n'est pas construit")
    ordre = lectures_valides[0]
    journal["B_format_date"] = "mois/jour/année (M/J/AAAA, sans zéro initial)" if ordre == "MJ" else "jour/mois/année"

    table_b = {}
    for l in donnees_b:
        d = lire_date_b(l[idx["date"]], ordre)
        if d in table_b:
            arret(f"date en double dans B : {d}")
        table_b[d] = l
    dates_b = sorted(table_b)
    journal["B_n_dates"] = len(dates_b)
    journal["B_premiere_date"] = dates_b[0].isoformat()
    journal["B_derniere_date"] = dates_b[-1].isoformat()
    journal["B_dates_en_ordre_croissant_dans_le_fichier"] = int(
        [lire_date_b(l[idx["date"]], ordre) for l in donnees_b] == dates_b)

    # Décimales et cellules vides des six colonnes utilisées (constat, pas de calcul sur les taux).
    decimales = {}
    for c in COLONNES_B_UTILISEES[1:]:
        compte = {}
        for l in donnees_b:
            v = l[idx[c]].strip()
            if v == "":
                cle = "vide"
            elif not est_nombre(v):
                cle = "non numérique"
            else:
                cle = str(len(v.split(".")[1]) if "." in v else 0) + " décimale(s)"
            compte[cle] = compte.get(cle, 0) + 1
        decimales[c] = compte
    journal["B_decimales_par_colonne"] = decimales
    journal["B_decimales_max"] = max(
        int(k.split()[0]) for cpt in decimales.values() for k in cpt if k[0].isdigit())

    # ---------------------------------------------------------------- calendrier C
    with open(CHEMIN_C, newline="", encoding="utf-8") as f:
        lect = csv.reader(f)
        entete_c = next(lect)
        if entete_c != ["observation_date", "DGS10"]:
            arret("en-tête inattendu dans DGS10.csv")
        cal = []
        for l in lect:
            if len(l) >= 2 and est_nombre(l[1].strip()):
                cal.append(dt.date.fromisoformat(l[0]))
    cal_exercice = sorted(d for d in cal if DEBUT <= d <= FIN)
    journal["C_n_jours_dans_exercice"] = len(cal_exercice)
    journal["C_jours_absents_de_B"] = [d.isoformat() for d in cal_exercice if d not in table_b]
    journal["B_dates_absentes_de_C"] = [d.isoformat() for d in dates_b if d not in set(cal_exercice)]

    # ---------------------------------------------------------------- fichier A
    with open(CHEMIN_A, newline="", encoding="utf-8") as f:
        lect = csv.DictReader(f)
        entete_a = lect.fieldnames
        lignes_a = list(lect)
    requis_a = ["id_ligne", "type_ligne", "cusip", "terme_api", "echeance", "principal", "date_adjudication", "mois",
                "date_j", "date_jm5", "date_jp5", "cmt_jm5", "cmt_j", "cmt_jp5", "gsw_jm5", "gsw_j", "gsw_jp5",
                "complet", "fenetre_propre"]
    for c in requis_a:
        if c not in entete_a:
            arret(f"colonne absente de A : {c}")
    journal["A_n_lignes"] = len(lignes_a)

    # Étape 1 de la règle d'échantillon.
    etape1 = [l for l in lignes_a
              if l["type_ligne"] == "reelle" and l["principal"] == "1"
              and DEBUT <= dt.date.fromisoformat(l["date_adjudication"]) <= FIN]
    journal["etape1_n_lignes"] = len(etape1)

    sortie = []
    for l in etape1:
        ech = l["echeance"]
        r = {c: l[c] for c in ("id_ligne", "cusip", "terme_api", "echeance", "date_adjudication", "mois",
                               "date_j", "date_jm5", "date_jp5",
                               "cmt_jm5", "cmt_j", "cmt_jp5", "gsw_jm5", "gsw_j", "gsw_jp5")}
        for s in SUFFIXES:
            d = dt.date.fromisoformat(l["date_" + s])
            hs = mc = ""
            # Une date hors de l'exercice n'est jamais utilisée, même si B la contenait.
            if DEBUT <= d <= FIN and d in table_b and ech in ("10", "20", "30"):
                hs = table_b[d][idx[f"nominal_hs_cmt_{ech}yr"]].strip()
                mc = table_b[d][idx[f"nominal_mc_cmt_{ech}yr"]].strip()
                if not est_nombre(hs):
                    hs = ""
                if not est_nombre(mc):
                    mc = ""
            r["hs_" + s] = hs
            r["mc_" + s] = mc
        jm5 = dt.date.fromisoformat(l["date_jm5"])
        jp5 = dt.date.fromisoformat(l["date_jp5"])
        r["dans_exercice"] = "1" if (jm5 >= DEBUT and jp5 <= FIN) else "0"
        r["complet"] = "1" if all(r[c].strip() != "" and est_nombre(r[c]) for c in TAUX) else "0"
        r["fenetre_propre"] = l["fenetre_propre"]
        sortie.append(r)

    sortie.sort(key=lambda r: (r["date_adjudication"], int(r["echeance"])))

    with open(SORTIE, "w", newline="", encoding="utf-8") as f:
        ecr = csv.DictWriter(f, fieldnames=COLONNES_SORTIE, lineterminator="\n")
        ecr.writeheader()
        ecr.writerows(sortie)

    # ---------------------------------------------------------------- comptes par filtre
    def n(pred):
        return sum(1 for r in sortie if pred(r))

    journal["filtres"] = {
        "etape1_reelle_principal_exercice": len(sortie),
        "dans_exercice_1": n(lambda r: r["dans_exercice"] == "1"),
        "dans_exercice_1_et_complet_1": n(lambda r: r["dans_exercice"] == "1" and r["complet"] == "1"),
        "P_dans_exercice_complet_fenetre_propre": n(
            lambda r: r["dans_exercice"] == "1" and r["complet"] == "1" and r["fenetre_propre"] == "1"),
        "complet_A_egal_1 (six taux du premier test)": sum(1 for l in etape1 if l["complet"] == "1"),
        "fenetre_propre_1": n(lambda r: r["fenetre_propre"] == "1"),
    }
    P = [r for r in sortie if r["dans_exercice"] == "1" and r["complet"] == "1" and r["fenetre_propre"] == "1"]
    journal["P_n_mois"] = len({r["mois"] for r in P})
    journal["P_par_echeance"] = {e: sum(1 for r in P if r["echeance"] == e) for e in ("10", "20", "30")}
    journal["lignes_hors_P"] = [
        {"id_ligne": r["id_ligne"], "dans_exercice": r["dans_exercice"], "complet": r["complet"],
         "fenetre_propre": r["fenetre_propre"], "date_jm5": r["date_jm5"], "date_jp5": r["date_jp5"]}
        for r in sortie if r not in P]
    journal["dates_adjudication"] = [[r["date_adjudication"], int(r["echeance"])] for r in sortie]
    journal["taux_manquants_dans_exercice"] = [
        {"id_ligne": r["id_ligne"], "colonne": c}
        for r in sortie for c in TAUX
        if r[c] == "" and not (c[:2] in ("hs", "mc") and not (
            DEBUT <= dt.date.fromisoformat(r["date_" + c.split("_")[1]]) <= FIN))]

    # ---------------------------------------------------------------- contrôles de schéma (section 4)
    journal["controles"] = controles_schema(SORTIE)
    journal["schema_ok"] = int(all(v["ok"] for v in journal["controles"].values()))

    with open(JOURNAL, "w", encoding="utf-8") as f:
        json.dump(journal, f, ensure_ascii=False, indent=2)
    print(json.dumps(journal, ensure_ascii=False, indent=2))
    print("sha256 du fichier d'analyse :", sha256(SORTIE))


def controles_schema(chemin):
    """Les neuf contrôles de la section 4, exécutés sur le fichier d'analyse relu depuis le disque."""
    brut = open(chemin, "rb").read()
    sans_bom = brut[:3] != b"\xef\xbb\xbf"
    lignes = list(csv.reader(io.StringIO(brut.decode("utf-8"), newline="")))
    entete, corps = lignes[0], lignes[1:]
    res = {}
    res["1_colonnes"] = {"ok": entete == COLONNES_SORTIE and sans_bom and all(len(l) == 24 for l in corps)}
    L = [dict(zip(entete, l)) for l in corps]

    def f(x):
        return float(x)

    ids = [r["id_ligne"] for r in L]
    res["2_domaines"] = {"ok": len(set(ids)) == len(ids)
                         and all(r["echeance"] in ("10", "20", "30") for r in L)
                         and all(r[c] in ("0", "1") for r in L for c in ("dans_exercice", "complet", "fenetre_propre"))}
    D = dt.date.fromisoformat
    res["3_dates"] = {"ok": all(
        D(r["date_jm5"]) < D(r["date_j"]) < D(r["date_jp5"]) and r["date_j"] == r["date_adjudication"]
        and DEBUT <= D(r["date_adjudication"]) <= FIN and r["mois"] == r["date_adjudication"][:7] for r in L)}
    res["4_dans_exercice"] = {"ok": all(
        (r["dans_exercice"] == "1") == (D(r["date_jm5"]) >= DEBUT and D(r["date_jp5"]) <= FIN) for r in L)}
    res["5_complet"] = {"ok": all((r["complet"] == "1") == all(r[c] != "" for c in TAUX) for r in L)}
    bornes = all(-1 <= f(r[c]) <= 20 for r in L for c in TAUX if r[c] != "")
    cg = [abs(f(r["cmt_" + s]) - f(r["gsw_" + s])) for r in L for s in SUFFIXES
          if r["cmt_" + s] != "" and r["gsw_" + s] != ""]
    res["6_bornes"] = {"ok": bornes and all(x <= 1 for x in cg), "max_abs_cmt_moins_gsw": max(cg)}
    hm = [abs(f(r["hs_" + s]) - f(r["mc_" + s])) for r in L for s in SUFFIXES
          if r["hs_" + s] != "" and r["mc_" + s] != ""]
    res["7_hs_mc"] = {"ok": all(x <= 0.25 for x in hm) and any(x > 0 for x in hm),
                      "max_abs_hs_moins_mc": max(hm), "n_paires": len(hm), "n_paires_differentes": sum(x > 0 for x in hm)}
    hc = [abs(f(r["hs_" + s]) - f(r["cmt_" + s])) for r in L for s in SUFFIXES
          if r["hs_" + s] != "" and r["cmt_" + s] != ""]
    res["8_hs_egal_fred"] = {"ok": all(x <= 0.0051 for x in hc), "max_abs_hs_moins_cmt": max(hc),
                             "n_paires": len(hc), "n_depassements": sum(x > 0.0051 for x in hc)}
    n_ex = sum(r["dans_exercice"] == "1" for r in L)
    res["9_comptes"] = {"ok": len(L) == 24 and 20 <= n_ex <= 24, "n_lignes": len(L), "n_dans_exercice": n_ex}
    return res


if __name__ == "__main__":
    main()
