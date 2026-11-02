"""Lanceur du tour fermé, version 61 (fichier neuf, R12 ; tâches A2, A3, A4). Cœur : `pole/tour_ferme_v61.py` ; lecture gelée
(séparée, jamais appelée ici sur une course réelle) : `pole/lecture_tour_ferme_v61.py`.

Deux modes, exclusifs :
- **à blanc** (`--a-blanc --graine G`, G < 2⁶⁴) : proposeurs, expérimentateur et vérificateur scriptés, aucun réseau, aucune
  clé ; le plan et les décisions se règlent en ligne de commande ; exploratoire, ne décide rien ;
- **réel** (`--preenregistrement P --configuration CONF --moteur reel --confirmer-moteur-reel --registre-go R --go ID`) :
  Kimi et Argon par les adaptateurs du pôle (`demonstrations/ideation_v8.adaptateurs_reels_v56`, mécanisme du lanceur de
  l'attaque de Goodhart v2 pour la configuration et le jeton `{REGISTRE}`). Le plan, les décisions D7 à D9, les plafonds, la
  configuration (empreinte) et le GO sont lus dans le **texte scellé** (bloc `plan-gele`), jamais en ligne de commande ;
  graine E = int(sha256 du texte scellé, 16) ≥ 2⁶⁴.

Gardes avant tout appel et toute écriture (code 2) : dossier de sortie non vide ; `--bac` sans défaut (« reel » exige `bwrap`
et, sous un noyau superutilisateur, `--utilisateur-bac`) ; mode réel : préenregistrement hors de
`prereg/preenregistrement-tour-ferme-v1-v<N>.md`, non scellé, nom contenant « brouillon », marqueur `<<…>>` restant, bloc
`empreintes-du-code` ne couvrant pas exactement `FICHIERS_GELES` ou d'empreinte différente du fichier présent (garde 6) ;
plan absent ou hors des valeurs permises ; configuration d'une autre empreinte que celle du plan, ou dont `budget.plafond_usd`
diffère du plafond de l'étage ; GO autre que celui du plan, absent du registre, d'un autre montant ; variable de clé dans
l'environnement ; étage 2 sans lecture scellée de l'étage 1 « tient » (garde 12) ; données tenues à l'écart d'une autre
empreinte que celle du plan (garde 11, `verifier_reserve`).
Codes : 0 relevé écrit (le code ne décide rien ; seule la lecture gelée décide) ; 2 refus ; 3 arrêt (plafond de dépense ou de
durée, contre-calcul en désaccord, héritage refusé) : relevé partiel scellé, aucune issue lue.

Usage à blanc : python3 -I -B demonstrations/tour_ferme_v61.py SORTIE_NEUVE --etage 1 --a-blanc --graine 7 --bac reel
                [--utilisateur-bac 64097] [--generations 3] [--d7 archive_du_bras_reel] [--scenario-proposeur hors_gabarit]
                [--cout-simule-usd 0.01 --plafond-usd 0.5] [--duree-max-h 1]
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
sys.path.insert(0, RACINE)

from pole import a_blanc_v59 as A  # noqa: E402
from pole import reserve_tenue_a_l_ecart_v61 as RV  # noqa: E402
from pole import tour_ferme_v61 as T  # noqa: E402
from pole.outils import ecrire_json_scelle, sha256_fichier, verifier_scelle  # noqa: E402

ETAPE = "tour_ferme_v61"
SORTIE = "tour-ferme-v1-etage{e}.json"
DOSSIER_PREREG = os.path.join(RACINE, "prereg")
NOM_PREREG = re.compile(r"^preenregistrement-tour-ferme-v1-v[1-9][0-9]*\.md$")
DEBUT_EMPREINTES, FIN_EMPREINTES = "<!-- empreintes-du-code : début -->", "<!-- empreintes-du-code : fin -->"
DEBUT_PLAN, FIN_PLAN = "<!-- plan-gele : début -->", "<!-- plan-gele : fin -->"
MARQUEUR = re.compile(r"<<[A-Z0-9_]+>>")
SHA = re.compile(r"^[0-9a-f]{64}$")
REGISTRE_COURSE = "registre-depense-cumulee-v1.jsonl"
UID_BAC_DEFAUT = None
# Fermeture des imports du chemin à blanc et du chemin réel (essai `Fermeture` de `essais/test_v61_tour_ferme.py`).
FICHIERS_GELES = (
    "demonstrations/tour_ferme_v61.py", "demonstrations/attaque_goodhart_v2.py", "demonstrations/banc_tricheurs_v7.py",
    "demonstrations/banc_tricheurs_v8.py", "demonstrations/ideation_v2.py", "demonstrations/ideation_v4.py",
    "demonstrations/ideation_v5.py", "demonstrations/ideation_v6.py", "demonstrations/ideation_v7.py", "demonstrations/ideation_v8.py",
    "pole/__init__.py", "pole/a_blanc_v59.py", "pole/adaptateur_kimi_v53.py", "pole/adaptateurs.py", "pole/adaptateurs_v56.py",
    "pole/aiguilleur_v53.py", "pole/attaque_goodhart_v2.py", "pole/bisociateur_v53.py", "pole/bisociateur_v54.py",
    "pole/bisociateur_v55.py", "pole/boucle_fermee_v59.py", "pole/budget_v53.py", "pole/budget_v54.py", "pole/budget_v56.py",
    "pole/caviardage.py", "pole/coffre_v53.py", "pole/coffre_v55.py", "pole/configuration_v53.py", "pole/configuration_v54.py",
    "pole/configuration_v55.py", "pole/configuration_v56.py", "pole/controles_pari.py", "pole/course2_v53.py",
    "pole/course2_v54.py", "pole/course2_v55.py", "pole/course2_v56.py", "pole/cycle.py", "pole/dossier_ferme.py",
    "pole/etage_entre_generations_v53.py", "pole/etage_entre_generations_v54.py", "pole/etage_entre_generations_v55.py",
    "pole/etage_entre_generations_v56.py", "pole/etage_entre_generations_v57.py", "pole/fiche.py", "pole/fiches_v53.py",
    "pole/fiches_v54.py", "pole/garde_outils.py", "pole/gardes_e0_v54.py", "pole/gardes_e0_v55.py", "pole/gardes_e0_v56.py",
    "pole/graines_v53.py", "pole/ideation_v2.py", "pole/juges_croises_v53.py", "pole/lecture_tour_ferme_v61.py", "pole/memoire.py",
    "pole/memoire_v53.py", "pole/mesures_v54.py", "pole/moisson.py", "pole/noyau_v54.py", "pole/noyau_v55.py", "pole/noyau_v56.py",
    "pole/nul_filles_v2.py", "pole/nul_v8.py", "pole/oracle_tour_ferme_v60.py", "pole/outils.py", "pole/pari_apparie.py",
    "pole/prepilote_v54.py", "pole/prepilote_v55.py", "pole/prepilote_v56.py", "pole/proposeurs_references_v59.py",
    "pole/protocole_outils.py", "pole/relais.py", "pole/relais_reel.py", "pole/reserve_tenue_a_l_ecart_v60.py", "pole/reserve_tenue_a_l_ecart_v61.py",
    "pole/selection_pari.py", "pole/suivi_roles_v54.py", "pole/tableau_v53.py", "pole/tests_de_mort_v2.py",
    "pole/tests_de_mort_v3.py", "pole/tests_de_mort_v4.py", "pole/tests_de_mort_v5.py", "pole/tour_ferme_v61.py")
CLES_PLAN = {"generations_etage_1", "generations_etage_2", "cartes_par_proposeur", "cartes_reference", "m_e_bh_etage_1",
             "m_e_bh_etage_2", "plafond_etage_1_usd", "plafond_etage_2_usd", "duree_etage_1_h", "duree_etage_2_h", "d7", "d8",
             "d9", "configuration_sha256", "go", "reserve_manifeste_sha256", "ordre_des_bras"}
A_BLANC = {"generations": 3, "cartes_par_proposeur": 6, "cartes_reference": 12, "m_e_bh": 19, "plafond_usd": 1e9, "duree_max_h": 24.0,
           "d7": "archive_du_bras_reel", "d8": "predicteur_connu", "d9": "mecanique"}


class PreenregistrementRefuse(T.TourRefuse):
    """Mode réel : texte autre que le fichier fixé, non scellé, à marqueur restant, sans code gelé conforme ou sans plan."""


def _bloc(texte, debut, fin, nom):
    i, j = texte.find(debut), texte.find(fin)
    if i < 0 or j < i:
        raise PreenregistrementRefuse(f"bloc « {nom} » absent du préenregistrement")
    return texte[i + len(debut):j]


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
        raise PreenregistrementRefuse(f"plan-gele : clés attendues {sorted(CLES_PLAN)}, trouvées {sorted(lignes)}")
    try:
        entiers = {k: int(lignes[k]) for k in ("generations_etage_1", "generations_etage_2", "cartes_par_proposeur", "cartes_reference",
                                                 "m_e_bh_etage_1", "m_e_bh_etage_2")}
        reels = {k: float(lignes[k].replace(",", ".")) for k in ("plafond_etage_1_usd", "plafond_etage_2_usd", "duree_etage_1_h",
                                                                 "duree_etage_2_h")}
    except ValueError:
        raise PreenregistrementRefuse("plan-gele : générations, cartes, m, plafonds et durées numériques") from None
    if entiers["generations_etage_1"] < 2 or entiers["generations_etage_2"] < 1 or entiers["cartes_par_proposeur"] < 1 \
            or entiers["cartes_reference"] < 1 or entiers["m_e_bh_etage_1"] < 2 * entiers["cartes_par_proposeur"] \
            or entiers["m_e_bh_etage_1"] < entiers["cartes_reference"] or any(v <= 0 for v in reels.values()):
        raise PreenregistrementRefuse("plan-gele : valeurs hors des bornes (générations ≥ 2 et ≥ 1 ; m ≥ emplacements de cartes ; "
                                      "plafonds et durées > 0)")
    decisions = T.verifier_decisions({k: lignes[k] for k in ("d7", "d8", "d9")})
    if not SHA.match(lignes["configuration_sha256"]) or not SHA.match(lignes["reserve_manifeste_sha256"]):
        raise PreenregistrementRefuse("plan-gele : configuration_sha256 et reserve_manifeste_sha256 = 64 caractères hexadécimaux")
    if not re.fullmatch(r"GO-\d{4}-\d{2}-\d{2}-\d{2}", lignes["go"]):
        raise PreenregistrementRefuse("plan-gele : go = GO-AAAA-MM-JJ-NN")
    ordre = tuple(x.strip() for x in lignes["ordre_des_bras"].split(","))
    if ordre != T.BRAS_ETAGE1:
        raise PreenregistrementRefuse(f"plan-gele : ordre_des_bras {ordre} ; le code gelé joue {T.BRAS_ETAGE1}")
    return dict(entiers, **reels, decisions=decisions, configuration_sha256=lignes["configuration_sha256"], go=lignes["go"],
                reserve_manifeste_sha256=lignes["reserve_manifeste_sha256"], ordre_des_bras=list(ordre))


def lire_preenregistrement(chemin):
    """Garde 6 : le texte au chemin fixé, scellé, sans « brouillon », sans marqueur, gelant exactement le code présent ; rend
    (entropie, empreinte, empreintes gelées, plan)."""
    reel, dossier = os.path.realpath(chemin), os.path.realpath(DOSSIER_PREREG)
    if os.path.dirname(reel) != dossier or not NOM_PREREG.match(os.path.basename(reel)) or "brouillon" in os.path.basename(reel):
        raise PreenregistrementRefuse(f"mode réel : le préenregistrement est prereg/preenregistrement-tour-ferme-v1-v<N>.md, pas {chemin}")
    if not os.path.isfile(reel):
        raise PreenregistrementRefuse(f"préenregistrement introuvable : {chemin}")
    if not verifier_scelle(reel):
        raise PreenregistrementRefuse(f"préenregistrement non scellé (compagnon .sha256 absent ou non conforme) : {chemin}")
    with open(reel, encoding="utf-8") as f:
        texte = f.read()
    restants = sorted(set(MARQUEUR.findall(texte)))
    if restants:
        raise PreenregistrementRefuse(f"marqueur(s) non rempli(s) : {restants} (décision de Lazar ou case à porter avant scellement)")
    gelees = re.findall(r"^([0-9a-f]{64})  (\S+)$", _bloc(texte, DEBUT_EMPREINTES, FIN_EMPREINTES, "empreintes-du-code"), re.M)
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
    plan = lire_plan(texte)
    empreinte = sha256_fichier(reel)
    entropie = int(empreinte, 16)
    if entropie < 2 ** 64:
        raise PreenregistrementRefuse("entropie décisive < 2^64 : espace réservé au mode à blanc")
    return entropie, empreinte, dict((r, h) for h, r in gelees), plan


def charger_goodhart_v2():
    spec = importlib.util.spec_from_file_location("attaque_goodhart_v2_pour_tour_ferme", os.path.join(ICI, "attaque_goodhart_v2.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def roles_reels(conf, plafond_usd, base_sessions, sortie, etage):
    """Adaptateurs du chemin réel : proposeurs Kimi et Argon, expérimentateur Kimi, vérificateur Argon (familles séparées,
    garde 9) ; même mécanisme que l'attaque de Goodhart v2 (`reglages_de_configuration`, `substituer_commandes`, pire cas du
    budget par appel) ; la configuration doit porter le plafond de l'étage (`budget.plafond_usd`, aucune substitution de plafond)."""
    from pole.relais import noms_de_cle_presents
    presents = noms_de_cle_presents(os.environ)
    if presents:
        raise T.TourRefuse(f"variables de clé dans l'environnement de l'orchestrateur ({', '.join(presents)}) : les relais tiennent les clés")
    g2 = charger_goodhart_v2()
    budget, modeles = g2.reglages_de_configuration(conf)
    if float((conf.get("budget") or {}).get("plafond_usd") or 0) != float(plafond_usd):
        raise T.TourRefuse(f"configuration : budget.plafond_usd = {(conf.get('budget') or {}).get('plafond_usd')!r} ≠ plafond de "
                           f"l'étage {etage} ({plafond_usd} USD) : demander une configuration à empreinte neuve, aucune substitution")
    conf2, substitutions = g2.substituer_commandes(conf, os.path.join(os.path.abspath(sortie), REGISTRE_COURSE), plafond_usd)
    v8 = g2.charger_ideation_v8()
    adaptateurs, portes = v8.adaptateurs_reels_v56(conf2, sortie, base_sessions)
    if sorted(n for n in adaptateurs if n in ("kimi", "argon")) != ["argon", "kimi"]:
        raise T.TourRefuse(f"configuration : adaptateurs « kimi » et « argon » exigés, trouvés {sorted(adaptateurs)}")
    accuses = {n: portes[n].transmettre(ETAPE, plafond_usd / 2) for n in ("kimi", "argon")}
    proposeurs = []
    for n in ("kimi", "argon"):
        d = os.path.join(base_sessions, "proposeur-" + n)
        os.makedirs(d, exist_ok=True)
        proposeurs.append(T.ProposeurAdaptateur(n, n, adaptateurs[n], d, budget, modeles[n]))

    class AdaptateurEtage:
        """Expérimentateur = Kimi, vérificateur = Argon (rôles de l'étage v5), par les adaptateurs réels."""
        nom = "etage-reel-v61"
        appels = []

        def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
            ad = adaptateurs["kimi" if role == "experimentateur_test" else "argon"]
            r = ad.lancer(role, consigne, dossier, budget_usd, max_tours, modele=modele)
            self.appels.append({"role": role, "modele": modele, "cout_usd": r.cout_declare_usd, "statut": r.statut})
            return r

    roles = {"experimentateur": ("experimentateur-kimi", modeles["kimi"]), "verificateur": ("verificateur-argon", modeles["argon"]),
             "familles": {"experimentateur": "kimi", "verificateur": "argon"}}
    infos = {"budget_appel_usd": budget, "modeles_demandes": modeles, "substitutions_dans_les_commandes": substitutions,
             "accuses_plafond": accuses, "portes": {n: portes[n].description() for n in ("kimi", "argon")}}
    return proposeurs, AdaptateurEtage(), roles, infos


