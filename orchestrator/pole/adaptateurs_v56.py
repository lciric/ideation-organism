"""Adaptateurs et relais, version 56 — au-dessus de `adaptateurs.py` et `adaptateur_kimi_v53.py` (inchangés, R12).

1. **CL20-01 (bloquant)** — `AdaptateurCommandeExterneV56` : la v55 contrôlait `modele_servi` sur la dernière ligne de la commande
   (`controle_modele`) puis **ne le recopiait pas** dans le résultat « ok » ; le contrôle A2 du noyau v55 (`controle_a2`)
   arrêtait donc l'exécution à la première réponse réussie d'Argon. Ici, la dernière ligne lue est gardée le temps de l'appel ;
   pour un statut « ok » ou « budget_depasse » (statuts où `controle_modele` n'a rien refusé), `modele_servi` est recopié dans
   le résultat s'il est dit et conforme au modèle demandé (identifiant exact, suffixe de date strict, ou liste explicite) ; une
   ligne non conforme qui passerait malgré tout devient un refus (jamais en silence). Une ligne « ok » **sans** `modele_servi`
   reste sans modèle servi : A2 l'arrête au noyau (arrêt du rôle, `noyau_v56`).
2. **CL20-02 (bloquant), DEP4 et A15 du brouillon 10** — **portes de plafond d'étape** : au lancement de chaque étape, le noyau
   transmet à chaque relais le plafond dur calculé selon A1 (`budget_v56`), qui ne change plus pendant l'étape ; un relais qui
   ne peut pas le recevoir, ou dont l'accusé ne porte pas le même plafond au centime, arrête le lancement (A15) :
   - `PortePlafondNoyau` : moteur simulé, aucun relais réel (le noyau tient seul le plafond : plafond de chaque appel borné au
     reste de l'étape) ; **refusée pour un adaptateur réel** ;
   - `PortePlafondEnvironnement` : commande externe (Argon), qui est elle-même son relais, lancée à chaque appel : le plafond
     dur et l'étape lui sont passés dans son environnement (`PLAFOND_ETAPE_USD`, `ETAPE_POLE`), les mêmes pour tous les appels
     de l'étape ;
   - `PortePlafondCommande` : relais persistant (relais Kimi v4, relais de Claude) : une commande de l'opérateur (session-depot)
     relance le relais avec ce plafond dur et imprime une ligne JSON `{"etape", "plafond_usd"}` ; environnement minimal,
     aucun nom de clé, groupe de processus arrêté au délai.
3. **CL20-06 (majeur)** — `verifier_lecture_interdite` : pour un adaptateur du kit (`AdaptateurClaudeSDK`), la liste de lecture
   interdite du bac doit couvrir la **sortie** (donc le coffre) en plus de la base des sessions ; depuis la relocalisation des
   sessions (v55), la liste par défaut (grand-parent du dossier de l'agent) ne couvrait plus que la base.
"""

import json
import os
import signal
import subprocess
from dataclasses import replace

from .adaptateur_kimi_v53 import AdaptateurKimiProtocole
from .adaptateurs import AdaptateurClaudeSDK, AdaptateurCommandeExterne, AdaptateurMixte, construire_options, modele_conforme
from .budget_v56 import centime_bas, centimes
from .caviardage import caviarder
from .relais import CleDansEnvironnement, noms_de_cle_presents

VERSION = "adaptateurs-v56"
VARIABLES_MINIMALES = ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR")
ROLES_KIT_DU_POLE = ("proposeur_ideation", "juge_ideation")


class RelaisSansPlafond(RuntimeError):
    """A15 (brouillon 10) : relais incapable de recevoir, au lancement de chaque étape, le plafond dur calculé selon A1."""


class LectureNonInterdite(RuntimeError):
    """CL20-06 : la liste de lecture interdite du bac d'un agent du kit ne couvre pas la sortie (ni donc le coffre)."""


# --- CL20-01 : commande externe qui recopie le modèle servi --------------------------------------------------------------------


