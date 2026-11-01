"""Plafond S17 et règle d'A1, version 54 — au-dessus de `budget_v53` (règle d'A1 inchangée, jouée mot pour mot).

Corrections (CL18-02, CL18-16, CL18-01) :

- **Coupure signalée** : `apres_etape(nom, coût, coupee=…)`. Une étape au cours de laquelle l'orchestrateur a rencontré un
  reste de budget nul (appel non lancé, fiche non jugée, lecture sautée) est **coupée** : protégée → « non mesurée
  (budget) », C13 non satisfaite ; retirable → retirée ; protégée hors porte (M6b) → « non mesurée hors porte », réserve,
  C13 inchangée (brouillon 7, M6b : « si elle ne tient pas sous S17, M6b non mesurée (budget), réserve écrite, C13
  inchangée »). Le test de coupure par le coût est `cumul ≥ plafond − EPS` (un cumul pile au plafond est une coupure dès
  qu'un travail restait).
- **Cumul jamais écrêté** : le coût réel est compté en entier ; un dépassement de S17 (relais qui n'a pas coupé) est écrit
  au journal (`depassement_s17_usd`), jamais effacé.
- **Non mesurée (technique)** (A14) : `marquer_technique(nom)` après l'étape ; même conséquence que « non mesurée (budget) »
  pour C13, cause distincte.
- **Rejeu sur les seules consommations** (A21, garde R5 ligne 30) : `rejouer_consommations` reçoit la liste des
  consommations **telle que le coffre la rend** (une entrée par appel, plus les marques de coupure, montants seuls) et rejoue
  les décisions ; l'essai compare au journal réel du run.
"""

from .budget_v53 import EPS, JOUER, NON_LANCEE_HORS_PORTE, NON_MESUREE, RETIREE, Budget, BudgetRefuse
from .configuration_v53 import reel

VERSION = "budget-a1-v54"
NON_MESUREE_HORS_PORTE = "non_mesuree_hors_porte"
NON_MESUREE_TECHNIQUE = "non_mesuree_technique"
__all__ = ("BudgetV54", "rejouer_consommations", "JOUER", "RETIREE", "NON_MESUREE", "NON_LANCEE_HORS_PORTE",
           "NON_MESUREE_HORS_PORTE", "NON_MESUREE_TECHNIQUE", "BudgetRefuse")


class BudgetV54(Budget):
    def apres_etape(self, nom, cout_reel_usd, coupee=False):
        e = self.etapes[nom]
        if e["etat"] != "en_cours":
            raise BudgetRefuse(f"étape {nom} non lancée : aucun coût à compter")
        if not reel(cout_reel_usd, 0):
            raise BudgetRefuse(f"coût réel : réel ≥ 0 (reçu {cout_reel_usd!r})")
        avant = self.cumul
        self.cumul += float(cout_reel_usd)  # jamais écrêté (CL18-16)
        depasse_reservation = float(cout_reel_usd) > self._reservation(e) + EPS
        depassement = max(0.0, self.cumul - self.plafond)
        coupee_cout = self.cumul >= self.plafond - EPS and (coupee or self.cumul > self.plafond + EPS)
        if coupee or coupee_cout:
            if e["role"] == "sacrifiable":
                e["etat"] = RETIREE
            elif e["role"] == "protegee_hors_porte":
                e["etat"] = NON_MESUREE_HORS_PORTE
            else:
                e["etat"] = NON_MESUREE
            self._consigner("coupee", nom, cout_usd=round(float(cout_reel_usd), 6), cumul_avant_usd=round(avant, 6),
                            depassement_s17_usd=round(depassement, 6), signalee=bool(coupee), etat=e["etat"])
            return e["etat"]
        e["etat"] = "jouee"
        self._consigner("jouee", nom, cout_usd=round(float(cout_reel_usd), 6), au_dela_de_la_reservation=depasse_reservation)
        return "jouee"

    def marquer_technique(self, nom, motif):
        """A14 : étape jouée dont un rôle a dépassé la part d'appels sans sortie exploitable."""
        e = self.etapes[nom]
        e["etat"] = NON_MESUREE_TECHNIQUE
        self._consigner(NON_MESUREE_TECHNIQUE, nom, motif=str(motif)[:300])
        return e["etat"]

    def etat(self):
        d = super().etat()
        d["version"] = VERSION
        d["c13_budget_satisfaite"] = not any(self.etapes[n]["etat"] == NON_MESUREE for n in self.ordre)
        d["c13_technique_satisfaite"] = not any(self.etapes[n]["etat"] == NON_MESUREE_TECHNIQUE for n in self.ordre)
        d["c13_satisfaite"] = d["c13_budget_satisfaite"] and d["c13_technique_satisfaite"]
        d["reserves_hors_porte"] = [n for n in self.ordre if self.etapes[n]["etat"] in (NON_MESUREE_HORS_PORTE, NON_LANCEE_HORS_PORTE)]
        d["depassement_s17_usd"] = round(max(0.0, self.cumul - self.plafond), 6)
        return d

    def decisions(self):
        """Le journal réduit aux décisions (ce que le rejeu doit retrouver)."""
        return [(j["quoi"], j["etape"]) for j in self.journal]


def rejouer_consommations(plafond_usd, arret_etape_usd, etapes, consommations):
    """Rejoue la règle d'A1 sur les consommations rendues par le coffre (`Coffre.consommations()`) : coût par étape = somme
    des `cout_usd` de ses entrées ; coupure = une entrée `coupure: true` de l'étape. Les entrées ne portent que des montants
    (le coffre refuse toute consommation qui porte un verdict). Rend (décisions, état)."""
    couts, coupees, techniques = {}, set(), {}
    for c in consommations:
        if not isinstance(c, dict) or "etape" not in c or not reel(c.get("cout_usd"), 0):
            raise BudgetRefuse(f"consommation illisible pour le rejeu : {c!r}")
        couts[c["etape"]] = couts.get(c["etape"], 0.0) + float(c["cout_usd"])
        if c.get("coupure"):
            coupees.add(c["etape"])
        if c.get("technique"):
            techniques[c["etape"]] = c.get("motif", "A14")
    b = BudgetV54(plafond_usd, arret_etape_usd, etapes)
    for nom in b.ordre:
        d, _ = b.avant_etape(nom)
        if d == JOUER:
            etat = b.apres_etape(nom, couts.get(nom, 0.0), coupee=nom in coupees)
            if nom in techniques and etat == "jouee":
                b.marquer_technique(nom, techniques[nom])
        if not b.etat()["c13_satisfaite"]:
            break  # nœud : l'orchestrateur s'arrête au premier « non mesuré » (CL18-02) ; le rejeu aussi
    return b.decisions(), b.etat()
