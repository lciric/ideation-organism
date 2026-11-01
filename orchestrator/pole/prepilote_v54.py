"""Pré-pilote d'étalonnage des instruments de la course 2 (brouillon 7, « Plan d'analyse ») — version 54 (CL18-04).

Plan (ordre par dépendance, jamais par résultat ; noms exigés dans `budget.etapes`, rôles imposés) :

| étape | contenu codé ici | rôle |
|---|---|---|
| `e1_redacteur` | plan des fonds (tâches `pp2-classes-axes`, `pp2-indices`, `pp2-fournisseurs`) ; rédacteur : squelette (12 à 16 ancres, couples de défaut) et déclaration par fond, contrôlés par programme ; autres produits du rédacteur (`prepilote.produits_redacteur` : difficiles, voisines, axe 7…) ; clé des classes au coffre | protégée |
| `e2_kimi_passe1` | passe 1 des proposeurs (Kimi) | protégée |
| `e3_rendus` | un rendu par fond chez son metteur en forme (consigne neutre, sans classe) ; S6 (ancres, couples) et A8 (longueur) par programme ; un seul nouvel essai ; A5 (fond exclu ; arrêt au-delà du maximum) | protégée |
| `e4_aiguillage` | aiguilleur sur rendus, passe 1, difficiles ; second lecteur sur la passe 1 | protégée |
| `e5_relecteur` | relecteur → ambigus, S6 (défaut vu), S20/A6 ; S18, S19 (A7) ; nœud avant les juges si A5, A6 ou A7 | protégée |
| `e6_juges` | trois juges sur les rendus non aiguillés, un appel par fiche, anonymes | protégée |
| `e7a_passe_tableau` | (si L1 = oui) tableau, passe « tableau », aiguilleur, second lecteur ; adjudicateur de M5 sur les désaccords des deux passes | sacrifiable |
| `e7b_etiquettes` | lectures d'étiquettes, S24, S28, paires, désaccord (comme la course) | protégée |
| `e7c_fusions` | fusions, aiguilleur, juges (même version de modèle qu'en É6 : A2) | sacrifiable |
| `e7d_axe7` | (si L2 = oui) table seule de l'axe 7 (Opus, éléments du rédacteur) | sacrifiable |
| `e8_paraphrases` | paraphrases des rendus (rédacteur, après É4) ; bardeaux (PB, NA, NB) | protégée |
| `e9_anteriorite` | vérificateur sur les fiches d'antériorité (pièce) ; réduite : tirage stratifié `pp2-reduction-e9` | réductible |
| `e9b_m6b` | (si D-g = b) vérificateur sur les fiches de M6b ; garde R5 ligne 31 (source hors de l'entrée) | protégée hors porte |

Fin de la phase de mesure **après É9 et É9b** (CL18, G5) ; ouverture des verdicts ; M1 calculée (S1 à S4 injectés) ; M4
« non étalonné (sans témoins concrets) » si aucun lot du bras d'attaque n'est servi.

**Ce qui n'est pas codé (squelettes qui refusent, motif exact)** : l'analyseur de l'étage 1 (DEP3 ; un objet injecté est
exigé, sinon `EtageUnAbsent` à É0) ; les lots du bras d'attaque (12 concrets ; `bras_attaque_v54`) ; la garde de forme de
M5 (ligne 9) ; le moissonneur (ligne 17) ; l'essai du relecteur (ligne 19) — ces trois lignes R5 ne se rejouent qu'à partir
d'un résultat externe scellé (`prepilote.gardes_externes`). É5bis (seconde version de témoins) : nœud « relancer avec
`temoins.version = 2` », jamais une troisième.

Lecture de code à confirmer par Lazar (déclarée) : É5 utilise la clé des classes **par programme** (ambigus, S19) avant la
fin d'É9 ; seule la décision (passe ou nœud) et des comptes sortent de la boîte, déposés au coffre ; aucun verdict d'É6/É7
n'est lu.
"""

import json
import os

from . import fiches_v54 as fv
from .configuration_v53 import ConfigurationRefusee
from .course2_v54 import ETAPES as ETAPES_COURSE  # noqa: F401
from .course2_v54 import GenerationV54, _fiches_ou_none, verifier_ordre_desaccord  # noqa: F401
from .mesures_v54 import aire_forme, etalonner_juges_v54, indices_forme, regle_s20
from .memoire_v53 import bardeaux, jaccard, texte_fiche
from .noyau_v54 import NoeudArret
from .outils import ecrire_json_scelle, empreinte_objet, extraire_bloc_json, normaliser_texte, verifier_scelle

VERSION = "pre-pilote-course-2-v54"
PLAN = ("e1_redacteur", "e2_kimi_passe1", "e3_rendus", "e4_aiguillage", "e5_relecteur", "e6_juges", "e7a_passe_tableau",
        "e7b_etiquettes", "e7c_fusions", "e7d_axe7", "e8_paraphrases", "e9_anteriorite", "e9b_m6b")
ROLES = {"e7a_passe_tableau": "sacrifiable", "e7c_fusions": "sacrifiable", "e7d_axe7": "sacrifiable",
         "e9_anteriorite": "reductible", "e9b_m6b": "protegee_hors_porte"}
