"""Répétition générale (version 0.6.0, pièce 3 du premier lancement réel) : une course entière du pôle par l'adaptateur
**réel** (`AdaptateurClaudeSDK`), le relais de clé **réel** (autre processus, clé factice dans son seul environnement),
un amont factice local et un faux moteur qui imite le Claude Agent SDK — **sans appel de modèle, sans vraie clé, sans
réseau, sans dépense**. C'est le chemin exact du premier lancement (option a du devis), sauf le modèle.

Ce qu'elle vérifie, et écrit dans `repetition-generale-v6.json` (scellé) :
1. la course va au bout (générations exécutées, aucune fiche « indécise » ni « retirée » par défaut du moteur) ;
2. témoins : aucune fausse gardée, aucune vraie éliminée ;
3. monde du noyau : `mesures.json` déposé pour chaque expérience, issues déclarées identiques ; graine secrète écrite
   après coup sous `noyau/`, absente des dossiers d'agents ;
4. relais : un appel par agent lancé, tous servis (statut 200) avec la clé ajoutée par le relais, dépense comptée ;
5. garde des outils (crochet du kit) : les appels interdits (réseau, chemin hors dossier, outil non permis) refusés, les
   appels permis acceptés — pour chaque agent ;
6. la clé factice n'apparaît ni dans le dossier de la course, ni dans la sortie de l'orchestrateur, ni dans les journaux ;
7. contre-essai : l'orchestrateur lancé avec un nom de variable de clé dans son environnement s'arrête (code 2,
   `CleDansEnvironnement`) avant tout agent, et le relais ne reçoit rien.

Le faux moteur doit être importable par le seul processus de l'orchestrateur : celui-ci est lancé avec `-P -s` (pas `-I`,
qui ignorerait `PYTHONPATH`) et `PYTHONPATH=essais/faux_sdk`. Au vrai lancement, le Python de l'opérateur porte le vrai kit.

Usage : python -I -B demonstrations/repetition_generale_v6.py DOSSIER_NEUF [--generations 2] [--horodatage HH:MM UTC]
"""

import argparse
import json
import os
import subprocess
import sys
import time

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)

from essais.faux_sdk.amont_factice import CLE_FACTICE, AmontFactice  # noqa: E402
from pole.outils import ecrire_json_scelle, horodatage, sha256_fichier  # noqa: E402

EXEMPLES = os.path.join(RACINE, "exemples")
INTERDITS = {("Bash", "curl http://example.com/"), ("Read", "/etc/passwd"), ("WebFetch", "http://example.com/")}
PERMIS = {("Read", "fiche.json"), ("Bash", "ls")}


def _lire_jsonl(chemin):
    if not os.path.exists(chemin):
        return []
    with open(chemin, encoding="utf-8") as f:
        return [json.loads(ligne) for ligne in f if ligne.strip()]


def _fichiers(dossier):
    for racine, _, noms in os.walk(dossier):
        for nom in noms:
            yield os.path.join(racine, nom)


def _contient(chemin, motif):
    with open(chemin, "rb") as f:
        return motif in f.read()


