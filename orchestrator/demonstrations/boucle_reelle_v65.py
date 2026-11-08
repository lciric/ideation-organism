"""Lanceur de la plus petite course réelle de la boucle complète de l'organisme, version 65 (fichier neuf, R12) — bras réel seul,
deux générations. Cœur : `pole/boucle_reelle_v65.py` ; lecture gelée (programme à part) : `demonstrations/lire_boucle_reelle_v65.py`,
`pole/lecture_boucle_reelle_v65.py`. Dessin : brouillon 1 du préenregistrement de la course (dépôt de travail,
`docs/notes/organisme-boucle-reelle-v1/`, sha256 736e3fd6…) ; décision du directeur GO-2026-11-08-02.

Deux modes, exclusifs, qui passent par **le même chemin** (proposeurs `ProposeurAdaptateur`, étage `AdaptateurEtageV64` de la v64) :
- **à blanc** (`--a-blanc --graine G`, G < 2⁶⁴) : doublures scriptées de la v64 (proposeurs, expérimentateur, vérificateur) qui ne
  lisent que le texte servi ; aucun réseau, aucune clé. Le plan, l'empreinte de l'héritage de départ et le jeu planté sont lus dans
  un texte (`--texte`, par défaut `exemples/plan-et-jeu-a-blanc-boucle-reelle-v65.md`, non scellé : exploratoire), par les mêmes
  fonctions que le mode réel ; options d'essai permises (cartes par proposeur, parts, coûts simulés, scénarios, bras, héritage) ;
- **réel** (`--preenregistrement P --configuration CONF --moteur reel --confirmer-moteur-reel --registre-go R --go ID --bac reel
  --utilisateur-bac U`) : le texte scellé `prereg/preenregistrement-boucle-reelle-organisme-v1-v<N>.md` (sceau compagnon, nom sans
  « brouillon », aucun marqueur `<<…>>`, code gelé égal au code présent, plan conforme, entropie ≥ 2⁶⁴) porte le plan, les empreintes
  de la configuration v5, de l'héritage de départ et du jeu planté, le GO ; l'héritage de départ est le fichier fixe
  `exemples/heritage-depart-boucle-reelle-v65.json` ; aucune option de plan.

Gardes avant tout appel (code 2) : dossier de sortie non vide ; bac sans défaut (« reel » exige `bwrap` ≥ 0.9, sonde réussie et, en
mode réel, un utilisateur dédié sans privilège : garde 22) ; bac factice en mode réel ; monde d'une autre empreinte ; plan hors
bornes ; bras autre que le bras réel seul (garde 20) ; héritage de départ d'une autre empreinte que celle du texte, altéré, ou
portant une loi plantée (garde 17) ; jeu planté absent, incomplet, non canonique, d'une autre empreinte, à fausse hors de la classe
couverte (M2, garde 19) ; mode réel : texte non conforme (garde 6), configuration d'une autre empreinte ou d'autres plafonds, commandes
v6 absentes ou d'une autre empreinte que celle que la configuration nomme, GO absent, révoqué ou d'un autre montant que plafond des
modèles + plafond de la machine (45 USD), variable de clé, machine non jetable, adaptateur qui ne joue pas son rôle.
Codes : 0 relevé écrit (le code ne décide rien) ; 2 refus ; 3 arrêt (toute exception après le manifeste : relevé partiel scellé).

Usage à blanc : python3 -I -B demonstrations/boucle_reelle_v65.py SORTIE_NEUVE --a-blanc --graine 7 --bac factice
                [--texte T] [--heritage-depart H] [--bras reel_seul] [--cartes-par-proposeur N] [--plafond-kimi-usd P]
                [--plafond-argon-usd P] [--cout-simule-usd C] [--cout-simule-etage-usd C] [--scenario-proposeur S] …
"""

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

from pole import a_blanc_v59 as A  # noqa: E402
from pole import adaptateur_commande_v64 as AC  # noqa: E402
from pole import boucle_reelle_v65 as B  # noqa: E402
from pole import tour_ferme_v64 as T  # noqa: E402
from pole.etage_entre_generations_v53 import MachineNonJetable  # noqa: E402
from pole.etage_entre_generations_v56 import exiger_machine_jetable_v56  # noqa: E402
from pole.outils import ecrire_json_scelle, sha256_fichier, verifier_scelle  # noqa: E402

