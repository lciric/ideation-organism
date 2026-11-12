#!/usr/bin/env python3
"""H03-v2 — construit le fichier d'analyse H03-v2_analyse.csv à partir de donnees/ seul.

Suit la préinscription scellée (sections 4 et 5) :
- 111 millésimes de la liste figée × horizons 1 à 4 = 444 lignes, y compris quand des valeurs manquent ;
- projection : OBS_VALUE à TIME_PERIOD = t_v + h dans le fichier du millésime v, si OBS_STATUS = F ;
- projection précédente : même règle dans le millésime de numéro t_v − 1 (vide pour W99) ;
- valeur réalisée : OBS_VALUE à TIME_PERIOD = q dans le millésime de numéro q + 2 si OBS_STATUS = A,
  sinon q + 3, sinon q + 4 ; manquante sinon ou hors liste figée ;
- révision et erreur arrondies à une décimale ;
- tri : t_millesime croissant puis horizon ; cellule vide = manquant.
Aucun téléchargement ici : si un des 111 fichiers manque dans donnees/, le script s'arrête
sans écrire le fichier d'analyse.

Usage : python3 construire.py
"""
import csv
import hashlib
import json
import os
import re
import sys
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import controles_schema as cs  # noqa: E402

ICI = os.path.dirname(os.path.abspath(__file__))
DONNEES = os.path.join(ICI, "donnees")
SORTIE = os.path.join(ICI, "H03-v2_analyse.csv")
JOURNAL = os.path.join(ICI, "construire_journal.json")
MOIS = ["January", "February", "March", "April", "May", "June", "July", "August",
        "September", "October", "November", "December"]
COLONNES_UTILES = ["KEY", "TIME_PERIOD", "OBS_VALUE", "OBS_STATUS", "TITLE_COMPL"]


def t_de_periode(p):
    m = re.fullmatch(r"(\d{4})-Q([1-4])", p)
    if not m:
        raise ValueError(f"TIME_PERIOD inattendu : {p!r}")
    return 4 * int(m.group(1)) + int(m.group(2)) - 1


def lire_millesime(code):
    """Renvoie (dict t -> (valeur_texte, statut), mois_titre ou None, t_premier_F ou None, n_lignes, sha256)."""
    chemin = os.path.join(DONNEES, f"MPD_Q_U2_HIC_A_{code}.csv")
    with open(chemin, "rb") as f:
        octets = f.read()
    sha = hashlib.sha256(octets).hexdigest()
    lignes = list(csv.DictReader(octets.decode("utf-8").splitlines()))
    for c in COLONNES_UTILES:
        if not lignes or c not in lignes[0]:
            raise ValueError(f"{code} : colonne {c} absente")
    cle = f"MPD.Q.U2.HIC.A.{code}.0000"
    serie = {}
    for l in lignes:
        if l["KEY"] != cle:
            raise ValueError(f"{code} : clé inattendue {l['KEY']!r}")
        t = t_de_periode(l["TIME_PERIOD"])
        if t in serie:
            raise ValueError(f"{code} : TIME_PERIOD en double {l['TIME_PERIOD']}")
        serie[t] = (l["OBS_VALUE"].strip(), l["OBS_STATUS"].strip())
    # mois lu dans TITLE_COMPL : nom de mois anglais (mot entier) ; vide si aucun
    titres = {l["TITLE_COMPL"] for l in lignes}
    trouves = []
    for titre in sorted(titres):
        for i, nom in enumerate(MOIS, start=1):
            if re.search(r"\b" + nom + r"\b", titre) and i not in trouves:
                trouves.append(i)
    if len(trouves) > 1:
        raise ValueError(f"{code} : plusieurs noms de mois dans TITLE_COMPL : {trouves}")
    mois = trouves[0] if trouves else None
    t_f = [t for t, (_, s) in serie.items() if s == "F"]
    return serie, mois, (min(t_f) if t_f else None), len(lignes), sha, sorted(titres)


def valeur(serie, t, statut):
    """OBS_VALUE (Decimal) à la ligne t si elle existe, n'est pas vide et a le statut demandé ; sinon None."""
    if serie is None or t not in serie:
        return None
    v, s = serie[t]
    if v == "" or s != statut:
        return None
    return Decimal(v)


def f1(x):
    """Écrit un décimal avec une décimale ; cellule vide si manquant ; jamais « -0.0 »."""
    if x is None:
        return ""
    s = f"{x:.1f}"
    return "0.0" if s == "-0.0" else s


