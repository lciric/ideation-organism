"""Configuration de la course 2 et de son pré-pilote (v53) : **paramètres injectés**, aucun seuil codé.

Le préenregistrement du pré-pilote (brouillon 6, non gelé) laisse ses seuils « À REMPLIR ». La v53 ne les fixe pas : chaque
seuil, plafond, longueur, règle d'agrégation et paramètre de bras est lu dans un fichier de configuration JSON. **Refus de
partir** (`ConfigurationRefusee`, avant tout appel et toute écriture) si un paramètre obligatoire manque, s'il porte encore
le marqueur « À REMPLIR », ou si une pièce empreintée (consigne figée, annexe du bras méta, source du substitut inspiré de
Gu et Krenn, liste fermée des concepts) n'a pas l'empreinte écrite dans la configuration. Tous les manques sont listés en
une fois.

A15 (aucun lancement sans ligne de GO au plafond gelé S17) : `verifier_go` lit `registres/go.md` comme la garde du dépôt
(`.claude/hooks/garde_calcul.py` : table à 8 colonnes, type « calcul », accordé par Lazar, période de validité, aucune
révocation), et exige en plus que la cellule « plafond » de la ligne couvre le plafond S17 de la configuration.
"""

import datetime
import json
import math
import os
import re

from .outils import empreinte_objet, sha256_fichier

VERSION = "configuration-course-2-v53"
MARQUEUR = "À REMPLIR"
GO_ID = re.compile(r"^GO-\d{4}-\d{2}-\d{2}-\d{2}$")
LIGNE_GO = re.compile(r"^\|\s*(GO-\d{4}-\d{2}-\d{2}-\d{2})\s*\|")
REGLES_AGREGATION = ("au_moins", "unanimite", "majorite_stricte")
BRAS_CONNUS = ("meta", "gu_krenn", "basique")
ROLES_ETAPE = ("protegee", "sacrifiable", "reductible", "protegee_hors_porte")


class ConfigurationRefusee(ValueError):
    pass


class GoRefuse(ConfigurationRefusee):
    pass


# --- lecture des valeurs -------------------------------------------------------------------------------------------------


def _marqueurs(objet, chemin=""):
    if isinstance(objet, str):
        return [chemin or "(racine)"] if MARQUEUR in objet else []
    if isinstance(objet, list):
        return [m for i, v in enumerate(objet) for m in _marqueurs(v, f"{chemin}[{i}]")]
    if isinstance(objet, dict):
        return [m for k, v in objet.items() for m in _marqueurs(v, f"{chemin}.{k}" if chemin else k)]
    return []


def _get(d, chemin):
    v = d
    for k in chemin.split("."):
        if not isinstance(v, dict) or k not in v:
            return None, False
        v = v[k]
    return v, True


def reel(v, mini=None, maxi=None, strict_mini=False):
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
        return False
    if mini is not None and (v <= mini if strict_mini else v < mini):
        return False
    return maxi is None or v <= maxi


def entier(v, mini=None):
    return not isinstance(v, bool) and isinstance(v, int) and (mini is None or v >= mini)


# --- schéma : (chemin, contrôle, description) ----------------------------------------------------------------------------