ETAPE = "boucle_reelle_v65"
SORTIE = "boucle-reelle-v65.json"
DOSSIER_PREREG = os.path.join(RACINE, "prereg")
NOM_PREREG = re.compile(r"^preenregistrement-boucle-reelle-organisme-v1-v[1-9][0-9]*\.md$")
DEBUT_EMPREINTES, FIN_EMPREINTES = "<!-- empreintes-du-code-v65 : début -->", "<!-- empreintes-du-code-v65 : fin -->"
MARQUEUR = re.compile(r"<<[A-Z0-9_-]+>>")
REGISTRE_COURSE = "registre-depense-cumulee-v1.jsonl"
MONDE_SHA256 = "fdf4d5c1ca0d2971b416ee5f694deff7a4696fe5defb3a6a1843dffef1231877"  # exemples/temoins-pari-demo-v1.json (monde S-V1)
HERITAGE_DEPART = os.path.join(RACINE, "exemples", "heritage-depart-boucle-reelle-v65.json")
TEXTE_A_BLANC = os.path.join(RACINE, "exemples", "plan-et-jeu-a-blanc-boucle-reelle-v65.md")
SECTION_CONFIGURATION = "boucle_reelle_v65"
VERSION_BWRAP_MIN = (0, 9)
# Bloc gelé : fermeture statique des imports des deux programmes v65 (arbre syntaxique, imports tardifs et fichiers chargés par
# chemin compris ; essai `FermetureV65` : égalité exacte) — 93 fichiers : les 92 de la v64, moins ses deux programmes et sa lecture
# gelée v63, plus les deux programmes v65, `pole/boucle_reelle_v65.py` et `pole/lecture_boucle_reelle_v65.py`.
FICHIERS_GELES = (
    "demonstrations/attaque_goodhart_v2.py", "demonstrations/boucle_reelle_v65.py", "demonstrations/ideation_v2.py",
    "demonstrations/ideation_v4.py", "demonstrations/ideation_v5.py", "demonstrations/ideation_v6.py",
    "demonstrations/ideation_v7.py", "demonstrations/ideation_v8.py", "demonstrations/lire_boucle_reelle_v65.py",
    "pole/__init__.py", "pole/a_blanc_v59.py", "pole/adaptateur_commande_v64.py", "pole/adaptateur_kimi_v53.py",
    "pole/adaptateurs.py", "pole/adaptateurs_v56.py", "pole/aiguilleur_v53.py", "pole/attaque_goodhart_v2.py",
    "pole/bisociateur_v53.py", "pole/bisociateur_v54.py", "pole/bisociateur_v55.py", "pole/boucle_fermee_v59.py",
    "pole/boucle_reelle_v65.py", "pole/bras_attaque_v54.py", "pole/budget_v53.py", "pole/budget_v54.py", "pole/budget_v56.py",
    "pole/caviardage.py", "pole/coffre_v53.py", "pole/coffre_v55.py", "pole/configuration_v53.py", "pole/configuration_v54.py",
    "pole/configuration_v55.py", "pole/configuration_v56.py", "pole/controles_pari.py", "pole/course2_v53.py",
    "pole/course2_v54.py", "pole/course2_v55.py", "pole/course2_v56.py", "pole/cycle.py", "pole/dossier_ferme.py",
    "pole/etage_entre_generations_v53.py", "pole/etage_entre_generations_v54.py", "pole/etage_entre_generations_v55.py",
    "pole/etage_entre_generations_v56.py", "pole/etage_entre_generations_v57.py", "pole/evaluateur_lois_v62.py", "pole/fiche.py",
    "pole/fiches_v53.py", "pole/fiches_v54.py", "pole/garde_outils.py", "pole/gardes_e0_v54.py", "pole/gardes_e0_v55.py",
    "pole/gardes_e0_v56.py", "pole/graines_v53.py", "pole/ideation.py", "pole/ideation_v2.py", "pole/juges_croises_v53.py",
    "pole/lecture_boucle_reelle_v65.py", "pole/memoire.py", "pole/memoire_v53.py", "pole/mesures_v54.py", "pole/moisson.py",
    "pole/monde_banque.py", "pole/monde_noyau.py", "pole/noyau_v54.py", "pole/noyau_v55.py", "pole/noyau_v56.py",
    "pole/nul_filles_v2.py", "pole/nul_v8.py", "pole/oracle_tour_ferme_v60.py", "pole/outils.py", "pole/pari_apparie.py",
    "pole/prepilote_v54.py", "pole/prepilote_v55.py", "pole/prepilote_v56.py", "pole/proposeurs_references_v59.py",
    "pole/protocole_outils.py", "pole/relais.py", "pole/relais_reel.py", "pole/selection_pari.py", "pole/simulation.py",
    "pole/simulation_v53.py", "pole/simulation_v54.py", "pole/simulation_v55.py", "pole/simulation_v56.py",
    "pole/suivi_roles_v54.py", "pole/tableau_v53.py", "pole/tests_de_mort.py", "pole/tests_de_mort_v2.py",
    "pole/tests_de_mort_v3.py", "pole/tests_de_mort_v4.py", "pole/tests_de_mort_v5.py", "pole/tour_ferme_v64.py",)


