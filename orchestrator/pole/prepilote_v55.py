"""Pré-pilote de la course 2, version 55 — au-dessus de `prepilote_v54` (inchangé, R12) et de la génération v55.

| constat | correction |
|---|---|
| CL19-02 | au **nœud** (étape protégée non mesurée, A5, A6, A7, É5bis…), aucune fin d'É9 déclarée, aucune clé ouverte, aucun verdict lu, aucun fichier d'analyse écrit ; les clés de sessions et d'anonymisation sont déposées (non ouvertes), le manifeste de fin est écrit, `NoeudArret` rend la main à Lazar (O12 : « rien n'en a été lu ») |
| CL19-03 (code) | plus aucune copie de la clé des classes en mémoire après É1 (ni `_cle_classes`, ni classe dans le plan des fonds) ; les deux lectures par programme avant la fin d'É9 (É3 : exemption A8 de la classe G ; É5 : S6, S20/A6, S18/S19/A7) passent par `CoffreV55.lire_pour_garde`, **journalisées** (horodatage, rôle, raison) avec leur sortie (comptes seulement) ; la boîte d'É5 ne sort que la décision et des comptes, le détail par témoin est **déposé scellé** au coffre et ouvert après la fin d'É9 seulement ; É6 appelle les juges dans l'ordre des **identifiants opaques** (jamais par classe) ; É9 réduite lit une **liste de réduction scellée** (`prepilote.anteriorite.liste_reduite`, pièce empreintée et scellée, tirée par session-depot avec `pp2-reduction-e9`) et jamais la clé d'antériorité |
| CL19-06 | `temoins.version = 2` n'est accepté qu'avec la pièce `prepilote.temoins.sortie_v1` : l'attestation scellée que la version 1 a fini en nœud É5bis (écrite par ce code, `temoins-v1-e5bis.json`) |
| CL19-07 | S6 : ancres comparées avec bornes de nombre et de mot (« valeur 12 » n'est pas trouvée dans « valeur 123 », « seuil 0,3 » pas dans « seuil 0,35 ») ; nombres du rendu absents du squelette comptés (`nombres_ajoutes`), plafond `prepilote.s6.nombres_ajoutes_max` (configuration, aucun défaut) |
| CL19-12 | entrée d'un rendu gardée (A4) **entière**, consigne comprise ; un relecteur sans sortie (défaut technique) ne fait plus un « ambigu » : témoin « non relu (technique) », hors S20, hors A5, non jugé, compté |
"""

import json
import os

from . import fiches_v54 as fv
from . import prepilote_v54 as p54
from .configuration_v53 import ConfigurationRefusee, chemin_piece, entier, texte_piece
from .course2_v55 import GenerationV55
from .mesures_v54 import aire_forme, indices_forme, regle_s20
from .noyau_v54 import NoeudArret
from .outils import ecrire_json_scelle, empreinte_objet, extraire_bloc_json, verifier_scelle

VERSION = "pre-pilote-course-2-v55"
PLAN, ROLES, CLASSES_N, ITEM_DE = p54.PLAN, p54.ROLES, p54.CLASSES_N, p54.ITEM_DE
EtageUnAbsent = p54.EtageUnAbsent
plan_attendu = p54.plan_attendu
garde_m6b, controle_longueur, valider_squelette = p54.garde_m6b, p54.controle_longueur, p54.valider_squelette
ATTESTATION_V1 = "temoins-v1-e5bis.json"
ROLE_E3, ROLE_E5 = "e3-exemption-a8", "boite-e5"


# --- S6 (CL19-07) ------------------------------------------------------------------------------------------------------------

import re  # noqa: E402

NOMBRE = re.compile(r"(?<!\w)\d+(?:[.,]\d+)*(?!\w)")


def _plat(t):
    return " ".join(str(t).split())


