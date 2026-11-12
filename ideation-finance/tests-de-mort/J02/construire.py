"""J02 - construit J02_analyse.csv a partir de donnees/ seulement (sections 4 et 5 de la preinscription).

Usage : python3 -I construire.py
Sorties : J02_analyse.csv ; construire_journal.json (sha256 et lignes de chaque fichier brut, metadonnees de
telechargement recopiees de telecharger_journal.json si present, drapeaux Eurostat, comptes, controles de schema).
S'arrete (code 2) si l'un des 109 fichiers MPD ou le fichier Eurostat manque.
"""
import csv, hashlib, json, pathlib, re, sys

ICI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
from controles_schema import COLONNES, LETTRE_TRIM, liste_millesimes, annee_code, t_code, controler  # noqa: E402

DONNEES = ICI / "donnees"
SORTIE = ICI / "J02_analyse.csv"
JOURNAL = ICI / "construire_journal.json"
MOIS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
        "November", "December"]
RE_MOIS = re.compile(r"\b(" + "|".join(MOIS) + r")\b")
RE_ANNEE = re.compile(r"\b(\d{4})\b")
COLS_MPD = ["KEY", "TIME_PERIOD", "OBS_VALUE", "OBS_STATUS", "TITLE_COMPL"]


def t_periode(tp):
    """'1999-Q1' -> 7996"""
    m = re.fullmatch(r"(\d{4})-Q([1-4])", tp)
    return 4 * int(m.group(1)) + int(m.group(2)) - 1


