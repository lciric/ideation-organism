"""Validation des juges d'idéation v2 : lanceur (fichier neuf, R12). Cœur : `pole/juges_idees_v2.py`.

Joue l'ancien protocole (`juges_croises_v53` : une fiche par appel, « notable » = tous les items vrais) et le protocole v2
(comparaisons par paires à l'aveugle, ancres, budget, preuve citée, règle de famille) **sur les mêmes fiches** : trois lots de
témoins plantés (décisifs ; 15 bons et 15 mauvais témoins d'évaluation), le bras « ancien protocole sans dossier » et, s'il est
fourni, le lot réel du second tour (lu descriptivement). Les étapes, leur ordre et la structure des phases sont fixés par le code
(`juges_idees_v2.etapes_v2`) ; le texte scellé les cite.

Trois modes, exclusifs :
- **à blanc** (`--a-blanc --graine G`, G dans [0 ; 2⁶⁴[) : juges scriptés (`AdaptateurScripte`), relais scripté en panne si
  demandé (`--panne-a`, `--panne-b` : « genre:début-fin,… »), horloge virtuelle (aucune attente réelle), aucun réseau, aucune
  clé ; exploratoire, ne décide rien ; lot réel de substitution (fiches factices) sauf `--sans-lot-reel` ;
- **puissance** (`--puissance`) : calculs cités par le préenregistrement (loi exacte de Mann et Whitney et modèle binormal ;
  test binomial exact du critère D6 ; plan joué par des juges scriptés « bruite » à plusieurs exactitudes) ; imprime un JSON ;
- **réel** (`--preenregistrement P --configuration CONF --moteur reel --confirmer-moteur-reel --registre-go R --go ID`) :
  chaque juge du bloc `plan-gele` par son relais de la configuration (`demonstrations/ideation_v8.adaptateurs_reels_v56`) ;
  le plan est lu dans le texte scellé, jamais en ligne de commande ; entropie des graines = empreinte SHA-256 du texte scellé.

Gardes avant tout appel et toute écriture dans la sortie (code 2) : dossier de sortie non vide ; en mode réel, texte autre que
`prereg/preenregistrement-juges-idees-v2-v<N>.md` dans le dossier `prereg/` (un brouillon est refusé), non scellé, portant un
marqueur `<<…>>` ou « À REMPLIR », sans bloc `empreintes-du-code` couvrant exactement `FICHIERS_GELES` ou dont une empreinte diffère du fichier
présent, sans bloc `plan-gele` conforme (clés exactes, valeurs fixes égales au code, consigne v2 à l'empreinte du code, plafond
au plus 60 USD, parts positives dans le plafond, durée maximale positive, juges d'étiquettes, de familles et de relais
distincts) ; option de plan ou graine en ligne de commande ; configuration d'une autre empreinte que celle du plan ; GO autre
que celui du plan, absent, d'un autre montant que le plafond, d'un autre type, hors validité ou révoqué ; variable de clé dans
l'environnement ; budget par appel (`plafonds_session.juge`) sous deux fois le prix de plan le plus haut ; matériaux d'une
autre empreinte, vérité connue non établie, forme favorable aux bons témoins ou classement possible sans les tables (contrôle
de diagnosticité) ; pièce de la configuration absente ou altérée ; lot réel qui ne passe pas la garde A4 de la configuration ;
relais d'un juge absent ; dépense requise (phases décisives et bras sans dossier, au prix du plan) au-dessus de la part d'un
juge ou du plafond ; durée haute au-dessus de la durée maximale ; porte de plafond qui n'accuse pas la part du juge.
`--verifier-seulement` (mode réel) : toutes ces gardes, adaptateurs construits et plafonds accusés, aucun appel, aucune écriture
dans la sortie.
Codes : 0 course allée à son terme (étapes jouées, ou non jouées selon les règles écrites d'avance ; le code ne décide rien :
seule la lecture gelée décide) ; 2 refus ; 3 arrêt de la course (plafond, durée, modèle servi, phase décisive de A interrompue,
pertes du relais, étiquette interdite) : journal partiel, mesures et lecture « partielle » scellés.

Usage à blanc : python3 -I -B demonstrations/validation_juges_idees_v2.py SORTIE_NEUVE --a-blanc --graine 7
                [--strategie-a indulgent] [--strategie-b parfait] [--panne-b relais_plancher:1-] [--sans-lot-reel]
"""

import argparse
import datetime
import importlib.util
import json
import os
import platform
import re
import signal
import subprocess
import sys
import tempfile
import time

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)

import numpy as np  # noqa: E402

from pole import juges_idees_v2 as J  # noqa: E402
from pole.graines_v53 import Graines  # noqa: E402
from pole.outils import ecrire_json_scelle, sha256_fichier, verifier_scelle  # noqa: E402

VERSION = "lanceur-validation-juges-idees-v2 (brouillon 3)"
ETAPE = "juges_idees_v2"
DOSSIER_PREREG = os.path.join(RACINE, "prereg")
NOM_PREREG = re.compile(r"^preenregistrement-juges-idees-v2-v[1-9][0-9]*\.md$")
DEBUT_EMPREINTES, FIN_EMPREINTES = "<!-- empreintes-du-code : début -->", "<!-- empreintes-du-code : fin -->"
DEBUT_PLAN, FIN_PLAN = "<!-- plan-gele : début -->", "<!-- plan-gele : fin -->"
MARQUEUR = re.compile(r"<<[A-Z0-9_]+>>|À REMPLIR")  # brouillon 3 : le seul marqueur du texte est « À REMPLIR » (commit cité)
SHA = re.compile(r"^[0-9a-f]{64}$")
PLAFOND_MAX_USD = 60.0  # GO-2026-11-02-32 : le plafond du texte scellé doit être exactement 60 USD (le GO exige le montant exact)
FACTEUR_BUDGET_APPEL = 2.0  # `plafonds_session.juge` ≥ 2 × le prix de plan le plus haut (un appel deux fois plus cher passe)
REGISTRE_COURSE = "registre-depense-cumulee-v1.jsonl"
SORTIES = {"manifeste": "manifeste.json", "materiaux": "materiaux-temoins-juges-idees-v2.json", "plan": "plan-des-appels.json",
           "journal": "journal-juges-idees-v2.json", "mesures": "mesures-juges-idees-v2.json",
           "lecture": "lecture-juges-idees-v2.json", "fil": "journal-au-fil-juges-idees-v2.jsonl"}
# Règle écrite d'avance pour une course tuée (brouillon 3, contre-lecture v2, I8) : le journal au fil de l'eau (une ligne JSON vidée
# sur disque par réponse, perte, attente, étape, projection) est la seule trace ; issue I0 « infrastructure » ; dépense relue au
# registre des commandes de la sortie ; aucune relance sans GO de Lazar.
REGLE_COURSE_TUEE = ("course tuée (processus arrêté sans journal scellé) : issue I0 « infrastructure » ; le journal au fil de l'eau "
                     f"({SORTIES['fil']}) est la seule trace, scellé par le lecteur tel qu'il est ; dépense relue au registre des "
                     "commandes de la sortie ; aucune relance sans GO de Lazar")