def motif_ancre(ancre):
    """Ancre cherchée littéralement (espaces normalisées, casse et ponctuation gardées, comme la v54), avec bornes : aucun
    caractère de mot collé avant ou après ; une ancre qui finit par un chiffre ne peut pas être suivie de « ,d » ni « .d »
    (extension décimale), une ancre qui commence par un chiffre ne peut pas être précédée de « d, » ni « d. »."""
    a = _plat(ancre)
    avant = (r"(?<!\w)" if a[:1].isalnum() else "") + (r"(?<!\d[.,])" if a[:1].isdigit() else "")
    apres = (r"(?!\w)" if a[-1:].isalnum() else "") + (r"(?![.,]\d)" if a[-1:].isdigit() else "")
    return re.compile(avant + re.escape(a) + apres)


def nombres(texte):
    return {x.replace(",", ".") for x in NOMBRE.findall(_plat(texte))}


def controle_ancres_v55(rendu, squelette):
    texte = _plat(fv.texte_plat(rendu))
    ancres, couples = squelette["ancres"], squelette["couples"]
    present = lambda a: motif_ancre(a).search(texte) is not None  # noqa: E731
    part_a = sum(1 for a in ancres if present(a)) / len(ancres) if ancres else 1.0
    part_c = sum(1 for a, b in couples if present(a) and present(b)) / len(couples) if couples else 1.0
    permis = set().union(*(nombres(x) for x in list(ancres) + [y for c in couples for y in c])) if (ancres or couples) else set()
    ajoutes = sorted(nombres(texte) - permis)
    return {"ancres": round(part_a, 6), "couples": round(part_c, 6), "nombres_ajoutes": len(ajoutes)}


# --- configuration -----------------------------------------------------------------------------------------------------------


def lire_liste_reduite(conf):
    an = conf["prepilote"]["anteriorite"]
    nom = an.get("liste_reduite")
    if not isinstance(nom, str) or nom not in (conf.get("pieces") or {}):
        raise ConfigurationRefusee("prepilote.anteriorite.liste_reduite : pièce scellée exigée (liste de réduction d'É9 tirée par "
                                   "session-depot ; la clé d'antériorité n'est jamais lue avant la fin d'É9)")
    if not verifier_scelle(chemin_piece(conf, conf["pieces"][nom]["chemin"])):
        raise ConfigurationRefusee("prepilote.anteriorite.liste_reduite : compagnon .sha256 absent ou faux (pièce non scellée)")
    liste = json.loads(texte_piece(conf, nom)).get("idents")
    fiches = {f["ident"] for f in json.loads(texte_piece(conf, an["fiches"]))["fiches"]}
    attendu = sum(int(v) for v in an["reduite"].values())
    if not isinstance(liste, list) or len(set(liste)) != len(liste) or not set(liste) <= fiches or len(liste) != attendu:
        raise ConfigurationRefusee(f"liste de réduction d'É9 : {attendu} identifiants distincts des fiches d'antériorité exigés")
    return liste


def lire_attestation_v1(conf):
    t = conf["prepilote"]["temoins"]
    nom = t.get("sortie_v1")
    if not isinstance(nom, str) or nom not in (conf.get("pieces") or {}):
        raise ConfigurationRefusee("temoins.version = 2 : pièce prepilote.temoins.sortie_v1 exigée (attestation scellée du nœud "
                                   "É5bis de la version 1, écrite par le pré-pilote ; jamais une valeur de configuration seule)")
    if not verifier_scelle(chemin_piece(conf, conf["pieces"][nom]["chemin"])):
        raise ConfigurationRefusee("temoins.sortie_v1 : attestation non scellée")
    att = json.loads(texte_piece(conf, nom))
    if att.get("version_temoins_epuisee") != 1 or att.get("noeud") != "É5bis" or att.get("version") != VERSION:
        raise ConfigurationRefusee("temoins.sortie_v1 : attestation d'un nœud É5bis de la version 1 (pré-pilote v55) exigée")
    return att


