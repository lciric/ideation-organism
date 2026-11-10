"""Lecture du registre des GO, version 66 (fichier neuf, R12 ; correction CLV65-07 de la contre-lecture du code v65).

Constat (contre-lecture `contre-lecture-code-v65-v2.md`, `c4ddfc7f…`, CLV65-07) : `configuration_v53.lire_registre_go` refuse
tout identifiant en double ; le registre réel du dépôt de travail (`registres/go.md`) porte des **lignes d'extension** qui
répètent un identifiant (R-389) ; le lanceur v65 refusait donc le registre réel (« identifiant GO-2026-10-24-07 en double »).

Ce module applique **la même règle que la garde de calcul du dépôt de travail** (`.claude/hooks/garde_calcul.py`, fonction
`lire_go`, recopiée ligne pour ligne, `bloquer` remplacé par `GoRefuse`) : une ligne qui répète un identifiant n'est admise que
si son périmètre commence par « extension » (casse ignorée), qu'elle est du même type que la première, accordée par Lazar, ni
antérieure à la première, et d'échéance non plus lointaine (les deux sans échéance, ou les deux datées et la seconde ≤ la
première) ; sinon refus. Une extension ne change ni le type ni la période de validité (ceux de la première ligne).

`verifier_go_v66` reprend ensuite les contrôles de `configuration_v55.verifier_go_v55` (identifiant exact, type « calcul »,
accordé par Lazar, période de validité, révocations, montant **exactement** égal au montant requis) avec deux règles neuves,
dites :
1. **GO cité qui porte une ou plusieurs lignes d'extension** : refus (une extension peut porter un autre plafond — le registre
   en montre, « plafond porté à … » — et la garde ne lit aucun plafond : le montant serait ambigu). Aucun des deux GO de la
   course (GO-2026-11-08-02, GO-2026-11-10-10) n'en porte au 10 novembre 2026.
2. **Enveloppe à parts nommées** (GO-2026-11-10-10 : « 120 USD (organisme 45, Bailey 75 ; aucun report) ») : si la cellule ne
   porte pas un montant seul (lecture v55), elle est lue comme `TOTAL USD (nom N, nom N[ ; texte sans nombre])` : chaque nombre
   de la parenthèse est le montant d'une part nommée, chaque nom une seule fois, la somme des parts égale au total au centime ;
   la part demandée (« organisme » par défaut, casse ignorée) doit exister et valoir **exactement** le montant requis.
   Toute autre forme : refus, motif dit. Aucun repli.
"""

import datetime
import re

from . import configuration_v53 as c53
from . import configuration_v55 as c55
from .configuration_v53 import GoRefuse, reel

VERSION = "registre-go-v66"
LIGNE_GO = c53.LIGNE_GO  # ^\|\s*(GO-\d{4}-\d{2}-\d{2}-\d{2})\s*\|  (même motif que la garde)
GO_ID = c53.GO_ID
PART_PAR_DEFAUT = "organisme"
ENVELOPPE = re.compile(r"^\s*(\d+(?:[.,]\d+)?)\s*USD\s*\(([^()]*)\)\s*$")
PART = re.compile(r"(?<![\w.,])([A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ'’-]*)\s+(\d+(?:[.,]\d+)?)(?!\d)(?![.,]\d)")
NOMBRE = re.compile(r"\d+(?:[.,]\d+)?")


def lire_registre_go_v66(chemin):
    """Table Markdown `| id | accordé le | type | périmètre | plafond | échéance | accordé par | référence |`, lue avec la règle
    de la garde de calcul (extensions admises, R-389). Rend {id: {accorde, type, echeance, par, perimetre, plafond, ref, ligne,
    extensions: [{ligne, accorde, perimetre, plafond, echeance}]}} ; lève `GoRefuse` (registre absent, ligne mal formée,
    dates illisibles, doublon qui n'est pas une extension)."""
    try:
        with open(chemin, encoding="utf-8") as f:
            lignes = f.read().splitlines()
    except OSError:
        raise GoRefuse(f"registre des GO absent ({chemin}) : aucun GO ne peut être établi") from None
    go = {}
    for n, ligne in enumerate(lignes, 1):
        if not LIGNE_GO.match(ligne):
            continue
        cellules = [c.strip() for c in ligne.strip().strip("|").split("|")]
        if len(cellules) != 8:
            raise GoRefuse(f"registre des GO mal formé ligne {n} : 8 colonnes attendues, {len(cellules)} trouvées")
        ident, accorde, typ, perimetre, plafond, echeance, par, ref = cellules
        try:
            accorde_d = datetime.date.fromisoformat(accorde)
            # « — » : sans échéance, admis seulement pour un GO qui n'est pas de calcul (règle de la garde)
            echeance_d = None if (echeance == "—" and typ != "calcul") else datetime.date.fromisoformat(echeance)
        except ValueError:
            raise GoRefuse(f"registre des GO mal formé ligne {n} : dates illisibles") from None
        if ident in go:
            premier = go[ident]
            echeance_ok = ((premier["echeance"] is None and echeance_d is None)
                           or (premier["echeance"] is not None and echeance_d is not None
                               and echeance_d <= premier["echeance"]))
            if not (perimetre.lower().startswith("extension") and typ == premier["type"] and par == "Lazar"
                    and accorde_d >= premier["accorde"] and echeance_ok):
                raise GoRefuse(f"registre des GO : identifiant {ident} en double (ligne {n}, qui n'est pas une extension admise)")
            # R-389 : la validité reste celle de la première ligne
            premier["extensions"].append({"ligne": n, "accorde": accorde_d.isoformat(), "perimetre": perimetre,
                                          "plafond": plafond, "echeance": None if echeance_d is None else echeance_d.isoformat()})
            continue
        go[ident] = {"accorde": accorde_d, "type": typ, "echeance": echeance_d, "par": par, "perimetre": perimetre,
                     "plafond": plafond, "ref": ref, "ligne": n, "extensions": []}
    return go