def roles_a_blanc(monde, args):
    props = [T.ProposeurScripte("kimi-scripte", monde, 0.6, args.scenario_proposeur, args.cout_simule_usd or 0.0),
             T.ProposeurScripte("argon-scripte", monde, 1.0, args.scenario_proposeur, args.cout_simule_usd or 0.0)]
    lois = {}

    class AdaptateurEtageBlanc(A.AdaptateurAblanc):
        def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
            if role == "experimentateur_test":
                ident = os.path.basename(os.path.dirname(os.path.dirname(dossier)))
                self.lois[ident] = lois[ident]
            return super().lancer(role, consigne, dossier, budget_usd, max_tours, modele)

    ad = AdaptateurEtageBlanc({}, {})
    orig = T.jouer_etage

    def jouer_etage(dossier_etage, cartes, lois_par_ident, *a, **k):
        lois.update(lois_par_ident)
        return orig(dossier_etage, cartes, lois_par_ident, *a, **k)

    T.jouer_etage = jouer_etage  # instance propre du module dans ce processus (mode à blanc seulement)
    fam = args.familles_a_blanc or "a,b"
    fa, fb = (fam.split(",") + [""])[:2]
    roles = {"experimentateur": ("experimentateur-scripte", "famille-" + fa), "verificateur": ("verificateur-scripte", "famille-" + fb),
             "familles": {"experimentateur": fa, "verificateur": fb}}
    return props, ad, roles


