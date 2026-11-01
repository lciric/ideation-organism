"""Configuration, version 56 — au-dessus de `configuration_v53`, `_v54`, `_v55` (inchangés, R12). Contre-lecture CL20.

1. **Plan de dépense (CL20-02)** : chaque étape porte `attendu_usd` et `plafond_relais_usd` (et, réductible, `reduite: {attendu_usd,
   plafond_relais_usd}`) ; `reservation_usd` est **refusée** (règle « réservation » du brouillon 7, sans objet au brouillon 10).
   La lecture v53 exige le nom `reservation_usd` : elle reçoit une copie où ce nom porte le plafond de relais, puis le plan v56
   est remis tel quel et l'empreinte de la configuration est recalculée sur le texte réel (aucun `reservation_usd` ne reste).
2. **DEP4 et A15 du brouillon 10 (CL20-02)** : plus de phrase de confirmation de la règle « réservation » (`dependances.dep4_phrase`
   refusée : sans objet) ; au moteur réel, chaque fournisseur porte `porte_plafond` (relais capable de recevoir, au lancement
   de chaque étape, le plafond dur calculé selon A1) ; `dependances.dep4`, s'il est donné, reste une pièce vérifiée à son
   empreinte (information).
3. **Spécification au lancement (CL20-03)** : `specification.preenregistrement` et `specification.contre_lecture` (`{chemin,
   sha256}`) : fichiers présents, à leur empreinte, **scellés** (compagnon `.sha256` égal), préenregistrement **sans marqueur**
   de remplissage (« À REMPLIR », « À FOURNIR AU SCELLEMENT ») et citant l'empreinte de sa contre-lecture ; exigée conforme au
   moteur réel, rapportée sinon ; écrite au manifeste (la v55 écrivait « brouillon 7 » en dur).
4. **Gu-Krenn (CL20-10)** : `bisociateur.gu_krenn.mode` exigé ∈ {substitut} ; « modele » refusé avec son motif (non branché en
   v56 ; la bascule d'A19 vers le substitut se déclare en écrivant « substitut »), jamais « source absente ».
5. **D-i (CL20-07)** et **D-g** : au moteur réel, `decisions_a15.d_i` doit désigner la même variante que `prepilote.d_i` (comme
   D-g, CL19-12) ; la v56 ne code que la variante (1) (refus de (2) et (3) à la configuration du pré-pilote).
"""

import copy
import json
import os
import re

from . import configuration_v53 as c53
from . import configuration_v54 as c54
from . import configuration_v55 as c55
from .budget_v56 import verifier_etapes_v56
from .configuration_v53 import ConfigurationRefusee, GoRefuse
from .outils import empreinte_objet, sha256_fichier, verifier_scelle

VERSION = "configuration-course-2-v56"
MARQUEUR = c53.MARQUEUR
MARQUEURS_SPECIFICATION = ("À REMPLIR", "À FOURNIR AU SCELLEMENT")
SHA = re.compile(r"[0-9a-f]{64}")
montant_requis = c54.montant_requis
verifier_go_v56 = c55.verifier_go_v55
lire_plafond = c55.lire_plafond


def _ombre_v53(conf):
    """Copie pour la lecture v53 : `reservation_usd` = plafond de relais (nom exigé par la v53), jamais gardée."""
    o = copy.deepcopy(conf)
    for e in ((o.get("budget") or {}).get("etapes") or []):
        if isinstance(e, dict):
            e.setdefault("reservation_usd", e.get("plafond_relais_usd", 0.0))
            if isinstance(e.get("reduite"), dict):
                e["reduite"].setdefault("reservation_usd", e["reduite"].get("plafond_relais_usd", 0.0))
    return o


