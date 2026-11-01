"""Moteur simulé de la course 2 (v53) : aucun appel, aucune dépense réelle ; réponses déterministes lues sur la consigne.

`AdaptateurSimuleCourse2` répond selon le rôle et les marques de section que le noyau écrit dans la consigne : proposeur
(`## Case`) → un bloc `{"fiches": [...]}` aux champs injectés ; aiguilleur (consigne figée contenant `AIGUILLEUR`) →
`{"classe": …}` ; juge (consigne figée contenant `JUGE`) → `{"items": {…}}` ; lecteur d'étiquettes (`## Lecture :`) → des
étiquettes tirées de la liste fermée servie ; metteur en fusion (`## Les deux fiches`) → une fiche. Coût fictif fixe par
appel (injecté). Les essais remplacent `decider` pour planter un artefact (concret, refus, modèle servi autre…).
"""

import hashlib
import json
import re

from .adaptateurs import Adaptateur, Resultat

VERSION = "simulation-course-2-v53"


def _h(texte, sel=""):
    return int.from_bytes(hashlib.sha256((sel + texte).encode("utf-8")).digest()[:4], "big")


class AdaptateurSimuleCourse2(Adaptateur):
    nom = "simule-course-2"

    def __init__(self, *, champs_fiche, items, cout_par_appel_usd, fiches_par_appel=2, modele_servi=None, decider=None,
                 champ_titre=None):
        self.champs = list(champs_fiche)
        self.items = list(items)
        self.cout = float(cout_par_appel_usd)
        self.n = fiches_par_appel
        self.modele_servi = modele_servi
        self.decider = decider
        self.champ_titre = champ_titre or self.champs[0]
        self.appels = []

    def description(self):
        return {"version": VERSION, "cout_par_appel_usd": self.cout, "fictif": True}

    def fiche(self, graine):
        f = {c: f"{c} simulé {graine} : méthode de mesure générale {graine % 97}" for c in self.champs}
        f[self.champ_titre] = f"Titre simulé {graine}"
        return f

    def reponse(self, role, consigne, modele):
        if "## Lecture :" in consigne:
            nature = re.search(r"## Lecture : (\S+)", consigne).group(1)
            liste = json.loads(re.search(r"## Liste fermée\n```json\n(.*?)\n```", consigne, re.S).group(1))
            h = _h(consigne)
            if nature == "niches":
                niches, types = liste["niches"], liste["types_structure"]
                return json.dumps({"niche": niches[h % len(niches)],
                                   "structures": [{"type": types[0], "nom": "objet commun"}], "affirmation_centrale": "x"})
            k = min(len(liste), 3)
            return json.dumps({"etiquettes": [liste[(h + i * 7) % len(liste)] for i in range(k)]})
        if "## Les deux fiches" in consigne:
            return json.dumps({"fiches": [self.fiche(_h(consigne, "fusion" + str(modele)))]}, ensure_ascii=False)
        if "## Case" in consigne:
            return json.dumps({"fiches": [self.fiche(_h(consigne, str(modele) + str(i))) for i in range(self.n)]}, ensure_ascii=False)
        if "AIGUILLEUR" in consigne:
            return json.dumps({"classe": "niveau_methode"})
        if "JUGE" in consigne:
            h = _h(consigne)
            return json.dumps({"items": {k: bool((h >> i) & 1) or i > 1 for i, k in enumerate(self.items)}})
        return json.dumps({"rien": True})

    def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
        texte = self.reponse(role, consigne, modele)
        servi = self.modele_servi or modele
        statut = "ok"
        if self.decider is not None:
            d = self.decider(role, consigne, modele, len(self.appels))
            if d is not None:
                texte = d.get("texte", texte)
                servi = d.get("modele_servi", servi)
                statut = d.get("statut", statut)
        cout = min(self.cout, float(budget_usd))
        self.appels.append({"role": role, "modele": modele, "cout": cout, "taille_consigne": len(consigne), "case": "## Case" in consigne,
                            "tableau": "## Tableau minimal" in consigne})
        return Resultat(texte if statut == "ok" else "", [], cout, statut, texte_brut=texte if statut == "ok" else None,
                        modele_servi=servi)