def preparer_bac(bac, utilisateur_bac):
    parent, racine_travail = None, None
    if bac == "reel" and os.geteuid() == 0 and utilisateur_bac is not None:
        parent = os.path.realpath(tempfile.mkdtemp(prefix="bac-tour-ferme-v61-"))
        os.chmod(parent, 0o711)
        racine_travail = os.path.join(parent, "bac")
        os.mkdir(racine_travail, 0o700)
        os.chown(racine_travail, int(utilisateur_bac), int(utilisateur_bac))
    A.choisir_executeur(bac, utilisateur_bac=utilisateur_bac, racine_travail=racine_travail)  # refus avant tout (garde 3)
    return parent, (lambda: A.choisir_executeur(bac, utilisateur_bac=utilisateur_bac, racine_travail=racine_travail))


def lire_lecture_etage_1(chemin, sha_attendue):
    """Garde 12 : lecture scellée de l'étage 1, à l'empreinte donnée, issue « tient » ; sinon refus."""
    if not chemin or not sha_attendue or not os.path.isfile(chemin) or not verifier_scelle(chemin) or sha256_fichier(chemin) != sha_attendue:
        raise T.TourRefuse("étage 2 : lecture scellée de l'étage 1 exigée (--lecture-etage-1 FICHIER --lecture-etage-1-sha256 SHA), "
                           "à l'empreinte donnée, sceau vérifié")
    with open(chemin, encoding="utf-8") as f:
        lecture = json.load(f)
    if (lecture.get("etage_1") or lecture).get("issue_etage_1") != "tient":
        raise T.TourRefuse(f"étage 2 refusé : la lecture scellée de l'étage 1 dit « {(lecture.get('etage_1') or lecture).get('issue_etage_1')} »")
    return lecture


