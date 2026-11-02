"""Lanceur du tour fermé, version 62 (fichier neuf, R12 ; tâches A2 et A4) — **étage 1 seul**. Cœur : `pole/tour_ferme_v62.py` ;
lecture gelée (programme à part) : `demonstrations/lire_tour_ferme_v62.py`, `pole/lecture_tour_ferme_v62.py`.

Deux modes, exclusifs, qui passent par **le même chemin** (contre-lecture 2, C8, C9, C22) : les proposeurs sont des
`ProposeurAdaptateur` et l'étage reçoit un `AdaptateurEtageV62` dans les deux modes ; seules changent les feuilles —
- **à blanc** (`--a-blanc --graine G`, G < 2⁶⁴) : doublures scriptées (proposeurs, expérimentateur, vérificateur) qui ne lisent
  que le texte servi (consigne, contexte, préenregistrement court) ; aucun canal hors bande ; aucun réseau, aucune clé ;
- **réel** (`--preenregistrement P --configuration CONF --moteur reel --confirmer-moteur-reel --registre-go R --go ID`) : Kimi et
  Argon par les adaptateurs du pôle (`ideation_v8.adaptateurs_reels_v56`, mécanisme de l'attaque de Goodhart v2). Le plan de
  l'étage 1, les décisions D7 et D9, les plafonds (étage et part de chaque relais), l'empreinte du monde, la configuration et le
  GO sont lus dans le **texte scellé** (bloc `plan-gele`), jamais en ligne de commande ; E = int(sha256 du texte scellé) ≥ 2⁶⁴.

Gardes avant tout appel (code 2) : dossier de sortie non vide ; `--etage 2` (aucun étage 2 sous ce texte) ; `--bac` sans défaut
(« reel » exige `bwrap`) ; monde planté d'une autre empreinte (C20) ; mode réel : texte hors de
`prereg/preenregistrement-tour-ferme-v1-v<N>.md`, non scellé, nom à « brouillon », marqueur `<<…>>` hors des zones de l'étage 2
(`<!-- etage-2-hors-scellement : début/fin -->`), zones mal formées, code gelé non conforme, entropie < 2⁶⁴ (garde 6) ; plan
absent ou hors bornes (parts des relais de somme ≠ plafond) ; configuration d'une autre empreinte ou d'un autre plafond ; GO
autre ou d'un autre montant ; variable de clé ; machine non jetable ou variable hors de la liste blanche (garde 15, C11).
Codes : 0 relevé écrit (le code ne décide rien) ; 2 refus ; 3 arrêt (toute exception après le manifeste : relevé partiel scellé,
aucune issue lue, C12).

Usage à blanc : python3 -I -B demonstrations/tour_ferme_v62.py SORTIE_NEUVE --etage 1 --a-blanc --graine 7 --bac reel
                [--utilisateur-bac 64097] [--generations 3] [--scenario-proposeur muet:1] [--scenario-experimentateur arrondi:2]
"""

import argparse
import datetime
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
import time

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

from pole import a_blanc_v59 as A  # noqa: E402
from pole import tour_ferme_v62 as T  # noqa: E402
from pole.etage_entre_generations_v53 import MachineNonJetable  # noqa: E402
from pole.etage_entre_generations_v56 import exiger_machine_jetable_v56  # noqa: E402
from pole.outils import ecrire_json_scelle, sha256_fichier, verifier_scelle  # noqa: E402

