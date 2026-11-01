"""Plafond S17 et règle d'A1, version 56 — **relais du devis v6** (préenregistrement du pré-pilote, brouillon 10 : Plan, « Sacrifice
à plafond atteint — règle d'A1 » ; A1, A15, DEP4 ; table R5, lignes 11a et 11b ; GO-2026-10-31-03 : « plafonds de relais du
brouillon 5 gardés, souples pour les étapes protégées »). Corrige CL20-02 : la v55 jouait la règle « réservation » du brouillon 7.

Paramètres injectés, aucun défaut : S17 (plafond, arrêt d'étape) ; par étape `attendu_usd` (attendu aux bases du devis v6),
`plafond_relais_usd` (plafond de relais du brouillon 5) et, pour l'étape réductible, `reduite: {attendu_usd, plafond_relais_usd}`.
La clé `reservation_usd` est **refusée** (règle « réservation » sans objet, brouillon 10, DEP4).

Avant chaque étape E non retirée, dans l'ordre du plan :

1. **Projection** = cumul + plafond de relais de E + attendu aux bases des étapes restantes non retirées ; tant qu'elle dépasse
   S17, on prend la prochaine mesure de la liste de sacrifice non encore jouée (rang croissant) : étape sacrifiable retirée,
   étape réductible réduite (une fois).
2. **Arrêt d'étape** : si le cumul l'atteint, les étapes sacrifiables non jouées sont retirées et l'étape réductible non jouée est
   réduite ; rien de protégé ne change.
3. **Plafond** : si cumul + plafond de relais de E dépasse S17 : E sacrifiable retirée ; E réductible non réduite réduite puis
   réexaminée ; E réductible réduite, ou protégée : non lancée, « non mesuré (budget) », C13 ; E protégée hors porte (M6b) : non
   lancée, réserve, C13 inchangée.
4. **Lancement** : le relais de E reçoit un **plafond dur fixé au lancement**, qui ne change plus pendant E —
   E protégée (M6 réduite et M6b comprises) : max(plafond de relais de E ; S17 − cumul − attendu aux bases des étapes
   restantes non retirées) ; E retirable (sacrifiable, et M6 entière) : son plafond de relais, fixe. Arrondi au centime
   **inférieur** (le plafond transmis au relais et celui que tient l'orchestrateur sont le même nombre de centimes) ; le test 3
   garantit cumul + plafond dur ≤ S17.

Après E (coût réel compté en entier, jamais écrêté) : E est **coupée** si l'orchestrateur a rencontré un reste nul sous le
plafond dur (appel non lancé) ou si le coût dépasse le plafond dur (relais qui n'a pas coupé). Statuts (ligne 11b) : protégée
coupée → « non mesuré (budget) », C13 ; sacrifiable coupée → retirée, dépense comptée ; M6 entière coupée → **lue réduite** si
les fiches de la réduction stratifiée, vérifiées en premier, l'ont toutes été avant la coupure (`lue_reduite=True`, dit par
l'étape), sinon « non mesuré (budget) » (silence = « non mesuré », jamais un repli) ; M6 réduite coupée → « non mesuré
(budget) » ; M6b coupée → réserve, C13 inchangée. Un coût au-delà du plafond de relais sous le plafond dur (souplesse utilisée)
est une réserve de M7, pas une coupure.

`rejouer_consommations_v56` est le **second programme** de la ligne 11a : il rejoue décisions **et plafonds durs** sur les seules
consommations rendues par le coffre ; l'orchestrateur compare, au centime, le plafond qu'il va transmettre à celui que ce
programme recalcule. Les décisions ne lisent que des montants (A21).
"""

import math

from .budget_v53 import EPS, JOUER, NON_LANCEE_HORS_PORTE, NON_MESUREE, RETIREE, Budget, BudgetRefuse
from .budget_v54 import NON_MESUREE_HORS_PORTE, NON_MESUREE_TECHNIQUE
from .configuration_v53 import entier, reel

VERSION = "budget-a1-v56 (relais du devis v6, brouillon 10)"
REGLE = ("A1 du brouillon 10 (relais du devis v6, GO-2026-10-31-03) : projection et plafond avec le plafond de relais ; au "
         "lancement, plafond dur = max(plafond de relais ; S17 − cumul − attendu aux bases des étapes restantes non retirées) "
         "pour une étape protégée, plafond de relais fixe pour une étape retirable ; fixé au lancement, transmis à chaque relais")
