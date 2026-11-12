#!/usr/bin/env python3
"""F04 — construction du fichier d'analyse F04_analyse.csv à partir de donnees/ seul.

Suit la préinscription scellée (sections 4 et 5). Aucun accès réseau.
Usage : python3 -I construire.py
"""
import csv
import json
import os
import sys
from bisect import bisect_left
from collections import Counter, defaultdict

ICI = os.path.dirname(os.path.abspath(__file__))
DON = os.path.join(ICI, "donnees")
SORTIE = os.path.join(ICI, "F04_analyse.csv")
JOURNAL = os.path.join(ICI, "construire_journal.json")

ECHEANCES = [2, 3, 5, 7, 10, 20, 30]
TERMES = {  # security_term -> (echeance, reouverture)
    "2-Year": (2, 0), "3-Year": (3, 0), "5-Year": (5, 0), "7-Year": (7, 0),
    "10-Year": (10, 0), "20-Year": (20, 0), "30-Year": (30, 0),
    "9-Year 10-Month": (10, 1), "9-Year 11-Month": (10, 1),
    "19-Year 10-Month": (20, 1), "19-Year 11-Month": (20, 1),
    "29-Year 10-Month": (30, 1), "29-Year 11-Month": (30, 1),
}
ATTENDU_TERMES = {
    "2-Year": 201, "3-Year": 201, "5-Year": 201, "7-Year": 201,
    "10-Year": 67, "20-Year": 26, "30-Year": 67,
    "9-Year 10-Month": 67, "9-Year 11-Month": 68,
    "19-Year 10-Month": 25, "19-Year 11-Month": 27,
    "29-Year 10-Month": 67, "29-Year 11-Month": 67,
}
CHAMPS_D1 = ["auction_date", "security_type", "security_term", "original_security_term",
             "reopening", "inflation_index_security", "floating_rate", "offering_amt",
             "cusip", "issue_date", "maturity_date"]
COLONNES = ["id_ligne", "type_ligne", "cusip", "terme_api", "echeance", "reouverture",
            "principal", "date_adjudication", "mois", "montant_offert_mds", "date_j",
            "date_jm5", "date_jp5", "cmt_jm5", "cmt_j", "cmt_jp5", "gsw_jm5", "gsw_j",
            "gsw_jp5", "complet", "fenetre_propre"]


def arret(msg):
    """Source manquante ou de colonnes différentes : pas de fichier d'analyse."""
    if os.path.exists(SORTIE):
        os.remove(SORTIE)
    sys.exit("ARRÊT (source non conforme, fichier d'analyse non construit) : " + msg)


journal = {}

# ---------------------------------------------------------------- D1
p = os.path.join(DON, "auctions_query.json")
if not os.path.exists(p):
    arret("D1 absente")
with open(p, encoding="utf-8") as f:
    d1 = json.load(f)
lignes_d1 = d1.get("data")
if not lignes_d1:
    arret("D1 sans données")
for r in lignes_d1:
    if set(r.keys()) != set(CHAMPS_D1):
        arret("D1 : champs différents : %s" % sorted(r.keys()))
journal["d1_lignes_api"] = len(lignes_d1)
journal["d1_total_count_meta"] = d1.get("meta", {}).get("total-count")
journal["d1_total_pages_meta"] = d1.get("meta", {}).get("total-pages")

filtre = [r for r in lignes_d1
          if r["inflation_index_security"] == "No" and r["floating_rate"] == "No"]
journal["d1_apres_filtres"] = len(filtre)
ecartees = [r for r in filtre if r["security_term"] not in TERMES]
journal["d1_termes_ecartes"] = dict(Counter(r["security_term"] for r in ecartees))
adj = [r for r in filtre if r["security_term"] in TERMES]
journal["d1_retenues"] = len(adj)
journal["d1_par_terme"] = dict(sorted(Counter(r["security_term"] for r in adj).items()))
journal["d1_par_terme_conforme_attendu"] = int(journal["d1_par_terme"] == dict(sorted(ATTENDU_TERMES.items())))

# ---------------------------------------------------------------- D2
cmt = {}
for e in ECHEANCES:
    serie = "DGS%d" % e
    p = os.path.join(DON, serie + ".csv")
    if not os.path.exists(p):
        arret("D2 : %s absente" % serie)
    with open(p, newline="", encoding="utf-8") as f:
        rd = csv.reader(f)
        entete = next(rd)
        if entete != ["observation_date", serie]:
            arret("D2 : en-tête de %s = %s" % (serie, entete))
        cmt[e] = {row[0]: row[1].strip() for row in rd if row}
    journal["d2_%s_lignes" % serie] = len(cmt[e])
    journal["d2_%s_derniere_date" % serie] = max(cmt[e])

# Calendrier C : dates où DGS10 a une valeur non vide, triées.
C = sorted(d for d, v in cmt[10].items() if v != "")
POS = {d: i for i, d in enumerate(C)}
journal["calendrier_n"] = len(C)
journal["calendrier_min"] = C[0]
journal["calendrier_max"] = C[-1]