def principal(argv=None):
    a = argparse.ArgumentParser(description="tour fermé (v61) : étage 1 (monde planté, trois bras) ; porte vers l'étage 2")
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
    a.add_argument("--utilisateur-bac", type=int, default=UID_BAC_DEFAUT)
    a.add_argument("--verifier-seulement", action="store_true")
    a.add_argument("--lecture-etage-1")
    a.add_argument("--lecture-etage-1-sha256")
    a.add_argument("--tenue-a-l-ecart", help="étage 2 : dossier de la réserve (manifeste à l'empreinte du plan)")
    # options du mode à blanc seulement
    a.add_argument("--generations", type=int)
    a.add_argument("--cartes-par-proposeur", type=int)
    a.add_argument("--cartes-reference", type=int)
    a.add_argument("--m-e-bh", type=int)
    a.add_argument("--plafond-usd", type=float)
    a.add_argument("--duree-max-h", type=float)
    a.add_argument("--d7", choices=T.DECISIONS["d7"])
    a.add_argument("--d8", choices=T.DECISIONS["d8"])
    a.add_argument("--d9", choices=T.DECISIONS["d9"])
    a.add_argument("--scenario-proposeur", choices=("hors_gabarit", "illisible"))
    a.add_argument("--familles-a-blanc", help="« a,b » (défaut) ; « a,a » = artefact de la garde 9")
    a.add_argument("--cout-simule-usd", type=float)
    args = a.parse_args(argv)
    options_plan = {k: getattr(args, k) for k in ("generations", "cartes_par_proposeur", "cartes_reference", "m_e_bh", "plafond_usd",
                                                   "duree_max_h", "d7", "d8", "d9", "scenario_proposeur", "familles_a_blanc", "cout_simule_usd")
                    if getattr(args, k) is not None}
    base_sessions, parent_bac = None, None
    from pole import configuration_v56 as cfg
    try:
        if os.path.exists(args.sortie) and os.listdir(args.sortie):
            raise FileExistsError(f"dossier de sortie non vide : {args.sortie} (on n'écrase jamais)")
        if args.bac == "factice" and not args.a_blanc:
            raise T.TourRefuse("mode réel : bac « reel » exigé (aucune barrière avec l'exécuteur factice)")
        monde = A.charger_monde(RACINE)
        if args.a_blanc:
            if args.graine is None or args.moteur or args.configuration or args.go or args.verifier_seulement:
                raise T.TourRefuse("à blanc : --graine G seulement (ni moteur réel, ni configuration, ni GO)")
            if not 0 <= args.graine < 2 ** 64:
                raise T.TourRefuse("à blanc : graine dans [0 ; 2^64[ (l'espace ≥ 2^64 est celui des textes scellés)")
            r = dict(A_BLANC, **{k: v for k, v in options_plan.items() if k in A_BLANC})
            plan = {"generations": r["generations"], "cartes_par_proposeur": r["cartes_par_proposeur"], "cartes_reference": r["cartes_reference"],
                    "m_e_bh": r["m_e_bh"], "plafond_usd": r["plafond_usd"], "duree_max_s": r["duree_max_h"] * 3600.0}
            decisions = T.verifier_decisions({k: r[k] for k in ("d7", "d8", "d9")})
            entropie, mode, preenregistrement, conf_info, moteur = args.graine, "a-blanc (exploratoire)", None, None, "simule"
            proposeurs, adaptateur, roles = roles_a_blanc(monde, args)
        else:
            if args.graine is not None or options_plan:
                raise T.TourRefuse(f"mode réel : le plan est lu dans le texte scellé ; options refusées : {sorted(options_plan) or ['--graine']}")
            if args.moteur != "reel" or not args.confirmer_moteur_reel or not args.configuration:
                raise T.TourRefuse("mode réel : --configuration, --moteur reel et --confirmer-moteur-reel exigés")
            entropie, empreinte, gelees, p = lire_preenregistrement(args.preenregistrement)
            e = args.etage
            plan = {"generations": p[f"generations_etage_{e}"], "cartes_par_proposeur": p["cartes_par_proposeur"],
                    "cartes_reference": p["cartes_reference"], "m_e_bh": p[f"m_e_bh_etage_{e}"], "plafond_usd": p[f"plafond_etage_{e}_usd"],
                    "duree_max_s": p[f"duree_etage_{e}_h"] * 3600.0}
            decisions = p["decisions"]
            if not os.path.isfile(args.configuration):
                raise T.TourRefuse(f"configuration introuvable : {args.configuration}")
            sha_conf = sha256_fichier(args.configuration)
            if sha_conf != p["configuration_sha256"]:
                raise T.TourRefuse(f"configuration d'empreinte {sha_conf[:12]}… : le texte scellé gèle {p['configuration_sha256'][:12]}… (aucune autre)")
            if not args.registre_go or args.go != p["go"]:
                raise T.TourRefuse(f"mode réel : --registre-go et --go {p['go']} (celui du texte scellé) exigés")
            try:
                go = cfg.verifier_go_v56(args.go, args.registre_go, plan["plafond_usd"])
            except cfg.GoRefuse as x:
                raise T.TourRefuse(str(x)) from None
            conf = cfg.lire_configuration_v56(args.configuration)
            base_sessions = tempfile.mkdtemp(prefix="tour-ferme-v61-sessions-")
            proposeurs, adaptateur, roles, infos = roles_reels(conf, plan["plafond_usd"], base_sessions, os.path.abspath(args.sortie), e)
            mode, moteur = "reel (decisif)", "simule"  # « simule » est le mot de l'étage v5 pour « pas le kit Claude » : adaptateurs externes
            preenregistrement = {"chemin": os.path.relpath(os.path.realpath(args.preenregistrement), RACINE), "sha256": empreinte,
                                 "empreintes_du_code_verifiees": gelees, "plan": p, "go": go}
            conf_info = dict(infos, chemin=os.path.abspath(args.configuration), sha256=sha_conf)
            if e == 2:
                lire_lecture_etage_1(args.lecture_etage_1, args.lecture_etage_1_sha256)  # garde 12
                if not args.tenue_a_l_ecart:
                    raise T.TourRefuse("étage 2 : --tenue-a-l-ecart DOSSIER exigé (réserve par empreinte)")
                RV.verifier_reserve(args.tenue_a_l_ecart, p["reserve_manifeste_sha256"])  # garde 11 au montage
                raise T.TourRefuse("étage 2 : porte et montage vérifiés ; le cœur de l'étage 2 (juge à plan plein avec archive, monde M2, "
                                   "test de mort contre le prédicteur connu) n'est pas écrit dans cette version : refus, aucun appel")
        if args.etage == 2:
            raise T.TourRefuse("étage 2 à blanc : non écrit dans cette version")
        T.exiger_familles_separees((roles["experimentateur"][0], roles["familles"]["experimentateur"]),
                                   (roles["verificateur"][0], roles["familles"]["verificateur"]))
        parent_bac, fabrique = preparer_bac(args.bac, args.utilisateur_bac)
        if args.verifier_seulement:
            print(json.dumps({"verification": "conforme", "ecriture": "aucune", "appel": "aucun", "plan": plan, "decisions": decisions,
                              "configuration": conf_info}, ensure_ascii=False, indent=1, default=str))
            return 0
    except (FileExistsError, T.TourRefuse, A.BacASableIndisponible, RV.ReserveRefusee, cfg.ConfigurationRefusee) as x:
        print(f"refus : {type(x).__name__} : {x}", file=sys.stderr)
        return 2
    except Exception as x:  # noqa: BLE001 — refus nommé, jamais de repli
        print(f"refus : {type(x).__name__} : {x}", file=sys.stderr)
        return 2
    finally:
        if parent_bac and args.verifier_seulement:
            shutil.rmtree(parent_bac, True)
    os.makedirs(args.sortie, exist_ok=True)
    m = T.manifeste_tour(etape=ETAPE, mode=mode, etage=args.etage, entropie_racine=str(entropie), plan=plan, decisions=decisions,
                         preenregistrement=preenregistrement, configuration=conf_info, bac=args.bac,
                         monde={k: monde[k] for k in ("source", "sha256", "loi_vraie")},
                         roles={k: list(v) for k, v in roles.items() if k != "familles"}, familles=roles["familles"],
                         code_sha256={r: sha256_fichier(os.path.join(RACINE, r)) for r in FICHIERS_GELES},
                         debut_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"))
    ecrire_json_scelle(os.path.join(args.sortie, "manifeste.json"), m)
    compteur = T.Compteur(plan["plafond_usd"], plan["duree_max_s"], time.time)
    try:
        try:
            releve, journal = T.jouer_etage_1(args.sortie, monde=monde, racine=entropie, plan=plan, decisions=decisions, proposeurs=proposeurs,
                                              adaptateur_etage=adaptateur, roles=roles, fabrique_executeur=fabrique, compteur=compteur, moteur=moteur)
        except T.ArretTour as x:
            rel = x.partiel.get("releve") or {"version": T.VERSION, "etage": args.etage, "arret": str(x), "cartes": [],
                                             "generations_jouees": {b: [] for b in T.BRAS_ETAGE1}, "boucle": {"incidents": [], "lectures": []}}
            rapport = {"version": T.VERSION, "mode": mode, "arret": str(x), "releve": rel, "journal": x.partiel.get("journal", []),
                       "depense": compteur.etat(), "issue": "non jugeable (arrêt) : aucune issue lue"}
            ecrire_json_scelle(os.path.join(args.sortie, SORTIE.format(e=args.etage)), rapport)
            print(json.dumps({"mode": mode, "arret": str(x), "depense": compteur.etat()}, ensure_ascii=False), file=sys.stderr)
            return 3
        except T.TourRefuse as x:
            rapport = {"version": T.VERSION, "mode": mode, "arret": f"{type(x).__name__} : {x}", "depense": compteur.etat(),
                       "issue": "non jugeable (refus en cours de course) : aucune issue lue"}
            ecrire_json_scelle(os.path.join(args.sortie, SORTIE.format(e=args.etage)), rapport)
            print(json.dumps({"mode": mode, "arret": rapport["arret"]}, ensure_ascii=False), file=sys.stderr)
            return 3
    finally:
        if parent_bac:
            shutil.rmtree(parent_bac, True)
    rapport = {"version": T.VERSION, "mode": mode, "preenregistrement": preenregistrement, "releve": releve, "journal": journal,
               "depense": compteur.etat(), "appels_proposeurs": [p.appels for p in proposeurs], "appels_etage": list(getattr(adaptateur, "appels", [])),
               "fin_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
    sha = ecrire_json_scelle(os.path.join(args.sortie, SORTIE.format(e=args.etage)), rapport)
    print(json.dumps({"mode": mode, "releve_sha256": sha, "generations_jouees": releve["generations_jouees"], "cartes": len(releve["cartes"]),
                      "depense": compteur.etat(), "lecture": "aucune (la lecture gelée est un autre programme)"}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(principal())
