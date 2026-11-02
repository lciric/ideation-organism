"""Mode « à blanc » de la boucle fermée, version 59 (fichier neuf, R12 ; tâches A2 et A4) — aucun réseau, aucun modèle, aucune
clé, aucune dépense.

Chaîne jouée, par bras et par génération (deux générations au moins) :
proposition scriptée → gardien (forme seule) → juge statistique sous le nul v8 → tests de mort v5 (verdict du noyau sur le
fichier brut) → vérificateur (lecteur témoin d'une autre famille, scripté) → sélection scellée (v57) → bilan scellé (v59) →
**lecture vérifiée par la génération suivante** (`boucle_fermee_v59.lire_heritage`).

Monde à loi plantée (source : `exemples/temoins-pari-demo-v1.json`, empreinte consignée) : la loi du monde est celle du témoin
vrai S-V1 (3 issues, 2 traits, 2 sous-populations : la classe de mondes du banc des tricheurs v8). Cartes scriptées de la
génération 1 : la loi plantée (vraie), quatre lois fausses (S-F1, S-F2, S-F4 de l'exemple ; l'anti-loi, poids opposés), un cas
inconclusif (loi plantée tempérée, l'expérimentateur n'écrit pas le fichier brut → « non concluant »), un cas éliminé (loi
plantée accentuée qui préenregistre un gain d'au moins 2 nat → « éliminée ») et une carte mal formée (sans bloc
`statistique` : refusée au gardien). Génération 2 : copie et mélange des lois de la vue (archive lue), plus une loi fausse.

Bras : « scripte » (ci-dessus), « aleatoire » et « recopie_melange » (`proposeurs_references_v59`) ; chaque bras joue ses deux
générations ; la génération 1 des trois bras porte les cartes scriptées de la génération 1 (amorce commune), plus les cartes du
bras. Le journal compte, par bras et par génération, les cartes proposées, refusées au gardien, jugées, promues, testées,
survivantes et retenues, et l'oracle de chaque carte (gain attendu sur la marginale du monde, divergence à la loi plantée).

Juge : la fonction de jugement « fiche fraîche » du banc des tricheurs v8 validé (`banc_tricheurs_v8.juger_v8`), réécrite ici
appel pour appel (bibliothèque standard + marginale d'entraînement + `nul_v8.membres_archive_v8` sur l'archive lue ; engagement
`construire_engagement_v2`, ordre secret ; tirages frais `tirer_frais` liés à l'empreinte de l'engagement ; `evaluer_v2`), puis
la règle e-BH de la génération (`cycle.appliquer_multiplicite`). Graines : `boucle_fermee_v59.graine_de_tache` (R9).

Bac à sable : `bac="reel"` exige `bwrap` et une sonde réussie (`ExecuteurBacASable` de l'étage v5 : celui de la v3, 768 Mo) ;
sous un noyau superutilisateur, un utilisateur dédié sans privilège (`utilisateur_bac`) est exigé. Indisponible → refus
(`BacASableIndisponible`), **jamais de repli** sur l'exécuteur factice ; `bac="factice"` doit être demandé explicitement et le
journal le dit (aucune barrière).
"""

import json
import math
import os
import random
import shutil
import tempfile

from . import boucle_fermee_v59 as bf
from . import nul_filles_v2 as nf
from . import nul_v8
from . import proposeurs_references_v59 as pr
from . import selection_pari as sp
from . import tests_de_mort_v5 as v5
from .adaptateurs import Resultat
from .controles_pari import _frequences
from .cycle import appliquer_multiplicite, instants_reguliers
from .etage_entre_generations_v53 import preparer_generation
from .etage_entre_generations_v57 import NOM_SELECTION, jouer_etage_v57, selection_entre_generations
from .fiches_v53 import preparer
from .outils import ecrire_json_scelle, empreinte_objet, sha256_fichier
from .protocole_outils import DEBUT_DONNEES, FIN_DONNEES

