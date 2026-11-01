"""Une génération de la course 2 (v53) : proposeurs (Kimi par voie protocole compris), aiguilleur avant les juges, notation
croisée, tableau minimal, mémoire anti-redite, bisociateur à trois bras, règle de non-lecture, plafond S17 et règle d'A1,
étage de tests de mort entre générations (machine jetable).

Ordre des étapes (par dépendance, jamais par résultat ; noms exigés dans `budget.etapes` de la configuration) :

| étape | contenu | rôle attendu dans le plan |
|---|---|---|
| `proposition` | passe 1 de chaque proposeur, dans chaque case (texte, bras) | protégée |
| `aiguillage` | aiguilleur sur toutes les fiches de la passe 1 ; garde de niveau méthode de Kimi (S12) | protégée (jamais sacrifié) |
| `juges` | trois juges sur chaque fiche munie d'un passeport, un appel par fiche et par juge ; verdicts au coffre | protégée |
| `passe_tableau` | tableau minimal par case (programme), passe « tableau », aiguillage et juges de ses fiches | sacrifiable |
| `etiquettes` | deux lecteurs, trois lectures séparées par fiche (concepts, vocabulaire S31, niches) | protégée |
| `fusions` | paires des bras produits (programme), fusions à l'aveugle, aiguillage et juges des fusions | sacrifiable |

Puis, sans dépense : mémoire anti-redite sur tout le lot (et contre les générations précédentes) ; **fin de la phase de
mesure** (`coffre.declarer_fin_e9`) ; ouverture des verdicts ; classement agrégé ; sorties scellées ; étage de tests de mort
si la configuration le demande (machine jetable exigée). `manifeste-fin.json` est écrit sur tout chemin, arrêt compris.

Arrêts (aucun repli silencieux) : A4 (étiquette dans une entrée), A17 (fiche sans passeport à une destination), A2 (version
servie d'un juge changée), A21 (lecture avant la fin de la phase de mesure) arrêtent la génération ; A18 (tableau) arrête la
passe « tableau » ; M5 (débordement de Kimi au-dessus de S12) arrête le rôle proposeur de Kimi (nœud, consigné) ; A19, A20
rendent un bras « non produit », décidé à É0 ; A1 (règle de sacrifice) retire ou ne lance pas une étape.
"""

import json
import os

from . import bisociateur_v53 as bis
from .aiguilleur_v53 import Aiguilleur, DebordementKimi, GardeKimi
from .budget_v53 import JOUER, depuis_configuration
from .coffre_v53 import Coffre
from .configuration_v53 import ConfigurationRefusee, chemin_piece, texte_piece
from .fiches_v53 import FicheRefusee, fiches_du_texte, garde_etiquettes, preparer, vue_servie
from .graines_v53 import Graines
from .juges_croises_v53 import JugesCroises, classement
from .memoire_v53 import Memoire
from .outils import EcrasementInterdit, ecrire_json_scelle, extraire_bloc_json, lister_fichiers, sha256_fichier
from .tableau_v53 import TableauRefuse, construire, texte_servi, verifier_tableau

VERSION = "course-2-generation-v53"
ETAPES = ("proposition", "aiguillage", "juges", "passe_tableau", "etiquettes", "fusions")
CHAMPS_GENERATION = ("proposeurs", "cases", "plafonds_session", "etiquettes_interdites", "champ_axe", "memoire.methode",
                     "tableau.consigne_passe", "lecteurs_etiquettes")


def manifeste_r9(graines):
    """R9 : versions, empreinte de chaque module du pôle, règle des graines (la racine ; les tâches tirées sont au manifeste
    de fin). Le commit n'est pas lu ici (l'arbre livré n'est pas un dépôt) : l'opérateur le porte au registre du run."""
    import platform
    ici = os.path.dirname(os.path.abspath(__file__))
    return {"python": platform.python_version(), "numpy": graines.np.__version__, "racine_graines": graines.racine,
            "regle_graines": "numpy.random.SeedSequence(racine, spawn_key=(cle_de_tache(tache),))",
            "code_sha256": {n: sha256_fichier(os.path.join(ici, n)) for n in sorted(os.listdir(ici)) if n.endswith(".py")},
            "commit": "non lu (arbre hors dépôt) : à porter au registre du run par l'opérateur"}


class GenerationArretee(RuntimeError):
    pass


