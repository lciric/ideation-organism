"""Configuration, version 55 — au-dessus de `configuration_v54` (inchangé, R12). Corrige CL19-05, CL19-09 (spécification
au lancement) et CL19-12 (cohérence de D-g).

1. **Ligne de GO (CL19-05)**. La v54 lisait « 1 045 USD » comme 45 (séparateur de milliers), « 10-45 USD » comme 45,
   acceptait « ≈ 45 USD » et « jusqu'à 45 USD par génération ». En v55 :
   - le montant est lu **entier** : groupes de trois chiffres séparés par une espace, une espace fine (U+2009), une espace
     fine insécable (U+202F) ou une espace insécable (U+00A0) ; décimale par virgule ou point ;
   - après retrait des identifiants de GO (`GO-AAAA-MM-JJ-NN`) et des dates ISO, la cellule ne doit contenir **aucun autre
     nombre** que le montant (plage, alerte, second plafond : refus « nombre étranger au montant ») ;
   - « ≈ », « ~ », « environ », « env. », « approx » refusés ; « par génération » (et « par lancement », « run », « appel »,
     « session », « jour », « instance », « étape ») refusés.
2. **DEP4 (CL19-05)** : la pièce doit contenir mot pour mot la phrase de confirmation `dependances.dep4_phrase` (fixée par
   Lazar ; « À REMPLIR » refusé), plus seulement exister à son empreinte.
3. **Spécification au lancement (CL19-09)** : `verifier_specification(racine)` recalcule l'empreinte du brouillon 7 ; le
   lanceur l'exige pour le moteur réel et la rapporte sinon.
4. **Cohérence (CL19-12)** : `decisions_a15.d_g` (mot de Lazar) doit désigner la même lettre que `prepilote.d_g`.
5. **I-9 (CL19-09)** : `bisociateur.meta.annexe.brouillon_relu` et `.rapport_contre_lecture` sont lus par la déclaration des
   bras (`course2_v55`) ; leur absence fait « non produit (annexe non conforme) », pas un refus de configuration (A20).
"""

import os
import re

from . import configuration_v53 as c53
from . import configuration_v54 as c54
from .configuration_v53 import ConfigurationRefusee, GoRefuse, reel
from .outils import sha256_fichier

VERSION = "configuration-course-2-v55"
MARQUEUR = c54.MARQUEUR
SPECIFICATION, SPECIFICATION_SHA256 = c54.SPECIFICATION, c54.SPECIFICATION_SHA256
ESPACES_MILLIERS = "    "
_G = "[" + ESPACES_MILLIERS + "]"
NOMBRE = r"(?:\d{1,3}(?:" + _G + r"\d{3})+|\d+)(?:[.,]\d+)?"
MONTANT_V55 = re.compile(r"(?<![\d.,])(" + NOMBRE + r")\s*(USD|\$|dollars?|€|EUR|euros?)(?![a-z])", re.I)
TOUT_NOMBRE = re.compile(r"(?<![\d.,])" + NOMBRE)
APPROX = re.compile(r"≈|~|\benviron\b|\benv\.|\bapprox", re.I)
PAR_UNITE = re.compile(r"\bpar\s+(lancement|run|appel|session|jour|instance|g[ée]n[ée]ration|[ée]tape)", re.I)
IDENT_GO = re.compile(r"\bGO-\d{4}-\d{2}-\d{2}-\d{2}\b")
DATE_ISO = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
lire_configuration_v54 = c54.lire_configuration_v54
montant_requis = c54.montant_requis


def _valeur(texte):
    return float(re.sub(_G, "", texte).replace(",", "."))


def montants_v55(cellule):
    return [(_valeur(m.group(1)), m.group(2)) for m in MONTANT_V55.finditer(cellule or "")]


def lire_plafond(cellule):
    """Rend (valeur, unité) du seul montant de la cellule ; lève `GoRefuse` (motif exact) sinon."""
    cellule = cellule or ""
    if APPROX.search(cellule):
        raise GoRefuse(f"A15 : montant approché (« {cellule} ») : plafond exact exigé")
    if PAR_UNITE.search(cellule):
        raise GoRefuse(f"A15 : plafond « par unité » (« {cellule} ») : plafond total exigé")
    ms = montants_v55(cellule)
    if not ms:
        raise GoRefuse(f"A15 : aucun montant lisible (« {cellule} »)")
    if len({(v, u.upper().rstrip("S")) for v, u in ms}) != 1:
        raise GoRefuse(f"A15 : plusieurs montants (« {cellule} ») : un seul plafond exigé")
    reste = DATE_ISO.sub(" ", IDENT_GO.sub(" ", cellule))
    nombres = [_valeur(x) for x in TOUT_NOMBRE.findall(reste)]
    if any(abs(x - ms[0][0]) > 1e-9 for x in nombres):
        raise GoRefuse(f"A15 : nombre étranger au montant dans la cellule (« {cellule} ») : plage, alerte ou second plafond refusés")
    return ms[0]