def lancer_relais(amont_url, journal, plafond=5.0):
    proc = subprocess.Popen([sys.executable, "-I", "-B", os.path.join(RACINE, "pole", "relais_reel.py"), "--port", "0",
                             "--amont", amont_url, "--plafond-usd", str(plafond), "--journal", journal,
                             "--modeles-permis", "claude-opus-5-5,claude-fable-5-1"],  # v47 (R-764, barrière 3)
                            env={"PATH": os.environ.get("PATH", ""), "ANTHROPIC_API_KEY": CLE_FACTICE},
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    ligne = proc.stdout.readline()
    if not ligne.startswith("relais prêt sur "):
        proc.kill()
        sortie, erreurs = proc.communicate(timeout=10)
        raise RuntimeError("relais non démarré : " + ligne + sortie + erreurs)
    return proc, ligne.split()[3]


def commande_pole(url_relais, sortie, generations, quand):
    """`quand` : la valeur d'horodatage (texte) passée à l'orchestrateur."""
    return [sys.executable, "-B", "-P", "-s", os.path.join(RACINE, "pole"),
            "--moteur", "claude-sdk", "--confirmer-moteur-reel", "--url-relais", url_relais,
            "--selection", "pari", "--monde-noyau", os.path.join(EXEMPLES, "monde-pari-demo-v1.json"), "--noyau-secret",
            "--population", os.path.join(EXEMPLES, "population-pari-demo-4traits-v1.json"),
            "--temoins", os.path.join(EXEMPLES, "temoins-pari-demo-4traits-v1.json"),
            "--generations", str(generations), "--budget-usd", "20", "--sortie", sortie, "--horodatage", quand,
            "--modele-experimentateur", "claude-opus-5-5", "--modele-verificateur", "claude-fable-5-1",
            "--modele-recombinaison", "claude-opus-5-5", "--modele-synthese", "claude-opus-5-5"]


def executer(dossier, generations=2, horodatage_fourni=None, plafond_relais=5.0):
    if os.path.exists(dossier) and os.listdir(dossier):
        raise FileExistsError(f"dossier non vide : {dossier} (on n'écrase jamais)")
    os.makedirs(dossier, exist_ok=True)
    quand = horodatage(horodatage_fourni)
    debut = time.time()
    amont = AmontFactice()
    journal_relais = os.path.join(dossier, "journal-relais.jsonl")
    journal_sdk = os.path.join(dossier, "journal-faux-moteur.jsonl")
    relais, url = lancer_relais(amont.url, journal_relais, plafond_relais)
    verifications, course = {}, os.path.join(dossier, "course")
    try:
        env = {"PATH": os.environ.get("PATH", ""), "PYTHONPATH": os.path.join(RACINE, "essais", "faux_sdk"),
               "FAUX_SDK_JOURNAL": journal_sdk, "FAUX_SDK_GRAINE": "20261027"}
        res = subprocess.run(commande_pole(url, course, generations, quand["valeur"]), env=env, capture_output=True, text=True,
                             timeout=1800, check=False)
        with open(os.path.join(dossier, "sortie-orchestrateur.txt"), "w", encoding="utf-8") as f:
            f.write(res.stdout + "\n--- stderr ---\n" + res.stderr)
        verifications["1_course_au_bout"] = {"code": res.returncode}
        bilan, index = {}, {}
        if os.path.exists(os.path.join(course, "bilan.json")):
            with open(os.path.join(course, "bilan.json"), encoding="utf-8") as f:
                bilan = json.load(f)
            with open(os.path.join(course, "archive", "index.json"), encoding="utf-8") as f:
                index = json.load(f)
        statuts = sorted({e["statut"] for e in index.values()})
        verifications["1_course_au_bout"].update({
            "generations_executees": bilan.get("generations_executees"), "arret": bilan.get("arret"),
            "statuts": statuts, "comptes": bilan.get("comptes_par_statut"),
            "tenu": res.returncode == 0 and bilan.get("generations_executees") == generations
            and not ({"indecise", "retiree"} & set(statuts))})
        q = bilan.get("qualite_cumulee") or {}
        verifications["2_temoins"] = {"fausses_gardees": q.get("fausses_gardees"), "vraies_eliminees": q.get("vraies_eliminees"),
                                      "temoins_faux_testes": q.get("temoins_faux_testes"),
                                      "temoins_vrais_testes": q.get("temoins_vrais_testes"),
                                      "tenu": q.get("fausses_gardees") == 0 and q.get("vraies_eliminees") == 0
                                      and (q.get("temoins_faux_testes") or 0) >= generations}
        # 3. monde du noyau
        experiences, conformes, graines = 0, 0, []
        racine_gen = os.path.join(course, "archive", "generations")
        for g in range(generations):
            chemin_g = os.path.join(course, "noyau", f"graine-noyau-generation-{g:02d}.json")
            if os.path.exists(chemin_g):
                with open(chemin_g, encoding="utf-8") as f:
                    graines.append(str(json.load(f)["graine_noyau"]))
        for racine, dossiers, noms in os.walk(racine_gen):
            if os.path.basename(racine) == "experience" and "engagement.json" in noms:
                experiences += 1
                if "mesures.json" in noms and "tirages.json" in noms:
                    with open(os.path.join(racine, "mesures.json"), encoding="utf-8") as f:
                        m = json.load(f)
                    with open(os.path.join(racine, "tirages.json"), encoding="utf-8") as f:
                        t = json.load(f)
                    conformes += m["issues"] == t.get("issues") and m["empreinte_engagement"] == t.get("empreinte_engagement")
        fuites_graine = [c for c in _fichiers(racine_gen) for s in graines if s and _contient(c, s.encode())]
        verifications["3_monde_du_noyau"] = {"experiences": experiences, "mesures_conformes": conformes,
                                             "graines_ecrites": len(graines), "fuites_de_graine": fuites_graine,
                                             "tenu": experiences > 0 and conformes == experiences
                                             and len(graines) == generations and not fuites_graine}
        # 4. relais
        entrees = _lire_jsonl(journal_relais)
        servies = [e for e in entrees if e.get("statut") == 200]
        agents = sum(1 for e in _lire_jsonl(journal_sdk) if e.get("type") == "resultat")
        verifications["4_relais"] = {"appels": len(entrees), "servis": len(servies), "agents_lances": agents,
                                     "depense_usd": entrees[-1].get("depense_cumulee_usd") if entrees else None,
                                     "cle_ajoutee_a_chaque_appel": all(r["cle"] == CLE_FACTICE for r in amont.requetes),
                                     "tenu": agents > 0 and len(servies) == len(entrees) == agents == len(amont.requetes)
                                     and all(r["cle"] == CLE_FACTICE for r in amont.requetes)}
        # 5. garde des outils
        crochets = [e for e in _lire_jsonl(journal_sdk) if e.get("type") == "crochet"]
        refus_attendus = [c for c in crochets if (c["outil"], c["entree"].get("command") or c["entree"].get("file_path")
                                                  or c["entree"].get("url")) in INTERDITS]
        permis_attendus = [c for c in crochets if (c["outil"], c["entree"].get("command") or c["entree"].get("file_path")) in PERMIS]
        verifications["5_garde_des_outils"] = {
            "appels_exerces": len(crochets), "refus": sum(c["decision"] == "deny" for c in refus_attendus),
            "refus_attendus": len(refus_attendus), "permis": sum(c["decision"] == "allow" for c in permis_attendus),
            "permis_attendus": len(permis_attendus),
            "tenu": crochets and all(c["decision"] == "deny" for c in refus_attendus)
            and all(c["decision"] == "allow" for c in permis_attendus) and len(refus_attendus) == 3 * agents}
        # 6. clé absente partout
        fuites = [c for c in _fichiers(dossier) if _contient(c, CLE_FACTICE.encode())]
        verifications["6_cle_absente"] = {"fichiers_qui_contiennent_la_cle": fuites,
                                          "tenu": not fuites and CLE_FACTICE not in res.stdout + res.stderr}
        # 7. contre-essai : clé dans l'environnement de l'orchestrateur
        avant = len(_lire_jsonl(journal_relais))
        res2 = subprocess.run(commande_pole(url, os.path.join(dossier, "contre-essai"), 1, quand["valeur"]),
                              env=dict(env, ANTHROPIC_API_KEY=CLE_FACTICE), capture_output=True, text=True, timeout=600,
                              check=False)
        verifications["7_contre_essai_cle_dans_environnement"] = {
            "code": res2.returncode, "motif": res2.stderr.strip()[-200:].replace(CLE_FACTICE, "[CAVIARDÉ]"),
            "appels_relais_en_plus": len(_lire_jsonl(journal_relais)) - avant,
            "tenu": res2.returncode == 2 and "CleDansEnvironnement" in res2.stderr
            and len(_lire_jsonl(journal_relais)) == avant and CLE_FACTICE not in res2.stdout}
    finally:
        relais.kill()
        sortie_relais, erreurs_relais = relais.communicate(timeout=10)
        amont.arreter()
    verifications["6_cle_absente"]["tenu"] = verifications["6_cle_absente"]["tenu"] and CLE_FACTICE not in sortie_relais + erreurs_relais
    rapport = {"horodatage": quand, "generations": generations, "duree_s": round(time.time() - debut, 1),
               "verifications": verifications, "tout_tenu": all(v["tenu"] for v in verifications.values()),
               "population": sha256_fichier(os.path.join(EXEMPLES, "population-pari-demo-4traits-v1.json")),
               "temoins": sha256_fichier(os.path.join(EXEMPLES, "temoins-pari-demo-4traits-v1.json"))}
    ecrire_json_scelle(os.path.join(dossier, "repetition-generale-v6.json"), rapport)
    return rapport


def principal(argv=None):
    a = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    a.add_argument("dossier")
    a.add_argument("--generations", type=int, default=2)
    a.add_argument("--horodatage")
    args = a.parse_args(argv)
    rapport = executer(args.dossier, args.generations, args.horodatage)
    print(json.dumps({k: v["tenu"] for k, v in rapport["verifications"].items()} | {"tout_tenu": rapport["tout_tenu"],
                     "duree_s": rapport["duree_s"]}, ensure_ascii=False, indent=1))
    return 0 if rapport["tout_tenu"] else 1


if __name__ == "__main__":
    sys.exit(principal())