ROLES = ("protegee", "sacrifiable", "reductible", "protegee_hors_porte")
__all__ = ("BudgetV56", "rejouer_consommations_v56", "verifier_etapes_v56", "centimes", "centime_bas", "statut_attendu_coupure",
           "verifier_plafonds_transmis", "plafond_independant", "verifier_cumul", "PlafondDeRelaisFaux", "CumulAuDelaDeS17", "JOUER", "RETIREE",
           "NON_MESUREE", "NON_LANCEE_HORS_PORTE", "NON_MESUREE_HORS_PORTE", "NON_MESUREE_TECHNIQUE", "BudgetRefuse", "REGLE")


class PlafondDeRelaisFaux(RuntimeError):
    """Ligne 11a : plafond transmis différent, au centime, de celui que recalcule le second programme ; plafond changé pendant
    l'étape ; plafond souple donné à une étape retirable."""


class CumulAuDelaDeS17(RuntimeError):
    """Ligne 11a : cumul au-delà de S17 (un relais n'a pas tenu son plafond dur) : arrêt."""


def centime_bas(x):
    """Arrondi au centime inférieur (tolérance d'arrondi binaire 1e-6 centime)."""
    return math.floor(float(x) * 100 + 1e-6) / 100


def centimes(x):
    """Nombre entier de centimes (comparaison « au centime »)."""
    return int(math.floor(float(x) * 100 + 1e-6))


def verifier_etapes_v56(etapes):
    """Liste des manques du plan de dépense v56 (vide si conforme)."""
    manques, noms = [], set()
    if not isinstance(etapes, list) or not etapes:
        return ["budget.etapes : liste non vide exigée"]
    for i, e in enumerate(etapes):
        if not isinstance(e, dict):
            manques.append(f"budget.etapes[{i}] : objet attendu")
            continue
        if not isinstance(e.get("nom"), str) or not e["nom"] or e["nom"] in noms:
            manques.append(f"budget.etapes[{i}].nom : chaîne unique exigée")
        noms.add(e.get("nom"))
        if "reservation_usd" in e or "reservation_usd" in (e.get("reduite") or {}):
            manques.append(f"budget.etapes[{i}] : reservation_usd refusée (règle « réservation » du brouillon 7, sans objet au "
                           "brouillon 10 : plafond_relais_usd exigé, CL20-02)")
        for c in ("attendu_usd", "plafond_relais_usd"):
            if not reel(e.get(c), 0):
                manques.append(f"budget.etapes[{i}].{c} : réel ≥ 0 exigé (aucun défaut)")
        if e.get("role") not in ROLES:
            manques.append(f"budget.etapes[{i}].role ∈ {ROLES}")
        if e.get("role") in ("sacrifiable", "reductible") and not entier(e.get("rang"), 1):
            manques.append(f"budget.etapes[{i}].rang : entier ≥ 1 exigé (étape {e.get('role')})")
        if e.get("role") == "reductible":
            r = e.get("reduite")
            if not isinstance(r, dict) or not reel(r.get("attendu_usd"), 0) or not reel(r.get("plafond_relais_usd"), 0):
                manques.append(f"budget.etapes[{i}].reduite : {{attendu_usd, plafond_relais_usd}} exigés")
    rangs = [e.get("rang") for e in etapes if isinstance(e, dict) and e.get("role") in ("sacrifiable", "reductible")]
    if len(set(rangs)) != len(rangs):
        manques.append("budget.etapes : rangs de sacrifice en double")
    return manques


def statut_attendu_coupure(role, reduite, lue_reduite):
    """Ligne 11b : le statut écrit au Plan (règle d'A1, point 4) pour une étape coupée par son relais."""
    if role == "sacrifiable":
        return RETIREE
    if role == "protegee_hors_porte":
        return NON_MESUREE_HORS_PORTE
    if role == "reductible" and not reduite:
        return "jouee" if lue_reduite is True else NON_MESUREE
    if role in ("protegee", "reductible"):
        return NON_MESUREE
    raise BudgetRefuse(f"rôle d'étape inconnu : {role!r}")


