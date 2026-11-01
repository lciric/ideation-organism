"""Monde sur banque (version 0.7.0, pièce 1 de v7) : les instances sont les lignes d'une **banque figée** (traits visibles,
issues cachées, un moniteur par colonne d'issues), tenue par le noyau hors des dossiers d'agents.

- Le **réservoir** d'une fiche = les instances de la partie d'épreuve qui portent une issue pour le moniteur de la
  fiche (`espace_instances["moniteur"]`), traits seulement (`z`, `g`) ; le plan y est choisi par divergence (comme avant).
- Les **mesures** sont lues (jamais calculées) : pour chaque instance du plan, l'issue du moniteur ; sous l'ordre secret,
  l'empreinte d'ordre est celle que le noyau recalcule (`selection_pari.ordre_execution`).
- Le **nul informé** (pièce 2) : un membre « connu:<moniteur> », loi softmax ajustée par le noyau sur la **partie de
  calibrage** de la banque (régression multinomiale à crête, numpy), ajoutée à la bibliothèque de la fiche avant le
  gel ; une fiche qui ne fait que redire ce prédicteur ne bat pas son nul.
- Les instances de calibrage ne sont jamais servies à une fiche ; une issue absente pour le moniteur demandé exclut
  l'instance (jamais imputée) ; un moniteur inconnu est refusé.

Même interface que `monde_noyau.MondeNoyau` pour le cycle : `mesures(enonce, gele, graine_noyau, numero_generation)`,
plus `reservoir(fiche)` et `membres_informes(fiche)`.
"""

import json
import os
import math

from . import selection_pari as sp
from .outils import empreinte_objet, graine_derivee, sha256_fichier


class BanqueInvalide(ValueError):
    pass