def _get(d, chemin):
    for k in chemin.split("."):
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return d


def verifier_configuration_generation(conf):
    manques = [f"{c} manquant" for c in CHAMPS_GENERATION if _get(conf, c) in (None, [], {}, "")]
    noms = [e["nom"] for e in conf["budget"]["etapes"]]
    absentes = [e for e in ETAPES if e not in noms]
    en_trop = [n for n in noms if n not in ETAPES]
    if absentes:
        manques.append("budget.etapes : étapes de la génération absentes du plan : " + ", ".join(absentes))
    if en_trop:
        manques.append("budget.etapes : étapes que la v53 ne joue pas (pré-pilote : rédacteur, rendus, relecteur, antériorité… "
                       "restent hors de la v53) : " + ", ".join(en_trop))
    if noms and [n for n in noms if n in ETAPES] != [e for e in ETAPES if e in noms]:
        manques.append("budget.etapes : ordre différent de l'ordre de la génération " + str(ETAPES))
    roles = {e["nom"]: e["role"] for e in conf["budget"]["etapes"]}
    for e in ("aiguillage", "proposition", "juges"):
        if roles.get(e) not in (None, "protegee"):
            manques.append(f"budget.etapes : {e} doit être protégée (l'aiguilleur n'est jamais sacrifié)")
    ps = conf.get("plafonds_session") or {}
    for r in ("proposeur", "aiguilleur", "juge", "fusion", "lecteur"):
        v = ps.get(r)
        if isinstance(v, bool) or not isinstance(v, (int, float)) or v <= 0:
            manques.append(f"plafonds_session.{r} : réel > 0 exigé (aucun défaut)")
    for p in conf.get("proposeurs") or []:
        if not all(isinstance(p.get(c), str) and p.get(c) for c in ("etiquette", "modele", "fournisseur", "consigne")):
            manques.append("proposeurs : {etiquette, modele, fournisseur, consigne} exigés")
    for c in conf.get("cases") or []:
        if not (isinstance(c, list) and len(c) == 2 and all(isinstance(x, str) and x for x in c)):
            manques.append("cases : [texte, bras] attendu")
    lect = conf.get("lecteurs_etiquettes") or []
    if len(lect) != 2 or len({l.get("etiquette") for l in lect}) != 2:
        manques.append("lecteurs_etiquettes : deux lecteurs isolés, étiquettes distinctes")
    if conf["bisociateur"]["bras"] and conf["bisociateur"]["k_paires"] > 0 and not isinstance(conf["bisociateur"].get("metteur_fusion"), dict):
        manques.append("bisociateur.metteur_fusion : {etiquette, modele, fournisseur} exigé")
    if manques:
        raise ConfigurationRefusee("configuration de génération refusée :\n- " + "\n- ".join(manques))
    return True


def declarer_bras(conf):
    """É0 : chaque bras est produit (paramètres chargés) ou « non produit » avec sa cause (A19, A20) ; écrit au manifeste."""
    b = conf["bisociateur"]
    decl, params = {}, {}
    for bras in b["bras"]:
        try:
            if bras == "meta":
                a = b["meta"]["annexe"]
                params[bras] = bis.lire_annexe_meta(chemin_piece(conf, a["chemin"]), a["sha256"])
                n0, n1 = params[bras]["niches"][:2]
                bis.garde_desaccord_hors_score(bis.score_meta, params[bras], n0, n1, set(), set())  # garde R5 ligne 24, à É0
                decl[bras] = {"produit": True, "annexe_sha256": a["sha256"]}
            elif bras == "gu_krenn":
                g = b["gu_krenn"]
                if g.get("mode") != "substitut":
                    raise bis.BisociationRefusee("A19 : seul le mode « substitut » est branché en v53 (mode déclaré : "
                                                 f"{g.get('mode')!r})")
                params[bras] = bis.SourceGuKrenn(chemin_piece(conf, g["source"]["chemin"]), g["source"]["sha256"],
                                                 oeuvres_min_vocabulaire=g["oeuvres_min_vocabulaire"], date_debut=g["date_debut"],
                                                 date_coupure=g["date_coupure"], actif_depuis=g["actif_depuis"],
                                                 actif_min_oeuvres=g["actif_min_oeuvres"])
                decl[bras] = {"produit": True, "mode": "substitut", "source_sha256": g["source"]["sha256"],
                              "vocabulaire": len(params[bras].vocabulaire)}
            else:
                liste = json.loads(texte_piece(conf, b["basique"]["liste_concepts"]))
                if not isinstance(liste, list) or not liste or not all(isinstance(x, str) for x in liste):
                    raise bis.BisociationRefusee("liste fermée des concepts : liste JSON de chaînes attendue")
                params[bras] = {"liste": liste, "exposant": b["basique"]["exposant"], "decalage": b["basique"]["decalage"]}
                decl[bras] = {"produit": True, "liste_concepts": len(liste)}
        except (bis.BisociationRefusee, OSError, ValueError, KeyError) as e:
            cause = "annexe non conforme" if bras == "meta" else ("source absente" if bras == "gu_krenn" else "liste absente")
            decl[bras] = {"produit": False, "cause": f"non produit ({cause})", "motif": str(e)[:300]}
    return decl, params


