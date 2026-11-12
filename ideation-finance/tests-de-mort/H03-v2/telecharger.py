#!/usr/bin/env python3
"""H03-v2 — téléchargement des 111 séries brutes de la base MPD (BCE).

Règle de la préinscription (section 4, « Téléchargement ») : pour chaque millésime,
jusqu'à 10 essais espacés de 10 secondes ; on garde le premier fichier reçu avec
HTTP 200 et une ligne d'en-tête conforme. Chaque fichier brut est gardé tel quel
(octets de la réponse, sans modification) sous donnees/MPD_Q_U2_HIC_A_<MILLÉSIME>.csv ;
sha256, date et code HTTP vont dans construire_journal.json.
Si un seul des 111 fichiers ne peut pas être obtenu : arrêt, code de sortie 2.

Un fichier déjà présent et inscrit au journal n'est pas redemandé (cache disque).
Usage : python3 telecharger.py
"""
import datetime as dt
import hashlib
import json
import os
import sys
import time

import requests

ICI = os.path.dirname(os.path.abspath(__file__))
DONNEES = os.path.join(ICI, "donnees")
JOURNAL = os.path.join(ICI, "construire_journal.json")
URL = "https://data-api.ecb.europa.eu/service/data/MPD/Q.U2.HIC.A.{v}.0000?format=csvdata"
URL_CLES = "https://data-api.ecb.europa.eu/service/data/MPD?detail=serieskeysonly&format=csvdata"
COLONNES_UTILES = ["KEY", "TIME_PERIOD", "OBS_VALUE", "OBS_STATUS", "TITLE_COMPL"]
ESSAIS_MAX = 10
ATTENTE_ESSAI = 10      # secondes entre deux essais (préinscription)
PAUSE = 1.5             # secondes entre deux millésimes (politesse)
DELAI = 90              # délai maximal d'une requête, secondes


def liste_figee():
    codes = []
    for annee in range(1999, 2026):
        for lettre in "WGSA":
            codes.append(f"{lettre}{annee % 100:02d}")
    codes += ["W26", "G26", "S26"]
    assert len(codes) == 111
    return codes


def maintenant():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def entete_conforme(octets, colonnes):
    premiere = octets.split(b"\n", 1)[0].decode("utf-8", "replace").strip().lstrip("﻿")
    noms = premiere.split(",")
    return all(c in noms for c in colonnes)


def obtenir(url, colonnes):
    """Renvoie (octets ou None, liste des essais)."""
    essais = []
    for k in range(1, ESSAIS_MAX + 1):
        quand = maintenant()
        try:
            r = requests.get(url, timeout=DELAI, headers={"Accept-Encoding": "gzip, deflate"})
            code = r.status_code
            corps = r.content
            ok = code == 200 and entete_conforme(corps, colonnes)
            essais.append({"essai": k, "date_utc": quand, "http": code,
                           "octets": len(corps), "entete_conforme": int(ok)})
            if ok:
                return corps, essais
        except Exception as ex:  # délai dépassé, coupure, etc.
            essais.append({"essai": k, "date_utc": quand, "http": None,
                           "erreur": f"{type(ex).__name__}: {ex}"[:300]})
        if k < ESSAIS_MAX:
            time.sleep(ATTENTE_ESSAI)
    return None, essais


