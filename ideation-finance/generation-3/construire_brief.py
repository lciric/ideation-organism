"""Brief de la génération 3 : parents = survivants de la génération 2 (verdicts calculés par l'orchestrateur). Rien des juges n'est servi."""
import json, re, pathlib, hashlib
R = pathlib.Path(__file__).resolve().parent.parent
def v(i): return json.loads((R / "tests-de-mort" / i / "verdict.json").read_text())
def c(i): return v(i)["chiffres_verificateur"]
def f(x, n=2): return f"{x:.{n}f}".replace(".", ",")
REG = [
 ("F04", "Pression de prix aux adjudications du Trésor américain", lambda c: f"sur {c['n_adjudications']:.0f} réouvertures à 10, 20 et 30 ans (2010-2026), pression moyenne de {f(c['v_moyen_pb'])} pb mesurée contre la courbe du Trésor (t = {f(c['t_stat'],1)}) ; par année, de 1,0 à 2,2 pb en 2011-2021, proche de zéro en 2022-2026 (lecture exploratoire)"),
 ("F04-bis", "Adjudications : la disparition après 2021 vient-elle de la méthode de la courbe du Trésor ?", lambda c: f"sur {c['n_adjudications']:.0f} réouvertures de l'exercice 2021, {f(c['v_hs_moyen_pb'])} pb avec l'ancienne méthode du Trésor et {f(c['v_mc_moyen_pb'])} pb avec la nouvelle ; différence {f(c['d_moyen_pb'])} pb, IC à 95 % [{f(c['d_borne_inf_95_pb'])} ; {f(c['d_borne_sup_95_pb'])}], qui contient le seuil préinscrit de 0,9"),
 ("F12", "Instrument de protection de la transmission de la BCE et écarts souverains", lambda c: f"variation de pente {f(c['d_hat'])}, erreur type {f(c['se_d'])}, {c['n_apres']:.0f} réunions après l'instrument"),
 ("F01", "Anomalies boursières publiées : effet de la publication ou tendance commune ?", lambda c: f"effet de la publication {f(c['theta'])} du rendement d'origine, IC [{f(c['borne_basse_ic95'])} ; {f(c['borne_haute_ic95'])}]"),
 ("H16", "Les surprises de la BCE sont-elles prévisibles hors échantillon avec des données publiques ?", lambda c: f"R² hors échantillon {f(100*c['r2_oos'],1)} % sur {c['n_eval']:.0f} réunions, Clark-West {f(c['cw_t'])} (seuil 1,645)"),
 ("H13", "Emploi américain : le taux à 2 ans réagit-il à la part du chiffre qui sera révisée ?", lambda c: f"{f(c['beta_pb_par_100k'])} pb par 100 000 emplois surestimés, sur {c['n_publications']:.0f} publications (t = {f(c['t_stat'])}) ; aucune décennie significative seule, les années 2010 négatives"),
 ("H03-v2", "Les erreurs de projection d'inflation de la BCE étaient-elles prévisibles en temps réel par une règle fondée sur les révisions ?", lambda c: f"corrélation {f(c['r_moyen'])} entre correction annoncée et erreur réalisée (IC à 90 % [{f(c['borne_basse_ic90'])} ; {f(c['borne_haute_ic90'])}]), {c['n_obs_evaluees']:.0f} observations ; la projection corrigée fait moins bien que la publiée"),
 ("J07", "Peut-on prévoir hors échantillon la partie révisée du chiffre de l'emploi ?", lambda c: f"sur {c['n_previsions']:.0f} prévisions depuis 1997, Clark-West {f(c['cw_stat'])} (seuil 1,645), R² hors échantillon {f(100*c['r2_hors_echantillon'],1)} %"),
 ("J02", "Les projections d'inflation de la BCE sous-réagissent-elles ?", lambda c: f"pente erreur sur révision réduites {f(c['beta_z'])} (t = {f(c['t_nw4'])}) sur {c['n_cibles']:.0f} trimestres cibles ; {f(c['beta_z_min_sans_deux_ans'])} sans 2021-2022 ; {f(c['beta_z_hors_2021_2023'])} hors 2021-2023"),
 ("J05", "Pression aux adjudications mesurée contre la courbe ajustée de la Fed, avant et après 2021", lambda c: f"concession {f(c['k_moyen_avant_pb'])} pb en 2010-2021 ({c['n_avant']:.0f} réouvertures) et {f(c['k_moyen_apres_pb'])} pb en 2022-2026 ({c['n_apres']:.0f}) : pas de baisse ; écart {f(c['delta_k_pb'])}, IC à 90 % [{f(c['borne_inf_90_pb'])} ; {f(c['borne_sup_90_pb'])}] ; non concluant parce qu'un contrôle de dates n'avait pas prévu les lundis fériés (trois lignes correctes) ; sans 2023 l'écart est nul (−0,04)"),
]
PARENTS = {
 "J07": """**Mesure.** Pour chaque publication mensuelle de l'emploi depuis 1990, N = première estimation moins troisième estimation de
la variation mensuelle de l'emploi (`PAYEMS`, millésimes ALFRED, en milliers). Prévision récursive à fenêtre croissante (au moins 60
publications d'apprentissage dont la troisième estimation est publiée au plus tard le jour de la prévision), MCO sur une constante,
x1 = première estimation moins la médiane des douze derniers mois connus, x2 = somme des deux révisions des mois précédents publiées
le même jour ; référence = moyenne historique de N. Clark-West avec Newey-West à 4 retards.
**Ce que la vérification a montré (descriptif).** Tout le pouvoir prédictif vient de x2 (Clark-West 2,12 seul) ; x1 n'apporte rien
(−1,15). Tout vient de 2020-2025 : sur ces prévisions, Clark-West 3,72 et R² 9,2 % ; sans elles, Clark-West −1,28. Retirer les deux
publications les plus influentes fait tomber la statistique à 1,52. Écart-type de N : environ 58 000 emplois.
**Questions ouvertes.** Pourquoi depuis 2020 (méthode du bureau des statistiques, taux de réponse, chocs de la pandémie) ? Le marché
se sert-il de cette prévisibilité le jour même (le parent de la génération 1 dit que le taux à 2 ans réagit au bruit) ? Vaut-elle pour
d'autres statistiques révisées ?""",
 "J02": """**Mesure.** Pour chaque trimestre cible de 1999T4 à 2026T3 (108 cibles), erreur = inflation réalisée (Eurostat, glissement
annuel de l'IPCH) moins projection de la BCE à horizon 2 trimestres ; révision = projection à horizon 2 moins projection à horizon 3
pour la même cible ; pente MCO de l'erreur réduite sur la révision réduite, Newey-West à 4 retards. Lettres des millésimes vérifiées :
W = mars, G = juin, S = septembre, A = décembre (colonne `TITLE_COMPL`).
**Ce que la vérification a montré (descriptif).** Pente brute 0,68 ; avant 2020, 0,13 (proche de Granziera, Jalasjoki et Paloviita
2021 : 0,20 non significatif) ; sans 2021-2022, 0,05 ; sans 2023 seule, 0,57.
**Questions ouvertes.** La sous-réaction est-elle propre aux grands chocs ? Vient-elle des hypothèses techniques (prix de l'énergie,
change, taux, figés sur les marchés à terme et publiés dans la même base) plutôt que du jugement des économistes ? Les prévisionnistes
professionnels (enquête de la BCE) sous-réagissent-ils de la même façon ? Une règle en temps réel ne l'exploitait pas (H03-v2).""",
}
OUVERTE = """### Question ouverte prioritaire — la pression aux adjudications a-t-elle disparu du marché, ou seulement de la courbe du Trésor ?

Trois tests l'ont approchée sans la trancher selon leur règle (voir le registre : F04, F04-bis, J05). Faits établis : mesurée contre la
courbe du Trésor, la pression disparaît après 2021 ; le 6 décembre 2021 le Trésor a changé la méthode de sa courbe, et sur l'exercice 2021
la nouvelle méthode efface environ la moitié de la pression ; mesurée contre la courbe ajustée de la Fed, nette de l'écart du même titre
cinq jours avant, elle ne baisse pas (hausse portée surtout par 2023 et le 30 ans). Prix de marché par titre disponibles depuis 2008
(FedInvest, TreasuryDirect, un formulaire par date). Une fiche qui tranche cette question, avec une mesure et un contrôle que les trois
tests n'ont pas eus, compte comme fille."""
def main():
    b2 = (R / "generation-2" / "brief-generation-2.md").read_text()
    tete = b2[:b2.index("---\n\n# Complément pour la génération 2")]
    sources = b2[b2.index("## Vous n'avez aucun outil"):b2.index("## Idées déjà proposées")]
    t1 = re.findall(r"(?m)^### F\d\d — (.*)$", (R / "jugements" / "fiches-anonymes.md").read_text())
    t2 = [t for fam, p in (("kimi", "2K"), ("gemini", "2G"), ("claude", "2C")) for t in re.findall(r"(?m)^### " + p + r"\d — (.*)$", (R / "course-2" / "fiches" / f"proposeur-{fam}.md").read_text())]
    t3 = [t for fam, p in (("kimi", "3K"), ("gemini", "3G"), ("astra", "3A"), ("claude", "3C")) for t in re.findall(r"(?m)^### " + p + r"\d — (.*)$", (R / "generation-2" / "fiches" / f"proposeur-{fam}.md").read_text())]
    assert (len(t1), len(t2), len(t3)) == (20, 15, 20)
    parents = [i for i in ("J07", "J02") if v(i)["verdict"] == "survit"]
    reg = "\n".join(f"- **{t}** — verdict : *{v(i)['verdict']}*. {fn(c(i))}." for i, t, fn in REG)
    texte = tete + f"""---

# Complément pour la génération 3 — 12 novembre 2026

Deux générations d'idées ont été proposées, jugées puis **testées sur données réelles** (préinscription scellée avant lecture des
données, exécution par un agent, recalcul par un autre, verdict par un code séparé). Vous êtes proposeur de la **génération 3** : vous
construisez sur ce qui a survécu et sur la question restée ouverte.

## Profil et centres d'intérêt de l'étudiant
- Centres d'intérêt, par ordre : **économie monétaire, banque centrale, macroéconomie**, puis finance de marché.
- Il sait : Python (pandas, numpy, statsmodels), mathématiques de classes préparatoires, cours de titres à revenu fixe et
  d'économie monétaire. Ses projets existants portent sur les actions.

## Registre des résultats (faits mesurés, chiffres du vérificateur ; « pb » = point de base)
{reg}

## Les parents : les {len(parents)} idées de la génération 2 qui ont survécu
""" + "\n".join(f"### Parent {k} — {dict((i, t) for i, t, _ in REG)[i]}\n\n{PARENTS[i]}\n" for k, i in zip("AB", parents)) + "\n" + OUVERTE + """

## Ce que vous rendez
Exactement **cinq fiches**, en français, au format de fiche du brief, avec deux champs en plus :
- **Parent et différence** (obligatoire) : `Parent A`, `Parent B`, `Question ouverte` ou `libre`. Pour une fille, dites lequel de ces
  quatre éléments vous changez par rapport au test qui l'inspire — la statistique, l'échantillon ou le marché, la source de données,
  l'identification — et pourquoi ce changement peut donner une réponse que ce test n'a pas. Une fiche qui reformule un test déjà fait
  sans changer l'un de ces éléments est refusée avant le jugement. Pour une fiche libre, citez le résultat du registre qui la motive.
- **Arithmétique de puissance** (obligatoire) : nombre d'observations réellement indépendantes, erreur type attendue (servez-vous des
  dispersions mesurées ci-dessus), effet prédit ; dites si le test peut trancher. Plusieurs tests ont fini « non concluants » faute
  d'observations, et deux survivants reposent sur quelques années récentes : un test qui ne peut pas trancher, ou dont le résultat
  tiendrait à un seul épisode, est une mauvaise fiche.

Au moins **trois fiches filles** (d'un parent ou de la question ouverte) et au plus **deux fiches libres**. Cinq questions et cinq
méthodes différentes.

""" + sources + "## Idées déjà proposées — ne pas les reprendre telles quelles\n" + "\n".join(f"- {t}" for t in t1 + t2 + t3) + """

## Sortie attendue
Cinq fiches, chacune sous un titre `### <ID> — <titre court>`, identifiants `{ID}1` à `{ID}5`. Rien d'autre : pas d'introduction,
pas de conclusion, pas de classement de vos propres fiches.
"""
    D = pathlib.Path(__file__).parent
    (D / "brief-generation-3.md").write_text(texte)
    for fam, pre in (("kimi", "4K"), ("gemini", "4G"), ("astra", "4A"), ("claude", "4C")):
        (D / "bruts" / f"consigne-proposeur-{fam}.md").write_text("Vous êtes un proposeur dans une course d'idéation de recherche, génération 3. Lisez le brief ci-dessous en entier et suivez-le à la lettre. Vos identifiants de fiches commencent par « " + pre + " ».\n\n" + texte.replace("{ID}", pre))
    print("parents :", parents, "|", len(texte), "caractères |", hashlib.sha256(texte.encode()).hexdigest()[:16])
    print(reg)
if __name__ == "__main__":
    main()