# Fermeture des imports du chemin réel (essai `Fermeture` de `essais/test_juges_idees_v2.py`) : le texte scellé gèle
# l'empreinte de chacun, le lanceur refuse tout écart.
FICHIERS_GELES = (
    "demonstrations/ideation_v2.py", "demonstrations/ideation_v4.py", "demonstrations/ideation_v5.py", "demonstrations/ideation_v6.py",
    "demonstrations/ideation_v7.py", "demonstrations/ideation_v8.py", "demonstrations/validation_juges_idees_v2.py",
    "pole/__init__.py", "pole/adaptateur_kimi_v53.py", "pole/adaptateurs.py", "pole/adaptateurs_v56.py", "pole/aiguilleur_v53.py",
    "pole/bisociateur_v53.py", "pole/bisociateur_v54.py", "pole/bisociateur_v55.py", "pole/budget_v53.py", "pole/budget_v54.py",
    "pole/budget_v56.py", "pole/caviardage.py", "pole/coffre_v53.py", "pole/coffre_v55.py", "pole/configuration_v53.py",
    "pole/configuration_v54.py", "pole/configuration_v55.py", "pole/configuration_v56.py", "pole/course2_v53.py",
    "pole/course2_v54.py", "pole/course2_v55.py", "pole/course2_v56.py", "pole/dossier_ferme.py",
    "pole/etage_entre_generations_v53.py", "pole/etage_entre_generations_v54.py", "pole/etage_entre_generations_v55.py",
    "pole/etage_entre_generations_v56.py", "pole/fiches_v53.py", "pole/fiches_v54.py", "pole/garde_outils.py",
    "pole/gardes_e0_v54.py", "pole/gardes_e0_v55.py", "pole/gardes_e0_v56.py", "pole/graines_v53.py", "pole/ideation_v2.py",
    "pole/juges_croises_v53.py", "pole/juges_idees_v2.py", "pole/memoire_v53.py", "pole/mesures_v54.py", "pole/moisson.py",
    "pole/noyau_v54.py", "pole/noyau_v55.py", "pole/noyau_v56.py", "pole/outils.py", "pole/pari_apparie.py",
    "pole/prepilote_v54.py", "pole/prepilote_v55.py", "pole/prepilote_v56.py", "pole/protocole_outils.py", "pole/relais.py",
    "pole/relais_reel.py", "pole/suivi_roles_v54.py", "pole/tableau_v53.py", "pole/tests_de_mort_v2.py",
    "pole/tests_de_mort_v3.py")
# Juges du plan (prix de plan : Argon 0,062 USD mesuré le 2 novembre ; Astra **non mesuré**, borne prudente 0,50 USD, deux fois le
# taux de devis d'A1-bis ; secondes : bornes de plan, Astra non mesuré)
JUGES_A_BLANC = {"juge_a": {"etiquette": "juge-a", "fournisseur": "argon", "modele": "gemini-4-argon", "famille": "gemini",
                            "prix_usd": 0.062, "secondes": (8.0, 40.0)},
                 "juge_b": {"etiquette": "juge-b", "fournisseur": "astra", "modele": "gpt-6-astra", "famille": "gpt",
                            "prix_usd": 0.5, "secondes": (10.0, 120.0)}}
CORRESPONDANCE_A_BLANC = {"kimi": "kimi", "argon": "gemini"}
OPTIONS_A_BLANC = ("strategie_a", "strategie_b", "sans_lot_reel", "cout_a", "cout_b", "plafond_usd", "duree_max_h", "panne_a",
                   "panne_b", "p_juste_a", "p_juste_b", "biais_a", "biais_b")
JUGE = re.compile(r"^etiquette=([a-z][a-z0-9-]{0,30}), fournisseur=([a-z][a-z0-9]{0,15}), modele=(\S+), famille=([a-z][a-z0-9]{0,15}), "
                  r"prix_usd=(\d+(?:\.\d+)?), secondes=(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)$")


class PreenregistrementRefuse(J.ProtocoleRefuse):
    """Mode réel : texte autre que le fichier fixé, non scellé, à marqueur restant, sans code gelé conforme ou sans plan."""


def seuils_texte():
    return ", ".join(f"{k}={v}" for k, v in J.SEUILS_LECTURE_V2.items())


PLAN_FIXE = {"version_plan": J.VERSION_PLAN, "jeu_de_mondes": J.JEU_DU_TEXTE, "temoins_par_classe": str(J.TEMOINS_PAR_CLASSE),
             "degre": str(J.DEGRE), "tirages_a": str(len(J.TIRAGES_A)), "degre_reel": str(J.DEGRE_REEL),
             "paires_b_max_par_lot": str(J.PAIRES_B_MAX_PAR_LOT), "part_budget": repr(J.PART_BUDGET),
             "ridge_forces": repr(J.RIDGE_FORCES), "ridge_position": repr(J.RIDGE_POSITION), "seuils": seuils_texte(),
             "politique_relais": J.politique_relais()}
CLES_PLAN = {"juge_a", "juge_b", "correspondance_auteurs", "graine_materiaux", "materiaux_sha256", "consigne_paire_sha256",
             "piece_consigne_ancienne", "piece_question", "piece_lot_reel", "plafond_usd", "plafond_juge_a_usd",
             "plafond_juge_b_usd", "duree_max_h", "configuration_sha256", "go"} | set(PLAN_FIXE)


# --- préenregistrement ------------------------------------------------------------------------------------------------------
def _bloc(texte, debut, fin, nom):
    i, j = texte.find(debut), texte.find(fin)
    if i < 0 or j < i:
        raise PreenregistrementRefuse(f"bloc « {nom} » absent du préenregistrement")
    return texte[i + len(debut):j]


def _nombre(texte, nom):
    try:
        v = float(texte.replace(",", "."))
    except ValueError:
        raise PreenregistrementRefuse(f"plan-gele : {nom} numérique, reçu {texte!r}") from None
    if not np.isfinite(v):
        raise PreenregistrementRefuse(f"plan-gele : {nom} fini exigé")
    return v


def lire_juge(valeur, nom):
    m = JUGE.match(valeur.strip())
    if not m:
        raise PreenregistrementRefuse(f"plan-gele : {nom} : « etiquette=…, fournisseur=…, modele=…, famille=…, prix_usd=…, "
                                      f"secondes=BAS-HAUT » attendu, reçu {valeur!r}")
    bas, haut = float(m.group(6)), float(m.group(7))
    if not 0 < bas <= haut:
        raise PreenregistrementRefuse(f"plan-gele : {nom} : secondes 0 < BAS ≤ HAUT")
    if not float(m.group(5)) > 0:
        raise PreenregistrementRefuse(f"plan-gele : {nom} : prix_usd > 0")
    return {"etiquette": m.group(1), "fournisseur": m.group(2), "modele": m.group(3), "famille": m.group(4),
            "prix_usd": float(m.group(5)), "secondes": (bas, haut)}