class PreenregistrementRefuse(B.BoucleRefusee):
    """Mode réel : texte autre que le fichier fixé, non scellé, à marqueur restant, sans code gelé conforme ou sans plan."""


def entropie_decisive(empreinte):
    e = int(empreinte, 16)
    if e < 2 ** 64:
        raise PreenregistrementRefuse("entropie décisive < 2^64 : espace réservé au mode à blanc")
    return e


def lire_preenregistrement(chemin, dossier_prereg=None):
    """Garde 6 (v65) : le texte au chemin fixé, scellé, sans « brouillon », sans aucun marqueur, gelant exactement le code présent,
    plan v65 conforme, entropie ≥ 2⁶⁴ ; rend (entropie, empreinte, empreintes du code, plan, texte)."""
    reel, dossier = os.path.realpath(chemin), os.path.realpath(dossier_prereg or DOSSIER_PREREG)
    if os.path.dirname(reel) != dossier or not NOM_PREREG.match(os.path.basename(reel)) or "brouillon" in os.path.basename(reel):
        raise PreenregistrementRefuse(f"mode réel : le texte est prereg/preenregistrement-boucle-reelle-organisme-v1-v<N>.md, pas {chemin}")
    if not os.path.isfile(reel):
        raise PreenregistrementRefuse(f"préenregistrement introuvable : {chemin}")
    if not verifier_scelle(reel):
        raise PreenregistrementRefuse(f"préenregistrement non scellé (compagnon .sha256 absent ou non conforme) : {chemin}")
    with open(reel, encoding="utf-8") as f:
        texte = f.read()
    restants = sorted(set(MARQUEUR.findall(texte)))
    if restants:
        raise PreenregistrementRefuse(f"marqueur(s) non rempli(s) : {restants}")
    gelees = re.findall(r"^([0-9a-f]{64})  (\S+)$", B.bloc_unique(texte, DEBUT_EMPREINTES, FIN_EMPREINTES, "empreintes-du-code-v65",
                                                                  PreenregistrementRefuse), re.M)
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
    plan = B.lire_plan(texte)
    empreinte = sha256_fichier(reel)
    return entropie_decisive(empreinte), empreinte, dict((r, h) for h, r in gelees), plan, texte


def verifier_monde(monde, sha_attendue):
    if monde.get("sha256") != sha_attendue:
        raise B.BoucleRefusee(f"monde planté d'empreinte {str(monde.get('sha256'))[:12]}… ≠ empreinte gelée {sha_attendue[:12]}…")
    return True