class MondeBanque:
    nom = "monde-banque"

    def __init__(self, chemin, graine, nul_informe=True, crete=1.0, tranches=1):
        with open(chemin, encoding="utf-8") as f:
            self.banque = json.load(f)
        self.empreinte_banque = sha256_fichier(chemin)
        self.chemin = os.path.abspath(chemin)  # v11 : au manifeste (C11 du socle)
        self.graine, self.nul_informe, self.crete = graine, nul_informe, crete
        if not (isinstance(tranches, int) and tranches >= 1):
            raise BanqueInvalide("tranches : entier ≥ 1")
        self.tranches = tranches
        self._tranche_de_fiche = {}  # tranche fixée au premier gel d'une fiche (un rejeu ne change pas de tranche)
        for cle in ("traits", "moniteurs", "instances"):
            if cle not in self.banque:
                raise BanqueInvalide(f"banque sans champ {cle!r}")
        self._par_traits = {}
        for ligne in self.banque["instances"]:
            self._par_traits.setdefault(self._cle(ligne["z"], ligne["g"]), []).append(ligne)
        self._connus = {}
        # Tranches de la partie d'épreuve (v7, exposition adaptative) : par tâche quand la banque en déclare, sinon par
        # instance ; affectation tirée par la graine du monde, fixe.
        import random as _random
        groupes = sorted({l.get("tache", l["identifiant"]) for l in self.banque["instances"] if l.get("partie", "epreuve") == "epreuve"})
        _random.Random(graine_derivee(graine, "tranches", self.empreinte_banque)).shuffle(groupes)
        self._tranche_du_groupe = {g: i % tranches for i, g in enumerate(groupes)}

    def tranche_de_ligne(self, ligne):
        return self._tranche_du_groupe.get(ligne.get("tache", ligne["identifiant"]), 0)

    def description_publique(self):
        """Ce que voit un proposeur : noms des traits, moniteurs (nombre d'issues, effectifs), sous-populations ;
        jamais une issue."""
        moniteurs = {}
        for nom, m in self.banque["moniteurs"].items():
            moniteurs[nom] = {"nombre_issues": m["nombre_issues"],
                              "epreuve": len(self._lignes(nom, "epreuve")), "calibrage": len(self._lignes(nom, "calibrage"))}
        return {"nom": self.banque.get("nom", "banque"), "traits": list(self.banque["traits"]),
                "sous_populations": int(self.banque.get("sous_populations", 2)), "moniteurs": moniteurs,
                "tranches": self.tranches}

    def donnees_developpement(self):
        """Partie de développement servie aux agents (v7, pièce 4 bis, phase exploratoire), traits **et issues** ;
        l'épreuve n'y figure jamais. Explorer ici ne coûte rien à la garantie : l'épreuve reste fraîche.

        v7, version 7 (synthèse du collisionneur « proposeur enfichable ») : une banque qui porte une partie
        « developpement » la sert, **distincte** de la partie de calibrage où le prédicteur connu est ajusté ; à défaut, la
        partie de calibrage (comportement des versions 4 à 6), et le drapeau `meme_partie_que_le_connu` le dit."""
        distincte = any(l.get("partie") == "developpement" for l in self.banque["instances"])
        partie = "developpement" if distincte else "calibrage"
        lignes = [l for l in self.banque["instances"] if l.get("partie", "epreuve") == partie]
        return {"traits": list(self.banque["traits"]), "moniteurs": {n: m["nombre_issues"] for n, m in self.banque["moniteurs"].items()},
                "partie": partie, "meme_partie_que_le_connu": not distincte,
                "instances": [{"identifiant": l["identifiant"], "z": list(l["z"]), "g": l["g"], "issues": dict(l["issues"])}
                              for l in lignes]}

    def predicteurs_connus_publics(self):
        """Lois des prédicteurs connus (ajustées sur la partie de calibrage ; déjà visibles dans les engagements)."""
        if not self.nul_informe:
            return {}
        sortie = {}
        for nom, m in self.banque["moniteurs"].items():
            if len(self._lignes(nom, "calibrage")) >= 5 * m["nombre_issues"]:
                fiche_factice = type("F", (), {"espace_instances": {"moniteur": nom, "nombre_issues": m["nombre_issues"],
                                                                    "dimension": len(self.banque["traits"])}})()
                sortie[nom] = self.membres_informes(fiche_factice)[0]["loi"]
        return sortie

    @staticmethod
    def _cle(z, g):
        return json.dumps([z, g], separators=(",", ":"))

    def moniteur_de(self, fiche):
        espace = fiche.espace_instances or {}
        nom = espace.get("moniteur")
        if nom not in self.banque["moniteurs"]:
            raise BanqueInvalide(f"moniteur inconnu de la banque : {nom!r}")
        m = self.banque["moniteurs"][nom]
        if int(espace.get("nombre_issues", m["nombre_issues"])) != m["nombre_issues"]:
            raise BanqueInvalide(f"nombre d'issues de la fiche ({espace.get('nombre_issues')}) différent de celui du "
                                 f"moniteur {nom} ({m['nombre_issues']})")
        if int(espace.get("dimension", len(self.banque["traits"]))) != len(self.banque["traits"]):
            raise BanqueInvalide("dimension de la fiche différente du nombre de traits de la banque")
        return nom

    def _lignes(self, moniteur, partie):
        return [l for l in self.banque["instances"] if l.get("partie", "epreuve") == partie and moniteur in l["issues"]]

    def reservoir(self, fiche, numero_generation=0):
        """Instances d'épreuve (traits seulement) qui portent une issue pour le moniteur de la fiche ; avec des tranches,
        celles de la tranche de la génération du premier gel de la fiche."""
        moniteur = self.moniteur_de(fiche)
        lignes = self._lignes(moniteur, "epreuve")
        if self.tranches > 1:
            cle = fiche.empreinte() if hasattr(fiche, "empreinte") else id(fiche)
            tranche = self._tranche_de_fiche.setdefault(cle, numero_generation % self.tranches)
            lignes = [l for l in lignes if self.tranche_de_ligne(l) == tranche]
        if not lignes:
            raise BanqueInvalide(f"aucune instance d'épreuve pour le moniteur {moniteur}")
        return [{"z": list(l["z"]), "g": l["g"]} for l in lignes]

    def mesures(self, enonce, gele, graine_noyau, numero_generation):
        """Issues lues dans la banque pour les instances du plan ; liées à l'engagement ; ordre secret recalculé."""
        engagement = gele.engagement
        moniteur = engagement.get("moniteur") or self._moniteur_du_plan(engagement)
        issues, servies = [], set()
        for instance in engagement["instances"]:
            candidats = [l for l in self._par_traits.get(self._cle(instance["z"], instance["g"]), [])
                         if moniteur in l["issues"] and l.get("partie", "epreuve") == "epreuve" and l["identifiant"] not in servies]
            if not candidats:
                raise BanqueInvalide("instance du plan absente de la partie d'épreuve pour ce moniteur (aucun repli)")
            servies.add(candidats[0]["identifiant"])
            issues.append(int(candidats[0]["issues"][moniteur]))
        sortie = {"empreinte_engagement": gele.empreinte, "issues": issues,
                  "plan_execution": sp.plan_execution_de(engagement)}
        if sortie["plan_execution"] == "ordre_secret":
            pi = sp.ordre_execution(graine_noyau, gele.empreinte, len(engagement["instances"]))
            sortie["empreinte_ordre"] = empreinte_objet(pi)
        return sortie

    def _moniteur_du_plan(self, engagement):
        """Le moniteur est déclaré dans l'engagement (sous son empreinte) par `preparer_engagement` ; sinon, refus."""
        raise BanqueInvalide("engagement sans moniteur déclaré : le monde sur banque exige `moniteur` dans l'engagement")

    # --- nul informé --------------------------------------------------------------------------------------------
    def membres_informes(self, fiche):
        """Membre « connu » du moniteur de la fiche (ajusté une fois par moniteur, sur la partie de calibrage)."""
        if not self.nul_informe:
            return []
        moniteur = self.moniteur_de(fiche)
        if moniteur not in self._connus:
            lignes = self._lignes(moniteur, "calibrage")
            k = self.banque["moniteurs"][moniteur]["nombre_issues"]
            if len(lignes) < 5 * k:
                raise BanqueInvalide(f"partie de calibrage trop petite pour ajuster le prédicteur connu de {moniteur}")
            loi = ajuster_softmax([l["z"] for l in lignes], [int(l["issues"][moniteur]) for l in lignes], k, self.crete)
            self._connus[moniteur] = {"nom": f"connu:{moniteur}", "type": "loi", "loi": loi,
                                      "ajuste_sur": {"partie": "calibrage", "instances": len(lignes), "crete": self.crete,
                                                     "banque": self.empreinte_banque}}
        return [dict(self._connus[moniteur])]