def nom_trimestre(t):
    an, q = divmod(t, 4)
    return f"{an}-Q{q + 1}"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def lire_csv(p):
    with open(p, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def lire_millesime(code):
    p = DONNEES / f"MPD_Q_U2_HIC_A_{code}.csv"
    if not p.exists():
        return None
    lignes = lire_csv(p)
    if not lignes or any(c not in lignes[0] for c in COLS_MPD):
        return None
    cle_att = f"MPD.Q.U2.HIC.A.{code}.0000"
    assert all(r["KEY"] == cle_att for r in lignes), f"cle inattendue dans {p.name}"
    titres = sorted({r["TITLE_COMPL"] for r in lignes})
    titre = titres[-1] if len(titres) == 1 else None  # un titre unique attendu ; sinon mois/annee laisses vides
    mois = annee = None
    if titre is not None:
        mm = RE_MOIS.findall(titre)
        mois = MOIS.index(mm[-1]) + 1 if mm else None          # dernier nom de mois anglais complet
        aa = RE_ANNEE.findall(titre)
        annee = int(aa[-1]) if aa else None                     # annee a quatre chiffres (la derniere si plusieurs)
    par_t = {}
    for r in lignes:
        t = t_periode(r["TIME_PERIOD"])
        assert t not in par_t, f"trimestre en double dans {p.name}"
        par_t[t] = r
    ts_f = sorted(t for t, r in par_t.items() if r["OBS_STATUS"] == "F")
    return {"fichier": p.name, "titre": titre, "n_titres": len(titres), "mois": mois, "annee": annee,
            "t_premier_F": ts_f[0] if ts_f else None, "par_t": par_t, "n_lignes": len(lignes)}


def lire_eurostat():
    p = DONNEES / "prc_hicp_minr_M_I15_TOTAL_EA.csv"
    if not p.exists():
        return None, None
    lignes = lire_csv(p)
    serie, drapeaux = {}, {}
    for r in lignes:
        assert (r["freq"], r["unit"], r["coicop18"], r["geo"]) == ("M", "I15", "TOTAL", "EA")
        tp = r["TIME_PERIOD"]
        if not ("1998-10" <= tp <= "2026-09"):
            continue  # mois utilises : 1998-10 a 2026-09
        serie[tp] = r["OBS_VALUE"]
        if r.get("OBS_FLAG", ""):
            drapeaux[tp] = r["OBS_FLAG"]
    return serie, drapeaux


def num(x):
    try:
        v = float(x)
        return v if v == v else None
    except (TypeError, ValueError):
        return None


def main():
    codes = liste_millesimes()
    vint = {c: lire_millesime(c) for c in codes}
    manquants = [c for c, v in vint.items() if v is None]
    serie, drapeaux = lire_eurostat()
    if manquants or serie is None:
        print("ARRET : fichier manquant", manquants, "eurostat" if serie is None else "")
        sys.exit(2)
    # repli I25 : seulement si un mois necessaire manque dans I15
    mois_requis = [f"{a}-{m:02d}" for a in range(1998, 2027) for m in range(1, 13) if "1998-10" <= f"{a}-{m:02d}" <= "2026-09"]
    mois_absents = [m for m in mois_requis if num(serie.get(m, "")) is None]
    if mois_absents:
        print("ARRET : mois absents dans I15, le repli I25 doit etre telecharge et ecrit dans ecarts.md", mois_absents)
        sys.exit(3)

    def mois_du_trimestre(t):
        an, q = divmod(t, 4)
        return [f"{an}-{3 * q + k:02d}" for k in (1, 2, 3)]

    sortie = []
    for t in range(7999, 8107):
        an, q = divmod(t, 4)
        row = {"cible": nom_trimestre(t), "t_cible": t, "annee_cible": an}
        for h in (2, 3):
            tm = t - h
            code = next(c for c in codes if t_code(c) == tm)
            v = vint[code]
            r = v["par_t"].get(t)
            statut = r["OBS_STATUS"] if r is not None else ""
            proj = ""
            if r is not None and statut == "F" and num(r["OBS_VALUE"]) is not None:
                proj = r["OBS_VALUE"].strip()
            row.update({f"millesime_h{h}": code, f"t_millesime_h{h}": tm,
                        f"mois_titre_h{h}": "" if v["mois"] is None else v["mois"],
                        f"annee_titre_h{h}": "" if v["annee"] is None else v["annee"],
                        f"t_premier_F_h{h}": "" if v["t_premier_F"] is None else v["t_premier_F"],
                        f"statut_h{h}": statut, f"projection_h{h}": proj})
        m = mois_du_trimestre(t)
        a = mois_du_trimestre(t - 4)
        bruts = [serie.get(x, "") for x in m + a]
        vals = [num(x) for x in bruts]
        for k in range(3):
            row[f"indice_m{k + 1}"] = bruts[k].strip() if vals[k] is not None else ""
        for k in range(3):
            row[f"indice_an_avant_m{k + 1}"] = bruts[3 + k].strip() if vals[3 + k] is not None else ""
        rea = None
        if all(x is not None for x in vals):
            rea = 100 * ((vals[0] + vals[1] + vals[2]) / (vals[3] + vals[4] + vals[5]) - 1)
        row["realise"] = "" if rea is None else f"{rea:.12f}"
        p2, p3 = num(row["projection_h2"]), num(row["projection_h3"])
        row["revision"] = "" if (p2 is None or p3 is None) else f"{p2 - p3:.10f}"
        row["erreur"] = "" if (rea is None or p2 is None) else f"{rea - p2:.12f}"
        sortie.append(row)

    with open(SORTIE, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLONNES, lineterminator="\n")
        w.writeheader()
        for row in sortie:
            w.writerow(row)

    # comptes par filtre
    n_h2 = sum(r["projection_h2"] != "" for r in sortie)
    n_h3 = sum(r["projection_h3"] != "" for r in sortie)
    n_a = sum(r["realise"] != "" for r in sortie)
    n_rev = sum(r["revision"] != "" for r in sortie)
    n_comp = sum(r["revision"] != "" and r["erreur"] != "" for r in sortie)
    controles = controler(SORTIE)
    # controle supplementaire (hors schema, pour le journal) : coherence lettre/titre sur les 109 millesimes
    lettre_titre = {c: {"mois": v["mois"], "annee": v["annee"], "t_premier_F": v["t_premier_F"],
                        "ok": v["mois"] == 3 * LETTRE_TRIM[c[0]] and v["annee"] == annee_code(c)
                        and v["t_premier_F"] == t_code(c)} for c, v in vint.items()}
    tel = {}
    tj = ICI / "telecharger_journal.json"
    if tj.exists():
        tel = json.loads(tj.read_text())
    fichiers = {}
    for p in sorted(DONNEES.glob("*.csv")):
        n = len(lire_csv(p))
        meta = next((v for v in tel.values() if v.get("fichier") == f"donnees/{p.name}"), {})
        fichiers[p.name] = {"sha256": sha(p), "lignes_donnees": n, "url": meta.get("url"),
                            "date_utc": meta.get("date_utc"), "http": meta.get("http"), "essais": meta.get("essais")}
        if meta and meta.get("sha256") != fichiers[p.name]["sha256"]:
            fichiers[p.name]["alerte"] = "sha256 different de celui du telechargement"
    journal = {
        "fichier_analyse": SORTIE.name, "sha256_fichier_analyse": sha(SORTIE),
        "n_lignes": len(sortie), "n_projection_h2": n_h2, "n_projection_h3": n_h3, "n_realise": n_a,
        "n_revision": n_rev, "n_completes": n_comp,
        "statuts_h2": sorted({r["statut_h2"] for r in sortie}), "statuts_h3": sorted({r["statut_h3"] for r in sortie}),
        "millesimes_lettre_titre_premierF_tous_ok": all(v["ok"] for v in lettre_titre.values()),
        "millesimes_titre_unique": all(v["n_titres"] == 1 for v in vint.values()),
        "millesimes_detail": lettre_titre,
        "eurostat_mois_utilises": [mois_requis[0], mois_requis[-1], len(mois_requis)],
        "eurostat_drapeaux": drapeaux, "repli_I25": False,
        "controles_schema": controles, "fichiers_bruts": fichiers,
    }
    JOURNAL.write_text(json.dumps(journal, indent=1, ensure_ascii=False))
    print(json.dumps({k: journal[k] for k in ["n_lignes", "n_projection_h2", "n_projection_h3", "n_realise",
                                               "n_revision", "n_completes", "statuts_h2", "statuts_h3",
                                               "millesimes_lettre_titre_premierF_tous_ok",
                                               "millesimes_titre_unique", "controles_schema"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