def _cles_v56(conf):
    manques = []
    b = conf.get("bisociateur") or {}
    if "gu_krenn" in (b.get("bras") or []):
        mode = (b.get("gu_krenn") or {}).get("mode")
        if mode == "modele":
            manques.append("bisociateur.gu_krenn.mode = « modele » : modèle de Gu-Krenn non branché en v56 (CL20-10) — déclarer "
                           "« substitut » (bascule d'A19, écrite au manifeste) ou attendre un modèle codé ; jamais « source absente »")
        elif mode != "substitut":
            manques.append(f"bisociateur.gu_krenn.mode : « substitut » exigé (A19, CL20-10 ; reçu {mode!r}, aucun défaut)")
    dep = conf.get("dependances") or {}
    if "dep4_phrase" in dep:
        manques.append("dependances.dep4_phrase : phrase de la règle « réservation » du brouillon 7, sans objet au brouillon 10 "
                       "(DEP4 : chaque relais lancé avec le plafond dur calculé) — retirer la clé (CL20-02)")
    spec = conf.get("specification")
    if spec is not None:
        if not isinstance(spec, dict):
            manques.append("specification : {preenregistrement, contre_lecture} attendu")
        else:
            for k in ("preenregistrement", "contre_lecture"):
                p = spec.get(k)
                if not isinstance(p, dict) or not isinstance(p.get("chemin"), str) or not SHA.fullmatch(str(p.get("sha256"))):
                    manques.append(f"specification.{k} : {{chemin, sha256 (64 hexadécimaux)}} exigés")
    for nom, f in (conf.get("fournisseurs") or {}).items():
        pp = (f or {}).get("porte_plafond")
        if pp is None:
            continue
        if not isinstance(pp, dict) or pp.get("type") not in ("commande", "environnement"):
            manques.append(f"fournisseurs.{nom}.porte_plafond.type ∈ (commande, environnement)")
        elif pp["type"] == "environnement" and (f or {}).get("type") != "commande_externe":
            manques.append(f"fournisseurs.{nom}.porte_plafond « environnement » : commande externe seulement")
        elif pp["type"] == "commande" and (not isinstance(pp.get("commande"), list) or not pp["commande"]
                                           or not c53.reel(pp.get("delai_s"), 0, strict_mini=True)):
            manques.append(f"fournisseurs.{nom}.porte_plafond : {{commande (liste), delai_s (> 0)}} exigés")
    return manques


def lire_configuration_v56(chemin_ou_objet, base=None):
    """Lecture v54 (marqueurs, obligatoires, pièces, clés v54) sur la copie d'ombre, plan de dépense v56, clés v56 ; tous les
    manques en une fois. Rend la configuration (plan v56 intact, empreinte recalculée sur le texte réel)."""
    if isinstance(chemin_ou_objet, dict):
        brut = json.loads(json.dumps(chemin_ou_objet))
        base = base or os.getcwd()
    else:
        with open(chemin_ou_objet, "r", encoding="utf-8") as f:
            brut = json.load(f)
        base = base or os.path.dirname(os.path.abspath(chemin_ou_objet))
    manques = list(verifier_etapes_v56((brut.get("budget") or {}).get("etapes")))
    manques += _cles_v56(brut)
    conf = None
    try:
        conf = c54.lire_configuration_v54(_ombre_v53(brut), base=base)
    except ConfigurationRefusee as e:
        manques.append(str(e))
    if manques:
        raise ConfigurationRefusee("configuration v56 refusée avant tout appel :\n- " + "\n- ".join(manques))
    conf["budget"]["etapes"] = copy.deepcopy(brut["budget"]["etapes"])
    conf["version_configuration"] = VERSION
    conf["empreinte_configuration"] = empreinte_objet({k: v for k, v in conf.items() if not k.startswith("_")
                                                       and k not in ("empreinte_configuration", "version_configuration")})
    return conf


# --- CL20-03 : spécification scellée -------------------------------------------------------------------------------------------