def ajuster_softmax(zs, issues, k, crete=1.0, iterations=200, pas=0.5):
    """Régression multinomiale à crête (pénalité `crete`·‖poids‖²/2), descente de gradient avec recherche de pas ;
    rend une loi « softmax » du pôle. numpy, importé ici seulement."""
    import numpy as np
    X = np.asarray(zs, dtype=float)
    n, d = X.shape
    Y = np.zeros((n, k))
    Y[np.arange(n), np.asarray(issues, dtype=int)] = 1.0
    W, b = np.zeros((k, d)), np.zeros(k)

    def perte(W, b):
        s = X @ W.T + b
        s -= s.max(axis=1, keepdims=True)
        lp = s - np.log(np.exp(s).sum(axis=1, keepdims=True))
        return -(Y * lp).sum() / n + crete * (W * W).sum() / (2 * n)

    courant = perte(W, b)
    for _ in range(iterations):
        s = X @ W.T + b
        s -= s.max(axis=1, keepdims=True)
        P = np.exp(s)
        P /= P.sum(axis=1, keepdims=True)
        gW = ((P - Y).T @ X) / n + crete * W / n
        gb = (P - Y).sum(axis=0) / n
        taille = pas
        while taille > 1e-6:
            W2, b2 = W - taille * gW, b - taille * gb
            nouvelle = perte(W2, b2)
            if nouvelle <= courant:
                W, b, courant = W2, b2, nouvelle
                break
            taille /= 2
        else:
            break
        if math.sqrt((gW * gW).sum() + (gb * gb).sum()) < 1e-6:
            break
    return {"type": "softmax", "poids": [[round(float(x), 6) for x in ligne] for ligne in W],
            "biais": [round(float(x), 6) for x in b]}


def charger_monde_banque(chemin, graine, nul_informe=True, tranches=1):
    return MondeBanque(chemin, graine, nul_informe=nul_informe, tranches=tranches)


__all__ = ["BanqueInvalide", "MondeBanque", "ajuster_softmax", "charger_monde_banque", "graine_derivee"]
