"""Gardes d'arrêt par rôle (A3, A11, A14 ; brouillon 7, Liste d'arrêt ; table R5 lignes 25, 28, 32) — v54.

Chaque appel d'un rôle (juge, aiguilleur, proposeur, lecteur, rédacteur, metteur en forme…) passe par `SuiviRoles` :

- **A3** : appel coupé (durée au-delà du délai de son fournisseur, `arrets.a3_delai_s`, clé « * » pour les autres) ou sans
  sortie exploitable = **échec compté** ; `arrets.a3_echecs_consecutifs` échecs consécutifs d'un rôle → **arrêt du rôle**
  (ses appels suivants ne sont pas lancés ; motif consigné). Un appel coupé n'est jamais lu, même s'il a rendu un texte
  (choix de code v54, côté prudent).
- **A11** : pour un modèle de `arrets.a11_modeles` (Opus 5.5), un refus est compté (`refus_a11`) ; une **limite
  hebdomadaire** (statut `limite`, ou refus dont l'événement est `limite_hebdomadaire`) arrête le rôle en « attente » —
  jamais de bascule vers un autre modèle ; un modèle servi différent est un arrêt A2 (`BasculeInterdite`).
- **A14** : part des appels d'un rôle sans sortie exploitable, cumulée sur le run ; au-delà de `arrets.a14_part_max`, la mesure
  de l'étape est « non mesurée (technique) » (nœud) — lu par l'orchestrateur à la fin de chaque étape.

L'horloge est injectable (essais) ; aucune attente réelle n'est faite (l'« attente » d'A11 est un arrêt du rôle, à reprendre
sur mot de Lazar).
"""

import time

VERSION = "suivi-roles-v54"


class RoleArrete(RuntimeError):
    """Le rôle est arrêté (A3 ou A11) : aucun appel de plus."""


class BasculeInterdite(RuntimeError):
    """A2/A11 : un modèle servi autre que celui demandé pour un rôle d'A11 : arrêt, aucune bascule."""


class SuiviRoles:
    def __init__(self, arrets, horloge=None):
        self.echecs_max = int(arrets["a3_echecs_consecutifs"])
        self.delais = dict(arrets["a3_delai_s"])
        self.part_max = float(arrets["a14_part_max"])
        self.modeles_a11 = set(arrets["a11_modeles"])
        self.horloge = horloge or time.monotonic
        self.roles = {}

    def _r(self, role):
        return self.roles.setdefault(role, {"appels": 0, "inexploitables": 0, "consecutifs": 0, "coupes": 0, "refus_a11": 0,
                                            "arrete": None, "etapes": {}})

    def delai(self, fournisseur):
        return float(self.delais.get(fournisseur, self.delais["*"]))

    def avant(self, role):
        r = self._r(role)
        if r["arrete"]:
            raise RoleArrete(f"rôle {role} arrêté : {r['arrete']}")
        return self.horloge()

    def apres(self, role, etape, *, fournisseur, modele, duree, statut, exploitable, refus=None, modele_servi=None):
        """Rend (utilisable, motif, durée) : `utilisable` faux si l'appel est coupé ou inexploitable. `duree` : mesurée par
        l'orchestrateur autour de l'appel (horloge injectée)."""
        r = self._r(role)
        r["appels"] += 1
        e = r["etapes"].setdefault(etape, {"appels": 0, "inexploitables": 0})
        e["appels"] += 1
        coupe = duree > self.delai(fournisseur)
        motif = None
        if modele in self.modeles_a11 and modele_servi and modele_servi != modele:
            r["arrete"] = f"A11/A2 : modèle servi {modele_servi!r} au lieu de {modele!r} : aucune bascule"
            raise BasculeInterdite(r["arrete"])
        limite = statut == "limite" or (isinstance(refus, dict) and refus.get("evenement") == "limite_hebdomadaire")
        if modele in self.modeles_a11 and (statut == "refus" or limite):
            r["refus_a11"] += 1
        if coupe:
            r["coupes"] += 1
            motif = f"A3 : appel coupé ({duree:.0f} s > {self.delai(fournisseur):g} s)"
        elif not exploitable:
            motif = f"sortie inexploitable (statut {statut})"
        if motif:
            r["inexploitables"] += 1
            e["inexploitables"] += 1
            r["consecutifs"] += 1
        else:
            r["consecutifs"] = 0
        if modele in self.modeles_a11 and limite:
            r["arrete"] = "A11 : limite hebdomadaire — attente (aucune bascule) ; rôle à reprendre sur mot de Lazar"
        elif r["consecutifs"] >= self.echecs_max:
            r["arrete"] = f"A3 : {r['consecutifs']} échecs consécutifs : arrêt du rôle, relais à corriger"
        return motif is None, motif, round(duree, 3)

    def depassements_a14(self):
        """Rôles dont la part d'appels sans sortie exploitable dépasse A14 (cumul du run)."""
        return {role: round(r["inexploitables"] / r["appels"], 6) for role, r in self.roles.items()
                if r["appels"] and r["inexploitables"] / r["appels"] > self.part_max + 1e-12}

    def etat(self):
        return {"version": VERSION, "a3_echecs_consecutifs": self.echecs_max, "a3_delai_s": self.delais,
                "a14_part_max": self.part_max, "a11_modeles": sorted(self.modeles_a11),
                "roles": {k: dict(v) for k, v in sorted(self.roles.items())}}
