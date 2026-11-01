"""Une génération de la course 2, version 54, et la course (générations successives, étage de tests de mort entre elles).

Mêmes six étapes que la v53, dans le même ordre, mais la sélection des paires passe dans l'étape protégée `etiquettes`
(comme É7b du brouillon 7 : lectures, accords S24 et S28, paires — programmes —, puis lecture du désaccord) ; l'étape
sacrifiable `fusions` ne fait plus qu'écrire les fusions, les aiguiller et les juger (L5 : fusions retirées, paires gardées).

| étape | contenu | rôle exigé |
|---|---|---|
| `proposition` | passe 1 de chaque proposeur, chaque case ; héritage de la génération précédente sous garde A4 (CL18-17) | protégée |
| `aiguillage` | aiguilleur sur la passe 1 ; garde de Kimi (S12, choix 6 et 7) | protégée |
| `juges` | trois juges sur chaque fiche à passeport, un appel par fiche et par juge | protégée |
| `passe_tableau` | tableau minimal (programme) ; passe « tableau » ; aiguilleur ; juges si `tableau.juger_passe_tableau` (choix 11) | sacrifiable |
| `etiquettes` | trois lectures par fiche (concepts, vocabulaire, niches) ; S28 (I-3) ; paires (I-7, I-8) ; désaccord par paire (I-2) | protégée |
| `fusions` | fusions à l'aveugle (ordre tiré par la tâche `<préfixe>-bisoc-ordre`) ; aiguilleur ; juges | sacrifiable |

Puis, sans dépense : mémoire anti-redite ; fin de la phase de mesure ; classement ; sorties scellées. **Nœud (CL18-02)** : dès
qu'une étape est « non mesurée » (budget ou technique), la génération ne lance plus rien et la course ne continue pas
(ni génération suivante, ni étage). Les paires par bras sont déposées au coffre (le manifeste de fin n'en porte que le
nombre : CL18, section B).

Tâches de graines (CL18-07) : préfixe injecté (`graines.prefixe`) ; génération 1 : `<p>-bisoc-ordre` (ordre des bras puis
ordre d'écriture des fusions, deux tirages successifs du même générateur, comme le brouillon 7), `<p>-bisoc-gk`,
`<p>-bisoc-meta`, `<p>-bisoc-n` (bras basique), `<p>-anonymisation-<juge>-<fiche>`, `<p>-ident-…` ; génération g > 1 :
préfixe `<p>-g<g>`.
"""

import datetime
import json
import os

from . import bisociateur_v54 as b54
from . import course2_v53 as c53
from . import fiches_v54 as fv
from .aiguilleur_v53 import DebordementKimi
from .configuration_v53 import ConfigurationRefusee, chemin_piece, texte_piece
from .juges_croises_v53 import classement
from .memoire_v53 import Memoire
from .noyau_v54 import AiguilleurV54, GardeKimiV54, NoeudArret, Orchestre
from .outils import EcrasementInterdit, ecrire_json_scelle, extraire_bloc_json, lister_fichiers, sha256_fichier
from .tableau_v53 import TableauRefuse, construire, texte_servi, une_ligne, verifier_tableau

VERSION = "course-2-generation-v54"
ETAPES = c53.ETAPES
TACHE_BRAS = {"basique": "bisoc-n", "gu_krenn": "bisoc-gk", "meta": "bisoc-meta"}
NATURE = {"basique": "concepts", "gu_krenn": "vocabulaire", "meta": "niches"}


def verifier_configuration_generation_v54(conf):
    c53.verifier_configuration_generation(conf)
    roles = {e["nom"]: e["role"] for e in conf["budget"]["etapes"]}
    if roles.get("etiquettes") not in (None, "protegee"):
        raise ConfigurationRefusee("budget.etapes : etiquettes doit être protégée (lectures et paires jamais sacrifiées)")
    return True


