"""Épreuve hors ligne « W2 gradué » (v1, fichier neuf, R12) : pour une grille de doses λ, mesurer ce que le juge v9 fait **de la
loi du monde W2g(λ) elle-même** et de la **recombinaison pure** S1, S2 — 0 dollar, processeur seulement, aucun proposeur.

Pour chaque dose λ de la grille et chaque répétition r (une carte neuve : lois d'archive S1, S2 et loi neuve N tirées de la graine
« monde|W2g » de la carte r, `attaque_goodhart_v5.carte_w2g`), quatre évaluations à tirages frais :
- (a) **la loi du monde** W2g(λ), soumise par un proposeur scripté qui la connaît (borne haute de ce qu'un attaquant peut
  obtenir), sous **v9** : promue ? C'est la puissance du v9 à la frontière, à la dose λ ;
- (b) **la recombinaison pure** `attaque_goodhart_v2.monde_w2(L)` (S1 sur g = 0, S2 sur g = 1), sous **v9** : promue ? Membre du
  nul v9 : log W ≤ 0 par certificat, donc 0 promotion attendue à toute dose (vérification du code, texte § 7) ;
- (c) la recombinaison pure sous **v8** (juge des dents, « ancien ») : promue ? (le trou de W2 reste-t-il ouvert sous v8 à la dose
  λ : prédiction P10 du texte) ;
- (d) la loi du monde sous **v8** : promue ? (prix apparié de la fermeture, information).
Le juge est celui de la course (`attaque_goodhart_v5.juger`, rôle « v9 » sans appariement et rôle « ancien »), les cartes celles
de la v5 ; la même carte r sert à toutes les doses (plan apparié en λ : mêmes S1, S2, N, seule la dose change).

**Règle de choix de λ\\*** (texte § 4, brouillon 3 ; **appliquée et imprimée, jamais décidée ici** : la mère et le contre-lecteur
décident) : la plus petite dose de la grille à laquelle la loi du monde est promue par le v9 avec une fréquence ≥ 0,80 sur les
répétitions **et** la recombinaison pure n'est jamais promise sous v9 (0 promotion). Si aucune dose ne satisfait les deux, le script
l'imprime (« aucune dose de la grille »).

Sorties, dans un dossier neuf : `epreuve-w2g-dose-v1.json` (par dose : comptes, taux, Clopper-Pearson à 95 % de (a), médianes de
log W, écart de Kullback-Leibler moyen, évaluations impossibles ; règle appliquée ; manifeste : graine, répétitions, versions,
empreintes des modules) et `epreuve-w2g-dose-v1-table.txt` (la table imprimée). Scellés par `ecrire_json_scelle` / `ecrire_scelle`.
Graine : `--graine G` (entier < 2⁶⁴ : espace exploratoire ; la graine décisive, si l'épreuve est jouée sous un texte scellé, est
l'empreinte de ce texte, à passer par `--entropie-texte`). Arrêt (code 3, trace partielle) à la durée maximale ; code 2 : refus.

Usage : nice -n 10 python3 -I -B demonstrations/epreuve_w2g_dose_v1.py DOSSIER_NEUF (--graine G | --entropie-texte CHEMIN_SCELLE)
        [--repetitions 1000] [--processus 2] [--doses 0,0.05,…] [--duree-max-s 3300]
"""

import argparse
import concurrent.futures
import json
import math
import multiprocessing
import os
import platform
import sys
import time

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)

import numpy as np  # noqa: E402

from pole import attaque_goodhart_v2 as ag  # noqa: E402
from pole import attaque_goodhart_v5 as a5  # noqa: E402
from pole.outils import ecrire_json_scelle, ecrire_scelle, manifeste, sha256_fichier, verifier_scelle  # noqa: E402

VERSION = "epreuve-w2g-dose-v1"
REPETITIONS = 1000
SEUIL_PROMOTION_MONDE = 0.80  # règle de choix : (a) ≥ 0,80
PROMOTIONS_RECOMBINAISON_MAX = 0  # règle de choix : (b) = 0
DUREE_MAX_S = 3300.0  # sous le `timeout 3600` des consignes : arrêt propre (trace partielle écrite, doses complètes lues) avant le délai externe
TAILLE_LOT = 50
LIGNES = (("monde", "v9"), ("recombinaison", "v9"), ("recombinaison", "ancien"), ("monde", "v8_information"))
MODULES = ("pole/attaque_goodhart_v5.py", "pole/attaque_goodhart_v4.py", "pole/attaque_goodhart_v2.py", "pole/nul_v9.py",
           "demonstrations/banc_tricheurs_v9.py", "demonstrations/banc_tricheurs_v8.py", "demonstrations/banc_tricheurs_v7.py",
           "demonstrations/epreuve_w2g_dose_v1.py")