def verifier_go_v55(go_id, registre, montant_requis_usd, aujourd_hui=None):
    """Contrôles v54 de la ligne (identifiant, type, Lazar, validité, révocations), puis lecture v55 du montant."""
    if not isinstance(go_id, str) or not c53.GO_ID.fullmatch(go_id):
        raise GoRefuse("A15 : aucun lancement sans identifiant de GO exact (GO_ID=GO-AAAA-MM-JJ-NN)")
    if not reel(montant_requis_usd, 0, strict_mini=True):
        raise GoRefuse(f"A15 : montant requis invalide {montant_requis_usd!r}")
    import datetime
    aujourd_hui = aujourd_hui or datetime.datetime.now(datetime.timezone.utc).date()
    reg = c53.lire_registre_go(registre)
    g = reg.get(go_id)
    if g is None:
        raise GoRefuse(f"A15 : {go_id} absent du registre {registre}")
    if g["type"] != "calcul":
        raise GoRefuse(f"A15 : {go_id} est un GO de type {g['type']!r}, pas « calcul »")
    if g["par"] != "Lazar":
        raise GoRefuse(f"A15 : {go_id} n'est pas accordé par Lazar")
    if not (g["accorde"] <= aujourd_hui <= g["echeance"]):
        raise GoRefuse(f"A15 : {go_id} hors de sa période de validité ({g['accorde']} → {g['echeance']})")
    revocations = sorted(k for k, r in reg.items() if r["type"] == "révocation" and (go_id in r["perimetre"] or go_id in r["ref"]))
    if revocations:
        raise GoRefuse(f"A15 : {go_id} révoqué par {', '.join(revocations)}")
    valeur, unite = lire_plafond(g["plafond"])
    if unite.upper() not in ("USD", "$", "DOLLAR", "DOLLARS"):
        raise GoRefuse(f"A15 : la ligne {go_id} porte un montant en {unite} : USD exigé")
    if abs(valeur - float(montant_requis_usd)) > 1e-9:
        raise GoRefuse(f"A15 : la ligne {go_id} porte {valeur:g} USD, pas exactement le plafond requis {float(montant_requis_usd):g} "
                       "USD : aucun lancement à un autre plafond (plus petit ou plus grand)")
    return dict(g, accorde=g["accorde"].isoformat(), echeance=g["echeance"].isoformat(), identifiant=go_id,
                plafond_lu_usd=valeur, montant_requis_usd=float(montant_requis_usd))


def verifier_dependances_lancement_v55(conf, plan="course"):
    manques = c54.verifier_dependances_lancement(conf, plan)
    nom, present = c53._get(conf, "dependances.dep4")
    phrase, p_present = c53._get(conf, "dependances.dep4_phrase")
    if not p_present or not isinstance(phrase, str) or not phrase.strip() or MARQUEUR in phrase:
        manques.append("dependances.dep4_phrase : phrase de confirmation fixée par Lazar exigée (CL19-05)")
    elif present and isinstance(nom, str) and nom in (conf.get("pieces") or {}):
        try:
            if phrase.strip() not in c53.texte_piece(conf, nom):
                manques.append("dependances.dep4 : la pièce ne contient pas la phrase de confirmation exigée")
        except (ConfigurationRefusee, OSError) as e:
            manques.append(f"dependances.dep4 : {e}")
    if plan == "pre_pilote" and isinstance(conf.get("decisions_a15"), dict) and isinstance(conf.get("prepilote"), dict):
        mot = conf["decisions_a15"].get("d_g")
        lettre = re.match(r"\s*\(?([ab])\)?(?![a-z])", mot or "", re.I)
        if isinstance(mot, str) and MARQUEUR not in mot and (lettre is None or lettre.group(1).lower() != conf["prepilote"].get("d_g")):
            manques.append(f"decisions_a15.d_g (« {mot} ») ne désigne pas prepilote.d_g = {conf['prepilote'].get('d_g')!r} (CL19-12)")
    return manques


def trouver_racine_depot(depart):
    d = os.path.realpath(depart)
    while True:
        if os.path.isfile(os.path.join(d, SPECIFICATION)):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def verifier_specification(depart):
    """Rend {chemin, sha256, conforme} ; `conforme` None si le fichier n'est pas trouvé au-dessus de `depart`."""
    racine = trouver_racine_depot(depart)
    if racine is None:
        return {"chemin": SPECIFICATION, "sha256": None, "conforme": None}
    sha = sha256_fichier(os.path.join(racine, SPECIFICATION))
    return {"chemin": SPECIFICATION, "sha256": sha, "conforme": sha == SPECIFICATION_SHA256}


__all__ = ("lire_plafond", "verifier_go_v55", "verifier_dependances_lancement_v55", "verifier_specification", "montants_v55",
           "ConfigurationRefusee", "GoRefuse")