# ---------------------------------------------------------------- D3
p = os.path.join(DON, "feds200628.csv")
if not os.path.exists(p):
    arret("D3 absente")
gsw = {e: {} for e in ECHEANCES}
with open(p, newline="", encoding="utf-8") as f:
    rd = csv.reader(f)
    n_preambule = 0
    entete = None
    for row in rd:
        if row and row[0] == "Date":
            entete = row
            break
        n_preambule += 1
    if entete is None:
        arret("D3 : pas d'en-tête commençant par Date")
    journal["d3_lignes_preambule"] = n_preambule
    if n_preambule != 9:
        arret("D3 : %d lignes de préambule au lieu de 9" % n_preambule)
    col = {}
    for e in ECHEANCES:
        nom = "SVENPY%02d" % e
        if nom not in entete:
            arret("D3 : colonne %s absente" % nom)
        col[e] = entete.index(nom)
    n = 0
    for row in rd:
        if not row:
            continue
        n += 1
        for e in ECHEANCES:
            v = row[col[e]].strip()
            gsw[e][row[0]] = "" if v == "NA" else v
    journal["d3_lignes"] = n
    journal["d3_derniere_date"] = max(gsw[10])


# ---------------------------------------------------------------- lignes
def decale(date, k):
    """« date + k » dans C ; None si date hors de C ou rang hors bornes."""
    i = POS.get(date)
    if i is None:
        return None
    j = i + k
    if j < 0 or j >= len(C):
        return None
    return C[j]


def montant(s):
    return repr(int(s) / 1e9)


reelles = []
for r in adj:
    ech, reouv = TERMES[r["security_term"]]
    reelles.append({
        "cusip": r["cusip"], "terme_api": r["security_term"], "echeance": ech,
        "reouverture": reouv, "principal": 1 if (reouv == 1 and ech in (10, 20, 30)) else 0,
        "date_adjudication": r["auction_date"], "mois": r["auction_date"][:7],
        "montant_offert_mds": montant(r["offering_amt"]), "reopening_api": r["reopening"],
    })

# Contrôle de construction : les lignes de réouverture ont reopening = "Yes" dans l'API.
princ = [r for r in reelles if r["principal"] == 1]
journal["n_principal_reelle"] = len(princ)
journal["n_principal_reopening_yes"] = sum(1 for r in princ if r["reopening_api"] == "Yes")
journal["controle_reopening_yes_ok"] = int(all(r["reopening_api"] == "Yes" for r in princ))
journal["n_reopening_yes_hors_principal"] = dict(sorted(Counter(
    r["terme_api"] for r in reelles if r["principal"] == 0 and r["reopening_api"] == "Yes").items()))
journal["n_dates_adjudication_hors_C"] = sum(1 for r in reelles if r["date_adjudication"] not in POS)

lignes = []
for r in reelles:
    base = {k: r[k] for k in ("cusip", "terme_api", "echeance", "reouverture", "principal",
                              "date_adjudication", "mois", "montant_offert_mds")}
    types = ["reelle"] + (["placebo"] if r["principal"] == 1 else [])
    for t in types:
        L = dict(base)
        L["type_ligne"] = t
        L["id_ligne"] = "%s_%s_%s" % (r["cusip"], r["date_adjudication"], t)
        if t == "reelle":
            L["date_j"] = r["date_adjudication"]
        else:
            L["date_j"] = decale(r["date_adjudication"], 10) or ""
        L["date_jm5"] = (decale(L["date_j"], -5) or "") if L["date_j"] else ""
        L["date_jp5"] = (decale(L["date_j"], 5) or "") if L["date_j"] else ""
        e = r["echeance"]
        for suf, cle in (("jm5", "date_jm5"), ("j", "date_j"), ("jp5", "date_jp5")):
            d = L[cle]
            L["cmt_" + suf] = cmt[e].get(d, "") if d else ""
            L["gsw_" + suf] = gsw[e].get(d, "") if d else ""
        six = [L[c] for c in ("cmt_jm5", "cmt_j", "cmt_jp5", "gsw_jm5", "gsw_j", "gsw_jp5")]
        L["complet"] = 1 if (all(v != "" for v in six) and r["date_adjudication"] in POS) else 0
        lignes.append(L)

# fenetre_propre : aucune AUTRE adjudication réelle de même échéance dans [date_jm5, date_jp5].
par_ech = defaultdict(list)
for r in reelles:
    par_ech[r["echeance"]].append((r["date_adjudication"], r["cusip"]))
for L in lignes:
    if not (L["date_jm5"] and L["date_jp5"]):
        L["fenetre_propre"] = 0
        continue
    autres = 0
    for d, cu in par_ech[L["echeance"]]:
        if L["date_jm5"] <= d <= L["date_jp5"]:
            # « autre » : toute ligne réelle sauf la ligne elle-même (pour une ligne réelle).
            if L["type_ligne"] == "reelle" and d == L["date_adjudication"] and cu == L["cusip"]:
                continue
            autres += 1
    L["fenetre_propre"] = 1 if autres == 0 else 0

