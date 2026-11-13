"""M01 - construction de M01_analyse.csv (preinscription sections 4.5, 6, 7) et controles de schema.
Usage : python3 -I construire.py construire      ecrit M01_analyse.csv puis lance les controles de schema sur le fichier ecrit
        python3 -I construire.py controles       controles de schema sur M01_analyse.csv
        python3 -I construire.py demonstration   chaque controle detecte une alteration (sur copies, jamais sur le vrai fichier)"""
import sys, os, re, csv, json, math, shutil, tempfile, datetime as dt

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import commun as K

DON = os.path.join(ICI, "donnees")
SORTIE = os.path.join(ICI, "M01_analyse.csv")
D1F = os.path.join(DON, "D1_auctions.json")

COLS = (["id_ligne", "cusip", "terme_api", "echeance", "date_adjudication", "mois", "annee", "periode",
         "date_emission_origine", "date_echeance", "taux_coupon_pct", "date_jm5", "date_jp5", "motif_exclusion",
         "prix_fi_jm5", "prix_fi_j", "prix_fi_jp5", "identite_fi_ok"]
        + [f"{b}_{x}" for x in ("jm5", "j", "jp5") for b in ("beta0", "beta1", "beta2", "beta3", "tau1", "tau2")]
        + [f"cmt_{x}" for x in ("jm5", "j", "jp5")] + [f"gswpar_{x}" for x in ("jm5", "j", "jp5")]
        + [f"rdt_fi_{x}_pct" for x in ("jm5", "j", "jp5")] + [f"rdt_gsw_{x}_pct" for x in ("jm5", "j", "jp5")]
        + [f"e_own_{x}_pb" for x in ("jm5", "j", "jp5")] + [f"e_cmt_{x}_pb" for x in ("jm5", "j", "jp5")]
        + ["v_own_pb", "v_cmt_pb", "ecart_pb", "complet", "dans_p"])
assert len(COLS) == 59
XS = ("jm5", "j", "jp5")


# ------------------------------------------------------------------ lecture des donnees brutes
def lire_gsw():
    with open(os.path.join(DON, "D3_gsw_feds200628.csv"), encoding="utf-8") as f:
        lignes = f.read().split("\n")
    assert lignes[9].startswith("Date,"), "en-tete GSW pas a la ligne 10"
    rd = csv.reader(lignes[9:])
    ent = next(rd)
    idx = {n: i for i, n in enumerate(ent)}
    out = {}
    for r in rd:
        if r:
            out[r[0]] = r
    return idx, out


def lire_fred(m):
    out = {}
    with open(os.path.join(DON, f"D4_DGS{m}.csv"), encoding="utf-8") as f:
        rd = csv.reader(f)
        ent = next(rd)
        assert ent == ["observation_date", f"DGS{m}"], ent
        for r in rd:
            out[r[0]] = r[1]
    return out


def lire_page(date):
    p = os.path.join(DON, "fedinvest", date.isoformat() + ".html")
    if not os.path.exists(p):
        return None
    h = open(p, encoding="utf-8", errors="replace").read()
    rows = {}
    for tr in re.findall(r"<tr>(.*?)</tr>", h, flags=re.S):
        td = [re.sub(r"<[^>]+>", "", c).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, flags=re.S)]
        if len(td) == 8:
            rows.setdefault(td[0], []).append(td)
    return rows


def vide(s):
    return s is None or s == "" or s == "NA"


def fmt(x):
    return "" if x is None else repr(float(x))