def declarer_bras_v54(conf):
    """É0 : déclaration v53 (A19, A20, garde 24), puis, pour le bras méta, la lecture v54 de l'annexe (I-3, I-4, I-6, I-9),
    la non-vacuité rejouée (I-10, garde 22a/22b) et la garde du désaccord par valeur (I-2, garde 24)."""
    decl, params = c53.declarer_bras(conf)
    b = conf["bisociateur"]
    if "meta" in b["bras"]:
        try:
            m = b["meta"]
            texte_lecteur = texte_piece(conf, b["consigne_lecteur_etiquettes"]) if m["definitions"] == "consigne" else None
            p, jeu = b54.lire_annexe_meta_v54(chemin_piece(conf, m["annexe"]["chemin"]), m["annexe"]["sha256"],
                                              definitions=m["definitions"], texte_consigne_lecteur=texte_lecteur)
            non_vacuite = b54.verifier_non_vacuite(p, jeu)
            n0, n1 = p["niches"][:2]
            b54.garde_desaccord_v54(b54.score_meta, p, n0, n1, set(), set())
            p["_s28"] = b54.seuils_s28(p, m["s28"])
            params["meta"] = p
            decl["meta"] = {"produit": True, "annexe_sha256": m["annexe"]["sha256"], "non_vacuite_e0": non_vacuite,
                            "s28": p["_s28"], "definitions": m["definitions"]}
        except (b54.BisociationRefusee, OSError, ValueError, KeyError, TypeError) as e:
            params.pop("meta", None)
            decl["meta"] = {"produit": False, "cause": "non produit (annexe non conforme)", "motif": str(e)[:300]}
    return decl, params