class BudgetV56(Budget):
    def __init__(self, plafond_usd, arret_etape_usd, etapes):
        manques = verifier_etapes_v56(etapes)
        if manques:
            raise BudgetRefuse("plan de dépense v56 refusé :\n- " + "\n- ".join(manques))
        super().__init__(plafond_usd, arret_etape_usd, etapes)
        for e in self.etapes.values():
            e["plafond_dur_usd"] = None

    # --- lectures -----------------------------------------------------------------------------------------------------------

    def _plafond_relais(self, e):
        return float(e["reduite"]["plafond_relais_usd"] if e["reduite_appliquee"] else e["plafond_relais_usd"])

    def _reservation(self, e):  # la projection de la v53 (cumul + ceci + attendus) est celle du brouillon 10 avec le relais
        return self._plafond_relais(e)

    @staticmethod
    def retirable(e):
        return e["role"] == "sacrifiable" or (e["role"] == "reductible" and not e["reduite_appliquee"])

    def attendu_restantes(self, nom):
        return sum(self._attendu(r) for r in self._restantes_apres(nom))

    def plafond_dur(self, nom):
        """(plafond dur au centime inférieur, souple ?) au lancement de `nom` (Plan, règle d'A1, point 4)."""
        e = self.etapes[nom]
        relais = self._plafond_relais(e)
        if self.retirable(e):
            return centime_bas(relais), False
        return centime_bas(max(relais, self.plafond - self.cumul - self.attendu_restantes(nom))), True

    # --- la règle -----------------------------------------------------------------------------------------------------------

    def avant_etape(self, nom):
        e = self.etapes[nom]
        if e["etat"] == RETIREE:
            return RETIREE, {"motif": "retirée plus tôt par la règle d'A1"}
        if e["etat"] != "a_jouer":
            raise BudgetRefuse(f"étape {nom} déjà {e['etat']} : jamais rejouée")
        while self.projection(nom) > self.plafond + EPS:  # 1. projection (avec le plafond de relais de E)
            m = self._prochaine_mesure()
            if m is None:
                break
            self._appliquer(m, "projection (cumul + plafond de relais + attendu aux bases des restantes) au-dessus de S17")
            if e["etat"] == RETIREE:
                return RETIREE, {"motif": "retirée par la projection (règle d'A1, 1)"}
        if self.arret is not None and self.cumul + EPS >= self.arret:  # 2. arrêt d'étape
            if not self.arret_touche:
                self._consigner("arret_etape_touche", nom, arret_usd=self.arret)
            self.arret_touche = True
            for n in self.ordre:
                r = self.etapes[n]
                if r["etat"] != "a_jouer":
                    continue
                if r["role"] == "sacrifiable" or (r["role"] == "reductible" and not r["reduite_appliquee"]):
                    self._appliquer(r, "arrêt d'étape atteint")
            if e["etat"] == RETIREE:
                return RETIREE, {"motif": "retirée à l'arrêt d'étape (règle d'A1, 2)"}
        while self.cumul + self._plafond_relais(e) > self.plafond + EPS:  # 3. plafond
            if e["role"] == "sacrifiable":
                self._appliquer(e, "cumul + plafond de relais au-dessus de S17")
                return RETIREE, {"motif": "retirée au plafond (règle d'A1, 3)"}
            if e["role"] == "reductible" and not e["reduite_appliquee"]:
                self._appliquer(e, "cumul + plafond de relais au-dessus de S17")
                continue
            if e["role"] == "protegee_hors_porte":
                e["etat"] = NON_LANCEE_HORS_PORTE
                self._consigner(NON_LANCEE_HORS_PORTE, nom)
                return NON_LANCEE_HORS_PORTE, {"motif": "étape protégée hors porte non lancée : réserve, C13 inchangée"}
            e["etat"] = NON_MESUREE
            self._consigner(NON_MESUREE, nom, motif="ne tient pas sous S17 (non lancée)")
            return NON_MESUREE, {"motif": "étape protégée (ou M6 réduite) qui ne tient pas sous S17 : non mesuré (budget), C13"}
        relais = self._plafond_relais(e)  # 4. lancement, plafond dur fixé ici
        dur, souple = self.plafond_dur(nom)
        e["etat"], e["plafond_dur_usd"] = "en_cours", dur
        self._consigner("lancee", nom, plafond_relais_usd=round(relais, 6), plafond_dur_usd=dur, souple=souple,
                        reduite=e["reduite_appliquee"], attendu_restantes_usd=round(self.attendu_restantes(nom), 6))
        return JOUER, {"plafond_dur_usd": dur, "plafond_relais_usd": round(relais, 6), "souple": souple,
                       "reduite": e["reduite_appliquee"], "reste_avant_plafond_usd": round(self.plafond - self.cumul, 6)}

    def apres_etape(self, nom, cout_reel_usd, coupee=False, lue_reduite=None):
        e = self.etapes[nom]
        if e["etat"] != "en_cours":
            raise BudgetRefuse(f"étape {nom} non lancée : aucun coût à compter")
        if not reel(cout_reel_usd, 0):
            raise BudgetRefuse(f"coût réel : réel ≥ 0 (reçu {cout_reel_usd!r})")
        avant, cout = self.cumul, float(cout_reel_usd)
        self.cumul += cout  # jamais écrêté
        dur = e["plafond_dur_usd"]
        depassement = max(0.0, self.cumul - self.plafond)
        if bool(coupee) or cout > dur + EPS:
            etat = statut_attendu_coupure(e["role"], e["reduite_appliquee"], lue_reduite)
            if etat == "jouee":  # M6 entière coupée après ses fiches de réduction : lue réduite
                e["reduite_appliquee"] = True
            e["etat"] = etat
            self._consigner("coupee", nom, cout_usd=round(cout, 6), cumul_avant_usd=round(avant, 6), plafond_dur_usd=dur,
                            depassement_s17_usd=round(depassement, 6), signalee=bool(coupee), etat=etat,
                            lue_reduite=lue_reduite if e["role"] == "reductible" else None)
            return etat
        e["etat"] = "jouee"
        self._consigner("jouee", nom, cout_usd=round(cout, 6), plafond_dur_usd=dur,
                        au_dela_du_plafond_de_relais=cout > self._plafond_relais(e) + EPS)
        return "jouee"

    def refuser_lancement(self, nom, motif):
        """A15 : un relais n'a pas reçu le plafond dur ; l'étape n'est pas jouée (rien n'est dépensé) et l'exécution s'arrête."""
        e = self.etapes[nom]
        e["etat"] = NON_MESUREE
        self._consigner("relais_sans_plafond", nom, motif=str(motif)[:300])
        return e["etat"]

    def marquer_technique(self, nom, motif):
        e = self.etapes[nom]
        e["etat"] = NON_MESUREE_TECHNIQUE
        self._consigner(NON_MESUREE_TECHNIQUE, nom, motif=str(motif)[:300])
        return e["etat"]

    def etat(self):
        d = super().etat()
        d["version"] = VERSION
        d["regle"] = REGLE
        d["c13_budget_satisfaite"] = not any(self.etapes[n]["etat"] == NON_MESUREE for n in self.ordre)
        d["c13_technique_satisfaite"] = not any(self.etapes[n]["etat"] == NON_MESUREE_TECHNIQUE for n in self.ordre)
        d["c13_satisfaite"] = d["c13_budget_satisfaite"] and d["c13_technique_satisfaite"]
        d["reserves_hors_porte"] = [n for n in self.ordre if self.etapes[n]["etat"] in (NON_MESUREE_HORS_PORTE, NON_LANCEE_HORS_PORTE)]
        d["depassement_s17_usd"] = round(max(0.0, self.cumul - self.plafond), 6)
        d["plafonds_durs_usd"] = {n: self.etapes[n]["plafond_dur_usd"] for n in self.ordre if self.etapes[n]["plafond_dur_usd"] is not None}
        return d

    def decisions(self):
        return [(j["quoi"], j["etape"]) for j in self.journal]