OBLIGATOIRES = (
    ("racine_graines", lambda v: entier(v, 0), "racine des graines du run (R9), entier ≥ 0"),
    ("champs_fiche", lambda v: isinstance(v, list) and v and all(isinstance(c, str) and c for c in v),
     "champs obligatoires d'une fiche au format du texte I (DEP1)"),
    ("champ_titre", lambda v: isinstance(v, str) and v, "champ de la fiche qui porte le titre"),
    ("budget.plafond_usd", lambda v: reel(v, 0, strict_mini=True), "S17 : plafond (USD)"),
    ("budget.arret_etape_usd", lambda v: v == "sans" or reel(v, 0, strict_mini=True), "S17 : arrêt d'étape (USD) ou « sans »"),
    ("budget.etapes", lambda v: isinstance(v, list) and v, "étapes du plan (attendu, réservation, rôle)"),
    ("juges", lambda v: isinstance(v, list) and v, "juges (étiquette, modèle, fournisseur, consigne)"),
    ("items_juge", lambda v: isinstance(v, list) and v and all(isinstance(c, str) and c for c in v) and len(set(v)) == len(v),
     "items de l'étage 2 lus sur la consigne figée (k, M1)"),
    ("agregation.regle", lambda v: v in REGLES_AGREGATION, f"règle d'agrégation des juges {REGLES_AGREGATION}"),
    ("aiguilleur.etiquette", lambda v: isinstance(v, str) and v, "étiquette de l'aiguilleur"),
    ("aiguilleur.modele", lambda v: isinstance(v, str) and v, "modèle de l'aiguilleur"),
    ("aiguilleur.consigne", lambda v: isinstance(v, str) and v, "pièce : consigne figée de l'aiguilleur"),
    ("aiguilleur.fournisseur", lambda v: isinstance(v, str) and v, "fournisseur (adaptateur) de l'aiguilleur"),
    ("garde_kimi.debordement_max", lambda v: reel(v, 0, 1), "S12 : débordement maximal du proposeur Kimi"),
    ("tableau.longueur_max_titre", lambda v: entier(v, 1), "S21 : longueur maximale d'un titre"),
    ("tableau.longueur_max_resume", lambda v: entier(v, 1), "S21 : longueur maximale d'un résumé"),
    ("tableau.champ_resume", lambda v: isinstance(v, str) and v, "champ tronqué en résumé d'une ligne (M8)"),
    ("memoire.methode", lambda v: v in ("bardeaux", "plongement"), "M3 : méthode (bardeaux ; plongement injecté)"),
    ("memoire.taille_bardeau", lambda v: entier(v, 1), "M3 : taille des bardeaux de mots"),
    ("memoire.seuil", lambda v: reel(v, 0, 1), "M3 : seuil t* de similarité"),
    ("bisociateur.bras", lambda v: isinstance(v, list) and set(v) <= set(BRAS_CONNUS) and len(set(v)) == len(v),
     f"bras du bisociateur parmi {BRAS_CONNUS}"),
    ("bisociateur.k_paires", lambda v: entier(v, 0), "S22/S23 : paires par bras et par session"),
    ("pieces", lambda v: isinstance(v, dict) and v, "pièces empreintées {nom: {chemin, sha256}}"),
    ("etiquettes_interdites", lambda v: isinstance(v, list) and v and all(isinstance(x, str) and x for x in v),
     "A4 : étiquettes interdites dans toute entrée servie"),
)

OBLIGATOIRES_BRAS = {
    "meta": (("bisociateur.meta.annexe.chemin", lambda v: isinstance(v, str) and v, "annexe scellée du bras méta (A20)"),
             ("bisociateur.meta.annexe.sha256", lambda v: isinstance(v, str) and re.fullmatch(r"[0-9a-f]{64}", v or ""),
              "empreinte de l'annexe écrite au préenregistrement")),
    "gu_krenn": (("bisociateur.gu_krenn.source.chemin", lambda v: isinstance(v, str) and v, "source gelée de S31 (A19)"),
                 ("bisociateur.gu_krenn.source.sha256", lambda v: isinstance(v, str) and re.fullmatch(r"[0-9a-f]{64}", v or ""),
                  "empreinte de la source de S31"),
                 ("bisociateur.gu_krenn.oeuvres_min_vocabulaire", lambda v: entier(v, 1), "S31 (ii) : œuvres minimales"),
                 ("bisociateur.gu_krenn.date_debut", lambda v: isinstance(v, str) and _date(v), "S31 (iv) : début"),
                 ("bisociateur.gu_krenn.date_coupure", lambda v: isinstance(v, str) and _date(v), "S31 (iv) : coupure"),
                 ("bisociateur.gu_krenn.actif_depuis", lambda v: isinstance(v, str) and _date(v), "S31 (v) : début d'« actif »"),
                 ("bisociateur.gu_krenn.actif_min_oeuvres", lambda v: entier(v, 1), "S31 (v) : œuvres pour « actif »")),
    "basique": (("bisociateur.basique.exposant", lambda v: reel(v, 0, strict_mini=True), "score basique : exposant"),
                ("bisociateur.basique.decalage", lambda v: reel(v, 0), "score basique : décalage de κ"),
                ("bisociateur.basique.liste_concepts", lambda v: isinstance(v, str) and v, "pièce : liste fermée des concepts")),
}