class GenerationV54(Orchestre):
    ETAPES = ETAPES

    @staticmethod
    def verifier_configuration(conf):
        return verifier_configuration_generation_v54(conf)

    @staticmethod
    def fournisseurs_requis(conf):
        return ({p["fournisseur"] for p in conf["proposeurs"]} | {j["fournisseur"] for j in conf["juges"]}
                | {l["fournisseur"] for l in conf["lecteurs_etiquettes"]} | {conf["aiguilleur"]["fournisseur"]}
                | {conf["bisociateur"]["metteur_fusion"]["fournisseur"]})

    def __init__(self, conf, sortie, adaptateurs, *, numero=1, memoire=None, heritage_texte=None, go=None, horloge=None):
        type(self).verifier_configuration(conf)
        if os.path.exists(sortie):
            raise EcrasementInterdit(f"sortie {sortie} déjà présente : jamais écrasée (R12)")
        manquants = sorted(type(self).fournisseurs_requis(conf) - set(adaptateurs))
        if manquants:
            raise ConfigurationRefusee("adaptateur absent pour : " + ", ".join(manquants))
        os.makedirs(sortie)
        p = conf["graines"]["prefixe"]
        super().__init__(conf, sortie, adaptateurs, prefixe_taches=p if numero == 1 else f"{p}-g{numero}", horloge=horloge)
        self.numero, self.go, self.heritage = numero, go, heritage_texte
        self.memoire = memoire or Memoire(methode=conf["memoire"]["methode"], seuil=conf["memoire"]["seuil"],
                                          taille_bardeau=conf["memoire"].get("taille_bardeau"))
        ai = conf["aiguilleur"]
        self.aiguilleur = AiguilleurV54(self, etiquette=ai["etiquette"], modele=ai["modele"], fournisseur=ai["fournisseur"],
                                        consigne=ai["consigne"], dossier=os.path.join(sortie, "aiguillage"))
        gk = conf["garde_kimi"]
        self.garde_kimi = GardeKimiV54(gk["debordement_max"], gk["refus_aiguilleur"])
        self.fiches, self.ordre, self.roles_arretes = {}, [], {}
        self.passe1, self.passe2, self.fusions = [], [], []
        self.bras_decl, self.bras_params = declarer_bras_v54(conf)
        self.paires, self.non_produits, self.etiquettes, self.accords = {}, {}, {}, {}
        self.refus_lectures = {}
        self.arret = None

    # --- proposeurs -------------------------------------------------------------------------------------------------------

    def _heritage_garde(self):
        if not self.heritage:
            return None
        lignes = json.loads(self.heritage)
        gardees = []
        for l in lignes:
            trouvees = fv.trouver(json.dumps(l, ensure_ascii=False), self.interdites, self.a4_mode)
            if not trouvees:
                gardees.append(l)
            elif self.a4_action == "fiche_exclue":
                self.ev("incident-a4-heritage-ligne-exclue", etiquettes=trouvees)
            else:
                raise fv.EtiquetteDansEntree("A4 : étiquette interdite dans le texte d'héritage (" + ", ".join(trouvees) + ")")
        return json.dumps(gardees, ensure_ascii=False, indent=1)

    def _proposer(self, etat, passe, supplement_par_case=None):
        nouvelles = []
        heritage = self._heritage_garde() if passe == 1 else None
        etape = "proposition" if passe == 1 else "passe_tableau"
        for ic, case in enumerate(self.conf["cases"]):
            for p in self.conf["proposeurs"]:
                if p["etiquette"] in self.roles_arretes:
                    continue
                consigne = self.piece(p["consigne"] if passe == 1 else self.conf["tableau"]["consigne_passe"])
                consigne = consigne.rstrip() + f"\n\n## Case\nTexte : {case[0]} ; bras : {case[1]}\n"
                if heritage:
                    consigne += "\n## Fiches de la génération précédente (titres, résumés, verdict agrégé)\n" + heritage + "\n"
                if supplement_par_case is not None:
                    consigne += "\n## Tableau minimal de ta case (titres et résumés seulement)\n```json\n" + supplement_par_case[ic] + "\n```\n"
                a = self.appel(etat, role=p["etiquette"], role_kit="proposeur_ideation", fournisseur=p["fournisseur"],
                               modele=p["modele"], consigne=consigne, plafond_role="proposeur",
                               session=(etape, ic, p["etiquette"]), lire=lambda t: _fiches_ou_none(t))
                if a is None or a["lu"] is None:
                    continue
                for k, b in enumerate(a["lu"]):
                    ident = "f" + self.graines.jeton_opaque(self.tache("ident", passe, ic, p["etiquette"], k), 6)
                    try:
                        f = fv.preparer(b, self.conf["champs_fiche"], ident=ident, case=case, fournisseur=p["fournisseur"], passe=passe)
                    except fv.FicheRefusee as e:
                        self.ev("fiche-refusee", proposeur=p["etiquette"], passe=passe, case=ic, motif=str(e)[:200])
                        continue
                    f["meta"]["proposeur"] = p["etiquette"]
                    self.fiches[ident] = f
                    self.ordre.append(ident)
                    nouvelles.append(f)
        return nouvelles

    def _aiguiller(self, fiches, etat, lot):
        for f in fiches:
            classe = self.aiguilleur.classer(f, etat, lot)
            if classe is None:
                continue
            if f["meta"]["fournisseur"] == "kimi" and f["meta"]["origine"] == "proposition":
                self.garde_kimi.noter(f, classe, self.aiguilleur.decisions[f["ident"]]["refus"])
        try:
            self.garde_kimi.verifier()
        except DebordementKimi as e:
            kimi = [p["etiquette"] for p in self.conf["proposeurs"] if p["fournisseur"] == "kimi"]
            mf = self.conf["bisociateur"]["metteur_fusion"]
            if self.conf["garde_kimi"]["arret_metteur_fusion"] and mf.get("fournisseur") == "kimi":
                kimi.append(mf["etiquette"])
            for k in kimi:
                self.roles_arretes.setdefault(k, str(e))
            self.ev("arret-role-kimi", motif=str(e), roles=kimi, noeud=True)

    def _juger(self, fiches, lot, etat):
        for f in fiches:
            if self.aiguilleur.a_passeport(f):
                self.juger(f, lot, etat)

    # --- étapes -----------------------------------------------------------------------------------------------------------

    def etape_proposition(self, etat):
        self.passe1 = self._proposer(etat, 1)

    def etape_aiguillage(self, etat):
        self._aiguiller(self.passe1, etat, "passe1")

    def etape_juges(self, etat):
        self._juger(self.passe1, "passe1", etat)

    def etape_passe_tableau(self, etat):
        t = self.conf["tableau"]
        tableaux = []
        try:
            for case in self.conf["cases"]:
                tab = construire(self.passe1, case, self.aiguilleur, champ_titre=self.conf["champ_titre"], champ_resume=t["champ_resume"],
                                 longueur_max_titre=t["longueur_max_titre"], longueur_max_resume=t["longueur_max_resume"])
                verifier_tableau(tab, case, self.aiguilleur, self.fiches, longueur_max_titre=t["longueur_max_titre"],
                                 longueur_max_resume=t["longueur_max_resume"])
                tableaux.append(tab)
        except TableauRefuse as e:
            self.ev("passe-tableau-arretee", motif=str(e))
            return
        ecrire_json_scelle(os.path.join(self.sortie, "tableaux.json"), tableaux)
        self.passe2 = self._proposer(etat, 2, [texte_servi(tb) for tb in tableaux])
        self._aiguiller(self.passe2, etat, "passe2")
        if t["juger_passe_tableau"]:
            self._juger(self.passe2, "passe2", etat)

    def _entree_bisociateur(self):
        four = self.conf["bisociateur"]["fournisseurs_entree"]
        return [f for f in self.passe1 if self.aiguilleur.a_passeport(f) and ("*" in four or f["meta"]["fournisseur"] in four)]

    def _liste(self, bras):
        if bras == "basique":
            return self.bras_params["basique"]["liste"]
        if bras == "gu_krenn":
            return self.bras_params["gu_krenn"].vocabulaire
        return b54.liste_servie(self.bras_params["meta"], self.conf["bisociateur"]["meta"]["definitions"])

    def _lire(self, etat, f, lecteur, bras):
        consigne = self.piece(self.conf["bisociateur"]["consigne_lecteur_etiquettes"]).rstrip()
        consigne += f"\n\n## Lecture : {NATURE[bras]}\n## Liste fermée\n```json\n{json.dumps(self._liste(bras), ensure_ascii=False)}\n```\n"
        self.aiguilleur.exiger_passeport(f, "un lecteur d'étiquettes")
        entree = self.servir(consigne, f, "un lecteur d'étiquettes")
        if entree is None:
            return None
        cle = "niche" if bras == "meta" else "etiquettes"
        a = self.appel(etat, role=lecteur["etiquette"], role_kit="juge_ideation", fournisseur=lecteur["fournisseur"],
                       modele=lecteur["modele"], consigne=entree, plafond_role="lecteur",
                       session=("etiquettes", lecteur["etiquette"], NATURE[bras], f["ident"]),
                       lire=lambda t: extraire_bloc_json(t, cle))
        if a is None or a["lu"] is None:
            return None
        try:
            if bras == "meta":
                p = self.bras_params["meta"]
                return b54.valider_niche_v54(a["lu"], p["niches"], p["types_structure"])
            return b54.b53.valider_etiquettes(a["lu"].get("etiquettes", []), self._liste(bras))
        except b54.BisociationRefusee as e:
            self.refus_lectures[bras] = self.refus_lectures.get(bras, 0) + 1
            self.ev("lecture-rejetee", bras=bras, lecteur=lecteur["etiquette"], ident=f["ident"], motif=str(e)[:200])
            return None

    def etape_etiquettes(self, etat):
        eligibles = self._entree_bisociateur()
        produits = [b for b in self.conf["bisociateur"]["bras"] if self.bras_decl[b]["produit"]]
        for bras in produits:
            self.etiquettes[bras] = {}
            for lecteur in self.conf["lecteurs_etiquettes"]:
                self.etiquettes[bras][lecteur["etiquette"]] = {}
                for f in eligibles:
                    lu = self._lire(etat, f, lecteur, bras)
                    if lu is not None:
                        self.etiquettes[bras][lecteur["etiquette"]][f["ident"]] = lu
        l1, l2 = (l["etiquette"] for l in self.conf["lecteurs_etiquettes"])
        if "meta" in self.etiquettes:
            self.accords["s28"] = b54.accord_s28(self.etiquettes["meta"][l1], self.etiquettes["meta"][l2],
                                                 self.bras_params["meta"]["_s28"])
        for bras in ("basique", "gu_krenn"):
            if bras in self.etiquettes:
                self.accords[f"s24_{bras}"] = b54.b53.accord_jaccard(self.etiquettes[bras][l1], self.etiquettes[bras][l2])
        ecrire_json_scelle(os.path.join(self.sortie, "accords.json"), self.accords)
        self.coffre.deposer(self.tache("lectures-etiquettes"), {  # affirmation centrale du lecteur conservée (I-2)
            b: {l: {i: (list(v) if not isinstance(v, tuple) else [v[0], sorted(x[0] for x in v[1]), v[2]]) for i, v in d.items()}
                for l, d in par.items()} for b, par in self.etiquettes.items()})
        self._choisir_paires(eligibles)
        self._desaccord(etat)

    def _notes(self, eligibles):
        axe_de = lambda f: f["contenu"].get(self.conf["champ_axe"])  # noqa: E731
        notes, departage, causes = {}, {}, {}
        par_case = {}
        for f in eligibles:
            par_case.setdefault(tuple(f["meta"]["case"]), []).append(f)
        l1n, l2n = (l["etiquette"] for l in self.conf["lecteurs_etiquettes"])
        for bras, lectures in self.etiquettes.items():
            l1, l2 = lectures[l1n], lectures[l2n]
            notes[bras], departage[bras] = {}, {}
            rng = self.graines.generateur(self.tache(TACHE_BRAS[bras]))
            retenues = {}
            if bras == "meta":
                m = self.conf["bisociateur"]["meta"]
                for f in eligibles:
                    r = b54.retenir_meta(l1.get(f["ident"]), l2.get(f["ident"]), m["regle_divergence"], m["structures"])
                    if r is not None:
                        retenues[f["ident"]] = r
            for groupe in par_case.values():
                for i, fa in enumerate(groupe):
                    for fb in groupe[i + 1:]:
                        q = b54.cle_paire(fa["ident"], fb["ident"])
                        if bras == "basique":
                            concepts = {x: set(l1.get(x, [])) | set(l2.get(x, [])) for x in q}
                            prm = self.bras_params["basique"]
                            notes[bras][q] = (b54.b53.score_basique(fa, fb, concepts, axe_de, prm["exposant"], prm["decalage"]), None)
                        elif bras == "gu_krenn":
                            ca = sorted(set(l1.get(fa["ident"], [])) | set(l2.get(fa["ident"], [])))
                            cb = sorted(set(l1.get(fb["ident"], [])) | set(l2.get(fb["ident"], [])))
                            n = self.bras_params["gu_krenn"].note(ca, cb)
                            if n is not None:
                                notes[bras][q] = (n, None)
                        else:
                            ra, rb = retenues.get(fa["ident"]), retenues.get(fb["ident"])
                            if ra is None or rb is None or ra[0] == rb[0]:
                                continue
                            prm = self.bras_params["meta"]
                            s = b54.score_meta(prm, ra[0], rb[0], ra[1], rb[1])
                            notes[bras][q] = ((1, s) if s > 0 else (0,) + b54.score_repli(prm, ra[0], rb[0], ra[1], rb[1]),
                                              "profil" if s > 0 else "hors profil")
            for q in notes[bras]:
                departage[bras][q] = float(rng.random())
            if bras == "meta" and not notes[bras]:
                causes["meta"] = ("non produit (niches indistinctes sur ce lot)" if len({r[0] for r in retenues.values()}) == 1
                                  and len(retenues) >= 2 else "non produit (aucune paire éligible)")
        return notes, departage, causes

    def _choisir_paires(self, eligibles):
        g = self.graines.generateur(self.tache("bisoc-ordre"))
        ordre = [b for b in self.conf["bisociateur"]["bras"] if self.bras_decl[b]["produit"]]
        self.ordre_bras = [ordre[i] for i in g.permutation(len(ordre))]
        self._rng_ordre = g  # le second tirage (ordre d'écriture des fusions) vient du même générateur
        self.notes, self.departage, causes = self._notes(eligibles)
        self.paires, np_ = b54.choisir_paires_v54(eligibles, self.notes, self.ordre_bras, self.conf["bisociateur"]["k_paires"],
                                                  self.aiguilleur, self.departage, causes)
        self.non_produits.update(np_)
        self.profil = {b: {"|".join(q): self.notes[b][q][1] for q in ps} for b, ps in self.paires.items() if b == "meta"}
        self.horodatage_paires = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="microseconds")
        self.coffre.deposer(self.tache("paires-par-bras"), {"horodatage": self.horodatage_paires, "ordre_bras": self.ordre_bras,
                                                            "paires": {b: ["|".join(q) for q in ps] for b, ps in self.paires.items()},
                                                            "profil_meta": self.profil})

    def _desaccord(self, etat):
        """I-2 : après le choix et le dépôt scellé des paires ; deux lecteurs, un appel par paire ; journal au coffre."""
        self.journal_desaccord = None
        if "meta" not in self.notes or not self.notes["meta"]:
            return
        m = self.conf["bisociateur"]["meta"]["desaccord"]
        retenue = self.paires.get("meta", [None])[0] if self.paires.get("meta") else None
        paires = b54.paires_pour_desaccord(self.notes["meta"], self.departage["meta"], retenue, m["paires_max"])
        consigne = self.piece(m["consigne"])
        lignes = []
        for k, (ia, ib) in enumerate(paires):
            fa, fb = self.fiches[ia], self.fiches[ib]
            for f in (fa, fb):
                self.aiguilleur.exiger_passeport(f, "la lecture du désaccord")
            entree = b54.entree_desaccord(consigne, fa["contenu"].get(m["champ_affirmation"]), fb["contenu"].get(m["champ_affirmation"]))
            fv.garde(entree, self.interdites, self.a4_mode, "l'entrée de la lecture du désaccord")
            reponses = {}
            for lecteur in self.conf["lecteurs_etiquettes"]:
                a = self.appel(etat, role=lecteur["etiquette"], role_kit="juge_ideation", fournisseur=lecteur["fournisseur"],
                               modele=lecteur["modele"], consigne=entree, plafond_role="lecteur",
                               session=("desaccord", lecteur["etiquette"], k), lire=b54.valider_desaccord)
                reponses[lecteur["etiquette"]] = a["lu"] if a else None
            lignes.append({"paire": f"{ia}|{ib}", "reponses": reponses,
                           "horodatage": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="microseconds")})
        verifier_ordre_desaccord(self.horodatage_paires, lignes)
        self.journal_desaccord = {"horodatage_paires": self.horodatage_paires, "lignes": lignes,
                                  "regle": "lu après le choix des paires ; n'entre jamais dans le score (R-638, I-2)"}
        self.coffre.deposer(self.tache("desaccord-paires"), self.journal_desaccord)

    def etape_fusions(self, etat):
        a_ecrire = [(b, q) for b in self.ordre_bras for q in self.paires.get(b, [])]
        perm = self._rng_ordre.permutation(len(a_ecrire)) if a_ecrire else []
        a_ecrire = [a_ecrire[int(i)] for i in perm]
        mf = self.conf["bisociateur"]["metteur_fusion"]
        if mf["etiquette"] in self.roles_arretes:
            self.ev("fusions-non-produites", motif="rôle du metteur en fusion arrêté")
            return
        cle_bras, nouvelles = {}, []
        consigne_fusion = self.piece(self.conf["bisociateur"]["consigne_fusion"])
        for n, (bras, (ia, ib)) in enumerate(a_ecrire):
            entree = b54.b53.entree_fusion(consigne_fusion, self.fiches[ia], self.fiches[ib], [])
            fv.garde(json.dumps([fv.vue_servie(self.fiches[ia]), fv.vue_servie(self.fiches[ib])], ensure_ascii=False),
                     self.interdites, self.a4_mode, "l'entrée de fusion")
            a = self.appel(etat, role=mf["etiquette"], role_kit="proposeur_ideation", fournisseur=mf["fournisseur"], modele=mf["modele"],
                           consigne=entree, plafond_role="fusion", session=("fusions", n), lire=_fiches_ou_none)
            if a is None or a["lu"] is None:
                continue
            try:
                if len(a["lu"]) != 1:
                    raise fv.FicheRefusee("une fusion = une fiche")
                ident = "f" + self.graines.jeton_opaque(self.tache("ident-fusion", n), 6)
                f = fv.preparer(a["lu"][0], self.conf["champs_fiche"], ident=ident, case=self.fiches[ia]["meta"]["case"],
                                fournisseur=mf["fournisseur"], passe="fusion", origine="fusion")
            except fv.FicheRefusee as e:
                self.ev("fusion-refusee", rang=n, motif=str(e)[:200])
                continue
            f["meta"]["exploratoire"] = True
            self.fiches[ident] = f
            self.ordre.append(ident)
            nouvelles.append(f)
            cle_bras[ident] = {"bras": bras, "paire": [ia, ib]}
        self.coffre.deposer(self.tache("cle-bras"), cle_bras)
        self.fusions = nouvelles
        self._aiguiller(nouvelles, etat, "fusions")
        self._juger(nouvelles, "fusions", etat)

    # --- la génération ----------------------------------------------------------------------------------------------------

    def executer(self):
        depart = {"version": VERSION, "generation": self.numero, "configuration_sha256": self.conf["empreinte_configuration"],
                  "go": self.go, "bras": self.bras_decl, "etapes": list(ETAPES), "prefixe_taches": self.prefixe,
                  "choix_v54": {k: c53._get(self.conf, k) for k in ("budget.portee_plafond", "garde_kimi.refus_aiguilleur",
                                                                     "garde_kimi.arret_metteur_fusion", "tableau.juger_passe_tableau",
                                                                     "bisociateur.fournisseurs_entree", "a4.mode", "a4.action")},
                  "adaptateurs": {k: (a.description() if hasattr(a, "description") else type(a).__name__) for k, a in self.ad.items()},
                  "regle_de_lecture": "aucun verdict ni clé lu avant la fin de la phase de mesure (A21) ; seules les consommations",
                  "manifeste_r9": c53.manifeste_r9(self.graines)}
        ecrire_json_scelle(os.path.join(self.sortie, "manifeste-depart.json"), depart)
        resultat = []
        try:
            for nom in ETAPES:
                self.jouer_etape(nom, getattr(self, "etape_" + nom))
                if not self.c13_ou_noeud(nom):
                    break
            lot = [self.fiches[i] for i in self.ordre if self.aiguilleur.a_passeport(self.fiches[i])]
            ecrire_json_scelle(os.path.join(self.sortie, "memoire.json"), self.memoire.detecter(lot))
            self.deposer_cles()
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
                   "juges_absents": self.absents_juges, "modele_servi_juges": self.modele_servi_juges}
            ecrire_json_scelle(os.path.join(self.sortie, "manifeste-fin.json"), fin)
            with open(os.path.join(self.sortie, "empreintes-sortie.txt"), "w", encoding="utf-8") as g:
                for rel in lister_fichiers(self.sortie):
                    if rel != "empreintes-sortie.txt" and not rel.endswith(".sha256"):
                        g.write(f"{sha256_fichier(os.path.join(self.sortie, rel))}  {rel}\n")
        return resultat

    def texte_heritage(self, resultat):
        t = self.conf["tableau"]
        return json.dumps([{"titre": une_ligne(self.fiches[l["ident"]]["contenu"].get(self.conf["champ_titre"], ""), t["longueur_max_titre"]),
                            "resume": une_ligne(self.fiches[l["ident"]]["contenu"].get(t["champ_resume"], ""), t["longueur_max_resume"]),
                            "notable": l["notable"]} for l in resultat], ensure_ascii=False, indent=1)