def rejouer_consommations_v56(plafond_usd, arret_etape_usd, etapes, consommations, jusqu_a=None):
    """Second programme (ligne 11a) : rejoue la règle d'A1 v56 sur les consommations rendues par le coffre — coût par étape
    (somme des `cout_usd`), coupure (`coupure: true`), lecture réduite de M6 entière coupée (`lue_reduite`), A14
    (`technique: true`). Rend (décisions, état, plafonds durs par étape lancée). Avec `jusqu_a`, s'arrête au lancement de cette
    étape (son plafond dur est rendu, rien n'est compté pour elle)."""
    couts, coupees, techniques, lues = {}, set(), {}, {}
    for c in consommations:
        if not isinstance(c, dict) or "etape" not in c or not reel(c.get("cout_usd"), 0):
            raise BudgetRefuse(f"consommation illisible pour le rejeu : {c!r}")
        couts[c["etape"]] = couts.get(c["etape"], 0.0) + float(c["cout_usd"])
        if c.get("coupure"):
            coupees.add(c["etape"])
        if c.get("technique"):
            techniques[c["etape"]] = c.get("motif", "A14")
        if "lue_reduite" in c:
            lues[c["etape"]] = c["lue_reduite"] is True
    b = BudgetV56(plafond_usd, arret_etape_usd, etapes)
    plafonds = {}
    for nom in b.ordre:
        d, detail = b.avant_etape(nom)
        if d == JOUER:
            plafonds[nom] = detail["plafond_dur_usd"]
            if nom == jusqu_a:
                break
            etat = b.apres_etape(nom, couts.get(nom, 0.0), coupee=nom in coupees, lue_reduite=lues.get(nom))
            if nom in techniques and etat == "jouee":
                b.marquer_technique(nom, techniques[nom])
        elif nom == jusqu_a:
            break
        if not b.etat()["c13_satisfaite"]:
            break  # nœud : l'orchestrateur s'arrête au premier « non mesuré » ; le rejeu aussi
    return b.decisions(), b.etat(), plafonds


