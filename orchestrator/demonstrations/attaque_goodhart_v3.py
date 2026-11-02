"""Attaque de Goodhart contre le juge statistique, v3 (A1-bis, quatre fournisseurs) : lanceur (fichier neuf, R12). Cœur :
`pole/attaque_goodhart_v3.py`, qui importe la v2 ; ce lanceur charge le lanceur v2 (`demonstrations/attaque_goodhart_v2.py`,
inchangé) pour tout ce qui ne change pas : blocs du texte, substitutions des commandes, GO, commit, chargement d'`ideation_v8`.

Deux modes, exclusifs :
- **à blanc** (`--a-blanc --graine G`, G dans [0 ; 2⁶⁴[) : proposeurs scriptés, aucun réseau, aucune clé ; exploratoire, ne
  décide rien ; le plan (mode course ou essai, cartes, mondes, fournisseurs, fils, pannes simulées, rejeux, plafonds) se
  règle en ligne de commande ;
- **réel** (`--preenregistrement P --configuration CONF --moteur reel --confirmer-moteur-reel --registre-go R --go ID`) : chaque
  fournisseur du bloc `plan-gele` par une commande externe v56 de la configuration. Le plan est lu dans le texte scellé,
  jamais en ligne de commande ; graine = empreinte SHA-256 du texte scellé (≥ 2⁶⁴). Le texte est, selon son bloc `mode`,
  `prereg/preenregistrement-attaque-goodhart-v3-v<N>.md` (course) ou `prereg/fiche-essai-attaque-goodhart-v3-v<N>.md` (essai) ;
  tout autre chemin est refusé, et le mode du bloc doit être celui du nom.

Bloc `plan-gele` (lignes « clé: valeur ») : `mode`, `grille` (course : « C cartes par monde, U unités par case », U = C ×
fournisseurs, U admise) ou `cartes` (essai : 1), `mondes`, `fournisseurs` (liste ordonnée de noms), une ligne
`fournisseur_<nom>: type=commande_externe, port=P, modele=M[, repli=R], fils=F, taux_usd=T, secondes=B-H` par nom,
`essais_avant_repli`, `relais_perdu_h` (heures d'attente cumulée par fournisseur avant l'arrêt « relais perdu », ou « aucun »),
`appels_max_par_fournisseur` (essai), `plafond_usd`, `duree_max_h`, `decision_ecart` (course),
`configuration_sha256`, `go`, et les valeurs fixes que le texte recopie du code (`tentatives`, `rejeux_*` en course,
`fournisseurs_en_parallele`, `processus_rejeux` en course).

Gardes avant tout appel et toute écriture (code 2) : celles de la v2 (chemin fixé, scellé, marqueurs, bloc `empreintes-du-code`
égal à `FICHIERS_GELES`, configuration à l'empreinte du bloc, GO nommé par le texte sur une ligne entière au montant du plafond,
aucune variable de clé, budget par appel = `plafonds_session.proposeur`), plus : fournisseur du plan absent de la configuration
ou dont la commande manque ou n'est pas une commande externe ; port absent de la commande ; proposeur de la configuration
d'un autre modèle que le plan ; `modeles_servis_permis` non vide pour un fournisseur du plan (un identifiant servi admis
autre que le modèle demandé serait un repli muet) ; plafond sous le maximum du devis par fournisseur ; durée sous la durée
attendue haute avec `fils` fils ; grille non admise ou unités ≠ cartes × fournisseurs ; repli déclaré sans identifiant.
Codes : 0 course ou essai complet (le code ne décide rien) ; 2 refus ; 3 arrêt (plafond, part d'un fournisseur ou durée :
trace partielle écrite et scellée, aucun taux lu).

Étape de dépense : **une par fournisseur** (`etape_du_fournisseur`, `ETAPE_POLE = attaque_goodhart_v3/<nom>`, `PLAFOND_ETAPE_USD` =
sa part), écrite au manifeste (`etapes_de_depense`, `accuses_plafond`) ; le registre de dépense cumulée reste commun (jeton
`{REGISTRE}`), avec `--plafond-cumule-usd` = plafond de la course. Mesure déclarée `unites_sans_loi` dans chaque sortie.
"""

import argparse
import datetime
import importlib.util
import json
import os
import platform
import re
import sys
import tempfile
import time

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)

import numpy as np  # noqa: E402

from pole import attaque_goodhart_v3 as a3  # noqa: E402
from pole.outils import ecrire_json_scelle, manifeste, sha256_fichier, verifier_scelle  # noqa: E402