def lire_correspondance(valeur):
    sortie = {}
    for morceau in [x.strip() for x in valeur.split(",") if x.strip()]:
        m = re.fullmatch(r"([a-z][a-z0-9]{0,15})=([a-z][a-z0-9]{0,15})", morceau)
        if not m or m.group(1) in sortie:
            raise PreenregistrementRefuse(f"plan-gele : correspondance_auteurs : « fournisseur=famille, … », reçu {morceau!r}")
        sortie[m.group(1)] = m.group(2)
    if not sortie:
        raise PreenregistrementRefuse("plan-gele : correspondance_auteurs vide")
    return sortie


def lire_plan(texte):
    """Bloc `plan-gele` : lignes « clé: valeur » ; rend le plan (dict) ou lève `PreenregistrementRefuse`."""
    lignes = {}
    for l in _bloc(texte, DEBUT_PLAN, FIN_PLAN, "plan-gele").splitlines():
        m = re.match(r"^\s*([a-z0-9_]+)\s*:\s*(.+?)\s*$", l)
        if m:
            if m.group(1) in lignes:
                raise PreenregistrementRefuse(f"plan-gele : clé {m.group(1)!r} en double")
            lignes[m.group(1)] = m.group(2)
    if set(lignes) != CLES_PLAN:
        raise PreenregistrementRefuse(f"plan-gele : clés attendues {sorted(CLES_PLAN)}, manquantes {sorted(CLES_PLAN - set(lignes))}, "
                                      f"en trop {sorted(set(lignes) - CLES_PLAN)}")
    for k, v in PLAN_FIXE.items():
        if lignes[k] != v:
            raise PreenregistrementRefuse(f"plan-gele : {k} = {lignes[k]!r}, le code gelé dit {v!r}")
    a, b = lire_juge(lignes["juge_a"], "juge_a"), lire_juge(lignes["juge_b"], "juge_b")
    if a["etiquette"] == b["etiquette"] or a["famille"] == b["famille"] or a["fournisseur"] == b["fournisseur"]:
        raise PreenregistrementRefuse("plan-gele : juges A et B d'étiquettes, de familles et de relais distincts exigés")
    for j in (a, b):
        if j["famille"] == J.FAMILLE_AUTEUR_TEMOINS:
            raise PreenregistrementRefuse(f"plan-gele : juge {j['etiquette']} de la famille de l'auteur des gabarits des témoins")
    if not re.fullmatch(r"\d+", lignes["graine_materiaux"]):
        raise PreenregistrementRefuse("plan-gele : graine_materiaux entière")
    for k in ("materiaux_sha256", "consigne_paire_sha256", "configuration_sha256"):
        if not SHA.match(lignes[k]):
            raise PreenregistrementRefuse(f"plan-gele : {k} = 64 caractères hexadécimaux")
    if lignes["consigne_paire_sha256"] != J.EMPREINTE_CONSIGNE_PAIRE_V2:
        raise PreenregistrementRefuse("plan-gele : consigne_paire_sha256 ≠ empreinte de la consigne v2 du code gelé")
    if not re.fullmatch(r"GO-\d{4}-\d{2}-\d{2}-\d{2}", lignes["go"]):
        raise PreenregistrementRefuse("plan-gele : go = GO-AAAA-MM-JJ-NN")
    plafond, pa, pb = (_nombre(lignes[k], k) for k in ("plafond_usd", "plafond_juge_a_usd", "plafond_juge_b_usd"))
    duree = _nombre(lignes["duree_max_h"], "duree_max_h")
    if not 0 < plafond <= PLAFOND_MAX_USD:
        raise PreenregistrementRefuse(f"plan-gele : plafond {plafond} USD hors de ]0 ; {PLAFOND_MAX_USD:g}] (GO-2026-11-02-32)")
    if not (pa > 0 and pb > 0 and pa + pb <= plafond + 1e-9):
        raise PreenregistrementRefuse(f"plan-gele : parts des juges ({pa} + {pb} USD) positives et dans le plafond ({plafond} USD)")
    if not duree > 0:
        raise PreenregistrementRefuse("plan-gele : duree_max_h > 0 (garde contre une boucle folle)")
    for k in ("piece_consigne_ancienne", "piece_question", "piece_lot_reel"):
        if not re.fullmatch(r"[a-z0-9_]{1,64}", lignes[k]):
            raise PreenregistrementRefuse(f"plan-gele : {k} = nom de pièce de la configuration (ou « aucune » pour le lot réel)")
    return {"juge_a": a, "juge_b": b, "correspondance": lire_correspondance(lignes["correspondance_auteurs"]),
            "graine_materiaux": int(lignes["graine_materiaux"]), "materiaux_sha256": lignes["materiaux_sha256"],
            "piece_consigne_ancienne": lignes["piece_consigne_ancienne"], "piece_question": lignes["piece_question"],
            "piece_lot_reel": lignes["piece_lot_reel"], "plafond_usd": plafond, "plafond_juge_a_usd": pa, "plafond_juge_b_usd": pb,
            "duree_max_s": duree * 3600.0, "configuration_sha256": lignes["configuration_sha256"], "go": lignes["go"]}


def lire_preenregistrement(chemin):
    """Mode réel : le texte au chemin fixé, scellé, sans marqueur, gelant exactement le code présent ; rend (entropie,
    empreinte, empreintes gelées, plan)."""
    reel, dossier = os.path.realpath(chemin), os.path.realpath(DOSSIER_PREREG)
    if os.path.dirname(reel) != dossier or not NOM_PREREG.match(os.path.basename(reel)):
        raise PreenregistrementRefuse(f"mode réel : le préenregistrement est prereg/preenregistrement-juges-idees-v2-v<N>.md, pas "
                                      f"{chemin} (un brouillon ne lance rien ; la graine est l'empreinte de ce fichier-là)")
    if not os.path.isfile(reel):
        raise PreenregistrementRefuse(f"préenregistrement introuvable : {chemin}")
    if not verifier_scelle(reel):
        raise PreenregistrementRefuse(f"préenregistrement non scellé (compagnon .sha256 absent ou non conforme) : {chemin}")
    with open(reel, encoding="utf-8") as f:
        texte = f.read()
    restants = sorted(set(MARQUEUR.findall(texte)))
    if restants:
        raise PreenregistrementRefuse(f"marqueur(s) non rempli(s) : {restants} (à remplir avant le scellement)")
    gelees = re.findall(r"^([0-9a-f]{64})  (\S+)$", _bloc(texte, DEBUT_EMPREINTES, FIN_EMPREINTES, "empreintes-du-code"), re.M)
    noms = [r for _, r in gelees]
    if sorted(noms) != sorted(FICHIERS_GELES) or len(set(noms)) != len(noms):
        raise PreenregistrementRefuse(f"code gelé ≠ fermeture du chemin réel : manquants {sorted(set(FICHIERS_GELES) - set(noms))}, "
                                      f"en trop {sorted(set(noms) - set(FICHIERS_GELES))}")
    ecarts = []
    for attendue, relatif in gelees:
        p = os.path.join(RACINE, relatif)
        presente = sha256_fichier(p) if os.path.isfile(p) else "absent"
        if presente != attendue:
            ecarts.append(f"{relatif} : gelé {attendue[:12]}…, présent {presente[:12]}…")
    if ecarts:
        raise PreenregistrementRefuse("code différent du code gelé : " + " ; ".join(ecarts))
    plan = lire_plan(texte)
    empreinte = sha256_fichier(reel)
    return int(empreinte, 16), empreinte, dict((r, h) for h, r in gelees), plan


