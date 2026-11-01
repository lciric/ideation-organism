"""Génération et course 2, version 55 — au-dessus de `course2_v54` (inchangé, R12).

| constat | correction |
|---|---|
| CL19-02 | après un **nœud** (étape « non mesurée »), la génération n'écrit plus la mémoire ni le classement, ne déclare pas la fin de la phase de mesure, n'ouvre aucun verdict ni aucune clé ; elle dépose les clés (sans les ouvrir), écrit le manifeste de fin et rend la main (la course lève `NoeudArret` avec le bilan, comme en v54) |
| CL19-01 | déclaration des bras v55 : la cause « source absente » du bras Gu-Krenn est gardée (A19 : déclaré, compté C12, sans arrêt) ; la garde R5 ligne 20 devient « sans objet (déclarée) » au lieu de refuser le départ (`gardes_e0_v55`) |
| CL19-08 (ligne 21) | `verifier_bascule_gk(decl_e0, decl)` : déclaration Gu-Krenn absente à É0 → arrêt ; changée après É0 → arrêt ; jouée par la génération avant les lectures d'étiquettes, et rejouée à É0 |
| CL19-09 | bras méta lu par `bisociateur_v55.lire_annexe_meta_v55` (brouillon relu et rapport recalculés, différence limitée) |
| CL19-10 | causes (iii) et (iv) de M9 : « non produit (moins de 2 fiches étiquetées) » (méta) et « non produit (moins de 2 fiches notables) » (Gu-Krenn) |
| CL19-04, CL19-10 (A2), CL19-03 | noyau v55 (`OrchestreV55`) : sessions hors de la sortie ; modèle servi absent = arrêt A2 ; coffre v55 |
"""

import copy
import json
import os

from . import bisociateur_v54 as b54
from . import bisociateur_v55 as b55
from . import course2_v53 as c53
from . import course2_v54 as c54
from .configuration_v53 import ConfigurationRefusee, chemin_piece, texte_piece
from .juges_croises_v53 import classement
from .noyau_v54 import NoeudArret
from .noyau_v55 import OrchestreV55
from .outils import EcrasementInterdit, ecrire_json_scelle, lister_fichiers, sha256_fichier

VERSION = "course-2-generation-v55"
ETAPES = c54.ETAPES
CAUSE_SOURCE_ABSENTE = "non produit (source absente)"
CAUSE_ANNEXE = "non produit (annexe non conforme)"


class BasculeGuKrennInterdite(RuntimeError):
    """R5 ligne 21 : déclaration Gu-Krenn absente à É0, ou changée après É0."""


def verifier_bascule_gk(decl_e0, decl_courante):
    d0 = (decl_e0 or {}).get("gu_krenn")
    if not isinstance(d0, dict) or not (("mode" in d0 and d0.get("produit")) or (d0.get("produit") is False and d0.get("cause"))):
        raise BasculeGuKrennInterdite("A19 / ligne 21 : déclaration du bras Gu-Krenn absente à É0 : arrêt")
    if (decl_courante or {}).get("gu_krenn") != d0:
        raise BasculeGuKrennInterdite("A19 / ligne 21 : déclaration du bras Gu-Krenn changée après É0 : arrêt")
    return True


def _piece_annexe(conf, m, cle):
    x = m["annexe"].get(cle)
    if not isinstance(x, dict) or not x.get("chemin") or not x.get("sha256"):
        return None
    return chemin_piece(conf, x["chemin"]), x["sha256"]


def declarer_bras_v55(conf):
    """É0 : bras basique et Gu-Krenn comme la v53 (cause « source absente » gardée : A19) ; bras méta lu par la v55 (I-9)."""
    decl, params = c53.declarer_bras(conf)
    if "gu_krenn" in decl and not decl["gu_krenn"]["produit"]:
        decl["gu_krenn"]["cause"] = CAUSE_SOURCE_ABSENTE  # A19 : déclaré à É0, compté (C12, O15), pas un échec de garde
    b = conf["bisociateur"]
    if "meta" in b["bras"]:
        try:
            m = b["meta"]
            texte_lecteur = texte_piece(conf, b["consigne_lecteur_etiquettes"]) if m["definitions"] == "consigne" else None
            p, jeu = b55.lire_annexe_meta_v55(chemin_piece(conf, m["annexe"]["chemin"]), m["annexe"]["sha256"],
                                              definitions=m["definitions"], texte_consigne_lecteur=texte_lecteur,
                                              brouillon_relu=_piece_annexe(conf, m, "brouillon_relu"),
                                              rapport=_piece_annexe(conf, m, "rapport_contre_lecture"))
            non_vacuite = b54.verifier_non_vacuite(p, jeu)
            n0, n1 = p["niches"][:2]
            b54.garde_desaccord_v54(b54.score_meta, p, n0, n1, set(), set())
            p["_s28"] = b54.seuils_s28(p, m["s28"])
            params["meta"] = p
            decl["meta"] = {"produit": True, "annexe_sha256": m["annexe"]["sha256"], "non_vacuite_e0": non_vacuite,
                            "s28": p["_s28"], "definitions": m["definitions"]}
        except (b54.BisociationRefusee, OSError, ValueError, KeyError, TypeError) as e:
            params.pop("meta", None)
            decl["meta"] = {"produit": False, "cause": CAUSE_ANNEXE, "motif": str(e)[:300]}
    return decl, params


