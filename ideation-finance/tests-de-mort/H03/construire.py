#!/usr/bin/env python3
"""H03 — construction du fichier d'analyse H03_analyse.csv à partir de donnees/ seul.

Suit la préinscription (sections 4 et 5) à la lettre :
- 111 millésimes figés (W, S, G, A pour 1999..2025, plus W26, S26, G26) ;
- lettres -> trimestre : W = 1, S = 2, G = 3, A = 4 (correspondance écrite dans la préinscription) ;
- t = 4 * année + (trimestre - 1) ;
- projection : OBS_VALUE à la ligne TIME_PERIOD = cible du fichier du millésime, si OBS_STATUS = F ;
- projection précédente : même règle dans le millésime de numéro t - 1 ;
- réalisé : millésime de numéro cible + 2, puis + 3, puis + 4, si OBS_STATUS = A ;
- 444 lignes, triées par t_millesime puis horizon.

Si un seul des 111 fichiers manque, le script s'arrête sans rien écrire.

Usage : python3 construire.py
"""
import csv
import json
import os
import re
import sys
from decimal import Decimal, InvalidOperation

ICI = os.path.dirname(os.path.abspath(__file__))
DONNEES = os.path.join(ICI, "donnees")
SORTIE = os.path.join(ICI, "H03_analyse.csv")
BILAN = os.path.join(ICI, "construire_bilan.json")

COLONNES = ["millesime", "t_millesime", "mois_titre", "t_premier_F", "horizon", "cible", "t_cible",
            "projection", "millesime_precedent", "projection_precedente", "millesime_realise",
            "t_lecture", "realise", "revision", "erreur"]
LETTRE_TRIM = {"W": 1, "S": 2, "G": 3, "A": 4}
TRIM_LETTRE = {v: k for k, v in LETTRE_TRIM.items()}
MOIS = ["january", "february", "march", "april", "may", "june", "july", "august", "september",
        "october", "november", "december"]
RE_MOIS = re.compile(r"\b(" + "|".join(MOIS) + r")\b", re.IGNORECASE)
RE_PERIODE = re.compile(r"^(\d{4})-Q([1-4])$")


def liste_millesimes():
    codes = []
    for annee in range(1999, 2026):
        for lettre in "WSGA":
            codes.append(f"{lettre}{annee % 100:02d}")
    codes += ["W26", "S26", "G26"]
    return codes


def t_du_code(code):
    aa = int(code[1:])
    annee = 1900 + aa if aa == 99 else 2000 + aa
    return 4 * annee + (LETTRE_TRIM[code[0]] - 1)


def periode_de_t(t):
    return f"{t // 4}-Q{t % 4 + 1}"


def t_de_periode(p):
    m = RE_PERIODE.match(p.strip())
    if not m:
        return None
    return 4 * int(m.group(1)) + (int(m.group(2)) - 1)


def mois_du_titre(titre):
    m = RE_MOIS.search(titre or "")
    return MOIS.index(m.group(1).lower()) + 1 if m else None


def dec(txt):
    txt = (txt or "").strip()
    if txt == "":
        return None
    try:
        d = Decimal(txt)
    except InvalidOperation:
        return None
    return d if d.is_finite() else None


def fmt(d):
    """Écrit un décimal ; une décimale quand la valeur en a au plus une, sinon telle quelle."""
    if d is None:
        return ""
    if d == 0:
        d = abs(d)
    if d == d.quantize(Decimal("0.1")):
        return f"{d:.1f}"
    return format(d, "f")


def lire_millesime(code):
    """Retourne (obs, titre, titre_compl, anomalies). obs : t -> (valeur Decimal ou None, statut)."""
    chemin = os.path.join(DONNEES, f"MPD_Q_U2_HIC_A_{code}.csv")
    attendu = f"MPD.Q.U2.HIC.A.{code}.0000"
    obs, titres, titres_compl, anomalies = {}, set(), set(), []
    with open(chemin, encoding="utf-8-sig", newline="") as f:
        lecteur = csv.DictReader(f)
        for ligne in lecteur:
            if ligne["KEY"] != attendu:
                anomalies.append(f"KEY inattendue {ligne['KEY']}")
                continue
            t = t_de_periode(ligne["TIME_PERIOD"])
            if t is None:
                anomalies.append(f"TIME_PERIOD illisible {ligne['TIME_PERIOD']}")
                continue
            if t in obs:
                anomalies.append(f"TIME_PERIOD en double {ligne['TIME_PERIOD']}")
                continue
            obs[t] = (dec(ligne["OBS_VALUE"]), ligne["OBS_STATUS"].strip())
            titres.add(ligne.get("TITLE", "") or "")
            titres_compl.add(ligne.get("TITLE_COMPL", "") or "")
    return obs, sorted(titres), sorted(titres_compl), anomalies


