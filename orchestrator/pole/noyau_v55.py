"""Noyau de la v55 — un mélange (`OrchestreV55`) placé devant l'orchestre v54 (inchangé, R12) dans les classes de la course
et du pré-pilote.

- **CL19-04** : les dossiers de session ne sont plus sous `sortie/sessions/`, voisins de `coffre/`, `temoins/`,
  `aiguillage/`. Ils vivent sous une racine **séparée** (`<base>/sessions/<opaque>`, `base` = dossier temporaire neuf hors de
  la sortie, ou racine injectée). Chaque chemin est normalisé (`realpath`), refusé s'il passe par un lien symbolique, s'il
  est sous la sortie, ou si la sortie est sous la base ; et l'ancêtre commun d'une session et du coffre doit être **au-dessus
  de la base** : depuis une session, `..` ne voit que des sessions, `../..` ne voit que `sessions/`, et le coffre n'est
  atteignable qu'en remontant hors de la base puis en connaissant le nom (tiré) de la sortie. L'isolement réel reste celui
  du bac (bwrap sur la machine du run) ; ce code ne le remplace pas.
- **CL19-10 (A2)** : un appel au statut « ok » sans modèle servi lu est un arrêt A2 (`ModeleServiAbsent`), pour tous les
  rôles (la v54 ne gardait que les juges, et seulement le changement entre lots).
- **CL19-03** : le coffre est un `CoffreV55` (lectures par programme journalisées, `coffre_v55`).
"""

import hashlib
import os
import tempfile

from .coffre_v55 import CoffreV55

VERSION = "noyau-v55"


class ModeleServiAbsent(RuntimeError):
    """A2 : réponse « ok » sans nom de modèle servi : on ne sait pas qui a répondu."""


class SessionsMalPlacees(RuntimeError):
    """CL19-04 : racine des sessions sous la sortie, voisine du coffre, ou chemin non normalisé."""


def controle_a2(statut, modele_servi, modele_demande):
    if statut == "ok" and not modele_servi:
        raise ModeleServiAbsent(f"A2 : modèle servi non lu pour une réponse « ok » (modèle demandé {modele_demande!r}) : arrêt")
    return True


def _sous(chemin, racine):
    chemin, racine = os.path.realpath(chemin), os.path.realpath(racine)
    return chemin == racine or chemin.startswith(racine.rstrip(os.sep) + os.sep)


def verifier_emplacement_sessions(base, sortie, coffre=None):
    """Refuse une base de sessions mal placée (CL19-04). Rend la racine `<base>/sessions` normalisée."""
    if os.path.realpath(base) != os.path.abspath(base):
        raise SessionsMalPlacees(f"racine des sessions {base!r} : chemin non normalisé ou lien symbolique")
    if _sous(base, sortie):
        raise SessionsMalPlacees("racine des sessions sous la sortie (voisine du coffre) : refusée")
    if _sous(sortie, base):
        raise SessionsMalPlacees("sortie sous la racine des sessions : refusée")
    # le coffre (sous la sortie) n'est donc jamais sous la base : l'ancêtre commun d'une session et du coffre est au-dessus
    # de la base (`<base>/sessions/<opaque>` : deux niveaux sans voisin)
    return os.path.join(os.path.realpath(base), "sessions")


class OrchestreV55:
    """Mélange à placer avant `GenerationV54` ; `racine_sessions` est lu sur l'instance si posé avant `__init__`."""

    def __init__(self, *a, **kw):
        base = kw.pop("racine_sessions", None) or getattr(self, "_racine_sessions_demandee", None)
        super().__init__(*a, **kw)
        # coffre v55 à la place du coffre v54 (vide à ce stade : vérifié, jamais en silence)
        ancien = self.coffre
        if ancien.acces or os.listdir(ancien.dossier):
            raise RuntimeError("coffre déjà utilisé avant son remplacement par le coffre v55")
        os.rmdir(ancien.dossier)
        self.coffre = CoffreV55(ancien.dossier)
        if base is None:
            base = tempfile.mkdtemp(prefix="pole-sessions-v55-")
        else:
            os.makedirs(base, exist_ok=True)
        self.racine_sessions = verifier_emplacement_sessions(base, self.sortie, self.coffre.dossier)
        os.makedirs(self.racine_sessions, exist_ok=True)
        self.base_sessions = os.path.realpath(base)

    def session(self, *logique):
        chemin = "/".join(str(x) for x in logique)
        opaque = hashlib.sha256(f"{self.conf['racine_graines']}|{self.prefixe}|{chemin}".encode("utf-8")).hexdigest()[:16]
        self.sessions[opaque] = chemin
        d = os.path.join(self.racine_sessions, opaque)
        os.makedirs(d, exist_ok=True)
        if os.path.realpath(d) != d or not _sous(d, self.racine_sessions) or _sous(d, self.sortie):
            raise SessionsMalPlacees(f"dossier de session {opaque} hors de la racine des sessions ou non normalisé")
        return d

    def appel(self, etat, **kw):
        a = super().appel(etat, **kw)
        if a is not None:
            controle_a2(a["r"].statut, getattr(a["r"], "modele_servi", None), kw.get("modele"))
        return a

    def ranger_sessions(self):
        """Fin de run : retire les dossiers de session **vides** (aucune trace écrite), puis `sessions/` et la base s'ils sont
        vides ; un dossier qui porte une trace est laissé. Rend {retires, gardes}."""
        retires, gardes = 0, 0
        for opaque in sorted(self.sessions):
            d = os.path.join(self.racine_sessions, opaque)
            if os.path.isdir(d) and not os.listdir(d):
                os.rmdir(d)
                retires += 1
            elif os.path.isdir(d):
                gardes += 1
        for d in (self.racine_sessions, self.base_sessions):
            if os.path.isdir(d) and not os.listdir(d):
                os.rmdir(d)
        return {"retires_vides": retires, "gardes_avec_traces": gardes}

    def deposer_cles(self):
        super().deposer_cles()
        self.coffre.deposer(self.tache("emplacement-sessions"), {"base": self.base_sessions, "racine": self.racine_sessions})


__all__ = ("OrchestreV55", "ModeleServiAbsent", "SessionsMalPlacees", "controle_a2", "verifier_emplacement_sessions")