def verifier_specification_v56(conf):
    """Rend {preenregistrement, contre_lecture, conforme, motif} ; `conforme` None si la configuration ne nomme aucune
    spécification (moteur simulé seulement), False avec le motif sinon."""
    spec = conf.get("specification")
    if spec is None:
        return {"conforme": None, "motif": "aucune spécification nommée (specification.preenregistrement) : moteur simulé seulement"}
    sortie = {"conforme": False, "motif": None}
    for k in ("preenregistrement", "contre_lecture"):
        p = spec[k]
        chemin = c53.chemin_piece(conf, p["chemin"])
        d = {"chemin": p["chemin"], "sha256": p["sha256"]}
        sortie[k] = d
        if not os.path.isfile(chemin):
            sortie["motif"] = f"{k} absent ({p['chemin']})"
            return sortie
        if sha256_fichier(chemin) != p["sha256"]:
            sortie["motif"] = f"{k} à empreinte différente de celle écrite ({p['sha256'][:8]}…)"
            return sortie
        if not verifier_scelle(chemin):
            sortie["motif"] = f"{k} non scellé (compagnon .sha256 absent ou faux)"
            return sortie
        d["scelle"] = True
    with open(c53.chemin_piece(conf, spec["preenregistrement"]["chemin"]), encoding="utf-8") as f:
        texte = f.read()
    restants = {m: texte.count(m) for m in MARQUEURS_SPECIFICATION if m in texte}
    if restants:
        sortie["motif"] = f"préenregistrement non gelé : marqueurs restants {restants}"
        return sortie
    if spec["contre_lecture"]["sha256"] not in texte:
        sortie["motif"] = "le préenregistrement ne cite pas l'empreinte de sa contre-lecture"
        return sortie
    sortie.update(conforme=True, motif=None)
    return sortie


# --- A15, DEP4 (brouillon 10) ----------------------------------------------------------------------------------------------------


def _lettre(mot, permis):
    m = re.match(r"\s*\(?([" + permis + r"])\)?(?![\w])", mot or "", re.I)
    return m.group(1).lower() if m else None


def verifier_dependances_lancement_v56(conf, plan="course"):
    """Moteur réel seulement. Rend la liste des manques (vide = conforme)."""
    manques = []
    nom = (conf.get("dependances") or {}).get("dep4")
    if nom is not None:
        if nom not in (conf.get("pieces") or {}):
            manques.append(f"dependances.dep4 : pièce {nom!r} absente de « pieces »")
        else:
            try:
                c53.texte_piece(conf, nom)
            except (ConfigurationRefusee, OSError) as e:
                manques.append(f"dependances.dep4 : {e}")
    fournisseurs = conf.get("fournisseurs") or {}
    if not fournisseurs:
        manques.append("fournisseurs : aucun relais déclaré (moteur réel)")
    for f, d in sorted(fournisseurs.items()):
        if not isinstance((d or {}).get("porte_plafond"), dict):
            manques.append(f"A15/DEP4 : fournisseurs.{f}.porte_plafond manquant : relais incapable de recevoir, au lancement de "
                           "chaque étape, le plafond dur calculé selon A1 (brouillon 10)")
    if plan == "pre_pilote":
        dec, pp = conf.get("decisions_a15"), conf.get("prepilote") or {}
        attendues = ("confidentialite", "d_f", "d_g", "d_h", "d_i", "d_j", "go_lancement")
        if not isinstance(dec, dict):
            manques.append("decisions_a15 manquant (A15 : confidentialité, D-f, D-g à D-j, GO de lancement)")
        else:
            for k in attendues:
                if not isinstance(dec.get(k), str) or not dec[k].strip() or MARQUEUR in dec[k]:
                    manques.append(f"decisions_a15.{k} : mot de Lazar absent (A15 : aucun lancement)")
            if isinstance(dec.get("d_g"), str) and MARQUEUR not in dec["d_g"] and _lettre(dec["d_g"], "ab") != pp.get("d_g"):
                manques.append(f"decisions_a15.d_g (« {dec['d_g']} ») ne désigne pas prepilote.d_g = {pp.get('d_g')!r} (CL19-12)")
            if isinstance(dec.get("d_i"), str) and MARQUEUR not in dec["d_i"] and _lettre(dec["d_i"], "123") != str(pp.get("d_i")):
                manques.append(f"decisions_a15.d_i (« {dec['d_i']} ») ne désigne pas prepilote.d_i = {pp.get('d_i')!r} (CL20-07)")
    return manques


__all__ = ("lire_configuration_v56", "verifier_specification_v56", "verifier_dependances_lancement_v56", "verifier_go_v56",
           "montant_requis", "lire_plafond", "ConfigurationRefusee", "GoRefuse", "MARQUEURS_SPECIFICATION")
