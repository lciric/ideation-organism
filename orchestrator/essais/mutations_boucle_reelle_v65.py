"""Banc de mutations du code v65 (gardes 17 à 22, gardes de dépense, lecture gelée C1 à C6 et A1 à A4) : chaque mutation est un
remplacement textuel exact (une seule occurrence exigée) dans une copie neuve de `orchestrator/` ; elle est « tuée » si les essais
nommés échouent sur la copie mutée. Une mutation dont le texte d'origine est absent ou ambigu est un défaut du banc (jamais
« tuée »). Le banc commence par jouer les mêmes essais sur la copie **non mutée** : ils doivent réussir (sinon le banc s'arrête).

  POLE_ESSAI_BAC_REEL_NON_JOUE=1 python3 -I -B essais/mutations_boucle_reelle_v65.py [--processus 4] [--sortie RESULTAT.json]
Codes : 0 toutes tuées ; 1 au moins une survit ou un défaut du banc ; 2 essais sains en échec.
"""

import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
C, LB, DL = "pole/boucle_reelle_v65.py", "pole/lecture_boucle_reelle_v65.py", "demonstrations/boucle_reelle_v65.py"
TB, TL = "essais/test_boucle_reelle_v65.py", "essais/test_lecture_boucle_reelle_v65.py"

