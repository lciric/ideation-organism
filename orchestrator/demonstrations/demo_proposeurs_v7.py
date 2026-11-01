"""Proposeurs enfichables et références gratuites, sur des mondes tirés au hasard dans une grammaire (v7, version 7) —
exploratoire, sans dépense, sans modèle.

Lignée conv-audit, 27 octobre 2026. Option 3 de la synthèse du collisionneur « proposeur enfichable » (`0a209c33…`) : la
batterie à 0 USD avant tout duel payé. Quatre bras, mêmes mondes, même population initiale (6 lois tirées au hasard au
gabarit), mêmes témoins (par moniteur : sa loi exacte, vraie ; une loi sur un trait de bruit, fausse), juge de v7 version 7
(juge v1 sans urne, nul informé sur la partie de calibrage, nul d'archive ajusté, règle e-BH, témoins jugés sans agents),
3 générations, 12 propositions par génération :
- « scripte_aveugle » : le proposeur scripté du pôle (`AdaptateurSimule`, gabarits joués mécaniquement ; c'est ma lignée,
  pas un modèle), sans la partie de développement ;
- « scripte_exploration » : le même, avec la partie de développement ;
- « aleatoire » : lois tirées au hasard au gabarit (référence gratuite n° 1) ;
- « mecanique » : chercheur mécanique sur la partie de développement (référence gratuite n° 2).

Lecture fixée avant l'exécution (taux sur les graines) :
- P1 : témoins faux promus ≤ α, dans chaque bras ;
- P2 (dents) : témoins vrais des moniteurs **non linéaires** promus au moins une fois sur deux (sinon : pas de dents, pas
  de conclusion sur les bras) ; ceux des moniteurs linéaires sont attendus éliminés par le nul informé (ils ne sont que du
  connu) ;
- P3 : moniteurs non linéaires couverts (au moins une fiche non témoin promue) par bras ; « aleatoire » ≤ « scripte_aveugle »
  attendu ; si « mecanique » ≥ « scripte_exploration », le scripté n'apporte rien au-delà d'une recherche mécanique ;
- P4 : fiches promues non témoins dont la loi n'a **aucun** lien avec la structure du moniteur (aucun des traits i, j de la
  vérité) : rapportées par bras (fausses découvertes au sens du monde ; attendues rares).
Ce n'est pas le duel : aucun modèle ici. C'est la batterie qui le rendra lisible.

v2 de la démonstration (16:25 UTC) : `--grammaire v2` tire les mondes de `generer_monde_grammaire_v2.py` (formes hors de
l'espace de recherche du mécanique : seuil décalé, trois traits, quadratique, produit) ; le lien d'une promue à la structure
devient précis (les seuls traits que la structure emploie : i ; i et j ; i, j et k) pour les deux grammaires — la course v1
employait le critère large (i ou j). Lecture fixée avant la course v2 : P1 et P2 comme en v1 (P2 : les témoins approchés
au gabarit, quadratique et produit, peuvent manquer : rapporté par forme) ; P3 : le mécanique ne devrait plus dominer
(attendu : moins de la moitié de ses 23 sur 35 de la v1, en proportion) ; c'est la barre gratuite d'un duel juste.

Usage : python -I -B demonstrations/demo_proposeurs_v7.py DOSSIER_NEUF [--graines 10] [--bras b1,b2] [--grammaire v1|v2]
"""

import argparse
import json
import os
import sys
import time

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)
sys.path.insert(0, os.path.join(RACINE, "exemples"))

import generer_monde_grammaire_v1 as grammaire_v1  # noqa: E402
import generer_monde_grammaire_v2 as grammaire_v2  # noqa: E402
from generer_monde_grammaire_v1 import fiches_de_temoins  # noqa: E402
from pole.cycle import ConfigGeneration  # noqa: E402
from pole.monde_banque import MondeBanque  # noqa: E402
from pole.outils import ecrire_json_scelle, graine_derivee  # noqa: E402
from pole.pole import executer_pole  # noqa: E402
from pole.proposeur import valider_proposition  # noqa: E402
from pole.proposeurs_references import propositions_aleatoires  # noqa: E402
from pole.simulation import AdaptateurSimule, MondeSimule  # noqa: E402