def exiger_configuration_v65(conf, plan):
    """La section `boucle_reelle_v65` de la configuration v5 : plafonds égaux au plan (modèles, parts, machine), GO du plan, et les
    deux commandes v6 **nommées** avec leurs empreintes ; chaque commande de `fournisseurs` porte ce chemin, le fichier existe et a
    cette empreinte (rien n'est lancé ici). Rend la section ; lève `BoucleRefusee` (code 2)."""
    s = (conf or {}).get(SECTION_CONFIGURATION)
    if not isinstance(s, dict):
        raise B.BoucleRefusee(f"configuration : section « {SECTION_CONFIGURATION} » absente")
    attendus = {"plafond_modeles_usd": plan["plafond_modeles_usd"], "plafond_machine_usd": plan["plafond_machine_usd"]}
    for k, v in attendus.items():
        if not isinstance(s.get(k), (int, float)) or abs(float(s[k]) - float(v)) > 1e-9:
            raise B.BoucleRefusee(f"configuration : {SECTION_CONFIGURATION}.{k} = {s.get(k)!r} ≠ plan ({v})")
    parts = s.get("parts_usd") or {}
    if set(parts) != {"kimi", "argon"} or any(abs(float(parts[n]) - float(plan[f"plafond_{n}_usd"])) > 1e-9 for n in parts):
        raise B.BoucleRefusee(f"configuration : {SECTION_CONFIGURATION}.parts_usd = {parts!r} ≠ parts du plan")
    if s.get("go") != plan["go"]:
        raise B.BoucleRefusee(f"configuration : {SECTION_CONFIGURATION}.go = {s.get('go')!r} ≠ GO du plan ({plan['go']})")
    if float((conf.get("budget") or {}).get("plafond_usd") or 0) != float(plan["plafond_modeles_usd"]):
        raise B.BoucleRefusee("configuration : budget.plafond_usd ≠ plafond des modèles du plan")
    commandes = s.get("commandes") or {}
    if set(commandes) != {"kimi", "argon"}:
        raise B.BoucleRefusee("configuration : commandes v6 de kimi et d'argon nommées exigées")
    for n, c in sorted(commandes.items()):
        if not isinstance(c, dict) or not isinstance(c.get("chemin"), str) or not B.SHA.match(str(c.get("sha256"))):
            raise B.BoucleRefusee(f"configuration : commande {n} = {{chemin, sha256}} exigés")
        liste = ((conf.get("fournisseurs") or {}).get(n) or {}).get("commande") or []
        if c["chemin"] not in liste:
            raise B.BoucleRefusee(f"configuration : la commande du relais {n} ne lance pas le fichier nommé {c['chemin']}")
        if not os.path.isfile(c["chemin"]):
            raise B.BoucleRefusee(f"commande v6 du relais {n} absente de cette machine : {c['chemin']} (pièce M6 à verser)")
        if sha256_fichier(c["chemin"]) != c["sha256"]:
            raise B.BoucleRefusee(f"commande v6 du relais {n} d'empreinte {sha256_fichier(c['chemin'])[:12]}… ≠ empreinte nommée {c['sha256'][:12]}…")
    dep = s.get("dependance_des_commandes")
    if not isinstance(dep, dict) or not isinstance(dep.get("chemin"), str) or not B.SHA.match(str(dep.get("sha256"))) \
            or not os.path.isfile(dep["chemin"]) or sha256_fichier(dep["chemin"]) != dep["sha256"]:
        raise B.BoucleRefusee(f"configuration : dépendance des commandes (registre de dépense cumulée) absente ou d'une autre empreinte : {dep!r}")
    return s


def version_bwrap(which=shutil.which):
    """La version de `bwrap` (tuple d'entiers) ou None si absent ou illisible."""
    if not which("bwrap"):
        return None
    try:
        out = subprocess.run(["bwrap", "--version"], capture_output=True, text=True, timeout=10).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    m = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?", out or "")
    return tuple(int(x) for x in m.groups() if x is not None) if m else None


def exiger_machine_du_bac(bac, reel, utilisateur_bac, version):
    """Garde 22 : bac « reel » → `bwrap` ≥ 0.9 et, en mode réel, un utilisateur dédié sans privilège (identité > 0) ; la sonde
    vient ensuite (`a_blanc_v59.choisir_executeur`, garde 3). Mode réel avec bac factice : refus. Lève `BoucleRefusee` (code 2)."""
    if bac == "factice":
        if reel:
            raise B.BoucleRefusee("mode réel : bac « reel » exigé (aucune barrière avec l'exécuteur factice)")
        return None
    if version is None:
        raise A.BacASableIndisponible("bac réel demandé : bwrap absent de cette machine : refus, aucun repli sur l'exécuteur factice")
    if tuple(version[:2]) < VERSION_BWRAP_MIN:
        raise B.BoucleRefusee(f"bwrap {'.'.join(map(str, version))} < 0.9 : refus (garde 22)")
    if reel and (utilisateur_bac is None or int(utilisateur_bac) <= 0):
        raise B.BoucleRefusee("mode réel : utilisateur dédié sans privilège exigé (--utilisateur-bac, identité > 0) (garde 22)")
    return version


def preparer_bac(bac, utilisateur_bac):
    """Dossier du bac (identité dédiée) puis sonde (garde 3) ; un refus ne laisse aucun dossier (mineur 34)."""
    parent, racine_travail = None, None
    try:
        if bac == "reel" and os.geteuid() == 0 and utilisateur_bac is not None:
            parent = os.path.realpath(tempfile.mkdtemp(prefix="bac-boucle-reelle-v65-"))
            os.chmod(parent, 0o711)
            racine_travail = os.path.join(parent, "bac")
            os.mkdir(racine_travail, 0o700)
            os.chown(racine_travail, int(utilisateur_bac), int(utilisateur_bac))
        A.choisir_executeur(bac, utilisateur_bac=utilisateur_bac, racine_travail=racine_travail)
    except BaseException:
        if parent:
            shutil.rmtree(parent, True)
        raise
    return parent, (lambda: A.choisir_executeur(bac, utilisateur_bac=utilisateur_bac, racine_travail=racine_travail))