# (identifiant, fichier, texte d'origine, texte muté, essais [(fichier, sélection -k)])
MUTATIONS = [
    ("G17-empreinte", C, 'h = bf.lire_scelle_verifie(chemin, sha_du_texte, "héritage de départ")',
     'h = json.load(open(chemin, encoding="utf-8"))', [(TB, "HeritageDepart")]),
    ("G17-K1-alteree", C, 'if not _egales(archive, jeu["archive_de_depart"]):', 'if False:', [(TB, "HeritageDepart")]),
    ("G17-statut", C, 'if h.get("statut") != {k: STATUT_K1 for k in ARCHIVE_DE_DEPART}:', 'if False:', [(TB, "HeritageDepart")]),
    ("G17-cles", C, 'if not isinstance(archive, dict) or sorted(archive) != sorted(ARCHIVE_DE_DEPART):', 'if not isinstance(archive, dict):',
     [(TB, "HeritageDepart")]),
    ("G19-empreinte", C, 'if not isinstance(sha_attendue, str) or sha != sha_attendue:', 'if False:', [(TB, "JeuPlante")]),
    ("G19-classe-tout", C, '    connues = list(archive.values())\n    if not connues or not isinstance(loi, dict):\n        return None',
     '    connues = list(archive.values())\n    return "copie d\'une loi de l\'archive"', [(TB, "JeuPlante")]),
    ("G19-melange-non-fixe", C, 'if None in sortes or "archive" not in sortes:', 'if "archive" not in sortes:', [(TB, "JeuPlante")]),
    ("G19-composition", C, 'if cles and cles <= {"puissance", "inclinaison"}:', 'if cles:', [(TB, "JeuPlante")]),
    ("G19-incomplet", C, 'if not isinstance(jeu[groupe], dict) or sorted(jeu[groupe]) != sorted(noms):',
     'if not isinstance(jeu[groupe], dict):', [(TB, "JeuPlante")]),
    ("G18-garde", C, 'if d["membres_d_archive"] != attendus or (archive and d["membres_d_archive"] == 0):', 'if False:',
     [(TB, "JugeAvecArchive")]),
    ("M3-canal-v64", C, 'a_plantees = archive if archive_des_plantees is None else archive_des_plantees',
     'a_plantees = {} if archive_des_plantees is None else archive_des_plantees', [(TB, "JugeAvecArchive")]),
    ("M3-hors-famille", C, 'promue = bool(ev["promue"]) and log_e >= seuil', 'promue = bool(ev["promue"])', [(TB, "seuil")]),
    ("G20-bras", C, '    if b != BRAS:\n        raise BrasRefuse', '    if False:\n        raise BrasRefuse', [(TB, "BrasEtGeneration2 and garde_20")]),
    ("D2-generations", C, 'if plan.get("generations") != GENERATIONS:', 'if False:', [(TB, "deux_generations")]),
    ("G21-ordre", C, 'ordre = sorted(retenues, key=lambda i: (-float(log_e_g1[i]), i))[:n]',
     'ordre = sorted(retenues, key=lambda i: (float(log_e_g1[i]), i))[:n]', [(TB, "copies_garde_21")]),
    ("G21-exiger", C, 'if src not in (heritage.get("retenues") or []) or not _egales(loi, (heritage.get("archive") or {}).get(src)):',
     'if False:', [(TB, "copies_garde_21")]),
    ("M4-g2-sans-selection", C, 'sha2, _ = jouer_generation(d2, 2, monde, jeu, h2,', 'sha2, _ = jouer_generation(d2, 2, monde, jeu, heritage_depart,',
     [(TB, "la_generation_2_lit")]),
    ("GO-cœur", C, '    if reel and not (isinstance(go, dict) and isinstance(go.get("identifiant"), str) and go.get("plafond_lu_usd")):',
     '    if False:', [(TB, "test_go")]),
    ("PART-avant-appel", C, '        exiger_part_avant_appel(compteur, p.relais, p.budget)\n', '', [(TB, "Depense")]),
    ("L-C5-incomplet", LB, 'partiel = bool(releve.get("arret")) or not releve.get("complet")', 'partiel = bool(releve.get("arret"))',
     [(TL, "C5")]),
    ("L-C5-masque-C2", LB, '        if fausses_promues:\n            aussi.append("C2 (partielle)")', '        pass', [(TL, "C5")]),
    ("L-ordre-C4-C2", LB, '    elif ecarts or copies_promues:\n        code = "C4"\n    elif fausses_promues:\n        code = "C2"',
     '    elif fausses_promues:\n        code = "C2"\n    elif ecarts or copies_promues:\n        code = "C4"', [(TL, "prime_sur_C2")]),
    ("L-C3-survit", LB, 'vraies_survivantes = sorted(n for n, p in vraies_g1.items() if p["promue"] and p.get("verdict") == "survit")',
     'vraies_survivantes = sorted(n for n, p in vraies_g1.items() if p["promue"])', [(TL, "C3")]),
    ("L-C6-T-MAL", LB, 'and t_mal["gardien"] == "refuse"', 'and True', [(TL, "C6")]),
    ("L-ordre-C3-C6", LB, '    elif not vraies_survivantes:\n        code = "C3"\n    elif not p4:\n        code = "C6"',
     '    elif not p4:\n        code = "C6"\n    elif not vraies_survivantes:\n        code = "C3"', [(TL, "prime_sur_C6")]),
    ("L-P6-empreinte", LB, 'if not ls.get("attendu") or ls.get("attendu") != ls.get("lu"):', 'if False:', [(TL, "C4_lecture")]),
    ("L-P6-membres", LB, 'if c.get("generation") == 2 and c.get("gardien") == "passe" and c.get("membres_d_archive") != attendus:',
     'if False:', [(TL, "C4_lecture")]),
    ("L-copie-promue", LB, '    elif ecarts or copies_promues:\n        code = "C4"', '    elif ecarts:\n        code = "C4"', [(TL, "C4_copie")]),
    ("L-A1", LB, 'if lecture["code"] == "C1":  # « trop beau », d\'office', 'if False:', [(TL, "A1")]),
    ("L-A2-diagnostic", LB, '"diagnostic": "jugée sans archive : défaut de chaîne" if not p.get("membres_d_archive")',
     '"diagnostic": "membre du nul promu : défaut numérique" if not p.get("membres_d_archive")', [(TL, "A2")]),
    ("L-A2-rejeu", LB, '    if monde is not None and sortie["audits"]["A2"]:', '    if False:', [(TL, "A2_rejeu_dans")]),
    ("N-parts", DL, 'if centimes["plafond_kimi_usd"] + centimes["plafond_argon_usd"] != centimes["plafond_modeles_usd"]:', 'if False:',
     [(TB, "PlanGele")]),
    ("N-GO-montant", DL, 'if centimes["plafond_modeles_usd"] + centimes["plafond_machine_usd"] != centimes["go_montant_usd"]:', 'if False:',
     [(TB, "PlanGele")]),
    ("N-bras-plan", DL, '    if lignes["bras"] != "reel_seul":', '    if False:', [(TB, "PlanGele")]),
    ("N-commande-v6", DL, 'if not os.path.isfile(e["chemin"]) or sha256_fichier(e["chemin"]) != e["sha256"]:', 'if not os.path.isfile(e["chemin"]):',
     [(TB, "ConfigurationV5")]),
    ("N-machine-version", DL, '    if version is None or tuple(version) < BWRAP_MIN:', '    if version is None:', [(TB, "garde_22")]),
    ("N-brouillon", DL, 'or not NOM_PREREG.match(base) or "brouillon" in base:', 'or "brouillon_" in base:', [(TB, "TexteScelle")]),
    ("N-bac-factice", DL, '        parent_bac, fabrique = L64.preparer_bac(args.bac, args.utilisateur_bac)',
     '        parent_bac, fabrique = L64.preparer_bac("factice", args.utilisateur_bac)', [(TB, "bwrap_absent")]),
]