class GenerationV55(OrchestreV55, c54.GenerationV54):
    def __init__(self, conf, sortie, adaptateurs, **kw):
        super().__init__(conf, sortie, adaptateurs, **kw)
        self.bras_decl, self.bras_params = declarer_bras_v55(conf)
        self.bras_decl_e0 = copy.deepcopy(self.bras_decl)

    def etape_etiquettes(self, etat):
        if "gu_krenn" in self.conf["bisociateur"]["bras"]:
            verifier_bascule_gk(self.bras_decl_e0, self.bras_decl)
        super().etape_etiquettes(etat)

    def _notes(self, eligibles):
        notes, departage, causes = super()._notes(eligibles)
        l1n, l2n = (l["etiquette"] for l in self.conf["lecteurs_etiquettes"])
        if "meta" in self.etiquettes and not notes.get("meta"):
            m = self.conf["bisociateur"]["meta"]
            l1, l2 = self.etiquettes["meta"][l1n], self.etiquettes["meta"][l2n]
            retenues = [f for f in eligibles if b54.retenir_meta(l1.get(f["ident"]), l2.get(f["ident"]), m["regle_divergence"],
                                                                  m["structures"]) is not None]
            if len(retenues) < 2:
                causes["meta"] = "non produit (moins de 2 fiches étiquetées)"
        if "gu_krenn" in self.etiquettes and not notes.get("gu_krenn"):
            l1, l2 = self.etiquettes["gu_krenn"][l1n], self.etiquettes["gu_krenn"][l2n]
            notables = [f for f in eligibles if len(set(l1.get(f["ident"], [])) | set(l2.get(f["ident"], []))) >= 2]
            causes["gu_krenn"] = ("non produit (moins de 2 fiches notables)" if len(notables) < 2
                                  else "non produit (aucune paire éligible)")
        return notes, departage, causes

    def executer(self):
        depart = {"version": VERSION, "generation": self.numero, "configuration_sha256": self.conf["empreinte_configuration"],
                  "go": self.go, "bras": self.bras_decl, "etapes": list(ETAPES), "prefixe_taches": self.prefixe,
                  "choix_v54": {k: c53._get(self.conf, k) for k in ("budget.portee_plafond", "garde_kimi.refus_aiguilleur",
                                                                     "garde_kimi.arret_metteur_fusion", "tableau.juger_passe_tableau",
                                                                     "bisociateur.fournisseurs_entree", "a4.mode", "a4.action")},
                  "adaptateurs": {k: (a.description() if hasattr(a, "description") else type(a).__name__) for k, a in self.ad.items()},
                  "regle_de_lecture": "aucun verdict ni clé lu avant la fin de la phase de mesure (A21) ; au nœud, rien n'est ouvert (O12)",
                  "sessions": {"base": self.base_sessions, "regle": "hors de la sortie (CL19-04)"},
                  "manifeste_r9": c53.manifeste_r9(self.graines)}
        ecrire_json_scelle(os.path.join(self.sortie, "manifeste-depart.json"), depart)
        resultat = []
        try:
            for nom in ETAPES:
                self.jouer_etape(nom, getattr(self, "etape_" + nom))
                if not self.c13_ou_noeud(nom):
                    break
            self.deposer_cles()
            if self.noeud:  # CL19-02 / O12 : rien n'est lu de ce qui a été mesuré ; ni fin d'É9, ni ouverture, ni analyse
                self.ev("noeud-rien-ouvert", regle="O12 : rejeu de la seule mesure non mesurée sur GO ; rien n'en a été lu")
                return resultat
            lot = [self.fiches[i] for i in self.ordre if self.aiguilleur.a_passeport(self.fiches[i])]
            ecrire_json_scelle(os.path.join(self.sortie, "memoire.json"), self.memoire.detecter(lot))
            self.coffre.declarer_fin_e9()
            verdicts = self.ouvrir_verdicts([f["ident"] for f in lot])
            ag = self.conf["agregation"]
            resultat = classement(verdicts, ag["regle"], ag.get("q"))
            ecrire_json_scelle(os.path.join(self.sortie, "classement.json"), {
                "lignes": [{k: l[k] for k in ("ident", "rang", "notable", "n_notables", "n_presents", "somme_x")}
                           | {"exploratoire": bool(self.fiches[l["ident"]]["meta"].get("exploratoire"))} for l in resultat],
                "regle_agregation": ag, "fusions_comptees_a_part": [f["ident"] for f in self.fusions], "noeud": self.noeud})
            ecrire_json_scelle(os.path.join(self.sortie, "fiches.json"),
                               {f["ident"]: {"contenu": f["contenu"], "empreinte": f["empreinte"], "meta": f["meta"]} for f in lot})
            self.memoire.ajouter_memoire(lot, self.numero)
        except Exception as e:
            self.arret = f"{type(e).__name__} : {str(e)[:500]}"
            raise
        finally:
            self.aiguilleur.sceller()
            rangement = self.ranger_sessions()
            fin = {"version": VERSION, "generation": self.numero, "arret": self.arret, "noeud": self.noeud,
                   "evenements": self.evenements, "etapes": self.etapes_etat, "budget": self.budget.etat(),
                   "graines": self.graines.manifeste(), "coffre": self.coffre.journal(), "garde_kimi": self.garde_kimi.etat(),
                   "roles_arretes": self.roles_arretes, "suivi_roles": self.suivi.etat(), "bras": self.bras_decl,
                   "non_produits": self.non_produits, "c12": b54.compter_c12(self.bras_decl, self.non_produits),
                   "paires": {"nombre": sum(len(v) for v in self.paires.values()), "coffre": self.tache("paires-par-bras")},
                   "desaccord_des_paires": ("lu par paire après le choix, déposé au coffre ; hors score" if getattr(self, "journal_desaccord", None)
                                            else "non lu (aucune paire méta notée ou étape non jouée)"),
                   "refus_lectures": self.refus_lectures, "exclues_a4": self.exclues_a4, "appels_sautes": self.appels_sautes,
                   "fusions": {"comptees_a_part": len(self.fusions), "etiquette": "exploratoire (registre seulement)"},
                   "juges_absents": self.absents_juges, "modele_servi_juges": self.modele_servi_juges,
                   "sessions": {"base": self.base_sessions, "nombre": len(self.sessions), "rangement": rangement}}
            ecrire_json_scelle(os.path.join(self.sortie, "manifeste-fin.json"), fin)
            with open(os.path.join(self.sortie, "empreintes-sortie.txt"), "w", encoding="utf-8") as g:
                for rel in lister_fichiers(self.sortie):
                    if rel != "empreintes-sortie.txt" and not rel.endswith(".sha256"):
                        g.write(f"{sha256_fichier(os.path.join(self.sortie, rel))}  {rel}\n")
        return resultat

    def texte_heritage(self, resultat):
        return json.dumps([], ensure_ascii=False) if self.noeud else super().texte_heritage(resultat)