def charger_goodhart_v2():
    import importlib.util
    spec = importlib.util.spec_from_file_location("attaque_goodhart_v2_pour_boucle_reelle_v65", os.path.join(ICI, "attaque_goodhart_v2.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def roles_reels(conf, plan, base_sessions, sortie, go, compteur, transmettre=True):
    """Adaptateurs du chemin réel (ceux de la v64 : `ideation_v8.adaptateurs_reels_v56`, puis commande externe v64), chacun enveloppé
    dans `AdaptateurSousGo` (GO cité, borne de l'appel contre la part restante) ; porte de chaque relais à sa part du plan ; barème
    prudent lu dans la configuration ; refus avant toute porte et tout appel (code 2)."""
    from pole.relais import noms_de_cle_presents
    presents = noms_de_cle_presents(os.environ)
    if presents:
        raise B.BoucleRefusee(f"variables de clé dans l'environnement de l'orchestrateur ({', '.join(presents)}) : les relais tiennent les clés")
    montant = plan["plafond_modeles_usd"] + plan["plafond_machine_usd"]
    B.exiger_go_cite(go, plan["go"], montant)
    g2 = charger_goodhart_v2()
    budget, modeles = g2.reglages_de_configuration(conf)
    conf2, substitutions = g2.substituer_commandes(conf, os.path.join(os.path.abspath(sortie), REGISTRE_COURSE), plan["plafond_modeles_usd"])
    v8 = g2.charger_ideation_v8()
    adaptateurs, portes = v8.adaptateurs_reels_v56(conf2, sortie, base_sessions)
    if sorted(n for n in adaptateurs if n in ("kimi", "argon")) != ["argon", "kimi"]:
        raise B.BoucleRefusee(f"configuration : adaptateurs « kimi » et « argon » exigés, trouvés {sorted(adaptateurs)}")
    try:
        adaptateurs, portes = AC.commandes_v64(conf2, adaptateurs, portes)
    except AC.RelaisNonCommande as x:
        raise B.BoucleRefusee(str(x)) from None
    try:
        bareme = {n: AC.bareme_depuis_configuration(conf, n) for n in ("kimi", "argon")}
    except AC.BaremeAbsent as x:
        raise B.BoucleRefusee(str(x)) from None
    sous_go = {n: B.AdaptateurSousGo(adaptateurs[n], n, go, plan["go"], montant, compteur) for n in ("kimi", "argon")}
    proposeurs = [T.ProposeurAdaptateur(n, n, sous_go[n], os.path.join(base_sessions, "proposeur-" + n), budget, modeles[n])
                  for n in ("kimi", "argon")]
    etage = T.AdaptateurEtageV64(sous_go["kimi"], sous_go["argon"], "kimi", "argon",
                                 prix_caractere_usd={n: bareme[n]["prix_caractere_usd"] for n in ("kimi", "argon")})
    T.exiger_roles_joues(T.paires_de_roles(proposeurs, etage))
    parts = {"kimi": plan["plafond_kimi_usd"], "argon": plan["plafond_argon_usd"]}
    accuses = {n: portes[n].transmettre(ETAPE, parts[n]) for n in ("kimi", "argon")} if transmettre else "non relancées (vérification seule)"
    roles = {"experimentateur": ("experimentateur-kimi", modeles["kimi"]), "verificateur": ("verificateur-argon", modeles["argon"]),
             "familles": {"experimentateur": "kimi", "verificateur": "argon"}, "relais": {"experimentateur": "kimi", "verificateur": "argon"}}
    infos = {"budget_appel_usd": budget, "modeles_demandes": modeles, "substitutions_dans_les_commandes": substitutions,
             "accuses_plafond": accuses, "parts_des_relais_usd": parts, "portes": {n: portes[n].description() for n in ("kimi", "argon")},
             "bareme_des_commandes": bareme, "adaptateurs": {n: sous_go[n].description() for n in ("kimi", "argon")}}
    return proposeurs, etage, roles, infos


def roles_a_blanc(args, sortie):
    """Doublures scriptées de la v64, branchées sur le chemin réel (mêmes classes)."""
    cout = args.cout_simule_usd or 0.0
    proposeurs = [T.ProposeurAdaptateur("kimi-scripte", "kimi", T.AdaptateurProposeurScripte("kimi-scripte", 0.4, args.scenario_proposeur, cout),
                                        os.path.join(sortie, "proposeurs", "kimi-scripte"), cout, "doublure-kimi"),
                  T.ProposeurAdaptateur("argon-scripte", "argon", T.AdaptateurProposeurScripte("argon-scripte", 0.8, args.scenario_proposeur, cout),
                                        os.path.join(sortie, "proposeurs", "argon-scripte"), cout, "doublure-argon")]
    cout_e = args.cout_simule_etage_usd or 0.0
    etage = T.AdaptateurEtageV64(T.AdaptateurExperimentateurScripte(args.scenario_experimentateur, cout_e),
                                 T.AdaptateurVerificateurScripte(cout_e, args.scenario_verificateur), "kimi", "argon")
    roles = {"experimentateur": ("experimentateur-scripte", "famille-a"), "verificateur": ("verificateur-scripte", "famille-b"),
             "familles": {"experimentateur": "a", "verificateur": "b"}, "relais": {"experimentateur": "kimi", "verificateur": "argon"}}
    T.exiger_roles_joues(T.paires_de_roles(proposeurs, etage))
    return proposeurs, etage, roles


def principal(argv=None):
    a = argparse.ArgumentParser(description="plus petite course réelle de la boucle complète (v65) : bras réel seul, deux générations")
    a.add_argument("sortie")
    g = a.add_mutually_exclusive_group(required=True)
    g.add_argument("--a-blanc", action="store_true")
    g.add_argument("--preenregistrement")
    a.add_argument("--graine", type=int)
    a.add_argument("--configuration")
    a.add_argument("--moteur", choices=("reel",))
    a.add_argument("--confirmer-moteur-reel", action="store_true")
    a.add_argument("--registre-go")
    a.add_argument("--go")
    a.add_argument("--bac", choices=("reel", "factice"), required=True, help="aucun défaut ; « reel » refuse sans bwrap ≥ 0.9")
    a.add_argument("--utilisateur-bac", type=int)
    a.add_argument("--verifier-seulement", action="store_true")
    for o, t in (("--cartes-par-proposeur", int), ("--plafond-kimi-usd", float), ("--plafond-argon-usd", float),
                 ("--cout-simule-usd", float), ("--cout-simule-etage-usd", float)):
        a.add_argument(o, type=t)
    for o in ("--texte", "--heritage-depart", "--bras", "--scenario-proposeur", "--scenario-experimentateur", "--scenario-verificateur"):
        a.add_argument(o)
    args = a.parse_args(argv)
    noms_options = ("cartes_par_proposeur", "plafond_kimi_usd", "plafond_argon_usd", "cout_simule_usd", "cout_simule_etage_usd", "texte",
                    "heritage_depart", "bras", "scenario_proposeur", "scenario_experimentateur", "scenario_verificateur")
    options = {k: getattr(args, k) for k in noms_options if getattr(args, k) is not None}
    base_sessions, parent_bac, reel = None, None, not args.a_blanc
    from pole import configuration_v56 as cfg
    try:
        if os.path.exists(args.sortie) and os.listdir(args.sortie):
            raise FileExistsError(f"dossier de sortie non vide : {args.sortie} (on n'écrase jamais)")
        exiger_machine_du_bac(args.bac, reel, args.utilisateur_bac, version_bwrap() if args.bac == "reel" else None)
        monde = A.charger_monde(RACINE)
        environnement, permis, go, conf_info, gelees, empreinte = dict(T.ENV_A_BLANC), (), None, None, None, None
        if args.a_blanc:
            if args.graine is None or args.moteur or args.configuration or args.go or args.registre_go or args.verifier_seulement:
                raise B.BoucleRefusee("à blanc : --graine G seulement (ni moteur réel, ni configuration, ni GO)")
            if not 0 <= args.graine < 2 ** 64:
                raise B.BoucleRefusee("à blanc : graine dans [0 ; 2^64[ (l'espace ≥ 2^64 est celui des textes scellés)")
            with open(args.texte or TEXTE_A_BLANC, encoding="utf-8") as f:
                texte = f.read()
            plan = B.lire_plan(texte)
            if args.bras is not None:
                B.exiger_bras_reel_seul(args.bras)
            if args.cartes_par_proposeur is not None:
                plan.update(cartes_par_proposeur=args.cartes_par_proposeur, m_e_bh=B.m_impose(args.cartes_par_proposeur))
            for n in ("kimi", "argon"):
                if getattr(args, f"plafond_{n}_usd") is not None:
                    plan[f"plafond_{n}_usd"] = getattr(args, f"plafond_{n}_usd")
            plan["plafond_modeles_usd"] = plan["plafond_kimi_usd"] + plan["plafond_argon_usd"]
            entropie, mode, preenregistrement = args.graine, "a-blanc (exploratoire)", None
            chemin_heritage = args.heritage_depart or HERITAGE_DEPART
        else:
            if args.graine is not None or options:
                raise B.BoucleRefusee(f"mode réel : le plan est lu dans le texte scellé ; options refusées : {sorted(options) or ['--graine']}")
            if args.moteur != "reel" or not args.confirmer_moteur_reel or not args.configuration:
                raise B.BoucleRefusee("mode réel : --configuration, --moteur reel et --confirmer-moteur-reel exigés")
            entropie, empreinte, gelees, plan, texte = lire_preenregistrement(args.preenregistrement)
            mode, chemin_heritage = "reel (decisif)", HERITAGE_DEPART
        verifier_monde(monde, plan["monde_sha256"])
        if plan["monde_sha256"] != MONDE_SHA256:
            raise B.BoucleRefusee("monde : le code v65 joue le monde S-V1 (temoins-pari-demo-v1.json) seulement")
        B.exiger_bras_reel_seul(plan["bras"])
        depart = B.lire_heritage_depart(chemin_heritage, texte)
        jeu, sha_jeu, octets_jeu = B.lire_jeu_plante(texte, depart["archive"])
        depart = B.lire_heritage_depart(chemin_heritage, texte, jeu)  # garde 17 : aucune loi plantée dans l'héritage
        B.exiger_jeu_conforme(jeu, octets_jeu)
        compteur = B.CompteurV65(plan["plafond_modeles_usd"], plan["duree_h"] * 3600.0,
                                 {"kimi": plan["plafond_kimi_usd"], "argon": plan["plafond_argon_usd"]}, plan["plafond_machine_usd"], time.time)
        if args.a_blanc:
            proposeurs, adaptateur, roles = roles_a_blanc(args, args.sortie)
        else:
            if not os.path.isfile(args.configuration):
                raise B.BoucleRefusee(f"configuration introuvable : {args.configuration}")
            sha_conf = sha256_fichier(args.configuration)
            if sha_conf != plan["configuration_sha256"]:
                raise B.BoucleRefusee(f"configuration d'empreinte {sha_conf[:12]}… : le texte scellé gèle {plan['configuration_sha256'][:12]}…")
            if not args.registre_go or args.go != plan["go"]:
                raise B.BoucleRefusee(f"mode réel : --registre-go et --go {plan['go']} (celui du texte scellé) exigés")
            try:  # le GO porte le total : plafond des modèles + plafond de la machine (GO-2026-11-08-02 : 45 USD)
                go = cfg.verifier_go_v56(args.go, args.registre_go, plan["plafond_modeles_usd"] + plan["plafond_machine_usd"])
            except cfg.GoRefuse as x:
                raise B.GoNonCite(str(x)) from None
            conf = cfg.lire_configuration_v56(args.configuration)
            section = exiger_configuration_v65(conf, plan)
            environnement = os.environ
            try:
                exiger_machine_jetable_v56(environnement, permis_en_plus=tuple(((conf.get("etage_tests_de_mort") or {}).get("environnement_permis") or ())))
            except MachineNonJetable as x:
                raise B.BoucleRefusee(f"machine jetable (garde 15) : {x}") from None
            permis = tuple(((conf.get("etage_tests_de_mort") or {}).get("environnement_permis") or ()))
            base_sessions = tempfile.mkdtemp(prefix="boucle-reelle-v65-sessions-")
            proposeurs, adaptateur, roles, infos = roles_reels(conf, plan, base_sessions, os.path.abspath(args.sortie), go, compteur,
                                                               transmettre=not args.verifier_seulement)
            preenregistrement = {"chemin": os.path.relpath(os.path.realpath(args.preenregistrement), RACINE), "sha256": empreinte,
                                 "empreintes_du_code_verifiees": gelees, "plan": plan, "go": go}
            conf_info = dict(infos, chemin=os.path.abspath(args.configuration), sha256=sha_conf, section_v65=section,
                             environnement_permis=list(permis))
        T.exiger_familles_separees((roles["experimentateur"][0], roles["familles"]["experimentateur"]),
                                   (roles["verificateur"][0], roles["familles"]["verificateur"]))
        parent_bac, fabrique = preparer_bac(args.bac, args.utilisateur_bac)
        if args.verifier_seulement:
            print(json.dumps({"verification": "conforme", "ecriture": "aucune", "appel": "aucun", "portes": "non relancées", "plan": plan,
                              "heritage_depart_sha256": depart["bilan_sha256"], "jeu_plante_sha256": sha_jeu, "configuration": conf_info},
                             ensure_ascii=False, indent=1, default=str))
            return 0
    except Exception as x:  # noqa: BLE001 — refus nommé avant tout appel, jamais de repli
        print(f"refus : {type(x).__name__} : {x}", file=sys.stderr)
        for d in (parent_bac, base_sessions):
            if d:
                shutil.rmtree(d, True)
        return 2
    finally:
        if args.verifier_seulement:
            for d in (parent_bac, base_sessions):
                if d:
                    shutil.rmtree(d, True)
    os.makedirs(args.sortie, exist_ok=True)
    m = B.manifeste_boucle(etape=ETAPE, mode=mode, entropie_racine=str(entropie), plan=plan, preenregistrement=preenregistrement,
                           configuration=conf_info, bac=args.bac, bac_factice_declare=args.bac == "factice",
                           moteur_etage="claude-sdk" if reel else "simule", environnement_etage=sorted(environnement),
                           monde={k: monde[k] for k in ("source", "sha256", "loi_vraie")}, roles=roles,
                           heritage_depart={"chemin": os.path.abspath(chemin_heritage), "sha256": depart["bilan_sha256"]},
                           jeu_plante_sha256=sha_jeu, options_a_blanc=options if args.a_blanc else None,
                           code_sha256={r: sha256_fichier(os.path.join(RACINE, r)) for r in FICHIERS_GELES},
                           debut_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"))
    ecrire_json_scelle(os.path.join(args.sortie, "manifeste.json"), m)
    try:
        try:
            releve, journal = B.jouer_boucle(args.sortie, monde=monde, racine=entropie, plan=plan, jeu=jeu, depart=depart,
                                             proposeurs=proposeurs, adaptateur_etage=adaptateur, roles=roles, fabrique_executeur=fabrique,
                                             compteur=compteur, moteur="claude-sdk" if reel else "simule", environnement=environnement,
                                             permis_en_plus=permis)
        except Exception as x:  # noqa: BLE001 — C12 : toute exception après le manifeste est un arrêt scellé (code 3)
            partiel = getattr(x, "partiel", {}) or {}
            rel = partiel.get("releve") or {"version": B.VERSION, "arret": f"{type(x).__name__} : {x}", "cartes": [], "plantees": [],
                                            "generations_jouees": [], "boucle": {"incidents": [], "lectures": []}, "plan": plan,
                                            "heritage_depart": {"sha256": depart["bilan_sha256"]}, "entropie_racine": str(entropie)}
            rapport = {"version": B.VERSION, "mode": mode, "arret": f"{type(x).__name__} : {x}", "releve": rel,
                       "journal": partiel.get("journal", []), "depense": compteur.etat(), "preenregistrement": preenregistrement,
                       "appels_proposeurs": [p.appels for p in proposeurs], "appels_etage": list(getattr(adaptateur, "appels", [])),
                       "issue": "non jugeable (arrêt) : aucune issue lue ici (C5 par la lecture gelée)",
                       "fin_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
            ecrire_json_scelle(os.path.join(args.sortie, SORTIE), rapport)
            print(json.dumps({"mode": mode, "arret": rapport["arret"], "depense": compteur.etat()}, ensure_ascii=False), file=sys.stderr)
            return 3
    finally:
        if parent_bac:
            shutil.rmtree(parent_bac, True)
    rapport = {"version": B.VERSION, "mode": mode, "preenregistrement": preenregistrement, "releve": releve, "journal": journal,
               "depense": compteur.etat(), "appels_proposeurs": [p.appels for p in proposeurs],
               "appels_etage": list(getattr(adaptateur, "appels", [])),
               "fin_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
    sha = ecrire_json_scelle(os.path.join(args.sortie, SORTIE), rapport)
    print(json.dumps({"mode": mode, "releve_sha256": sha, "generations_jouees": releve["generations_jouees"], "cartes": len(releve["cartes"]),
                      "plantees": len(releve["plantees"]), "depense": compteur.etat(),
                      "lecture": "aucune (la lecture gelée est un autre programme)"}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(principal())
