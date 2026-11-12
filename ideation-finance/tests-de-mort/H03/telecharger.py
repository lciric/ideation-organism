#!/usr/bin/env python3
"""H03 — téléchargement des 111 millésimes MPD (préinscription, section 4).

Une requête par millésime :
  https://data-api.ecb.europa.eu/service/data/MPD/Q.U2.HIC.A.<MILLESIME>.0000?format=csvdata
Jusqu'à 10 essais espacés de 10 secondes ; on garde le premier fichier reçu avec HTTP 200 et
une ligne d'en-tête conforme. Les fichiers bruts sont écrits tels quels dans donnees/ ; le
sha256, la date et le code HTTP sont consignés dans construire_journal.json.
Un fichier déjà présent ET consigné dans le journal avec le même sha256 n'est pas retéléchargé.

Usage : python3 telecharger.py
"""
import datetime
import hashlib
import json
import os
import subprocess
import sys
import time

ICI = os.path.dirname(os.path.abspath(__file__))
DONNEES = os.path.join(ICI, "donnees")
JOURNAL = os.path.join(ICI, "construire_journal.json")
BASE = "https://data-api.ecb.europa.eu/service/data/MPD"
COLONNES_REQUISES = ["KEY", "TIME_PERIOD", "OBS_VALUE", "OBS_STATUS", "TITLE"]
N_ESSAIS = 10
PAUSE_ESSAI = 10
DELAI_MAX = 180  # secondes par requête
PAUSE_ENTRE_REQUETES = 1.5


def liste_millesimes():
    codes = []
    for annee in range(1999, 2026):
        for lettre in "WSGA":
            codes.append(f"{lettre}{annee % 100:02d}")
    codes += ["W26", "S26", "G26"]
    assert len(codes) == 111
    return codes


def maintenant():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256(chemin):
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def charger_journal():
    if os.path.exists(JOURNAL):
        with open(JOURNAL, encoding="utf-8") as f:
            return json.load(f)
    return {"fichiers": {}, "essais": []}


def ecrire_journal(j):
    tmp = JOURNAL + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(j, f, ensure_ascii=False, indent=1)
    os.replace(tmp, JOURNAL)


def requete(url, sortie_tmp):
    """Retourne (code_http ou 0, message d'erreur curl)."""
    cmd = ["curl", "-sS", "-m", str(DELAI_MAX), "-o", sortie_tmp, "-w", "%{http_code}",
           "-H", "Accept-Encoding: identity", url]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=DELAI_MAX + 30)
    except subprocess.TimeoutExpired:
        return 0, "delai depasse (subprocess)"
    try:
        code = int(p.stdout.strip()[-3:])
    except ValueError:
        code = 0
    return code, p.stderr.strip()[:300]


def entete_conforme(chemin, colonnes):
    try:
        with open(chemin, "rb") as f:
            premiere = f.readline().decode("utf-8", errors="replace").strip().lstrip("﻿")
    except OSError:
        return False
    noms = premiere.split(",")
    return all(c in noms for c in colonnes)


def obtenir(nom_fichier, url, colonnes, journal):
    chemin = os.path.join(DONNEES, nom_fichier)
    deja = journal["fichiers"].get(nom_fichier)
    if deja and os.path.exists(chemin) and sha256(chemin) == deja["sha256"]:
        return True
    tmp = chemin + ".part"
    for essai in range(1, N_ESSAIS + 1):
        t0 = time.time()
        code, err = requete(url, tmp)
        duree = round(time.time() - t0, 2)
        ok = code == 200 and os.path.exists(tmp) and entete_conforme(tmp, colonnes)
        journal["essais"].append({"fichier": nom_fichier, "url": url, "essai": essai,
                                  "date_utc": maintenant(), "code_http": code,
                                  "duree_s": duree, "retenu": int(ok), "erreur_curl": err})
        if ok:
            os.replace(tmp, chemin)
            with open(chemin, "rb") as f:
                n_lignes = sum(1 for _ in f)
            journal["fichiers"][nom_fichier] = {
                "url": url, "date_utc": maintenant(), "code_http": code,
                "sha256": sha256(chemin), "octets": os.path.getsize(chemin),
                "lignes_avec_entete": n_lignes, "essai_retenu": essai}
            ecrire_journal(journal)
            print(f"OK   {nom_fichier}  essai {essai}  HTTP {code}  {duree}s", flush=True)
            return True
        ecrire_journal(journal)
        print(f"ECHEC {nom_fichier}  essai {essai}  HTTP {code}  {duree}s  {err}", flush=True)
        if os.path.exists(tmp):
            os.remove(tmp)
        if essai < N_ESSAIS:
            time.sleep(PAUSE_ESSAI)
    return False


def main():
    os.makedirs(DONNEES, exist_ok=True)
    journal = charger_journal()
    manquants = []
    for code in liste_millesimes():
        nom = f"MPD_Q_U2_HIC_A_{code}.csv"
        url = f"{BASE}/Q.U2.HIC.A.{code}.0000?format=csvdata"
        if not obtenir(nom, url, COLONNES_REQUISES, journal):
            manquants.append(code)
        time.sleep(PAUSE_ENTRE_REQUETES)
    # liste des clés, pour contrôle (préinscription, section 4)
    url_cles = f"{BASE}?detail=serieskeysonly&format=csvdata"
    cles_ok = obtenir("MPD_serieskeysonly.csv", url_cles, ["KEY"], journal)
    journal["bilan"] = {"date_utc": maintenant(), "n_millesimes_obtenus": 111 - len(manquants),
                        "millesimes_manquants": manquants, "liste_cles_obtenue": int(cles_ok)}
    ecrire_journal(journal)
    print("BILAN", json.dumps(journal["bilan"]))
    return 0 if not manquants else 1


if __name__ == "__main__":
    sys.exit(main())