def verifier_go(registre, go, plan, cfg):
    """Le GO nommé par le texte scellé, sur une ligne entière du registre (`configuration_v56.verifier_go_v56` : identifiant
    exact, type calcul, accordé par Lazar, en cours de validité, non révoqué, montant égal au plafond)."""
    if not registre or not go:
        raise J.ProtocoleRefuse("mode réel : --registre-go et --go exigés (GO de Lazar sur devis)")
    if go != plan["go"]:
        raise J.ProtocoleRefuse(f"GO {go} : le texte scellé nomme {plan['go']} (aucun autre GO)")
    try:
        return cfg.verifier_go_v56(go, registre, plan["plafond_usd"])
    except cfg.GoRefuse as e:
        raise J.ProtocoleRefuse(str(e)) from None


# --- chemin réel ------------------------------------------------------------------------------------------------------------
_V8 = {}


def charger_ideation_v8():
    if "m" not in _V8:
        spec = importlib.util.spec_from_file_location("ideation_v8_pour_juges_idees_v2", os.path.join(ICI, "ideation_v8.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)  # instance propre (R12)
        _V8["m"] = m
    return _V8["m"]


def substituer_commandes(conf, registre, plafond_usd):
    """Copie de la configuration où, dans chaque commande externe, le jeton `{REGISTRE}` devient `registre` et la valeur de
    `--plafond-cumule-usd` devient le plafond de la course (même mécanisme que le lanceur de l'attaque de Goodhart v2) ; rend
    (copie, substitutions faites). La configuration lue (et son empreinte) reste celle du fichier."""
    copie = json.loads(json.dumps(conf))
    faites = []
    for nom, f in sorted((copie.get("fournisseurs") or {}).items()):
        c = f.get("commande") if isinstance(f, dict) and f.get("type") == "commande_externe" else None
        if not isinstance(c, list):
            continue
        for i, x in enumerate(c):
            if isinstance(x, str) and "{REGISTRE}" in x:
                c[i] = x.replace("{REGISTRE}", registre)
                faites.append({"fournisseur": nom, "argument": i, "avant": x, "apres": c[i]})
            if x == "--plafond-cumule-usd" and i + 1 < len(c):
                avant, c[i + 1] = c[i + 1], f"{plafond_usd:g}"
                faites.append({"fournisseur": nom, "argument": i + 1, "avant": avant, "apres": c[i + 1]})
    return copie, faites


def etape_du_juge(etiquette):
    """Étape de dépense propre à un juge (`juges_idees_v2/<étiquette>`), transmise à sa porte de plafond avec sa part."""
    return f"{ETAPE}/{etiquette}"


def budget_par_appel(conf, plan):
    """`plafonds_session.juge` (budget par appel, aucun défaut) : au moins `FACTEUR_BUDGET_APPEL` fois le prix de plan le plus
    haut des deux juges (un appel deux fois plus cher que prévu passe sans dépassement de session)."""
    b = (conf.get("plafonds_session") or {}).get("juge")
    if isinstance(b, bool) or not isinstance(b, (int, float)) or not b > 0:
        raise J.ProtocoleRefuse("configuration : plafonds_session.juge exigé (budget par appel, réel > 0, aucun défaut)")
    minimum = FACTEUR_BUDGET_APPEL * max(plan["juge_a"]["prix_usd"], plan["juge_b"]["prix_usd"])
    if b + 1e-12 < minimum:
        raise J.ProtocoleRefuse(f"configuration : plafonds_session.juge = {b:g} USD < {minimum:g} USD ({FACTEUR_BUDGET_APPEL:g} fois "
                                "le prix de plan le plus haut) : un appel plus cher que prévu dépasserait sa session")
    return float(b)


def juges_reels(conf, plan, base_sessions, sortie):
    """Adaptateurs du chemin réel et plafonds accusés par juge ; rend (adaptateurs, accusés, informations du manifeste)."""
    from pole.relais import noms_de_cle_presents
    presents = noms_de_cle_presents(os.environ)
    if presents:
        raise J.ProtocoleRefuse(f"variables de clé dans l'environnement de l'orchestrateur ({', '.join(presents)}) : les relais "
                                "tiennent les clés")
    b = budget_par_appel(conf, plan)
    conf, substitutions = substituer_commandes(conf, os.path.join(os.path.abspath(sortie), REGISTRE_COURSE), plan["plafond_usd"])
    adaptateurs, portes = charger_ideation_v8().adaptateurs_reels_v56(conf, sortie, base_sessions)
    accuses, permis = {}, {}
    for cle in ("juge_a", "juge_b"):
        j = plan[cle]
        if j["fournisseur"] not in adaptateurs:
            raise J.ProtocoleRefuse(f"configuration : relais « {j['fournisseur']} » du {cle} absent (trouvés {sorted(adaptateurs)})")
        if j["fournisseur"] not in portes:  # contre-lecture v2, M15 : refus nommé, jamais une erreur brute
            raise J.ProtocoleRefuse(f"configuration : porte de plafond absente pour « {j['fournisseur']} » ({cle})")
        part = plan[f"plafond_{cle}_usd"]
        accuses[j["etiquette"]] = portes[j["fournisseur"]].transmettre(etape_du_juge(j["etiquette"]), part)
        # brouillon 3 (contre-lecture v2, I7) : identifiants servis que l'adaptateur admet (liste explicite de la configuration,
        # `modeles_servis_permis`), repris tels quels par le contrôle A2 du cœur (`classer_resultat`)
        liste = (getattr(adaptateurs[j["fournisseur"]], "modeles_servis_permis", None) or {}).get(j["modele"], ())
        permis[j["etiquette"]] = [x for x in liste if isinstance(x, str) and x]
    infos = {"budget_appel_usd": b, "substitutions_dans_les_commandes": substitutions, "modeles_servis_permis": permis,
             "adaptateurs": {n: (a.description() if hasattr(a, "description") else type(a).__name__) for n, a in adaptateurs.items()},
             "portes": {n: p.description() for n, p in portes.items()}}
    return adaptateurs, accuses, infos


def commit():
    try:
        r = subprocess.run(["git", "-C", RACINE, "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10)
        etat = subprocess.run(["git", "-C", RACINE, "status", "--porcelain"], capture_output=True, text=True, timeout=30)
        return {"commit": r.stdout.strip() or "inconnu", "arbre_modifie": bool(etat.stdout.strip())}
    except (OSError, subprocess.SubprocessError):
        return {"commit": "inconnu (hors dépôt git)", "arbre_modifie": None}


# --- préparation commune -------------------------------------------------------------------------------------------------------
def verifier_devis(etapes, plan):
    """Dépense **requise** (phases décisives et bras sans dossier, au prix du plan) de chaque juge dans sa part, total dans le
    plafond ; durée haute (toutes les étapes) dans la durée maximale. Les phases descriptives (lot réel) sont conditionnelles :
    jouées seulement si leur projection tient au moment de les jouer."""
    juges = {plan["juge_a"]["etiquette"]: plan["juge_a"], plan["juge_b"]["etiquette"]: plan["juge_b"]}
    d = J.devis(etapes, juges)
    for cle in ("juge_a", "juge_b"):
        e = plan[cle]["etiquette"]
        if d["requis_usd"].get(e, 0.0) > plan[f"plafond_{cle}_usd"] + 1e-9:
            raise J.ProtocoleRefuse(f"devis de {e} : {d['requis_usd'][e]} USD requis au-dessus de sa part ({plan[f'plafond_{cle}_usd']} USD)")
    if d["requis_total_usd"] > plan["plafond_usd"] + 1e-9:
        raise J.ProtocoleRefuse(f"devis requis {d['requis_total_usd']} USD au-dessus du plafond {plan['plafond_usd']} USD")
    if d["duree_h"][1] * 3600.0 > plan["duree_max_s"] + 1e-9:
        raise J.ProtocoleRefuse(f"durée haute {d['duree_h'][1]} h au-dessus de la durée maximale {plan['duree_max_s'] / 3600:g} h")
    return d


def preparer_reel(args, cfg):
    """Toutes les gardes du mode réel, sans appel ni écriture dans la sortie ; rend le contexte de la course."""
    from pole import configuration_v53 as c53
    entropie, empreinte, gelees, plan = lire_preenregistrement(args.preenregistrement)
    if not os.path.isfile(args.configuration):
        raise J.ProtocoleRefuse(f"configuration introuvable : {args.configuration}")
    sha_conf = sha256_fichier(args.configuration)
    if sha_conf != plan["configuration_sha256"]:
        raise J.ProtocoleRefuse(f"configuration d'empreinte {sha_conf[:12]}… : le texte scellé gèle {plan['configuration_sha256'][:12]}…")
    go = verifier_go(args.registre_go, args.go, plan, cfg)
    conf = cfg.lire_configuration_v56(args.configuration)
    materiaux = J.construire_materiaux(plan["graine_materiaux"])
    controles = J.exiger_materiaux(materiaux, plan["materiaux_sha256"])
    pieces = conf.get("pieces") or {}
    for k in ("piece_consigne_ancienne", "piece_question") + (("piece_lot_reel",) if plan["piece_lot_reel"] != "aucune" else ()):
        if plan[k] not in pieces:
            raise J.ProtocoleRefuse(f"configuration : pièce {plan[k]!r} ({k}) absente de « pieces »")
    try:
        ancienne = c53.texte_piece(conf, plan["piece_consigne_ancienne"])
        lot_reel = None
        if plan["piece_lot_reel"] != "aucune":
            objet = json.loads(c53.texte_piece(conf, plan["piece_lot_reel"]))
            lot_reel = J.lot_reel_depuis(objet, c53.texte_piece(conf, plan["piece_question"]), plan["correspondance"])
    except (c53.ConfigurationRefusee, OSError, ValueError) as e:
        raise J.ProtocoleRefuse(f"pièce de la configuration illisible ou altérée : {e}") from None
    items = conf.get("items_juge")
    if lot_reel is not None:
        lot_reel["interdites"], lot_reel["mode_a4"] = tuple(conf["etiquettes_interdites"]), conf["a4"]["mode"]
        J.exiger_lot_reel(lot_reel, lot_reel["interdites"], lot_reel["mode_a4"])
    J.exiger_entrees(materiaux["lots"] + ([lot_reel] if lot_reel else []), {"ancien": ancienne, "v2": J.CONSIGNE_PAIRE_V2})
    graines = Graines(entropie)
    etapes, graphes = J.etapes_v2(materiaux, plan["juge_a"], plan["juge_b"], graines, lot_reel=lot_reel)
    devis = verifier_devis(etapes, plan)
    base_sessions = tempfile.mkdtemp(prefix="juges-idees-v2-sessions-")  # hors de la sortie
    try:
        adaptateurs, accuses, infos = juges_reels(conf, plan, base_sessions, os.path.abspath(args.dossier))
    except BaseException:
        import shutil
        shutil.rmtree(base_sessions, ignore_errors=True)  # refus : le dossier des sessions, vide, n'est pas gardé
        raise
    for cle in ("juge_a", "juge_b"):
        plan[cle]["modeles_servis_permis"] = list(infos["modeles_servis_permis"].get(plan[cle]["etiquette"], []))
    return {"mode": "reel (decisif)", "entropie": entropie, "plan": plan, "graines": graines, "materiaux": materiaux,
            "controles": controles, "lot_reel": lot_reel, "etapes": etapes, "graphes": graphes, "devis": devis,
            "adaptateurs": adaptateurs, "consignes": {"ancien": ancienne, "v2": J.CONSIGNE_PAIRE_V2}, "items": items,
            "plafond_session": infos["budget_appel_usd"], "base_sessions": base_sessions, "horloge": time.monotonic,
            "dormir": time.sleep,
            "preenregistrement": {"chemin": os.path.relpath(os.path.realpath(args.preenregistrement), RACINE), "sha256": empreinte,
                                  "empreintes_du_code_verifiees": gelees, "go": go},
            "configuration": dict(infos, chemin=os.path.abspath(args.configuration), sha256=sha_conf,
                                  empreinte_configuration=conf.get("empreinte_configuration"), accuses_plafond=accuses,
                                  consigne_ancienne_sha256=pieces[plan["piece_consigne_ancienne"]]["sha256"])}


def preparer_a_blanc(args):
    if args.graine is None or not 0 <= args.graine < 2 ** 64:
        raise J.ProtocoleRefuse("à blanc : --graine G exigée, G dans [0 ; 2⁶⁴[")
    for nom in ("strategie_a", "strategie_b"):
        if getattr(args, nom) not in J.STRATEGIES:
            raise J.ProtocoleRefuse(f"--{nom.replace('_', '-')} : parmi {J.STRATEGIES}")
    if not args.plafond_usd > 0 or not args.duree_max_h > 0:
        raise J.ProtocoleRefuse("à blanc : --plafond-usd et --duree-max-h > 0")
    regles = {"a": J.regles_de_panne(args.panne_a), "b": J.regles_de_panne(args.panne_b)}
    plan = {"juge_a": dict(JUGES_A_BLANC["juge_a"]), "juge_b": dict(JUGES_A_BLANC["juge_b"]), "correspondance": CORRESPONDANCE_A_BLANC,
            "graine_materiaux": J.GRAINE_MATERIAUX, "plafond_usd": args.plafond_usd, "duree_max_s": args.duree_max_h * 3600.0,
            "plafond_juge_a_usd": args.plafond_usd * 0.4, "plafond_juge_b_usd": args.plafond_usd * 0.6}
    materiaux = J.construire_materiaux(plan["graine_materiaux"])
    controles = J.exiger_materiaux(materiaux)
    lot_reel, qualites = None, None
    if not args.sans_lot_reel:
        objet, qualites = J.lot_reel_substitution(args.graine % (2 ** 32))
        lot_reel = J.lot_reel_depuis(objet, J.QUESTION_SUBSTITUTION, CORRESPONDANCE_A_BLANC)
    J.exiger_entrees(materiaux["lots"] + ([lot_reel] if lot_reel else []),
                     {"ancien": J.CONSIGNE_ANCIENNE_SUBSTITUTION, "v2": J.CONSIGNE_PAIRE_V2})
    graines = Graines(args.graine)
    etapes, graphes = J.etapes_v2(materiaux, plan["juge_a"], plan["juge_b"], graines, lot_reel=lot_reel)
    juges = {plan["juge_a"]["etiquette"]: plan["juge_a"], plan["juge_b"]["etiquette"]: plan["juge_b"]}
    oracle = J.oracle_depuis(materiaux, lot_reel, qualites)
    horloge = J.HorlogeVirtuelle()
    adaptateurs = {}
    for cle, lettre, cout, g in (("juge_a", "a", args.cout_a, args.graine), ("juge_b", "b", args.cout_b, args.graine + 1)):
        j = plan[cle]
        base = J.AdaptateurScripte(getattr(args, f"strategie_{lettre}"), oracle, graine=g, cout_par_appel_usd=cout,
                                   p_juste=getattr(args, f"p_juste_{lettre}"), biais_premier=getattr(args, f"biais_{lettre}"),
                                   horloge=horloge, secondes_par_appel=j["secondes"][0])
        adaptateurs[j["fournisseur"]] = (J.AdaptateurPanneScripte(base, regles[lettre], horloge=horloge, secondes_par_echec=5.0)
                                         if regles[lettre] else base)
    return {"mode": "a-blanc (exploratoire)", "entropie": args.graine, "plan": plan, "graines": graines, "materiaux": materiaux,
            "controles": controles, "lot_reel": lot_reel, "etapes": etapes, "graphes": graphes, "devis": J.devis(etapes, juges),
            "adaptateurs": adaptateurs, "consignes": {"ancien": J.CONSIGNE_ANCIENNE_SUBSTITUTION, "v2": J.CONSIGNE_PAIRE_V2},
            "items": list(J.ITEMS_SUBSTITUTION), "plafond_session": 1.0, "base_sessions": None, "horloge": horloge,
            "dormir": horloge.avancer, "preenregistrement": None,
            "configuration": {"juges_scriptes": {"a": args.strategie_a, "b": args.strategie_b}, "couts_fictifs": [args.cout_a, args.cout_b],
                              "pannes_scriptees": {k: [list(r) for r in v] for k, v in regles.items()},
                              "horloge": "virtuelle (aucune attente réelle)"}}


# --- puissance ---------------------------------------------------------------------------------------------------------------
def calculs_de_puissance(repetitions, graines_plan, graine):
    """Tables citées par le préenregistrement : (1) modèle binormal, test de Mann et Whitney exact (D1 au niveau 0,05, D4 au
    niveau 0,10, sur un second tirage indépendant) ; (2) D1b, bonnes lois contre lois fausses (15 contre 7) ; (3) test binomial
    exact du critère D6 ; (4) plan joué par des juges scriptés « bruite » (sans biais de position, ancien protocole indulgent) à
    plusieurs exactitudes par comparaison, lu par la lecture gelée."""
    table1 = [J.puissance_aire(n, n, a, repetitions=repetitions, graine=graine)
              for n in (10, 12, 14, 15, 16, 18, 20) for a in (0.5, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9)]
    table_d1b = [J.puissance_aire(15, 7, a, repetitions=repetitions, graine=graine) for a in (0.5, 0.7, 0.75, 0.8, 0.85, 0.9)]
    table_d6 = [J.puissance_binomiale(n, p, J.SEUILS_LECTURE_V2["alpha_reproduction"]) for n in (20, 24, 28, 32, 36, 39)
                for p in (0.5, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9)]
    materiaux = J.construire_materiaux()
    oracle = J.oracle_depuis(materiaux)
    a, b = dict(JUGES_A_BLANC["juge_a"]), dict(JUGES_A_BLANC["juge_b"])
    table2 = []
    for p in (0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.95):
        issues, d = {}, {k: 0 for k in ("D1", "D4", "D5", "D6", "D1b")}
        aires, exactitudes, appels_b = [], [], []
        for k in range(graines_plan):
            g = Graines(graine * 1000 + k)
            etapes, _ = J.etapes_v2(materiaux, a, b, g)
            h = J.HorlogeVirtuelle()
            ad = {a["fournisseur"]: J.AdaptateurScripte("bruite", oracle, graine=k, p_juste=p, biais_premier=0.0, p_item_bon=1.0,
                                                        p_item_mauvais=1.0),
                  b["fournisseur"]: J.AdaptateurScripte("bruite", oracle, graine=10 ** 6 + k, p_juste=p, biais_premier=0.0,
                                                        p_item_bon=1.0, p_item_mauvais=1.0)}
            c = J.Compteur(1e9, 1e12, h, {a["etiquette"]: 0.0, b["etiquette"]: 0.0}, dormir=h.avancer)
            jn = J.executer_validation(etapes, materiaux=materiaux, juges={a["etiquette"]: a, b["etiquette"]: b}, adaptateurs=ad,
                                       consignes={"ancien": J.CONSIGNE_ANCIENNE_SUBSTITUTION, "v2": J.CONSIGNE_PAIRE_V2},
                                       items=J.ITEMS_SUBSTITUTION, graines=g, compteur=c, plafond_session=1.0,
                                       interdites=J.ETIQUETTES_INTERDITES_TEMOINS, dossier_appel=lambda j, e: os.devnull)
            mes = J.mesurer(jn, materiaux, a, b, etapes=etapes)
            lec = J.lire_validation(mes)
            issues[lec["issue"]] = issues.get(lec["issue"], 0) + 1
            for x in d:
                d[x] += bool(lec["criteres"][x]["tenu"])
            aires.append(mes["v2"][a["etiquette"]]["1"]["aire"])
            exactitudes.append(mes["accord"]["exactitude_b"]["exactitude"] or 0.0)
            appels_b.append(sum(len(e["appels"]) for e in etapes if e["juge"] == b["etiquette"] and e["protocole"] == "v2"))
        aires_t = sorted(aires)
        table2.append({"exactitude_par_comparaison": p, "graines": graines_plan, "issues": issues,
                       "parts_criteres": {x: round(v / graines_plan, 3) for x, v in d.items()},
                       "aire_v2_moyenne": round(sum(aires) / len(aires), 3), "aire_v2_decile_bas": round(aires_t[graines_plan // 10], 3),
                       "exactitude_b_moyenne": round(sum(exactitudes) / len(exactitudes), 3),
                       "paires_b_min_moyenne_max": [min(appels_b), round(sum(appels_b) / len(appels_b), 1), max(appels_b)]})
    return {"version": VERSION, "graine": graine, "repetitions": repetitions, "binormal_mann_whitney": table1,
            "binormal_d1b_15_contre_7": table_d1b, "binomial_d6": table_d6, "plan_v2_juges_scriptes": table2,
            "regle": "binormal : mauvais ~ N(0, 1), bons ~ N(√2·Φ⁻¹(aire), 1) ; graines SeedSequence (clé de tâche « puissance|… ») ; "
                     "plan : graines de course Graines(graine·1000 + k), k = 0…graines_plan − 1"}


# --- exécution ----------------------------------------------------------------------------------------------------------------
def dossier_appel_pour(base):
    def dossier(juge, etape):
        if base is None:
            return os.devnull
        d = os.path.join(base, juge, f"{etape['phase']}-{etape['lot']}-t{etape['tirage']}")
        os.makedirs(d, exist_ok=True)
        return d
    return dossier


class FilJournal:
    """Journal au fil de l'eau (brouillon 3, contre-lecture v2, I8) : une ligne JSON par entrée du journal (réponse, perte, attente,
    étape, projection, arrêt d'un juge, phase), écrite, vidée et synchronisée sur disque aussitôt ; scellé (compagnon `.sha256`) à
    la fin de la course, qu'elle aille à son terme ou s'arrête. Un processus tué laisse le fichier tel quel (règle
    `REGLE_COURSE_TUEE`)."""

    def __init__(self, chemin):
        if os.path.exists(chemin):
            raise FileExistsError(f"journal au fil de l'eau déjà présent : {chemin} (on n'écrase jamais)")
        self.chemin, self.lignes = chemin, 0
        self.f = open(chemin, "x", encoding="utf-8")

    def __call__(self, cle, entree):
        self.f.write(json.dumps({"n": self.lignes + 1, "cle": cle, "entree": entree}, ensure_ascii=False, sort_keys=True,
                                default=str) + "\n")
        self.f.flush()
        os.fsync(self.f.fileno())
        self.lignes += 1

    def sceller(self, bilan=None):
        if bilan is not None:
            self("bilan", bilan)
        self.f.close()
        with open(self.chemin + ".sha256", "x", encoding="utf-8") as g:
            g.write(f"{sha256_fichier(self.chemin)}  {os.path.basename(self.chemin)}\n")
        return self.lignes


def _interruption(signum, frame):  # brouillon 3 (I8) : un signal de fin devient une interruption, journal partiel scellé
    raise KeyboardInterrupt(f"signal {signum}")


def ecrire_resultats(sortie, ctx, journal, arret=None):
    juge_a, juge_b = ctx["plan"]["juge_a"], ctx["plan"]["juge_b"]
    ecrire_json_scelle(os.path.join(sortie, SORTIES["journal"]), dict(journal, arret=arret))
    mesures = J.mesurer(journal, ctx["materiaux"], juge_a, juge_b, etapes=ctx["etapes"], lot_reel=ctx["lot_reel"])
    ecrire_json_scelle(os.path.join(sortie, SORTIES["mesures"]), mesures)
    lecture = J.lire_validation(mesures)
    lecture["partielle"] = arret is not None
    lecture["arret"] = arret
    ecrire_json_scelle(os.path.join(sortie, SORTIES["lecture"]), lecture)
    return lecture


def principal(argv=None):
    a = argparse.ArgumentParser(description="Validation des juges d'idéation v2 (ancien protocole contre v2, mêmes fiches)")
    a.add_argument("dossier", nargs="?")
    g = a.add_mutually_exclusive_group(required=True)
    g.add_argument("--a-blanc", action="store_true", help="juges scriptés, sans réseau (exploratoire)")
    g.add_argument("--puissance", action="store_true", help="calculs de puissance cités par le préenregistrement (aucune écriture)")
    g.add_argument("--preenregistrement", help="mode réel : préenregistrement scellé (graine = son empreinte)")
    a.add_argument("--graine", type=int)
    a.add_argument("--configuration")
    a.add_argument("--moteur", choices=("reel",))
    a.add_argument("--confirmer-moteur-reel", action="store_true")
    a.add_argument("--registre-go")
    a.add_argument("--go")
    a.add_argument("--verifier-seulement", action="store_true")
    a.add_argument("--strategie-a")
    a.add_argument("--strategie-b")
    a.add_argument("--sans-lot-reel", action="store_true", default=None)
    a.add_argument("--cout-a", type=float)
    a.add_argument("--cout-b", type=float)
    a.add_argument("--plafond-usd", type=float)
    a.add_argument("--duree-max-h", type=float)
    a.add_argument("--panne-a")
    a.add_argument("--panne-b")
    a.add_argument("--p-juste-a", type=float)
    a.add_argument("--p-juste-b", type=float)
    a.add_argument("--biais-a", type=float)
    a.add_argument("--biais-b", type=float)
    a.add_argument("--repetitions", type=int, default=20000)
    a.add_argument("--graines-plan", type=int, default=40)
    args = a.parse_args(argv)
    from pole import configuration_v56 as cfg
    try:
        if args.puissance:
            print(json.dumps(calculs_de_puissance(args.repetitions, args.graines_plan, args.graine or 0), ensure_ascii=False, indent=1))
            return 0
        if not args.dossier:
            raise J.ProtocoleRefuse("dossier de sortie exigé")
        if os.path.exists(args.dossier) and (not os.path.isdir(args.dossier) or os.listdir(args.dossier)):
            raise FileExistsError(f"dossier de sortie non vide : {args.dossier} (on n'écrase jamais)")
        donnees = {k: getattr(args, k) for k in OPTIONS_A_BLANC if getattr(args, k) is not None}
        if args.a_blanc:
            if args.moteur or args.configuration or args.go or args.registre_go or args.verifier_seulement:
                raise J.ProtocoleRefuse("à blanc : ni moteur réel, ni configuration, ni GO")
            for k, v in (("strategie_a", "indulgent"), ("strategie_b", "parfait"), ("sans_lot_reel", False), ("cout_a", 0.062),
                         ("cout_b", 0.5), ("plafond_usd", PLAFOND_MAX_USD), ("duree_max_h", 48.0), ("panne_a", "aucune"),
                         ("panne_b", "aucune"), ("p_juste_a", 0.75), ("p_juste_b", 0.75), ("biais_a", 0.10), ("biais_b", 0.10)):
                if getattr(args, k) is None:
                    setattr(args, k, v)
            ctx = preparer_a_blanc(args)
        else:
            if args.graine is not None:
                raise J.ProtocoleRefuse("mode réel : la graine est l'empreinte du préenregistrement, --graine refusée")
            if donnees:
                raise J.ProtocoleRefuse(f"mode réel : le plan est lu dans le texte scellé ; options refusées : {sorted(donnees)}")
            if args.moteur != "reel" or not args.confirmer_moteur_reel or not args.configuration:
                raise J.ProtocoleRefuse("mode réel : --configuration, --moteur reel et --confirmer-moteur-reel exigés")
            ctx = preparer_reel(args, cfg)
            if args.verifier_seulement:
                import shutil
                shutil.rmtree(ctx["base_sessions"], ignore_errors=True)  # dossier des sessions, vide : rien n'est gardé
                print(json.dumps({"verification": "conforme", "ecriture": "aucune dans la sortie", "appel": "aucun",
                                  "devis": ctx["devis"], "plan": {k: v for k, v in ctx["plan"].items()},
                                  "controles_des_materiaux": ctx["controles"], "configuration": ctx["configuration"]},
                                 ensure_ascii=False, indent=1, default=str))
                return 0
    except (FileExistsError, J.ProtocoleRefuse, cfg.ConfigurationRefusee) as e:
        print(f"refus : {type(e).__name__} : {e}", file=sys.stderr)
        return 2
    except Exception as e:  # noqa: BLE001 — refus nommé (relais, porte, configuration), jamais de repli
        print(f"refus : {type(e).__name__} : {e}", file=sys.stderr)
        return 2
    sortie = args.dossier
    os.makedirs(sortie, exist_ok=True)
    plan = ctx["plan"]
    juges = {plan["juge_a"]["etiquette"]: plan["juge_a"], plan["juge_b"]["etiquette"]: plan["juge_b"]}
    manifeste = {"version": VERSION, "coeur": J.VERSION, "version_plan": J.VERSION_PLAN, "mode": ctx["mode"],
                 "entropie_racine": str(ctx["entropie"]),
                 "horodatage_debut_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                 "plan": plan, "devis": ctx["devis"], "preenregistrement": ctx["preenregistrement"],
                 "configuration": ctx["configuration"], "dossier_des_sessions": ctx["base_sessions"],
                 "consigne_paire_sha256": J.EMPREINTE_CONSIGNE_PAIRE_V2, "politique_relais": J.politique_relais(),
                 "materiaux_empreinte": ctx["materiaux"]["empreinte"], "controles_des_materiaux": ctx["controles"],
                 "lot_reel": ({"fiches": len(ctx["lot_reel"]["fiches"]), "familles": {f["ident"]: f["familles"] for f in ctx["lot_reel"]["fiches"]}}
                              if ctx["lot_reel"] else None),
                 "journal_au_fil": SORTIES["fil"], "regle_course_tuee": REGLE_COURSE_TUEE,
                 "numpy": np.__version__, "python": platform.python_version(), "depot": commit(),
                 "code_sha256": {r: sha256_fichier(os.path.join(RACINE, r)) for r in FICHIERS_GELES},
                 "regle_des_graines": ("graines_v53.Graines(entropie) : SeedSequence(entropie, spawn_key=(cle_de_tache(tâche),)) ; "
                                       "entropie = int(SHA-256 du texte scellé, 16) en mode réel, --graine à blanc ; tâches : "
                                       "graphe|<lot>|tirage-<t>, ordres|<lot>|tirage-<t>|<juge>, paires-b|<lot>, ordre-ancien|<lot>|<juge>|tirage-<t>, "
                                       "ordre-ancien-sans-dossier|<lot>|<juge>, anonymisation|<juge>|tirage-<t>|<lot>|<fiche>, "
                                       "anonymisation-sans-dossier|<juge>|<lot>|<fiche>, graphe|reel|<juge>, ordres|reel|<juge> ; matériaux : "
                                       "Graines(graine_materiaux), tâches materiaux|<monde>|tentative-<k> et materiaux|<monde>|fiche-<k> ; "
                                       "contrôle de diagnosticité : Graines(20261102000 + k), k = 0…19")}
    ecrire_json_scelle(os.path.join(sortie, SORTIES["manifeste"]), manifeste)
    ecrire_json_scelle(os.path.join(sortie, SORTIES["materiaux"]), ctx["materiaux"])
    ecrire_json_scelle(os.path.join(sortie, SORTIES["plan"]), {"etapes": ctx["etapes"], "devis": ctx["devis"],
                                                               "graphes": {f"{k[0]}|{k[1]}": v for k, v in ctx["graphes"].items()}})
    compteur = J.Compteur(plan["plafond_usd"], plan["duree_max_s"], ctx["horloge"], {j: v["prix_usd"] for j, v in juges.items()},
                          parts={plan["juge_a"]["etiquette"]: plan["plafond_juge_a_usd"],
                                 plan["juge_b"]["etiquette"]: plan["plafond_juge_b_usd"]}, dormir=ctx["dormir"])
    fil = FilJournal(os.path.join(sortie, SORTIES["fil"]))
    precedent = signal.getsignal(signal.SIGTERM)
    try:
        signal.signal(signal.SIGTERM, _interruption)
    except ValueError:  # hors du fil principal : le signal garde son traitement (le journal au fil de l'eau reste la trace)
        precedent = None
    try:
        journal = J.executer_validation(ctx["etapes"], materiaux=ctx["materiaux"], juges=juges, adaptateurs=ctx["adaptateurs"],
                                        consignes=ctx["consignes"], items=ctx["items"], graines=ctx["graines"], compteur=compteur,
                                        plafond_session=ctx["plafond_session"], interdites=J.ETIQUETTES_INTERDITES_TEMOINS,
                                        dossier_appel=dossier_appel_pour(ctx["base_sessions"]), lot_reel=ctx["lot_reel"], fil=fil)
    except J.ArretJuges as e:
        if precedent is not None:
            signal.signal(signal.SIGTERM, precedent)
        fil.sceller(compteur.bilan())
        journal = dict(e.partiel, depense_usd=round(compteur.depense, 4), appels=compteur.appels)
        lecture = ecrire_resultats(sortie, ctx, journal, arret=f"{type(e).__name__} : {e}")
        print(json.dumps({"mode": ctx["mode"], "arret": str(e), "appels": compteur.appels, "depense_usd": round(compteur.depense, 4),
                          "issue": lecture["issue"], "partielle": True}, ensure_ascii=False), file=sys.stderr)
        return 3
    if precedent is not None:
        signal.signal(signal.SIGTERM, precedent)
    fil.sceller(compteur.bilan())
    journal = dict(journal, depense_usd=round(compteur.depense, 4), appels=compteur.appels,
                   duree_s=round(ctx["horloge"]() - compteur.debut, 1))
    lecture = ecrire_resultats(sortie, ctx, journal)
    print(json.dumps({"mode": ctx["mode"], "appels": compteur.appels, "depense_usd": round(compteur.depense, 4), "issue": lecture["issue"],
                      "sous_issue": lecture["sous_issue"], "bras_sans_dossier": lecture["bras_sans_dossier"]["lecture"],
                      "lecture_des_tables": lecture["lecture_des_tables"]["lecture"], "audit": lecture["audit"]["declenche"]},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(principal())