class Generation:
    def __init__(self, conf, sortie, adaptateurs, *, numero=1, memoire=None, heritage_texte=None, go=None):
        verifier_configuration_generation(conf)
        if os.path.exists(sortie):
            raise EcrasementInterdit(f"sortie {sortie} déjà présente : jamais écrasée (R12)")
        manquants = sorted(({p["fournisseur"] for p in conf["proposeurs"]} | {j["fournisseur"] for j in conf["juges"]}
                           | {l["fournisseur"] for l in conf["lecteurs_etiquettes"]} | {conf["aiguilleur"]["fournisseur"]}
                           | ({conf["bisociateur"]["metteur_fusion"]["fournisseur"]} if conf["bisociateur"].get("metteur_fusion") else set()))
                           - set(adaptateurs))
        if manquants:
            raise ConfigurationRefusee("adaptateur absent pour : " + ", ".join(manquants))
        os.makedirs(sortie)
        self.conf, self.sortie, self.ad, self.numero = conf, sortie, adaptateurs, numero
        self.graines = Graines(conf["racine_graines"])
        self.coffre = Coffre(os.path.join(sortie, "coffre"))
        self.budget = depuis_configuration(conf)
        self.memoire = memoire or Memoire(methode=conf["memoire"]["methode"], seuil=conf["memoire"]["seuil"],
                                          taille_bardeau=conf["memoire"].get("taille_bardeau"))
        self.heritage = heritage_texte
        self.go = go
        self.ps = conf["plafonds_session"]
        self.interdites = conf["etiquettes_interdites"]
        ai = conf["aiguilleur"]
        self.aiguilleur = Aiguilleur(adaptateurs[ai["fournisseur"]], etiquette=ai["etiquette"], modele=ai["modele"],
                                     consigne_figee=texte_piece(conf, ai["consigne"]), etiquettes_interdites=self.interdites,
                                     plafond_session_usd=self.ps["aiguilleur"], journal_dossier=os.path.join(sortie, "aiguillage"))
        self.garde_kimi = GardeKimi(conf["garde_kimi"]["debordement_max"])
        consignes = {j["consigne"]: texte_piece(conf, j["consigne"]) for j in conf["juges"]}
        self.juges = JugesCroises(adaptateurs, conf["juges"], consignes, items=conf["items_juge"], etiquettes_interdites=self.interdites,
                                  plafond_session_usd=self.ps["juge"], graines=self.graines, coffre=self.coffre,
                                  dossier=os.path.join(sortie, "juges"))
        self.fiches = {}
        self.ordre = []
        self.roles_arretes = {}
        self.evenements = []
        self.lots_juges = set()
        self.bras_decl, self.bras_params = declarer_bras(conf)
        self.paires, self.non_produits = {}, {}
        self.etiquettes = {}
        self.fusions = []
        self.arret = None
        self.etapes_etat = {}

    # --- outils -------------------------------------------------------------------------------------------------------------

    def ev(self, quoi, **champs):
        self.evenements.append(dict({"n": len(self.evenements) + 1, "evenement": quoi}, **champs))

    def tache(self, *morceaux):
        return f"g{self.numero}-" + "-".join(str(m) for m in morceaux)

    def _plafond(self, role, reste):
        return min(float(self.ps[role]), reste)

    def _appel(self, etape, role_kit, fournisseur, modele, consigne, dossier, plafond, etat):
        os.makedirs(dossier, exist_ok=True)
        r = self.ad[fournisseur].lancer(role_kit, consigne, dossier, plafond, 1, modele=modele)
        etat["cout"] += float(r.cout_declare_usd)
        self.coffre.noter_consommation(etape, role_kit, r.cout_declare_usd, fournisseur=fournisseur, modele_demande=modele,
                                       modele_servi=r.modele_servi, statut=r.statut)
        return r

    def _reste(self, etat):
        return etat["reste"] - etat["cout"]

    def jouer_etape(self, nom, fonction):
        decision, detail = self.budget.avant_etape(nom)
        self.ev("etape", etape=nom, decision=decision, **{k: v for k, v in detail.items() if k != "motif"})
        if decision != JOUER:
            self.etapes_etat[nom] = decision
            return decision
        etat = {"cout": 0.0, "reste": detail["reste_avant_plafond_usd"]}
        try:
            fonction(etat)
        finally:
            self.etapes_etat[nom] = self.budget.apres_etape(nom, etat["cout"])
        return self.etapes_etat[nom]

    # --- proposeurs ---------------------------------------------------------------------------------------------------------

    def _proposer(self, etat, passe, supplement_par_case=None):
        nouvelles = []
        for ic, case in enumerate(self.conf["cases"]):
            for p in self.conf["proposeurs"]:
                if p["etiquette"] in self.roles_arretes or self._reste(etat) <= 0:
                    continue
                consigne = texte_piece(self.conf, p["consigne"] if passe == 1 else self.conf["tableau"]["consigne_passe"])
                consigne = consigne.rstrip() + f"\n\n## Case\nTexte : {case[0]} ; bras : {case[1]}\n"
                if passe == 1 and self.heritage:
                    consigne += "\n## Fiches de la génération précédente (titres, résumés, verdict agrégé)\n" + self.heritage + "\n"
                if supplement_par_case is not None:
                    consigne += "\n## Tableau minimal de ta case (titres et résumés seulement)\n```json\n" + supplement_par_case[ic] + "\n```\n"
                r = self._appel("proposition" if passe == 1 else "passe_tableau", "proposeur_ideation", p["fournisseur"], p["modele"],
                                consigne, os.path.join(self.sortie, "sessions", f"passe{passe}", f"case{ic}", p["etiquette"]),
                                self._plafond("proposeur", self._reste(etat)), etat)
                if r.statut != "ok":
                    self.ev("proposeur-sans-sortie", etiquette=p["etiquette"], passe=passe, case=ic, statut=r.statut)
                    continue
                try:
                    brutes = fiches_du_texte(r.texte_brut or r.texte_final)
                except FicheRefusee as e:
                    self.ev("proposeur-illisible", etiquette=p["etiquette"], passe=passe, case=ic, motif=str(e)[:200])
                    continue
                for k, b in enumerate(brutes):
                    ident = "f" + self.graines.jeton_opaque(self.tache("ident", passe, ic, p["etiquette"], k), 6)
                    try:
                        f = preparer(b, self.conf["champs_fiche"], ident=ident, case=case, fournisseur=p["fournisseur"], passe=passe)
                    except FicheRefusee as e:
                        self.ev("fiche-refusee", etiquette=p["etiquette"], passe=passe, case=ic, motif=str(e)[:200])
                        continue
                    f["meta"]["proposeur"] = p["etiquette"]
                    self.fiches[ident] = f
                    self.ordre.append(ident)
                    nouvelles.append(f)
        return nouvelles

    def _aiguiller(self, fiches, etat):
        for f in fiches:
            if self._reste(etat) <= 0:
                self.ev("aiguillage-coupe", ident=f["ident"])
                continue
            classe, cout = self.aiguilleur.classer(f, plafond=self._plafond("aiguilleur", self._reste(etat)),
                                                   dossier_appel=os.path.join(self.sortie, "aiguillage", "appels", f["ident"]))
            etat["cout"] += cout
            self.coffre.noter_consommation("aiguillage", "aiguilleur", cout)
            if f["meta"]["fournisseur"] == "kimi" and f["meta"]["origine"] == "proposition":
                self.garde_kimi.noter(f, classe)
        kimi = [p["etiquette"] for p in self.conf["proposeurs"] if p["fournisseur"] == "kimi"]
        mf = self.conf["bisociateur"].get("metteur_fusion") or {}
        if mf.get("fournisseur") == "kimi":
            kimi.append(mf["etiquette"])  # choix de code v53 : Kimi auteur arrêté aussi comme metteur en fusion
        try:
            self.garde_kimi.verifier()
        except DebordementKimi as e:
            for k in kimi:
                self.roles_arretes[k] = str(e)
            self.ev("arret-role-kimi", motif=str(e), noeud=True)

    def _juger(self, fiches, lot, etat):
        self.lots_juges.add(lot)
        for f in fiches:
            if not self.aiguilleur.a_passeport(f):
                continue
            if self._reste(etat) <= 0:
                self.ev("juges-coupes", ident=f["ident"], lot=lot)
                continue
            etat["cout"] += self.juges.juger(f, self.aiguilleur, lot, plafond_restant=self._reste(etat))

    # --- étapes -------------------------------------------------------------------------------------------------------------

    def etape_proposition(self, etat):
        self.passe1 = self._proposer(etat, 1)

    def etape_aiguillage(self, etat):
        self._aiguiller(self.passe1, etat)

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
        self._aiguiller(self.passe2, etat)
        self._juger(self.passe2, "passe2", etat)

    def _lire_etiquettes(self, etat, f, lecteur, nature, liste):
        consigne = texte_piece(self.conf, self.conf["bisociateur"]["consigne_lecteur_etiquettes"]).rstrip()
        consigne += f"\n\n## Lecture : {nature}\n## Liste fermée\n```json\n{json.dumps(liste, ensure_ascii=False)}\n```\n"
        corps = json.dumps(vue_servie(f), ensure_ascii=False, indent=1)
        garde_etiquettes(corps, self.interdites)
        consigne += "\n## La fiche\n```json\n" + corps + "\n```\n"
        self.aiguilleur.exiger_passeport(f, "un lecteur d'étiquettes")
        r = self._appel("etiquettes", "juge_ideation", lecteur["fournisseur"], lecteur["modele"], consigne,
                        os.path.join(self.sortie, "etiquettes", lecteur["etiquette"], nature, f["ident"]),
                        self._plafond("lecteur", self._reste(etat)), etat)
        if r.statut != "ok":
            return None
        return extraire_bloc_json(r.texte_brut or r.texte_final, "niche" if nature == "niches" else "etiquettes")

    def etape_etiquettes(self, etat):
        eligibles = [f for f in self.passe1 if self.aiguilleur.a_passeport(f)]
        produits = [b for b, d in self.bras_decl.items() if d["produit"]]
        natures = {"basique": ("concepts", lambda: self.bras_params["basique"]["liste"]),
                   "gu_krenn": ("vocabulaire_gk", lambda: self.bras_params["gu_krenn"].vocabulaire),
                   "meta": ("niches", lambda: {"niches": self.bras_params["meta"]["niches"],
                                               "types_structure": self.bras_params["meta"]["types_structure"]})}
        for bras in produits:
            nature, liste = natures[bras]
            lectures = {}
            for lecteur in self.conf["lecteurs_etiquettes"]:
                lectures[lecteur["etiquette"]] = {}
                for f in eligibles:
                    if self._reste(etat) <= 0:
                        break
                    bloc = self._lire_etiquettes(etat, f, lecteur, nature, liste())
                    try:
                        if nature == "niches":
                            lectures[lecteur["etiquette"]][f["ident"]] = bis.valider_niche(
                                bloc or {}, self.bras_params["meta"]["niches"], self.bras_params["meta"]["types_structure"])
                        else:
                            lectures[lecteur["etiquette"]][f["ident"]] = bis.valider_etiquettes((bloc or {}).get("etiquettes", []), liste())
                    except bis.BisociationRefusee as e:
                        self.ev("etiquette-rejetee", bras=bras, lecteur=lecteur["etiquette"], ident=f["ident"], motif=str(e)[:200])
            self.etiquettes[bras] = lectures

    def _notes(self, eligibles):
        """Notes de chaque bras produit sur toutes les paires de même case (programme, 0 USD)."""
        axe_de = lambda f: f["contenu"].get(self.conf["champ_axe"])  # noqa: E731
        notes, departage = {}, {}
        par_case = {}
        for f in eligibles:
            par_case.setdefault(tuple(f["meta"]["case"]), []).append(f)
        for bras, lectures in self.etiquettes.items():
            l1, l2 = (lectures[l["etiquette"]] for l in self.conf["lecteurs_etiquettes"])
            notes[bras], departage[bras] = {}, {}
            rng = self.graines.generateur(self.tache("bisoc", bras))
            for groupe in par_case.values():
                for i, fa in enumerate(groupe):
                    for fb in groupe[i + 1:]:
                        p = bis.cle_paire(fa["ident"], fb["ident"])
                        if bras == "basique":
                            concepts = {x: set(l1.get(x, [])) | set(l2.get(x, [])) for x in p}
                            prm = self.bras_params["basique"]
                            notes[bras][p] = (bis.score_basique(fa, fb, concepts, axe_de, prm["exposant"], prm["decalage"]), None)
                        elif bras == "gu_krenn":
                            ca = sorted(set(l1.get(fa["ident"], [])) | set(l2.get(fa["ident"], [])))
                            cb = sorted(set(l1.get(fb["ident"], [])) | set(l2.get(fb["ident"], [])))
                            n = self.bras_params["gu_krenn"].note(ca, cb)
                            if n is not None:
                                notes[bras][p] = (n, None)
                        else:
                            la, lb = l1.get(fa["ident"]), l1.get(fb["ident"])
                            ma, mb = l2.get(fa["ident"]), l2.get(fb["ident"])
                            if not (la and lb and ma and mb) or la[0] != ma[0] or lb[0] != mb[0] or la[0] == lb[0]:
                                continue  # niche indécise (lecteurs en désaccord) ou même niche : hors du bras méta
                            prm = self.bras_params["meta"]
                            sa, sb = la[1] | ma[1], lb[1] | mb[1]
                            s = bis.score_meta(prm, la[0], lb[0], sa, sb)
                            notes[bras][p] = ((1, s) if s > 0 else (0,) + bis.score_repli(prm, la[0], lb[0], sa, sb), "profil" if s > 0 else "hors profil")
            for p in notes[bras]:
                departage[bras][p] = float(rng.random())
        return notes, departage

    def etape_fusions(self, etat):
        eligibles = [f for f in self.passe1 if self.aiguilleur.a_passeport(f)]
        ordre = [b for b in self.conf["bisociateur"]["bras"] if self.bras_decl[b]["produit"]]
        ordre = [ordre[i] for i in self.graines.permutation(self.tache("bisoc-ordre"), len(ordre))]
        notes, departage = self._notes(eligibles)
        self.paires, np_ = bis.choisir_paires(eligibles, notes, ordre, self.conf["bisociateur"]["k_paires"], self.aiguilleur, departage)
        self.non_produits.update(np_)
        self.profil = {b: {"|".join(p): notes[b][p][1] for p in ps} for b, ps in self.paires.items() if b == "meta"}
        a_ecrire = [(b, p) for b in ordre for p in self.paires.get(b, [])]
        a_ecrire = [a_ecrire[i] for i in self.graines.permutation(self.tache("bisoc-ordre-fusion"), len(a_ecrire))]
        mf = self.conf["bisociateur"]["metteur_fusion"]
        if mf.get("etiquette") in self.roles_arretes:
            self.ev("fusions-non-produites", motif="rôle du metteur en fusion arrêté")
            return
        cle_bras = {}
        consigne_fusion = texte_piece(self.conf, self.conf["bisociateur"]["consigne_fusion"])
        nouvelles = []
        for n, (bras, (ia, ib)) in enumerate(a_ecrire):
            if self._reste(etat) <= 0:
                self.ev("fusion-coupee", rang=n)
                continue
            entree = bis.entree_fusion(consigne_fusion, self.fiches[ia], self.fiches[ib], self.interdites)
            r = self._appel("fusions", "proposeur_ideation", mf["fournisseur"], mf["modele"], entree,
                            os.path.join(self.sortie, "sessions", "fusions", f"fusion{n}"), self._plafond("fusion", self._reste(etat)), etat)
            if r.statut != "ok":
                self.ev("fusion-sans-sortie", rang=n, statut=r.statut)
                continue
            try:
                brutes = fiches_du_texte(r.texte_brut or r.texte_final)
                if len(brutes) != 1:
                    raise FicheRefusee("une fusion = une fiche")
                ident = "f" + self.graines.jeton_opaque(self.tache("ident-fusion", n), 6)
                f = preparer(brutes[0], self.conf["champs_fiche"], ident=ident, case=self.fiches[ia]["meta"]["case"],
                             fournisseur=mf["fournisseur"], passe="fusion", origine="fusion")
            except FicheRefusee as e:
                self.ev("fusion-refusee", rang=n, motif=str(e)[:200])
                continue
            f["meta"]["exploratoire"] = True
            self.fiches[ident] = f
            self.ordre.append(ident)
            nouvelles.append(f)
            cle_bras[ident] = {"bras": bras, "paire": [ia, ib]}
        self.coffre.deposer(self.tache("cle-bras"), cle_bras)
        self.fusions = nouvelles
        self._aiguiller(nouvelles, etat)
        self._juger(nouvelles, "fusions", etat)

    # --- la génération ------------------------------------------------------------------------------------------------------

    def executer(self):
        depart = {"version": VERSION, "generation": self.numero, "configuration_sha256": self.conf["empreinte_configuration"],
                  "go": self.go, "bras": self.bras_decl, "etapes": list(ETAPES),
                  "adaptateurs": {k: (a.description() if hasattr(a, "description") else type(a).__name__) for k, a in self.ad.items()},
                  "regle_de_lecture": "aucun verdict ni clé lu avant la fin de la phase de mesure (A21) ; seules les consommations",
                  "manifeste_r9": manifeste_r9(self.graines)}
        ecrire_json_scelle(os.path.join(self.sortie, "manifeste-depart.json"), depart)
        self.passe1, self.passe2 = [], []
        resultat = None
        try:
            for nom in ETAPES:
                self.jouer_etape(nom, getattr(self, "etape_" + nom))
            lot = [self.fiches[i] for i in self.ordre if self.aiguilleur.a_passeport(self.fiches[i])]
            redites = self.memoire.detecter(lot)
            ecrire_json_scelle(os.path.join(self.sortie, "memoire.json"), redites)
            for lot_j in sorted(self.lots_juges):
                self.juges.deposer_cles(lot_j)
            self.coffre.declarer_fin_e9()
            verdicts = {}
            for lot_j in sorted(self.lots_juges):
                for f in lot:
                    nom = f"verdicts-{lot_j}-{f['ident']}"
                    if os.path.exists(os.path.join(self.coffre.dossier, nom + ".json")):
                        verdicts[f["ident"]] = self.coffre.ouvrir(nom)["verdicts"]
            ag = self.conf["agregation"]
            resultat = classement(verdicts, ag["regle"], ag.get("q"))
            ecrire_json_scelle(os.path.join(self.sortie, "classement.json"), {
                "lignes": [{k: l[k] for k in ("ident", "rang", "notable", "n_notables", "n_presents", "somme_x")}
                           | {"exploratoire": bool(self.fiches[l["ident"]]["meta"].get("exploratoire"))} for l in resultat],
                "regle_agregation": ag, "fusions_comptees_a_part": [f["ident"] for f in self.fusions]})
            ecrire_json_scelle(os.path.join(self.sortie, "fiches.json"),
                               {i: {"contenu": self.fiches[i]["contenu"], "empreinte": self.fiches[i]["empreinte"],
                                    "meta": self.fiches[i]["meta"]} for i in self.ordre if self.aiguilleur.a_passeport(self.fiches[i])})
            self.memoire.ajouter_memoire(lot, self.numero)
        except Exception as e:
            self.arret = f"{type(e).__name__} : {str(e)[:500]}"
            raise
        finally:
            self.aiguilleur.sceller_journal()
            fin = {"version": VERSION, "generation": self.numero, "arret": self.arret, "evenements": self.evenements,
                   "etapes": self.etapes_etat, "budget": self.budget.etat(), "graines": self.graines.manifeste(),
                   "coffre": self.coffre.journal(), "garde_kimi": self.garde_kimi.etat(), "roles_arretes": self.roles_arretes,
                   "bras": self.bras_decl, "non_produits": self.non_produits,
                   "paires": {b: ["|".join(p) for p in ps] for b, ps in self.paires.items()},
                   "profil_meta": getattr(self, "profil", {}),
                   "desaccord_des_paires": "non lu en v53 (lecture par paire à brancher) ; n'entre jamais dans le score (R-638)",
                   "fusions": {"comptees_a_part": len(self.fusions), "etiquette": "exploratoire (registre seulement)"},
                   "juges_absents": self.juges.absents, "modele_servi_juges": self.juges.modele_servi}
            ecrire_json_scelle(os.path.join(self.sortie, "manifeste-fin.json"), fin)
            with open(os.path.join(self.sortie, "empreintes-sortie.txt"), "w", encoding="utf-8") as g:
                for rel in lister_fichiers(self.sortie):
                    if rel != "empreintes-sortie.txt" and not rel.endswith(".sha256"):
                        g.write(f"{sha256_fichier(os.path.join(self.sortie, rel))}  {rel}\n")
        return resultat

    def texte_heritage(self, resultat):
        """Titres, résumés d'une ligne et verdict agrégé des fiches de cette génération, pour la passe 1 de la suivante."""
        t = self.conf["tableau"]
        from .tableau_v53 import une_ligne
        return json.dumps([{"titre": une_ligne(self.fiches[l["ident"]]["contenu"].get(self.conf["champ_titre"], ""), t["longueur_max_titre"]),
                            "resume": une_ligne(self.fiches[l["ident"]]["contenu"].get(t["champ_resume"], ""), t["longueur_max_resume"]),
                            "notable": l["notable"]} for l in resultat], ensure_ascii=False, indent=1)