def _date(texte):
    try:
        datetime.date.fromisoformat(texte)
        return True
    except ValueError:
        return False


def lire_configuration(chemin_ou_objet, base=None):
    """Rend la configuration vérifiée (dict, avec `empreinte_configuration`) ; lève `ConfigurationRefusee` avec la liste
    complète des manques. `base` : dossier où se résolvent les chemins relatifs (défaut : celui du fichier)."""
    if isinstance(chemin_ou_objet, dict):
        conf = json.loads(json.dumps(chemin_ou_objet))
        base = base or os.getcwd()
    else:
        with open(chemin_ou_objet, "r", encoding="utf-8") as f:
            conf = json.load(f)
        base = base or os.path.dirname(os.path.abspath(chemin_ou_objet))
    manques = [f"marqueur « {MARQUEUR} » encore présent : {m}" for m in _marqueurs(conf)]
    for chemin, controle, quoi in OBLIGATOIRES:
        v, present = _get(conf, chemin)
        if not present:
            manques.append(f"{chemin} manquant ({quoi})")
        elif not controle(v):
            manques.append(f"{chemin} invalide ({quoi}) : {v!r}")
    bras = _get(conf, "bisociateur.bras")[0] if isinstance(_get(conf, "bisociateur.bras")[0], list) else []
    for b in bras:
        for chemin, controle, quoi in OBLIGATOIRES_BRAS.get(b, ()):
            v, present = _get(conf, chemin)
            if not present:
                manques.append(f"{chemin} manquant ({quoi} ; bras {b} demandé)")
            elif not controle(v):
                manques.append(f"{chemin} invalide ({quoi}) : {v!r}")
    regle, _ = _get(conf, "agregation.regle")
    juges = conf.get("juges") if isinstance(conf.get("juges"), list) else []
    if regle == "au_moins":
        q, present = _get(conf, "agregation.q")
        if not present or not entier(q, 1) or q > max(len(juges), 1):
            manques.append(f"agregation.q : entier de 1 au nombre de juges ({len(juges)}) exigé par la règle « au_moins »")
    etiquettes = []
    for i, j in enumerate(juges):
        if not isinstance(j, dict) or not all(isinstance(j.get(c), str) and j.get(c) for c in ("etiquette", "modele",
                                                                                                 "fournisseur", "consigne")):
            manques.append(f"juges[{i}] : {{etiquette, modele, fournisseur, consigne}} exigés")
        else:
            etiquettes.append(j["etiquette"])
    if len(set(etiquettes)) != len(etiquettes):
        manques.append("juges : étiquettes en double")
    etapes = _get(conf, "budget.etapes")[0]
    if isinstance(etapes, list):
        manques += _verifier_etapes(etapes)
    if not manques:
        manques += _verifier_pieces(conf, base, bras)
    if manques:
        raise ConfigurationRefusee("configuration refusée avant tout appel (" + str(len(manques)) + " manque(s)) :\n- "
                                   + "\n- ".join(manques))
    conf["_base"] = base
    conf["empreinte_configuration"] = empreinte_objet({k: v for k, v in conf.items() if not k.startswith("_")})
    return conf