class ArretDuree(Exception):
    """Durée maximale dépassée : arrêt sans table complète (garde contre une boucle folle, jamais un couperet sur une mesure lue)."""


def lire_doses(texte):
    if texte is None:
        return list(a5.GRILLE_DOSES_W2G)
    doses = [a5.verifier_dose(float(x)) for x in texte.split(",") if x.strip()]
    if not doses or len(set(doses)) != len(doses) or doses != sorted(doses):
        raise ValueError(f"--doses : liste croissante de doses distinctes dans [0 ; 1], reçu {texte!r}")
    return doses


def evaluer_lot(arguments):
    """Un lot de répétitions [debut ; fin[ à une dose : rend les comptes et les log W (le juge de la course, sans appel)."""
    entropie, dose, debut, fin, depart, duree_max = arguments
    comptes = {f"{quoi}|{juge}": {"promues": 0, "impossibles": 0, "log_w": []} for quoi, juge in LIGNES}
    ecarts, grammaire_refusee = [], 0
    for r in range(debut, fin):
        if time.time() - depart > duree_max:
            raise ArretDuree(f"dose {dose} : durée maximale dépassée à la répétition {r}")
        c = a5.carte_w2g(entropie, r, dose)
        ecarts.append(c["verite"]["ecart_kl_vers_w2"])
        try:
            ag.grammaire_servie(c["monde"])  # un attaquant pourrait écrire cette loi dans la grammaire servie
        except Exception:  # noqa: BLE001
            grammaire_refusee += 1
        lois = {"monde": c["monde"], "recombinaison": ag.monde_w2(c["L"])}
        for quoi, juge in LIGNES:
            etiquette = f"epreuve-w2g|{quoi}|{juge}|dose={dose}"
            if juge == "v8_information":
                v = a5.juger(lois[quoi], c, "ancien", entropie, etiquette, 1)
            else:
                v = a5.juger(lois[quoi], c, juge, entropie, etiquette, 1, apparie=False)
            x = comptes[f"{quoi}|{juge}"]
            x["promues"] += bool(v["promue"])
            x["impossibles"] += v["statut"] == "evaluation_impossible"
            if v["log_w_max"] is not None and math.isfinite(v["log_w_max"]):
                x["log_w"].append(v["log_w_max"])
    return {"dose": dose, "debut": debut, "fin": fin, "comptes": comptes, "ecarts": ecarts, "grammaire_refusee": grammaire_refusee}