def executer_course_v55(conf, sortie, adaptateurs, *, nombre_generations, go, etage=None, environnement=None, horloge=None,
                        racine_sessions=None):
    """Comme la v54 (nœud : ni génération suivante, ni étage), avec `GenerationV55` et la machine jetable v55."""
    from .etage_entre_generations_v53 import preparer_generation
    from .etage_entre_generations_v55 import exiger_machine_jetable_v55, jouer_etage_v55
    if isinstance(nombre_generations, bool) or not isinstance(nombre_generations, int) or nombre_generations < 1:
        raise ConfigurationRefusee("nombre de générations : entier ≥ 1, aucun défaut")
    if etage is not None:
        exiger_machine_jetable_v55(environnement)
        for c in ("adaptateur", "reglages", "nombre", "tranche_index_sha256", "correspondance", "plafond_etage_usd"):
            if c not in etage:
                raise ConfigurationRefusee(f"étage entre générations : {c} manquant (aucun défaut)")
    if os.path.exists(sortie):
        raise EcrasementInterdit(f"sortie {sortie} déjà présente (R12)")
    os.makedirs(sortie)
    memoire, heritage, bilan, noeud = None, None, [], None
    for g in range(1, nombre_generations + 1):
        rs = None if racine_sessions is None else os.path.join(racine_sessions, f"generation-{g}")
        gen = GenerationV55(conf, os.path.join(sortie, f"generation-{g}"), adaptateurs, numero=g, memoire=memoire,
                            heritage_texte=heritage, go=go, horloge=horloge, racine_sessions=rs)
        resultat = gen.executer()
        ligne = {"generation": g, "fiches_classees": len(resultat), "notables": sum(l["notable"] for l in resultat),
                 "c13_satisfaite": gen.budget.etat()["c13_satisfaite"], "noeud": gen.noeud}
        if gen.noeud:
            noeud = f"génération {g} : {gen.noeud}"
            bilan.append(ligne)
            break
        memoire, heritage = gen.memoire, gen.texte_heritage(resultat)
        if etage is not None and g < nombre_generations:
            d = preparer_generation(os.path.join(sortie, f"etage-apres-generation-{g}"), resultat, gen.fiches,
                                    nombre=etage["nombre"], tranche_index_sha256=etage["tranche_index_sha256"],
                                    correspondance=etage["correspondance"], lisible=gen.arret is None)
            ligne["etage"] = jouer_etage_v55(etage["adaptateur"], d, reglages=etage["reglages"], environnement=environnement,
                                             executer=etage.get("executer"))
        bilan.append(ligne)
    ecrire_json_scelle(os.path.join(sortie, "bilan-course.json"), {"version": VERSION, "go": go, "generations": bilan, "noeud": noeud})
    if noeud:
        raise NoeudArret(noeud)
    return bilan


__all__ = ("GenerationV55", "declarer_bras_v55", "verifier_bascule_gk", "BasculeGuKrennInterdite", "executer_course_v55",
           "CAUSE_SOURCE_ABSENTE", "CAUSE_ANNEXE")
