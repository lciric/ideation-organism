"""Mémoire anti-redite et doublons (M3 ; v53) : détection **intra-lot** et **inter-fournisseurs**, et contre les fiches des
générations précédentes. Paramètres injectés : méthode, taille des bardeaux, seuil t* (aucun défaut).

Méthode `bardeaux` : similarité de Jaccard des ensembles de n-grammes de mots (texte normalisé : minuscules, accents
retirés) de la fiche entière (tous ses champs, clés triées). Méthode `plongement` : le plongement figé du préenregistrement
(« nommé au scellement ») n'existe pas encore ; la v53 l'accepte seulement si une fonction de similarité est **injectée**
avec son nom et son empreinte (sinon refus : aucun repli silencieux sur les bardeaux).

Pour chaque paire au-dessus de t* : `intra_lot` (même lot), `inter_fournisseurs` (fournisseurs différents),
`contre_memoire` (fiche d'une génération précédente) ; la fiche **la plus récente** de la paire (ordre d'arrivée) est
marquée « redite ». Les redites restent jugées (choix de code v53 : la mémoire compte, elle ne filtre pas) ; le compte
d'idées distinctes et les paires sont écrits au manifeste.
"""

import itertools
import json

from .outils import normaliser_texte

VERSION = "memoire-anti-redite-v53"


class MemoireRefusee(ValueError):
    pass


def texte_fiche(fiche):
    return normaliser_texte(json.dumps(fiche["contenu"], ensure_ascii=False, sort_keys=True))


def bardeaux(texte, n):
    mots = texte.split()
    if len(mots) < n:
        return {tuple(mots)} if mots else set()
    return {tuple(mots[i:i + n]) for i in range(len(mots) - n + 1)}


def jaccard(a, b):
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


class Memoire:
    def __init__(self, *, methode, seuil, taille_bardeau=None, similarite=None, nom_similarite=None):
        if methode not in ("bardeaux", "plongement"):
            raise MemoireRefusee(f"méthode de la mémoire inconnue : {methode!r}")
        if isinstance(seuil, bool) or not isinstance(seuil, (int, float)) or not 0 <= seuil <= 1:
            raise MemoireRefusee("seuil t* : réel de 0 à 1 exigé, aucun défaut")
        if methode == "bardeaux" and (isinstance(taille_bardeau, bool) or not isinstance(taille_bardeau, int) or taille_bardeau < 1):
            raise MemoireRefusee("taille des bardeaux : entier ≥ 1 exigé, aucun défaut")
        if methode == "plongement" and (not callable(similarite) or not nom_similarite):
            raise MemoireRefusee("méthode « plongement » : fonction de similarité injectée et nommée exigée (plongement figé non "
                                 "fourni : aucun repli sur les bardeaux)")
        self.methode, self.seuil, self.n = methode, float(seuil), taille_bardeau
        self.similarite, self.nom_similarite = similarite, nom_similarite
        self.anciennes = []  # (fiche, génération)

    def sim(self, a, b):
        if self.methode == "bardeaux":
            return jaccard(bardeaux(texte_fiche(a), self.n), bardeaux(texte_fiche(b), self.n))
        return float(self.similarite(a["contenu"], b["contenu"]))

    def ajouter_memoire(self, fiches, generation):
        self.anciennes += [(f, generation) for f in fiches]

    def detecter(self, lot):
        """`lot` : fiches dans l'ordre d'arrivée. Rend {paires, redites, idees_distinctes}."""
        paires, redites = [], set()
        for (i, a), (j, b) in itertools.combinations(enumerate(lot), 2):
            s = self.sim(a, b)
            if s + 1e-12 >= self.seuil:
                paires.append({"a": a["ident"], "b": b["ident"], "similarite": round(s, 6), "intra_lot": True,
                               "inter_fournisseurs": a["meta"]["fournisseur"] != b["meta"]["fournisseur"], "contre_memoire": False})
                redites.add(b["ident"])
        for b in lot:
            for a, g in self.anciennes:
                s = self.sim(a, b)
                if s + 1e-12 >= self.seuil:
                    paires.append({"a": a["ident"], "b": b["ident"], "similarite": round(s, 6), "intra_lot": False,
                                   "inter_fournisseurs": a["meta"]["fournisseur"] != b["meta"]["fournisseur"],
                                   "contre_memoire": True, "generation_a": g})
                    redites.add(b["ident"])
        return {"version": VERSION, "methode": self.methode if self.methode == "bardeaux" else self.nom_similarite,
                "seuil": self.seuil, "taille_bardeau": self.n, "paires": paires, "redites": sorted(redites),
                "idees_distinctes": len(lot) - len(redites), "taille_lot": len(lot)}