CLASSES_N = ("N1", "N2", "N3", "N4")
ITEM_DE = {"P": "aucun", "C": "aucun", "N1": "K1", "N2": "K2", "N3": "K3", "N4": "K4", "G": "K5"}


class EtageUnAbsent(ConfigurationRefusee):
    """DEP3 : analyseur de l'étage 1 non fourni : le pré-pilote ne part pas (garde R5 ligne 6 non rejouable)."""


def plan_attendu(conf):
    pp = conf["prepilote"]
    sans = set()
    if pp["L1"] != "oui":
        sans.add("e7a_passe_tableau")
    if pp["L2"] != "oui":
        sans.add("e7d_axe7")
    if pp["d_g"] != "b":
        sans.add("e9b_m6b")
    return tuple(e for e in PLAN if e not in sans)


def verifier_configuration_pre_pilote(conf):
    manques = []
    pp = conf.get("prepilote")
    if not isinstance(pp, dict):
        raise ConfigurationRefusee("prepilote manquant")
    for k, permis in (("L1", ("oui", "retiree")), ("L2", ("oui", "reduite")), ("d_g", ("a", "b"))):
        if pp.get(k) not in permis:
            manques.append(f"prepilote.{k} ∈ {permis} exigé (décision de Lazar, aucun défaut)")
    for k in ("temoins", "redacteur", "squelette", "metteurs", "consigne_rendu", "a8", "s6", "a5_exclus_max", "second_lecteur",
              "relecteur", "s20", "controles_forme", "paraphrases", "anteriorite", "seuils_m1"):
        if k not in pp:
            manques.append(f"prepilote.{k} manquant (aucun défaut)")
    if manques:
        raise ConfigurationRefusee("configuration du pré-pilote refusée :\n- " + "\n- ".join(manques))
    noms = [e["nom"] for e in conf["budget"]["etapes"]]
    attendu = plan_attendu(conf)
    if tuple(noms) != attendu:
        manques.append(f"budget.etapes : plan exigé {attendu} (dans cet ordre), reçu {tuple(noms)}")
    for e in conf["budget"]["etapes"]:
        exige = ROLES.get(e["nom"], "protegee")
        if e.get("role") != exige:
            manques.append(f"budget.etapes : {e['nom']} doit être « {exige} » (brouillon 7, liste des protégées)")
    if pp["L1"] == "oui" and not pp.get("adjudicateur"):
        manques.append("prepilote.adjudicateur manquant (M5, L1 = oui)")
    if pp["L2"] == "oui" and not pp.get("axe7"):
        manques.append("prepilote.axe7 manquant (L2 = oui)")
    if pp["d_g"] == "b" and not pp.get("m6b"):
        manques.append("prepilote.m6b manquant (D-g = b)")
    ps = conf.get("plafonds_session") or {}
    for r in ("proposeur", "aiguilleur", "juge", "fusion", "lecteur", "redacteur", "metteur", "relecteur", "verificateur"):
        v = ps.get(r)
        if isinstance(v, bool) or not isinstance(v, (int, float)) or v <= 0:
            manques.append(f"plafonds_session.{r} : réel > 0 exigé (aucun défaut)")
    lect = conf.get("lecteurs_etiquettes") or []
    if len(lect) != 2 or len({l.get("etiquette") for l in lect}) != 2:
        manques.append("lecteurs_etiquettes : deux lecteurs isolés, étiquettes distinctes")
    if len(conf.get("cases") or []) != 1:
        manques.append("cases : une seule case au pré-pilote (texte I, bras de défense)")
    if pp.get("concrets") is not None:
        from .bras_attaque_v54 import refuser_lots
        manques.append(refuser_lots())
    if manques:
        raise ConfigurationRefusee("configuration du pré-pilote refusée :\n- " + "\n- ".join(manques))
    return True


# --- plan des fonds (tirages R9) -----------------------------------------------------------------------------------------------