ETAPE = "tour_ferme_v62"
SORTIE = "tour-ferme-v1-etage{e}.json"
DOSSIER_PREREG = os.path.join(RACINE, "prereg")
NOM_PREREG = re.compile(r"^preenregistrement-tour-ferme-v1-v[1-9][0-9]*\.md$")
DEBUT_EMPREINTES, FIN_EMPREINTES = "<!-- empreintes-du-code : début -->", "<!-- empreintes-du-code : fin -->"
DEBUT_PLAN, FIN_PLAN = "<!-- plan-gele : début -->", "<!-- plan-gele : fin -->"
DEBUT_ZONE_2, FIN_ZONE_2 = "<!-- etage-2-hors-scellement : début -->", "<!-- etage-2-hors-scellement : fin -->"
MARQUEUR = re.compile(r"<<[A-Z0-9_]+>>")
SHA = re.compile(r"^[0-9a-f]{64}$")
REGISTRE_COURSE = "registre-depense-cumulee-v1.jsonl"
MONDE_SHA256_A_BLANC = "fdf4d5c1ca0d2971b416ee5f694deff7a4696fe5defb3a6a1843dffef1231877"  # exemples/temoins-pari-demo-v1.json
# Fermeture des imports du chemin à blanc, du chemin réel et de la lecture gelée (essai `Fermeture` de essais/test_tour_ferme_v62.py).
FICHIERS_GELES = (
    "demonstrations/tour_ferme_v62.py", "demonstrations/lire_tour_ferme_v62.py", "demonstrations/attaque_goodhart_v2.py",
    "demonstrations/ideation_v2.py", "demonstrations/ideation_v4.py", "demonstrations/ideation_v5.py",
    "demonstrations/ideation_v6.py", "demonstrations/ideation_v7.py", "demonstrations/ideation_v8.py", "pole/__init__.py",
    "pole/a_blanc_v59.py", "pole/adaptateur_kimi_v53.py", "pole/adaptateurs.py", "pole/adaptateurs_v56.py",
    "pole/aiguilleur_v53.py", "pole/attaque_goodhart_v2.py", "pole/bisociateur_v53.py", "pole/bisociateur_v54.py",
    "pole/bisociateur_v55.py", "pole/boucle_fermee_v59.py", "pole/budget_v53.py", "pole/budget_v54.py", "pole/budget_v56.py",
    "pole/caviardage.py", "pole/coffre_v53.py", "pole/coffre_v55.py", "pole/configuration_v53.py", "pole/configuration_v54.py",
    "pole/configuration_v55.py", "pole/configuration_v56.py", "pole/controles_pari.py", "pole/course2_v53.py",
    "pole/course2_v54.py", "pole/course2_v55.py", "pole/course2_v56.py", "pole/cycle.py", "pole/dossier_ferme.py",
    "pole/etage_entre_generations_v53.py", "pole/etage_entre_generations_v54.py", "pole/etage_entre_generations_v55.py",
    "pole/etage_entre_generations_v56.py", "pole/etage_entre_generations_v57.py", "pole/evaluateur_lois_v62.py",
    "pole/fiche.py", "pole/fiches_v53.py", "pole/fiches_v54.py", "pole/garde_outils.py", "pole/gardes_e0_v54.py",
    "pole/gardes_e0_v55.py", "pole/gardes_e0_v56.py", "pole/graines_v53.py", "pole/ideation_v2.py",
    "pole/juges_croises_v53.py", "pole/lecture_tour_ferme_v62.py", "pole/memoire.py", "pole/memoire_v53.py",
    "pole/mesures_v54.py", "pole/moisson.py", "pole/noyau_v54.py", "pole/noyau_v55.py", "pole/noyau_v56.py",
    "pole/nul_filles_v2.py", "pole/nul_v8.py", "pole/oracle_tour_ferme_v60.py", "pole/outils.py", "pole/pari_apparie.py",
    "pole/prepilote_v54.py", "pole/prepilote_v55.py", "pole/prepilote_v56.py", "pole/proposeurs_references_v59.py",
    "pole/protocole_outils.py", "pole/relais.py", "pole/relais_reel.py", "pole/selection_pari.py", "pole/suivi_roles_v54.py",
    "pole/tableau_v53.py", "pole/tests_de_mort_v2.py", "pole/tests_de_mort_v3.py", "pole/tests_de_mort_v4.py",
    "pole/tests_de_mort_v5.py", "pole/tour_ferme_v62.py")
CLES_PLAN = {"generations_etage_1", "cartes_par_proposeur", "cartes_reference", "m_e_bh_etage_1", "plafond_etage_1_usd",
             "plafond_kimi_usd", "plafond_argon_usd", "duree_etage_1_h", "d7", "d9", "configuration_sha256", "go", "monde_sha256",
             "ordre_des_bras"}
A_BLANC = {"generations": 3, "cartes_par_proposeur": 6, "cartes_reference": 12, "m_e_bh": 19, "plafond_usd": 1e9, "duree_max_h": 24.0,
           "d7": "archive_du_bras_reel", "d9": "mecanique"}


class PreenregistrementRefuse(T.TourRefuse):
    """Mode réel : texte autre que le fichier fixé, non scellé, à marqueur restant, sans code gelé conforme ou sans plan."""


