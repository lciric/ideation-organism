"""K20-LIV : téléchargement brut des sources nommées par la préinscription (section 3).
Écrit donnees/<fichier> (octets bruts) et donnees/PROVENANCE.md ; construire_journal.json reçoit le même contenu."""
import subprocess, hashlib, datetime, json, pathlib, sys, time, io
D = pathlib.Path(__file__).resolve().parent / "donnees"
D.mkdir(exist_ok=True)
P = "https://www.philadelphiafed.org/-/media/FRBP/Assets/Surveys-And-Data/livingston-survey/"
F = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="
SRC = [("means.xlsx", P+"historical-data/means.xlsx"),
       ("medians.xlsx", P+"historical-data/medians.xlsx"),
       ("individualdata.xlsx", P+"historical-data/individualdata.xlsx"),
       ("livingston-documentation.pdf", P+"livingston-documentation.pdf")]
for s in ["CPIAUCNS","CPIAUCSL","UNRATE","DPRIME","DTB3","HOUST","USRECP","USREC"]:
    SRC.append((f"FRED_{s}.csv", F+s))
rows = []
for nom, url in SRC:
    ok = False
    for essai in range(5):
        r = subprocess.run(["curl","-sS","-L","--max-time","300","-o",str(D/nom),"-w","%{http_code}",url],capture_output=True,text=True)
        code = r.stdout.strip()
        if code == "200" and (D/nom).stat().st_size > 0:
            ok = True; break
        print("échec", nom, code, r.stderr[:200], file=sys.stderr)
        time.sleep(120 if essai < 4 else 0)
    date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    b = (D/nom).read_bytes() if (D/nom).exists() else b""
    lignes = b.count(b"\n") if nom.endswith(".csv") else None
    rows.append(dict(fichier=nom, url=url, date=date, http=code, sha256=hashlib.sha256(b).hexdigest(), octets=len(b), lignes=lignes))
    if not ok:
        print("FICHIER MANQUANT", nom); 
md = ["# PROVENANCE — K20-LIV", "", "Téléchargement brut, aucun fichier modifié. Les données brutes ne sont pas versionnées ; ce fichier l'est.", "",
      "| Fichier | URL | Date | HTTP | sha256 | Octets | Lignes |", "|---|---|---|---|---|---|---|"]
for r in rows:
    md.append(f"| {r['fichier']} | {r['url']} | {r['date']} | {r['http']} | {r['sha256']} | {r['octets']} | {r['lignes'] if r['lignes'] is not None else 'n/a (binaire)'} |")
(D/"PROVENANCE.md").write_text("\n".join(md)+"\n")
(D.parent/"construire_journal.json").write_text(json.dumps(rows, indent=1))
print("\n".join(md))