def _charger_lanceur_v2():
    spec = importlib.util.spec_from_file_location("attaque_goodhart_v2_lanceur_pour_v3", os.path.join(ICI, "attaque_goodhart_v2.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)  # instance propre, inchangée (R12)
    return m


l2 = _charger_lanceur_v2()
ag = a3.ag
ETAPE = "attaque_goodhart_v3"


def etape_du_fournisseur(nom):
    """Étape de dépense propre à un fournisseur : `attaque_goodhart_v3/<nom>`. La v2 passait la même étape à toutes les portes
    (`demonstrations/attaque_goodhart_v2.py:285`) ; le registre de dépense cumulée des commandes (côté session-depot) additionne
    réglé + engagé **par étape**, donc le plafond effectif d'A1 était la part d'un seul fournisseur pour les deux (défaut vu le
    2 novembre, 16:45 UTC). Ici chaque commande reçoit `ETAPE_POLE` = son étape et `PLAFOND_ETAPE_USD` = sa part
    (`PortePlafondEnvironnement.transmettre`, `pole/adaptateurs_v56.py:130-136`, puis `environnement_commande`, `:67-71` ; rien
    d'autre n'écrit ces variables : `AdaptateurCommandeExterne.environnement_commande` les laisse à la v56, `pole/adaptateurs.py:648-664`).
    Forme vérifiée par session-depot sur leur registre réel (`essai_etape_par_fournisseur.py`, sha256 `bae46233…`) : la garde
    d'étape est indexée sur le nom d'étape seul, « / » y est admis, chaque fournisseur atteint sa part et le plafond cumulé tient."""
    return f"{ETAPE}/{nom}"
SORTIES = {"course": "attaque-goodhart-v3.json", "essai": "essai-attaque-goodhart-v3.json"}
DOSSIER_PREREG = os.path.join(RACINE, "prereg")
NOMS_PREREG = {"course": re.compile(r"^preenregistrement-attaque-goodhart-v3-v[1-9][0-9]*\.md$"),
               "essai": re.compile(r"^fiche-essai-attaque-goodhart-v3-v[1-9][0-9]*\.md$")}
DEBUT_EMPREINTES, FIN_EMPREINTES, DEBUT_PLAN, FIN_PLAN = l2.DEBUT_EMPREINTES, l2.FIN_EMPREINTES, l2.DEBUT_PLAN, l2.FIN_PLAN
MARQUEUR, SHA, GRILLE, REGISTRE_COURSE = l2.MARQUEUR, l2.SHA, l2.GRILLE, l2.REGISTRE_COURSE
PreenregistrementRefuse = l2.PreenregistrementRefuse
# Valeurs fixes du bloc plan-gele (le texte les écrit, le lanceur vérifie qu'il dit la même chose que le code).
PLAN_FIXE = {"course": {"tentatives": str(ag.N_MAX), "rejeux_v8": str(ag.REJEUX["v8"]), "rejeux_v7": str(ag.REJEUX["v7"]),
                        "rejeux_audit": str(ag.REJEUX_AUDIT), "fournisseurs_en_parallele": "oui", "processus_rejeux": "2"},
             "essai": {"tentatives": str(ag.N_MAX), "fournisseurs_en_parallele": "oui"}}
CLES_PLAN = {"course": {"mode", "grille", "mondes", "fournisseurs", "essais_avant_repli", "relais_perdu_h", "plafond_usd", "duree_max_h",
                        "decision_ecart", "configuration_sha256", "go"},
             "essai": {"mode", "cartes", "mondes", "fournisseurs", "essais_avant_repli", "relais_perdu_h", "appels_max_par_fournisseur",
                       "plafond_usd", "duree_max_h", "configuration_sha256", "go"}}
# Fermeture des imports du chemin réel (essai `Fermeture.test_fichiers_geles_egaux_a_la_fermeture`) : celle de la v2 (le lanceur
# v2 est chargé) plus les deux fichiers neufs ; le texte scellé gèle l'empreinte de chacun, le lanceur refuse tout écart.
FICHIERS_GELES = tuple(sorted(set(l2.FICHIERS_GELES) | {"demonstrations/attaque_goodhart_v3.py", "pole/attaque_goodhart_v3.py"}))
OPTIONS_DE_PLAN = ("mode", "cartes", "mondes", "fournisseurs", "fils", "panne", "code_panne", "muet", "coupure_relais_s", "relais_perdu_h",
                   "appels_max", "essais_avant_repli", "n_max", "rejeux_v8",
                   "rejeux_v7", "rejeux_audit", "plafond_usd", "duree_max_h", "processus", "sequentiel", "proposeur", "sans_echo",
                   "cout_simule_usd")
A_BLANC = {"mode": "course", "cartes": 6, "mondes": "W1,W2", "fournisseurs": ",".join(f["nom"] for f in a3.PLAN_A1_BIS), "fils": None,
           "panne": None, "code_panne": None, "muet": False, "coupure_relais_s": None, "relais_perdu_h": "2", "appels_max": 20,
           "essais_avant_repli": 3, "n_max": ag.N_MAX, "rejeux_v8": ag.REJEUX["v8"],
           "rejeux_v7": ag.REJEUX["v7"], "rejeux_audit": ag.REJEUX_AUDIT, "plafond_usd": 1e9, "duree_max_h": 24.0, "processus": 2,
           "sequentiel": False, "proposeur": "sortant", "sans_echo": False, "cout_simule_usd": 0.0}
LIGNE_FOURNISSEUR = re.compile(r"^fournisseur_([a-z][a-z0-9]{0,15})$")
PAIRE = re.compile(r"^([a-z_]+)=(\S+)$")
SECONDES = re.compile(r"^(\d+(?:[.,]\d+)?)-(\d+(?:[.,]\d+)?)$")


# --- préenregistrement : bloc plan-gele v3 ----------------------------------------------------------------------------------
def _nombre(texte, nom):
    try:
        return float(texte.replace(",", "."))
    except ValueError:
        raise PreenregistrementRefuse(f"plan-gele : {nom} numérique, reçu {texte!r}") from None


def _entier(texte, nom):
    if not re.fullmatch(r"\d+", texte):
        raise PreenregistrementRefuse(f"plan-gele : {nom} entier, reçu {texte!r}")
    return int(texte)


def lire_fournisseur(nom, valeur):
    """Ligne `fournisseur_<nom>: type=…, port=…, modele=…[, repli=…], fils=…, taux_usd=…, secondes=B-H` → dict du plan."""
    champs = {}
    for morceau in [m.strip() for m in valeur.split(",") if m.strip()]:
        p = PAIRE.match(morceau)
        if not p or p.group(1) in champs:
            raise PreenregistrementRefuse(f"plan-gele : fournisseur_{nom} : « clé=valeur » attendu, reçu {morceau!r}")
        champs[p.group(1)] = p.group(2)
    attendues, facultatives = {"type", "port", "modele", "fils", "taux_usd", "secondes"}, {"repli"}
    if not attendues <= set(champs) or set(champs) - attendues - facultatives:
        raise PreenregistrementRefuse(f"plan-gele : fournisseur_{nom} : champs {sorted(attendues)} (+ repli), reçus {sorted(champs)}")
    s = SECONDES.match(champs["secondes"])
    if not s:
        raise PreenregistrementRefuse(f"plan-gele : fournisseur_{nom} : secondes=BAS-HAUT, reçu {champs['secondes']!r}")
    f = {"nom": nom, "type": champs["type"], "port": _entier(champs["port"], f"fournisseur_{nom}.port"), "modele": champs["modele"],
         "fils": _entier(champs["fils"], f"fournisseur_{nom}.fils"), "taux_usd": _nombre(champs["taux_usd"], f"fournisseur_{nom}.taux_usd"),
         "secondes": (_nombre(s.group(1), "secondes"), _nombre(s.group(2), "secondes"))}
    if "repli" in champs:
        f["repli"] = champs["repli"]
    try:
        return a3.verifier_fournisseur(f)
    except a3.AttaqueRefusee as e:
        raise PreenregistrementRefuse(f"plan-gele : {e}") from None


def lire_plan(texte, mode_attendu=None):
    """Bloc `plan-gele` v3 : rend le plan (dict) ou lève `PreenregistrementRefuse`. Les fournisseurs viennent du texte, jamais
    du code ; le devis par fournisseur borne le plafond et la durée."""
    lignes = {}
    for l in l2._bloc(texte, DEBUT_PLAN, FIN_PLAN, "plan-gele").splitlines():
        m = re.match(r"^\s*([a-z0-9_]+)\s*:\s*(.+?)\s*$", l)
        if m:
            if m.group(1) in lignes:
                raise PreenregistrementRefuse(f"plan-gele : clé {m.group(1)!r} en double")
            lignes[m.group(1)] = m.group(2)
    mode = lignes.get("mode")
    if mode not in a3.MODES:
        raise PreenregistrementRefuse(f"plan-gele : mode = course ou essai, reçu {mode!r}")
    if mode_attendu is not None and mode != mode_attendu:
        raise PreenregistrementRefuse(f"plan-gele : mode {mode!r} dans un texte nommé pour le mode {mode_attendu!r}")
    noms = [n.strip() for n in lignes.get("fournisseurs", "").split(",") if n.strip()]
    lignes_f = {LIGNE_FOURNISSEUR.match(k).group(1): v for k, v in lignes.items() if LIGNE_FOURNISSEUR.match(k)}
    attendues = CLES_PLAN[mode] | set(PLAN_FIXE[mode]) | {f"fournisseur_{n}" for n in noms}
    if set(lignes) != attendues:
        raise PreenregistrementRefuse(f"plan-gele : clés attendues {sorted(attendues)}, trouvées {sorted(lignes)}")
    if not noms or len(set(noms)) != len(noms) or set(lignes_f) != set(noms):
        raise PreenregistrementRefuse(f"plan-gele : fournisseurs {noms!r} : liste non vide sans doublon, une ligne fournisseur_<nom> chacun")
    for k, v in PLAN_FIXE[mode].items():
        if lignes[k] != v:
            raise PreenregistrementRefuse(f"plan-gele : {k} = {lignes[k]!r}, le code gelé dit {v!r}")
    try:
        fournisseurs = a3.verifier_fournisseurs([lire_fournisseur(n, lignes_f[n]) for n in noms])
    except a3.AttaqueRefusee as e:
        raise PreenregistrementRefuse(f"plan-gele : {e}") from None
    mondes = [m.strip() for m in re.split(r",| et ", lignes["mondes"]) if m.strip()]
    if not mondes or len(set(mondes)) != len(mondes) or not set(mondes) <= set(ag.MONDES):
        raise PreenregistrementRefuse(f"plan-gele : mondes {lignes['mondes']!r} (W1, W2 ou « W1 et W2 »)")
    mondes = [w for w in ag.MONDES if w in mondes]
    essais = _entier(lignes["essais_avant_repli"], "essais_avant_repli")
    plafond, duree = _nombre(lignes["plafond_usd"], "plafond_usd"), _nombre(lignes["duree_max_h"], "duree_max_h")
    relais_perdu_s = lire_relais_perdu(lignes["relais_perdu_h"])
    plan = {"mode": mode, "mondes": mondes, "fournisseurs": fournisseurs, "n_max": ag.N_MAX, "essais_avant_repli": essais,
            "relais_perdu_h": lignes["relais_perdu_h"], "relais_perdu_s": relais_perdu_s,
            "plafond_usd": plafond, "duree_max_s": duree * 3600.0, "parallele": True, "configuration_sha256": lignes["configuration_sha256"],
            "go": lignes["go"]}
    if mode == "course":
        g = GRILLE.match(lignes["grille"])
        if not g:
            raise PreenregistrementRefuse(f"plan-gele : grille {lignes['grille']!r} (« C cartes par monde, U unités par case »)")
        plan.update(cartes=int(g.group(1)), unites_par_case=int(g.group(2)), rejeux=dict(ag.REJEUX), rejeux_audit=ag.REJEUX_AUDIT,
                    processus=2, decision_ecart=lignes["decision_ecart"])
        if not lignes["decision_ecart"].strip():
            raise PreenregistrementRefuse("plan-gele : decision_ecart vide")
    else:
        plan.update(cartes=_entier(lignes["cartes"], "cartes"), appels_max_par_fournisseur=_entier(lignes["appels_max_par_fournisseur"],
                                                                                                "appels_max_par_fournisseur"),
                    processus=1)
    try:
        a3.verifier_plan(plan)
        d = a3.devis(plan["cartes"], mondes, fournisseurs, mode, plan.get("appels_max_par_fournisseur"))
    except a3.AttaqueRefusee as e:
        raise PreenregistrementRefuse(f"plan-gele : {e}") from None
    if not plafond >= d["total"]["usd_max"]:
        raise PreenregistrementRefuse(f"plan-gele : plafond {plafond} USD sous le maximum du devis ({d['total']['usd_max']} USD, "
                                      f"somme des maximums par fournisseur ; R20)")
    attendue = d["total"]["duree_attendue_haute_h"]
    if not duree >= attendue:
        raise PreenregistrementRefuse(f"plan-gele : durée {duree} h sous la durée attendue haute ({attendue:.2f} h : le fournisseur "
                                      "le plus long à ses fils, plus rejeux sur deux cœurs)")
    if not SHA.match(lignes["configuration_sha256"]):
        raise PreenregistrementRefuse("plan-gele : configuration_sha256 = 64 caractères hexadécimaux")
    if not re.fullmatch(r"GO-\d{4}-\d{2}-\d{2}-\d{2}", lignes["go"]):
        raise PreenregistrementRefuse("plan-gele : go = GO-AAAA-MM-JJ-NN")
    plan["devis"] = d
    return plan


def lire_relais_perdu(texte):
    """`relais_perdu_h: H` (réel > 0 : arrêt « relais perdu » après H heures d'attente cumulée par fournisseur, option (i) du texte)
    ou `relais_perdu_h: aucun` (option (ii) : aucun arrêt sur relais, seule la durée maximale arrête) ; rend les secondes ou None."""
    if texte.strip().lower() == "aucun":
        return None
    h = _nombre(texte, "relais_perdu_h")
    if not h > 0:
        raise PreenregistrementRefuse("plan-gele : relais_perdu_h = réel > 0 (heures) ou « aucun »")
    return h * 3600.0


def mode_du_nom(nom):
    for mode, motif in NOMS_PREREG.items():
        if motif.match(nom):
            return mode
    return None


def lire_preenregistrement(chemin):
    """Mode réel : le texte au chemin fixé de son mode, scellé, sans marqueur, gelant exactement le code présent ; rend
    (entropie, empreinte, empreintes gelées, plan)."""
    reel, dossier = os.path.realpath(chemin), os.path.realpath(DOSSIER_PREREG)
    mode = mode_du_nom(os.path.basename(reel))
    if os.path.dirname(reel) != dossier or mode is None:
        raise PreenregistrementRefuse("mode réel : le texte est prereg/preenregistrement-attaque-goodhart-v3-v<N>.md (course) ou "
                                      f"prereg/fiche-essai-attaque-goodhart-v3-v<N>.md (essai), pas {chemin} (la graine est son empreinte)")
    if not os.path.isfile(reel):
        raise PreenregistrementRefuse(f"préenregistrement introuvable : {chemin}")
    if not verifier_scelle(reel):
        raise PreenregistrementRefuse(f"préenregistrement non scellé (compagnon .sha256 absent ou non conforme) : {chemin}")
    with open(reel, encoding="utf-8") as f:
        texte = f.read()
    restants = sorted(set(MARQUEUR.findall(texte)))
    if restants:
        raise PreenregistrementRefuse(f"marqueur(s) non rempli(s) : {restants} (décision de Lazar à porter avant scellement)")
    gelees = re.findall(r"^([0-9a-f]{64})  (\S+)$", l2._bloc(texte, DEBUT_EMPREINTES, FIN_EMPREINTES, "empreintes-du-code"), re.M)
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
    plan = lire_plan(texte, mode_attendu=mode)
    empreinte = sha256_fichier(reel)
    return ag.verifier_entropie(int(empreinte, 16), decisif=True), empreinte, dict((r, h) for h, r in gelees), plan


verifier_go = l2.verifier_go  # le GO nommé par le texte, ligne entière, montant égal au plafond (configuration_v56.verifier_go_v56)


# --- chemin réel ------------------------------------------------------------------------------------------------------------------
def _port_dans_commande(f, port):
    if isinstance(f.get("port"), int) and not isinstance(f.get("port"), bool):
        return f["port"] == port
    return any(isinstance(x, str) and re.search(rf"(?<!\d){port}(?!\d)", x) for x in f.get("commande") or [])


def reglages_de_configuration(conf, fournisseurs):
    """Budget par appel = `plafonds_session.proposeur` (aucun défaut) ; pour chaque fournisseur du plan : relais de la
    configuration présent, du type du plan (commande externe), commande présente et portant le port, aucun identifiant servi
    admis en plus du modèle demandé (`modeles_servis_permis` vide : un repli n'est jamais muet), exactement un proposeur de la
    configuration pour ce fournisseur, au modèle du plan. Rend (budget, {nom: modèle})."""
    b = (conf.get("plafonds_session") or {}).get("proposeur")
    if not ag._reel(b, 0.0) or not b > 0:
        raise ag.AttaqueRefusee("configuration : plafonds_session.proposeur exigé (budget par appel, réel > 0, aucun défaut)")
    four = conf.get("fournisseurs") or {}
    modeles = {}
    for spec in fournisseurs:
        n = spec["nom"]
        f = four.get(n)
        if not isinstance(f, dict):
            raise ag.AttaqueRefusee(f"configuration : fournisseur « {n} » du plan absent de la configuration")
        if f.get("type") != spec["type"]:
            raise ag.AttaqueRefusee(f"configuration : relais « {n} » de type {spec['type']} exigé par le plan (trouvé {f.get('type')!r})")
        if not isinstance(f.get("commande"), list) or not f["commande"]:
            raise ag.AttaqueRefusee(f"configuration : la commande du fournisseur « {n} » manque")
        if not _port_dans_commande(f, spec["port"]):
            raise ag.AttaqueRefusee(f"configuration : le port {spec['port']} du plan n'apparaît ni dans la commande de « {n} » ni "
                                    "dans son champ « port »")
        if f.get("modeles_servis_permis"):
            raise ag.AttaqueRefusee(f"configuration : fournisseurs.{n}.modeles_servis_permis non vide ({f['modeles_servis_permis']!r}) : "
                                    "un identifiant servi admis autre que le modèle demandé serait un repli muet ; le repli se "
                                    "déclare dans le texte et se demande explicitement")
        p = [x for x in conf.get("proposeurs") or [] if isinstance(x, dict) and x.get("fournisseur") == n]
        if len(p) != 1 or not isinstance(p[0].get("modele"), str) or not p[0]["modele"]:
            raise ag.AttaqueRefusee(f"configuration : exactement un proposeur « {n} » avec son modèle exact (trouvés {len(p)})")
        if p[0]["modele"] != spec["modele"]:
            raise ag.AttaqueRefusee(f"configuration : le proposeur « {n} » demande {p[0]['modele']!r}, le plan dit {spec['modele']!r}")
        modeles[n] = spec["modele"]
    return float(b), modeles


def proposeurs_reels(conf, plan, base_sessions, sortie):
    """Adaptateurs du chemin réel pour les fournisseurs du plan, plafond réparti (plafond / nombre de fournisseurs) entre
    leurs portes ; rend (proposeurs, accusés, informations du manifeste). Le pire cas par appel est tenu par chaque commande
    externe (son plafond de session, `PLAFOND_SESSION_USD`)."""
    from pole.adaptateurs_v56 import AdaptateurCommandeExterneV56
    from pole.relais import noms_de_cle_presents
    presents = noms_de_cle_presents(os.environ)
    if presents:
        raise ag.AttaqueRefusee(f"variables de clé dans l'environnement de l'orchestrateur ({', '.join(presents)}) : les relais "
                                "tiennent les clés")
    fournisseurs = plan["fournisseurs"]
    budget, modeles = reglages_de_configuration(conf, fournisseurs)
    conf, substitutions = l2.substituer_commandes(conf, os.path.join(os.path.abspath(sortie), REGISTRE_COURSE), plan["plafond_usd"])
    v8 = l2.charger_ideation_v8()
    adaptateurs, portes = v8.adaptateurs_reels_v56(conf, sortie, base_sessions)
    manquants = [f["nom"] for f in fournisseurs if f["nom"] not in adaptateurs]
    if manquants:
        raise ag.AttaqueRefusee(f"configuration : adaptateurs manquants pour {manquants}")
    for f in fournisseurs:
        if not isinstance(adaptateurs[f["nom"]], AdaptateurCommandeExterneV56):
            raise ag.AttaqueRefusee(f"fournisseur « {f['nom']} » : commande externe v56 exigée, trouvé {type(adaptateurs[f['nom']]).__name__}")
    part = plan["plafond_usd"] / len(fournisseurs)
    accuses = {f["nom"]: portes[f["nom"]].transmettre(etape_du_fournisseur(f["nom"]), part) for f in fournisseurs}
    for f in fournisseurs:  # l'accusé de chaque porte porte bien l'étape propre du fournisseur et sa part (jamais une autre)
        if accuses[f["nom"]].get("etape") != etape_du_fournisseur(f["nom"]) or abs(accuses[f["nom"]].get("plafond_usd", -1) - part) > 0.01:
            raise ag.AttaqueRefusee(f"porte de « {f['nom']} » : accusé {accuses[f['nom']]!r}, attendu étape "
                                    f"{etape_du_fournisseur(f['nom'])!r} et part {part:.2f} USD")
    etapes = {f["nom"]: {"etape": etape_du_fournisseur(f["nom"]), "part_usd": part, "variables": ["ETAPE_POLE", "PLAFOND_ETAPE_USD"]}
              for f in fournisseurs}
    proposeurs = {}
    for f in fournisseurs:
        d = os.path.join(base_sessions, f["nom"])
        os.makedirs(d, exist_ok=True)
        proposeurs[f["nom"]] = a3.ProposeurAdaptateur(adaptateurs[f["nom"]], d, budget, (f["modele"],) + ((f["repli"],) if f.get("repli") else ()))
    longue = l2.consigne_la_plus_longue()
    infos = {"budget_appel_usd": budget, "modeles_demandes": modeles, "replis_declares": {f["nom"]: f.get("repli") for f in fournisseurs},
             "fils": {f["nom"]: f["fils"] for f in fournisseurs}, "ports": {f["nom"]: f["port"] for f in fournisseurs},
             "role_pole": ag.ROLE, "part_par_relais_usd": part, "etapes_de_depense": etapes,
             "substitutions_dans_les_commandes": substitutions,
             "consigne_la_plus_longue_octets": len(longue.encode("utf-8")),
             "pire_cas_par_appel": "tenu par chaque commande externe (PLAFOND_SESSION_USD = budget par appel)",
             "adaptateurs": {f["nom"]: adaptateurs[f["nom"]].description() for f in fournisseurs},
             "portes": {f["nom"]: portes[f["nom"]].description() for f in fournisseurs}}
    return proposeurs, accuses, infos


# --- à blanc ----------------------------------------------------------------------------------------------------------------------
def fils_a_blanc(texte):
    """`--fils N` (tous) ou `--fils kimi=6,opus=1` (par fournisseur, les autres gardent le plan A1-bis) ; rend {nom: N} ou N."""
    if texte is None:
        return {}
    if re.fullmatch(r"\d+", texte):
        return int(texte)
    sortie = {}
    for morceau in texte.split(","):
        m = re.fullmatch(r"\s*([a-z][a-z0-9]*)=(\d+)\s*", morceau)
        if not m:
            raise ag.AttaqueRefusee(f"--fils : N ou nom=N,… attendu, reçu {texte!r}")
        sortie[m.group(1)] = int(m.group(2))
    return sortie


def fournisseurs_a_blanc(noms_texte, fils=None):
    choisis = [n.strip() for n in noms_texte.split(",") if n.strip()]
    base = {f["nom"]: f for f in a3.PLAN_A1_BIS + a3.PLAN_B_PRIME}
    inconnus = [n for n in choisis if n not in base]
    if inconnus:
        raise ag.AttaqueRefusee(f"--fournisseurs : inconnus à blanc {inconnus} (connus : {sorted(base)})")
    fils = fils_a_blanc(fils)
    return a3.verifier_fournisseurs([dict(base[n], fils=fils if isinstance(fils, int) else fils.get(n, base[n]["fils"])) for n in choisis])


def pannes_a_blanc(texte):
    """`--panne MODELE:I-J[;MODELE:*]` : échecs scriptés des appels I à J de ce modèle (ou de tous ses appels)."""
    pannes = {}
    for morceau in (texte or "").split(";"):
        if not morceau.strip():
            continue
        m = re.fullmatch(r"\s*([A-Za-z0-9._-]+):(\*|(\d+)-(\d+))\s*", morceau)
        if not m:
            raise ag.AttaqueRefusee(f"--panne : MODELE:I-J ou MODELE:* attendu, reçu {morceau!r}")
        pannes[m.group(1)] = "*" if m.group(2) == "*" else set(range(int(m.group(3)), int(m.group(4)) + 1))
    return pannes


# --- programme --------------------------------------------------------------------------------------------------------------------
def principal(argv=None):
    a = argparse.ArgumentParser(description="Attaque de Goodhart contre le juge statistique (v3, A1-bis : quatre fournisseurs)")
    a.add_argument("dossier")
    g = a.add_mutually_exclusive_group(required=True)
    g.add_argument("--a-blanc", action="store_true", help="proposeurs scriptés, sans réseau (exploratoire)")
    g.add_argument("--preenregistrement", help="mode réel : texte scellé (course ou fiche d'essai ; graine = son empreinte)")
    a.add_argument("--graine", type=int)
    a.add_argument("--configuration")
    a.add_argument("--moteur", choices=("reel",))
    a.add_argument("--confirmer-moteur-reel", action="store_true")
    a.add_argument("--registre-go")
    a.add_argument("--go")
    a.add_argument("--verifier-seulement", action="store_true")
    a.add_argument("--mode", choices=a3.MODES)
    a.add_argument("--cartes", type=int)
    a.add_argument("--mondes")
    a.add_argument("--fournisseurs", help="à blanc : noms parmi les plans de référence, dans l'ordre (kimi,astra,fable,opus ; argon)")
    a.add_argument("--fils", help="à blanc : N (tous) ou nom=N,… (défaut : fils du plan A1-bis)")
    a.add_argument("--panne", help="à blanc : MODELE:I-J (appels I à J en échec) ou MODELE:* ; plusieurs séparés par « ; »")
    a.add_argument("--code-panne", type=int, help="à blanc : code de sortie simulé des pannes (3 relais, 4 budget, 5 modèle)")
    a.add_argument("--muet", action="store_true", default=None, help="à blanc : pannes muettes (aucune ligne de coût : plafond de session compté)")
    a.add_argument("--coupure-relais-s", type=float, help="à blanc : relais coupé pendant N secondes depuis le premier appel (code 3, coût plancher)")
    a.add_argument("--relais-perdu-h", help="à blanc : heures d'attente cumulée par fournisseur avant l'arrêt « relais perdu », ou « aucun »")
    a.add_argument("--appels-max", type=int, help="à blanc, mode essai : appels au plus par fournisseur")
    a.add_argument("--essais-avant-repli", type=int)
    a.add_argument("--n-max", type=int)
    a.add_argument("--rejeux-v8", type=int)
    a.add_argument("--rejeux-v7", type=int)
    a.add_argument("--rejeux-audit", type=int)
    a.add_argument("--plafond-usd", type=float)
    a.add_argument("--duree-max-h", type=float)
    a.add_argument("--processus", type=int)
    a.add_argument("--sequentiel", action="store_true", default=None)
    a.add_argument("--proposeur", choices=("sortant", "melangeur"))
    a.add_argument("--sans-echo", action="store_true", default=None)
    a.add_argument("--cout-simule-usd", type=float, help="à blanc : coût fictif par appel scripté (liste d'arrêt)")
    args = a.parse_args(argv)
    from pole import configuration_v56 as cfg
    base_sessions = None
    try:
        if os.path.exists(args.dossier) and os.listdir(args.dossier):
            raise FileExistsError(f"dossier de sortie non vide : {args.dossier} (on n'écrase jamais)")
        donnees = {k: getattr(args, k) for k in OPTIONS_DE_PLAN if getattr(args, k) is not None}
        if args.a_blanc:
            if args.graine is None or args.moteur or args.configuration or args.go or args.verifier_seulement:
                raise ag.AttaqueRefusee("à blanc : --graine G seulement (ni moteur réel, ni configuration, ni GO)")
            r = dict(A_BLANC, **donnees)
            mondes = [w for w in ag.MONDES if w in r["mondes"].split(",")]
            if sorted(mondes) != sorted(set(r["mondes"].split(","))):
                raise ag.AttaqueRefusee(f"--mondes : parmi {ag.MONDES}, reçu {r['mondes']!r}")
            fournisseurs = fournisseurs_a_blanc(r["fournisseurs"], r["fils"])
            plan = {"mode": r["mode"], "cartes": r["cartes"] if r["mode"] == "course" else 1, "mondes": mondes, "fournisseurs": fournisseurs,
                    "n_max": r["n_max"], "essais_avant_repli": r["essais_avant_repli"],
                    "plafond_usd": r["plafond_usd"],
                    "duree_max_s": r["duree_max_h"] * 3600.0, "processus": r["processus"], "parallele": not r["sequentiel"],
                    "appels_max_par_fournisseur": r["appels_max"] if r["mode"] == "essai" else None, "exiger_grille": False}
            if r["mode"] == "course":
                plan.update(rejeux={"v8": r["rejeux_v8"], "v7": r["rejeux_v7"]}, rejeux_audit=r["rejeux_audit"])
            plan["relais_perdu_h"] = str(r["relais_perdu_h"])
            plan["relais_perdu_s"] = lire_relais_perdu(plan["relais_perdu_h"])
            a3.verifier_plan(plan)
            entropie = ag.verifier_entropie(args.graine, decisif=False)
            mode, preenregistrement, conf_info = f"a-blanc (exploratoire, {plan['mode']})", None, None
            pannes = pannes_a_blanc(r["panne"])
        else:
            if args.graine is not None:
                raise ag.AttaqueRefusee("mode réel : la graine est l'empreinte du préenregistrement, --graine refusée")
            if donnees:
                raise ag.AttaqueRefusee(f"mode réel : le plan est lu dans le texte scellé ; options refusées : {sorted(donnees)}")
            if args.moteur != "reel" or not args.confirmer_moteur_reel or not args.configuration:
                raise ag.AttaqueRefusee("mode réel : --configuration, --moteur reel et --confirmer-moteur-reel exigés")
            entropie, empreinte, gelees, plan = lire_preenregistrement(args.preenregistrement)
            if not os.path.isfile(args.configuration):
                raise ag.AttaqueRefusee(f"configuration introuvable : {args.configuration}")
            sha_conf = sha256_fichier(args.configuration)
            if sha_conf != plan["configuration_sha256"]:
                raise ag.AttaqueRefusee(f"configuration d'empreinte {sha_conf[:12]}… : le texte scellé gèle "
                                        f"{plan['configuration_sha256'][:12]}… (aucune autre configuration)")
            go = verifier_go(args.registre_go, args.go, plan, cfg)
            conf = cfg.lire_configuration_v56(args.configuration)
            base_sessions = tempfile.mkdtemp(prefix="attaque-goodhart-v3-sessions-")  # hors de la sortie
            proposeurs, accuses, infos = proposeurs_reels(conf, plan, base_sessions, os.path.abspath(args.dossier))
            mode = f"reel (decisif, {plan['mode']})"
            preenregistrement = {"chemin": os.path.relpath(os.path.realpath(args.preenregistrement), RACINE), "sha256": empreinte,
                                 "empreintes_du_code_verifiees": gelees, "plan": {k: v for k, v in plan.items() if k != "devis"},
                                 "devis": plan["devis"], "go": go}
            conf_info = dict(infos, chemin=os.path.abspath(args.configuration), sha256=sha_conf,
                             empreinte_configuration=conf.get("empreinte_configuration"), accuses_plafond=accuses)
            if args.verifier_seulement:
                print(json.dumps({"verification": "conforme", "ecriture": "aucune", "appel": "aucun", "plan": preenregistrement["plan"],
                                  "configuration": conf_info}, ensure_ascii=False, indent=1, default=str))
                return 0
    except (FileExistsError, ag.AttaqueRefusee, cfg.ConfigurationRefusee) as e:
        print(f"refus : {type(e).__name__} : {e}", file=sys.stderr)
        return 2
    except Exception as e:  # noqa: BLE001 — refus nommé (relais, porte, configuration), jamais de repli
        print(f"refus : {type(e).__name__} : {e}", file=sys.stderr)
        return 2
    if args.a_blanc:
        proposeurs = {f["nom"]: a3.ProposeurScripte(args.proposeur or A_BLANC["proposeur"], echo=not args.sans_echo,
                                                    cout_par_appel=args.cout_simule_usd or 0.0, pannes=pannes, code_echec=args.code_panne,
                                                    muet=bool(args.muet), coupure_relais_s=args.coupure_relais_s)
                      for f in plan["fournisseurs"]}
    os.makedirs(args.dossier, exist_ok=True)
    m = manifeste(attaque=a3.VERSION, mode=mode, entropie_racine=str(entropie),
                  plan={k: v for k, v in plan.items() if k != "devis"}, devis=plan.get("devis"), preenregistrement=preenregistrement,
                  configuration=conf_info, coeur=a3.description(), numpy=np.__version__, python=platform.python_version(),
                  depot=l2.commit(), code_sha256={r: sha256_fichier(os.path.join(RACINE, r)) for r in FICHIERS_GELES},
                  proposeur_a_blanc=((args.proposeur or A_BLANC["proposeur"]) + ("" if not args.sans_echo else ", sans écho")
                                     + (f", pannes {sorted(pannes)}" if pannes else "")) if args.a_blanc else None)
    m["regle_des_graines"] = ("SeedSequence (R9) : entropie = int(SHA-256 du texte scellé, 16) en mode réel, --graine (< 2^64) à blanc ; "
                              "carte c du monde w : spawn_key=(cle('monde|w'), c) ; développement : (cle('developpement|w'), c) ; "
                              "évaluation de la tentative k : (cle('<monde>|<fournisseur>|<condition>|<juge>|scenario|noyau|frais'), c, k) ; "
                              "rejeu r : (cle('rejeu|<monde>|…'), c, k, 1 + r) ; audit A2 : (cle('audit|<monde>|…'), c, k, 1 + r) ; "
                              "rééchantillonnage : (cle('bootstrap'), cle('<monde>|<juge>')) ; le modèle (principal ou repli) n'entre "
                              "pas dans l'étiquette : une unité est jouée sous un seul modèle")
    for k in ("regle_du_repli", "regle_des_unites_jouees", "regle_de_l_attente", "regle_du_cout_inconnu"):
        m[k] = a3.description()[k]
    ecrire_json_scelle(os.path.join(args.dossier, "manifeste.json"), m)
    compteur = a3.Compteur(plan["plafond_usd"], plan["duree_max_s"], time.time, plan["fournisseurs"], plan.get("appels_max_par_fournisseur"),
                           relais_perdu_s=plan.get("relais_perdu_s"))
    sortie = os.path.join(args.dossier, SORTIES[plan["mode"]])
    commun = lambda: {"attaque": a3.VERSION, "mode": mode, "appels": compteur.appels, "reprises": compteur.reprises,  # noqa: E731
                      "depense_usd": round(compteur.usd, 4), "depense_par_fournisseur_usd": compteur.par_fournisseur,
                      "appels_par_fournisseur": compteur.appels_par_fournisseur, "appels_budget_depasse": compteur.budget_depasse,
                      "modeles_servis": compteur.modeles_servis, "par_fournisseur_et_modele_demande": compteur.par_modele,
                      "unites_basculees_sur_repli": compteur.replis, "attentes_relais": compteur.attentes_relais,
                      "attente_relais_s": {f: round(v, 1) for f, v in compteur.attente_relais_s.items()},
                      "appels_cout_inconnu": compteur.cout_inconnu, "cout_inconnu_usd": compteur.cout_inconnu_usd,
                      "relais_perdu_s": plan.get("relais_perdu_s"), "duree_s": round(time.time() - compteur.debut, 1),
                      "fin_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
    try:
        suites, rejeux, audits = a3.jouer_tout(proposeurs, entropie, plan, compteur, decisif=not args.a_blanc,
                                               parallele=plan["parallele"], processus=plan["processus"])
    except ag.ArretAttaque as e:
        rapport = dict(commun(), arret=str(e), suites_partielles=e.partiel.get("suites", []),
                       unites_sans_loi=a3.unites_sans_loi(e.partiel.get("suites", [])))
        if plan["mode"] == "course":
            rapport.update(issue="non jugeable (arrêt) : aucun taux lu", rejeux_partiels=e.partiel.get("rejeux", []))
        else:
            rapport["arret_essai"] = "aucune mesure calculée : trace partielle seule"
            a3.verifier_sortie_essai(rapport)
        ecrire_json_scelle(sortie, rapport)
        print(json.dumps({k: rapport[k] for k in ("mode", "arret", "appels", "depense_usd", "duree_s")}, ensure_ascii=False), file=sys.stderr)
        return 3
    if plan["mode"] == "essai":
        rapport = dict(commun(), preenregistrement=preenregistrement, mesures=a3.rapport_essai(suites, plan["fournisseurs"])["mesures"],
                       unites_sans_loi=a3.unites_sans_loi(suites), suites=suites)
        try:
            a3.verifier_sortie_essai(rapport)
        except ag.AttaqueRefusee as e:
            print(f"refus : {type(e).__name__} : {e}", file=sys.stderr)
            return 2
        ecrire_json_scelle(sortie, rapport)
        resume = {n: {m_: {k: v[k] for k in ("appels", "reussis", "echecs", "cout_usd_par_appel_reussi", "duree_s_par_appel_reussi",
                                              "modeles_servis")}
                      for m_, v in x["par_modele_demande"].items()} for n, x in rapport["mesures"].items()}
        print(json.dumps({"mode": mode, "mesures": resume, "appels": compteur.appels, "depense_usd": rapport["depense_usd"],
                          "duree_s": rapport["duree_s"]}, ensure_ascii=False, indent=1))
        return 0
    lecture = a3.lire(suites, rejeux, audits, plan["mondes"], plan["unites_par_case"], entropie, plan["fournisseurs"])
    rapport = dict(commun(), preenregistrement=preenregistrement, lecture=lecture, unites_sans_loi=a3.unites_sans_loi(suites),
                   suites=suites, rejeux=rejeux, audit_A2=audits)
    ecrire_json_scelle(sortie, rapport)
    print(json.dumps({"mode": mode, "issues": lecture["issues"], "audits": {w: x["audits"] for w, x in lecture["mondes"].items()},
                      "appels": compteur.appels, "depense_usd": rapport["depense_usd"], "duree_s": rapport["duree_s"],
                      "unites_basculees_sur_repli": compteur.replis, "unites_sans_loi": rapport["unites_sans_loi"]["total_sans_loi"],
                      "attentes_relais": compteur.attentes_relais, "appels_cout_inconnu": compteur.cout_inconnu},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(principal())
