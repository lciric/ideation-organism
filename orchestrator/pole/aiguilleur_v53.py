"""Aiguilleur avant les juges (R-575, M4) et garde de niveau méthode chez Kimi proposeur (R-567, M5) — v53.

**Jamais sacrifié** : l'étape d'aiguillage est protégée dans le plan (rôle « protegee » de la configuration). Un lecteur
neuf (session neuve par fiche, consigne figée empreintée, une fiche anonyme par appel) classe chaque fiche :
`niveau_methode`, `a_corriger` ou `concret`. Seule une fiche `niveau_methode` reçoit un **passeport** ; toute autre
destination (juge, tableau, lecteur d'étiquettes, metteur en fusion) exige le passeport (A17, garde R5 ligne 12) : une fiche
sans passeport présentée à une destination est un arrêt (`SansPasseport`).

Une fiche `concret` ne va ni aux juges ni au tableau : elle est consignée au **journal scellé de l'aiguillage**
(identifiant opaque, empreinte, classe, catégorie déclarée par l'aiguilleur, fournisseur) — **le contenu n'est jamais
copié**. Une réponse illisible de l'aiguilleur, un refus ou une erreur valent aiguillage (M4 : comptés à part comme
« refus de l'aiguilleur », jamais un passage). Une fiche `a_corriger` est retenue et comptée (choix de code v53 : aucune
correction automatique dans la course ; elle n'est servie à personne).

Garde de niveau méthode chez Kimi (`GardeKimi`) : chaque fiche de Kimi passe l'aiguilleur ; une fiche `concret` (ou
aiguillée par refus) est **refusée et journalisée** ; le taux de débordement est lu après chaque passe contre le seuil
injecté S12 (`garde_kimi.debordement_max`) : au-dessus, `DebordementKimi` (arrêt du rôle proposeur de Kimi, nœud).

Étalonnage (M4, pré-pilote) : `etalonner` calcule rappel sur les concrets écrits et fausses alertes sur les fiches de niveau
méthode, et les compare aux seuils injectés S10, S11 (aucun défaut).
"""

import json
import os

from .fiches_v53 import entree_une_fiche
from .outils import EcrasementInterdit, ecrire_json_scelle, extraire_bloc_json

VERSION = "aiguilleur-v53"
CLASSES = ("niveau_methode", "a_corriger", "concret")


class SansPasseport(RuntimeError):
    """A17 : une fiche non passée par l'aiguilleur atteint un juge, le tableau ou un lecteur."""


class DebordementKimi(RuntimeError):
    """M5 : débordement de Kimi proposeur au-dessus de S12 : arrêt du rôle."""


def lire_classe(texte):
    bloc = extraire_bloc_json(texte, "classe")
    if not bloc or bloc.get("classe") not in CLASSES:
        return None, None
    cat = bloc.get("categorie")
    return bloc["classe"], (cat if isinstance(cat, str) and len(cat) <= 40 else None)


