"""Notation croisée des juges (v53 ; R-577, R-578, R-634 ; brouillon 6, Métrique, M1).

Chaque fiche (munie d'un passeport de l'aiguilleur) est jugée par **chacun** des juges de la configuration (Kimi, Argon,
Opus 5.5 troisième juge), **un appel par fiche et par juge**, session neuve, consigne figée du juge (pièce empreintée) + la
seule fiche, sous un identifiant opaque propre au juge : **aucun juge ne voit les notes des autres** (rien d'autre n'est
servi). Réponse attendue (contrat écrit dans la consigne figée) : un bloc JSON `{"items": {K1: vrai|faux, …}, "note": …}`
avec exactement les items injectés (`items_juge`, k lu sur la consigne figée).

Pour chaque fiche et chaque juge : verdict de chaque item, **X** = part des items vrais (un point = 0,01), « notable » = tous
les items vrais ; une note graduée éventuelle est gardée, en descriptif. Les verdicts sont **déposés au coffre** (A21) :
l'orchestrateur ne les lit qu'après la fin de la phase de mesure.

**Agrégation définie par configuration** (`agregation.regle`, aucune règle par défaut) : `au_moins` (notable chez au moins
`q` juges), `unanimite`, `majorite_stricte` (plus de la moitié des juges qui ont rendu un verdict lisible). Une réponse
illisible ou un refus d'un juge : verdict « absent » (jamais « notable »), compté ; la règle se lit sur les juges présents
pour `majorite_stricte`, sur le nombre de juges notables pour `au_moins` et `unanimite` (un absent fait tomber l'unanimité).

A2 (version du modèle servi) : le premier modèle servi lu pour un juge est gardé ; un modèle servi différent ensuite (par
exemple entre les fiches de la passe 1 et les fusions) est un arrêt du rôle (`VersionServieChangee`).

Étalonnage sur témoins (M1, pré-pilote) : `etalonner_juges` calcule par juge rappel P, spécificité N, exactitude équilibrée,
et l'accord (kappa de Fleiss des verdicts « notable », kappa de Cohen par couple), puis les compare aux seuils injectés S1 à
S4 (aucun défaut).
"""

import itertools
import os

from .fiches_v53 import entree_une_fiche
from .outils import extraire_bloc_json

VERSION = "juges-croises-v53"


class VersionServieChangee(RuntimeError):
    """A2 : arrêt du rôle ; aucune bascule sans mot de Lazar."""


def lire_verdict(texte, items):
    bloc = extraire_bloc_json(texte, "items")
    if not bloc or not isinstance(bloc.get("items"), dict) or set(bloc["items"]) != set(items):
        return None
    if not all(isinstance(bloc["items"][k], bool) for k in items):
        return None
    note = bloc.get("note")
    vrais = sum(bloc["items"][k] for k in items)
    return {"items": {k: bloc["items"][k] for k in items}, "x": round(vrais / len(items), 6),
            "notable": vrais == len(items), "note": note if isinstance(note, (int, float, str)) and not isinstance(note, bool) else None}


def agreger(verdicts_par_juge, regle, q=None):
    """`verdicts_par_juge` : {juge: verdict ou None}. Rend {notable, n_notables, n_presents, regle}."""
    presents = {j: v for j, v in verdicts_par_juge.items() if v is not None}
    n_not = sum(1 for v in presents.values() if v["notable"])
    if regle == "au_moins":
        if isinstance(q, bool) or not isinstance(q, int) or not 1 <= q <= len(verdicts_par_juge):
            raise ValueError("règle « au_moins » : q entier de 1 au nombre de juges")
        notable = n_not >= q
    elif regle == "unanimite":
        notable = n_not == len(verdicts_par_juge) and len(verdicts_par_juge) > 0
    elif regle == "majorite_stricte":
        notable = len(presents) > 0 and n_not * 2 > len(presents)
    else:
        raise ValueError(f"règle d'agrégation inconnue : {regle!r} (aucune règle par défaut)")
    return {"notable": notable, "n_notables": n_not, "n_presents": len(presents), "n_juges": len(verdicts_par_juge),
            "regle": regle, "q": q, "somme_x": round(sum(v["x"] for v in presents.values()), 6)}