VERSION = "a-blanc-v59"
K, DIM = pr.K, pr.DIM
ALPHA, TIRAGES, ENTRAINEMENT, EPISODES_TRANCHE, ORACLE = 0.05, 200, 100, 400, 4000
BRAS = ("scripte", "aleatoire", "recopie_melange")
SOURCE_MONDE = os.path.join("exemples", "temoins-pari-demo-v1.json")
LOI_VRAIE, LOIS_FAUSSES = "S-V1", ("S-F1", "S-F2", "S-F4")
CHAMPS_CARTE = ("identifiant", "titre", "hypothese", "prediction", "signe", "metrique", "loi_predictive", "test_de_mort", "source")
CHAMPS_FICHE = ("titre", "hypothese", "prediction", "signe", "metrique", "test_de_mort")
CORRESPONDANCE = {"nom": "titre", "enonce": "hypothese", "prediction": "prediction", "signe": "signe", "metrique": "metrique",
                  "test_de_mort": "test_de_mort"}
EXPERIMENTATEUR = ("experimentateur-scripte", "famille-a-scriptee-v59")
VERIFICATEUR = ("verificateur-scripte", "famille-b-scriptee-v59")
ENV_A_BLANC = {"PATH": "/usr/bin:/bin", "POLE_MACHINE_JETABLE_V56": "1"}  # déclaration du mode à blanc : aucun secret, aucune clé
FIN = "```json\n" + json.dumps({"fin": "fini"}) + "\n```"


class BacASableIndisponible(RuntimeError):
    """`bac="reel"` sans `bwrap`, sonde en échec, ou noyau superutilisateur sans utilisateur dédié : refus, aucun repli."""


class CarteRefusee(ValueError):
    pass


# --- monde planté -------------------------------------------------------------------------------------------------------------


def charger_monde(racine_orchestrateur):
    chemin = os.path.join(racine_orchestrateur, SOURCE_MONDE)
    with open(chemin, encoding="utf-8") as f:
        fiches = {x["identifiant"]: x for x in json.load(f)["fiches"]}
    vraie = fiches[LOI_VRAIE]
    if vraie.get("temoin") != "vraie" or vraie["espace_instances"]["nombre_issues"] != K or vraie["espace_instances"]["dimension"] != DIM:
        raise CarteRefusee(f"monde planté : {LOI_VRAIE} n'est pas un témoin vrai à {K} issues et {DIM} traits")
    return {"source": SOURCE_MONDE, "sha256": sha256_fichier(chemin), "loi_vraie": LOI_VRAIE, "loi": vraie["loi_predictive"],
            "fausses": {i: fiches[i]["loi_predictive"] for i in LOIS_FAUSSES},
            "enonce_vrai": vraie["enonce"]}


def oracle(loi, monde, racine):
    """Mesures d'audit (jamais servies ni décisives) : gain attendu de log-score de la loi sur la marginale du monde (nat par
    épisode) et divergence moyenne de la loi plantée à la loi, sur ORACLE instances fixées par la tâche « oracle »."""
    rng = random.Random(bf.graine_de_tache(racine, "oracle|instances"))
    instances = sp.tirer_instances(rng, ORACLE, DIM)
    P = [sp.proba(monde["loi"], x, [], 0) for x in instances]
    marg = [sum(p[k] for p in P) / len(P) for k in range(K)]
    gain, kl = 0.0, 0.0
    for x, p in zip(instances, P):
        q = sp.proba(loi, x, [], 0)
        gain += sum(pk * (math.log(max(qk, 1e-12)) - math.log(mk)) for pk, qk, mk in zip(p, q, marg))
        kl += sum(pk * (math.log(pk) - math.log(max(qk, 1e-12))) for pk, qk in zip(p, q) if pk > 0)
    return {"gain_attendu_nat": round(gain / len(instances), 6), "divergence_a_la_loi_plantee_nat": round(kl / len(instances), 6),
            "est_la_loi_plantee": loi == monde["loi"]}


# --- cartes scriptées ----------------------------------------------------------------------------------------------------------


