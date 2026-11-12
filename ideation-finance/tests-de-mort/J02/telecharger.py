"""J02 - telechargement des donnees brutes (section 4 de la preinscription).

Regle preinscrite (MPD) : jusqu'a 10 essais, delai maximal 120 s par essai, 10 s entre deux essais ; on garde le premier
fichier recu avec HTTP 200 et une ligne d'en-tete contenant KEY, TIME_PERIOD, OBS_VALUE, OBS_STATUS, TITLE_COMPL.
La meme regle est appliquee a Eurostat (la preinscription n'en fixe pas pour cette source).
Les fichiers deja presents dans donnees/ et valides ne sont pas retelecharges (cache).
Journal : telecharger_journal.json (url, date UTC, code HTTP, nombre d'essais, sha256, octets, lignes).
"""
import csv, hashlib, io, json, pathlib, sys, time, datetime
import urllib.request, urllib.error

ICI = pathlib.Path(__file__).resolve().parent
DONNEES = ICI / "donnees"
JOURNAL = ICI / "telecharger_journal.json"
MPD_URL = "https://data-api.ecb.europa.eu/service/data/MPD/Q.U2.HIC.A.{v}.0000?format=csvdata"
EUROSTAT_URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/prc_hicp_minr/M.I15.TOTAL.EA?format=SDMX-CSV"
COLS_MPD = ["KEY", "TIME_PERIOD", "OBS_VALUE", "OBS_STATUS", "TITLE_COMPL"]
COLS_EST = ["TIME_PERIOD", "OBS_VALUE", "OBS_FLAG"]


def millesimes():
    out = []
    for an in range(1999, 2026):
        for l in "WGSA":
            out.append(f"{l}{an % 100:02d}")
    out.append("W26")
    assert len(out) == 109
    return out


def entete_ok(contenu: bytes, cols):
    try:
        premiere = contenu.decode("utf-8-sig").splitlines()[0]
    except Exception:
        return False
    noms = next(csv.reader(io.StringIO(premiere)))
    return all(c in noms for c in cols)


def nlignes(contenu: bytes):
    return max(0, len(list(csv.reader(io.StringIO(contenu.decode("utf-8-sig"))))) - 1)


def telecharger(url, cible: pathlib.Path, cols, journal, cle):
    if cible.exists() and entete_ok(cible.read_bytes(), cols) and cle in journal:
        return True
    essais = []
    for k in range(1, 11):
        horodatage = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
        code, contenu, err = None, None, None
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "python-urllib"})
            with urllib.request.urlopen(req, timeout=120) as r:
                code = r.status
                contenu = r.read()
        except urllib.error.HTTPError as e:
            code, err = e.code, str(e)
        except Exception as e:  # delai, connexion
            err = repr(e)
        essais.append({"essai": k, "date_utc": horodatage, "http": code, "erreur": err})
        if code == 200 and contenu is not None and entete_ok(contenu, cols):
            cible.write_bytes(contenu)
            journal[cle] = {
                "url": url, "fichier": f"donnees/{cible.name}", "date_utc": horodatage, "http": code,
                "essais": k, "historique_essais": essais, "sha256": hashlib.sha256(contenu).hexdigest(),
                "octets": len(contenu), "lignes_donnees": nlignes(contenu),
            }
            print(f"{cle}: OK essai {k}", flush=True)
            return True
        print(f"{cle}: echec essai {k} ({code}, {err})", flush=True)
        if k < 10:
            time.sleep(10)
    journal[cle] = {"url": url, "fichier": None, "echec": True, "historique_essais": essais}
    return False


def main():
    DONNEES.mkdir(exist_ok=True)
    journal = json.loads(JOURNAL.read_text()) if JOURNAL.exists() else {}
    journal = {k: v for k, v in journal.items() if not v.get("echec")}
    manquants = []
    for v in millesimes():
        ok = telecharger(MPD_URL.format(v=v), DONNEES / f"MPD_Q_U2_HIC_A_{v}.csv", COLS_MPD, journal, f"MPD_{v}")
        JOURNAL.write_text(json.dumps(journal, indent=1, ensure_ascii=False))
        if not ok:
            manquants.append(v)
    ok = telecharger(EUROSTAT_URL, DONNEES / "prc_hicp_minr_M_I15_TOTAL_EA.csv", COLS_EST, journal, "EUROSTAT_I15")
    JOURNAL.write_text(json.dumps(journal, indent=1, ensure_ascii=False))
    if not ok:
        manquants.append("EUROSTAT_I15")
    print("manquants:", manquants)
    sys.exit(1 if manquants else 0)


if __name__ == "__main__":
    main()
