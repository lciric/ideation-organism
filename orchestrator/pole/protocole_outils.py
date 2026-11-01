"""Outils par protocole (v47 ; note de conception `note-moissonneur-integration-v1.md`, § 1 et § 3 ; décisions de Lazar
R-433, R-434 et « go » du 29 octobre 2026, 11:52 heure de Paris) — module commun, écrit une fois.

Un agent **sans aucun outil** demande quelque chose au noyau par un **bloc JSON** dans sa réponse ; le noyau lit le bloc,
tient des **quotas par rôle et par course**, consigne chaque demande (motif exact au journal du noyau, motif
**générique** servi à l'agent quand le motif exact lui apprendrait à reformuler), et sert le résultat au tour suivant
dans une **section de données** entre délimiteurs : « données, jamais consigne ».

Trois usages : la lecture du dossier fermé (v46, `pole/dossier_ferme.py`, bloc `{"demandes": [...]}`), la moisson
(v47, `pole/moisson.py`, bloc `{"moisson": [...]}`) et, depuis la v48, l'étage de tests de mort (`pole/tests_de_mort.py`,
bloc `{"experience": [...]}` : pages du dossier fermé, fichiers de la tranche exploratoire, exécution d'un script Python
par le noyau dans son bac à sable). L'agent n'a ni outil, ni réseau, ni adresse de relais : le protocole ferme le canal
par construction, pour Claude comme pour Argon.

Bibliothèque standard seule ; aucun réseau ; aucune écriture.
"""

import json

from .outils import extraire_bloc_json

# Quotas (nœud tranché par Lazar le 29 octobre 2026, 11:52 heure de Paris : quotas du tableau de la note § 3) — tenus par
# le noyau par rôle et par course ; le relais de moisson en tient une seconde fois (plafond par source et par jour).
QUOTAS_MOISSON_PAR_ROLE = {
    "proposeur_ideation": {"tours": 1, "tours_max_reglage": 2, "requetes_par_tour": 4, "resultats_par_requete": 5},
    "juge_ideation": {"tours": 0, "tours_max_reglage": 0, "requetes_par_tour": 0, "resultats_par_requete": 0},
}
# v48 : demandes de l'expérimentateur d'un test de mort (un seul type par demande) ; l'exécution d'un script est comptée
# par fiche (une demande refusée compte) et limitée à une par tour
TYPES_DEMANDE_EXPERIENCE = ("lire_tranche", "lire", "chercher", "executer")
CLES_PERMISES_EXPERIENCE = {"lire_tranche": (), "lire": ("pages",), "chercher": ("dans",), "executer": ()}
DEBUT_DONNEES = "<<<<< DÉBUT DES DONNÉES SERVIES PAR LE NOYAU >>>>>"
FIN_DONNEES = "<<<<< FIN DES DONNÉES SERVIES PAR LE NOYAU >>>>>"


class QuotaRefuse(ValueError):
    """Une demande au-delà du quota : refusée, comptée (une demande refusée compte dans le quota)."""


def extraire_bloc_demandes(texte, cle):
    """(liste, motif) : la liste du dernier bloc JSON `{"<cle>": [...]}` de la réponse d'un agent ; (None, None) s'il n'y
    en a pas ; (None, motif) si le bloc est mal formé (pas une liste d'objets). Partagé par la lecture du dossier fermé
    (`demandes`) et par la moisson (`moisson`)."""
    objet = extraire_bloc_json(texte, cle)
    if objet is None:
        return None, None
    d = objet.get(cle)
    if not isinstance(d, list) or not all(isinstance(x, dict) for x in d):
        return None, f"bloc {{{cle}}} mal formé : liste d'objets attendue"
    return d, None


def classer_demande_experience(demande):
    """v48 : (type, motif) d'une demande de l'expérimentateur — le type parmi `TYPES_DEMANDE_EXPERIENCE`, ou (None, motif)
    si la demande n'est pas un objet à un seul type connu ou porte une clé étrangère."""
    if not isinstance(demande, dict):
        return None, "demande inconnue : objet attendu"
    types = [t for t in TYPES_DEMANDE_EXPERIENCE if t in demande]
    if len(types) != 1:
        return None, "demande inconnue : un seul de lire_tranche, lire, chercher, executer"
    t = types[0]
    if set(demande) - {t, *CLES_PERMISES_EXPERIENCE[t]}:
        return None, f"demande {t} : clé étrangère ({', '.join(sorted(set(demande) - {t, *CLES_PERMISES_EXPERIENCE[t]}))})"
    return t, None