def cartes_scriptees(generation, monde, vue):
    """(cartes, scénarios de l'expérimentateur). Génération 1 : l'amorce ; génération ≥ 2 : copie et mélange des lois de la vue,
    plus une loi fausse (S-F4)."""
    p, v = f"G{generation}", monde["loi"]
    if generation == 1:
        anti = {"type": "softmax", "poids": [[-w for w in ligne] for ligne in v["poids"]], "biais": list(v["biais"])}
        cartes = [pr.carte(f"{p}-VRAIE", "Loi plantée (témoin vrai S-V1 de l'exemple)", v, "scripte"),
                  pr.carte(f"{p}-FAUSSE-1", "Loi fausse S-F1 de l'exemple", monde["fausses"]["S-F1"], "scripte"),
                  pr.carte(f"{p}-FAUSSE-2", "Loi fausse S-F2 de l'exemple", monde["fausses"]["S-F2"], "scripte"),
                  pr.carte(f"{p}-FAUSSE-3", "Anti-loi (poids opposés à la loi plantée)", anti, "scripte"),
                  pr.carte(f"{p}-INCONCLUSIVE", "Loi plantée tempérée (fichier brut non écrit)",
                           {"type": "transformee", "base": v, "puissance": 0.8}, "scripte"),
                  pr.carte(f"{p}-ELIMINEE", "Loi plantée accentuée, gain préenregistré d'au moins 2 nat",
                           {"type": "transformee", "base": v, "puissance": 1.25}, "scripte",
                           test_de_mort=dict(pr.TEST_DE_MORT, seuil="au moins 2,0")),
                  dict(pr.carte(f"{p}-MALFORMEE", "Carte sans bloc statistique", v, "scripte"),
                       test_de_mort={k: x for k, x in pr.TEST_DE_MORT.items() if k != "statistique"})]
        return cartes, {f"{p}-INCONCLUSIVE": "sans_fichier"}
    cartes = []
    for x in vue["lois_retenues"]:
        cartes.append(pr.carte(f"{p}-COPIE-{x['identifiant']}", f"Copie de {x['identifiant']} sous un autre nom", x["loi"], "scripte"))
        cartes.append(pr.carte(f"{p}-MELANGE-{x['identifiant']}", f"{x['identifiant']} mélangée à l'uniforme",
                               {"type": "melange", "composantes": [x["loi"], {"type": "fixe", "probas": [1.0 / K] * K}],
                                "poids": [0.5, 0.5]}, "scripte"))
    cartes.append(pr.carte(f"{p}-FAUSSE-4", "Loi fausse S-F4 de l'exemple", monde["fausses"]["S-F4"], "scripte"))
    return cartes, {}


# --- gardien (forme seule) ---------------------------------------------------------------------------------------------------


def garder(carte):
    """Le gardien du mode à blanc : la forme seule (champs fermés, loi valide au gabarit du monde, champ `test_de_mort` validé
    par l'étage v5, bloc `statistique` compris). Rend (passeport, None) ou (None, motif). En tour réel : `aiguilleur_v53`."""
    if not isinstance(carte, dict):
        return None, "carte non dictionnaire"
    manquants = [c for c in CHAMPS_CARTE if carte.get(c) in (None, "", [], {})]
    inconnus = sorted(set(carte) - set(CHAMPS_CARTE))
    if manquants or inconnus:
        return None, f"champs manquants {manquants} ou inconnus {inconnus}"
    try:
        sp.valider_loi(carte["loi_predictive"], K, DIM)
    except Exception as e:  # noqa: BLE001 — tout refus de la loi est un refus de forme, motif dit
        return None, f"loi prédictive invalide : {type(e).__name__} : {str(e)[:200]}"
    try:
        v5.valider_champ_test(carte["test_de_mort"])
    except v5.ChampTestInvalide as e:
        return None, f"test de mort refusé (étage v5) : {str(e)[:300]}"
    return {"identifiant": carte["identifiant"], "empreinte": empreinte_objet(carte), "classe": "niveau méthode (forme seule)"}, None


# --- juge (nul v8) ------------------------------------------------------------------------------------------------------------


def juger_carte(loi, monde, archive, racine, tache):
    """Jugement d'une carte fraîche sous le nul v8 (appel pour appel `banc_tricheurs_v8.juger_v8`, genre « fraîche »)."""
    rng = random.Random(bf.graine_de_tache(racine, f"{tache}|plan"))
    entrainement = sp.tirer_instances(rng, ENTRAINEMENT, DIM)
    q_ent = _frequences([sp.tirer_categorie(rng, sp.proba(monde["loi"], x, [], 0)) for x in entrainement], K)
    standard = list(sp.BIBLIOTHEQUE_STANDARD) + [{"nom": "marginale_entrainement", "type": "fixe", "probas": q_ent}]
    instances = sp.tirer_instances(rng, TIRAGES, DIM)
    biblio = standard + nul_v8.membres_archive_v8(dict(archive), None, K, DIM)
    gele = sp.geler_engagement(nf.construire_engagement_v2("fiche", loi, instances, K, ALPHA, biblio, 0, None,
                                                           instants_reguliers(TIRAGES, len(nf.INSTANTS_PAR_DEFAUT))))
    graines = {"noyau": bf.graine_de_tache(racine, f"{tache}|noyau"),
               "frais": bf.graine_de_tache(racine, f"{tache}|frais|{gele.empreinte}")}
    tirages = sp.tirer_frais(gele, monde["loi"], graines["frais"], graine_noyau=graines["noyau"])
    ev = nf.evaluer_v2(gele, tirages, graine_noyau=graines["noyau"])
    return ev, {"empreinte_engagement": gele.empreinte, "graines": graines, "membres_du_nul": len(biblio),
                "membres_d_archive": len(biblio) - len(standard)}