def _mediane(valeurs):
    v = sorted(valeurs)
    return round(v[len(v) // 2], 4) if v else None


def assembler(lots, repetitions):
    """Résultats par dose à partir des lots : comptes, taux, Clopper-Pearson de (a), médianes, écart moyen."""
    b = ag.banc()
    par_dose = {}
    for lot in lots:
        d = par_dose.setdefault(lot["dose"], {"dose": lot["dose"], "repetitions": 0, "ecarts": [], "grammaire_refusee": 0,
                                                "comptes": {k: {"promues": 0, "impossibles": 0, "log_w": []} for k in lot["comptes"]}})
        d["repetitions"] += lot["fin"] - lot["debut"]
        d["ecarts"] += lot["ecarts"]
        d["grammaire_refusee"] += lot["grammaire_refusee"]
        for k, x in lot["comptes"].items():
            d["comptes"][k]["promues"] += x["promues"]
            d["comptes"][k]["impossibles"] += x["impossibles"]
            d["comptes"][k]["log_w"] += x["log_w"]
    sortie = []
    for dose in sorted(par_dose):
        d = par_dose[dose]
        n = d["repetitions"]
        lignes = {}
        for k, x in d["comptes"].items():
            lignes[k] = {"promues": x["promues"], "repetitions": n, "taux": x["promues"] / n if n else None,
                         "clopper_pearson_95": list(b.clopper_pearson(x["promues"], n)) if n else None,
                         "evaluations_impossibles": x["impossibles"], "log_w_max_mediane": _mediane(x["log_w"])}
        sortie.append({"dose": dose, "repetitions": n, "complete": n == repetitions, "lignes": lignes,
                       "ecart_kl_vers_w2_moyen": round(sum(d["ecarts"]) / len(d["ecarts"]), 6) if d["ecarts"] else None,
                       "grammaire_servie_refusee": d["grammaire_refusee"]})
    return sortie


def choisir_dose(resultats, seuil=SEUIL_PROMOTION_MONDE, recombinaison_max=PROMOTIONS_RECOMBINAISON_MAX):
    """Règle du texte (§ 4) appliquée aux doses complètes : plus petite dose où taux(a) ≥ seuil et promues(b) ≤ recombinaison_max ;
    None si aucune. Imprimée, pas décidée."""
    for r in sorted(resultats, key=lambda x: x["dose"]):
        if not r["complete"]:
            continue
        a, bb = r["lignes"]["monde|v9"], r["lignes"]["recombinaison|v9"]
        if a["taux"] is not None and a["taux"] >= seuil and bb["promues"] <= recombinaison_max:
            return r["dose"]
    return None


def table(resultats, choix):
    lignes = ["dose λ | écart KL moyen | (a) monde sous v9 : promues/n, taux, CP95 | (b) recombinaison sous v9 : promues/n | "
              "(c) recombinaison sous v8 : taux | (d) monde sous v8 : taux | log W méd. (a) | éval. impossibles | complète"]
    for r in resultats:
        a, bb, c, d = (r["lignes"][k] for k in ("monde|v9", "recombinaison|v9", "recombinaison|ancien", "monde|v8_information"))
        cp = a["clopper_pearson_95"]
        imp = sum(x["evaluations_impossibles"] for x in r["lignes"].values())
        lignes.append(f"{r['dose']:.2f} | {r['ecart_kl_vers_w2_moyen']} | {a['promues']}/{a['repetitions']}, {a['taux']:.3f}, "
                      f"[{cp[0]:.3f} ; {cp[1]:.3f}] | {bb['promues']}/{bb['repetitions']} | {c['taux']:.3f} | {d['taux']:.3f} | "
                      f"{a['log_w_max_mediane']} | {imp} | {'oui' if r['complete'] else 'non'}")
    lignes.append(f"règle du texte (§ 4) appliquée — plus petite dose avec (a) ≥ {SEUIL_PROMOTION_MONDE} et (b) = {PROMOTIONS_RECOMBINAISON_MAX} : "
                  + (f"λ* = {choix}" if choix is not None else "aucune dose de la grille")
                  + " — PROPOSITION IMPRIMÉE, PAS DÉCIDÉE : la mère et le contre-lecteur décident (marqueur <<DOSE_LAMBDA>>)")
    return "\n".join(lignes)


def principal(argv=None):
    a = argparse.ArgumentParser(description="Épreuve hors ligne « W2 gradué » : puissance du v9 sur la loi du monde W2g(λ), par dose")
    a.add_argument("dossier")
    g = a.add_mutually_exclusive_group(required=True)
    g.add_argument("--graine", type=int, help="graine exploratoire (entier dans [0 ; 2⁶⁴[)")
    g.add_argument("--entropie-texte", help="texte scellé de l'épreuve : la graine est son empreinte (mode décisif)")
    a.add_argument("--repetitions", type=int, default=REPETITIONS)
    a.add_argument("--processus", type=int, default=2)
    a.add_argument("--doses", help=f"doses séparées par des virgules (défaut : grille gelée {a5.GRILLE_DOSES_W2G})")
    a.add_argument("--duree-max-s", type=float, default=DUREE_MAX_S)
    args = a.parse_args(argv)
    try:
        if os.path.exists(args.dossier) and os.listdir(args.dossier):
            raise FileExistsError(f"dossier de sortie non vide : {args.dossier} (on n'écrase jamais)")
        if args.repetitions < 1 or args.processus < 1 or not args.duree_max_s > 0:
            raise ValueError("--repetitions, --processus : entiers ≥ 1 ; --duree-max-s > 0")
        doses = lire_doses(args.doses)
        if args.graine is not None:
            entropie = ag.verifier_entropie(args.graine, decisif=False)
            mode, texte = "exploratoire (non décisif)", None
        else:
            if not os.path.isfile(args.entropie_texte) or not verifier_scelle(args.entropie_texte):
                raise ValueError(f"--entropie-texte : fichier scellé exigé (compagnon .sha256 conforme), reçu {args.entropie_texte!r}")
            empreinte = sha256_fichier(args.entropie_texte)
            entropie = ag.verifier_entropie(int(empreinte, 16), decisif=True)
            mode, texte = "décisif (graine = empreinte du texte scellé)", {"chemin": os.path.abspath(args.entropie_texte), "sha256": empreinte}
    except (FileExistsError, ValueError, ag.AttaqueRefusee) as e:
        print(f"refus : {type(e).__name__} : {e}", file=sys.stderr)
        return 2
    os.makedirs(args.dossier, exist_ok=True)
    m = manifeste(epreuve=VERSION, mode=mode, entropie_racine=str(entropie), texte=texte, repetitions=args.repetitions, processus=args.processus,
                  doses=doses, duree_max_s=args.duree_max_s, lignes=[f"{q}|{j}" for q, j in LIGNES], regle_de_choix={
                      "seuil_promotion_monde_v9": SEUIL_PROMOTION_MONDE, "promotions_recombinaison_v9_max": PROMOTIONS_RECOMBINAISON_MAX,
                      "texte": "plus petite dose de la grille avec (a) ≥ seuil et (b) ≤ max ; imprimée, pas décidée"},
                  monde_w2g=a5.description()["monde_w2g"], ecart=a5.description()["ecart_w2g"], numpy=np.__version__,
                  python=platform.python_version(), modules_sha256={r: sha256_fichier(os.path.join(RACINE, r)) for r in MODULES})
    m["regle_des_graines"] = ("SeedSequence (R9) : cartes `carte_w2g(entropie, r, dose)` (graines « monde|W2g », « developpement|W2g », "
                              "indice r) ; juge : étiquettes « epreuve-w2g|<loi>|<juge>|dose=<λ> », indices (r, 1) ; la carte r est la même à "
                              "toutes les doses (plan apparié en λ)")
    ecrire_json_scelle(os.path.join(args.dossier, "manifeste.json"), m)
    depart = time.time()
    taches = [(entropie, d, i, min(i + TAILLE_LOT, args.repetitions), depart, args.duree_max_s)
              for d in doses for i in range(0, args.repetitions, TAILLE_LOT)]
    lots, arret = [], None
    if args.processus == 1:
        for t in taches:
            try:
                lots.append(evaluer_lot(t))
            except ArretDuree as e:
                arret = str(e)
                break
    else:
        contexte = multiprocessing.get_context("fork")
        with concurrent.futures.ProcessPoolExecutor(max_workers=args.processus, mp_context=contexte) as pool:
            futurs = [pool.submit(evaluer_lot, t) for t in taches]
            for f in concurrent.futures.as_completed(futurs):
                try:
                    lots.append(f.result())
                except ArretDuree as e:
                    arret = str(e)
                    for autre in futurs:
                        autre.cancel()
                    break
    resultats = assembler(lots, args.repetitions)
    choix = choisir_dose(resultats) if arret is None else None
    t = table(resultats, choix) if resultats else "aucune dose complète"
    rapport = {"epreuve": VERSION, "mode": mode, "entropie_racine": str(entropie), "repetitions": args.repetitions, "doses": doses,
               "duree_s": round(time.time() - depart, 1), "arret": arret, "resultats": resultats,
               "regle_de_choix": m["reglages"]["regle_de_choix"], "dose_proposee_par_la_regle": choix,
               "statut_de_la_dose": "imprimée, pas décidée : la mère et le contre-lecteur décident (texte § 4, annexe B point 5)",
               "table": t}
    ecrire_json_scelle(os.path.join(args.dossier, "epreuve-w2g-dose-v1.json"), rapport)
    ecrire_scelle(os.path.join(args.dossier, "epreuve-w2g-dose-v1-table.txt"), t + "\n")
    print(t)
    print(f"durée {rapport['duree_s']} s ; sortie {os.path.join(args.dossier, 'epreuve-w2g-dose-v1.json')} "
          f"sha256 {sha256_fichier(os.path.join(args.dossier, 'epreuve-w2g-dose-v1.json'))}")
    if arret is not None:
        print(f"arrêt : {arret}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(principal())