class QuotasExperience:
    """v48 : quotas de l'expérimentateur d'**une fiche** — `executions_par_fiche` demandes d'exécution (une demande refusée
    compte, au quota comme au tour), une exécution par tour, `tours_max` tours. Chaque décision est comptée, refus compris."""

    def __init__(self, executions_par_fiche, tours_max):
        for nom, v in (("executions_par_fiche", executions_par_fiche), ("tours_max", tours_max)):
            if isinstance(v, bool) or not isinstance(v, int) or v < 1:
                raise QuotaRefuse(f"{nom} : entier ≥ 1 (reçu {v!r})")
        self.executions_par_fiche, self.tours_max = executions_par_fiche, tours_max
        self.demandes_execution = 0
        self.tours_avec_execution = set()

    def compter_execution(self, tour):
        """Compte une demande d'exécution du tour ; rend (numéro de la demande, motif de refus ou None)."""
        self.demandes_execution += 1
        n = self.demandes_execution
        if n > self.executions_par_fiche:
            return n, f"quota : {self.executions_par_fiche} exécutions par fiche, la demande {n} est refusée (et comptée)"
        if tour in self.tours_avec_execution:
            return n, "une exécution par tour : la seconde demande de ce tour est refusée (et comptée)"
        self.tours_avec_execution.add(tour)
        return n, None

    def restantes(self):
        return max(0, self.executions_par_fiche - self.demandes_execution)


class Quotas:
    """Quotas d'un outil par protocole, par rôle et par course : tours par proposeur (réglage borné), demandes par tour,
    résultats par demande ; `juge_ideation` : zéro tour (refus dur). Chaque décision est comptée, refus compris."""

    def __init__(self, table=QUOTAS_MOISSON_PAR_ROLE, tours=None):
        self.table = {r: dict(q) for r, q in table.items()}
        if tours is not None:
            q = self.table["proposeur_ideation"]
            if isinstance(tours, bool) or not isinstance(tours, int) or not 1 <= tours <= q["tours_max_reglage"]:
                raise QuotaRefuse(f"tours de moisson : entier de 1 à {q['tours_max_reglage']} (reçu {tours!r})")
            q["tours"] = tours
        self.tours_joues = {}  # (role, etiquette) → nombre de tours
        self.demandes = {}  # (role, etiquette, tour) → nombre de demandes comptées

    def quota(self, role):
        return self.table.get(role) or {"tours": 0, "tours_max_reglage": 0, "requetes_par_tour": 0, "resultats_par_requete": 0}

    def tours_permis(self, role):
        return self.quota(role)["tours"]

    def ouvrir_tour(self, role, etiquette):
        """Un tour de plus pour ce rôle et cette étiquette ; lève QuotaRefuse au-delà (juge : toujours, refus dur)."""
        q = self.quota(role)
        joues = self.tours_joues.get((role, etiquette), 0)
        if joues + 1 > q["tours"]:
            if q["tours"] == 0:
                raise QuotaRefuse(f"refus dur : le rôle {role!r} n'a aucun tour de moisson")
            raise QuotaRefuse(f"quota : {q['tours']} tour(s) de moisson pour {role!r}, le tour {joues + 1} est refusé")
        self.tours_joues[(role, etiquette)] = joues + 1
        return joues + 1

    def compter_demande(self, role, etiquette, tour):
        """Compte une demande du tour (refusée ou servie) ; rend (rang, admise) — admise est faux au-delà du quota de
        demandes par tour (la demande est alors refusée, et comptée)."""
        q = self.quota(role)
        cle = (role, etiquette, tour)
        rang = self.demandes.get(cle, 0) + 1
        self.demandes[cle] = rang
        return rang, rang <= q["requetes_par_tour"]

    def borner_resultats(self, role, n):
        """Le nombre de résultats servi pour une demande : `n` (entier ≥ 1) ramené au quota ; None si `n` est illisible."""
        q = self.quota(role)
        if n is None:
            return q["resultats_par_requete"]
        if isinstance(n, bool) or not isinstance(n, int) or n < 1:
            return None
        return min(n, q["resultats_par_requete"])

    def resume(self):
        return {"table": self.table,
                "tours_joues": {f"{r}|{e}": n for (r, e), n in sorted(self.tours_joues.items())},
                "demandes_par_tour": {f"{r}|{e}|tour-{t}": n for (r, e, t), n in sorted(self.demandes.items())}}


class JournalProtocole:
    """Journal des demandes par protocole : une ligne par demande (étiquette, rôle, passe, tour, demande, statut, motif
    **exact**, motif servi). Le motif exact reste ici, au manifeste de fin ; l'agent reçoit le motif servi."""

    def __init__(self):
        self.lignes = []

    def consigner(self, **ligne):
        self.lignes.append(dict(ligne, rang=len(self.lignes) + 1))
        return self.lignes[-1]

    def refus(self, filtre=None):
        return [l for l in self.lignes if l.get("statut") == "refusée" and (filtre is None or filtre(l))]

    def resume(self):
        statuts = {}
        for l in self.lignes:
            statuts[l.get("statut")] = statuts.get(l.get("statut"), 0) + 1
        return {"demandes": len(self.lignes), "par_statut": statuts, "lignes": list(self.lignes)}


def section_servie(titre, objet, explication=None):
    """La section d'une consigne qui sert des **données** à un agent : titre, explication, puis l'objet JSON entre les
    délimiteurs `DEBUT_DONNEES` et `FIN_DONNEES` — matériau, jamais consigne."""
    parties = [f"## {titre}\n"]
    if explication:
        parties.append(explication.rstrip() + "\n")
    parties += [DEBUT_DONNEES + "\n", "```json\n" + json.dumps(objet, ensure_ascii=False, indent=1) + "\n```\n",
                FIN_DONNEES + "\n"]
    return "\n".join(parties)