def juger_generation(cartes, monde, archive, racine, tache):
    """Juge chaque carte, puis la règle e-BH de la génération ; rend (promues dans l'ordre des e-valeurs, détail par carte)."""
    issues, detail = {}, {}
    for c in cartes:
        ev, d = juger_carte(c["loi_predictive"], monde, archive, racine, f"{tache}|carte={c['identifiant']}")
        issues[c["identifiant"]] = {"verdict_final": "survit" if ev["promue"] else "eliminee", "motif": "", "pari": dict(ev)}
        detail[c["identifiant"]] = dict(d, promue_seule=bool(ev["promue"]), log_richesse_max=round(ev["log_richesse_max"], 6),
                                        membre_dominant_final=ev.get("membre_dominant_final"))
    mult = appliquer_multiplicite(issues, ALPHA) if issues else {"m": 0, "retenues": []}
    for i, issue in issues.items():
        detail[i]["promue"] = issue["verdict_final"] == "survit"
        detail[i]["log_e"] = issue["pari"].get("multiplicite", {}).get("log_e")
    promues = sorted((i for i in issues if detail[i]["promue"]), key=lambda i: (-(detail[i]["log_e"] or -1e9), i))
    return promues, detail, mult["m"]


# --- étage de tests de mort v5 (expérimentateur et vérificateur scriptés) --------------------------------------------------------

SCRIPT = '''import csv, json, math
LOI = json.loads({loi!r})
def norm(p):
    s = sum(p)
    return [x / s for x in p]
def proba(loi, z):
    t = loi["type"]
    if t == "fixe":
        return norm(loi["probas"])
    if t == "softmax":
        sc = [b + sum(w * x for w, x in zip(l, z)) for l, b in zip(loi["poids"], loi["biais"])]
        m = max(sc)
        return norm([math.exp(s - m) for s in sc])
    if t == "melange":
        mix = [0.0] * {k}
        for w, c in zip(loi["poids"], loi["composantes"]):
            mix = [a + w * x for a, x in zip(mix, proba(c, z))]
        return norm(mix)
    if t == "transformee":
        p = proba(loi["base"], z)
        if loi.get("puissance") is not None:
            p = norm([max(x, 1e-12) ** loi["puissance"] for x in p])
        if loi.get("inclinaison"):
            p = norm([x * math.exp(b) for x, b in zip(p, loi["inclinaison"])])
        return p
    raise ValueError(t)
lignes = list(csv.DictReader(open("tranche/episodes.csv", encoding="utf-8")))
comptes = [0.5] * {k}
for r in lignes:
    comptes[int(r["y"])] += 1
marg = norm(comptes)
gains = []
for r in lignes:
    y = int(r["y"])
    p = proba(LOI, [float(r["z0"]), float(r["z1"])])
    gains.append(math.log(max(p[y], 1e-12)) - math.log(marg[y]))
{ecrire}print("RESULTAT: %.6f" % (sum(gains) / len(gains)))
'''
ECRIRE = 'open("gains.csv", "w", encoding="utf-8").write("episode,gain\\n" + "".join("%d,%r\\n" % (i, g) for i, g in enumerate(gains, 1)))\n'


def script_experimentateur(loi, scenario=None):
    return SCRIPT.format(loi=json.dumps(loi), k=K, ecrire="" if scenario == "sans_fichier" else ECRIRE)


def _section(consigne, debut_titre):
    import re
    m = re.search(r"## " + re.escape(debut_titre) + r"[^\n]*\n.*?" + re.escape(DEBUT_DONNEES) + r"\s*```json\n(.*?)\n```\s*"
                  + re.escape(FIN_DONNEES), consigne, re.S)
    return json.loads(m.group(1)) if m else None