class Aiguilleur:
    def __init__(self, adaptateur, *, etiquette, modele, consigne_figee, etiquettes_interdites, plafond_session_usd,
                 journal_dossier):
        if os.path.exists(journal_dossier):
            raise EcrasementInterdit(f"journal d'aiguillage {journal_dossier} déjà présent (R12)")
        os.makedirs(journal_dossier)
        self.adaptateur, self.etiquette, self.modele = adaptateur, etiquette, modele
        self.consigne = consigne_figee
        self.interdites = list(etiquettes_interdites)
        self.plafond = float(plafond_session_usd)
        self.dossier = journal_dossier
        self.passeports = {}      # ident -> empreinte (le contenu exact qui a été aiguillé)
        self.decisions = {}       # ident -> {classe, motif}
        self.journal = []         # fiches retenues : jamais de contenu
        self.refus = 0
        self.modele_servi = None

    def classer(self, fiche, plafond=None, dossier_appel=None):
        """Rend (classe retenue, coût). `plafond` : plafond de la session (≤ plafond injecté)."""
        consigne = entree_une_fiche(self.consigne, fiche, self.interdites)
        plafond = min(self.plafond, plafond) if plafond is not None else self.plafond
        d = dossier_appel or os.path.join(self.dossier, "appels", fiche["ident"])
        os.makedirs(d, exist_ok=True)
        r = self.adaptateur.lancer("juge_ideation", consigne, d, plafond, 1, modele=self.modele)
        classe, categorie = (lire_classe(r.texte_brut or r.texte_final) if r.statut == "ok" else (None, None))
        if r.statut == "ok" and r.modele_servi:
            self.modele_servi = self.modele_servi or r.modele_servi
        motif = None
        if classe is None:
            self.refus += 1
            motif = f"refus ou réponse illisible de l'aiguilleur (statut {r.statut}) : vaut aiguillage (M4)"
            classe_retenue = "concret"
        else:
            classe_retenue = classe
        self.decisions[fiche["ident"]] = {"classe": classe_retenue, "lue": classe, "motif": motif}
        if classe_retenue == "niveau_methode":
            self.passeports[fiche["ident"]] = fiche["empreinte"]
        else:
            self.journal.append({"ident": fiche["ident"], "empreinte": fiche["empreinte"], "classe": classe_retenue,
                                 "categorie": categorie, "fournisseur": fiche["meta"]["fournisseur"],
                                 "passe": fiche["meta"]["passe"], "origine": fiche["meta"]["origine"],
                                 "refus_aiguilleur": classe is None, "contenu": "non copié (R-575)"})
        return classe_retenue, float(r.cout_declare_usd)

    def a_passeport(self, fiche):
        return self.passeports.get(fiche.get("ident")) == fiche.get("empreinte")

    def exiger_passeport(self, fiche, destination):
        if not self.a_passeport(fiche):
            raise SansPasseport(f"A17 : fiche {fiche.get('ident')!r} sans passage « niveau méthode » par l'aiguilleur présentée "
                                f"à {destination} : arrêt, notations annulées")
        return True

    def sceller_journal(self, nom="journal-aiguillage"):
        objet = {"version": VERSION, "regle": "fiches retenues (concret, à corriger, refus) : identifiant, empreinte, classe ; "
                 "contenu jamais copié (R-575)", "retenues": self.journal, "refus_aiguilleur": self.refus,
                 "passeports": len(self.passeports), "modele_servi": self.modele_servi}
        return ecrire_json_scelle(os.path.join(self.dossier, nom + ".json"), objet)


class GardeKimi:
    def __init__(self, debordement_max):
        if isinstance(debordement_max, bool) or not isinstance(debordement_max, (int, float)) or not 0 <= debordement_max <= 1:
            raise ValueError("S12 : réel de 0 à 1 exigé, aucun défaut")
        self.seuil = float(debordement_max)
        self.vues, self.debordements = 0, 0
        self.refusees = []

    def noter(self, fiche, classe):
        self.vues += 1
        if classe != "niveau_methode":
            self.debordements += 1 if classe == "concret" else 0
            self.refusees.append({"ident": fiche["ident"], "empreinte": fiche["empreinte"], "classe": classe})

    def taux(self):
        return self.debordements / self.vues if self.vues else 0.0

    def verifier(self):
        if self.vues and self.taux() > self.seuil + 1e-12:
            raise DebordementKimi(f"débordement de Kimi proposeur {self.debordements}/{self.vues} = {self.taux():.3f} > S12 = "
                                  f"{self.seuil:g} : arrêt du rôle proposeur de Kimi (nœud)")
        return True

    def etat(self):
        return {"vues": self.vues, "concretes": self.debordements, "taux": self.taux(), "seuil_S12": self.seuil,
                "refusees": self.refusees}


def etalonner(decisions, attendus, *, rappel_min, fausses_alertes_max):
    """M4 : `decisions` {ident: classe retenue}, `attendus` {ident: "concret" | "niveau_methode"}. Seuils injectés (S10, S11).
    Rappel = part des concrets écrits aiguillés (classe ≠ niveau_methode) ; fausses alertes = part des fiches de niveau
    méthode aiguillées."""
    for nom, v in (("rappel_min", rappel_min), ("fausses_alertes_max", fausses_alertes_max)):
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not 0 <= v <= 1:
            raise ValueError(f"{nom} : réel de 0 à 1 exigé, aucun défaut")
    concrets = [i for i, a in attendus.items() if a == "concret"]
    methode = [i for i, a in attendus.items() if a == "niveau_methode"]
    rappel = sum(decisions[i] != "niveau_methode" for i in concrets) / len(concrets) if concrets else None
    fa = sum(decisions[i] != "niveau_methode" for i in methode) / len(methode) if methode else None
    ok = rappel is not None and fa is not None and rappel + 1e-12 >= rappel_min and fa <= fausses_alertes_max + 1e-12
    return {"rappel": rappel, "fausses_alertes": fa, "n_concrets": len(concrets), "n_methode": len(methode),
            "etalonne": ok, "seuils": {"rappel_min": rappel_min, "fausses_alertes_max": fausses_alertes_max}}


def resume_json(aiguilleur):
    return json.loads(json.dumps({"decisions": aiguilleur.decisions, "refus": aiguilleur.refus}))