BRAS = {"scripte_aveugle": {"proposeur": "agent", "exploration": False},
        "scripte_exploration": {"proposeur": "agent", "exploration": True},
        "aleatoire": {"proposeur": "aleatoire", "exploration": False},
        "mecanique": {"proposeur": "mecanique", "exploration": True}}
D, K, MONITEURS = 4, 3, 3


def _traits_de(loi, d=D):
    """Traits portant un poids non nul dans une loi du gabarit."""
    if loi["type"] == "softmax":
        return {t for t in range(d) if any(abs(l[t]) > 1e-9 for l in loi["poids"])}
    if loi["type"] == "par_sous_population":
        return set().union(*(_traits_de(l, d) for l in loi["lois"].values()))
    if loi["type"] == "si_sinon":
        c = loi["condition"]
        return _traits_de(loi["si"], d) | _traits_de(loi["sinon"], d) | ({c["indice"]} if "indice" in c else set())
    if loi["type"] == "melange":
        return set().union(*(_traits_de(l, d) for l in loi["composantes"]))
    return set()


TRAITS_DE_LA_STRUCTURE = {"monotone": ("i",), "sous_population": ("i",), "quadratique": ("i",),
                          "combinaison": ("i", "j"), "interaction": ("i", "j"), "seuil": ("i", "j"),
                          "seuil_decale": ("i", "j"), "produit": ("i", "j"), "trois_traits": ("i", "j", "k")}


def traits_de_la_structure(v):
    return {v[c] for c in TRAITS_DE_LA_STRUCTURE[v["structure"]]}


def executer_bras(nom, graine, dossier, chemin_banque, temoins, verite):
    reglages = BRAS[nom]
    monde = MondeBanque(chemin_banque, graine, nul_informe=True, tranches=3)  # v11 : une tranche par génération
    description = monde.description_publique()
    population = [valider_proposition(p, monde, 0.05, f"P{i:02d}", "reference-aleatoire", references=True)
                  for i, p in enumerate(propositions_aleatoires(description, 6, graine_derivee(graine, "population"), 0), 1)]
    config = ConfigGeneration(selection="pari", juge="v1", nul_filles="v2", urne=False, graine=graine, taille_plan=150,
                              taille_plan_filles=150, instants_filles=6, part_calibrage=12, budget_generation_usd=500.0,
                              multiplicite="e-bh", temoins_sans_agent=True, nul_archive=True, nul_archive_ajuste=True,
                              propositions_par_generation=12, exploration_developpement=reglages["exploration"],
                              proposeur=reglages["proposeur"]).valider()
    adaptateur = AdaptateurSimule(graine, MondeSimule(graine))
    bilan = executer_pole(population, fiches_de_temoins(temoins, D, K), adaptateur, config, 3, 5000.0, dossier,
                          memoire_active=True, horodatage_fourni="demo proposeurs v7",
                          temoins_par_generation=MONITEURS, k_recombinaison=4, max_paires=2, monde_noyau=monde)
    with open(os.path.join(dossier, "archive", "index.json"), encoding="utf-8") as f:
        index = json.load(f)
    promues = []
    for ident, e in index.items():
        if e["statut"] != "survit" or e["temoin"]:
            continue
        with open(os.path.join(dossier, "archive", "fiches", ident, "etat-final.json"), encoding="utf-8") as f:
            etat = json.load(f)
        moniteur = (etat.get("espace_instances") or {}).get("moniteur")
        v = verite.get(moniteur, {})
        lien = bool(_traits_de(etat["loi_predictive"]) & traits_de_la_structure(v)) if v else False
        promues.append({"identifiant": ident, "moniteur": moniteur, "source": e["source"], "lien_a_la_structure": lien})
    # Un témoin est resservi à chaque génération (tous le sont dès la génération 0) : on lit son premier jugement.
    temoins_statut = {}
    for ident in sorted(index, key=lambda i: (int(i.split("-")[0][1:]), i)):
        e = index[ident]
        if e["temoin"]:
            temoins_statut.setdefault(e["source"].split(":", 1)[1], e["statut"])
    couverts = sorted({p["moniteur"] for p in promues if p["lien_a_la_structure"]})
    return {"bras": nom, "generations": bilan["generations_executees"], "arret": bilan["arret"],
            "promues": promues, "nombre_promues": len(promues),
            "promues_sans_lien": sum(not p["lien_a_la_structure"] for p in promues),
            "moniteurs_couverts": couverts,
            "non_lineaires_couverts": [m for m in couverts if not verite[m]["lineaire"]],
            "temoins": temoins_statut, "qualite": bilan["qualite_cumulee"]}