def verificateur_temoin(consigne):
    """Le vérificateur scripté (lecteur témoin de l'étage v5, autre famille) : seuil gelé appliqué à la dernière ligne
    `RESULTAT:` de la dernière exécution réussie ; témoin, jamais décisif."""
    prereg = _section(consigne, v5.TITRE_SECTION_PREREG)
    vue = _section(consigne, "Sortie scellée des exécutions") or []
    reussies = [e for e in vue if e["statut"] == "réussie" and e["lignes_resultat"]]
    if not reussies or prereg is None:
        return "VERDICT: non concluant ; chiffre: aucun ; ligne: aucune"
    ligne = reussies[-1]["lignes_resultat"][-1]
    valeur = float(ligne.split(":", 1)[1])
    survit = v5.comparer(valeur, prereg["seuil"]["comparateur"], prereg["seuil"]["valeur"])
    return f"VERDICT: {'survit' if survit else 'éliminée'} ; chiffre: {valeur} ; ligne: {ligne}"


class AdaptateurAblanc:
    """Expérimentateur et vérificateur scriptés de l'étage (aucun appel de modèle, coût nul)."""
    nom = "scripte-a-blanc-v59"

    def __init__(self, lois, scenarios):
        self.lois, self.scenarios, self.appels = dict(lois), dict(scenarios), []

    def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
        if role == v5.ROLE_EXPERIMENTATEUR:
            d_fiche = os.path.dirname(os.path.dirname(dossier))
            ident, tour = os.path.basename(d_fiche), int(os.path.basename(dossier).split("-")[1])
            texte = FIN if tour > 1 else "```json\n" + json.dumps(
                {"experience": [{"executer": {"script": script_experimentateur(self.lois[ident], self.scenarios.get(ident))}}]},
                ensure_ascii=False) + "\n```"
        elif role == v5.ROLE_LECTEUR:
            ident, texte = os.path.basename(os.path.dirname(dossier)), verificateur_temoin(consigne)
        else:
            raise CarteRefusee(f"rôle inattendu à l'étage : {role}")
        self.appels.append({"role": role, "fiche": ident, "modele": modele})
        return Resultat(texte, [], 0.0, "ok")


def creer_tranche(dossier, monde, racine, tache):
    """La tranche exploratoire : EPISODES_TRANCHE épisodes du monde planté (traits, sous-population, issue), graine de la tâche."""
    from . import dossier_ferme as dfm
    from . import ideation_v2 as idn
    rng = random.Random(bf.graine_de_tache(racine, f"{tache}|tranche"))
    lignes = ["episode,z0,z1,g,y"]
    for i, x in enumerate(sp.tirer_instances(rng, EPISODES_TRANCHE, DIM), 1):
        y = sp.tirer_categorie(rng, sp.proba(monde["loi"], x, [], 0))
        lignes.append(f"{i},{x['z'][0]!r},{x['z'][1]!r},{x['g']},{y}")
    tr = os.path.join(dossier, "tranche")
    os.makedirs(tr)
    with open(os.path.join(tr, "episodes.csv"), "w", encoding="utf-8") as f:
        f.write("\n".join(lignes) + "\n")
    dfm.ecrire_index(tr, [{"chemin": "episodes.csv", "titre": "Épisodes du monde planté",
                           "resume": "traits z0, z1, sous-population g, issue y (mode à blanc v59)"}])
    lb = os.path.join(dossier, "liste-blanche.json")
    idn.construire_liste_blanche([os.path.join(tr, "index.json")], lb)
    return v5.charger_tranche(tr, idn.charger_liste_blanche(lb))