def _bloc(texte, debut, fin, nom):
    i, j = texte.find(debut), texte.find(fin)
    if i < 0 or j < i or texte.count(debut) != 1 or texte.count(fin) != 1:
        raise PreenregistrementRefuse(f"bloc « {nom} » absent ou en double dans le préenregistrement")
    return texte[i + len(debut):j]


def texte_hors_etage_2(texte):
    """Le texte sans les zones de l'étage 2 (hors de ce scellement) ; zones mal formées (ouvertes, imbriquées) → refus."""
    sortie, pos = [], 0
    while True:
        i = texte.find(DEBUT_ZONE_2, pos)
        j = texte.find(FIN_ZONE_2, pos)
        if i < 0:
            if j >= 0:
                raise PreenregistrementRefuse("zone de l'étage 2 fermée sans ouverture")
            sortie.append(texte[pos:])
            return "".join(sortie)
        if j < i:
            raise PreenregistrementRefuse("zone de l'étage 2 fermée sans ouverture")
        k = texte.find(DEBUT_ZONE_2, i + len(DEBUT_ZONE_2))
        if k >= 0 and k < j:
            raise PreenregistrementRefuse("zones de l'étage 2 imbriquées")
        sortie.append(texte[pos:i])
        pos = j + len(FIN_ZONE_2)


def lire_plan(texte):
    """Bloc `plan-gele` de l'étage 1 : lignes « clé: valeur » ; rend le plan (dict) ou lève `PreenregistrementRefuse`."""
    lignes = {}
    for l in _bloc(texte, DEBUT_PLAN, FIN_PLAN, "plan-gele").splitlines():
        m = re.match(r"^\s*([a-z0-9_]+)\s*:\s*(.+?)\s*$", l)
        if m:
            if m.group(1) in lignes:
                raise PreenregistrementRefuse(f"plan-gele : clé {m.group(1)!r} en double")
            lignes[m.group(1)] = m.group(2)
    if set(lignes) != CLES_PLAN:
        raise PreenregistrementRefuse(f"plan-gele (étage 1) : clés attendues {sorted(CLES_PLAN)}, trouvées {sorted(lignes)}")
    try:
        entiers = {k: int(lignes[k]) for k in ("generations_etage_1", "cartes_par_proposeur", "cartes_reference", "m_e_bh_etage_1")}
        reels = {k: float(lignes[k].replace(",", ".")) for k in ("plafond_etage_1_usd", "plafond_kimi_usd", "plafond_argon_usd",
                                                                 "duree_etage_1_h")}
    except ValueError:
        raise PreenregistrementRefuse("plan-gele : générations, cartes, m, plafonds et durée numériques") from None
    if entiers["generations_etage_1"] < 2 or entiers["cartes_par_proposeur"] < 1 or entiers["cartes_reference"] < 1 \
            or entiers["m_e_bh_etage_1"] < 2 * entiers["cartes_par_proposeur"] or entiers["m_e_bh_etage_1"] < entiers["cartes_reference"] \
            or any(v <= 0 for v in reels.values()):
        raise PreenregistrementRefuse("plan-gele : valeurs hors des bornes (générations ≥ 2 ; m ≥ emplacements de cartes ; "
                                      "plafonds et durée > 0)")
    if round(reels["plafond_kimi_usd"] * 100) + round(reels["plafond_argon_usd"] * 100) != round(reels["plafond_etage_1_usd"] * 100):
        raise PreenregistrementRefuse("plan-gele : parts des relais (Kimi + Argon) ≠ plafond de l'étage (au centime)")
    decisions = T.verifier_decisions({k: lignes[k] for k in ("d7", "d9")})
    for k in ("configuration_sha256", "monde_sha256"):
        if not SHA.match(lignes[k]):
            raise PreenregistrementRefuse(f"plan-gele : {k} = 64 caractères hexadécimaux")
    if not re.fullmatch(r"GO-\d{4}-\d{2}-\d{2}-\d{2}", lignes["go"]):
        raise PreenregistrementRefuse("plan-gele : go = GO-AAAA-MM-JJ-NN")
    ordre = tuple(x.strip() for x in lignes["ordre_des_bras"].split(","))
    if ordre != T.BRAS_ETAGE1:
        raise PreenregistrementRefuse(f"plan-gele : ordre_des_bras {ordre} ; le code gelé joue {T.BRAS_ETAGE1}")
    return dict(entiers, **reels, decisions=decisions, configuration_sha256=lignes["configuration_sha256"], go=lignes["go"],
                monde_sha256=lignes["monde_sha256"], ordre_des_bras=list(ordre))