def main():
    figee = cs.liste_figee()
    manquants = [c for c in figee if not os.path.exists(os.path.join(DONNEES, f"MPD_Q_U2_HIC_A_{c}.csv"))]
    if manquants:
        print(f"ARRÊT : {len(manquants)} fichier(s) brut(s) manquant(s) : {manquants}", file=sys.stderr)
        sys.exit(2)

    journal = {}
    if os.path.exists(JOURNAL):
        with open(JOURNAL, encoding="utf-8") as f:
            journal = json.load(f)
    sha_journal = {k: v.get("sha256") for k, v in journal.get("fichiers", {}).items()}

    series, meta, sha_differents = {}, {}, []
    for code in figee:
        serie, mois, t_f, n, sha, titres = lire_millesime(code)
        t = cs.t_du_code(code)
        series[t] = serie
        meta[code] = {"t": t, "mois_titre": mois, "t_premier_F": t_f, "n_lignes": n, "sha256": sha,
                      "titre": titres}
        attendu = sha_journal.get(f"MPD_Q_U2_HIC_A_{code}.csv")
        if attendu is not None and attendu != sha:
            sha_differents.append(code)
    if sha_differents:
        print(f"ARRÊT : sha256 différent du journal de téléchargement pour {sha_differents}", file=sys.stderr)
        sys.exit(2)
    assert len(series) == 111 and min(series) == 7996 and max(series) == cs.T_MAX

    def realise(q):
        for d in (2, 3, 4):
            tl = q + d
            if tl in series:            # hors de la liste figée : on passe au suivant
                v = valeur(series[tl], q, "A")
                if v is not None:
                    return v, tl
        return None, None

    lignes = []
    for code in sorted(figee, key=cs.t_du_code):
        tv = meta[code]["t"]
        for h in (1, 2, 3, 4):
            q = tv + h
            proj = valeur(series[tv], q, "F")
            prec = valeur(series.get(tv - 1), q, "F")
            rea, tl = realise(q)
            rev = round(proj - prec, 1) if (proj is not None and prec is not None) else None
            err = round(rea - proj, 1) if (rea is not None and proj is not None) else None
            lignes.append({
                "millesime": code,
                "t_millesime": tv,
                "mois_titre": "" if meta[code]["mois_titre"] is None else meta[code]["mois_titre"],
                "t_premier_F": "" if meta[code]["t_premier_F"] is None else meta[code]["t_premier_F"],
                "horizon": h,
                "cible": cs.periode_du_t(q),
                "t_cible": q,
                "projection": f1(proj),
                "millesime_precedent": "" if code == "W99" else cs.code_du_t(tv - 1),
                "projection_precedente": f1(prec),
                "millesime_realise": "" if tl is None else cs.code_du_t(tl),
                "t_lecture": "" if tl is None else tl,
                "realise": f1(rea),
                "revision": f1(rev),
                "erreur": f1(err),
            })
    assert len(lignes) == 444

    with open(SORTIE, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cs.COLONNES, lineterminator="\n")
        w.writeheader()
        w.writerows(lignes)

    # Contrôles de schéma, refaits sur le fichier écrit
    res = cs.controler(SORTIE)
    nviol = cs.n_violations(res)

    # Comptes à chaque filtre
    def present(l, c):
        return l[c] != ""
    comptes = {
        "lignes": len(lignes),
        "projection_presente": sum(present(l, "projection") for l in lignes),
        "projection_precedente_presente": sum(present(l, "projection_precedente") for l in lignes),
        "realise_present": sum(present(l, "realise") for l in lignes),
        "revision_presente": sum(present(l, "revision") for l in lignes),
        "erreur_presente": sum(present(l, "erreur") for l in lignes),
        "completes_revision_et_erreur": sum(present(l, "revision") and present(l, "erreur") for l in lignes),
        "completes_cible_8016_8103": sum(present(l, "revision") and present(l, "erreur")
                                         and 8016 <= l["t_cible"] <= 8103 for l in lignes),
        "lignes_cible_8016_8103": sum(8016 <= l["t_cible"] <= 8103 for l in lignes),
        "ecart_lecture_2": sum(l["t_lecture"] != "" and l["t_lecture"] - l["t_cible"] == 2 for l in lignes),
        "ecart_lecture_3": sum(l["t_lecture"] != "" and l["t_lecture"] - l["t_cible"] == 3 for l in lignes),
        "ecart_lecture_4": sum(l["t_lecture"] != "" and l["t_lecture"] - l["t_cible"] == 4 for l in lignes),
        "mois_titre_rempli": sum(present(l, "mois_titre") for l in lignes),
        "t_premier_F_rempli": sum(present(l, "t_premier_F") for l in lignes),
        "t_premier_F_egal_t_millesime": sum(l["t_premier_F"] == l["t_millesime"] for l in lignes),
    }
    cibles_realisees = sorted({l["t_cible"] for l in lignes if present(l, "realise")})
    comptes["trimestres_cibles_avec_realise"] = len(cibles_realisees)
    comptes["dernier_trimestre_cible_realise"] = cs.periode_du_t(cibles_realisees[-1])

    with open(SORTIE, "rb") as f:
        sha_sortie = hashlib.sha256(f.read()).hexdigest()
    journal["construction"] = {
        "fichier_analyse": os.path.basename(SORTIE),
        "sha256_fichier_analyse": sha_sortie,
        "comptes": comptes,
        "controles_schema": {str(n): {"ok": int(ok), "detail": d} for n, (ok, d) in sorted(res.items())},
        "n_violations_schema": nviol,
        "millesimes": {c: {k: v for k, v in m.items()} for c, m in meta.items()},
    }
    with open(JOURNAL, "w", encoding="utf-8") as f:
        json.dump(journal, f, ensure_ascii=False, indent=1)

    print(f"Écrit : {SORTIE} ({len(lignes)} lignes), sha256 {sha_sortie}")
    for k, v in comptes.items():
        print(f"  {k} : {v}")
    for n in sorted(res):
        print(f"  contrôle {n:2d} : {'OK   ' if res[n][0] else 'VIOLÉ'} {res[n][1]}")
    print("  n_violations_schema =", nviol)


if __name__ == "__main__":
    main()