def choisir_executeur(bac, *, utilisateur_bac=None, racine_travail=None, which=shutil.which):
    """L'exécuteur des tests de mort : « reel » (bwrap, sonde réussie exigée ; aucun repli) ou « factice » (demandé
    explicitement ; aucune barrière, dit). Rend (exécuteur, description)."""
    if bac == "factice":
        e = v5.ExecuteurFactice(delai_s=60.0)
        return e, dict(e.description(), demande="factice (explicite) : aucune barrière")
    if bac != "reel":
        raise BacASableIndisponible(f"bac : « reel » ou « factice » (reçu {bac!r} ; aucun défaut)")
    if not which("bwrap"):
        raise BacASableIndisponible("bac réel demandé : bwrap absent de cette machine : refus, aucun repli sur l'exécuteur factice")
    if os.geteuid() == 0 and (utilisateur_bac is None or racine_travail is None):
        raise BacASableIndisponible("bac réel sous un noyau superutilisateur : utilisateur dédié sans privilège et dossier racine "
                                    "à lui exigés (--utilisateur-bac) : refus, aucun repli")
    kw = {"utilisateur_bac": utilisateur_bac, "racine_travail": racine_travail} if os.geteuid() == 0 else {}
    e = v5.ExecuteurBacASable(delai_s=60.0, memoire_mo=768, **kw)
    ok, motif = e.disponible()
    if not ok:
        raise BacASableIndisponible(f"bac réel : sonde en échec ({motif}) : refus, aucun repli")
    return e, dict(e.description(), sonde=motif, demande="reel")


def jouer_etage(dossier_etage, cartes_promues, monde, racine, tache, executeur, scenarios, journal):
    """L'étage v5 sur les cartes promues (ordre des e-valeurs) puis la sélection v57 ; sans carte promue, sélection vide scellée
    (étage non joué, dit). Rend (résumé de l'étage ou None, chemin de la sélection, empreinte, appels de l'adaptateur)."""
    if not cartes_promues:
        os.makedirs(dossier_etage)
        selection = selection_entre_generations({"par_fiche": [], "version_etage": None})
        chemin = os.path.join(dossier_etage, NOM_SELECTION)
        return None, chemin, ecrire_json_scelle(chemin, selection), []
    tranche = creer_tranche(os.path.join(os.path.dirname(dossier_etage), "exploratoire-etage"), monde, racine, tache)
    fiches = {c["identifiant"]: preparer({k: c[k] for k in CHAMPS_FICHE}, list(CHAMPS_FICHE), ident=c["identifiant"],
                                         case=("a-blanc", c["source"]), fournisseur="scripte-v59", passe=1) for c in cartes_promues}
    classement = [{"ident": c["identifiant"], "notable": True, "rang": k} for k, c in enumerate(cartes_promues, 1)]
    preparer_generation(dossier_etage, classement, fiches, nombre=len(cartes_promues), tranche_index_sha256=tranche.index_sha256,
                        correspondance=CORRESPONDANCE, lisible=True)
    ad = AdaptateurAblanc({c["identifiant"]: c["loi_predictive"] for c in cartes_promues}, scenarios)
    reglages = {"tranche": tranche, "nombre": len(cartes_promues), "experimentateur": EXPERIMENTATEUR, "lecteur": VERIFICATEUR,
                "executeur": executeur, "moteur": "simule"}
    resume = jouer_etage_v57(ad, dossier_etage, reglages=reglages, environnement=ENV_A_BLANC)
    journal.append({"evenement": "etage-tests-de-mort", "tache": tache, "bac_a_sable": resume["bac_a_sable"].get("nom"),
                    "factice": resume["bac_a_sable"].get("factice"), "tranche_index_sha256": tranche.index_sha256,
                    "comptes": resume["comptes"], "selection_sha256": resume["selection"]["sha256"]})
    return resume, os.path.join(dossier_etage, NOM_SELECTION), resume["selection"]["sha256"], ad.appels


# --- une génération, un bras -------------------------------------------------------------------------------------------------


def proposer(bras, generation, monde, vue, racine, tache, nombre_reference):
    """Cartes d'une génération d'un bras : amorce scriptée en génération 1 (tous les bras), puis les cartes du bras."""
    cartes, scenarios, motifs = [], {}, []
    if generation == 1 or bras == "scripte":
        c, s = cartes_scriptees(generation, monde, bf.exiger_vue_sans_verdict(vue))
        cartes, scenarios = cartes + c, dict(scenarios, **s)
    if bras == "aleatoire":
        c, m = pr.proposer_aleatoire(vue, nombre_reference, racine, tache)
        cartes, motifs = cartes + c, motifs + ([m] if m else [])
    elif bras == "recopie_melange":
        c, m = pr.proposer_recopie_melange(vue, nombre_reference, racine, tache)
        cartes, motifs = cartes + c, motifs + ([m] if m else [])
    return cartes, scenarios, motifs


