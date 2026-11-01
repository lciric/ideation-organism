"""Plafond S17, arrêt d'étape et règle de sacrifice d'A1 (v53) — paramètres injectés, aucun défaut codé.

Règle écrite une seule fois au plan d'analyse du préenregistrement du pré-pilote (brouillon 6, « Sacrifice à plafond
atteint — règle d'A1 ») et jouée ici mot pour mot, dans l'ordre des étapes donné par la configuration. Avant chaque étape E
non retirée :

1. **Projection** = cumul + réservation de E + attendu des étapes restantes non retirées ; tant qu'elle dépasse le plafond
   S17, on prend la prochaine mesure de la liste de sacrifice (étapes « sacrifiable » et « reductible », par rang croissant)
   qui n'est ni jouée ni déjà appliquée : une étape sacrifiable est retirée, une étape réductible est réduite (une fois).
2. **Arrêt d'étape** (si S17 en a un) : si le cumul l'atteint, les étapes retirables non jouées sont retirées et les étapes
   réductibles non jouées sont réduites ; rien de protégé ne change.
3. **Plafond** : si cumul + réservation de E dépasse S17 : E retirable est retirée ; E réductible non réduite est réduite puis
   réexaminée ; E réductible déjà réduite, ou E protégée, **n'est pas lancée** : « non mesuré (budget) », C13 non satisfaite ;
   E protégée hors porte n'est pas lancée : réserve, C13 inchangée.
4. Sinon E est jouée. **La réservation est une réservation** (CP5-09) : le coût réel est compté en entier ; S17 est le seul
   plafond qui coupe : si le cumul franchit S17 pendant E, E est coupée à S17 (protégée : « non mesuré (budget) » ;
   retirable : retirée). Un dépassement de la réservation sans franchir S17 est une réserve de M7, pas une coupure.

Une étape réductible n'est **jamais retirée entière** (M6, CP5-02). Les décisions ne lisent **que des consommations**
(montants) : aucune méthode ne reçoit un verdict, une note ou une clé (règle de lecture d'A21) ; `journal` permet de rejouer
les décisions sur les seules consommations (garde R5 ligne 30).
"""

from .configuration_v53 import ConfigurationRefusee, reel

VERSION = "budget-a1-v53"
JOUER, RETIREE, NON_MESUREE, NON_LANCEE_HORS_PORTE = "jouer", "retiree", "non_mesuree_budget", "non_lancee_hors_porte"
EPS = 1e-9


class BudgetRefuse(ConfigurationRefusee):
    pass