def entropie_decisive(empreinte):
    """E = int(empreinte, 16), exigée ≥ 2⁶⁴ en mode réel (l'espace < 2⁶⁴ est celui du mode à blanc)."""
    e = int(empreinte, 16)
    if e < 2 ** 64:
        raise PreenregistrementRefuse("entropie décisive < 2^64 : espace réservé au mode à blanc")
    return e


def lire_preenregistrement(chemin, dossier_prereg=None):
    """Garde 6 : le texte au chemin fixé, scellé, sans « brouillon », sans marqueur hors des zones de l'étage 2, gelant
    exactement le code présent, plan de l'étage 1 conforme, entropie ≥ 2⁶⁴ ; rend (entropie, empreinte, empreintes, plan).
    `dossier_prereg` : essais seulement (le lanceur ne le passe jamais : `prereg/` du dépôt)."""
    reel, dossier = os.path.realpath(chemin), os.path.realpath(dossier_prereg or DOSSIER_PREREG)
    if os.path.dirname(reel) != dossier or not NOM_PREREG.match(os.path.basename(reel)) or "brouillon" in os.path.basename(reel):
        raise PreenregistrementRefuse(f"mode réel : le préenregistrement est prereg/preenregistrement-tour-ferme-v1-v<N>.md, pas {chemin}")
    if not os.path.isfile(reel):
        raise PreenregistrementRefuse(f"préenregistrement introuvable : {chemin}")
    if not verifier_scelle(reel):
        raise PreenregistrementRefuse(f"préenregistrement non scellé (compagnon .sha256 absent ou non conforme) : {chemin}")
    with open(reel, encoding="utf-8") as f:
        texte = f.read()
    hors_zone = texte_hors_etage_2(texte)
    restants = sorted(set(MARQUEUR.findall(hors_zone)))
    if restants:
        raise PreenregistrementRefuse(f"marqueur(s) non rempli(s) hors de l'étage 2 : {restants} (décision de Lazar ou case à porter)")
    gelees = re.findall(r"^([0-9a-f]{64})  (\S+)$", _bloc(hors_zone, DEBUT_EMPREINTES, FIN_EMPREINTES, "empreintes-du-code"), re.M)
    noms = [r for _, r in gelees]
    if sorted(noms) != sorted(FICHIERS_GELES) or len(set(noms)) != len(noms):
        raise PreenregistrementRefuse(f"code gelé ≠ fermeture : manquants {sorted(set(FICHIERS_GELES) - set(noms))}, "
                                      f"en trop {sorted(set(noms) - set(FICHIERS_GELES))}")
    ecarts = []
    for attendue, relatif in gelees:
        p = os.path.join(RACINE, relatif)
        presente = sha256_fichier(p) if os.path.isfile(p) else "absent"
        if presente != attendue:
            ecarts.append(f"{relatif} : gelé {attendue[:12]}…, présent {presente[:12]}…")
    if ecarts:
        raise PreenregistrementRefuse("code différent du code gelé : " + " ; ".join(ecarts))
    plan = lire_plan(hors_zone)
    empreinte = sha256_fichier(reel)
    return entropie_decisive(empreinte), empreinte, dict((r, h) for h, r in gelees), plan


def verifier_monde(monde, sha_attendue):
    """C20 : le monde planté chargé a l'empreinte gelée (plan en mode réel ; constante du lanceur à blanc)."""
    if monde.get("sha256") != sha_attendue:
        raise T.TourRefuse(f"monde planté d'empreinte {str(monde.get('sha256'))[:12]}… ≠ empreinte gelée {sha_attendue[:12]}…")
    return True


def exiger_machine_jetable_reel(environnement, conf):
    """Garde 15 (C11) : en mode réel, l'environnement **du processus** et la liste permise de la configuration
    (`etage_tests_de_mort.environnement_permis`) ; refus avant tout appel. Rend la liste permise, passée à l'étage."""
    permis = tuple(((conf or {}).get("etage_tests_de_mort") or {}).get("environnement_permis") or ())
    try:
        exiger_machine_jetable_v56(environnement, permis_en_plus=permis)
    except MachineNonJetable as x:
        raise T.TourRefuse(f"machine jetable (garde 15) : {x}") from None
    return permis