def _verifier_etapes(etapes):
    manques, noms = [], set()
    for i, e in enumerate(etapes):
        if not isinstance(e, dict):
            manques.append(f"budget.etapes[{i}] : objet attendu")
            continue
        if not isinstance(e.get("nom"), str) or not e["nom"] or e["nom"] in noms:
            manques.append(f"budget.etapes[{i}].nom : chaîne unique exigée")
        noms.add(e.get("nom"))
        for c in ("attendu_usd", "reservation_usd"):
            if not reel(e.get(c), 0):
                manques.append(f"budget.etapes[{i}].{c} : réel ≥ 0 exigé")
        if e.get("role") not in ROLES_ETAPE:
            manques.append(f"budget.etapes[{i}].role ∈ {ROLES_ETAPE}")
        if e.get("role") == "sacrifiable" and not entier(e.get("rang"), 1):
            manques.append(f"budget.etapes[{i}].rang : entier ≥ 1 exigé pour une étape sacrifiable")
        if e.get("role") == "reductible":
            if not entier(e.get("rang"), 1):
                manques.append(f"budget.etapes[{i}].rang : entier ≥ 1 exigé pour une étape réductible")
            r = e.get("reduite")
            if not isinstance(r, dict) or not reel(r.get("attendu_usd"), 0) or not reel(r.get("reservation_usd"), 0):
                manques.append(f"budget.etapes[{i}].reduite : {{attendu_usd, reservation_usd}} exigés")
    rangs = [e.get("rang") for e in etapes if isinstance(e, dict) and e.get("role") in ("sacrifiable", "reductible")]
    if len(set(rangs)) != len(rangs):
        manques.append("budget.etapes : rangs de sacrifice en double")
    return manques


def chemin_piece(conf, chemin, base=None):
    base = base or conf.get("_base") or os.getcwd()
    return chemin if os.path.isabs(chemin) else os.path.normpath(os.path.join(base, chemin))


def _verifier_pieces(conf, base, bras):
    manques = []
    pieces = conf["pieces"]
    for nom, p in pieces.items():
        if not isinstance(p, dict) or not isinstance(p.get("chemin"), str) or not re.fullmatch(r"[0-9a-f]{64}", str(p.get("sha256"))):
            manques.append(f"pieces.{nom} : {{chemin, sha256 (64 hexadécimaux)}} exigés")
            continue
        reel_ = chemin_piece(conf, p["chemin"], base)
        if not os.path.isfile(reel_):
            manques.append(f"pieces.{nom} : fichier absent ({p['chemin']})")
        elif sha256_fichier(reel_) != p["sha256"]:
            manques.append(f"pieces.{nom} : empreinte différente de celle écrite (A16)")
    requises = {conf["aiguilleur"]["consigne"]} | {j["consigne"] for j in conf["juges"]}
    if "basique" in bras:
        requises.add(conf["bisociateur"]["basique"]["liste_concepts"])
    for nom in ("consigne_fusion", "consigne_lecteur_etiquettes"):
        if bras and conf["bisociateur"].get("k_paires", 0) > 0:
            requises.add(conf["bisociateur"].get(nom) or f"(bisociateur.{nom} manquant)")
    for nom in sorted(requises):
        if nom not in pieces:
            manques.append(f"pièce {nom!r} citée mais absente de « pieces »")
    return manques


def texte_piece(conf, nom):
    """Le texte d'une pièce, relu et revérifié à son empreinte (A16) au moment de l'usage."""
    p = conf["pieces"][nom]
    reel_ = chemin_piece(conf, p["chemin"])
    with open(reel_, "rb") as f:
        octets = f.read()
    from .outils import sha256_octets
    if sha256_octets(octets) != p["sha256"]:
        raise ConfigurationRefusee(f"pièce {nom} modifiée depuis la lecture de la configuration (A16) : arrêt")
    return octets.decode("utf-8")


# --- A15 : la ligne de GO --------------------------------------------------------------------------------------------------


