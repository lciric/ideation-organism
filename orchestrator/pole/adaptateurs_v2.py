"""**Version 2 des adaptateurs** (orchestrateur v52) : `pole/adaptateurs.py` reste tel quel (R12) ; ce module n'ajoute que ce
que demande le mode « juges seulement » (décision du directeur R-805, 30 octobre 2026) — un adaptateur du kit qui accepte, **en
plus** des modèles permis par la décision du 27 octobre (`MODELES_REELS_PERMIS` : Opus 5.5, Fable 5.1), les seuls modèles de
repli **déclarés** par `--bascule-declaree` et autorisés par une décision (`BASCULES_AUTORISEES`).

L'adaptateur ne bascule jamais lui-même : il lance le modèle qu'on lui demande. C'est le cœur du mode (`pole/juges_seulement_v1.py`)
qui, sur un refus du modèle déclaré, et seulement alors, ouvre une session neuve du même juge sur le modèle de repli. Le kit reste
sans repli (`fallback_model=None`, variables `VARIABLES_SANS_REPLI_DE_MODELE`) ; toute bascule du kit dans une session reste un
refus (R-764), lu par `AdaptateurClaudeSDK._executer`, inchangé.
"""

import asyncio
import os

from .adaptateurs import (MODELES_REELS_PERMIS, AdaptateurClaudeSDK, ModeleNonPermis, MoteurNonArme, Resultat,
                          construire_options, importer_sdk, verifier_modele_reel)
from .caviardage import caviarder
from .outils import lister_fichiers
from .relais import CleDansEnvironnement, noms_de_cle_presents

# Bascules déclarables : (modèle déclaré, modèle de repli) → décision qui l'autorise. Toute autre paire est refusée avant tout
# appel (une nouvelle paire exige une nouvelle décision, donc une nouvelle version du code).
BASCULES_AUTORISEES = {
    ("claude-opus-5-5", "claude-opus-4-6"): "R-805 (mot direct de Lazar, 30 octobre 2026, ≈ 08:00 UTC : « bascule sur opus 4.6 si "
                                            "refus d'opus ») : juge seulement, bascule déclarée, modèle servi consigné",
}


def verifier_bascules(bascules):
    """`bascules` : {modèle déclaré: modèle de repli}. Lève `ModeleNonPermis` pour toute paire hors de `BASCULES_AUTORISEES` ;
    rend {modèle déclaré: {"repli", "autorisation"}}."""
    sortie = {}
    for declare, repli in dict(bascules or {}).items():
        if not isinstance(declare, str) or not isinstance(repli, str) or declare == repli:
            raise ModeleNonPermis(f"bascule déclarée mal formée : {declare!r} → {repli!r}")
        verifier_modele_reel(declare)  # le modèle déclaré reste un modèle de la décision du 27 octobre
        motif = BASCULES_AUTORISEES.get((declare, repli))
        if motif is None:
            raise ModeleNonPermis(f"bascule {declare!r} → {repli!r} non autorisée : seules {sorted(BASCULES_AUTORISEES)} le sont "
                                  "(R-805) ; toute autre bascule reste un arrêt (R-764)")
        sortie[declare] = {"repli": repli, "autorisation": motif}
    return sortie


def verifier_modele_reel_ou_repli(modele, replis=()):
    """Le modèle est permis par la décision du 27 octobre, ou il est exactement un modèle de repli déclaré (jamais par préfixe)."""
    if isinstance(modele, str) and modele in tuple(replis):
        return modele
    return verifier_modele_reel(modele)


class AdaptateurClaudeSDKBascule(AdaptateurClaudeSDK):
    """L'adaptateur du kit (`AdaptateurClaudeSDK`), qui accepte aussi les modèles de repli déclarés (`replis`, noms exacts,
    chacun dans `BASCULES_AUTORISEES`). Même lancement, mêmes options, même lecture du modèle servi et des refus ; seule la
    vérification du nom du modèle demandé change. Les juges n'ont aucun outil : le chemin « outils de lecture » de la v46 n'est
    pas repris (refusé ici)."""

    nom = "claude-sdk"

    def __init__(self, url_relais, replis=(), **kw):
        super().__init__(url_relais, **kw)
        autorises = {r for (_, r) in BASCULES_AUTORISEES}
        hors = sorted(set(replis) - autorises)
        if hors:
            raise ModeleNonPermis(f"modèle(s) de repli {hors} hors des bascules autorisées (R-805)")
        self.replis = tuple(sorted(set(replis)))

    def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None, racine_lecture=None,
               max_demandes_lecture=1000, mode_lecture=None):
        if racine_lecture is not None or mode_lecture is not None:
            raise ValueError("adaptateur de bascule : juges sans outil seulement (aucune lecture de dossier fermé)")
        environnement = os.environ if self._environnement is None else self._environnement
        presents = noms_de_cle_presents(environnement)
        if presents:
            raise CleDansEnvironnement("variables de clé présentes dans l'environnement de l'orchestrateur ("
                                       + ", ".join(presents) + ") : la clé doit rester dans le relais du noyau")
        if not self.arme:
            raise MoteurNonArme("moteur réel non armé : aucun agent réel n'est lancé (essais, simulation)")
        verifier_modele_reel_ou_repli(modele, self.replis)
        sdk = importer_sdk()
        o = construire_options(os.path.abspath(dossier), budget_usd, max_tours, url_relais=self.url_relais,
                               modele=modele, role=role, interdire_lecture=self.interdire_lecture)
        options = self.options_sdk(sdk, o)
        texte, cout, statut, erreur, lecture = asyncio.run(self._executer(sdk, consigne, options, self.delai_s))
        return Resultat(caviarder(texte)[0], lister_fichiers(dossier), cout, statut, erreur, texte_brut=texte,
                        refus=lecture["refus"], modele_servi=lecture["modele_servi"],
                        depense_modele_non_autorise_usd=lecture["depense_modele_non_autorise_usd"],
                        cout_inconnu=lecture["cout_inconnu"])


__all__ = ["BASCULES_AUTORISEES", "MODELES_REELS_PERMIS", "AdaptateurClaudeSDKBascule", "verifier_bascules",
           "verifier_modele_reel_ou_repli"]