class AdaptateurCommandeExterneV56(AdaptateurCommandeExterne):
    nom = "commande-externe-v56"

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._derniere = None
        self.plafond_etape = None  # (étape, plafond dur) reçu par `PortePlafondEnvironnement`

    def lire_derniere_ligne(self, sortie_octets):  # masque la méthode statique : garde l'objet lu le temps de l'appel
        objet, motif = AdaptateurCommandeExterne.lire_derniere_ligne(sortie_octets)
        self._derniere = objet
        return objet, motif

    def environnement_commande(self, budget_usd=None, role=None, modele=None):
        env = super().environnement_commande(budget_usd, role, modele)
        if self.plafond_etape is not None:
            env["ETAPE_POLE"], env["PLAFOND_ETAPE_USD"] = str(self.plafond_etape[0]), f"{self.plafond_etape[1]:.2f}"
        return env

    def description(self):
        d = super().description()
        d["version"] = VERSION
        d["modele_servi_recopie"] = ("CL20-01 : modele_servi de la dernière ligne recopié dans le résultat « ok » (et « budget_depasse ») "
                                     "après le contrôle de la commande ; absent : A2 au noyau")
        d["plafond_etape"] = "variables ETAPE_POLE et PLAFOND_ETAPE_USD (porte « environnement »), fixées au lancement de l'étape"
        return d

    def lancer(self, role, consigne, dossier, budget_usd, max_tours, modele=None):
        self._derniere = None
        r = super().lancer(role, consigne, dossier, budget_usd, max_tours, modele=modele)
        objet, self._derniere = self._derniere, None
        if r.statut not in ("ok", "budget_depasse") or r.modele_servi is not None or not isinstance(objet, dict):
            return r
        servi = objet.get("modele_servi")
        if not isinstance(servi, str) or not servi.strip():
            return r  # « ok » sans modèle servi : A2 au noyau (arrêt du rôle)
        if not (isinstance(modele, str) and modele and modele_conforme(modele, servi, self.modeles_servis_permis.get(modele, ()))):
            refus = {"motif": f"modèle servi {servi!r} ≠ modèle demandé {modele!r} (contrôle v56 à la recopie)",
                     "modele_demande": modele, "modele_servi": servi, "evenement": "commande.modele_servi"}
            return replace(r, texte_final="", texte_brut=None, statut="refus", erreur="refus (R-764) : " + refus["motif"],
                           refus=refus, modele_servi=servi, depense_modele_non_autorise_usd=float(r.cout_declare_usd))
        return replace(r, modele_servi=servi)


def est_adaptateur_reel(ad):
    """Vrai pour un adaptateur qui dépense réellement (kit, commande externe, Kimi par protocole, mixte à partie réelle)."""
    if isinstance(ad, AdaptateurMixte):
        return est_adaptateur_reel(ad.reel)
    return isinstance(ad, (AdaptateurClaudeSDK, AdaptateurCommandeExterne, AdaptateurKimiProtocole)) or bool(getattr(ad, "relais_reel", False))


# --- CL20-02 : portes de plafond d'étape ------------------------------------------------------------------------------------


class PortePlafondNoyau:
    """Aucun relais réel : le noyau tient seul le plafond dur (plafond de chaque appel borné au reste de l'étape)."""

    type = "noyau"

    def transmettre(self, etape, plafond_usd):
        return {"etape": etape, "plafond_usd": centime_bas(plafond_usd), "par": "noyau (aucun relais réel)"}

    def description(self):
        return {"type": self.type, "regle": "moteur simulé : plafond tenu par le noyau seul"}


class PortePlafondEnvironnement:
    """Commande externe (Argon) : le plafond dur de l'étape est passé à chaque appel dans l'environnement de la commande."""

    type = "environnement"

    def __init__(self, adaptateur):
        if not isinstance(adaptateur, AdaptateurCommandeExterneV56):
            raise RelaisSansPlafond("porte « environnement » : seulement pour une commande externe v56 (qui lit PLAFOND_ETAPE_USD)")
        self.adaptateur = adaptateur

    def transmettre(self, etape, plafond_usd):
        p = centime_bas(plafond_usd)
        self.adaptateur.plafond_etape = (etape, p)
        env = self.adaptateur.environnement_commande()
        if env.get("ETAPE_POLE") != str(etape) or env.get("PLAFOND_ETAPE_USD") != f"{p:.2f}":
            raise RelaisSansPlafond("porte « environnement » : le plafond n'est pas dans l'environnement de la commande")
        return {"etape": etape, "plafond_usd": p, "par": "environnement de la commande (PLAFOND_ETAPE_USD)"}

    def description(self):
        return {"type": self.type, "variables": ["ETAPE_POLE", "PLAFOND_ETAPE_USD"]}


