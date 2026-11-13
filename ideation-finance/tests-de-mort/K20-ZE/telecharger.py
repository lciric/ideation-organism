#!/usr/bin/env python3
"""K20-ZE : telechargement des sources nommees dans la preinscription (section 3).
Jusqu'a 10 essais, 120 s par essai, 10 s entre deux essais. Fichiers bruts non modifies dans donnees/.
Usage : python3 telecharger.py"""
import subprocess, hashlib, pathlib, datetime, time, zipfile, sys

ICI = pathlib.Path(__file__).resolve().parent
D = ICI / "donnees"
D.mkdir(exist_ok=True)
EUR = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/"
SOURCES = [  # (nom local, URL, obligatoire)
    ("SPF_microdata_by_variable.zip",
     "https://www.ecb.europa.eu/stats/prices/indic/forecast/shared/files/SPF_microdata_by_variable.zip", True),
    ("eurostat_prc_hicp_ainr.csv", EUR + "prc_hicp_ainr/A.RCH_A_AVG.TOTAL.EA?format=SDMX-CSV", True),
    ("eurostat_nama_10_gdp.csv", EUR + "nama_10_gdp/A.CLV_PCH_PRE.B1GQ.EA?format=SDMX-CSV", True),
    ("eurostat_une_rt_m.csv", EUR + "une_rt_m/M.NSA.TOTAL.PC_ACT.T.EA21?format=SDMX-CSV", True),
    # documents du comite de datation (verification de la chronologie, 6.8) : non utilises dans le calcul
    ("cepr_eabcn_findings_sept2020.pdf",
     "https://eabcn.org/sites/default/files/2023-09/eabcdc_findings_september_2020_0.pdf", False),
    ("cepr_eabcn_findings_dec2022.pdf",
     "https://eabcn.org/sites/default/files/2023-09/eabcdc_findings_december2022_0.pdf", False),
]
EXTRAITS = ["1_HICP.csv", "3_RGDP.csv", "5_UNEM.csv", "0_Round_dates.csv"]

def curl(url, dest):
    for essai in range(1, 11):
        r = subprocess.run(["curl", "-sS", "-L", "--max-time", "120", "-o", str(dest), "-w", "%{http_code}", url],
                           capture_output=True, text=True)
        code = r.stdout.strip()
        if r.returncode == 0 and code == "200":
            return 200, essai
        print(f"  essai {essai} : curl={r.returncode} http={code} {r.stderr.strip()[:120]}", file=sys.stderr)
        if essai < 10:
            time.sleep(10)
    return (int(code) if code.isdigit() else 0), 10

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def lignes(p): return p.read_bytes().count(b"\n")

lignes_prov = []
manque = []
for nom, url, oblig in SOURCES:
    dest = D / nom
    quand = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    code, essais = curl(url, dest)
    if code != 200:
        if dest.exists(): dest.unlink()
        lignes_prov.append((nom, url, quand, code, "-", "-", "-", essais, "OBLIGATOIRE" if oblig else "facultatif"))
        if oblig: manque.append(nom)
        continue
    lignes_prov.append((nom, url, quand, code, sha(dest), dest.stat().st_size,
                        lignes(dest) if not nom.endswith((".zip", ".pdf")) else "-", essais,
                        "obligatoire" if oblig else "facultatif"))

# extraction de la copie a la racine de l'archive (3.1)
extraits = []
z = D / "SPF_microdata_by_variable.zip"
if z.exists():
    with zipfile.ZipFile(z) as zf:
        for n in EXTRAITS:
            (D / n).write_bytes(zf.read(n))
            extraits.append(n)

with open(D / "PROVENANCE.md", "w", encoding="utf-8") as f:
    f.write("# PROVENANCE des donnees brutes de K20-ZE\n\nFichiers bruts non modifies, non versionnes ; "
            "reproductibles par `python3 telecharger.py`.\n\n")
    f.write("| fichier | URL | date de telechargement | HTTP | sha256 | octets | lignes | essais | statut |\n|---|---|---|---|---|---|---|---|---|\n")
    for l in lignes_prov:
        f.write("| " + " | ".join(str(x) for x in l) + " |\n")
    f.write("\nFichiers extraits de l'archive de la BCE (copie a la racine, octets inchanges) :\n\n")
    f.write("| fichier | sha256 | octets | lignes |\n|---|---|---|---|\n")
    for n in extraits:
        p = D / n
        f.write(f"| {n} | {sha(p)} | {p.stat().st_size} | {lignes(p)} |\n")
print(open(D / "PROVENANCE.md").read())
if manque:
    print("FICHIER OBLIGATOIRE MANQUANT :", manque); sys.exit(1)