class Budget:
    def __init__(self, plafond_usd, arret_etape_usd, etapes):
        if not reel(plafond_usd, 0, strict_mini=True):
            raise BudgetRefuse(f"plafond S17 : réel > 0 exigé, aucun défaut (reçu {plafond_usd!r})")
        if arret_etape_usd != "sans" and not reel(arret_etape_usd, 0, strict_mini=True):
            raise BudgetRefuse(f"arrêt d'étape S17 : réel > 0 ou « sans », aucun défaut (reçu {arret_etape_usd!r})")
        if arret_etape_usd != "sans" and arret_etape_usd > plafond_usd:
            raise BudgetRefuse("arrêt d'étape au-dessus du plafond S17")
        if not etapes:
            raise BudgetRefuse("aucune étape")
        self.plafond = float(plafond_usd)
        self.arret = None if arret_etape_usd == "sans" else float(arret_etape_usd)
        self.ordre = [e["nom"] for e in etapes]
        self.etapes = {e["nom"]: dict(e, etat="a_jouer", reduite_appliquee=False) for e in etapes}
        self.cumul = 0.0
        self.journal = []
        self.arret_touche = False

    # --- lectures ---------------------------------------------------------------------------------------------------------

    def _attendu(self, e):
        return float(e["reduite"]["attendu_usd"] if e["reduite_appliquee"] else e["attendu_usd"])

    def _reservation(self, e):
        return float(e["reduite"]["reservation_usd"] if e["reduite_appliquee"] else e["reservation_usd"])

    def _restantes_apres(self, nom):
        i = self.ordre.index(nom)
        return [self.etapes[n] for n in self.ordre[i + 1:] if self.etapes[n]["etat"] == "a_jouer"]

    def projection(self, nom):
        e = self.etapes[nom]
        return self.cumul + self._reservation(e) + sum(self._attendu(r) for r in self._restantes_apres(nom))

    def _consigner(self, quoi, nom, **champs):
        self.journal.append(dict({"n": len(self.journal) + 1, "quoi": quoi, "etape": nom, "cumul_usd": round(self.cumul, 6)}, **champs))

    # --- sacrifices -------------------------------------------------------------------------------------------------------

    def _liste_sacrifice(self):
        cand = [self.etapes[n] for n in self.ordre if self.etapes[n]["role"] in ("sacrifiable", "reductible")]
        return sorted(cand, key=lambda e: e["rang"])

    def _appliquer(self, e, motif):
        if e["role"] == "sacrifiable":
            e["etat"] = RETIREE
            self._consigner("retiree", e["nom"], motif=motif)
        else:
            e["reduite_appliquee"] = True
            self._consigner("reduite", e["nom"], motif=motif)

    def _prochaine_mesure(self):
        for e in self._liste_sacrifice():
            if e["etat"] != "a_jouer":
                continue
            if e["role"] == "reductible" and e["reduite_appliquee"]:
                continue
            return e
        return None

    # --- la règle ---------------------------------------------------------------------------------------------------------

    def avant_etape(self, nom):
        """Rend (décision, détail) : `jouer` (avec `reservation_usd`, `reduite`, `reste_avant_plafond_usd`), `retiree`,
        `non_mesuree_budget` (C13) ou `non_lancee_hors_porte` (réserve)."""
        e = self.etapes[nom]
        if e["etat"] == RETIREE:
            return RETIREE, {"motif": "retirée plus tôt par la règle d'A1"}
        if e["etat"] != "a_jouer":
            raise BudgetRefuse(f"étape {nom} déjà {e['etat']} : jamais rejouée")
        # 1. projection
        while self.projection(nom) > self.plafond + EPS:
            m = self._prochaine_mesure()
            if m is None:
                break
            self._appliquer(m, "projection au-dessus du plafond S17")
            if e["etat"] == RETIREE:
                return RETIREE, {"motif": "retirée par la projection (règle d'A1, 1)"}
        # 2. arrêt d'étape
        if self.arret is not None and self.cumul + EPS >= self.arret:
            if not self.arret_touche:
                self._consigner("arret_etape_touche", nom, arret_usd=self.arret)
            self.arret_touche = True
            for n in self.ordre:
                r = self.etapes[n]
                if r["etat"] != "a_jouer":
                    continue
                if r["role"] == "sacrifiable":
                    self._appliquer(r, "arrêt d'étape atteint")
                elif r["role"] == "reductible" and not r["reduite_appliquee"]:
                    self._appliquer(r, "arrêt d'étape atteint")
            if e["etat"] == RETIREE:
                return RETIREE, {"motif": "retirée à l'arrêt d'étape (règle d'A1, 2)"}
        # 3. plafond
        while self.cumul + self._reservation(e) > self.plafond + EPS:
            if e["role"] == "sacrifiable":
                self._appliquer(e, "cumul + réservation au-dessus du plafond S17")
                return RETIREE, {"motif": "retirée au plafond (règle d'A1, 3)"}
            if e["role"] == "reductible" and not e["reduite_appliquee"]:
                self._appliquer(e, "cumul + réservation au-dessus du plafond S17")
                continue
            if e["role"] == "protegee_hors_porte":
                e["etat"] = NON_LANCEE_HORS_PORTE
                self._consigner(NON_LANCEE_HORS_PORTE, nom)
                return NON_LANCEE_HORS_PORTE, {"motif": "étape protégée hors porte non lancée : réserve, C13 inchangée"}
            e["etat"] = NON_MESUREE
            self._consigner(NON_MESUREE, nom)
            return NON_MESUREE, {"motif": "étape protégée (ou réduite) qui ne tient pas sous S17 : non mesurée (budget), C13"}
        e["etat"] = "en_cours"
        self._consigner("jouer", nom, reservation_usd=self._reservation(e), reduite=e["reduite_appliquee"])
        return JOUER, {"reservation_usd": self._reservation(e), "reduite": e["reduite_appliquee"],
                       "reste_avant_plafond_usd": round(self.plafond - self.cumul, 6)}

    def apres_etape(self, nom, cout_reel_usd):
        """Compte le coût réel en entier ; rend l'état final de l'étape (`jouee`, `coupee_retiree`, `non_mesuree_budget`)."""
        e = self.etapes[nom]
        if e["etat"] != "en_cours":
            raise BudgetRefuse(f"étape {nom} non lancée : aucun coût à compter")
        if not reel(cout_reel_usd, 0):
            raise BudgetRefuse(f"coût réel : réel ≥ 0 (reçu {cout_reel_usd!r})")
        avant = self.cumul
        self.cumul += float(cout_reel_usd)
        depasse_reservation = float(cout_reel_usd) > self._reservation(e) + EPS
        if self.cumul > self.plafond + EPS:
            self.cumul = self.plafond  # le relais coupe à S17 : rien au-delà n'est dépensé
            e["etat"] = RETIREE if e["role"] == "sacrifiable" else NON_MESUREE
            self._consigner("coupee_a_s17", nom, cout_usd=round(self.plafond - avant, 6), etat=e["etat"])
            return e["etat"]
        e["etat"] = "jouee"
        self._consigner("jouee", nom, cout_usd=round(float(cout_reel_usd), 6), au_dela_de_la_reservation=depasse_reservation)
        return "jouee"

    def etat(self):
        return {"version": VERSION, "plafond_usd": self.plafond, "arret_etape_usd": self.arret, "cumul_usd": round(self.cumul, 6),
                "arret_touche": self.arret_touche,
                "etapes": {n: {"etat": self.etapes[n]["etat"], "reduite": self.etapes[n]["reduite_appliquee"]} for n in self.ordre},
                "c13_budget_satisfaite": not any(self.etapes[n]["etat"] == NON_MESUREE for n in self.ordre),
                "journal": list(self.journal)}


def rejouer(plafond_usd, arret_etape_usd, etapes, couts):
    """Garde R5 ligne 30 : rejoue les décisions sur les seules consommations (`couts` : {étape: coût}) ; rend le journal."""
    b = Budget(plafond_usd, arret_etape_usd, etapes)
    for nom in b.ordre:
        d, _ = b.avant_etape(nom)
        if d == JOUER:
            b.apres_etape(nom, couts.get(nom, 0.0))
    return [(j["quoi"], j["etape"]) for j in b.journal]


def depuis_configuration(conf):
    b = conf["budget"]
    return Budget(b["plafond_usd"], b["arret_etape_usd"], b["etapes"])