# ------------------------------------------------------------------ construction
def construire():
    d1 = K.charger_d1(D1F)
    prem = K.premieres(d1)
    par_cusip = {}
    for r in d1:
        par_cusip.setdefault(r["cusip"], []).append(r["auction_date"])
    pop = K.population(d1)
    gidx, gsw = lire_gsw()
    fred = {m: lire_fred(m) for m in (10, 20, 30)}
    pages = {}
    def page(d):
        if d not in pages:
            pages[d] = lire_page(d)
        return pages[d]

    lignes, journal = [], {"pages_absentes": [], "cusip_absent_page": []}
    for r in pop:
        j = K.iso(r["auction_date"])
        jm5, jp5 = K.fenetre(j)
        ech = K.echeance_de(r["security_term"])
        p1 = prem[r["cusip"]]
        assert len(p1) == 1
        p1 = p1[0]
        row = {c: "" for c in COLS}
        row.update(id_ligne=f"{r['cusip']}_{r['auction_date']}", cusip=r["cusip"], terme_api=r["security_term"],
                   echeance=ech, date_adjudication=r["auction_date"], mois=r["auction_date"][:7],
                   annee=j.year, periode="avant" if r["auction_date"] <= "2021-12-31" else "apres",
                   date_emission_origine=p1["issue_date"], date_echeance=r["maturity_date"],
                   taux_coupon_pct=r["int_rate"], date_jm5=jm5.isoformat(), date_jp5=jp5.isoformat())
        rj = K.RANG[j]
        chev = any(a != r["auction_date"] and abs(K.RANG[K.iso(a)] - rj) <= 10 for a in par_cusip[r["cusip"]])
        non_emis = p1["issue_date"] > jm5.isoformat()
        motif = "fenetre_chevauchee" if chev else ("titre_non_emis_a_jm5" if non_emis else "")
        if motif:
            row.update(motif_exclusion=motif, identite_fi_ok=0, complet=0, dans_p=0)
            lignes.append(row)
            continue
        c = float(r["int_rate"])
        M = K.iso(r["maturity_date"])
        dates = dict(zip(XS, (jm5, j, jp5)))
        ident = 1
        prix = {}
        for x, d in dates.items():
            pg = page(d)
            if pg is None:
                journal["pages_absentes"].append(d.isoformat())
                ident = 0
                continue
            lg = [t for t in pg.get(r["cusip"], []) if t[1] in ("MARKET BASED NOTE", "MARKET BASED BOND")]
            if len(lg) != 1:
                journal["cusip_absent_page"].append((d.isoformat(), r["cusip"], len(pg.get(r["cusip"], []))))
                ident = 0
                continue
            t = lg[0]
            try:
                ok_rate = abs(float(t[2].rstrip("%")) - c) < 1e-9
                ok_mat = dt.datetime.strptime(t[3], "%m/%d/%Y").date() == M
                eod = float(t[7])
            except ValueError:
                ident = 0
                continue
            row[f"prix_fi_{x}"] = t[7]
            prix[x] = eod
            if not (ok_rate and ok_mat and eod > 0):
                ident = 0
        row["identite_fi_ok"] = ident
        par = {}
        for x, d in dates.items():
            g = gsw.get(d.isoformat())
            if g is not None:
                for b in ("beta0", "beta1", "beta2", "beta3", "tau1", "tau2"):
                    v = g[gidx[b.upper()]]
                    row[f"{b}_{x}"] = "" if v == "NA" else v
                v = g[gidx[f"SVENPY{ech}"]]
                row[f"gswpar_{x}"] = "" if v == "NA" else v
            v = fred[ech].get(d.isoformat(), "")
            row[f"cmt_{x}"] = "" if v == "" else v
        # valeurs derivees
        for x in XS:
            if row[f"prix_fi_{x}"] != "":
                row[f"rdt_fi_{x}_pct"] = fmt(K.rendement(float(row[f"prix_fi_{x}"]), c, M, dates[x]))
            if all(row[f"{b}_{x}"] != "" for b in ("beta0", "beta1", "beta2", "beta3", "tau1", "tau2")):
                pp = [float(row[f"{b}_{x}"]) for b in ("beta0", "beta1", "beta2", "beta3", "tau1", "tau2")]
                row[f"rdt_gsw_{x}_pct"] = fmt(K.rendement_gsw(c, M, dates[x], pp))
            if row[f"rdt_fi_{x}_pct"] != "" and row[f"rdt_gsw_{x}_pct"] != "":
                row[f"e_own_{x}_pb"] = fmt(100 * (float(row[f"rdt_fi_{x}_pct"]) - float(row[f"rdt_gsw_{x}_pct"])))
            if row[f"cmt_{x}"] != "" and row[f"gswpar_{x}"] != "":
                row[f"e_cmt_{x}_pb"] = fmt(100 * (float(row[f"cmt_{x}"]) - float(row[f"gswpar_{x}"])))
        if all(row[f"e_own_{x}_pb"] != "" for x in XS):
            a, b, cc = (float(row[f"e_own_{x}_pb"]) for x in XS)
            row["v_own_pb"] = fmt(2 * b - a - cc)
        if all(row[f"e_cmt_{x}_pb"] != "" for x in XS):
            a, b, cc = (float(row[f"e_cmt_{x}_pb"]) for x in XS)
            row["v_cmt_pb"] = fmt(2 * b - a - cc)
        if row["v_own_pb"] != "" and row["v_cmt_pb"] != "":
            row["ecart_pb"] = fmt(float(row["v_cmt_pb"]) - float(row["v_own_pb"]))
        cols_in = [f"prix_fi_{x}" for x in XS] + [f"{b}_{x}" for x in XS for b in ("beta0", "beta1", "beta2", "beta3", "tau1", "tau2")] \
            + [f"cmt_{x}" for x in XS] + [f"gswpar_{x}" for x in XS]
        comp = int(all(row[k] != "" for k in cols_in) and ident == 1)
        row["complet"] = comp
        row["motif_exclusion"] = "" if comp else "valeur_manquante"
        row["dans_p"] = 1 if comp else 0
        lignes.append(row)
    lignes.sort(key=lambda r: (r["date_adjudication"], r["echeance"]))
    with open(SORTIE, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(COLS)
        for r in lignes:
            w.writerow([r[c] for c in COLS])
    print("ecrit", SORTIE, len(lignes), "lignes")
    print("journal :", json.dumps(journal)[:2000])
    return journal


# ------------------------------------------------------------------ controles de schema (section 7)
def _f(s):
    return float(s)


def controles(chemin):
    """Renvoie {n: (ok, detail)} pour les controles 1 a 9. Les controles 3 a 9 ne portent que sur dans_p = 1."""
    d1 = K.charger_d1(D1F)
    prem = K.premieres(d1)
    par_cusip = {}
    for r in d1:
        par_cusip.setdefault(r["cusip"], []).append(r["auction_date"])
    res = {}
    with open(chemin, encoding="utf-8", newline="") as f:
        rd = csv.reader(f)
        ent = next(rd)
        brut = [r for r in rd]
    # 1
    res[1] = (ent == COLS and all(len(r) == 59 for r in brut), f"{len(ent)} colonnes")
    if ent != COLS:
        for n in range(2, 10):
            res[n] = (False, "colonnes invalides")
        return res
    rows = [dict(zip(ent, r)) for r in brut]
    # 2
    ids = [r["id_ligne"] for r in rows]
    attendu = {f"{r['cusip']}_{r['auction_date']}" for r in K.population(d1)}
    res[2] = (len(ids) == len(set(ids)) and set(ids) == attendu,
              f"{len(ids)} lignes, {len(set(ids))} id distincts, attendu {len(attendu)}, manquantes {len(attendu - set(ids))}, en trop {len(set(ids) - attendu)}")
    P = [r for r in rows if r["motif_exclusion"] == ""]
    exclues = {}
    for r in rows:
        if r["motif_exclusion"]:
            exclues[r["motif_exclusion"]] = exclues.get(r["motif_exclusion"], 0) + 1
    bad = {n: [] for n in range(3, 10)}
    for r in P:
        i = r["id_ligne"]
        try:
            j = K.iso(r["date_adjudication"])
            first = prem.get(r["cusip"], [None])[0]
            ok3 = (r["id_ligne"] == f"{r['cusip']}_{r['date_adjudication']}" and len(r["cusip"]) == 9
                   and K.echeance_de(r["terme_api"]) == int(r["echeance"]) and r["mois"] == r["date_adjudication"][:7]
                   and int(r["annee"]) == j.year
                   and r["periode"] == ("avant" if r["date_adjudication"] <= "2021-12-31" else "apres")
                   and first is not None and _f(r["taux_coupon_pct"]) == _f(first["int_rate"])
                   and r["date_echeance"] == first["maturity_date"] and r["date_emission_origine"] == first["issue_date"]
                   and r["complet"] == "1" and r["identite_fi_ok"] in ("0", "1") and r["complet"] in ("0", "1")
                   and r["dans_p"] in ("0", "1") and r["dans_p"] == "1")
            if not ok3:
                bad[3].append(i)
            ok4 = j in K.RANG and r["date_jm5"] == K.C[K.RANG[j] - 5].isoformat() and r["date_jp5"] == K.C[K.RANG[j] + 5].isoformat()
            if not ok4:
                bad[4].append(i)
            rj = K.RANG[j]
            ok5 = (not any(a != r["date_adjudication"] and abs(K.RANG[K.iso(a)] - rj) <= 10 for a in par_cusip[r["cusip"]])
                   and r["date_emission_origine"] <= r["date_jm5"])
            if not ok5:
                bad[5].append(i)
            if r["identite_fi_ok"] != "1":
                bad[6].append(i)
            ok7 = (all(30 <= _f(r[f"prix_fi_{x}"]) <= 200 for x in XS)
                   and all(_f(r[f"{b}_{x}"]) > 0 for x in XS for b in ("tau1", "tau2"))
                   and all(-1 <= _f(r[f"{b}_{x}"]) <= 20 for x in XS for b in ("cmt", "gswpar"))
                   and all(-1 <= _f(r[f"{b}_{x}_pct"]) <= 20 for x in XS for b in ("rdt_fi", "rdt_gsw"))
                   and 0 <= _f(r["taux_coupon_pct"]) <= 15)
            if not ok7:
                bad[7].append(i)
            ok8 = all(abs(_f(r[f"rdt_fi_{x}_pct"]) - _f(r[f"rdt_gsw_{x}_pct"])) <= 0.60
                      and abs(_f(r[f"cmt_{x}"]) - _f(r[f"gswpar_{x}"])) <= 1 for x in XS)
            if not ok8:
                bad[8].append(i)
            eo = [100 * (_f(r[f"rdt_fi_{x}_pct"]) - _f(r[f"rdt_gsw_{x}_pct"])) for x in XS]
            ec = [100 * (_f(r[f"cmt_{x}"]) - _f(r[f"gswpar_{x}"])) for x in XS]
            vo, vc = 2 * eo[1] - eo[0] - eo[2], 2 * ec[1] - ec[0] - ec[2]
            ok9 = (all(r[c] != "" for c in COLS[14:42])
                   and all(abs(_f(r[f"e_own_{x}_pb"]) - e) <= 1e-6 for x, e in zip(XS, eo))
                   and all(abs(_f(r[f"e_cmt_{x}_pb"]) - e) <= 1e-6 for x, e in zip(XS, ec))
                   and abs(_f(r["v_own_pb"]) - vo) <= 1e-6 and abs(_f(r["v_cmt_pb"]) - vc) <= 1e-6
                   and abs(_f(r["ecart_pb"]) - (vc - vo)) <= 1e-6)
            if not ok9:
                bad[9].append(i)
        except Exception as e:  # une valeur illisible ou absente fait echouer les controles qui la lisent
            for n in range(3, 10):
                if i not in bad[n]:
                    bad[n].append(i + f" [exception {type(e).__name__}]")
    noms = {3: "champs d'identite et de coherence", 4: "calendrier au rang", 5: "chevauchement / emission", 6: "identite FedInvest",
            7: "plages", 8: "garde d'appariement", 9: "arithmetique et colonnes 15-42 remplies"}
    for n in range(3, 10):
        res[n] = (not bad[n], f"{noms[n]} : {len(bad[n])} lignes de P en defaut sur {len(P)}" + (f" ({bad[n][:3]})" if bad[n] else ""))
    res["P"] = (True, f"|P| = {len(P)} ; lignes exclues (comptees seulement) : {exclues}")
    # verification annexe (hors numerotation 1-9) : tri
    cles = [(r["date_adjudication"], int(r["echeance"])) for r in rows]
    res["tri"] = (cles == sorted(cles), "tri par date_adjudication puis echeance")
    return res


def schema_ok(res):
    return int(all(res[n][0] for n in range(1, 10)))


def afficher(res):
    for n in range(1, 10):
        print(f"  controle {n} : {'OK' if res[n][0] else 'ECHEC'} - {res[n][1]}")
    print("  ", res["P"][1], "| tri :", "OK" if res["tri"][0] else "ECHEC")
    print("  schema_ok =", schema_ok(res))


# ------------------------------------------------------------------ demonstration de detection
def lire_csv(chemin):
    with open(chemin, encoding="utf-8", newline="") as f:
        rd = csv.reader(f)
        ent = next(rd)
        return ent, list(rd)


def ecrire_csv(chemin, ent, rows):
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(ent)
        w.writerows(rows)


def demonstration():
    ent, rows = lire_csv(SORTIE)
    ix = {c: i for i, c in enumerate(ent)}
    iP = [k for k, r in enumerate(rows) if r[ix["motif_exclusion"]] == ""]
    iX = [k for k, r in enumerate(rows) if r[ix["motif_exclusion"]] != ""]
    k0 = iP[len(iP) // 2]
    print("fichier reel :")
    afficher(controles(SORTIE))
    def alt(nom, fonction, attendu_echec):
        ent2, rows2 = [list(ent)], [list(r) for r in rows]
        fonction(ent2, rows2)
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "copie.csv")
            ecrire_csv(p, ent2[0], rows2)
            res = controles(p)
        echecs = [n for n in range(1, 10) if not res[n][0]]
        ok = all(n in echecs for n in attendu_echec)
        print(f"- {nom} : controles en echec {echecs} ; attendu parmi {attendu_echec} -> {'DETECTE' if ok else 'NON DETECTE'}")
        return ok
    tout = []
    tout.append(alt("1 colonnes permutees (prix_fi_j <-> prix_fi_jp5)", lambda e, r: (e[0].__setitem__(ix["prix_fi_j"], "prix_fi_jp5"), e[0].__setitem__(ix["prix_fi_jp5"], "prix_fi_j")), [1]))
    tout.append(alt("2a une ligne supprimee", lambda e, r: r.pop(k0), [2]))
    tout.append(alt("2b id_ligne dupliquee", lambda e, r: r[k0].__setitem__(0, r[k0 + 1][0]), [2]))
    tout.append(alt("3 periode alteree", lambda e, r: r[k0].__setitem__(ix["periode"], "apres" if r[k0][ix["periode"]] == "avant" else "avant"), [3]))
    def a4(e, r):
        k = K.RANG[K.iso(r[k0][ix["date_jm5"]])]
        r[k0][ix["date_jm5"]] = K.C[k + 1].isoformat()
    tout.append(alt("4 date_jm5 decalee d'un rang", a4, [4]))
    tout.append(alt("5 date_emission_origine posterieure a date_jm5", lambda e, r: r[k0].__setitem__(ix["date_emission_origine"], r[k0][ix["date_adjudication"]]), [5]))
    tout.append(alt("6 identite_fi_ok = 0", lambda e, r: r[k0].__setitem__(ix["identite_fi_ok"], "0"), [6]))
    tout.append(alt("7 prix_fi_j = 250", lambda e, r: r[k0].__setitem__(ix["prix_fi_j"], "250"), [7]))
    tout.append(alt("8 rdt_fi_j_pct decale de +1 point (e_own recalcules coherents)", lambda e, r: (
        r[k0].__setitem__(ix["rdt_fi_j_pct"], repr(float(r[k0][ix["rdt_fi_j_pct"]]) + 1.0)),
        r[k0].__setitem__(ix["e_own_j_pb"], repr(float(r[k0][ix["e_own_j_pb"]]) + 100.0)),
        r[k0].__setitem__(ix["v_own_pb"], repr(float(r[k0][ix["v_own_pb"]]) + 200.0)),
        r[k0].__setitem__(ix["ecart_pb"], repr(float(r[k0][ix["ecart_pb"]]) - 200.0))), [8]))
    tout.append(alt("9 v_cmt_pb altere de 1e-3", lambda e, r: r[k0].__setitem__(ix["v_cmt_pb"], repr(float(r[k0][ix["v_cmt_pb"]]) + 1e-3)), [9]))
    tout.append(alt("9bis cmt_j efface", lambda e, r: r[k0].__setitem__(ix["cmt_j"], ""), [9]))
    # portee : alteration d'une ligne exclue -> controles 3 a 9 inchanges
    if iX:
        kx = next((k for k in iX if rows[k][ix['motif_exclusion']] == 'fenetre_chevauchee'), iX[0])
        ent2, rows2 = list(ent), [list(r) for r in rows]
        rows2[kx][ix["periode"]] = "xx"; rows2[kx][ix["prix_fi_j"]] = "9999"; rows2[kx][ix["date_jm5"]] = "1999-01-01"
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "copie.csv")
            ecrire_csv(p, ent2, rows2)
            res = controles(p)
        ok = all(res[n][0] for n in range(1, 10))
        print(f"- portee : alteration de la ligne exclue {rows[kx][0]} (motif {rows[kx][ix['motif_exclusion']]}) -> schema_ok={schema_ok(res)} ; "
              f"{'NON DECLENCHE comme prevu' if ok else 'DECLENCHE A TORT'}")
        tout.append(ok)
    print("toutes les demonstrations conformes :", all(tout))
    afficher(controles(SORTIE))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "construire":
        construire()
        afficher(controles(SORTIE))
    elif cmd == "controles":
        afficher(controles(SORTIE))
    elif cmd == "demonstration":
        demonstration()