def jouer_generation(dossier, bras, generation, monde, heritage, racine, executeur_fabrique, nombre_reference, journal):
    tache = f"{VERSION}|bras={bras}|generation={generation}"
    vue = bf.vue_pour_proposeur(heritage)
    cartes, scenarios, motifs = proposer(bras, generation, monde, vue, racine, tache, nombre_reference)
    passees, refusees = [], {}
    for c in cartes:
        passeport, motif = garder(c)
        if passeport is None:
            refusees[c["identifiant"]] = motif
        else:
            passees.append(c)
    promues, detail, m = juger_generation(passees, monde, heritage["archive"], racine, tache)
    par_ident = {c["identifiant"]: c for c in passees}
    executeur, description_bac = executeur_fabrique()
    resume, chemin_sel, sha_sel, appels = jouer_etage(os.path.join(dossier, bf.DOSSIER_ETAGE), [par_ident[i] for i in promues],
                                                      monde, racine, tache, executeur, scenarios, journal)
    verdicts = {r["identifiant_auteur"]: r["verdict_noyau"] for r in (resume or {}).get("par_fiche", []) if r.get("statut") == "testée"}
    survivantes = bf.survivantes_des_verdicts(verdicts)
    with open(chemin_sel, encoding="utf-8") as f:
        retenues = json.load(f)["retenues"]
    oracles = {c["identifiant"]: oracle(c["loi_predictive"], monde, racine) for c in passees}
    comptes = {"proposees": len(cartes), "refusees_au_gardien": len(refusees), "jugees": len(passees), "m_e_bh": m,
               "promues": len(promues), "testees": len(verdicts),
               "verdicts": {x: sum(v["verdict"] == x for v in verdicts.values()) for x in v5.VERDICTS},
               "refusees_a_l_etage": (resume or {}).get("refusees_a_l_etage", 0), "survivantes": len(survivantes),
               "retenues": len(retenues), "promues_puis_survivantes": len([i for i in promues if i in survivantes]),
               "sessions_experimentateur": sum(a["role"] == v5.ROLE_EXPERIMENTATEUR for a in appels),
               "sessions_verificateur": sum(a["role"] == v5.ROLE_LECTEUR for a in appels),
               "executions": sum(len(r.get("executions") or []) for r in (resume or {}).get("par_fiche", [])),
               "tirages_par_carte_jugee": TIRAGES, "episodes_de_tranche": EPISODES_TRANCHE if resume else 0,
               "motifs_du_proposeur": motifs}
    graines = {"tache": tache, "par_carte": {i: d["graines"] for i, d in detail.items()}}
    sha_bilan = bf.ecrire_bilan_generation(dossier, generation=generation, bras=bras, cartes=passees, resume_etage=resume,
                                           chemin_selection=chemin_sel, sha_selection=sha_sel,
                                           archive_precedente=heritage["archive"], heritage_lu=heritage, comptes=comptes,
                                           graines=graines)
    ligne = {"evenement": "generation", "bras": bras, "generation": generation, "heritage_lu": heritage.get("bilan_sha256"),
             "archive_lue": sorted(heritage["archive"]), "refusees_au_gardien": refusees, "promues": promues,
             "verdicts": {i: v["verdict"] for i, v in verdicts.items()}, "retenues": retenues, "comptes": comptes,
             "bac_a_sable": description_bac.get("nom"), "factice": description_bac.get("factice"),
             "selection_sha256": sha_sel, "bilan_sha256": sha_bilan,
             "juge": {i: {k: d[k] for k in ("promue", "promue_seule", "log_richesse_max", "log_e", "membre_dominant_final",
                                            "membres_d_archive", "empreinte_engagement")} for i, d in detail.items()},
             "oracle": oracles}
    journal.append(ligne)
    return sha_bilan, ligne


