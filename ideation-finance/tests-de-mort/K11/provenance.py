#!/usr/bin/env python3
"""K11 -- ecrit donnees/PROVENANCE.md : un tableau (fichier, origine, URL, date et heure, sha256, lignes).

Origine des dates et heures :
- fichiers telecharges par K11 : horodatage du journal (journal_fedinvest.csv, journal_controle.csv) ou de la requete D1 ;
- pages copiees de J05 : date de modification du fichier, conservee a la copie (shutil.copy2), c.-a-d. l'heure ou J05
  l'a ecrit.
Usage : python3 -I provenance.py
"""
import csv
import datetime as dt
import hashlib
import json
import os
import re

ICI = os.path.dirname(os.path.abspath(__file__))
DON = os.path.join(ICI, "donnees")
URL_D1 = ("https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query?fields=cusip,"
          "auction_date,issue_date,maturity_date,security_type,security_term,original_security_term,reopening,"
          "inflation_index_security,floating_rate,closing_time_comp,int_rate,high_yield,high_price&filter="
          "security_type:in:(Note,Bond),auction_date:lte:2026-10-31&sort=auction_date&page%5Bsize%5D=10000")
URL_FI = ("https://www.treasurydirect.gov/GA-FI/FedInvest/securityPriceDetail (apres GET selectSecurityPriceDate + "
          "POST priceDate=AAAA-MM-JJ)")
HORODATAGE_D1 = "2026-11-12T23:49:56Z"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def journal(p):
    if not os.path.exists(p):
        return {}
    with open(p, encoding="utf-8") as f:
        return {r["date_demandee"]: r for r in csv.DictReader(f) if r["sha256"]}


def lignes_page(p):
    s = open(p, encoding="utf-8", errors="replace").read()
    i = s.find("<th>END OF DAY</th>")
    if i < 0:
        return 0, 0
    t = s[i:]
    return len(re.findall(r"<tr>\s*<td>", t)), len(re.findall(r"MARKET BASED (?:NOTE|BOND)", t))


def main():
    jf = journal(os.path.join(DON, "journal_fedinvest.csv"))
    jc = journal(os.path.join(DON, "journal_controle.csv"))
    out = ["# K11 — provenance des données brutes", "",
           "Toutes les pages FedInvest sont des réponses brutes non modifiées de "
           "`securityPriceDetail` (procédure de la préinscription, section 4.2, une session par date). "
           "Origine « J05 (copie) » : fichier brut copié sans modification depuis "
           "`tests-de-mort/J05/donnees/fedinvest/` (shutil.copy2 ; la date est celle du fichier écrit par J05). "
           "Origine « K11 » : téléchargé par K11 (`telecharger.py`), date du journal. "
           "Origine « K11 (contrôle) » : retéléchargement de contrôle d'une date copiée de J05 "
           "(`donnees/fedinvest_controle/`) ; seule différence constatée : le jeton `_csrf` de session (voir le rapport). "
           "« Lignes » : pour D1, nombre d'enregistrements JSON ; pour une page, lignes du tableau de prix "
           "(toutes catégories) / dont notes et obligations « MARKET BASED NOTE/BOND ». "
           "Les journaux `journal_fedinvest.csv` et `journal_controle.csv` gardent les codes HTTP (200/302/200), "
           "la date affichée et le nombre d'essais de chaque téléchargement K11.", "",
           "| Fichier | Origine | URL ou motif d'URL | Date et heure (UTC) | sha256 | Lignes |",
           "|---|---|---|---|---|---|"]
    p = os.path.join(DON, "auctions_query.json")
    n = len(json.load(open(p, encoding="utf-8"))["data"])
    out.append(f"| `auctions_query.json` | K11 | `{URL_D1}` | {HORODATAGE_D1} | `{sha(p)}` | {n} |")
    for sous, jr, orig_k in (("fedinvest", jf, "K11"), ("fedinvest_controle", jc, "K11 (contrôle)")):
        d = os.path.join(DON, sous)
        for f in sorted(os.listdir(d)):
            p = os.path.join(d, f)
            date = f[:-5]
            if date in jr:
                orig, quand = orig_k, jr[date]["horodatage_utc"]
                assert jr[date]["sha256"] == sha(p)
            else:
                orig = "J05 (copie)"
                quand = dt.datetime.fromtimestamp(os.path.getmtime(p), dt.timezone.utc).isoformat(timespec="seconds")
            nt, nn = lignes_page(p)
            out.append(f"| `{sous}/{f}` | {orig} | {URL_FI} | {quand} | `{sha(p)}` | {nt} / {nn} |")
    for f in ("journal_fedinvest.csv", "journal_controle.csv"):
        p = os.path.join(DON, f)
        n = sum(1 for _ in open(p, encoding="utf-8")) - 1
        q = dt.datetime.fromtimestamp(os.path.getmtime(p), dt.timezone.utc).isoformat(timespec="seconds")
        out.append(f"| `{f}` | K11 (journal, non brut) | — | {q} | `{sha(p)}` | {n} |")
    open(os.path.join(DON, "PROVENANCE.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
    print(len(out) - 9, "lignes de tableau")


if __name__ == "__main__":
    main()
