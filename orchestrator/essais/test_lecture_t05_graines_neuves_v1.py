"""Essais (R5) de la lecture préenregistrée du lot T0.5 à graines neuves (v1) et du juge à plan pleine épreuve.

Tout est **synthétique** : une banque de calibrage au format de `banque-e2.json` (96 tâches × 3 épisodes, moniteurs à 2 et
3 issues, complétude partielle) et quatre dossiers de course au format exact des fichiers réels du pilote et des
notations du 17 octobre (`episodes.json` : `resultat.fiches[*]` avec `episode`, `tache`, `jetons_par_action`,
`bilan.actions_valides` ; `notations-{8B,3B}-decisives.json` : `resultat.notations[*]` avec `cle`
« juge-XB/tâche/eK/passe-N », `notes`, `variante` « b0 », `score`, `tronquee`… ; compagnons `.sha256` au format de
sha256sum). Aucune donnée réelle neuve n'est lue (elle n'existe pas encore).

- cas sain, course à blanc de bout en bout : une loi vraie (synthétique) déclarée témoin vrai par la règle de L3 est
  promue sous le plan plein ; les témoins faux sont refusés ; le témoin planté de force 0,8 est promu ;
- chaque garde de la liste d'arrêt déclenchée sur un artefact : fichier manquant (A1), empreinte discordante (A2),
  notation en double (A3), moniteur trop pauvre (A4), tâche des deux côtés (A5), format (A6), table de rangs (A7) ;
- juge : plan plus petit que l'épreuve refusé, plan tronqué refusé, nul v8 imposé.
"""

import copy
import hashlib
import json
import math
import os
import random
import statistics
import sys

import pytest

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)
sys.path.insert(0, os.path.join(RACINE, "exemples"))
sys.path.insert(0, os.path.join(RACINE, "demonstrations"))

import construire_banque_t05_v3 as b3  # noqa: E402
import lecture_t05_graines_neuves_v1 as lec  # noqa: E402
from pole import juge_plan_plein_v1 as jpp  # noqa: E402
from pole.nul_v8 import NulV8Refuse  # noqa: E402

SUFFIXE = "-g2"
# Moniteurs synthétiques : (juge, rubrique, valeurs possibles, complétude, loi) ; « RIGOR » du 8B suit log_jetons_total
# (trait continu : sur un trait discret comme actions_valides, le plan trié par divergence groupe les valeurs égales et le
# membre « moyenne glissante » du nul suit ces blocs ; constat consigné au préenregistrement).
MONITEURS = (("8B", "RIGOR", (0, 4), 0.75, "vraie"), ("8B", "NOVELTY", (1, 4), 0.6, None),
             ("3B", "BALANCE", (1, 3), 0.5, None), ("3B", "COHERENCE", (2, 5), 0.9, None))