class PortePlafondCommande:
    """Relais persistant : commande de l'opérateur qui relance le relais avec ce plafond dur ; accusé = dernière ligne JSON
    `{"etape", "plafond_usd"}`, égale au centime, code de sortie 0."""

    type = "commande"

    def __init__(self, commande, delai_s, environnement=None):
        if not isinstance(commande, (list, tuple)) or not commande or not all(isinstance(c, str) and c for c in commande):
            raise ValueError("porte de plafond : commande = liste non vide de chaînes")
        if isinstance(delai_s, bool) or not isinstance(delai_s, (int, float)) or not delai_s > 0:
            raise ValueError("porte de plafond : délai strictement positif (secondes), aucun défaut")
        self.commande, self.delai_s, self._environnement = list(commande), float(delai_s), environnement

    def _env(self, etape, plafond):
        source = os.environ if self._environnement is None else self._environnement
        presents = noms_de_cle_presents(source)
        if presents:
            raise CleDansEnvironnement("porte de plafond : variables de clé dans l'environnement de l'orchestrateur ("
                                       + ", ".join(presents) + ")")
        env = {v: source[v] for v in VARIABLES_MINIMALES if v in source}
        env.setdefault("PATH", os.defpath)
        env.update(ETAPE_POLE=str(etape), PLAFOND_ETAPE_USD=f"{plafond:.2f}")
        return env

    def transmettre(self, etape, plafond_usd):
        p = centime_bas(plafond_usd)
        env = self._env(etape, p)
        try:
            proc = subprocess.Popen(self.commande, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    env=env, start_new_session=True)
        except OSError as e:
            raise RelaisSansPlafond(f"porte de plafond non lancée ({type(e).__name__})") from None
        try:
            sortie, err = proc.communicate(timeout=self.delai_s)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except OSError:
                pass
            proc.communicate()
            raise RelaisSansPlafond(f"porte de plafond : délai de {self.delai_s:g} s dépassé (groupe arrêté)") from None
        except BaseException:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except OSError:
                pass
            raise
        if proc.returncode != 0:
            raise RelaisSansPlafond(f"porte de plafond : code {proc.returncode} : " + caviarder(err.decode("utf-8", "replace"))[0][:300])
        lignes = [l for l in sortie.decode("utf-8", "replace").splitlines() if l.strip()]
        try:
            objet = json.loads(lignes[-1]) if lignes else None
        except ValueError:
            objet = None
        if not isinstance(objet, dict) or objet.get("etape") != etape:
            raise RelaisSansPlafond("porte de plafond : accusé illisible ou d'une autre étape (ligne JSON {etape, plafond_usd} exigée)")
        v = objet.get("plafond_usd")
        if isinstance(v, bool) or not isinstance(v, (int, float)) or centimes(v) != centimes(p):
            raise RelaisSansPlafond(f"porte de plafond : le relais accuse {v!r} USD, pas le plafond dur {p:.2f} USD (au centime)")
        return {"etape": etape, "plafond_usd": p, "par": "commande de l'opérateur (relais relancé)"}

    def description(self):
        from .outils import sha256_fichier
        return {"type": self.type, "commande": list(self.commande), "delai_s": self.delai_s,
                "empreintes": {c: sha256_fichier(c) for c in self.commande if os.path.isfile(c)}}


def porte_depuis_configuration(nom, decl, adaptateur):
    """`fournisseurs.<nom>.porte_plafond` : {"type": "commande", "commande": [...], "delai_s": N} ou {"type": "environnement"}
    (commande externe seulement). Lève `RelaisSansPlafond` (A15) sinon."""
    if not isinstance(decl, dict):
        raise RelaisSansPlafond(f"A15 : fournisseurs.{nom}.porte_plafond manquant : relais incapable de recevoir le plafond dur au "
                                "lancement de chaque étape (DEP4)")
    if decl.get("type") == "commande":
        return PortePlafondCommande(decl.get("commande"), decl.get("delai_s"))
    if decl.get("type") == "environnement":
        return PortePlafondEnvironnement(adaptateur)
    raise RelaisSansPlafond(f"A15 : fournisseurs.{nom}.porte_plafond.type inconnu : {decl.get('type')!r} (commande, environnement)")


# --- CL20-06 : liste de lecture interdite du bac ------------------------------------------------------------------------------


def _sous(chemin, racine):
    chemin, racine = os.path.realpath(chemin), os.path.realpath(racine)
    return chemin == racine or chemin.startswith(racine.rstrip(os.sep) + os.sep)


def verifier_lecture_interdite(adaptateur, sortie, racine_sessions):
    """Pour un adaptateur du kit : rend {rôle: denyRead} si la liste interdit la sortie et le coffre pour chaque rôle du pôle ;
    lève `LectureNonInterdite` sinon. Autres adaptateurs : None (aucun bac du kit)."""
    if not isinstance(adaptateur, AdaptateurClaudeSDK):
        return None
    sonde = os.path.join(racine_sessions, "sonde-lecture-v56")
    sortie_vue = {}
    for role in ROLES_KIT_DU_POLE:
        try:
            o = construire_options(sonde, 1.0, 1, url_relais=adaptateur.url_relais, role=role,
                                   interdire_lecture=adaptateur.interdire_lecture)
        except ValueError as e:
            raise LectureNonInterdite(f"CL20-06 : liste de lecture interdite refusée pour {role} : {e}") from None
        refus = o["sandbox"]["filesystem"]["denyRead"]
        for cible in (sortie, os.path.join(sortie, "coffre")):
            if not any(_sous(cible, d) for d in refus):
                raise LectureNonInterdite(f"CL20-06 : la sortie ({cible}) n'est pas interdite en lecture au bac du rôle {role} "
                                          f"(denyRead = {refus}) : passer interdire_lecture=[base des sessions, sortie]")
            if any(_sous(cible, a) for a in o["sandbox"]["filesystem"]["allowRead"]):
                raise LectureNonInterdite(f"CL20-06 : la sortie ({cible}) est rouverte en lecture au rôle {role}")
        sortie_vue[role] = list(refus)
    return sortie_vue


__all__ = ("AdaptateurCommandeExterneV56", "PortePlafondNoyau", "PortePlafondEnvironnement", "PortePlafondCommande",
           "porte_depuis_configuration", "est_adaptateur_reel", "verifier_lecture_interdite", "RelaisSansPlafond",
           "LectureNonInterdite")