def essayer(dossier, essais):
    env = dict(os.environ, POLE_ESSAI_BAC_REEL_NON_JOUE="1", PYTHONDONTWRITEBYTECODE="1")
    for fichier, k in essais:
        r = subprocess.run([sys.executable, "-I", "-B", "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", fichier, "-k", k],
                           cwd=dossier, capture_output=True, text=True, timeout=900, env=env)
        derniere = (r.stdout.strip().splitlines() or [""])[-1]
        if r.returncode != 0:
            return False, derniere
        if " passed" not in derniere and " skipped" not in derniere:
            return False, f"aucun essai joué : {derniere}"
    return True, derniere


def copier():
    d = tempfile.mkdtemp(prefix="mutation-v65-")
    shutil.copytree(RACINE, os.path.join(d, "orchestrator"), ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    return d, os.path.join(d, "orchestrator")


def une(m):
    ident, fichier, avant, apres, essais = m
    d, o = copier()
    try:
        chemin = os.path.join(o, fichier)
        with open(chemin, encoding="utf-8") as f:
            s = f.read()
        if s.count(avant) != 1:
            return {"mutation": ident, "fichier": fichier, "issue": "défaut du banc", "motif": f"texte d'origine trouvé {s.count(avant)} fois"}
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(s.replace(avant, apres))
        ok, derniere = essayer(o, essais)
        return {"mutation": ident, "fichier": fichier, "issue": "survit" if ok else "tuée", "essais": essais, "derniere_ligne": derniere}
    finally:
        shutil.rmtree(d, True)


def principal(argv=None):
    a = argparse.ArgumentParser()
    a.add_argument("--processus", type=int, default=4)
    a.add_argument("--sortie")
    a.add_argument("--seulement")
    x = a.parse_args(argv)
    debut = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    choisies = [m for m in MUTATIONS if not x.seulement or m[0] in x.seulement.split(",")]
    d, o = copier()
    try:
        tous = sorted({e for m in choisies for e in m[4]})
        ok, derniere = essayer(o, tous)
    finally:
        shutil.rmtree(d, True)
    if not ok:
        print(f"essais sains en échec sur la copie non mutée : {derniere}")
        return 2
    with ThreadPoolExecutor(max_workers=x.processus) as ex:
        res = list(ex.map(une, choisies))
    for r in res:
        print(f"{r['mutation']:24s} {r['issue']:14s} {r.get('derniere_ligne') or r.get('motif')}")
    tuees = sum(r["issue"] == "tuée" for r in res)
    print(f"{tuees} tuées sur {len(res)} mutations")
    if x.sortie:
        with open(x.sortie, "w", encoding="utf-8") as f:
            json.dump({"debut_utc": debut, "fin_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                       "resultats": res, "tuees": tuees, "n": len(res)}, f, ensure_ascii=False, indent=1)
    return 0 if tuees == len(res) else 1


if __name__ == "__main__":
    sys.exit(principal())