def plafond_independant(etapes, plafond_usd, journal_budget, consommations, nom):
    """Second calcul du plafond dur de `nom` au lancement, **indépendant de `BudgetV56`** (formule du Plan, point 4, réécrite) :
    cumul = somme des consommations déjà notées ; étapes retirées et réduites lues aux entrées « retiree » et « reduite » du
    journal ; étapes restantes = celles qui suivent `nom` dans le plan et ne sont pas retirées. Rend (plafond au centime
    inférieur, souple ?)."""
    conf = {e["nom"]: e for e in etapes}
    ordre = [e["nom"] for e in etapes]
    retirees = {j["etape"] for j in journal_budget if j["quoi"] == "retiree"}
    reduites = {j["etape"] for j in journal_budget if j["quoi"] == "reduite"}
    cumul = sum(float(c["cout_usd"]) for c in consommations)
    e = conf[nom]
    reduite = nom in reduites
    relais = float(e["reduite"]["plafond_relais_usd"] if reduite else e["plafond_relais_usd"])
    if e["role"] == "sacrifiable" or (e["role"] == "reductible" and not reduite):
        return centime_bas(relais), False
    attendu = sum(float(conf[n]["reduite"]["attendu_usd"] if n in reduites else conf[n]["attendu_usd"])
                  for n in ordre[ordre.index(nom) + 1:] if n not in retirees)
    return centime_bas(max(relais, float(plafond_usd) - cumul - attendu)), True


def verifier_plafonds_transmis(transmissions, plafonds_recalcules):
    """Ligne 11a : `transmissions` = [{etape, plafond_usd, ...}] (ce que chaque relais a reçu) ; un seul plafond par étape (jamais
    changé pendant l'étape), égal au centime au plafond recalculé (`plafonds_recalcules` : {étape: plafond}). Lève
    `PlafondDeRelaisFaux` ; rend le nombre d'étapes vérifiées."""
    par_etape = {}
    for t in transmissions:
        par_etape.setdefault(t["etape"], set()).add(centimes(t["plafond_usd"]))
    for nom, valeurs in sorted(par_etape.items()):
        if len(valeurs) != 1:
            raise PlafondDeRelaisFaux(f"11a : plafond du relais changé pendant l'étape {nom} ({sorted(valeurs)} centimes)")
        v = next(iter(valeurs))
        if nom not in plafonds_recalcules or v != centimes(plafonds_recalcules[nom]):
            raise PlafondDeRelaisFaux(f"11a : plafond transmis pour {nom} ({v} centimes) différent du plafond recalculé "
                                      f"({plafonds_recalcules.get(nom)!r})")
    return len(par_etape)


def verifier_cumul(consommations, plafond_usd):
    """Ligne 11a : le cumul des consommations ne dépasse jamais S17."""
    total = sum(float(c["cout_usd"]) for c in consommations)
    if total > float(plafond_usd) + EPS:
        raise CumulAuDelaDeS17(f"11a : cumul {total:.6f} USD au-delà de S17 = {float(plafond_usd):g} USD : arrêt")
    return round(total, 6)