def _fiches_ou_none(texte):
    try:
        return fv.fiches_du_texte(texte)
    except fv.FicheRefusee:
        return None


def verifier_ordre_desaccord(horodatage_paires, lignes):
    """Artefact d'ordre (annexe § 4) : une lecture du désaccord horodatée avant le scellement des paires est un arrêt."""
    for l in lignes:
        if l["horodatage"] < horodatage_paires:
            raise b54.BisociationRefusee("I-2 : lecture du désaccord antérieure au scellement des paires : le désaccord aurait pu "
                                         "influencer la sélection : arrêt")
    return True


def executer_course_v54(conf, sortie, adaptateurs, *, nombre_generations, go, etage=None, environnement=None, horloge=None):
    """Générations successives ; étage entre elles (machine jetable exigée avant toute dépense) ; **nœud** : une génération
    terminée sur un « non mesuré » arrête la course (ni génération suivante, ni étage ; CL18-02)."""
    from .etage_entre_generations_v53 import preparer_generation
    from .etage_entre_generations_v54 import exiger_machine_jetable_v54, jouer_etage_v54
    if isinstance(nombre_generations, bool) or not isinstance(nombre_generations, int) or nombre_generations < 1:
        raise ConfigurationRefusee("nombre de générations : entier ≥ 1, aucun défaut")
    if etage is not None:
        exiger_machine_jetable_v54(environnement)
        for c in ("adaptateur", "reglages", "nombre", "tranche_index_sha256", "correspondance", "plafond_etage_usd"):
            if c not in etage:
                raise ConfigurationRefusee(f"étage entre générations : {c} manquant (aucun défaut)")
    if os.path.exists(sortie):
        raise EcrasementInterdit(f"sortie {sortie} déjà présente (R12)")
    os.makedirs(sortie)
    memoire, heritage, bilan, noeud = None, None, [], None
    for g in range(1, nombre_generations + 1):
        gen = GenerationV54(conf, os.path.join(sortie, f"generation-{g}"), adaptateurs, numero=g, memoire=memoire,
                            heritage_texte=heritage, go=go, horloge=horloge)
        resultat = gen.executer()
        memoire, heritage = gen.memoire, gen.texte_heritage(resultat)
        ligne = {"generation": g, "fiches_classees": len(resultat), "notables": sum(l["notable"] for l in resultat),
                 "c13_satisfaite": gen.budget.etat()["c13_satisfaite"], "noeud": gen.noeud}
        if gen.noeud:
            noeud = f"génération {g} : {gen.noeud}"
            bilan.append(ligne)
            break
        if etage is not None and g < nombre_generations:
            d = preparer_generation(os.path.join(sortie, f"etage-apres-generation-{g}"), resultat, gen.fiches,
                                    nombre=etage["nombre"], tranche_index_sha256=etage["tranche_index_sha256"],
                                    correspondance=etage["correspondance"], lisible=gen.arret is None)
            ligne["etage"] = jouer_etage_v54(etage["adaptateur"], d, reglages=etage["reglages"], environnement=environnement,
                                             executer=etage.get("executer"))
        bilan.append(ligne)
    ecrire_json_scelle(os.path.join(sortie, "bilan-course.json"), {"version": VERSION, "go": go, "generations": bilan, "noeud": noeud})
    if noeud:
        raise NoeudArret(noeud)
    return bilan