def verifier_configuration_pre_pilote_v55(conf):
    p54.verifier_configuration_pre_pilote(conf)
    pp = conf["prepilote"]
    manques = []
    if not entier(pp["s6"].get("nombres_ajoutes_max"), 0):
        manques.append("prepilote.s6.nombres_ajoutes_max : entier ≥ 0 exigé (CL19-07, aucun défaut)")
    if pp["temoins"].get("version") not in (1, 2):
        manques.append("prepilote.temoins.version ∈ {1, 2} exigé (jamais une troisième)")
    if manques:
        raise ConfigurationRefusee("configuration du pré-pilote v55 refusée :\n- " + "\n- ".join(manques))
    lire_liste_reduite(conf)
    if pp["temoins"]["version"] == 2:
        lire_attestation_v1(conf)
    return True


# --- le pré-pilote -----------------------------------------------------------------------------------------------------------


class PrePiloteV55(p54.PrePiloteV54, GenerationV55):
    @staticmethod
    def verifier_configuration(conf):
        return verifier_configuration_pre_pilote_v55(conf)

    def __init__(self, conf, sortie, adaptateurs, *, go=None, horloge=None, etage1=None, gardes_e0=None, racine_sessions=None):
        self._racine_sessions_demandee = racine_sessions
        super().__init__(conf, sortie, adaptateurs, go=go, horloge=horloge, etage1=etage1, gardes_e0=gardes_e0)
        self.exclus_techniques = {}
        self._cles_deposees = False
        for role in (ROLE_E3, ROLE_E5):
            self.coffre.permettre(self.tache("cle-classes"), role)

    # --- clé des classes : jamais gardée ---------------------------------------------------------------------------------------

    def etape_e1_redacteur(self, etat):
        super().etape_e1_redacteur(etat)
        self.__dict__.pop("_cle_classes", None)  # CL19-03 : aucune copie en mémoire
        self.fonds = [{k: v for k, v in f.items() if k != "classe"} for f in self.fonds]

    def _lire_cle(self, role, raison):
        return self.coffre.lire_pour_garde(self.tache("cle-classes"), role, raison)

    # --- É3 ------------------------------------------------------------------------------------------------------------------

    def etape_e3_rendus(self, etat):
        jeton, cle = self._lire_cle(ROLE_E3, "A8 : la classe G est exemptée du contrôle de longueur (Plan, É3)")
        self._exempts_a8 = {i for i, v in cle.items() if v["classe"] == "G"}
        self.coffre.noter_sortie_garde(jeton, {"fonds": len(cle), "exemptes_a8": len(self._exempts_a8)})
        del cle
        super().etape_e3_rendus(etat)

    def _rendre(self, etat, f, essai):
        m = self.pp["metteurs"][f["metteur"]]
        sq = self.squelettes[f["ident"]]
        corps = json.dumps({"ancres": sq["ancres"], "couples": sq["couples"]}, ensure_ascii=False, indent=1)
        entree = self.piece(self.pp["consigne_rendu"]).rstrip() + "\n\n## Éléments à mettre en forme\n```json\n" + corps + "\n```\n"
        fv.garde(entree, self.interdites, self.a4_mode, "l'entrée complète d'un rendu (consigne comprise)")
        a = self.appel(etat, role=m["etiquette"], role_kit="proposeur_ideation", fournisseur=m["fournisseur"], modele=m["modele"],
                       consigne=entree, plafond_role="metteur", session=("e3", f["ident"], essai), lire=p54._fiches_ou_none)
        if a is None or not a["lu"] or len(a["lu"]) != 1:
            return None, "rendu sans sortie exploitable"
        try:
            fiche = fv.preparer(a["lu"][0], self.conf["champs_fiche"], ident=f["ident"], case=self.conf["cases"][0],
                                fournisseur=f["metteur"], passe="rendu", origine="rendu")
        except fv.FicheRefusee as e:
            return None, f"rendu refusé : {e}"
        s6 = controle_ancres_v55(fiche, sq)
        if f["ident"] not in self._exempts_a8:
            ok_l, n = controle_longueur(fiche, self.pp["a8"]["min"], self.pp["a8"]["max"])
            if not ok_l:
                return None, f"A8 : longueur {n} hors de [{self.pp['a8']['min']} ; {self.pp['a8']['max']}]"
        if s6["ancres"] + 1e-12 < self.pp["s6"]["ancres_min"] or s6["couples"] + 1e-12 < self.pp["s6"]["couples_min"]:
            return None, f"A5 : fidélité sous S6 (ancres {s6['ancres']}, couples {s6['couples']})"
        if s6["nombres_ajoutes"] > self.pp["s6"]["nombres_ajoutes_max"]:
            return None, f"A5 : {s6['nombres_ajoutes']} nombre(s) ajouté(s) au rendu > {self.pp['s6']['nombres_ajoutes_max']} (S6)"
        fiche["meta"]["s6"] = s6
        return fiche, None

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
        """Lecture journalisée de la clé ; sortie : décision et comptes ; détail par témoin déposé scellé (ouvert après É9)."""
        jeton, cle = self._lire_cle(ROLE_E5, "S6 (défaut vu), S20/A6, S18/S19/A7 avant tout juge (Plan, É5)")
        s6 = self.pp["s6"]
        ambigus, primaires, defaut_non_vu, non_relus = set(), {}, [], []
        for i, f in self.rendus.items():
            if not self.aiguilleur.a_passeport(f):
                continue
            c = cle[i]["classe"]
            lu = self.relectures.get(i)
            if not isinstance(lu, dict):  # CL19-12 : relecteur sans sortie = défaut technique, pas un ambigu
                non_relus.append(i)
                continue
            if c in CLASSES_N and lu.get("defaut_present") is not True:
                defaut_non_vu.append(i)
            if c == "P" or c in CLASSES_N:
                primaires[i] = c
                attendu_notable = c == "P"
                if lu.get("notable") is not attendu_notable or (c in CLASSES_N and lu.get("item") not in (None, ITEM_DE[c])):
                    ambigus.add(i)
        n_N = sum(1 for c in primaires.values() if c in CLASSES_N)
        part_vu = 1 - len(defaut_non_vu) / n_N if n_N else 1.0
        for i in defaut_non_vu:
            self.exclus.setdefault(i, "exclu par la boîte d'É5 (motif scellé au coffre)")
            primaires.pop(i, None)
        for i in non_relus:
            self.exclus_techniques[i] = "non relu (technique)"
        s20 = regle_s20(primaires, ambigus, **self.pp["s20"])
        cf = self.pp["controles_forme"]
        elems19 = [{"groupe": i, "classe": 1 if primaires[i] == "P" else 0,
                    "indices": indices_forme(fv.texte_plat(self.rendus[i]), len(self.rendus[i]["contenu"]))}
                   for i in sorted(primaires) if i not in ambigus]
        s19 = aire_forme(elems19, ridge=cf["ridge"])
        kimi = [f for f in self.passe1 if self.aiguilleur.a_passeport(f)]
        if len(kimi) < cf["s18_effectif_min"]:
            s18 = {"aire": None, "motif": f"non évaluée : {len(kimi)} fiches de Kimi < {cf['s18_effectif_min']} (réserve)"}
        else:
            elems18 = [{"groupe": i, "classe": 1, "indices": indices_forme(fv.texte_plat(f), len(f["contenu"]))}
                       for i, f in sorted(self.rendus.items()) if self.aiguilleur.a_passeport(f)]
            elems18 += [{"groupe": f["ident"], "classe": 0, "indices": indices_forme(fv.texte_plat(f), len(f["contenu"]))} for f in kimi]
            s18 = aire_forme(elems18, ridge=cf["ridge"])
        detail = {"ambigus": sorted(ambigus), "defaut_non_vu": sorted(defaut_non_vu), "non_relus": sorted(non_relus)}
        n_primaires = len(primaires)
        del cle, primaires
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
            motifs.append("É5bis : témoins à replanter — relancer le pré-pilote avec temoins.version = 2 et l'attestation "
                          f"{ATTESTATION_V1} (compte commun A6/A7)" if version < 2 else "deux versions de témoins épuisées : C5 non satisfaite")
        self.coffre.deposer(self.tache("e5-detail"), detail)
        sortie = {"passe": not motifs, "motif": " ; ".join(motifs) or None, "ambigus": len(ambigus), "s20": s20,
                  "s18": s18, "s19": s19, "defaut_vu": round(part_vu, 6), "exclus": len(self.exclus),
                  "non_relus": len(non_relus), "version_temoins": version}
        self.coffre.noter_sortie_garde(jeton, {"passe": sortie["passe"], "primaires": n_primaires, "ambigus": len(ambigus),
                                               "defaut_non_vu": len(defaut_non_vu), "non_relus": len(non_relus),
                                               "s18_aire": s18.get("aire"), "s19_aire": s19.get("aire")})
        return sortie

    # --- É6 : ordre par identifiant opaque -----------------------------------------------------------------------------------

    def etape_e6_juges(self, etat):
        for i in sorted(self.rendus):  # identifiants opaques tirés (pp2-ident-fond-n) : l'ordre ne dépend pas de la classe
            f = self.rendus[i]
            if self.aiguilleur.a_passeport(f) and i not in self.exclus and i not in self.exclus_techniques:
                if f["empreinte"] != empreinte_objet(f["contenu"]):
                    raise NoeudArret(f"A13 : empreinte du témoin {i} différente de celle scellée")
                self.juger(f, "e6", etat)

    # --- É9 : liste de réduction scellée -------------------------------------------------------------------------------------

    def etape_e9_anteriorite(self, etat):
        an = self.pp["anteriorite"]
        fiches = json.loads(self.piece(an["fiches"]))["fiches"]
        if self.budget.etapes["e9_anteriorite"]["reduite_appliquee"]:
            garde = set(lire_liste_reduite(self.conf))  # jamais la clé d'antériorité (CL19-03)
            fiches = [f for f in fiches if f["ident"] in garde]
            self.ev("e9-reduite", fiches=len(fiches), source="liste de réduction scellée")
        self._verifier_fiches(etat, fiches, "e9")

    # --- exécution -----------------------------------------------------------------------------------------------------------

    def _deposer_cles_une_fois(self):
        if not self._cles_deposees:
            self._cles_deposees = True
            self.deposer_cles()

    def executer(self):
        self.etage1_resultats = {}
        ecrire_json_scelle(os.path.join(self.sortie, "manifeste-depart.json"), {
            "version": VERSION, "specification": "brouillon 7 (799b9ca9…)", "configuration_sha256": self.conf["empreinte_configuration"],
            "go": self.go, "plan": list(self.plan), "bras": self.bras_decl, "prefixe_taches": self.prefixe,
            "gardes_e0": self.gardes_e0, "lectures": {k: self.pp[k] for k in ("L1", "L2", "d_g")},
            "m4": "non étalonné (M4 sans témoins concrets : aucun lot du bras d'attaque servi)",
            "lectures_par_programme_permises": sorted([n, r] for n, r in self.coffre.lectures_permises),
            "sessions": {"base": self.base_sessions, "regle": "hors de la sortie (CL19-04)"},
            "regle_de_lecture": "aucun verdict d'É6/É7 ni clé ouvert avant la fin d'É9 ; deux lectures par programme de la clé des "
                                "classes (É3, É5), journalisées au coffre, comptes seulement (A21 : décision ouverte de Lazar) ; "
                                "au nœud, rien n'est ouvert (O12)"})
        resultat = None
        try:
            for nom in self.plan:
                self.jouer_etape(nom, getattr(self, "etape_" + nom))
                if not self.c13_ou_noeud(nom):
                    break
            self._deposer_cles_une_fois()
            if self.noeud:
                raise NoeudArret(self.noeud)
            for i, f in sorted(self.rendus.items()):
                self.etage1_resultats[i] = bool(self.etage1.signaler(f))
            self.coffre.deposer(self.tache("etage1"), self.etage1_resultats)
            self.coffre.declarer_fin_e9()  # après É9 et É9b
            verdicts = self.ouvrir_verdicts(sorted(set(self.rendus) | {f["ident"] for f in self.fusions}))
            resultat = self._analyse_m1(verdicts)
            ecrire_json_scelle(os.path.join(self.sortie, "analyse-m1.json"), resultat)
        except NoeudArret as e:
            self.noeud = self.noeud or str(e)
            self.ev("noeud-rien-ouvert", regle="O12 : ni fin d'É9, ni clé, ni verdict, ni analyse ; main rendue à Lazar")
            self._deposer_cles_une_fois()
            if "É5bis" in self.noeud and self.pp["temoins"]["version"] == 1:
                ecrire_json_scelle(os.path.join(self.sortie, ATTESTATION_V1), {
                    "version": VERSION, "version_temoins_epuisee": 1, "noeud": "É5bis",
                    "configuration_sha256": self.conf["empreinte_configuration"]})
            raise
        except Exception as e:
            self.arret = f"{type(e).__name__} : {str(e)[:500]}"
            raise
        finally:
            self.aiguilleur.sceller()
            rangement = self.ranger_sessions()
            ecrire_json_scelle(os.path.join(self.sortie, "manifeste-fin.json"), {
                "version": VERSION, "arret": self.arret, "noeud": self.noeud, "evenements": self.evenements,
                "etapes": self.etapes_etat, "budget": self.budget.etat(), "graines": self.graines.manifeste(),
                "coffre": self.coffre.journal(), "suivi_roles": self.suivi.etat(), "bras": self.bras_decl,
                "non_produits": self.non_produits, "exclus": self.exclus, "exclus_techniques": self.exclus_techniques,
                "exclues_a4": self.exclues_a4, "rendus": len(self.rendus), "fonds": len(self.fonds),
                "m5": {k: len(v) for k, v in self.m5.items()}, "e5": self.decisions_e5,
                "juges_absents": self.absents_juges, "modele_servi_juges": self.modele_servi_juges,
                "sessions": {"base": self.base_sessions, "nombre": len(self.sessions), "rangement": rangement}})
        return resultat

    def _analyse_m1(self, verdicts):
        cle = self.coffre.ouvrir(self.tache("cle-classes"))
        detail = self.coffre.ouvrir(self.tache("e5-detail"))
        retires = set(detail["ambigus"]) | set(self.exclus) | set(self.exclus_techniques)
        prim = {i for i, v in cle.items() if (v["classe"] == "P" or v["classe"] in CLASSES_N) and i not in retires}
        attendus = {i: ("P" if cle[i]["classe"] == "P" else "N") for i in sorted(prim) if i in verdicts}
        notables = {j["etiquette"]: {i: (verdicts[i].get(j["etiquette"]) or {}).get("notable") if verdicts[i].get(j["etiquette"]) else None
                                     for i in attendus} for j in self.conf["juges"]}
        from .mesures_v54 import etalonner_juges_v54
        return {"m1": etalonner_juges_v54(notables, attendus, **self.pp["seuils_m1"]) if attendus else "aucun témoin primaire jugé",
                "temoins_primaires_juges": len(attendus), "lecture": "verdict de porte prononcé par un sous-agent neuf (R13)"}


__all__ = ("PrePiloteV55", "controle_ancres_v55", "verifier_configuration_pre_pilote_v55", "lire_liste_reduite",
           "lire_attestation_v1", "EtageUnAbsent", "PLAN", "ATTESTATION_V1")
