"""Construit le brief de la génération 2 à partir des verdicts calculés par l'orchestrateur (tests-de-mort/*/verdict.json).
Les parents sont les fiches au verdict « survit » ; rien de ce que les juges ont écrit n'est servi."""
import json, re, pathlib, hashlib
R = pathlib.Path(__file__).resolve().parent.parent
def verdict(i): return json.loads((R / "tests-de-mort" / i / "verdict.json").read_text())["verdict"]
def chiffres(i): return json.loads((R / "tests-de-mort" / i / "verdict.json").read_text())["chiffres_verificateur"]

REGISTRE = {  # titre, résultat en une ligne (faits mesurés), dans l'ordre des tests
 "F04": ("Pression de prix aux adjudications du Trésor américain",
         lambda c: f"sur {c['n_adjudications']:.0f} réouvertures à 10, 20 et 30 ans (2010-2026), pression moyenne de {c['v_moyen_pb']:.2f} pb (erreur type {c['erreur_type_pb']:.2f}, t = {c['t_stat']:.1f}) ; placebo à J+10 : |t| = {c['t_placebo_abs']:.2f}"),
 "F04-bis": ("Adjudications : la disparition de l'effet après 2021 vient-elle de la méthode de la courbe du Trésor ?",
         lambda c: f"sur {c['n_adjudications']:.0f} réouvertures de l'exercice 2021, pression de {c['v_hs_moyen_pb']:.2f} pb avec l'ancienne méthode du Trésor et de {c['v_mc_moyen_pb']:.2f} pb avec la nouvelle ; différence {c['d_moyen_pb']:.2f} pb, intervalle à 95 % [{c['d_borne_inf_95_pb']:.2f} ; {c['d_borne_sup_95_pb']:.2f}], qui contient le seuil préinscrit de 0,9"),
 "F12": ("Instrument de protection de la transmission de la BCE et écarts souverains",
         lambda c: f"pente écart souverain / surprise de taux : {c['b_avant']:.2f} avant juillet 2022 ({c['n_avant']:.0f} réunions), {c['b_apres']:.2f} après ({c['n_apres']:.0f}) ; variation {c['d_hat']:.2f}, erreur type {c['se_d']:.2f} ; sans la réunion du 12 mars 2020 la variation tombe à {c['d_max_sans_une']:.2f}"),
 "F01": ("Anomalies boursières publiées : effet de la publication ou tendance commune ?",
         lambda c: f"effet propre de la publication : {c['theta']:.2f} du rendement d'origine (erreur type {c['se_theta']:.2f}), intervalle [{c['borne_basse_ic95']:.2f} ; {c['borne_haute_ic95']:.2f}] ; {c['n_anomalies_traitees']:.0f} anomalies"),
 "H16": ("Les surprises de la BCE sont-elles prévisibles hors échantillon avec des données publiques ?",
         lambda c: f"sur {c['n_eval']:.0f} réunions (2010-2025), cinq prédicteurs publics réestimés avant chaque réunion : R² hors échantillon de {100*c['r2_oos']:.1f} %, statistique de Clark-West {c['cw_t']:.2f} (seuil 1,645)"),
 "H13": ("Emploi américain : le taux à 2 ans réagit-il à la part du chiffre qui sera révisée ?",
         lambda c: f"sur {c['n_publications']:.0f} publications (1990-2025), {c['beta_pb_par_100k']:.2f} pb par tranche de 100 000 emplois surestimés (erreur type {c['erreur_type_pb']:.2f}, t = {c['t_stat']:.2f}) ; placebo la veille : |t| = {c['t_placebo_abs']:.2f}"),
}
PARENTS_DETAIL = {
 "F04": """**Mesure.** V = 100 × [2·E(J) − E(J−5) − E(J+5)], en points de base, où E = rendement à échéance constante du Trésor (FRED `DGS10`, `DGS20`, `DGS30`) moins rendement au pair de la courbe ajustée de la Fed (`SVENPY10/20/30` de `feds200628.csv`) ; J = jour de l'adjudication, en jours ouvrés. Seules les réouvertures sont gardées (le titre de référence n'y change pas). Erreur type groupée par mois (134 mois).
**Dispersion mesurée, utile pour vos calculs de puissance.** Écart-type de V : 2,57 pb par adjudication.
**Lectures exploratoires, faites après le verdict (questions, pas résultats).** Par échéance : 1,17 pb à 10 ans, 1,04 à 30 ans, −0,13 à 20 ans. Par année : de 1,0 à 2,2 pb de 2011 à 2021, puis 0,30 ; −0,03 ; 0,23 ; −0,54 ; 0,39 de 2022 à 2026.
**Fait de mesure établi.** Le 6 décembre 2021 le Trésor a remplacé la méthode de sa courbe (spline d'Hermite, puis méthode « monotone convexe »). Sur l'exercice 2021, où il publie les deux méthodes côte à côte (fichier à deux décimales, soit 1 pb de résolution), l'écart ancienne moins nouvelle méthode vaut en moyenne 0,26 pb à J−5, 0,70 pb à J et 0,35 pb à J+5 : l'ancienne méthode gonfle le taux le jour même de l'adjudication.
**Littérature la plus proche (vérifiée).** Fleming, Liu et Nguyen (2026, Fed de New York) : pression mesurée sur données intrajournalières et CRSP de 1991 à juillet 2024, qui « faiblit nettement » en 2015-2024 ; le montant offert ne l'explique pas. Lou, Yan et Zhang (2013) : article d'origine, 1980-2008.
**Ce qui reste ouvert.** La disparition après 2021 vient-elle du marché ou de la mesure ? Les échéances de 2 à 7 ans, l'effet de taille et les autres émetteurs souverains n'ont pas été testés. Aucune mesure indépendante de la courbe du Trésor n'a été essayée.""",
 "H13": """**Mesure.** Régression MCO, par publication mensuelle de l'emploi, de la variation du taux à 2 ans (FRED `DGS2`, en pb) le jour de la publication sur N = première estimation moins troisième estimation de la variation mensuelle de l'emploi (`PAYEMS`, millésimes ALFRED, en centaines de milliers), avec en contrôle les révisions des deux mois précédents publiées le même jour, la variation publiée du taux de chômage et la médiane des douze dernières variations connues la veille. Erreurs types robustes (HC3). Hors révisions annuelles larges, publication double et extrêmes de 2020.
**Dispersion mesurée, utile pour vos calculs de puissance.** Écart-type de la variation du taux à 2 ans un jour d'emploi : 9,43 pb.
**Fragilité mesurée (descriptif).** Aucune décennie n'est significative seule ; les années 2010 donnent −0,45 pb (t = −0,39) ; sans les années 2020 (47 publications), t tombe à 1,75.
**Limite de fond.** Il n'existe pas de source gratuite de la prévision de consensus : la vraie surprise du jour manque. Un coefficient positif est attendu même d'un marché rationnel qui ne peut pas voir l'erreur le jour même ; le test ne montre donc pas un défaut de filtrage.
**Littérature la plus proche (vérifiée).** Gilbert (2011) : sur les actions, les prix bougent dans le sens de la révision future (signe contraire) ; seul son résumé a été lu. Krueger et Fortson (2003) ; Gilbert, Scotti, Strasser et Vega (2017).
**Ce qui reste ouvert.** Le taux revient-il en arrière quand la révision est publiée ? L'effet existe-t-il pour d'autres statistiques révisées (ventes au détail, production industrielle, PIB), d'autres échéances, d'autres marchés ? Pourquoi est-il absent dans les années 2010 ? La syntaxe qui marche pour les millésimes : `https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=<SERIE>&vintage_date=AAAA-MM-JJ`.""",
}
def main():
    v1 = (R / "brief.md").read_text()
    c2 = (R / "course-2" / "brief-course-2.md").read_text()
    sources = c2[c2.index("Sources vérifiées"):c2.index("## Champ ajouté")]
    t1 = re.findall(r"(?m)^### F\d\d — (.*)$", (R / "jugements" / "fiches-anonymes.md").read_text())
    t2 = [t for f in ("kimi", "gemini", "claude") for t in re.findall(r"(?m)^### 2[KGC]\d — (.*)$", (R / "course-2" / "fiches" / f"proposeur-{f}.md").read_text())]
    assert len(t1) == 20 and len(t2) == 15, (len(t1), len(t2))
    parents = [i for i in REGISTRE if (R / "tests-de-mort" / i / "verdict.json").exists() and verdict(i) == "survit"]
    lignes = [f"- **{REGISTRE[i][0]}** — verdict : *{verdict(i)}*. {REGISTRE[i][1](chiffres(i))}." for i in REGISTRE]
    lignes.append("- **Les erreurs de projection d'inflation de la BCE étaient-elles prévisibles en temps réel ?** — *test annulé, à refaire* : la préinscription rangeait à l'envers les exercices de juin et de septembre ; aucun résultat valide.")
    texte = v1 + f"""
---

# Complément pour la génération 2 — 12 novembre 2026

Une première génération d'idées a été proposée, jugée puis **testée sur données réelles**, chaque test étant préinscrit et
scellé avant lecture des données, exécuté par un agent, recalculé par un autre, et jugé par un code séparé. Vous êtes proposeur
de la **génération 2** : vous construisez sur ce qui a survécu.

## Profil et centres d'intérêt de l'étudiant
- Centres d'intérêt, par ordre : **économie monétaire, banque centrale, macroéconomie**, puis finance de marché.
- Il sait : Python (pandas, numpy, statsmodels), mathématiques de classes préparatoires, cours de titres à revenu fixe et
  d'économie monétaire. Ses projets existants portent sur les actions.

## Registre des résultats (faits mesurés ; « pb » = point de base)
{chr(10).join(lignes)}

## Les parents : les {len(parents)} idées qui ont survécu
""" + "\n".join(f"### Parent {k} — {REGISTRE[i][0]}\n\n{PARENTS_DETAIL[i]}\n" for k, i in zip("AB", parents)) + f"""
## Ce que vous rendez
Exactement **cinq fiches**, en français, au format de fiche du brief, avec deux champs en plus :
- **Parent et différence** (obligatoire) : `Parent A`, `Parent B` ou `libre`. Pour une fiche fille, dites lequel de ces quatre
  éléments vous changez par rapport au parent — la statistique, l'échantillon ou le marché, la source de données,
  l'identification — et pourquoi ce changement peut donner une réponse que le parent n'a pas. Une fiche qui reformule son parent
  sans changer l'un de ces quatre éléments est refusée avant le jugement. Pour une fiche libre, citez le résultat du registre
  qui la motive.
- **Arithmétique de puissance** (obligatoire) : nombre d'observations réellement indépendantes, erreur type attendue (servez-vous
  des dispersions mesurées ci-dessus), effet prédit ; dites si le test peut trancher. Plusieurs tests de la génération 1 ont fini
  « non concluants » faute d'observations : un test qui ne peut pas trancher est une mauvaise fiche.

Au moins **trois fiches filles** (réparties comme vous voulez entre les parents) et au plus **deux fiches libres**.
Cinq questions et cinq méthodes différentes. Les meilleures fiches filles tranchent une question que le parent a laissée ouverte.

## Vous n'avez aucun outil
Vous ne pouvez rien télécharger ni tester. Le champ « Données » ne cite que des sources de la liste ci-dessous, dont l'accès a
été vérifié. Toute autre source porte la mention « source non vérifiée » et ne peut pas être indispensable au test de mort.

{sources}- Ajouts vérifiés depuis : fichier du Trésor donnant ses deux méthodes de courbe côte à côte pour l'exercice 2021
  (`https://home.treasury.gov/system/files/221/fy2021-mc-vs-hs-combined.csv`) ; millésimes ALFRED par
  `alfredgraph.csv?id=<SERIE>&vintage_date=AAAA-MM-JJ` ; hypothèses individuelles de taux directeur dans l'enquête de la BCE auprès
  des prévisionnistes (2002-2026) ; facteurs quotidiens Europe de la bibliothèque Ken French.

## Idées déjà proposées — ne pas les reprendre telles quelles (une fille d'un parent doit s'en distinguer comme dit plus haut)
""" + "\n".join(f"- {t}" for t in t1 + t2) + """

## Sortie attendue
Cinq fiches, chacune sous un titre `### <ID> — <titre court>`, identifiants `{ID}1` à `{ID}5`. Rien d'autre : pas d'introduction,
pas de conclusion, pas de classement de vos propres fiches.
"""
    (pathlib.Path(__file__).parent / "brief-generation-2.md").write_text(texte)
    for fam, pre in (("kimi", "3K"), ("gemini", "3G"), ("claude", "3C")):
        (pathlib.Path(__file__).parent / "bruts" / f"consigne-proposeur-{fam}.md").write_text(
            "Vous êtes un proposeur dans une course d'idéation de recherche, génération 2. Lisez le brief ci-dessous en entier et suivez-le à la lettre. Vos identifiants de fiches commencent par « " + pre + " ».\n\n" + texte.replace("{ID}", pre))
    print("parents :", parents, "|", len(texte), "caractères |", hashlib.sha256(texte.encode()).hexdigest()[:16])
    print("\n".join(lignes[:7]))
if __name__ == "__main__":
    main()