# --- fabrique synthétique au format réel ------------------------------------------------------------------------------
def _sha(chemin):
    with open(chemin, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _ecrire_json_et_compagnon(chemin, objet):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(objet, f, ensure_ascii=False, indent=1)
    with open(chemin + ".sha256", "w", encoding="utf-8") as f:
        f.write(f"{_sha(chemin)}  {os.path.basename(chemin)}\n")


def resceller(chemin):
    with open(chemin + ".sha256", "w", encoding="utf-8") as f:
        f.write(f"{_sha(chemin)}  {os.path.basename(chemin)}\n")


def _episode(rng, tache, k):
    actions_valides = rng.choice((6, 7, 8, 9, 10, 10, 10))
    base = rng.uniform(120, 260)
    jetons = [max(5, int(rng.gauss(base, rng.uniform(5, 40)))) for _ in range(10)]
    return {"actions": [{"texte": "…"}] * 10, "bilan": {"N": 1, "T": 10, "actions": 10, "actions_valides": actions_valides,
                                                        "ensemble": "PROPOSAL 1: …"},
            "empreintes": {"activations": "0" * 64, "trajectoire": "0" * 64}, "episode": f"{tache}/e{k}",
            "equivalence": {}, "jetons_par_action": jetons, "tache": tache}


def _note(rng, juge, rub, bornes, loi, z_trait):
    lo, hi = bornes
    if loi == "vraie":
        v = round(2 + 1.6 * z_trait + rng.gauss(0, 0.5))
    else:
        v = rng.randint(lo, hi)
    return max(lo, min(hi, int(v)))


def _notes_de(rng, episode, z_trait):
    sortie = {}
    for juge, rub, bornes, completude, loi in MONITEURS:
        if rng.random() < completude:
            sortie.setdefault(juge, {})[rub] = _note(rng, juge, rub, bornes, loi, z_trait)
    return sortie


def _z_jetons(ep, moy, ect):
    return (math.log(sum(ep["jetons_par_action"])) - moy) / ect


def fabriquer(dossier, graine=7, taches=96, courses=(30, 30, 30, 6)):
    """Calibrage synthétique (format banque-e2) + quatre courses synthétiques (format du pilote et du 17 octobre) +
    préenregistrement factice scellé. Rend les chemins utiles."""
    rng = random.Random(graine)
    anciennes = [f"2610.{10000 + i:05d}v1" for i in range(taches)]
    eps_cal = [_episode(rng, t, k) for t in anciennes for k in range(3)]
    eps_new = [_episode(rng, t + SUFFIXE, k) for t in anciennes for k in range(3)]
    # normalisation sur le calibrage (comme construire_banque_t05_v3, sur ses seules lignes)
    bruts = [[math.log(sum(e["jetons_par_action"])), float(e["bilan"]["actions_valides"]),
              statistics.pstdev(e["jetons_par_action"]), rng.gauss(0, 1)] for e in eps_cal]
    moy = [statistics.fmean(b[j] for b in bruts) for j in range(4)]
    ect = [statistics.pstdev([b[j] for b in bruts]) or 1.0 for j in range(4)]
    notes_cal = [_notes_de(rng, e, _z_jetons(e, moy[0], ect[0])) for e in eps_cal]
    moniteurs = {}
    for juge, rub, _, _, _ in MONITEURS:
        valeurs = [n[juge][rub] for n in notes_cal if rub in n.get(juge, {})]
        coupes = b3.classes_equilibrees(valeurs)
        moniteurs[f"{juge}:{rub}"] = {"coupes": list(coupes), "instances": len(valeurs), "juge": juge,
                                      "nombre_issues": len(coupes) + 1, "rubrique": rub}
    for i in range(3):  # moniteurs plantés de la banque d'origine (ignorés par la lecture)
        moniteurs[f"plante:{i}"] = {"coupes": None, "instances": len(eps_cal), "juge": "plante", "nombre_issues": 3,
                                    "rubrique": "plante"}
    instances = []
    for e, b, n in zip(eps_cal, bruts, notes_cal):
        issues = {nom: b3.classe(n[m["juge"]][m["rubrique"]], m["coupes"]) for nom, m in moniteurs.items()
                  if m["juge"] in n and m["rubrique"] in n[m["juge"]]}
        issues.update({f"plante:{i}": rng.randint(0, 2) for i in range(3)})
        instances.append({"g": int(e["episode"][-1]), "identifiant": e["episode"], "issues": issues, "partie": "epreuve",
                          "tache": e["tache"], "z": [round((x - m) / s, 6) for x, m, s in zip(b, moy, ect)]})
    banque = {"nom": "banque-synthetique", "graine": graine, "traits": list(b3.TRAITS), "sous_populations": 3,
              "normalisation": {"moyennes": moy, "ecarts_types": ect}, "moniteurs": moniteurs, "instances": instances,
              "sources": {}, "notes": "synthétique", "parts": {}, "effectifs": {}, "temoins": {}, "toutes_les_passes": False}
    chemin_cal = os.path.join(dossier, "calibrage", "banque-synthetique.json")
    os.makedirs(os.path.dirname(chemin_cal), exist_ok=True)
    with open(chemin_cal, "w", encoding="utf-8") as f:
        json.dump(banque, f)
    # table des identifiants (format du kit de production : tâche d'origine → identifiant « -g2 » → lot)
    table, debut = [], 0
    for c, nb in zip("abcd", courses):
        table += [{"tache_origine": t, "identifiant": t + SUFFIXE, "lot": c} for t in anciennes[debut:debut + nb]]
        debut += nb
    chemin_table = os.path.join(dossier, "table", "table-identifiants-synthetique.json")
    _ecrire_json_et_compagnon(chemin_table, {"source": {}, "schema": "identifiant = tache_origine + « -g2 »",
                                             "cle_de_notation": "juge-<8B|3B>/<identifiant>/e<0|1|2>/passe-<0|1>",
                                             "table": table})
    # courses neuves : épisodes et notations au format réel (décisives : e0 passes 0 et 1, e1 passe 0 ; descriptives :
    # e2 passe 0), dans diag/<run>/ de chaque branche
    runs, debut = [], 0
    for c, nb in zip("abcd", courses):
        taches_c = [t + SUFFIXE for t in anciennes[debut:debut + nb]]
        debut += nb
        run_id = f"20261102-0{c}0000-t05-pilote-reel"
        dossier_run = os.path.join(dossier, "lot", c, "diag", run_id)
        fiches = [e for e in eps_new if e["tache"] in taches_c]
        _ecrire_json_et_compagnon(os.path.join(dossier_run, "episodes.json"),
                                  {"manifeste_sha256": "0" * 64, "run_id": run_id,
                                   "resultat": {"fiches": fiches, "duree_s": 1.0, "descriptifs": {}, "formats": {},
                                                "noyau_attention": "defaut", "noyaux_permis": {}, "reglages": {},
                                                "controle_negatif": {}, "vecteurs": "", "vecteurs_sha256": ""}})
        notations = {(j, sorte): [] for j in ("8B", "3B") for sorte in ("decisives", "descriptives")}
        for e in fiches:
            n = _notes_de(rng, e, _z_jetons(e, moy[0], ect[0]))
            k = e["episode"].rsplit("/e", 1)[1]
            passes = ("passe-0", "passe-1") if k == "0" else ("passe-0",)
            sorte = "descriptives" if k == "2" else "decisives"
            for juge in ("8B", "3B"):
                for passe in passes:
                    notes = dict(n.get(juge, {})) if passe == "passe-0" else _notes_de(rng, e, 0.0).get(juge, {})
                    notations[(juge, sorte)].append({"anomalies": [], "cle": f"juge-{juge}/{e['tache']}/e{k}/{passe}",
                                                     "ensemble_sha256": "0" * 64, "jetons_contexte": 5000,
                                                     "jetons_reponse": 900, "notes": notes, "reponse": "…",
                                                     "score": None, "tronquee": False, "variante": "b0"})
        for (juge, sorte), liste in notations.items():
            _ecrire_json_et_compagnon(os.path.join(dossier_run, f"notations-{juge}-{sorte}.json"),
                                      {"manifeste_sha256": "0" * 64, "run_id": run_id,
                                       "resultat": {"descriptifs": {}, "notations": liste, "noyau": "défaut",
                                                    "noyaux_permis": {}}})
        runs.append(dossier_run)
    prereg = os.path.join(dossier, "prereg", "preenregistrement-factice.md")
    os.makedirs(os.path.dirname(prereg), exist_ok=True)
    with open(prereg, "w", encoding="utf-8") as f:
        f.write("# Préenregistrement factice des essais\n")
    resceller(prereg)
    return {"calibrage": chemin_cal, "empreinte_calibrage": _sha(chemin_cal), "runs": runs, "prereg": prereg,
            "taches_anciennes": anciennes, "table": chemin_table, "empreinte_table": _sha(chemin_table)}


def arguments(f, sortie, reechantillonnages=3):
    a = ["--preenregistrement", f["prereg"], "--calibrage", f["calibrage"], "--empreinte-calibrage",
         f["empreinte_calibrage"], "--table-identifiants", f["table"], "--empreinte-table", f["empreinte_table"],
         "--sortie", sortie, "--reechantillonnages", str(reechantillonnages)]
    for r in f["runs"]:
        a += ["--run", r]
    return a


def lancer(f, sortie, **kw):
    code = lec.principal(arguments(f, sortie, **kw))
    if code == 0:
        with open(os.path.join(sortie, f"{lec.NOM}.json"), encoding="utf-8") as fh:
            return code, json.load(fh)
    with open(os.path.join(sortie, "arret.json"), encoding="utf-8") as fh:
        return code, json.load(fh)


@pytest.fixture(scope="module")
def lot_sain(tmp_path_factory):
    dossier = str(tmp_path_factory.mktemp("lot-sain"))
    f = fabriquer(dossier)
    code, r = lancer(f, os.path.join(dossier, "sortie"))
    return f, code, r


# --- cas sain : course à blanc de bout en bout --------------------------------------------------------------------------
def test_course_a_blanc_de_bout_en_bout(lot_sain):
    f, code, r = lot_sain
    assert code == 0, r
    assert r["a_blanc"] is True
    assert r["epreuve"]["episodes_retenus"] == 288 and r["epreuve"]["taches_retenues"] == 96
    assert r["calibrage"]["garde_A7"]["applique"] is False
    assert r["lot"]["comptes"]["taches_appariees_au_calibrage_par_suffixe"] == {"une": 96}
    assert sorted(r["lot"]["comptes"]["lots_des_courses"].values()) == ["a", "b", "c", "d"]
    assert sum(1 for v in r["lot"]["comptes"]["fichiers_de_notations"].values() if v == "absent") == 0
    # e0 a deux passes : seule la première est lue
    assert r["lot"]["comptes"]["notations_passe_0"] < r["lot"]["comptes"]["notations_lues"]
    assert set(r["instances_par_moniteur"]) == {"8B:RIGOR", "8B:NOVELTY", "3B:BALANCE", "3B:COHERENCE"}
    assert os.path.exists(os.path.join(os.path.dirname(os.path.dirname(f["prereg"])), "sortie", f"{lec.NOM}.md"))


def test_loi_vraie_declaree_par_la_regle_et_promue_sous_le_plan_plein(lot_sain):
    _, _, r = lot_sain
    vrais = [i for i, v in r["familles"]["R"]["verdicts"]["plein"].items() if v["temoin"] == "vraie"]
    assert vrais == ["T-8B-RIGO-log_jeto-vrai"], vrais
    v = r["familles"]["R"]["verdicts"]["plein"]["T-8B-RIGO-log_jeto-vrai"]
    assert v["e_bh"] is True and v["n_plan"] == v["n_reservoir"] == r["instances_par_moniteur"]["8B:RIGOR"]
    assert r["lecture"]["L3_reel"]["etat"] == "dents" and r["lecture"]["L3_reel"]["fraction"] == 1.0
    assert r["lecture"]["L3_reel"]["reechantillonnage"]["repliques"] == 3


def test_temoins_faux_refuses(lot_sain):
    _, _, r = lot_sain
    assert r["lecture"]["L1"]["tenu"] is True
    for fam in ("T", "R"):
        for bras in ("plein", "gele"):
            for i, v in r["familles"][fam]["verdicts"][bras].items():
                if v["temoin"] == "fausse":
                    assert v["e_bh"] is False, (fam, bras, i)


def test_temoins_plantes_et_plans(lot_sain):
    _, _, r = lot_sain
    T = r["familles"]["T"]["verdicts"]
    assert T["plein"]["TVP03"]["e_bh"] is True  # force 0,8
    assert all(T["plein"][i]["n_plan"] == 288 for i in ("TVP01", "TVP02", "TVP03"))
    assert all(T["gele"][i]["n_plan"] == 120 for i in ("TVP01", "TVP02", "TVP03"))
    assert r["familles"]["T"]["m"] == 4 + 6 and r["familles"]["R"]["m"] == 4 + 4
    assert r["configurations"]["plein"]["taille_plan"] == 288 and r["configurations"]["gele"]["taille_plan"] == 120
    for b in ("plein", "gele"):
        assert r["configurations"][b]["nul_archive"] and r["configurations"][b]["nul_archive_ajuste"]
    assert r["lecture"]["issue"]["code"] in ("I1", "I2", "I4", "I5")
    assert r["lecture"]["exposition"]["lectures_de_l_epreuve"] == 1


def test_invariant_du_prefixe(lot_sain):
    """Le plan gelé est le préfixe du plan plein (même mélange, même tri) : log W max plein ≥ gelé, et un témoin vrai promu
    sous le plan gelé l'est sous le plan plein ; la garde lève I5 sur un artefact (plan gelé altéré)."""
    _, _, r = lot_sain
    assert r["lecture"]["invariant_prefixe"] == {"tenu": True, "ecarts": []}
    for fam in ("T", "R"):
        for i, p in r["familles"][fam]["verdicts"]["plein"].items():
            g = r["familles"][fam]["verdicts"]["gele"][i]
            assert p["log_w_max"] >= g["log_w_max"] - 1e-6 and g["empreinte_plan"] == p["empreinte_prefixe_gele"], (fam, i)
    altere = copy.deepcopy(r)
    altere["familles"]["T"]["verdicts"]["gele"]["TVP01"]["empreinte_plan"] = "0" * 64
    L = lec.lectures(altere)
    assert L["invariant_prefixe"]["tenu"] is False and L["issue"]["code"] in ("I3", "I4", "I5")
    assert any("TVP01" in m for m in L["audit_R4"]["motifs"])


def test_lois_connues_jugees_sous_le_monde_aveugle(lot_sain):
    _, _, r = lot_sain
    R = r["familles"]["R"]["verdicts"]["plein"]
    lr = sorted(i for i in R if i.startswith("LR-"))
    assert lr == ["LR-3B-BALANCE", "LR-3B-COHERENCE", "LR-8B-NOVELTY", "LR-8B-RIGOR"]
    assert r["familles"]["R"]["monde"] == "aveugle" and r["familles"]["T"]["monde"] == "informé"


def test_reechantillonnage_independant_du_nombre_de_processus(lot_sain, tmp_path):
    """Mêmes répliques (graine dérivée de l'empreinte) quel que soit le nombre de processus : mêmes résumés."""
    f, _, r1 = lot_sain
    args = arguments(f, str(tmp_path / "deux-processus")) + ["--processus", "2"]
    assert lec.principal(args) == 0
    with open(tmp_path / "deux-processus" / f"{lec.NOM}.json", encoding="utf-8") as fh:
        r2 = json.load(fh)
    for cle in ("L3_plante", "L3_reel"):
        assert r1["lecture"][cle]["reechantillonnage"] == r2["lecture"][cle]["reechantillonnage"]
    assert r1["familles"] == r2["familles"]


def test_sortie_refusee_dans_le_depot_public(lot_sain):
    f, _, _ = lot_sain
    interdite = os.path.join(RACINE, "resultats-interdits-essai")
    with pytest.raises(SystemExit):
        lec.principal(arguments(f, interdite))
    assert not os.path.exists(interdite)


def test_sortie_jamais_ecrasee(lot_sain, tmp_path):
    f, _, _ = lot_sain
    sortie = tmp_path / "pleine"
    sortie.mkdir()
    (sortie / "x").write_text("x")
    with pytest.raises(FileExistsError):
        lec.principal(arguments(f, str(sortie)))


# --- liste d'arrêt : chaque garde sur un artefact -------------------------------------------------------------------------
def _nouveau_lot(tmp_path):
    return fabriquer(str(tmp_path / "lot"))


def _arret(f, tmp_path):
    code, r = lancer(f, str(tmp_path / "sortie"), reechantillonnages=0)
    assert code == 2, r
    assert sorted(os.listdir(tmp_path / "sortie")) == ["arret.json"]
    return r["arret"], r["message"]


def test_arret_fichier_manquant(tmp_path):
    f = _nouveau_lot(tmp_path)
    os.remove(os.path.join(f["runs"][3], "episodes.json"))
    assert _arret(f, tmp_path)[0] == "A1"


def test_arret_compagnon_manquant(tmp_path):
    f = _nouveau_lot(tmp_path)
    os.remove(os.path.join(f["runs"][0], "notations-3B-decisives.json.sha256"))
    assert _arret(f, tmp_path)[0] == "A1"


def test_arret_empreinte_discordante_lot(tmp_path):
    f = _nouveau_lot(tmp_path)
    chemin = os.path.join(f["runs"][1], "notations-8B-decisives.json")
    with open(chemin, "a", encoding="utf-8") as fh:
        fh.write(" ")
    assert _arret(f, tmp_path)[0] == "A2"


def test_arret_empreinte_discordante_calibrage(tmp_path):
    f = _nouveau_lot(tmp_path)
    f["empreinte_calibrage"] = "1" * 64
    code, message = _arret(f, tmp_path)
    assert code == "A2" and "calibrage" in message


def test_arret_empreinte_discordante_preenregistrement(tmp_path):
    f = _nouveau_lot(tmp_path)
    with open(f["prereg"], "a", encoding="utf-8") as fh:
        fh.write("modifié après scellement\n")
    assert _arret(f, tmp_path)[0] == "A2"


def test_arret_notation_en_double(tmp_path):
    f = _nouveau_lot(tmp_path)
    chemin = os.path.join(f["runs"][2], "notations-3B-decisives.json")
    with open(chemin, encoding="utf-8") as fh:
        d = json.load(fh)
    d["resultat"]["notations"].append(copy.deepcopy(d["resultat"]["notations"][5]))
    with open(chemin, "w", encoding="utf-8") as fh:
        json.dump(d, fh)
    resceller(chemin)
    code, message = _arret(f, tmp_path)
    assert code == "A3" and "double" in message


def test_arret_notation_en_double_entre_deux_fichiers(tmp_path):
    f = _nouveau_lot(tmp_path)
    source = os.path.join(f["runs"][0], "notations-8B-decisives.json")
    sup = tmp_path / "sup"
    sup.mkdir()
    with open(source, encoding="utf-8") as fh:
        d = json.load(fh)
    d["resultat"]["notations"] = d["resultat"]["notations"][:2]
    cible = str(sup / "notations-8B-decisives.json")
    with open(cible, "w", encoding="utf-8") as fh:
        json.dump(d, fh)
    resceller(cible)
    args = arguments(f, str(tmp_path / "sortie"), reechantillonnages=0) + ["--notations-sup", str(sup)]
    assert lec.principal(args) == 2
    with open(tmp_path / "sortie" / "arret.json", encoding="utf-8") as fh:
        assert json.load(fh)["arret"] == "A3"


def test_arret_tache_des_deux_cotes(tmp_path):
    f = _nouveau_lot(tmp_path)
    run = f["runs"][0]
    ancienne = f["taches_anciennes"][0]
    for nom in ("episodes.json", "notations-8B-decisives.json", "notations-3B-decisives.json"):
        chemin = os.path.join(run, nom)
        with open(chemin, encoding="utf-8") as fh:
            texte = fh.read()
        with open(chemin, "w", encoding="utf-8") as fh:
            fh.write(texte.replace(ancienne + SUFFIXE, ancienne))  # la tâche n'est plus renommée
        resceller(chemin)
    code, message = _arret(f, tmp_path)
    assert code == "A5" and ancienne in message


def _renommer_dans_la_course(run, avant, apres):
    for nom in os.listdir(run):
        if nom.endswith(".json"):
            chemin = os.path.join(run, nom)
            with open(chemin, encoding="utf-8") as fh:
                texte = fh.read()
            with open(chemin, "w", encoding="utf-8") as fh:
                fh.write(texte.replace(avant, apres))
            resceller(chemin)


def test_arret_tache_sans_suffixe_g2(tmp_path):
    f = _nouveau_lot(tmp_path)
    ancienne = f["taches_anciennes"][1]
    _renommer_dans_la_course(f["runs"][0], ancienne + SUFFIXE, ancienne + "-g3")
    code, message = _arret(f, tmp_path)
    assert code == "A5" and "-g2" in message


def test_arret_tache_g2_au_calibrage(tmp_path):
    f = _nouveau_lot(tmp_path)
    with open(f["calibrage"], encoding="utf-8") as fh:
        b = json.load(fh)
    t0 = b["instances"][0]["tache"]
    for l in b["instances"]:
        if l["tache"] == t0:
            l["tache"], l["identifiant"] = t0 + "-g2", l["identifiant"].replace(t0, t0 + "-g2")
    with open(f["calibrage"], "w", encoding="utf-8") as fh:
        json.dump(b, fh)
    f["empreinte_calibrage"] = _sha(f["calibrage"])
    code, message = _arret(f, tmp_path)
    assert code == "A5" and "calibrage" in message


def test_descriptives_absentes_permises(tmp_path):
    """Échéance de 15 000 s avant les descriptives : e2 non noté, la lecture continue sans ces épisodes."""
    f = _nouveau_lot(tmp_path)
    for juge in ("8B", "3B"):
        for suffixe in ("", ".sha256"):
            os.remove(os.path.join(f["runs"][0], f"notations-{juge}-descriptives.json{suffixe}"))
    code, r = lancer(f, str(tmp_path / "sortie"), reechantillonnages=0)
    assert code == 0, r
    assert r["epreuve"]["exclus_sans_notation"] == 30 and r["epreuve"]["episodes_retenus"] == 258
    assert sum(1 for v in r["lot"]["comptes"]["fichiers_de_notations"].values() if v == "absent") == 2


def test_arret_decisives_manquantes(tmp_path):
    f = _nouveau_lot(tmp_path)
    for suffixe in ("", ".sha256"):
        os.remove(os.path.join(f["runs"][1], "notations-8B-decisives.json" + suffixe))
    code, message = _arret(f, tmp_path)
    assert code == "A1" and "décisives" in message


def test_arret_lot_manquant(tmp_path):
    f = _nouveau_lot(tmp_path)
    f["runs"] = f["runs"][:3]
    code, message = _arret(f, tmp_path)
    assert code == "A1" and "'d'" in message


def test_arret_table_discordante(tmp_path):
    f = _nouveau_lot(tmp_path)
    f["empreinte_table"] = "2" * 64
    code, message = _arret(f, tmp_path)
    assert code == "A2" and "table" in message


def test_arret_moniteur_trop_pauvre(tmp_path):
    f = _nouveau_lot(tmp_path)
    garde = 0
    for chemin in [os.path.join(r, f"notations-3B-{s}.json") for r in f["runs"] for s in ("decisives", "descriptives")]:
        # on retire la note BALANCE du 3B partout sauf sur 40 épisodes
        with open(chemin, encoding="utf-8") as fh:
            d = json.load(fh)
        for n in d["resultat"]["notations"]:
            if "BALANCE" in n["notes"] and n["cle"].endswith("passe-0"):
                garde += 1
                if garde > 40:
                    del n["notes"]["BALANCE"]
        with open(chemin, "w", encoding="utf-8") as fh:
            json.dump(d, fh)
        resceller(chemin)
    code, message = _arret(f, tmp_path)
    assert code == "A4" and "3B:BALANCE" in message
    assert "notes" not in message and "issue" not in message


def test_arret_format_variante(tmp_path):
    f = _nouveau_lot(tmp_path)
    chemin = os.path.join(f["runs"][3], "notations-8B-decisives.json")
    with open(chemin, encoding="utf-8") as fh:
        d = json.load(fh)
    d["resultat"]["notations"][0]["variante"] = "b1"
    with open(chemin, "w", encoding="utf-8") as fh:
        json.dump(d, fh)
    resceller(chemin)
    assert _arret(f, tmp_path)[0] == "A6"


def test_arret_notation_sans_episode(tmp_path):
    f = _nouveau_lot(tmp_path)
    chemin = os.path.join(f["runs"][3], "notations-8B-decisives.json")
    with open(chemin, encoding="utf-8") as fh:
        d = json.load(fh)
    n = copy.deepcopy(d["resultat"]["notations"][0])
    n["cle"] = "juge-8B/9999.99999v1" + SUFFIXE + "/e0/passe-0"
    d["resultat"]["notations"].append(n)
    with open(chemin, "w", encoding="utf-8") as fh:
        json.dump(d, fh)
    resceller(chemin)
    assert _arret(f, tmp_path)[0] == "A6"


def _prereg_avec_bloc(f, alterer=None):
    """Préenregistrement factice portant le bloc d'empreintes du code (état actuel des fichiers), rescellé."""
    lignes = []
    for chemin in lec.FICHIERS_DE_CODE_EXIGES + ("pole/selection_pari.py",):
        h = _sha(os.path.join(RACINE, chemin))
        if alterer == chemin:
            h = ("0" if h[0] != "0" else "1") + h[1:]
        lignes.append(f"{h}  {chemin}")
    with open(f["prereg"], "w", encoding="utf-8") as fh:
        fh.write("# Préenregistrement factice\n\n```\n" + "\n".join(lignes) + "\n```\n")
    resceller(f["prereg"])


def test_arret_table_de_rangs(tmp_path, monkeypatch):
    """A7 : sur le calibrage du préenregistrement, la règle doit redonner la table écrite ; on simule ce calibrage
    (cas sain de la vérification du code : bloc d'empreintes juste)."""
    f = _nouveau_lot(tmp_path)
    _prereg_avec_bloc(f)
    monkeypatch.setattr(lec, "EMPREINTE_CALIBRAGE", f["empreinte_calibrage"])  # le calibrage synthétique joue le réel
    code, message = _arret(f, tmp_path)
    assert code == "A7" and "table de rangs" in message


def test_arret_code_different_du_preenregistrement(tmp_path, monkeypatch):
    f = _nouveau_lot(tmp_path)
    _prereg_avec_bloc(f, alterer="pole/selection_pari.py")
    monkeypatch.setattr(lec, "EMPREINTE_CALIBRAGE", f["empreinte_calibrage"])
    code, message = _arret(f, tmp_path)
    assert code == "A2" and "pole/selection_pari.py" in message


def test_arret_bloc_d_empreintes_absent_hors_course_a_blanc(tmp_path, monkeypatch):
    f = _nouveau_lot(tmp_path)
    monkeypatch.setattr(lec, "EMPREINTE_CALIBRAGE", f["empreinte_calibrage"])
    code, message = _arret(f, tmp_path)
    assert code == "A2" and "bloc d'empreintes" in message


def test_aucun_message_d_arret_ne_porte_de_note(tmp_path):
    """Les messages d'arrêt citent des fichiers, des clés et des comptes, jamais une note ni une issue."""
    f = _nouveau_lot(tmp_path)
    chemin = os.path.join(f["runs"][2], "notations-3B-decisives.json")
    with open(chemin, encoding="utf-8") as fh:
        d = json.load(fh)
    d["resultat"]["notations"].append(copy.deepcopy(d["resultat"]["notations"][0]))
    with open(chemin, "w", encoding="utf-8") as fh:
        json.dump(d, fh)
    resceller(chemin)
    _, message = _arret(f, tmp_path)
    notes = d["resultat"]["notations"][0]["notes"]
    assert "notes" not in message and all(f"'{k}'" not in message for k in notes)


# --- juge à plan pleine épreuve -----------------------------------------------------------------------------------------
def test_plan_plus_petit_que_l_epreuve_refuse():
    with pytest.raises(jpp.PlanPleinRefuse):
        jpp.configuration_plan_plein(288, taille_plan=120)
    with pytest.raises(jpp.PlanPleinRefuse):
        jpp.configuration_plan_plein(0)
    c = jpp.configuration_plan_plein(288)
    assert c.taille_plan == 288 and c.nul_archive_ajuste is True and c.multiplicite == "e-bh" and c.urne is False
    assert jpp.configuration_plan_gele().taille_plan == 120


def test_plan_tronque_refuse(lot_sain, tmp_path):
    """Garde du bras plein sur un engagement réel : plan entier accepté, plan tronqué d'une instance refusé."""
    f, _, _ = lot_sain
    banque_cal = lec.lire_calibrage(f["calibrage"], f["empreinte_calibrage"])
    temoins, _, _ = lec.temoins_de_calibrage(banque_cal)
    lot = lec.lire_lot(f["runs"], [], banque_cal)
    graines = lec.graines_de("ab" * 32)
    instances, _ = lec.construire_epreuve(lot, banque_cal, graines["bruit"])
    banque, _ = lec.banque_complete(banque_cal, instances, graines)
    chemin = lec._ecrire_banque(banque, str(tmp_path))
    monde = lec.MondeBanque(chemin, jpp.GRAINE_DU_JUGE, nul_informe=True)
    fiche = next(t for t in temoins if t.temoin == "fausse")
    reservoir = monde.reservoir(fiche, 0)
    config = jpp.configuration_plan_plein(len(instances))
    gele = lec.preparer_engagement(fiche, config, None, reservoir=reservoir,
                                   membres_supplementaires=monde.membres_informes(fiche), moniteur=monde.moniteur_de(fiche))
    assert jpp.verifier_plan_plein(gele, reservoir) is gele
    with pytest.raises(jpp.PlanPleinRefuse):
        jpp.verifier_plan_plein(gele, reservoir[:-1])
    gele_120 = lec.preparer_engagement(fiche, jpp.configuration_plan_gele(), None, reservoir=reservoir,
                                       membres_supplementaires=monde.membres_informes(fiche), moniteur=monde.moniteur_de(fiche))
    if len(reservoir) > 120:
        with pytest.raises(jpp.PlanPleinRefuse):
            jpp.verifier_plan_plein(gele_120, reservoir)


def test_nul_v8_impose():
    with pytest.raises(NulV8Refuse):
        jpp.configuration_nul_v8(taille_plan=288, nul_archive_ajuste=False, **jpp.REGLAGES_COMMUNS)


# --- graines (R9) et courbe ---------------------------------------------------------------------------------------------
def test_graines_derivees_de_l_empreinte():
    a, b = lec.graines_de("ab" * 32), lec.graines_de("ab" * 32)
    c = lec.graines_de("ac" * 32)
    assert a["plantation"] == b["plantation"] != c["plantation"]
    import numpy as np
    assert np.random.default_rng(a["bruit"]).standard_normal() == np.random.default_rng(b["bruit"]).standard_normal()


def test_conditionnel_aux_paires():
    plantes = [{"i": 2, "j": 0, "force": 0.3}, {"i": 0, "j": 2, "force": 0.5}, {"i": 1, "j": 2, "force": 0.8}]
    c288, c192 = lec.conditionnel_aux_paires(plantes, 288), lec.conditionnel_aux_paires(plantes, 192)
    p288 = [lec.PUISSANCE_PAR_PAIRE_288[(2, 0, 0.3)][0], lec.PUISSANCE_PAR_PAIRE_288[(0, 2, 0.5)][0],
            lec.PUISSANCE_PAR_PAIRE_288[(1, 2, 0.8)][0]]
    assert c288["applicable"] and c288["attendu_plein"] == pytest.approx(sum(p288), abs=1e-3)
    p = p288
    attendu = p[0] * p[1] * p[2] + p[0] * p[1] * (1 - p[2]) + p[0] * (1 - p[1]) * p[2] + (1 - p[0]) * p[1] * p[2]
    assert c288["proba_fraction_au_moins_deux_tiers"] == pytest.approx(round(attendu, 3))
    assert c288["proba_I4"] == pytest.approx((1 - p[1]) * (1 - p[2]), abs=1e-4)
    assert c192["attendu_plein"] < c288["attendu_plein"]  # la table à 192 est plus faible
    c240 = lec.conditionnel_aux_paires(plantes, 240)
    assert c240["attendu_plein"] == pytest.approx((c192["attendu_plein"] + c288["attendu_plein"]) / 2, abs=2e-3)
    assert lec.conditionnel_aux_paires(plantes, 100)["attendu_plein"] == c192["attendu_plein"]  # bornée à 192
    assert lec.conditionnel_aux_paires([{"i": 0, "j": 1, "force": 0.4}], 288)["applicable"] is False
    for t in (lec.PUISSANCE_PAR_PAIRE_192, lec.PUISSANCE_PAR_PAIRE_288):  # invariant du préfixe dans les tables
        assert len(t) == 18 and all(pl >= ge for pl, ge in t.values())


def test_courbe_et_bornes():
    assert lec.puissance_courbe(0.5, 288, "plein") == pytest.approx(0.964)
    assert lec.puissance_courbe(0.5, 288, "gele") == pytest.approx(0.734)
    assert lec.puissance_courbe(0.3, 234, "plein") == pytest.approx(0.31 + (0.612 - 0.31) * 54 / 108)
    b288 = lec.borne_information(288)
    assert 0.45 < b288["force"] < 0.48 and 0.05 < b288["information_nat"] < 0.056
    assert lec.borne_information(120)["force"] > lec.borne_information(180)["force"] > b288["force"]
    assert lec.borne_information(60) is None  # force 0,8 sous 0,9 à N = 60