def planifier_fonds(conf, graines, prefixe):
    """Classes et axes (`<p>-classes-axes`), indices de forme (`<p>-indices`), metteurs en forme (`<p>-fournisseurs`).
    Contraintes injectées : effectifs par classe, axes, fonds par axe [min, max], au plus k fonds d'une même classe par axe."""
    t = conf["prepilote"]["temoins"]
    classes = [c for c, n in sorted(t["classes"].items()) for _ in range(n)]
    axes = list(t["axes"])
    g = graines.generateur(f"{prefixe}-classes-axes")
    for _ in range(int(t["essais_max_tirage"])):
        perm = [classes[int(i)] for i in g.permutation(len(classes))]
        tailles = [t["par_axe_min"]] * len(axes)
        reste = len(perm) - sum(tailles)
        ordre = [int(i) for i in g.permutation(len(axes))]
        for i in ordre:
            if reste <= 0:
                break
            ajout = min(reste, t["par_axe_max"] - tailles[i])
            tailles[i] += ajout
            reste -= ajout
        if reste:
            raise ConfigurationRefusee("plan des fonds impossible : effectifs et fonds par axe incompatibles")
        affect, k = [], 0
        for a, n in zip(axes, tailles):
            affect += [(a, c) for c in perm[k:k + n]]
            k += n
        if all(sum(1 for a2, c2 in affect if a2 == a and c2 == c) <= t["meme_classe_par_axe_max"] for a, c in set(affect)):
            break
    else:
        raise ConfigurationRefusee("plan des fonds : contrainte « même classe par axe » non tenue après le nombre d'essais injecté")
    gi = graines.generateur(f"{prefixe}-indices")
    fonds = []
    for n, (a, c) in enumerate(affect):
        ident = "t" + graines.jeton_opaque(f"{prefixe}-ident-fond-{n}", 5)
        ind = {k: v[int(gi.integers(0, len(v)))] for k, v in sorted(t["indices"].items())}
        fonds.append({"ident": ident, "classe": c, "axe": a, "indices": ind})
    gf = graines.generateur(f"{prefixe}-fournisseurs")
    comptes = dict(t["fournisseurs"])
    if sum(comptes.values()) != len(fonds):
        raise ConfigurationRefusee(f"metteurs en forme : {sum(comptes.values())} places pour {len(fonds)} fonds")
    noms = sorted(comptes)
    tour = [noms[int(i)] for i in gf.permutation(len(noms))]  # ordre du tourniquet, tiré
    par_classe = sorted(range(len(fonds)), key=lambda i: (fonds[i]["classe"], float(gf.random())))
    k = 0
    for i in par_classe:  # tourniquet dans l'ordre des classes : équilibre des metteurs par classe
        while comptes[tour[k % len(tour)]] == 0:
            k += 1
        m = tour[k % len(tour)]
        fonds[i]["metteur"] = m
        comptes[m] -= 1
        k += 1
    return fonds


# --- contrôles par programme (S6, A8) --------------------------------------------------------------------------------------------


def _plat(t):
    return " ".join(str(t).split())


def controle_ancres(rendu, squelette):
    """S6 (programme) : part des ancres présentes littéralement (espaces normalisés) ; part des couples dont les deux chaînes
    sont présentes."""
    texte = _plat(fv.texte_plat(rendu))
    ancres = squelette["ancres"]
    part_a = sum(1 for a in ancres if _plat(a) in texte) / len(ancres) if ancres else 1.0
    couples = squelette["couples"]
    part_c = sum(1 for a, b in couples if _plat(a) in texte and _plat(b) in texte) / len(couples) if couples else 1.0
    return {"ancres": round(part_a, 6), "couples": round(part_c, 6)}


def controle_longueur(rendu, minimum, maximum):
    n = len(fv.texte_plat(rendu))
    return minimum <= n <= maximum, n


def garde_m6b(entree, source):
    """Garde R5 ligne 31 : ni le titre, ni un auteur, ni l'identifiant de la source dans l'entrée du vérificateur."""
    plat = normaliser_texte(entree)
    for k in ("titre", "identifiant"):
        if source.get(k) and normaliser_texte(source[k]) in plat:
            return False, f"{k} de la source dans l'entrée"
    for a in source.get("auteurs", []):
        if a and normaliser_texte(a) in plat:
            return False, "auteur de la source dans l'entrée"
    return True, None


def valider_squelette(bloc, fond, ancres_min, ancres_max):
    if not isinstance(bloc, dict):
        raise ValueError("réponse du rédacteur illisible")
    sq, dec = bloc.get("squelette"), bloc.get("declaration")
    if not isinstance(sq, dict) or not isinstance(dec, dict):
        raise ValueError("squelette et déclaration exigés")
    a, c = sq.get("ancres"), sq.get("couples")
    if not isinstance(a, list) or not all(isinstance(x, str) and x.strip() for x in a) or not ancres_min <= len(a) <= ancres_max:
        raise ValueError(f"ancres : {ancres_min} à {ancres_max} chaînes exigées")
    if not isinstance(c, list) or not all(isinstance(x, list) and len(x) == 2 and all(isinstance(y, str) and y for y in x) for x in c):
        raise ValueError("couples de défaut : paires de chaînes exigées")
    if fond["classe"] in CLASSES_N and not c:
        raise ValueError("classe N : au moins un couple de défaut exigé")
    if dec.get("item") != ITEM_DE[fond["classe"]]:
        raise ValueError(f"déclaration : item {dec.get('item')!r} ≠ item de la classe")
    if fond["classe"] in CLASSES_N and (not isinstance(dec.get("champs"), list) or len(dec["champs"]) != 2 or not dec.get("phrase")):
        raise ValueError("déclaration : deux champs et la phrase du texte I exigés")
    return {"ancres": a, "couples": c}, dec