class JugesCroises:
    def __init__(self, adaptateurs, juges, consignes, *, items, etiquettes_interdites, plafond_session_usd, graines, coffre,
                 dossier):
        """`adaptateurs` : {fournisseur: Adaptateur} ; `juges` : [{etiquette, modele, fournisseur, consigne}] ;
        `consignes` : {nom de pièce: texte vérifié}."""
        self.adaptateurs, self.juges, self.consignes = adaptateurs, juges, consignes
        self.items = list(items)
        self.interdites = list(etiquettes_interdites)
        self.plafond = float(plafond_session_usd)
        self.graines, self.coffre, self.dossier = graines, coffre, dossier
        self.modele_servi = {}
        self.absents = {j["etiquette"]: 0 for j in juges}
        self.cles = {}  # ident servi par juge -> ident de la fiche : déposées au coffre

    def juger(self, fiche, aiguilleur, lot, plafond_restant=None):
        """Juge une fiche chez tous les juges ; dépose les verdicts au coffre ; rend le coût total (rien d'un verdict)."""
        aiguilleur.exiger_passeport(fiche, "un juge")
        cout = 0.0
        verdicts = {}
        for j in self.juges:
            if plafond_restant is not None and plafond_restant - cout <= 0:
                verdicts[j["etiquette"]] = None
                self.absents[j["etiquette"]] += 1
                continue
            ident_servi = "F" + self.graines.jeton_opaque(f"anonymisation-{j['etiquette']}-{fiche['ident']}", 5)
            self.cles.setdefault(j["etiquette"], {})[ident_servi] = fiche["ident"]
            consigne = entree_une_fiche(self.consignes[j["consigne"]], fiche, self.interdites, identifiant_servi=ident_servi)
            plafond = self.plafond if plafond_restant is None else min(self.plafond, plafond_restant - cout)
            d = os.path.join(self.dossier, lot, j["etiquette"], fiche["ident"])
            os.makedirs(d, exist_ok=True)
            r = self.adaptateurs[j["fournisseur"]].lancer("juge_ideation", consigne, d, plafond, 1, modele=j["modele"])
            cout += float(r.cout_declare_usd)
            if r.statut == "ok" and r.modele_servi:
                vu = self.modele_servi.setdefault(j["etiquette"], r.modele_servi)
                if vu != r.modele_servi:
                    raise VersionServieChangee(f"A2 : juge {j['etiquette']} servi par {r.modele_servi!r} après {vu!r} : arrêt du rôle")
            v = lire_verdict(r.texte_brut or r.texte_final, self.items) if r.statut == "ok" else None
            if v is None:
                self.absents[j["etiquette"]] += 1
            verdicts[j["etiquette"]] = v
        self.coffre.deposer(f"verdicts-{lot}-{fiche['ident']}", {"ident": fiche["ident"], "empreinte": fiche["empreinte"],
                                                                 "verdicts": verdicts})
        return cout

    def deposer_cles(self, lot):
        return self.coffre.deposer(f"cles-anonymisation-{lot}", self.cles)


def classement(verdicts_par_fiche, regle, q=None):
    """Après la fin de la phase de mesure seulement. `verdicts_par_fiche` : {ident: {juge: verdict}}. Ordre : notable
    agrégé, nombre de juges notables, somme des X (jamais une moyenne de jetons), puis identifiant (déterministe)."""
    lignes = []
    for ident, par_juge in verdicts_par_fiche.items():
        a = agreger(par_juge, regle, q)
        lignes.append(dict(a, ident=ident, par_juge=par_juge))
    lignes.sort(key=lambda l: (not l["notable"], -l["n_notables"], -l["somme_x"], l["ident"]))
    for rang, l in enumerate(lignes, 1):
        l["rang"] = rang
    return lignes


# --- étalonnage (M1) -------------------------------------------------------------------------------------------------------


def kappa_cohen(a, b):
    n = len(a)
    if n == 0 or len(b) != n:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def kappa_fleiss(table):
    """`table` : liste par témoin de verdicts booléens (un par juge, mêmes juges partout)."""
    if not table:
        return None
    n_j = len(table[0])
    if n_j < 2 or any(len(t) != n_j for t in table):
        return None
    N = len(table)
    p1 = sum(sum(t) for t in table) / (N * n_j)
    pe = p1 ** 2 + (1 - p1) ** 2
    pbar = sum((sum(t) * (sum(t) - 1) + (n_j - sum(t)) * (n_j - sum(t) - 1)) / (n_j * (n_j - 1)) for t in table) / N
    return 1.0 if pe == 1 else (pbar - pe) / (1 - pe)


def etalonner_juges(notables, attendus, *, exactitude_min, rappel_min, plancher_echec, fleiss_min, cohen_min, accord_plancher):
    """M1 : `notables` {juge: {ident: bool}} ; `attendus` {ident: "P" | "N"} (témoins primaires). Seuils injectés S1 à S4."""
    seuils = {"exactitude_min": exactitude_min, "rappel_min": rappel_min, "plancher_echec": plancher_echec,
              "fleiss_min": fleiss_min, "cohen_min": cohen_min, "accord_plancher": accord_plancher}
    for nom, v in seuils.items():
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not -1 <= v <= 1:
            raise ValueError(f"{nom} : seuil injecté exigé, aucun défaut")
    ids = sorted(attendus)
    P = [i for i in ids if attendus[i] == "P"]
    N = [i for i in ids if attendus[i] == "N"]
    par_juge = {}
    for j, v in notables.items():
        rappel = sum(v[i] for i in P) / len(P) if P else None
        spec = sum(not v[i] for i in N) / len(N) if N else None
        ee = (rappel + spec) / 2 if rappel is not None and spec is not None else None
        par_juge[j] = {"rappel_P": rappel, "specificite_N": spec, "exactitude_equilibree": ee,
                       "defaillant": ee is not None and ee < plancher_echec,
                       "etalonne": ee is not None and ee + 1e-12 >= exactitude_min and rappel + 1e-12 >= rappel_min}
    juges = sorted(notables)
    table = [[notables[j][i] for j in juges] for i in ids]
    fleiss = kappa_fleiss(table)
    cohen = {f"{a}|{b}": kappa_cohen([notables[a][i] for i in ids], [notables[b][i] for i in ids])
             for a, b in itertools.combinations(juges, 2)}
    accord_ok = fleiss is not None and fleiss + 1e-12 >= fleiss_min and all(c is not None and c + 1e-12 >= cohen_min for c in cohen.values())
    accord_echec = fleiss is not None and fleiss < accord_plancher
    return {"par_juge": par_juge, "fleiss": fleiss, "cohen": cohen, "accord_satisfait": accord_ok, "accord_en_echec": accord_echec,
            "porte_juges": all(p["etalonne"] for p in par_juge.values()) and accord_ok, "seuils": seuils}
