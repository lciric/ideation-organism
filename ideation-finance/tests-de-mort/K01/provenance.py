"""K01 — écrit donnees/PROVENANCE.md à partir de construire_journal.json et des fichiers de donnees/."""
import hashlib
import io
import json
import os
import zipfile

ICI = os.path.dirname(os.path.abspath(__file__))
DONNEES = os.path.join(ICI, "donnees")
with open(os.path.join(ICI, "construire_journal.json"), encoding="utf-8") as f:
    J = json.load(f)


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def lignes(nom):
    p = os.path.join(DONNEES, nom)
    if nom.endswith(".zip"):
        with zipfile.ZipFile(p) as z:
            n = sum(1 for _ in io.TextIOWrapper(io.BytesIO(z.read("1_HICP.csv")), encoding="utf-8")) - 1
        return f"{n} (lignes de données de `1_HICP.csv`, copie à la racine)"
    with open(p, encoding="utf-8") as f:
        return str(sum(1 for _ in f) - 1)


noms = sorted(k for k in J if not k.startswith("_"))
ordre = ["SPF_microdata_by_variable.zip", "prc_hicp_ainr_A.RCH_A_AVG.TOTAL.EA.csv"]
noms = ordre + [n for n in noms if n not in ordre]
out = ["# Provenance des données brutes de K01", "",
       "Fichiers enregistrés tels que reçus (aucune modification). Date et heure : UTC, au moment de la réception. "
       "Nombre de lignes : lignes de données hors ligne d'en-tête. Le sha256 est recalculé sur le fichier présent "
       "dans ce dossier et comparé au journal (`../construire_journal.json`).", "",
       "| Fichier | URL | Date et heure (UTC) | HTTP | sha256 | Octets | Lignes |", "|---|---|---|---|---|---|---|"]
for n in noms:
    e = J[n]
    h = sha(os.path.join(DONNEES, n))
    assert h == e["sha256"], n
    out.append(f"| `{n}` | {e['url']} | {e['date_utc']} | {e['http']} | `{h}` | {e['octets']} | {lignes(n)} |")
with open(os.path.join(DONNEES, "PROVENANCE.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print(len(noms), "fichiers")