class PrePiloteV54(GenerationV54):
    ETAPES = None

    @staticmethod
    def verifier_configuration(conf):
        return verifier_configuration_pre_pilote(conf)

    @staticmethod
    def fournisseurs_requis(conf):
        pp = conf["prepilote"]
        roles = [pp["redacteur"], pp["second_lecteur"], pp["relecteur"], pp["anteriorite"]["verificateur"]] + list(pp["metteurs"].values())
        roles += [pp["adjudicateur"]] if pp.get("adjudicateur") else []
        roles += [pp["axe7"]["lecteur"]] if pp.get("axe7") else []
        return GenerationV54.fournisseurs_requis(conf) | {r["fournisseur"] for r in roles}

    def __init__(self, conf, sortie, adaptateurs, *, go=None, horloge=None, etage1=None, gardes_e0=None):
        if etage1 is None or not callable(getattr(etage1, "signaler", None)):
            raise EtageUnAbsent("étage 1 : analyseur (DEP3) non fourni — le pré-pilote ne part pas (garde R5 ligne 6, classe G, "
                                "« passage » des fusions) ; aucun repli")
        super().__init__(conf, sortie, adaptateurs, numero=1, go=go, horloge=horloge)
        self.pp = conf["prepilote"]
        self.etage1 = etage1
        self.gardes_e0 = gardes_e0
        self.plan = plan_attendu(conf)
        self.fonds, self.squelettes, self.rendus, self.exclus = [], {}, {}, {}
        self.produits = {}
        self.relectures, self.m5 = {}, {"second_lecteur": {}, "adjudicateur": {}}
        self.decisions_e5 = None

    def _aiguiller(self, fiches, etat, lot):
        """Au pré-pilote, M5 est une mesure (union, intersection, adjudication) lue après É9, pas un arrêt en route : la garde de
        Kimi de la course n'est pas jouée ici (choix de code v54, déclaré)."""
        for f in fiches:
            self.aiguilleur.classer(f, etat, lot)

    # --- É1 ------------------------------------------------------------------------------------------------------------------

    def etape_e1_redacteur(self, etat):
        self.fonds = planifier_fonds(self.conf, self.graines, self.prefixe)
        r = self.pp["redacteur"]
        consigne = self.piece(r["consigne"])
        cle, declarations = {}, {}
        for f in self.fonds:
            spec = {"ident": f["ident"], "classe": f["classe"], "axe": f["axe"], "indices_cibles": f["indices"]}
            entree = consigne.rstrip() + "\n\n## Fond\n```json\n" + json.dumps(spec, ensure_ascii=False) + "\n```\n"
            a = self.appel(etat, role=r["etiquette"], role_kit="proposeur_ideation", fournisseur=r["fournisseur"], modele=r["modele"],
                           consigne=entree, plafond_role="redacteur", session=("e1", f["ident"]),
                           lire=lambda t: extraire_bloc_json(t, "squelette"))
            if a is None or a["lu"] is None:
                self.exclus[f["ident"]] = "squelette non écrit (rédacteur sans sortie)"
                continue
            try:
                sq, dec = valider_squelette(a["lu"], f, self.pp["squelette"]["ancres_min"], self.pp["squelette"]["ancres_max"])
            except ValueError as e:
                self.exclus[f["ident"]] = f"squelette refusé : {e}"
                self.ev("squelette-refuse", fond=f["ident"], motif=str(e)[:200])
                continue
            self.squelettes[f["ident"]] = sq
            declarations[f["ident"]] = dec
            cle[f["ident"]] = {"classe": f["classe"], "axe": f["axe"], "metteur": f["metteur"], "indices": f["indices"]}
        for prod in self.pp.get("produits_redacteur", []):
            entree = self.piece(prod["consigne"])
            a = self.appel(etat, role=r["etiquette"], role_kit="proposeur_ideation", fournisseur=r["fournisseur"], modele=r["modele"],
                           consigne=entree, plafond_role="redacteur", session=("e1", "produit", prod["nom"]),
                           lire=lambda t, c=prod["cle_json"]: extraire_bloc_json(t, c))
            liste = (a["lu"] or {}).get(prod["cle_json"]) if a else None
            if not isinstance(liste, list) or len(liste) != prod["nombre"]:
                self.ev("produit-redacteur-incomplet", produit=prod["nom"], attendu=prod["nombre"],
                        recu=len(liste) if isinstance(liste, list) else None)
                liste = liste if isinstance(liste, list) else []
            self.produits[prod["nom"]] = liste
        ecrire_json_scelle(os.path.join(self.sortie, "temoins", "squelettes.json"), self.squelettes)
        self.coffre.deposer(self.tache("cle-classes"), cle)
        self.coffre.deposer(self.tache("declarations"), declarations)
        self._cle_classes = cle  # tenue par le programme ; jamais lue avant la fin d'É9 sauf la boîte d'É5 (déclaré)

    # --- É2 ------------------------------------------------------------------------------------------------------------------

    def etape_e2_kimi_passe1(self, etat):
        self.passe1 = self._proposer(etat, 1)

    # --- É3 ------------------------------------------------------------------------------------------------------------------

    def _rendre(self, etat, f, essai):
        m = self.pp["metteurs"][f["metteur"]]
        sq = self.squelettes[f["ident"]]
        corps = json.dumps({"ancres": sq["ancres"], "couples": sq["couples"]}, ensure_ascii=False, indent=1)
        fv.garde(corps, self.interdites, self.a4_mode, "l'entrée d'un rendu")
        entree = self.piece(self.pp["consigne_rendu"]).rstrip() + "\n\n## Éléments à mettre en forme\n```json\n" + corps + "\n```\n"
        a = self.appel(etat, role=m["etiquette"], role_kit="proposeur_ideation", fournisseur=m["fournisseur"], modele=m["modele"],
                       consigne=entree, plafond_role="metteur", session=("e3", f["ident"], essai), lire=_fiches_ou_none)
        if a is None or not a["lu"] or len(a["lu"]) != 1:
            return None, "rendu sans sortie exploitable"
        try:
            fiche = fv.preparer(a["lu"][0], self.conf["champs_fiche"], ident=f["ident"], case=self.conf["cases"][0],
                                fournisseur=f["metteur"], passe="rendu", origine="rendu")
        except fv.FicheRefusee as e:
            return None, f"rendu refusé : {e}"
        s6 = controle_ancres(fiche, sq)
        if f["classe"] != "G":
            ok_l, n = controle_longueur(fiche, self.pp["a8"]["min"], self.pp["a8"]["max"])
            if not ok_l:
                return None, f"A8 : longueur {n} hors de [{self.pp['a8']['min']} ; {self.pp['a8']['max']}]"
        if s6["ancres"] + 1e-12 < self.pp["s6"]["ancres_min"] or s6["couples"] + 1e-12 < self.pp["s6"]["couples_min"]:
            return None, f"A5 : fidélité sous S6 (ancres {s6['ancres']}, couples {s6['couples']})"
        fiche["meta"]["s6"] = s6
        return fiche, None

    def etape_e3_rendus(self, etat):
        if not verifier_scelle(os.path.join(self.sortie, "temoins", "squelettes.json")):
            raise NoeudArret("A13 : squelettes scellés modifiés avant les rendus : arrêt")
        for f in self.fonds:
            if f["ident"] not in self.squelettes:
                continue
            fiche, motif = self._rendre(etat, f, 1)
            if fiche is None and motif and not motif.startswith("rendu sans"):
                self.ev("rendu-refait", fond=f["ident"], motif=motif)
                fiche, motif = self._rendre(etat, f, 2)  # une seule reprise (A5, A8)
            if fiche is None:
                if etat["coupee"]:
                    return
                self.exclus[f["ident"]] = motif
                continue
            self.rendus[f["ident"]] = fiche
            self.fiches[f["ident"]] = fiche
            self.ordre.append(f["ident"])
        self._verifier_a5()

    def _verifier_a5(self):
        n = len(self.exclus)
        if n > self.pp["a5_exclus_max"]:
            raise NoeudArret(f"A5 : {n} fonds exclus > {self.pp['a5_exclus_max']} : arrêt")

    # --- É4 ------------------------------------------------------------------------------------------------------------------

    def _lecteur_m5(self, etat, f, quoi, lot):
        r = self.pp[quoi]
        entree = self.servir(self.piece(r["consigne"]), f, f"le {quoi}")
        if entree is None:
            return None
        from .aiguilleur_v53 import lire_classe
        a = self.appel(etat, role=r["etiquette"], role_kit="juge_ideation", fournisseur=r["fournisseur"], modele=r["modele"],
                       consigne=entree, plafond_role="aiguilleur", session=(quoi, lot, f["ident"]), lire=lambda t: lire_classe(t)[0])
        classe = a["lu"] if a else None
        self.m5[quoi][f["ident"]] = classe if classe else ("refus" if a else "non lu")
        return classe

    def etape_e4_aiguillage(self, etat):
        for f in list(self.rendus.values()):
            self.aiguilleur.classer(f, etat, "rendus")
        for i, d in enumerate(self.produits.get("difficiles", [])):
            try:
                fd = fv.preparer(d, self.conf["champs_fiche"], ident=f"d{i}", case=self.conf["cases"][0], fournisseur="redacteur",
                                 passe="difficile", origine="difficile")
            except fv.FicheRefusee as e:
                self.ev("difficile-refusee", rang=i, motif=str(e)[:200])
                continue
            self.fiches[fd["ident"]] = fd
            self.aiguilleur.classer(fd, etat, "difficiles")
        for f in self.passe1:
            self.aiguilleur.classer(f, etat, "passe1")
            self._lecteur_m5(etat, f, "second_lecteur", "passe1")

    # --- É5 ------------------------------------------------------------------------------------------------------------------

    def etape_e5_relecteur(self, etat):
        r = self.pp["relecteur"]
        consigne = self.piece(r["consigne"])
        for i, f in self.rendus.items():
            if not self.aiguilleur.a_passeport(f):
                continue
            entree = self.servir(consigne, f, "le relecteur")
            if entree is None:
                continue
            a = self.appel(etat, role=r["etiquette"], role_kit="juge_ideation", fournisseur=r["fournisseur"], modele=r["modele"],
                           consigne=entree, plafond_role="relecteur", session=("e5", i),
                           lire=lambda t: extraire_bloc_json(t, "notable"))
            self.relectures[i] = a["lu"] if a else None
        self.decisions_e5 = self._boite_e5()
        self.coffre.deposer(self.tache("e5-boite"), self.decisions_e5)
        if not self.decisions_e5["passe"]:
            raise NoeudArret("É5 : " + self.decisions_e5["motif"] + " — arrêt avant les juges")

    def _boite_e5(self):
        """Programme : clé des classes lue ici seulement (déclaré) ; ne sortent que la décision et des comptes."""
        cle, s6 = self._cle_classes, self.pp["s6"]
        ambigus, primaires, defaut_non_vu = set(), {}, []
        for i, f in self.rendus.items():
            if not self.aiguilleur.a_passeport(f):
                continue
            c = cle[i]["classe"]
            lu = self.relectures.get(i)
            if c in CLASSES_N and not (isinstance(lu, dict) and lu.get("defaut_present") is True):
                defaut_non_vu.append(i)
            if c == "P" or c in CLASSES_N:
                primaires[i] = c
                attendu_notable = c == "P"
                if not isinstance(lu, dict) or lu.get("notable") is not attendu_notable or (c in CLASSES_N and lu.get("item") not in (None, ITEM_DE[c])):
                    ambigus.add(i)
        n_N = sum(1 for c in primaires.values() if c in CLASSES_N)
        part_vu = 1 - len(defaut_non_vu) / n_N if n_N else 1.0
        for i in defaut_non_vu:
            self.exclus.setdefault(i, "A5 : défaut non vu par le relecteur (S6)")
            primaires.pop(i, None)
        s20 = regle_s20(primaires, ambigus, **self.pp["s20"])
        cf = self.pp["controles_forme"]
        elems19 = [{"groupe": i, "classe": 1 if primaires[i] == "P" else 0,
                    "indices": indices_forme(fv.texte_plat(self.rendus[i]), len(self.rendus[i]["contenu"]))}
                   for i in primaires if i not in ambigus]
        s19 = aire_forme(elems19, ridge=cf["ridge"])
        kimi = [f for f in self.passe1 if self.aiguilleur.a_passeport(f)]
        if len(kimi) < cf["s18_effectif_min"]:
            s18 = {"aire": None, "motif": f"non évaluée : {len(kimi)} fiches de Kimi < {cf['s18_effectif_min']} (réserve)"}
        else:
            elems18 = [{"groupe": i, "classe": 1, "indices": indices_forme(fv.texte_plat(f), len(f["contenu"]))}
                       for i, f in self.rendus.items() if self.aiguilleur.a_passeport(f)]
            elems18 += [{"groupe": f["ident"], "classe": 0, "indices": indices_forme(fv.texte_plat(f), len(f["contenu"]))} for f in kimi]
            s18 = aire_forme(elems18, ridge=cf["ridge"])
        motifs = []
        if len(self.exclus) > self.pp["a5_exclus_max"]:
            motifs.append(f"A5 : {len(self.exclus)} fonds exclus > {self.pp['a5_exclus_max']}")
        if part_vu + 1e-12 < s6["defaut_vu_min"]:
            motifs.append(f"S6 : défaut vu sur {part_vu:.2f} des N < {s6['defaut_vu_min']}")
        if not s20["passe"]:
            motifs.append("A6 : " + s20["motif"])
        if s18.get("aire") is not None and s18["aire"] > cf["s18_aire_max"] + 1e-12:
            motifs.append(f"A7 : S18 aire {s18['aire']} > {cf['s18_aire_max']}")
        if s19.get("aire") is not None and s19["aire"] > cf["s19_aire_max"] + 1e-12:
            motifs.append(f"A7 : S19 aire {s19['aire']} > {cf['s19_aire_max']}")
        version = self.pp["temoins"]["version"]
        if motifs:
            suite = ("É5bis : témoins à replanter — relancer le pré-pilote avec temoins.version = 2 (compte commun A6/A7)"
                     if version < 2 else "deux versions de témoins épuisées : C5 non satisfaite")
            motifs.append(suite)
        return {"passe": not motifs, "motif": " ; ".join(motifs) or None, "ambigus": len(ambigus), "s20": s20,
                "s18": s18, "s19": s19, "defaut_vu": round(part_vu, 6), "exclus": len(self.exclus), "version_temoins": version,
                "primaires_non_ambigus": sorted(i for i in primaires if i not in ambigus)}

    # --- É6, É7 --------------------------------------------------------------------------------------------------------------

    def etape_e6_juges(self, etat):
        for i in self.decisions_e5["primaires_non_ambigus"] + sorted(set(self.rendus) - set(self.decisions_e5["primaires_non_ambigus"])):
            f = self.rendus[i]
            if self.aiguilleur.a_passeport(f) and i not in self.exclus:
                if f["empreinte"] != empreinte_objet(f["contenu"]):
                    raise NoeudArret(f"A13 : empreinte du témoin {i} différente de celle scellée")
                self.juger(f, "e6", etat)

    def etape_e7a_passe_tableau(self, etat):
        self.etape_passe_tableau(etat)
        for f in self.passe2:
            self._lecteur_m5(etat, f, "second_lecteur", "passe2")
        for f in self.passe1 + self.passe2:
            d = self.aiguilleur.decisions.get(f["ident"], {})
            s = self.m5["second_lecteur"].get(f["ident"])
            if d.get("classe") is None or s in (None, "non lu"):
                continue
            if (d["classe"] != "niveau_methode") != (s != "niveau_methode"):
                self._lecteur_m5(etat, f, "adjudicateur", "adjudication")

    def etape_e7b_etiquettes(self, etat):
        self.etape_etiquettes(etat)

    def etape_e7c_fusions(self, etat):
        self.etape_fusions(etat)
        for f in self.fusions:
            self.etage1_resultats[f["ident"]] = bool(self.etage1.signaler(f))

    def etape_e7d_axe7(self, etat):
        ax = self.pp["axe7"]
        consigne = self.piece(ax["consigne"])
        verdicts = {}
        for k, el in enumerate(self.produits.get("axe7", [])):
            corps = json.dumps(el, ensure_ascii=False, indent=1)
            fv.garde(corps, self.interdites, self.a4_mode, "un élément de l'axe 7")
            a = self.appel(etat, role=ax["lecteur"]["etiquette"], role_kit="juge_ideation", fournisseur=ax["lecteur"]["fournisseur"],
                           modele=ax["lecteur"]["modele"], consigne=consigne.rstrip() + "\n\n## La fiche\n```json\n" + corps + "\n```\n",
                           plafond_role="juge", session=("e7d", k), lire=lambda t: extraire_bloc_json(t, "items"))
            verdicts[str(k)] = a["lu"] if a else None
        self.coffre.deposer(self.tache("verdicts-e7d"), verdicts)

    # --- É8 ------------------------------------------------------------------------------------------------------------------

    def etape_e8_paraphrases(self, etat):
        p = self.pp["paraphrases"]
        r = self.pp["redacteur"]
        sources = sorted(i for i, f in self.rendus.items() if self.aiguilleur.a_passeport(f) and i not in self.exclus)
        g = self.graines.generateur(self.tache("paraphrases"))  # tâche déclarée (absente de la liste du brouillon 7)
        choisies = [sources[int(i)] for i in g.permutation(len(sources))][:p["nombre_par_niveau"] * len(p["niveaux"])]
        consigne = self.piece(p["consigne"])
        paraphrases = []
        for k, i in enumerate(choisies):
            niveau = p["niveaux"][k % len(p["niveaux"])]
            entree = self.servir(consigne.rstrip() + f"\n\n## Paraphrase\nNiveau : {niveau}\n", self.rendus[i], "le rédacteur (paraphrase)")
            if entree is None:
                continue
            a = self.appel(etat, role=r["etiquette"], role_kit="proposeur_ideation", fournisseur=r["fournisseur"], modele=r["modele"],
                           consigne=entree, plafond_role="redacteur", session=("e8", i), lire=_fiches_ou_none)
            if a and a["lu"] and len(a["lu"]) == 1:
                paraphrases.append({"source": i, "niveau": niveau, "fiche": {"contenu": a["lu"][0]}})
        gp = self.graines.generateur(self.tache("partition"))
        fonds = sorted(self.rendus)
        moitie = {f: int(gp.integers(0, 2)) for f in fonds}
        n = self.conf["memoire"]["taille_bardeau"]
        sim = lambda x, y: jaccard(bardeaux(texte_fiche(x), n), bardeaux(texte_fiche(y), n))  # noqa: E731
        pb = [{"source": q["source"], "niveau": q["niveau"], "similarite": round(sim(q["fiche"], self.rendus[q["source"]]), 6)} for q in paraphrases]
        na = [{"a": a, "b": b, "similarite": round(sim(self.rendus[a], self.rendus[b]), 6), "moitie": moitie[a]}
              for x, a in enumerate(fonds) for b in fonds[x + 1:] if moitie[a] == moitie[b]]
        nb = [{"voisine": k, "similarite_max": round(max((sim({"contenu": v}, self.rendus[i]) for i in fonds), default=0.0), 6)}
              for k, v in enumerate(self.produits.get("voisines", []))]
        ecrire_json_scelle(os.path.join(self.sortie, "memoire-e8.json"), {"methode": "bardeaux", "taille": n, "PB": pb, "NA": na,
                                                                           "NB": nb, "partition": moitie,
                                                                           "t_etoile": "calibré par l'analyse (S7), jamais ici"})

    # --- É9, É9b -------------------------------------------------------------------------------------------------------------

    def _verifier_fiches(self, etat, fiches, lot, sources=None):
        v = self.pp["anteriorite"]["verificateur"]
        consigne = self.piece(self.pp["anteriorite"]["consigne"] if lot == "e9" else self.pp["m6b"]["consigne"])
        for fiche in fiches:
            corps = json.dumps(fiche, ensure_ascii=False, indent=1)
            entree = consigne.rstrip() + "\n\n## La fiche\n```json\n" + corps + "\n```\n"
            if sources is not None:
                ok, motif = garde_m6b(entree, sources.get(fiche["ident"], {}))
                if not ok:
                    self.ev("m6b-fiche-arretee", ident=fiche["ident"], motif=motif)
                    continue
            a = self.appel(etat, role=v["etiquette"], role_kit=v["role_kit"], fournisseur=v["fournisseur"], modele=v["modele"],
                           consigne=entree, plafond_role="verificateur", session=(lot, fiche["ident"]),
                           lire=lambda t: extraire_bloc_json(t, "references"))
            self.coffre.deposer(f"verdicts-{lot}-{fiche['ident']}", {"ident": fiche["ident"], "verdict": a["lu"] if a else None})

    def etape_e9_anteriorite(self, etat):
        an = self.pp["anteriorite"]
        fiches = json.loads(self.piece(an["fiches"]))["fiches"]
        if self.budget.etapes["e9_anteriorite"]["reduite_appliquee"]:
            strates = json.loads(self.piece(an["cle"]))  # programme : strates lues pour le tirage stratifié (déclaré)
            g = self.graines.generateur(self.tache("reduction-e9"))
            garde = []
            for strate, k in sorted(an["reduite"].items()):
                ids = sorted(f["ident"] for f in fiches if strates.get(f["ident"]) == strate)
                garde += [ids[int(i)] for i in g.permutation(len(ids))][:k]
            fiches = [f for f in fiches if f["ident"] in set(garde)]
            self.ev("e9-reduite", fiches=len(fiches))
        self._verifier_fiches(etat, fiches, "e9")

    def etape_e9b_m6b(self, etat):
        m = self.pp["m6b"]
        self._verifier_fiches(etat, json.loads(self.piece(m["fiches"]))["fiches"], "e9b", sources=json.loads(self.piece(m["sources"])))

    # --- le pré-pilote ---------------------------------------------------------------------------------------------------------

    def executer(self):
        self.etage1_resultats = {}
        ecrire_json_scelle(os.path.join(self.sortie, "manifeste-depart.json"), {
            "version": VERSION, "specification": "brouillon 7 (799b9ca9…)", "configuration_sha256": self.conf["empreinte_configuration"],
            "go": self.go, "plan": list(self.plan), "bras": self.bras_decl, "prefixe_taches": self.prefixe,
            "gardes_e0": self.gardes_e0, "lectures": {k: self.pp[k] for k in ("L1", "L2", "d_g")},
            "m4": "non étalonné (M4 sans témoins concrets : aucun lot du bras d'attaque servi)",
            "regle_de_lecture": "aucun verdict d'É6/É7 ni clé ouvert avant la fin d'É9 ; É5 : clé des classes lue par programme (déclaré)"})
        resultat = None
        try:
            for nom in self.plan:
                self.jouer_etape(nom, getattr(self, "etape_" + nom))
                if not self.c13_ou_noeud(nom):
                    break
            for i, f in self.rendus.items():
                self.etage1_resultats[i] = bool(self.etage1.signaler(f))
            self.deposer_cles()
            self.coffre.deposer(self.tache("etage1"), self.etage1_resultats)
            self.coffre.declarer_fin_e9()  # après É9 et É9b (CL18, G5)
            verdicts = self.ouvrir_verdicts(sorted(set(self.rendus) | {f["ident"] for f in self.fusions}))
            resultat = self._analyse_m1(verdicts)
            ecrire_json_scelle(os.path.join(self.sortie, "analyse-m1.json"), resultat)
        except NoeudArret as e:
            self.noeud = str(e)
            raise
        except Exception as e:
            self.arret = f"{type(e).__name__} : {str(e)[:500]}"
            raise
        finally:
            self.aiguilleur.sceller()
            ecrire_json_scelle(os.path.join(self.sortie, "manifeste-fin.json"), {
                "version": VERSION, "arret": self.arret, "noeud": self.noeud, "evenements": self.evenements,
                "etapes": self.etapes_etat, "budget": self.budget.etat(), "graines": self.graines.manifeste(),
                "coffre": self.coffre.journal(), "suivi_roles": self.suivi.etat(), "bras": self.bras_decl,
                "non_produits": self.non_produits, "exclus": self.exclus, "exclues_a4": self.exclues_a4,
                "rendus": len(self.rendus), "fonds": len(self.fonds), "m5": {k: len(v) for k, v in self.m5.items()},
                "e5": None if self.decisions_e5 is None else {k: v for k, v in self.decisions_e5.items() if k != "primaires_non_ambigus"},
                "juges_absents": self.absents_juges, "modele_servi_juges": self.modele_servi_juges})
        return resultat

    def _analyse_m1(self, verdicts):
        prim = set(self.decisions_e5["primaires_non_ambigus"]) if self.decisions_e5 else set()
        cle = self.coffre.ouvrir(self.tache("cle-classes"))
        attendus = {i: ("P" if cle[i]["classe"] == "P" else "N") for i in prim if i in verdicts}
        notables = {j["etiquette"]: {i: (verdicts[i].get(j["etiquette"]) or {}).get("notable") if verdicts[i].get(j["etiquette"]) else None
                                     for i in attendus} for j in self.conf["juges"]}
        s = self.pp["seuils_m1"]
        return {"m1": etalonner_juges_v54(notables, attendus, **s) if attendus else "aucun témoin primaire jugé",
                "temoins_primaires_juges": len(attendus), "lecture": "verdict de porte prononcé par un sous-agent neuf (R13)"}
