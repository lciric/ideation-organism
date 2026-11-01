"""Monde tenu par le noyau (version 0.6.0) — option (a) du devis du premier lancement réel
(`../premier-lancement-reel/devis-premier-lancement-reel-v1.md`).

Les expérimentateurs réels n'ont ni réseau ni clé : ils ne peuvent rien « mesurer » seuls. Le noyau tire lui-même, après
le gel et dans l'ordre d'exécution imposé, les issues du monde caché aux instances du plan, et les dépose dans le dossier
de l'expérience (`mesures.json`, lié à l'engagement par son empreinte). L'agent écrit le code rejouable qui vérifie ce lien
et range les issues dans `tirages.json` ; le vérificateur le rejoue ; le noyau compare enfin les issues déclarées à
celles qu'il a déposées (toute différence : « rejetee (test change) »). Le monde (table des vérités, lois) n'est jamais
écrit dans un dossier d'agent ; seules les issues le sont.

Monde caché : une table de vérités par énoncé (même règle que le monde simulé, `simulation.MondeSimule`) ; une fiche
vraie a pour monde sa propre loi ; une fiche fausse, la marginale aveugle de sa loi sur le plan (le nul le plus
trompeur) ; un énoncé absent de la table reçoit une vérité tirée de la graine du monde (probabilité `p_vraie`). La graine
des tirages dérive de la graine du monde, de l'empreinte de l'engagement, du numéro de génération **et de la graine du
noyau** : sous `noyau_secret`, les issues ne sont donc reproductibles qu'avec la graine écrite après les évaluations.
"""

from . import selection_pari as sp
from .outils import graine_derivee
from .simulation import MondeSimule


class MondeNoyau:
    nom = "monde-noyau"

    def __init__(self, graine, verites=None, p_vraie=0.5):
        self.graine = graine
        self._verites = MondeSimule(graine, verites, p_vraie)

    def verite(self, enonce):
        return self._verites.verite(enonce)

    def loi_du_monde(self, enonce, gele):
        loi = gele.engagement["loi"]
        if self._verites.verite(enonce):
            return loi
        return {"type": "fixe", "probas": sp.moyenne_loi(loi, gele.engagement["instances"])}

    def mesures(self, enonce, gele, graine_noyau, numero_generation):
        """Issues fraîches du monde caché aux instances du plan (ordre imposé sous l'ordre secret), liées à l'engagement."""
        monde = self.loi_du_monde(enonce, gele)
        graine = graine_derivee(self.graine, "mesures-du-noyau", gele.empreinte, numero_generation, graine_noyau)
        if sp.plan_execution_de(gele.engagement) == "ordre_secret":
            return sp.tirer_frais(gele, monde, graine, graine_noyau=graine_noyau)
        return sp.tirer_frais(gele, monde, graine)


def charger_monde_noyau(chemin, graine, temoins=(), p_vraie=0.5):
    """Monde du noyau depuis un fichier JSON {"verites": {énoncé: vrai|faux}} (jamais copié dans un dossier d'agent),
    complété par la vérité des témoins."""
    import json
    verites = {t.enonce: t.temoin == "vraie" for t in temoins}
    if chemin:
        with open(chemin, encoding="utf-8") as f:
            verites.update(json.load(f)["verites"])
    return MondeNoyau(graine, verites, p_vraie)


def issues_conformes(deposees, declarees):
    """(conforme, motif) : les issues déclarées par l'agent sont exactement celles que le noyau a déposées."""
    if not isinstance(declarees, dict):
        return False, "tirages illisibles"
    if declarees.get("empreinte_engagement") != deposees["empreinte_engagement"]:
        return False, "tirages liés à un autre engagement que celui des mesures déposées"
    if list(declarees.get("issues") or []) != list(deposees["issues"]):
        return False, "issues déclarées différentes de celles déposées par le noyau"
    for cle in ("plan_execution", "empreinte_ordre"):
        if deposees.get(cle) is not None and declarees.get(cle) != deposees.get(cle):
            return False, f"{cle} déclaré différent de celui des mesures déposées"
    return True, "issues identiques à celles déposées par le noyau"