# --- la course : générations successives, étage de tests de mort entre deux générations ------------------------------------


def plafond_course(conf, nombre_generations, etage=None):
    """Somme des plafonds que la ligne de GO doit couvrir (A15) : S17 par génération (choix de code v53 : le plan et son
    plafond s'appliquent à chaque génération) + le plafond de l'étage entre deux générations."""
    total = nombre_generations * float(conf["budget"]["plafond_usd"])
    if etage is not None and nombre_generations > 1:
        total += (nombre_generations - 1) * float(etage["plafond_etage_usd"])
    return total


def executer_course(conf, sortie, adaptateurs, *, nombre_generations, go, etage=None, environnement=None):
    """`etage` : None (étage non joué) ou {adaptateur, reglages (arguments de `executer_tests_de_mort`, plafonds compris),
    nombre, tranche_index_sha256, correspondance, plafond_etage_usd, executer (essais)}. L'étage est joué **entre** deux
    générations (après chaque génération sauf la dernière), sur les fiches les mieux classées ; la machine jetable est
    vérifiée **avant la première génération** (aucune dépense si elle manque)."""
    from .etage_entre_generations_v53 import exiger_machine_jetable, jouer_etage, preparer_generation
    if isinstance(nombre_generations, bool) or not isinstance(nombre_generations, int) or nombre_generations < 1:
        raise ConfigurationRefusee("nombre de générations : entier ≥ 1, aucun défaut")
    if etage is not None:
        exiger_machine_jetable(environnement)
        for c in ("adaptateur", "reglages", "nombre", "tranche_index_sha256", "correspondance", "plafond_etage_usd"):
            if c not in etage:
                raise ConfigurationRefusee(f"étage entre générations : {c} manquant (aucun défaut)")
    if os.path.exists(sortie):
        raise EcrasementInterdit(f"sortie {sortie} déjà présente (R12)")
    os.makedirs(sortie)
    memoire, heritage, bilan = None, None, []
    for g in range(1, nombre_generations + 1):
        gen = Generation(conf, os.path.join(sortie, f"generation-{g}"), adaptateurs, numero=g, memoire=memoire,
                         heritage_texte=heritage, go=go)
        resultat = gen.executer()
        memoire, heritage = gen.memoire, gen.texte_heritage(resultat)
        ligne = {"generation": g, "fiches_classees": len(resultat), "notables": sum(l["notable"] for l in resultat)}
        if etage is not None and g < nombre_generations:
            d = preparer_generation(os.path.join(sortie, f"etage-apres-generation-{g}"), resultat, gen.fiches,
                                    nombre=etage["nombre"], tranche_index_sha256=etage["tranche_index_sha256"],
                                    correspondance=etage["correspondance"], lisible=gen.arret is None)
            ligne["etage"] = jouer_etage(etage["adaptateur"], d, reglages=etage["reglages"], environnement=environnement,
                                         executer=etage.get("executer"))
        bilan.append(ligne)
    ecrire_json_scelle(os.path.join(sortie, "bilan-course.json"), {"version": VERSION, "go": go, "generations": bilan})
    return bilan