def lire_registre_go(chemin):
    """Même lecture que la garde du dépôt : `| id | accordé le | type | périmètre | plafond | échéance | accordé par | réf. |`."""
    if not os.path.isfile(chemin):
        raise GoRefuse(f"registre des GO absent ({chemin}) : aucun GO ne peut être établi (A15)")
    go = {}
    with open(chemin, "r", encoding="utf-8") as f:
        lignes = f.read().splitlines()
    for n, ligne in enumerate(lignes, 1):
        if not LIGNE_GO.match(ligne):
            continue
        cellules = [c.strip() for c in ligne.strip().strip("|").split("|")]
        if len(cellules) != 8:
            raise GoRefuse(f"registre des GO mal formé ligne {n} : 8 colonnes attendues, {len(cellules)} trouvées")
        ident, accorde, typ, perimetre, plafond, echeance, par, ref = cellules
        try:
            accorde_d = datetime.date.fromisoformat(accorde)
            echeance_d = None if (echeance == "—" and typ != "calcul") else datetime.date.fromisoformat(echeance)
        except ValueError:
            raise GoRefuse(f"registre des GO mal formé ligne {n} : dates illisibles") from None
        if ident in go:
            raise GoRefuse(f"registre des GO : identifiant {ident} en double")
        go[ident] = {"accorde": accorde_d, "type": typ, "perimetre": perimetre, "plafond": plafond, "echeance": echeance_d,
                     "par": par, "ref": ref, "ligne": n}
    return go


def montant_plafond(cellule):
    """Le plus grand montant en dollars écrit dans la cellule « plafond » (« 45 USD », « ≤ 45 USD ») ; None si aucun."""
    montants = [float(m.replace(",", ".")) for m in re.findall(r"(\d+(?:[.,]\d+)?)\s*(?:USD|\$|dollars?)", cellule or "")]
    return max(montants) if montants else None


def verifier_go(go_id, registre, plafond_usd, aujourd_hui=None):
    """A15 : rend la ligne de GO (dict) si elle autorise ce lancement au plafond S17 ; lève `GoRefuse` sinon. Aucune clé
    lue ; seul `GO_ID` (identifiant public) est consulté."""
    if not isinstance(go_id, str) or not GO_ID.match(go_id):
        raise GoRefuse("A15 : aucun lancement sans ligne de GO citée (GO_ID=GO-AAAA-MM-JJ-NN)")
    aujourd_hui = aujourd_hui or datetime.datetime.now(datetime.timezone.utc).date()
    reg = lire_registre_go(registre)
    g = reg.get(go_id)
    if g is None:
        raise GoRefuse(f"A15 : {go_id} absent de {registre}")
    if g["type"] != "calcul":
        raise GoRefuse(f"A15 : {go_id} est un GO de type {g['type']!r}, pas « calcul »")
    if g["par"] != "Lazar":
        raise GoRefuse(f"A15 : {go_id} n'est pas accordé par Lazar")
    if not (g["accorde"] <= aujourd_hui <= g["echeance"]):
        raise GoRefuse(f"A15 : {go_id} hors de sa période de validité ({g['accorde']} → {g['echeance']})")
    revocations = sorted(k for k, r in reg.items() if r["type"] == "révocation" and (go_id in r["perimetre"] or go_id in r["ref"]))
    if revocations:
        raise GoRefuse(f"A15 : {go_id} révoqué par {', '.join(revocations)}")
    montant = montant_plafond(g["plafond"])
    if montant is None or montant + 1e-9 < float(plafond_usd):
        raise GoRefuse(f"A15 : la ligne {go_id} (plafond « {g['plafond']} ») ne couvre pas le plafond gelé S17 = "
                       f"{float(plafond_usd):g} USD : aucun lancement à un autre plafond")
    return dict(g, accorde=g["accorde"].isoformat(), echeance=g["echeance"].isoformat(), identifiant=go_id,
                plafond_lu_usd=montant)