def main():
    os.makedirs(DONNEES, exist_ok=True)
    journal = {"fichiers": {}}
    if os.path.exists(JOURNAL):
        with open(JOURNAL, encoding="utf-8") as f:
            journal = json.load(f)
    journal.setdefault("fichiers", {})

    def sauver():
        with open(JOURNAL, "w", encoding="utf-8") as f:
            json.dump(journal, f, ensure_ascii=False, indent=1)

    # Liste des clés, pour contrôle (clés seules, sans valeur)
    nom_cles = "MPD_serieskeysonly.csv"
    chemin_cles = os.path.join(DONNEES, nom_cles)
    if not (os.path.exists(chemin_cles) and nom_cles in journal["fichiers"]):
        corps, essais = obtenir(URL_CLES, ["KEY"])
        if corps is None:
            journal["fichiers"][nom_cles] = {"url": URL_CLES, "obtenu": 0, "essais": essais}
            sauver()
            print("ÉCHEC : liste des clés non obtenue", file=sys.stderr)
            sys.exit(2)
        with open(chemin_cles, "wb") as f:
            f.write(corps)
        journal["fichiers"][nom_cles] = {
            "url": URL_CLES, "obtenu": 1, "http": 200, "date_utc": essais[-1]["date_utc"],
            "sha256": hashlib.sha256(corps).hexdigest(), "octets": len(corps),
            "n_essais": len(essais), "essais": essais}
        sauver()
        print(f"{nom_cles}: 200, {len(corps)} octets, {len(essais)} essai(s)", flush=True)
        time.sleep(PAUSE)

    for v in liste_figee():
        nom = f"MPD_Q_U2_HIC_A_{v}.csv"
        chemin = os.path.join(DONNEES, nom)
        if os.path.exists(chemin) and journal["fichiers"].get(nom, {}).get("obtenu") == 1:
            continue
        url = URL.format(v=v)
        corps, essais = obtenir(url, COLONNES_UTILES)
        if corps is None:
            journal["fichiers"][nom] = {"url": url, "obtenu": 0, "essais": essais}
            sauver()
            print(f"ÉCHEC : {nom} non obtenu après {ESSAIS_MAX} essais — arrêt", file=sys.stderr)
            sys.exit(2)
        with open(chemin, "wb") as f:
            f.write(corps)
        journal["fichiers"][nom] = {
            "url": url, "obtenu": 1, "http": 200, "date_utc": essais[-1]["date_utc"],
            "sha256": hashlib.sha256(corps).hexdigest(), "octets": len(corps),
            "n_essais": len(essais), "essais": essais}
        sauver()
        print(f"{nom}: 200, {len(corps)} octets, {len(essais)} essai(s)", flush=True)
        time.sleep(PAUSE)

    n = sum(1 for k, x in journal["fichiers"].items()
            if k.startswith("MPD_Q_U2_HIC_A_") and x.get("obtenu") == 1)
    journal["n_millesimes_obtenus"] = n
    sauver()
    print(f"Terminé : {n} millésimes obtenus sur 111.")
    if n != 111:
        sys.exit(2)
    ecrire_provenance(journal)


def ecrire_provenance(journal):
    """donnees/PROVENANCE.md : une table (fichier, URL, date et heure, HTTP, essais, sha256, lignes)."""
    lignes = [
        "# Provenance des fichiers bruts — H03-v2",
        "",
        "Source unique : base MPD de la BCE, API du portail de données. Chaque fichier est la réponse de l'API,",
        "octet pour octet, sans modification. Tous les fichiers ont été téléchargés à neuf pour cette course par",
        "`telecharger.py` ; **aucun fichier n'a été copié depuis le dossier de la course annulée** (`H03/donnees/`",
        "n'a pas été ouvert).",
        "",
        "- Motif d'URL des séries : `https://data-api.ecb.europa.eu/service/data/MPD/Q.U2.HIC.A.<MILLÉSIME>.0000?format=csvdata`",
        "- Liste des clés (contrôle) : `https://data-api.ecb.europa.eu/service/data/MPD?detail=serieskeysonly&format=csvdata`",
        "- Règle : jusqu'à 10 essais espacés de 10 s ; premier fichier reçu avec HTTP 200 et en-tête conforme.",
        "- Dates en temps universel (UTC). « Lignes » = lignes de données, sans la ligne d'en-tête.",
        "- Le sha256 est celui du fichier sur disque, recalculé au moment d'écrire cette table ; il est égal à celui",
        "  noté au téléchargement dans `construire_journal.json`.",
        "",
        "| Fichier | URL | Date et heure (UTC) | HTTP | Essais | sha256 | Lignes |",
        "|---|---|---|---|---|---|---|",
    ]
    for nom in sorted(journal["fichiers"], key=lambda k: (k.startswith("MPD_Q"), journal["fichiers"][k]["date_utc"], k)):
        x = journal["fichiers"][nom]
        with open(os.path.join(DONNEES, nom), "rb") as f:
            octets = f.read()
        sha = hashlib.sha256(octets).hexdigest()
        assert sha == x["sha256"], nom
        n_lignes = len(octets.decode("utf-8").splitlines()) - 1
        lignes.append(f"| `{nom}` | {x['url']} | {x['date_utc']} | {x['http']} | {x['n_essais']} | `{sha}` | {n_lignes} |")
    with open(os.path.join(DONNEES, "PROVENANCE.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lignes) + "\n")


if __name__ == "__main__":
    main()