def main():
    codes = liste_millesimes()
    assert len(codes) == 111 and len(set(codes)) == 111
    manquants = [c for c in codes if not os.path.exists(os.path.join(DONNEES, f"MPD_Q_U2_HIC_A_{c}.csv"))]
    if manquants:
        print("ARRET : fichiers manquants :", manquants)
        return 2

    par_t, infos = {}, {}
    for code in codes:
        obs, titres, titres_compl, anomalies = lire_millesime(code)
        t = t_du_code(code)
        par_t[t] = (code, obs)
        t_f = [tt for tt, (_, s) in obs.items() if s == "F"]
        titre = titres[0] if len(titres) == 1 else " | ".join(titres)
        titre_compl = titres_compl[0] if len(titres_compl) == 1 else " | ".join(titres_compl)
        infos[code] = {
            "t_millesime": t, "n_obs": len(obs),
            "premiere_periode": periode_de_t(min(obs)) if obs else "",
            "derniere_periode": periode_de_t(max(obs)) if obs else "",
            "statuts": sorted({s for _, s in obs.values()}),
            "t_premier_F": min(t_f) if t_f else None,
            "TITLE": titre, "TITLE_COMPL": titre_compl,
            # lecture littérale de la préinscription : mois lu dans la colonne TITLE
            "mois_titre": mois_du_titre(titre),
            # lecture alternative, consignée pour ecarts.md seulement : colonne TITLE_COMPL
            "mois_titre_compl": mois_du_titre(titre_compl),
            "anomalies": anomalies,
        }
    assert sorted(par_t) == list(range(7996, 8107))

    def lire(t_v, t_q, statut):
        if t_v not in par_t:
            return None
        v = par_t[t_v][1].get(t_q)
        if v is None or v[0] is None or v[1] != statut:
            return None
        return v[0]

    lignes = []
    for t_v in sorted(par_t):
        code = par_t[t_v][0]
        info = infos[code]
        for h in (1, 2, 3, 4):
            q = t_v + h
            proj = lire(t_v, q, "F")
            code_prec = par_t[t_v - 1][0] if (t_v - 1) in par_t else ""
            prec = lire(t_v - 1, q, "F")
            realise, t_lect = None, None
            for dt in (2, 3, 4):
                if (q + dt) in par_t:
                    val = lire(q + dt, q, "A")
                    if val is not None:
                        realise, t_lect = val, q + dt
                        break
            revision = None if (proj is None or prec is None) else (proj - prec).quantize(Decimal("0.1"))
            erreur = None if (proj is None or realise is None) else (realise - proj).quantize(Decimal("0.1"))
            lignes.append({
                "millesime": code, "t_millesime": t_v,
                "mois_titre": "" if info["mois_titre"] is None else info["mois_titre"],
                "t_premier_F": "" if info["t_premier_F"] is None else info["t_premier_F"],
                "horizon": h, "cible": periode_de_t(q), "t_cible": q,
                "projection": fmt(proj), "millesime_precedent": code_prec,
                "projection_precedente": fmt(prec),
                "millesime_realise": par_t[t_lect][0] if t_lect is not None else "",
                "t_lecture": "" if t_lect is None else t_lect,
                "realise": fmt(realise), "revision": fmt(revision), "erreur": fmt(erreur),
            })
    assert len(lignes) == 444

    with open(SORTIE, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLONNES, lineterminator="\n")
        w.writeheader()
        w.writerows(lignes)

    # bilan des filtres
    def n(pred):
        return sum(1 for l in lignes if pred(l))
    bilan = {
        "n_lignes": len(lignes),
        "n_projection_presente": n(lambda l: l["projection"] != ""),
        "n_projection_precedente_presente": n(lambda l: l["projection_precedente"] != ""),
        "n_realise_present": n(lambda l: l["realise"] != ""),
        "n_revision_presente": n(lambda l: l["revision"] != ""),
        "n_erreur_presente": n(lambda l: l["erreur"] != ""),
        "n_completes": n(lambda l: l["revision"] != "" and l["erreur"] != ""),
        "n_completes_cible_2004_2025": n(lambda l: l["revision"] != "" and l["erreur"] != ""
                                         and 8016 <= l["t_cible"] <= 8103),
        "n_realise_lu_a_q_plus": {str(d): n(lambda l, d=d: l["t_lecture"] != "" and l["t_lecture"] - l["t_cible"] == d)
                                  for d in (2, 3, 4)},
        "lignes_incompletes": [
            {"millesime": l["millesime"], "horizon": l["horizon"], "cible": l["cible"],
             "projection": l["projection"], "projection_precedente": l["projection_precedente"],
             "realise": l["realise"]}
            for l in lignes if l["revision"] == "" or l["erreur"] == ""],
        "millesimes": infos,
    }
    with open(BILAN, "w", encoding="utf-8") as f:
        json.dump(bilan, f, ensure_ascii=False, indent=1)

    # contrôles de schéma, refaits sur le fichier écrit (même fonction que analyse.py)
    sys.path.insert(0, ICI)
    from analyse import controles_schema  # noqa: E402
    viol = controles_schema(SORTIE)
    print("Fichier écrit :", SORTIE)
    for k in ("n_lignes", "n_projection_presente", "n_projection_precedente_presente", "n_realise_present",
              "n_completes", "n_completes_cible_2004_2025", "n_realise_lu_a_q_plus"):
        print(f"  {k} = {bilan[k]}")
    print("Contrôles de schéma violés :", {k: v for k, v in viol.items() if v} or "aucun")
    return 0


if __name__ == "__main__":
    sys.exit(main())
