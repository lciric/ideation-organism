#!/usr/bin/env python3
"""H03 — écrit donnees/PROVENANCE.md à partir de construire_journal.json et des fichiers présents.

Le sha256 et le nombre de lignes sont recalculés sur les fichiers ; un désaccord avec le journal est signalé.
Usage : python3 provenance.py
"""
import hashlib
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
DONNEES = os.path.join(ICI, "donnees")


def main():
    with open(os.path.join(ICI, "construire_journal.json"), encoding="utf-8") as f:
        j = json.load(f)
    essais = j["essais"]
    lignes, desaccords = [], []
    for nom in sorted(j["fichiers"], key=lambda n: j["fichiers"][n]["date_utc"]):
        info = j["fichiers"][nom]
        chemin = os.path.join(DONNEES, nom)
        with open(chemin, "rb") as f:
            contenu = f.read()
        sha = hashlib.sha256(contenu).hexdigest()
        n_lignes = contenu.count(b"\n") + (0 if contenu.endswith(b"\n") or not contenu else 1)
        if sha != info["sha256"]:
            desaccords.append(nom)
        n_essais = sum(1 for e in essais if e["fichier"] == nom)
        lignes.append(f"| `{nom}` | {info['date_utc']} | {info['code_http']} | {n_essais} | "
                      f"{n_lignes - 1} | {len(contenu)} | `{sha}` |")
    echecs = [e for e in essais if not e["retenu"]]
    txt = []
    txt.append("# H03 — Provenance des données brutes\n")
    txt.append("Source unique : base des projections macroéconomiques de la BCE (MPD), API du portail de données "
               "de la BCE. Aucun compte, aucune autre source. Fichiers enregistrés tels que reçus (aucune "
               "modification).\n")
    txt.append("**Modèle d'URL (un fichier par millésime)** :\n")
    txt.append("```\nhttps://data-api.ecb.europa.eu/service/data/MPD/Q.U2.HIC.A.<MILLÉSIME>.0000?format=csvdata\n```\n")
    txt.append("enregistré sous `MPD_Q_U2_HIC_A_<MILLÉSIME>.csv`.\n")
    txt.append("**Liste des clés (pour contrôle)** :\n")
    txt.append("```\nhttps://data-api.ecb.europa.eu/service/data/MPD?detail=serieskeysonly&format=csvdata\n```\n")
    txt.append("enregistrée sous `MPD_serieskeysonly.csv`.\n")
    txt.append(f"Téléchargement par `telecharger.py` (curl, en-tête `Accept-Encoding: identity`), jusqu'à 10 essais "
               f"espacés de 10 s par fichier. Requêtes émises : {len(essais)} ; essais en échec : {len(echecs)}. "
               f"Le détail de chaque essai (date, code HTTP, durée) est dans `../construire_journal.json`.\n")
    if echecs:
        txt.append("Essais en échec : " + ", ".join(
            f"`{e['fichier']}` essai {e['essai']} (HTTP {e['code_http']}, {e['date_utc']})" for e in echecs) + ".\n")
    txt.append("Dates en UTC. « Lignes » = lignes de données, en-tête non compté. « Essais » = nombre de requêtes "
               "émises pour ce fichier.\n")
    txt.append("| Fichier | Date et heure (UTC) | HTTP | Essais | Lignes | Octets | sha256 |")
    txt.append("|---|---|---|---|---|---|---|")
    txt.extend(lignes)
    txt.append("")
    if desaccords:
        txt.append("**ATTENTION : sha256 différent du journal pour : " + ", ".join(desaccords) + "**\n")
    with open(os.path.join(DONNEES, "PROVENANCE.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(txt))
    print(len(lignes), "fichiers ;", len(echecs), "essais en échec ; désaccords :", desaccords)
    return 1 if desaccords else 0


if __name__ == "__main__":
    sys.exit(main())