def _valeur(texte):
    return float(texte.replace(",", "."))


def lire_part_d_enveloppe(cellule, part):
    """(montant de la part, total, {nom: montant}) d'une cellule « TOTAL USD (nom N, nom N[ ; texte sans nombre]) » ; lève
    `GoRefuse` sur toute autre forme, sur un nombre qui n'est pas le montant d'une part nommée, sur un nom en double, sur une
    somme des parts ≠ total (au centime) et sur une part demandée absente."""
    m = ENVELOPPE.match(cellule or "")
    if not m:
        raise GoRefuse(f"A15 : plafond « {cellule} » : ni un montant seul ni une enveloppe « TOTAL USD (nom N, …) »")
    if c55.APPROX.search(cellule) or c55.PAR_UNITE.search(cellule):
        raise GoRefuse(f"A15 : plafond « {cellule} » : montant approché ou « par unité » refusé")
    total, dedans = _valeur(m.group(1)), m.group(2)
    parts = {}
    for nom, montant in PART.findall(dedans):
        cle = nom.casefold()
        if cle in parts:
            raise GoRefuse(f"A15 : enveloppe « {cellule} » : part « {nom} » nommée deux fois")
        parts[cle] = _valeur(montant)
    if len(NOMBRE.findall(dedans)) != len(parts) or not parts:
        raise GoRefuse(f"A15 : enveloppe « {cellule} » : nombre étranger aux parts nommées (ou aucune part) : refus")
    if round(sum(parts.values()) * 100) != round(total * 100):
        raise GoRefuse(f"A15 : enveloppe « {cellule} » : somme des parts {sum(parts.values()):g} ≠ total {total:g} USD")
    cle = str(part).casefold()
    if cle not in parts:
        raise GoRefuse(f"A15 : enveloppe « {cellule} » : part « {part} » absente (parts : {sorted(parts)})")
    return parts[cle], total, parts


def verifier_go_v66(go_id, registre, montant_requis_usd, part=PART_PAR_DEFAUT, aujourd_hui=None):
    """Rend la ligne de GO (dict) si elle autorise ce lancement au montant requis **exactement** ; lève `GoRefuse` sinon.
    Contrôles de `verifier_go_v55` sur le registre lu par `lire_registre_go_v66`, plus les deux règles neuves du module (GO à
    extension refusé ; part d'enveloppe nommée)."""
    if not isinstance(go_id, str) or not GO_ID.fullmatch(go_id):
        raise GoRefuse("A15 : aucun lancement sans identifiant de GO exact (GO_ID=GO-AAAA-MM-JJ-NN)")
    if not reel(montant_requis_usd, 0, strict_mini=True):
        raise GoRefuse(f"A15 : montant requis invalide {montant_requis_usd!r}")
    aujourd_hui = aujourd_hui or datetime.datetime.now(datetime.timezone.utc).date()
    reg = lire_registre_go_v66(registre)
    g = reg.get(go_id)
    if g is None:
        raise GoRefuse(f"A15 : {go_id} absent du registre {registre}")
    if g["type"] != "calcul":
        raise GoRefuse(f"A15 : {go_id} est un GO de type {g['type']!r}, pas « calcul »")
    if g["par"] != "Lazar":
        raise GoRefuse(f"A15 : {go_id} n'est pas accordé par Lazar")
    if g["echeance"] is None or not (g["accorde"] <= aujourd_hui <= g["echeance"]):
        raise GoRefuse(f"A15 : {go_id} hors de sa période de validité ({g['accorde']} → {g['echeance']})")
    revocations = sorted(k for k, r in reg.items() if r["type"] == "révocation" and (go_id in r["perimetre"] or go_id in r["ref"]))
    if revocations:
        raise GoRefuse(f"A15 : {go_id} révoqué par {', '.join(revocations)}")
    if g["extensions"]:
        raise GoRefuse(f"A15 : {go_id} porte {len(g['extensions'])} ligne(s) d'extension (lignes "
                       f"{[e['ligne'] for e in g['extensions']]}) : montant ambigu, aucune lecture (v66, règle 1)")
    requis = float(montant_requis_usd)
    try:
        valeur, unite = c55.lire_plafond(g["plafond"])
        forme, enveloppe = "montant seul", None
    except GoRefuse as e_seul:
        try:
            valeur, total, parts = lire_part_d_enveloppe(g["plafond"], part)
        except GoRefuse as e_env:
            raise GoRefuse(f"{e_seul} ; {e_env}") from None
        unite, forme, enveloppe = "USD", f"part « {part} » d'une enveloppe", {"total_usd": total, "parts_usd": parts}
    if unite.upper() not in ("USD", "$", "DOLLAR", "DOLLARS"):
        raise GoRefuse(f"A15 : la ligne {go_id} porte un montant en {unite} : USD exigé")
    if abs(valeur - requis) > 1e-9:
        raise GoRefuse(f"A15 : la ligne {go_id} porte {valeur:g} USD ({forme}), pas exactement le montant requis {requis:g} USD : "
                       "aucun lancement à un autre montant (plus petit ou plus grand)")
    return dict(g, accorde=g["accorde"].isoformat(), echeance=g["echeance"].isoformat(), identifiant=go_id, plafond_lu_usd=valeur,
                montant_requis_usd=requis, forme_du_plafond=forme, enveloppe=enveloppe, lecteur=VERSION)


__all__ = ("VERSION", "PART_PAR_DEFAUT", "GoRefuse", "lire_registre_go_v66", "lire_part_d_enveloppe", "verifier_go_v66")