def moteur_de_l_etage(reel):
    """C21 : « claude-sdk » en mode réel (coûts réels au manifeste de l'étage, exécuteur factice refusé par l'étage) ; « simule »
    à blanc. Le mot est celui de l'étage v5 ; les modèles sont Kimi et Argon par leurs relais."""
    return "claude-sdk" if reel else "simule"


def charger_goodhart_v2():
    spec = importlib.util.spec_from_file_location("attaque_goodhart_v2_pour_tour_ferme_v62", os.path.join(ICI, "attaque_goodhart_v2.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def roles_reels(conf, plan, base_sessions, sortie, transmettre=True):
    """Adaptateurs du chemin réel : proposeurs Kimi et Argon (`ProposeurAdaptateur`), étage `AdaptateurEtageV62`
    (expérimentateur Kimi, vérificateur Argon) ; porte de chaque relais à sa part du plan (C13)."""
    from pole.relais import noms_de_cle_presents
    presents = noms_de_cle_presents(os.environ)
    if presents:
        raise T.TourRefuse(f"variables de clé dans l'environnement de l'orchestrateur ({', '.join(presents)}) : les relais tiennent les clés")
    g2 = charger_goodhart_v2()
    budget, modeles = g2.reglages_de_configuration(conf)
    if float((conf.get("budget") or {}).get("plafond_usd") or 0) != float(plan["plafond_usd"]):
        raise T.TourRefuse(f"configuration : budget.plafond_usd = {(conf.get('budget') or {}).get('plafond_usd')!r} ≠ plafond de "
                           f"l'étage 1 ({plan['plafond_usd']} USD) : demander une configuration à empreinte neuve")
    conf2, substitutions = g2.substituer_commandes(conf, os.path.join(os.path.abspath(sortie), REGISTRE_COURSE), plan["plafond_usd"])
    v8 = g2.charger_ideation_v8()
    adaptateurs, portes = v8.adaptateurs_reels_v56(conf2, sortie, base_sessions)
    if sorted(n for n in adaptateurs if n in ("kimi", "argon")) != ["argon", "kimi"]:
        raise T.TourRefuse(f"configuration : adaptateurs « kimi » et « argon » exigés, trouvés {sorted(adaptateurs)}")
    accuses = {n: portes[n].transmettre(ETAPE, plan["parts"][n]) for n in ("kimi", "argon")} if transmettre else "non relancées (vérification seule)"
    proposeurs = [T.ProposeurAdaptateur(n, n, adaptateurs[n], os.path.join(base_sessions, "proposeur-" + n), budget, modeles[n])
                  for n in ("kimi", "argon")]
    etage = T.AdaptateurEtageV62(adaptateurs["kimi"], adaptateurs["argon"], "kimi", "argon")
    roles = {"experimentateur": ("experimentateur-kimi", modeles["kimi"]), "verificateur": ("verificateur-argon", modeles["argon"]),
             "familles": {"experimentateur": "kimi", "verificateur": "argon"}, "relais": {"experimentateur": "kimi", "verificateur": "argon"}}
    infos = {"budget_appel_usd": budget, "modeles_demandes": modeles, "substitutions_dans_les_commandes": substitutions,
             "accuses_plafond": accuses, "parts_des_relais_usd": plan["parts"], "portes": {n: portes[n].description() for n in ("kimi", "argon")}}
    return proposeurs, etage, roles, infos


def roles_a_blanc(args, sortie):
    """Doublures scriptées **branchées sur le chemin réel** (mêmes classes : `ProposeurAdaptateur`, `AdaptateurEtageV62`)."""
    cout = args.cout_simule_usd or 0.0
    proposeurs = [T.ProposeurAdaptateur("kimi-scripte", "kimi", T.AdaptateurProposeurScripte("kimi-scripte", 0.4, args.scenario_proposeur, cout),
                                        os.path.join(sortie, "proposeurs", "kimi-scripte"), 0.0, "doublure-kimi"),
                  T.ProposeurAdaptateur("argon-scripte", "argon", T.AdaptateurProposeurScripte("argon-scripte", 0.8, args.scenario_proposeur, cout),
                                        os.path.join(sortie, "proposeurs", "argon-scripte"), 0.0, "doublure-argon")]
    cout_e = args.cout_simule_etage_usd or 0.0
    etage = T.AdaptateurEtageV62(T.AdaptateurExperimentateurScripte(args.scenario_experimentateur, cout_e),
                                 T.AdaptateurVerificateurScripte(cout_e), "kimi", "argon")
    fam = args.familles_a_blanc or "a,b"
    fa, fb = (fam.split(",") + [""])[:2]
    roles = {"experimentateur": ("experimentateur-scripte", "famille-" + fa), "verificateur": ("verificateur-scripte", "famille-" + fb),
             "familles": {"experimentateur": fa, "verificateur": fb}, "relais": {"experimentateur": "kimi", "verificateur": "argon"}}
    return proposeurs, etage, roles


def preparer_bac(bac, utilisateur_bac):
    parent, racine_travail = None, None
    if bac == "reel" and os.geteuid() == 0 and utilisateur_bac is not None:
        parent = os.path.realpath(tempfile.mkdtemp(prefix="bac-tour-ferme-v62-"))
        os.chmod(parent, 0o711)
        racine_travail = os.path.join(parent, "bac")
        os.mkdir(racine_travail, 0o700)
        os.chown(racine_travail, int(utilisateur_bac), int(utilisateur_bac))
    A.choisir_executeur(bac, utilisateur_bac=utilisateur_bac, racine_travail=racine_travail)  # refus avant tout (garde 3)
    return parent, (lambda: A.choisir_executeur(bac, utilisateur_bac=utilisateur_bac, racine_travail=racine_travail))


def principal(argv=None):
    a = argparse.ArgumentParser(description="tour fermé (v62) : étage 1 seul (monde planté, trois bras)")
    a.add_argument("sortie")
    a.add_argument("--etage", type=int, choices=(1, 2), required=True)
    g = a.add_mutually_exclusive_group(required=True)
    g.add_argument("--a-blanc", action="store_true")
    g.add_argument("--preenregistrement")
    a.add_argument("--graine", type=int)
    a.add_argument("--configuration")
    a.add_argument("--moteur", choices=("reel",))
    a.add_argument("--confirmer-moteur-reel", action="store_true")
    a.add_argument("--registre-go")
    a.add_argument("--go")
    a.add_argument("--bac", choices=("reel", "factice"), required=True, help="aucun défaut ; « reel » refuse sans bwrap")
    a.add_argument("--utilisateur-bac", type=int)
    a.add_argument("--verifier-seulement", action="store_true")
    # options du mode à blanc seulement
    for o, t in (("--generations", int), ("--cartes-par-proposeur", int), ("--cartes-reference", int), ("--m-e-bh", int),
                 ("--plafond-usd", float), ("--plafond-kimi-usd", float), ("--plafond-argon-usd", float), ("--duree-max-h", float),
                 ("--cout-simule-usd", float), ("--cout-simule-etage-usd", float)):
        a.add_argument(o, type=t)
    a.add_argument("--d7", choices=T.DECISIONS["d7"])
    a.add_argument("--d9", choices=T.DECISIONS["d9"])
    a.add_argument("--scenario-proposeur")
    a.add_argument("--scenario-experimentateur")
    a.add_argument("--familles-a-blanc", help="« a,b » (défaut) ; « a,a » = artefact de la garde 9")
    args = a.parse_args(argv)
    noms_options = ("generations", "cartes_par_proposeur", "cartes_reference", "m_e_bh", "plafond_usd", "plafond_kimi_usd",
                    "plafond_argon_usd", "duree_max_h", "d7", "d9", "scenario_proposeur", "scenario_experimentateur", "familles_a_blanc",
                    "cout_simule_usd", "cout_simule_etage_usd")
    options_plan = {k: getattr(args, k) for k in noms_options if getattr(args, k) is not None}
    base_sessions, parent_bac, reel = None, None, not args.a_blanc
    from pole import configuration_v56 as cfg
    try:
        if os.path.exists(args.sortie) and os.listdir(args.sortie):
            raise FileExistsError(f"dossier de sortie non vide : {args.sortie} (on n'écrase jamais)")
        if args.etage != 1:
            raise T.TourRefuse("aucun étage 2 sous ce texte (étage 1 seul) : refus avant tout appel")
        if args.bac == "factice" and reel:
            raise T.TourRefuse("mode réel : bac « reel » exigé (aucune barrière avec l'exécuteur factice)")
        monde = A.charger_monde(RACINE)
        environnement, permis = dict(T.ENV_A_BLANC), ()
        if args.a_blanc:
            if args.graine is None or args.moteur or args.configuration or args.go or args.verifier_seulement:
                raise T.TourRefuse("à blanc : --graine G seulement (ni moteur réel, ni configuration, ni GO)")
            if not 0 <= args.graine < 2 ** 64:
                raise T.TourRefuse("à blanc : graine dans [0 ; 2^64[ (l'espace ≥ 2^64 est celui des textes scellés)")
            verifier_monde(monde, MONDE_SHA256_A_BLANC)
            r = dict(A_BLANC, **{k: v for k, v in options_plan.items() if k in A_BLANC})
            parts = {k: v for k, v in (("kimi", args.plafond_kimi_usd), ("argon", args.plafond_argon_usd)) if v is not None}
            plan = {"generations": r["generations"], "cartes_par_proposeur": r["cartes_par_proposeur"], "cartes_reference": r["cartes_reference"],
                    "m_e_bh": r["m_e_bh"], "plafond_usd": r["plafond_usd"], "duree_max_s": r["duree_max_h"] * 3600.0, "parts": parts}
            decisions = T.verifier_decisions({k: r[k] for k in ("d7", "d9")})
            entropie, mode, preenregistrement, conf_info = args.graine, "a-blanc (exploratoire)", None, None
            proposeurs, adaptateur, roles = roles_a_blanc(args, args.sortie)
        else:
            if args.graine is not None or options_plan:
                raise T.TourRefuse(f"mode réel : le plan est lu dans le texte scellé ; options refusées : {sorted(options_plan) or ['--graine']}")
            if args.moteur != "reel" or not args.confirmer_moteur_reel or not args.configuration:
                raise T.TourRefuse("mode réel : --configuration, --moteur reel et --confirmer-moteur-reel exigés")
            entropie, empreinte, gelees, p = lire_preenregistrement(args.preenregistrement)
            verifier_monde(monde, p["monde_sha256"])
            plan = {"generations": p["generations_etage_1"], "cartes_par_proposeur": p["cartes_par_proposeur"],
                    "cartes_reference": p["cartes_reference"], "m_e_bh": p["m_e_bh_etage_1"], "plafond_usd": p["plafond_etage_1_usd"],
                    "duree_max_s": p["duree_etage_1_h"] * 3600.0, "parts": {"kimi": p["plafond_kimi_usd"], "argon": p["plafond_argon_usd"]}}
            decisions = p["decisions"]
            if not os.path.isfile(args.configuration):
                raise T.TourRefuse(f"configuration introuvable : {args.configuration}")
            sha_conf = sha256_fichier(args.configuration)
            if sha_conf != p["configuration_sha256"]:
                raise T.TourRefuse(f"configuration d'empreinte {sha_conf[:12]}… : le texte scellé gèle {p['configuration_sha256'][:12]}…")
            if not args.registre_go or args.go != p["go"]:
                raise T.TourRefuse(f"mode réel : --registre-go et --go {p['go']} (celui du texte scellé) exigés")
            try:
                go = cfg.verifier_go_v56(args.go, args.registre_go, plan["plafond_usd"])
            except cfg.GoRefuse as x:
                raise T.TourRefuse(str(x)) from None
            conf = cfg.lire_configuration_v56(args.configuration)
            environnement = os.environ  # C11 : l'environnement du processus, jamais une déclaration constante
            permis = exiger_machine_jetable_reel(environnement, conf)
            base_sessions = tempfile.mkdtemp(prefix="tour-ferme-v62-sessions-")
            proposeurs, adaptateur, roles, infos = roles_reels(conf, plan, base_sessions, os.path.abspath(args.sortie),
                                                               transmettre=not args.verifier_seulement)
            mode = "reel (decisif)"
            preenregistrement = {"chemin": os.path.relpath(os.path.realpath(args.preenregistrement), RACINE), "sha256": empreinte,
                                 "empreintes_du_code_verifiees": gelees, "plan": p, "go": go}
            conf_info = dict(infos, chemin=os.path.abspath(args.configuration), sha256=sha_conf, environnement_permis=list(permis))
        moteur = moteur_de_l_etage(reel)
        T.exiger_familles_separees((roles["experimentateur"][0], roles["familles"]["experimentateur"]),
                                   (roles["verificateur"][0], roles["familles"]["verificateur"]))
        parent_bac, fabrique = preparer_bac(args.bac, args.utilisateur_bac)
        if args.verifier_seulement:
            print(json.dumps({"verification": "conforme", "ecriture": "aucune", "appel": "aucun", "portes": "non relancées",
                              "plan": plan, "decisions": decisions, "configuration": conf_info}, ensure_ascii=False, indent=1, default=str))
            return 0
    except Exception as x:  # noqa: BLE001 — refus nommé avant tout appel, jamais de repli
        print(f"refus : {type(x).__name__} : {x}", file=sys.stderr)
        return 2
    finally:
        if args.verifier_seulement:
            if parent_bac:
                shutil.rmtree(parent_bac, True)
            if base_sessions:
                shutil.rmtree(base_sessions, True)
    os.makedirs(args.sortie, exist_ok=True)
    m = T.manifeste_tour(etape=ETAPE, mode=mode, etage=1, entropie_racine=str(entropie), plan=plan, decisions=decisions,
                         preenregistrement=preenregistrement, configuration=conf_info, bac=args.bac, moteur_etage=moteur,
                         environnement_etage=sorted(environnement), monde={k: monde[k] for k in ("source", "sha256", "loi_vraie")},
                         roles={k: v for k, v in roles.items()}, options_a_blanc=options_plan if args.a_blanc else None,
                         code_sha256={r: sha256_fichier(os.path.join(RACINE, r)) for r in FICHIERS_GELES},
                         debut_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"))
    ecrire_json_scelle(os.path.join(args.sortie, "manifeste.json"), m)
    compteur = T.Compteur(plan["plafond_usd"], plan["duree_max_s"], plan.get("parts"), time.time)
    try:
        try:
            releve, journal = T.jouer_etage_1(args.sortie, monde=monde, racine=entropie, plan=plan, decisions=decisions,
                                              proposeurs=proposeurs, adaptateur_etage=adaptateur, roles=roles, fabrique_executeur=fabrique,
                                              compteur=compteur, moteur=moteur, environnement=environnement, permis_en_plus=permis)
        except Exception as x:  # noqa: BLE001 — C12 : toute exception après le manifeste est un arrêt scellé (code 3)
            partiel = getattr(x, "partiel", {}) or {}
            rel = partiel.get("releve") or {"version": T.VERSION, "etage": 1, "arret": f"{type(x).__name__} : {x}", "cartes": [],
                                            "generations_jouees": {b: [] for b in T.BRAS_ETAGE1}, "boucle": {"incidents": [], "lectures": []},
                                            "plan": plan, "recherche_loi_plantee": None}
            rapport = {"version": T.VERSION, "mode": mode, "arret": f"{type(x).__name__} : {x}", "releve": rel,
                       "journal": partiel.get("journal", []), "depense": compteur.etat(), "preenregistrement": preenregistrement,
                       "appels_proposeurs": [p.appels for p in proposeurs], "appels_etage": list(getattr(adaptateur, "appels", [])),
                       "issue": "non jugeable (arrêt) : aucune issue lue",
                       "fin_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
            ecrire_json_scelle(os.path.join(args.sortie, SORTIE.format(e=1)), rapport)
            print(json.dumps({"mode": mode, "arret": rapport["arret"], "depense": compteur.etat()}, ensure_ascii=False), file=sys.stderr)
            return 3
    finally:
        if parent_bac:
            shutil.rmtree(parent_bac, True)
    rapport = {"version": T.VERSION, "mode": mode, "preenregistrement": preenregistrement, "releve": releve, "journal": journal,
               "depense": compteur.etat(), "appels_proposeurs": [p.appels for p in proposeurs],
               "appels_etage": list(getattr(adaptateur, "appels", [])),
               "fin_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
    sha = ecrire_json_scelle(os.path.join(args.sortie, SORTIE.format(e=1)), rapport)
    print(json.dumps({"mode": mode, "releve_sha256": sha, "generations_jouees": releve["generations_jouees"], "cartes": len(releve["cartes"]),
                      "depense": compteur.etat(), "lecture": "aucune (la lecture gelée est un autre programme)"}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(principal())