def jouer_bras(dossier, bras, monde, racine, generations, executeur_fabrique, nombre_reference, journal):
    """Les générations d'un bras ; la génération g+1 lit (vérifié) le bilan scellé de la génération g."""
    lignes, sha_prec, dossier_prec, evaluations_precedentes = [], None, None, None
    for g in range(1, generations + 1):
        d = os.path.join(dossier, f"generation-{g}")
        os.makedirs(d)
        if g == 1:
            heritage = bf.heritage_initial()
        else:
            heritage = bf.lire_heritage(dossier_prec, sha_prec)
        journal.append({"evenement": "heritage-lu", "bras": bras, "generation": g, "bilan_sha256": heritage["bilan_sha256"],
                        "retenues_lues": heritage["retenues"], "archive": sorted(heritage["archive"])})
        sha_prec, ligne = jouer_generation(d, bras, g, monde, heritage, racine, executeur_fabrique, nombre_reference, journal)
        dossier_prec, evaluations_precedentes = d, ligne["juge"]
        lignes.append(ligne)
    fin = bf.lire_heritage(dossier_prec, sha_prec)  # la boucle se referme aussi après la dernière génération (lecture vérifiée)
    journal.append({"evenement": "heritage-final-lu", "bras": bras, "bilan_sha256": sha_prec, "retenues_lues": fin["retenues"],
                    "archive": sorted(fin["archive"]), "evaluations_gardees_hors_vue": sorted(evaluations_precedentes or {})})
    return lignes


def jouer_a_blanc(sortie, *, racine_graines, racine_orchestrateur, bac, generations=2, bras=BRAS, nombre_reference=6,
                  utilisateur_bac=None, which=shutil.which):
    """Le mode à blanc entier ; écrit `journal-a-blanc-v59.json` scellé dans `sortie` (neuve) ; rend le journal."""
    if os.path.exists(sortie):
        raise FileExistsError(f"sortie {sortie} déjà présente (R12)")
    if isinstance(generations, bool) or not isinstance(generations, int) or generations < 2:
        raise ValueError("générations : entier ≥ 2 (la boucle se ferme entre deux générations au moins)")
    os.makedirs(sortie)
    monde = charger_monde(racine_orchestrateur)
    parent_bac = None
    if bac == "reel" and os.geteuid() == 0 and utilisateur_bac is not None:
        parent_bac = os.path.realpath(tempfile.mkdtemp(prefix="bac-a-blanc-v59-"))
        os.chmod(parent_bac, 0o711)
        racine_travail = os.path.join(parent_bac, "bac")
        os.mkdir(racine_travail, 0o700)
        os.chown(racine_travail, int(utilisateur_bac), int(utilisateur_bac))
    else:
        racine_travail = None
    choisir_executeur(bac, utilisateur_bac=utilisateur_bac, racine_travail=racine_travail, which=which)  # refus avant tout

    def fabrique():
        return choisir_executeur(bac, utilisateur_bac=utilisateur_bac, racine_travail=racine_travail, which=which)

    journal = [{"evenement": "depart", "version": VERSION, "racine_graines": racine_graines, "bac": bac,
                "monde": {k: monde[k] for k in ("source", "sha256", "loi_vraie", "enonce_vrai")}, "generations": generations,
                "bras": list(bras), "nombre_reference": nombre_reference, "nul": nul_v8.description(),
                "environnement_etage": sorted(ENV_A_BLANC), "reseau": "aucun", "modeles": "aucun (scriptés)"}]
    resultats = {}
    try:
        for b in bras:
            resultats[b] = jouer_bras(os.path.join(sortie, f"bras-{b}"), b, monde, racine_graines, generations, fabrique,
                                      nombre_reference, journal)
    finally:
        if parent_bac:
            shutil.rmtree(parent_bac, True)
    synthese = {b: [{"generation": l["generation"], **{k: l["comptes"][k] for k in ("proposees", "refusees_au_gardien", "jugees",
                                                                                     "promues", "testees", "survivantes", "retenues",
                                                                                     "promues_puis_survivantes")},
                     "verdicts": l["comptes"]["verdicts"], "retenues_ids": l["retenues"], "heritage_lu": l["heritage_lu"],
                     "bilan_sha256": l["bilan_sha256"]} for l in lignes] for b, lignes in resultats.items()}
    rapport = {"version": VERSION, "journal": journal, "synthese_par_bras": synthese}
    rapport["sha256"] = ecrire_json_scelle(os.path.join(sortie, "journal-a-blanc-v59.json"), rapport)
    return rapport


__all__ = ("jouer_a_blanc", "jouer_bras", "jouer_generation", "choisir_executeur", "garder", "juger_carte", "juger_generation",
           "cartes_scriptees", "charger_monde", "oracle", "BacASableIndisponible", "VERSION", "BRAS", "ENV_A_BLANC")
