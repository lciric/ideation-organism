"""Répétition du duel des proposeurs (v7, version 9) : le chemin exact d'un duel payé — proposeur par l'adaptateur **réel**
(`--roles-reels proposeur`), les autres rôles simulés, relais de clé réel avec une clé factice, amont factice, faux moteur —
**sans appel de modèle, sans vraie clé, sans dépense**. Monde : un monde de la grammaire v2 (`exemples/generer_monde_grammaire_v2.py`),
phase exploratoire ouverte, témoins jugés sans agents.

Ce qu'elle vérifie (écrit dans `repetition-duel-v7.json`, scellé) :
1. la course va au bout (code 0, générations demandées, aucune erreur de l'orchestrateur) ;
2. **seul le proposeur passe par le relais** : appels du relais = sessions de proposeur du faux moteur = générations − 1 ;
   aucun autre rôle n'appelle le relais ;
3. le proposeur a reçu la partie de développement (`developpement.json` dans son dossier, distincte du calibrage) et
   jamais une issue d'épreuve ;
4. le manifeste porte l'adaptateur « mixte » ;
5. la clé factice n'apparaît nulle part.

Usage : python -I -B demonstrations/repetition_duel_v7.py DOSSIER_NEUF [--generations 3]
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
sys.path.insert(0, os.path.join(RACINE, "exemples"))
sys.path.insert(0, ICI)

from essais.faux_sdk.amont_factice import CLE_FACTICE, AmontFactice  # noqa: E402
from generer_monde_grammaire_v1 import fiches_de_temoins  # noqa: E402
import generer_monde_grammaire_v2 as g2  # noqa: E402
from pole.monde_banque import MondeBanque  # noqa: E402
from pole.outils import ecrire_json_scelle  # noqa: E402
from pole.proposeur import valider_proposition  # noqa: E402
from pole.proposeurs_references import propositions_aleatoires  # noqa: E402
from repetition_generale_v6 import _contient, _fichiers, _lire_jsonl, lancer_relais  # noqa: E402

GRAINE = 20261201


def preparer(dossier):
    banque, temoins, _ = g2.generer_monde(GRAINE, structures=["trois_traits", "seuil_decale", "trois_traits"])
    chemin_banque = os.path.join(dossier, "monde", "banque.json")
    ecrire_json_scelle(chemin_banque, banque)
    monde = MondeBanque(chemin_banque, GRAINE)
    population = [valider_proposition(p, monde, 0.05, f"P{i:02d}", "reference-aleatoire", references=True)
                  for i, p in enumerate(propositions_aleatoires(monde.description_publique(), 4, GRAINE, 0), 1)]
    chemin_pop = os.path.join(dossier, "monde", "population.json")
    chemin_tem = os.path.join(dossier, "monde", "temoins.json")
    ecrire_json_scelle(chemin_pop, [f.vers_dict() for f in population])
    ecrire_json_scelle(chemin_tem, [f.vers_dict() for f in fiches_de_temoins(temoins, 4, 3)])
    return chemin_banque, chemin_pop, chemin_tem, banque


def commande(url, sortie, generations, chemins):
    banque, pop, tem = chemins
    return [sys.executable, "-B", "-P", "-s", os.path.join(RACINE, "pole"),
            "--moteur", "claude-sdk", "--confirmer-moteur-reel", "--url-relais", url, "--roles-reels", "proposeur",
            "--selection", "pari", "--monde-banque", banque, "--sans-urne", "--temoins-sans-agent",
            "--temoins-par-generation", "3", "--population", pop, "--temoins", tem, "--generations", str(generations),
            "--budget-usd", "50", "--propositions-par-generation", "6", "--proposeur", "agent",
            "--modele-proposeur", "claude-opus-5-5", "--exploration-developpement", "--sortie", sortie,
            "--horodatage", "répétition du duel", "--tranches", str(generations)]  # v11 : une tranche par génération


def executer(dossier, generations=3):
    if os.path.exists(dossier) and os.listdir(dossier):
        raise FileExistsError(dossier)
    os.makedirs(dossier, exist_ok=True)
    debut = time.time()
    chemin_banque, chemin_pop, chemin_tem, banque = preparer(dossier)
    amont = AmontFactice()
    journal_relais = os.path.join(dossier, "journal-relais.jsonl")
    journal_sdk = os.path.join(dossier, "journal-faux-moteur.jsonl")
    relais, url = lancer_relais(amont.url, journal_relais, 5.0)
    verifications, course = {}, os.path.join(dossier, "course")
    try:
        env = {"PATH": os.environ.get("PATH", ""), "PYTHONPATH": os.path.join(RACINE, "essais", "faux_sdk"),
               "FAUX_SDK_JOURNAL": journal_sdk, "FAUX_SDK_GRAINE": "20261027"}
        res = subprocess.run(commande(url, course, generations, (chemin_banque, chemin_pop, chemin_tem)), env=env,
                             capture_output=True, text=True, timeout=1800, check=False)
        with open(os.path.join(dossier, "sortie-orchestrateur.txt"), "w", encoding="utf-8") as f:
            f.write(res.stdout + "\n--- stderr ---\n" + res.stderr)
        bilan, manifeste, erreurs = {}, {}, []
        if os.path.exists(os.path.join(course, "bilan.json")):
            with open(os.path.join(course, "bilan.json"), encoding="utf-8") as f:
                bilan = json.load(f)
            with open(os.path.join(course, "manifeste.json"), encoding="utf-8") as f:
                manifeste = json.load(f)
            for g in range(bilan.get("generations_executees") or 0):
                with open(os.path.join(course, "journal", f"generation-{g:02d}.json"), encoding="utf-8") as f:
                    erreurs += (json.load(f).get("erreurs_orchestrateur") or {}).get("fiches", [])
        verifications["1_course_au_bout"] = {"code": res.returncode, "generations": bilan.get("generations_executees"),
                                             "erreurs_orchestrateur": erreurs,
                                             "tenu": res.returncode == 0 and bilan.get("generations_executees") == generations
                                             and not erreurs}
        resultats = [e for e in _lire_jsonl(journal_sdk) if e.get("type") == "resultat"]
        roles = sorted({e.get("role") for e in resultats})
        entrees = _lire_jsonl(journal_relais)
        verifications["2_seul_le_proposeur_au_relais"] = {
            "sessions_du_faux_moteur": len(resultats), "roles": roles, "appels_relais": len(entrees),
            "tenu": roles == ["proposeur"] and len(resultats) == generations - 1 and len(entrees) == len(resultats)}
        dev_ok, fuite = True, []
        epreuve = {json.dumps(l["issues"], sort_keys=True) + json.dumps(l["z"]) for l in banque["instances"] if l["partie"] == "epreuve"}
        for g in range(generations - 1):
            chemin = os.path.join(course, "archive", "generations", f"generation-{g:02d}", "proposeur", "developpement.json")
            if not os.path.exists(chemin):
                dev_ok = False
                continue
            with open(chemin, encoding="utf-8") as f:
                dev = json.load(f)
            dev_ok = dev_ok and dev.get("partie") == "developpement" and not dev.get("meme_partie_que_le_connu")
            fuite += [l["identifiant"] for l in dev["instances"]
                      if json.dumps(l["issues"], sort_keys=True) + json.dumps(l["z"]) in epreuve]
        verifications["3_developpement_seul"] = {"developpement_distinct": dev_ok, "instances_d_epreuve_servies": fuite,
                                                 "tenu": dev_ok and not fuite}
        adaptateur = (manifeste.get("reglages") or {}).get("adaptateur")
        verifications["4_adaptateur_mixte"] = {"adaptateur": adaptateur, "tenu": adaptateur == "mixte"}
        fuites = [c for c in _fichiers(dossier) if _contient(c, CLE_FACTICE.encode())]
        verifications["5_cle_absente"] = {"fichiers": fuites, "tenu": not fuites and CLE_FACTICE not in res.stdout + res.stderr}
    finally:
        relais.kill()
        relais.communicate(timeout=10)
        amont.arreter()
    rapport = {"generations": generations, "duree_s": round(time.time() - debut, 1), "verifications": verifications,
               "tout_tenu": all(v["tenu"] for v in verifications.values())}
    ecrire_json_scelle(os.path.join(dossier, "repetition-duel-v7.json"), rapport)
    return rapport


def principal(argv=None):
    a = argparse.ArgumentParser()
    a.add_argument("dossier")
    a.add_argument("--generations", type=int, default=3)
    args = a.parse_args(argv)
    rapport = executer(args.dossier, args.generations)
    print(json.dumps({k: v["tenu"] for k, v in rapport["verifications"].items()} | {"tout_tenu": rapport["tout_tenu"],
                     "duree_s": rapport["duree_s"]}, ensure_ascii=False, indent=1))
    return 0 if rapport["tout_tenu"] else 1


if __name__ == "__main__":
    sys.exit(principal())