lignes.sort(key=lambda L: (L["date_adjudication"], L["echeance"], L["type_ligne"], L["cusip"]))
cles_tri = [(L["date_adjudication"], L["echeance"], L["type_ligne"]) for L in lignes]
journal["tri_ex_aequo_departages_par_cusip"] = len(cles_tri) - len(set(cles_tri))

with open(SORTIE, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=COLONNES, lineterminator="\n")
    w.writeheader()
    for L in lignes:
        w.writerow({c: L[c] for c in COLONNES})

# ---------------------------------------------------------------- contrôles de schéma (section 5)
with open(SORTIE, newline="", encoding="utf-8") as f:
    rd = csv.DictReader(f)
    entete_lue = rd.fieldnames
    T = list(rd)

ctl = {}
ctl["1_colonnes"] = entete_lue == COLONNES
ids = [r["id_ligne"] for r in T]
ctl["2_valeurs_permises"] = (
    len(ids) == len(set(ids))
    and all(r["type_ligne"] in ("reelle", "placebo") for r in T)
    and all(r["echeance"] in ("2", "3", "5", "7", "10", "20", "30") for r in T)
    and all(r[c] in ("0", "1") for r in T for c in ("reouverture", "principal", "complet", "fenetre_propre"))
)
ctl["3_dates"] = all(
    r["date_jm5"] < r["date_j"] < r["date_jp5"] and r["date_jm5"] != ""
    and ((r["type_ligne"] == "reelle" and r["date_j"] == r["date_adjudication"])
         or (r["type_ligne"] == "placebo" and r["date_j"] > r["date_adjudication"]))
    for r in T)
ctl["4_periode_mois_montant"] = all(
    "2010-01-01" <= r["date_adjudication"] <= "2026-09-30"
    and r["mois"] == r["date_adjudication"][:7] and float(r["montant_offert_mds"]) > 0
    for r in T)
cle_reelle = Counter((r["cusip"], r["date_adjudication"]) for r in T if r["type_ligne"] == "reelle")
ctl["5_principal_placebo"] = (
    all((r["principal"] == "1") == (r["reouverture"] == "1" and r["echeance"] in ("10", "20", "30")) for r in T)
    and all(r["principal"] == "1" and cle_reelle[(r["cusip"], r["date_adjudication"])] == 1
            for r in T if r["type_ligne"] == "placebo"))
REND = ("cmt_jm5", "cmt_j", "cmt_jp5", "gsw_jm5", "gsw_j", "gsw_jp5")
ctl["6_complet"] = all((r["complet"] == "1") == all(r[c] != "" for c in REND) for r in T)
ok7 = True
for r in T:
    for c in REND:
        if r[c] != "" and not (-1 <= float(r[c]) <= 20):
            ok7 = False
    for suf in ("jm5", "j", "jp5"):
        a, b = r["cmt_" + suf], r["gsw_" + suf]
        if a != "" and b != "" and abs(float(a) - float(b)) > 1:
            ok7 = False
ctl["7_bornes_rendements"] = ok7
n_pr = sum(1 for r in T if r["type_ligne"] == "reelle" and r["principal"] == "1")
ctl["8_n_principal_300_330"] = 300 <= n_pr <= 330
journal["controles_schema"] = {k: int(v) for k, v in ctl.items()}
journal["schema_ok"] = int(all(ctl.values()))

# ---------------------------------------------------------------- comptes
journal["n_lignes"] = len(T)
journal["n_reelle"] = sum(1 for r in T if r["type_ligne"] == "reelle")
journal["n_placebo_lignes"] = sum(1 for r in T if r["type_ligne"] == "placebo")
journal["n_reelle_principal"] = n_pr


def compte(type_ligne, principal=None):
    S = [r for r in T if r["type_ligne"] == type_ligne and (principal is None or r["principal"] == principal)]
    return {
        "lignes": len(S),
        "complet_1": sum(1 for r in S if r["complet"] == "1"),
        "fenetre_propre_1": sum(1 for r in S if r["fenetre_propre"] == "1"),
        "complet_1_et_fenetre_propre_1": sum(1 for r in S if r["complet"] == "1" and r["fenetre_propre"] == "1"),
    }


journal["filtres_reelle_principal"] = compte("reelle", "1")
journal["filtres_placebo"] = compte("placebo")
journal["filtres_reelle_toutes"] = compte("reelle")
journal["incomplets"] = [
    {c: r[c] for c in ("id_ligne", "date_jm5", "date_j", "date_jp5") + REND}
    for r in T if r["complet"] == "0"]
journal["fenetre_non_propre_principal_ou_placebo"] = [
    r["id_ligne"] for r in T if r["principal"] == "1" and r["fenetre_propre"] == "0"]

with open(JOURNAL, "w", encoding="utf-8") as f:
    json.dump(journal, f, ensure_ascii=False, indent=1)

print(json.dumps({k: v for k, v in journal.items()
                  if k not in ("incomplets", "fenetre_non_propre_principal_ou_placebo")},
                 ensure_ascii=False, indent=1))
print("incomplets :", len(journal["incomplets"]))
for x in journal["incomplets"]:
    print("  ", x)
print("fenêtre non propre (principal/placebo) :", journal["fenetre_non_propre_principal_ou_placebo"])