def principal(argv=None):
    a = argparse.ArgumentParser()
    a.add_argument("dossier")
    a.add_argument("--graines", type=int, default=10)
    a.add_argument("--bras", default=",".join(BRAS))
    a.add_argument("--grammaire", choices=("v1", "v2"), default="v1")
    args = a.parse_args(argv)
    if os.path.exists(args.dossier) and os.listdir(args.dossier):
        raise FileExistsError(args.dossier)
    os.makedirs(args.dossier, exist_ok=True)
    debut = time.time()
    resultats = []
    for s in range(1, args.graines + 1):
        graine = 20261100 + s
        generer = (grammaire_v1 if args.grammaire == "v1" else grammaire_v2).generer_monde
        banque, temoins, verite = generer(graine)
        dossier_monde = os.path.join(args.dossier, f"monde-{s:02d}")
        chemin = os.path.join(dossier_monde, "banque.json")
        ecrire_json_scelle(chemin, banque)
        par_bras = {}
        for nom in args.bras.split(","):
            par_bras[nom] = executer_bras(nom, graine, os.path.join(dossier_monde, nom), chemin, temoins, verite)
        resultats.append({"graine": graine, "grammaire": args.grammaire,
                          "structures": {m: v["structure"] for m, v in verite.items()},
                          "non_lineaires": [m for m, v in verite.items() if not v["lineaire"]], "bras": par_bras})
    lecture = lire(resultats, args.bras.split(","))
    rapport = {"graines": args.graines, "grammaire": args.grammaire, "duree_s": round(time.time() - debut, 1),
               "lecture": lecture, "par_forme": par_forme(resultats, args.bras.split(",")), "resultats": resultats}
    ecrire_json_scelle(os.path.join(args.dossier, "demo-proposeurs-v7.json"), rapport)
    print(json.dumps({"lecture": lecture, "duree_s": rapport["duree_s"]}, ensure_ascii=False, indent=1))
    return 0


def par_forme(resultats, bras):
    """Par forme de structure : témoins vrais promus, et moniteurs couverts par bras."""
    sortie = {}
    for r in resultats:
        for moniteur, forme in r["structures"].items():
            f = sortie.setdefault(forme, {"moniteurs": 0, "temoin_vrai_promu": 0, "couverts": {b: 0 for b in bras}})
            f["moniteurs"] += 1
            f["temoin_vrai_promu"] += r["bras"][bras[0]]["temoins"].get(f"V-{moniteur}") == "survit"
            for b in bras:
                f["couverts"][b] += moniteur in r["bras"][b]["moniteurs_couverts"]
    return sortie


def lire(resultats, bras):
    lecture = {}
    for nom in bras:
        faux = vrais_nl = vrais_nl_promus = vrais_l = vrais_l_promus = 0
        couverts_nl = non_lineaires = promues = sans_lien = 0
        for r in resultats:
            b = r["bras"][nom]
            for ident, statut in b["temoins"].items():
                moniteur = ident.split("-", 1)[1]
                if ident.startswith("F-"):
                    faux += statut == "survit"
                elif moniteur in r["non_lineaires"]:
                    vrais_nl += 1
                    vrais_nl_promus += statut == "survit"
                else:
                    vrais_l += 1
                    vrais_l_promus += statut == "survit"
            couverts_nl += len(b["non_lineaires_couverts"])
            non_lineaires += len(r["non_lineaires"])
            promues += b["nombre_promues"]
            sans_lien += b["promues_sans_lien"]
        nb_faux = sum(1 for r in resultats for i in r["bras"][nom]["temoins"] if i.startswith("F-"))
        lecture[nom] = {"P1_temoins_faux_promus": [faux, nb_faux],
                        "P2_temoins_vrais_non_lineaires_promus": [vrais_nl_promus, vrais_nl],
                        "P2_temoins_vrais_lineaires_promus": [vrais_l_promus, vrais_l],
                        "P3_moniteurs_non_lineaires_couverts": [couverts_nl, non_lineaires],
                        "P4_promues_sans_lien_a_la_structure": [sans_lien, promues]}
    return lecture


if __name__ == "__main__":
    sys.exit(principal())
