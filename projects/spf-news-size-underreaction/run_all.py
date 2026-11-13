"""Run the whole project: python run_all.py

1. checks the sha256 of each sealed preregistration copied in audit/<ID>/ (against its .sha256 file and
   the seal recorded in verdict.json);
2. downloads every raw file (or reuses data/raw/) and writes data/raw/PROVENANCE.md;
3. for each study: builds its analysis dataset (data/processed/<ID>_analysis.csv), computes every
   preregistered field and the verdict the sealed rule gives on them, runs its descriptive analyses;
4. compares the studies side by side (descriptive);
5. writes results/results.json, results/RESULTS.md, results/reproduction.md and results/figures/*.png.

Optional: python run_all.py --seed <path to tests-de-mort> fills empty cache slots by copying the raw files
the sealed tests downloaded (<ID>/donnees/; recorded as such in data/raw/PROVENANCE.md).

Each study is one function `run_<id>()` registered in STUDIES: K20 (US SPF) and K20-ZE (ECB SPF). A later
study (the US Livingston Survey, K20-LIV, being preregistered) is added as a new module in src/snu/, a new
function here and a new entry in STUDIES; the functions below are shared.
"""
import hashlib
import json
import sys
import warnings
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
warnings.filterwarnings("ignore", message="Cannot parse header or footer")
warnings.filterwarnings("ignore", message="Workbook contains no default style")

from snu import data, descriptive, figures, k20, k20ze, measures, simulation  # noqa: E402

RESULTS = ROOT / "results"
SEALED_TESTS = ROOT.parents[1] / "ideation-finance" / "tests-de-mort"   # read only: sha256 comparison
FIGURES = RESULTS / "figures"
LABEL = "*Descriptive, not preregistered.*"


# ------------------------------------------------------------------------------------------ shared
def check_seal(tid):
    """The copied preregistration must hash to the sealed value (its .sha256 file and its verdict.json)."""
    folder = ROOT / "audit" / tid
    sha = hashlib.sha256((folder / "preenregistrement.md").read_bytes()).hexdigest()
    sealed = (folder / "preenregistrement.md.sha256").read_text().split()[0]
    in_verdict = json.loads((folder / "verdict.json").read_text(encoding="utf-8"))["sceau_preenregistrement"]
    if not sha == sealed == in_verdict:
        raise SystemExit(f"{tid}: preregistration sha256 {sha} does not match the seal {sealed}")
    print(f"seal OK  {tid}  {sha}")
    return sha


def verdict_from_rule(rule, fields):
    """The machine-readable rule of the preregistration: 'non concluant' if any non-conclusion condition
    holds, 'survit' if all survival conditions hold, 'éliminée' otherwise."""
    ops = {">": lambda a, b: a > b, ">=": lambda a, b: a >= b, "<": lambda a, b: a < b, "<=": lambda a, b: a <= b}
    held = [c for c in rule["non_concluant_si"] if ops[c["operateur"]](fields[c["champ"]], c["seuil"])]
    if held:
        return "non concluant", held
    if all(ops[c["operateur"]](fields[c["champ"]], c["seuil"]) for c in rule["survit_si"]):
        return "survit", []
    return "éliminée", []


def fmt(x):
    return f"{x}" if isinstance(x, int) else f"{x:.6f}"


def reproduction_table(tid, fields, sealed):
    """Markdown table: field, sealed verifier value, pipeline value, gap, tolerance, OK / NOT OK."""
    tol = sealed["regle"]["tolerance"]
    lines = [f"## {tid}", "", "| field | sealed verifier value | pipeline value | absolute gap | tolerance | status |",
             "|---|---|---|---|---|---|"]
    n_ok = 0
    for field, ref in sealed["chiffres_verificateur"].items():
        gap = abs(float(fields[field]) - float(ref))
        ok = gap <= tol[field]
        n_ok += ok
        lines.append(f"| `{field}` | {fmt(ref)} | {fmt(fields[field])} | {gap:.1e} | {tol[field]} | "
                     f"{'OK' if ok else 'NOT OK'} |")
    return lines, n_ok, len(sealed["chiffres_verificateur"])


def ci(r):
    return f"[{r['lo90']:.2f}, {r['hi90']:.2f}]"


def md(text):
    """Escape the pipes of a label for a Markdown table cell."""
    return text.replace("|", "\\|")


def records(df):
    return json.loads(df.to_json(orient="records"))


# ------------------------------------------------------------------------------------------ K20
def run_k20():
    """The US study: preregistered test K20 plus descriptive analyses. Returns (results entry,
    RESULTS.md lines, reproduction summary row, reproduction.md lines)."""
    tid = "K20"
    df = measures.build_k20()
    (ROOT / "data" / "processed").mkdir(parents=True, exist_ok=True)
    df.to_csv(ROOT / "data" / "processed" / "K20_analysis.csv", index=False)

    # ---- preregistered
    fields, x = k20.run(df)
    sealed = json.loads((ROOT / "audit" / tid / "verdict.json").read_text(encoding="utf-8"))
    fields = {k: int(v) if isinstance(sealed["chiffres_verificateur"].get(k), int) else float(v)
              for k, v in fields.items()}
    verdict, held = verdict_from_rule(sealed["regle"], fields)
    # what the rule gives if the one failed schema check is set aside (reported, never used as the verdict)
    verdict_without_schema, _ = verdict_from_rule(sealed["regle"], {**fields, "n_violations_schema": 0})
    repro, n_ok, n = reproduction_table(tid, fields, sealed)
    schema = k20.schema_violations(df)
    failing = k20.check9_failures(df)[["variable", "target", "level", "level_before", "complete", "main"]]
    print(f"{tid}: {n_ok}/{n} fields reproduced; verdict from rule: {verdict} (sealed: {sealed['verdict']})")

    # ---- descriptive, not preregistered
    base = x["base"]
    cg_full = descriptive.cg_slopes(base)
    cg_pre2020 = descriptive.cg_slopes(base[base["t_target"] <= 8079])
    cg_raw = descriptive.raw_unit_slopes(cg_full, x["consts"])
    small_large = descriptive.small_large_slopes(x["main_fit"], x["by_variable_fit"])
    c_var = descriptive.c_by_variable(fields)
    c_epi = descriptive.c_without_episodes(base, x["without_episode"])
    sorts = descriptive.sort_comparison(base)
    decades = descriptive.by_decade(base)
    sims, sim_large = {}, {}
    for noise in ("scaled", "fixed"):
        sims[noise] = simulation.summarise(simulation.replicate(noise=noise))
        big = simulation.interaction_by_sort(simulation.simulate_panel(40000, 20261113, noise))
        sim_large[noise] = {k: {"c": v[0], "se": v[1]} for k, v in big.items()}

    figs = ["fig1_slopes_small_vs_large_surprises.png", "fig2_c_without_each_episode.png",
            "fig3_sort_on_revision_vs_surprise.png", "fig4_base_slope_by_decade.png"]
    figures.fig1_small_large(small_large, FIGURES / figs[0])
    figures.fig2_without_episodes(c_epi, fields["c"], FIGURES / figs[1])
    figures.fig3_sorts(sorts, sims, FIGURES / figs[2])
    figures.fig4_by_decade(decades, float(cg_full.iloc[-1]["estimate"]), FIGURES / figs[3])

    entry = {
        "question": "Does the under-reaction of the US SPF consensus grow after large surprises (extra slope c > 0)?",
        "preregistered": {"fields": fields, "verdict_from_pipeline_numbers": verdict,
                          "non_conclusion_conditions_held": held, "sealed_verdict": sealed["verdict"],
                          "fields_reproduced": f"{n_ok}/{n}", "schema_checks_passed": schema,
                          "check9_failing_rows": records(failing),
                          "rule_applied_with_schema_check_set_aside": verdict_without_schema},
        "descriptive_not_preregistered": {
            "base_slope_full_sample": records(cg_full), "base_slope_before_2020": records(cg_pre2020),
            "base_slope_raw_units": records(cg_raw), "slopes_small_vs_large_surprises": records(small_large),
            "c_by_variable": records(c_var), "c_without_each_episode": records(c_epi),
            "c_by_sort_variable": records(sorts), "base_slope_by_decade": records(decades),
            "simulation_300_panels_of_1000_rows": sims, "simulation_one_panel_of_200000_rows": sim_large,
            "simulation_parameters": simulation.DEFAULTS,
            "simulation_noise_share_of_revision_variance": {n: simulation.noise_share(noise=n) for n in ("scaled", "fixed")}},
        "figures": [f"figures/{f}" for f in figs]}

    f = fields
    L = [f"## K20 — US Survey of Professional Forecasters, five variables, targets 1969-2026", "",
         "### The preregistered test", "",
         f"- Sample: {f['n_principal']} variable-quarter rows ({f['n_trimestres']} target quarters), "
         f"{f['n_grands']} of them after a large surprise (top third of |surprise| of the variable).",
         f"- **Extra slope after large surprises c = {f['c']:.3f}** (Driscoll-Kraay 4-lag se {f['et_c_dk4']:.3f}, "
         f"t = {f['t_c']:.2f}); 90% interval [{f['borne_basse_ic90']:.3f}, {f['borne_haute_ic90']:.3f}]. The card "
         f"predicted +0.40.",
         f"- Base slope after small surprises (mean of the five b_v) {f['b_moyen']:.3f}; after large surprises "
         f"{f['pente_moyenne_grandes']:.3f}. Revision variance ratio large/small {f['rapport_variance_revision']:.2f} "
         f"(relevance condition: at least 1.25). Mechanical-bias floor {f['seuil_survie_bas']:.2f} (computed bias "
         f"with 20% noise: {f['biais_mecanique_nu20']:.3f}). Effective observations {f['n_effectif']:.0f}.",
         f"- **Verdict from the sealed rule applied to this pipeline's numbers: {verdict}** (sealed verdict: "
         f"{sealed['verdict']}). The only condition that holds is `n_violations_schema` = "
         f"{f['n_violations_schema']} > 0: schema check 9 fails on one row, "
         + ", ".join(f"{r.variable} {r.target}" for r in failing.itertuples())
         + " (October 2025 is missing in FRED, so the previous-quarter CPI level is missing although the "
           "2026-Q1 level exists). That row is not complete, so it enters no regression; every number above "
           "is the same whether or not it is in the file.",
         f"- For information only (not the verdict): with that check set aside, the same rule gives "
         f"**{verdict_without_schema}** (upper bound {f['borne_haute_ic90']:.3f} < 0.40). See `audit/README.md`.",
         "", "Preregistered secondary analyses (computed by the rule, outside the verdict):", "",
         "| analysis | c | se |", "|---|---|---|",
         f"| S2: 8 lags / 0 lags | {f['c']:.3f} | {f['et_c_dk8']:.3f} / {f['et_c_dk0']:.3f} |",
         f"| S3: with RGDP and UNEMP 2020-2021 | {f['c_avec_pandemie']:.3f} | {f['et_c_avec_pandemie_dk4']:.3f} |",
         f"| S4: targets from 1985 | {f['c_depuis_1985']:.3f} | {f['et_c_depuis_1985_dk4']:.3f} |",
         f"| S5: targets to 2019Q4 | {f['c_avant_2020']:.3f} | {f['et_c_avant_2020_dk4']:.3f} |",
         f"| S6: median consensus | {f['c_mediane']:.3f} | {f['et_c_mediane_dk4']:.3f} |",
         f"| S7: card's cut, \\|revision\\| > 1 s.d. | {f['c_coupure_revision']:.3f} | {f['et_c_coupure_revision_dk4']:.3f} |",
         "", "### 1. Base under-reaction slope, by variable and pooled", "", LABEL, "",
         "Slope of the standardised error on the standardised revision, one constant per variable, no split by "
         "surprise size (the Coibion-Gorodnichenko regression in K20's units: s.d. of error per s.d. of revision). "
         "Positive = under-reaction. 'Before 2020' = targets to 2019Q4, with the full-sample standardisation. "
         "Raw units = points of error per point of revision.", "",
         "| variable | full sample: slope (se) | 90% interval | rows | before 2020: slope (se) | 90% interval | rows | raw units, full sample |",
         "|---|---|---|---|---|---|---|---|"]
    raw = cg_raw.set_index("label")
    for (_, a), (_, b) in zip(cg_full.iterrows(), cg_pre2020.iterrows()):
        r = f"{raw.at[a['label'], 'estimate']:.2f} ({raw.at[a['label'], 'se']:.2f})" if a["label"] in raw.index else "–"
        L.append(f"| {a['label']} | {a['estimate']:.3f} ({a['se']:.3f}) | {ci(a)} | {a['n']} | "
                 f"{b['estimate']:.3f} ({b['se']:.3f}) | {ci(b)} | {b['n']} | {r} |")
    L += ["", "### 2. Extra slope c by variable and with each episode removed", "", LABEL,
          "The point estimates are preregistered fields (secondary S1 and the episode guard); the intervals and "
          "this presentation are added here.", "",
          "| variable | slope after small surprises (se) | slope after large surprises (se) | c_v (se) | 90% interval of c_v |",
          "|---|---|---|---|---|"]
    sl = small_large.set_index(["label", "class"])
    for _, r in c_var.iterrows():
        v = r["label"]
        L.append(f"| {v} | {sl.at[(v, 'small'), 'estimate']:.3f} ({sl.at[(v, 'small'), 'se']:.3f}) | "
                 f"{sl.at[(v, 'large'), 'estimate']:.3f} ({sl.at[(v, 'large'), 'se']:.3f}) | "
                 f"{r['estimate']:.3f} ({r['se']:.3f}) | {ci(r)} |")
    L.append(f"| pooled | {sl.at[('pooled', 'small'), 'estimate']:.3f} ({sl.at[('pooled', 'small'), 'se']:.3f}) | "
             f"{sl.at[('pooled', 'large'), 'estimate']:.3f} ({sl.at[('pooled', 'large'), 'se']:.3f}) | "
             f"{f['c']:.3f} ({f['et_c_dk4']:.3f}) | [{f['borne_basse_ic90']:.2f}, {f['borne_haute_ic90']:.2f}] |")
    L += ["", "| episode removed | target window | main rows removed | c (se) | t | 90% interval |", "|---|---|---|---|---|---|"]
    for _, r in c_epi.iterrows():
        L.append(f"| {r['label']} | {r['window']} | {r['rows_removed']} | {r['estimate']:.3f} ({r['se']:.3f}) | "
                 f"{r['t']:.2f} | {ci(r)} |")
    L += ["", "### 3. Sorting on the size of the revision instead of the surprise", "", LABEL,
          "Same regression, three definitions of 'large'. Sorting on the revision also sorts on the consensus "
          "noise that the revision shares (with the opposite sign) with the error, which pushes c up even when "
          "the true slope does not depend on size (preregistration, section 7). The variance ratio is the "
          "variance of the standardised revision after large news over that after small news.", "",
          "| definition of 'large' | share of rows | variance ratio | c (se) | 90% interval |", "|---|---|---|---|---|"]
    for _, r in sorts.iterrows():
        L.append(f"| {md(r['label'])} | {r['share_large']:.2f} | {r['variance_ratio']:.1f} | {r['estimate']:.3f} "
                 f"({r['se']:.3f}) | {ci(r)} |")
    p = simulation.DEFAULTS
    L += ["", f"Simulation (`src/snu/simulation.py`, also run as a test): panels with **no true size effect** "
          f"(constant true slope), fat-tailed news (Student t, {p['df']} degrees of freedom), consensus noise "
          f"in both surveys (noise s.d. {p['noise_sd']} x the quarter's volatility: "
          f"{100 * simulation.noise_share():.0f}% of the variance of the revision with scaled noise, "
          f"{100 * simulation.noise_share(noise='fixed'):.0f}% with fixed noise), and a lagged surprise that reveals the quarter's volatility but not the noise of the "
          f"survey being evaluated. 'Scaled' noise grows with turbulence (forecast disagreement does); 'fixed' "
          f"noise has the same size in every quarter.", "",
          "| noise model | sort | mean c, 300 panels of 1 000 rows | 5-95% range | c in one panel of 200 000 rows (se) |",
          "|---|---|---|---|---|"]
    for noise in ("scaled", "fixed"):
        for sort, name in (("surprise_sort", "lagged |surprise|, top third (K20)"), ("revision_sort", "|revision| > 1 s.d. (card)")):
            s, b = sims[noise][sort], sim_large[noise][sort]
            L.append(f"| {noise} | {md(name)} | {s['mean']:+.3f} | [{s['p05']:+.2f}, {s['p95']:+.2f}] | "
                     f"{b['c']:+.3f} ({b['se']:.3f}) |")
    L += ["", "With scaled noise the surprise sort is unbiased and the revision sort is not. With fixed noise "
          "the surprise sort keeps a smaller positive residual (differential attenuation, section 7 of the "
          "preregistration), which the preregistered floor max(0.10, computed bias) is meant to absorb.", "",
          "### 4. Base under-reaction slope by decade", "", LABEL,
          "Pooled slope (one constant per variable, one common slope, no size split) by decade of the target "
          "quarter; CPI and T-bill targets start in 1982Q3.", "",
          "| decade | rows | quarters | variables | slope (se) | 90% interval |", "|---|---|---|---|---|---|"]
    for _, r in decades.iterrows():
        L.append(f"| {r['label']} | {r['n']} | {r['quarters']} | {r['variables']} | {r['estimate']:.3f} "
                 f"({r['se']:.3f}) | {ci(r)} |")
    L += [""]
    ctx = {"fields": fields, "base_pooled": cg_full.iloc[-1].to_dict(), "c_by_variable": c_var, "figures": figs}
    return entry, L, (tid, n_ok, n, verdict, sealed["verdict"]), repro, ctx


# ------------------------------------------------------------------------------------------ K20-ZE
def run_k20ze():
    """The euro-area study: preregistered test K20-ZE (blind replication on the ECB SPF) plus descriptive
    analyses. Returns the same five items as run_k20."""
    tid = "K20-ZE"
    raw = k20ze.load_raw()
    df = k20ze.build_k20ze(raw)
    df.to_csv(ROOT / "data" / "processed" / "K20-ZE_analysis.csv", index=False)

    # ---- preregistered
    fields, x = k20ze.run(df, raw)
    sealed = json.loads((ROOT / "audit" / tid / "verdict.json").read_text(encoding="utf-8"))
    fields = {k: int(v) if isinstance(sealed["chiffres_verificateur"].get(k), int) else float(v)
              for k, v in fields.items()}
    verdict, held = verdict_from_rule(sealed["regle"], fields)
    repro, n_ok, n = reproduction_table(tid, fields, sealed)
    print(f"{tid}: {n_ok}/{n} fields reproduced; verdict from rule: {verdict} (sealed: {sealed['verdict']})")

    # ---- descriptive, not preregistered
    base = x["base"]
    c_var = descriptive.ea_c_by_variable(fields)
    pand = descriptive.ea_pandemic(fields, x["data"])
    slopes = descriptive.ea_base_slopes(base)
    periods = descriptive.ea_by_period(base)
    entry = {
        "question": "Does the under-reaction of the ECB SPF consensus grow after large news (extra slope c > 0)?",
        "preregistered": {"fields": fields, "verdict_from_pipeline_numbers": verdict,
                          "non_conclusion_conditions_held": held, "sealed_verdict": sealed["verdict"],
                          "fields_reproduced": f"{n_ok}/{n}"},
        "descriptive_not_preregistered": {"c_by_variable": records(c_var), "c_with_and_without_pandemic": records(pand),
                                          "base_slope_by_variable": records(slopes),
                                          "base_slope_by_period": records(periods)}}
    f = fields
    L = ["## K20-ZE — ECB Survey of Professional Forecasters, three variables, target years 2000-2025", "",
         "A blind replication of K20, preregistered and sealed on 2026-11-13 before any statistic was computed "
         "(see `../audit/README.md`). Annual targets (calendar-year averages), eight survey rounds per target, "
         "six series (variable x horizon); the news is the change in the latest published figure that the ECB "
         "sends to the forecasters between two rounds, so it contains no survey noise.", "",
         "### The preregistered test", "",
         f"- Sample: {f['n_principal']} variable x target-year x round rows ({f['n_tours']} rounds, "
         f"{f['n_annees_cibles']} target years), {f['n_grands']} after large news. Schema: "
         f"`n_violations_schema` = {f['n_violations_schema']}, `n_anomalies_hors_principal` = "
         f"{f['n_anomalies_hors_principal']}.",
         f"- **Extra slope after large news c = {f['c']:.3f}** (Driscoll-Kraay 8-lag se {f['et_c_dk8']:.3f}, "
         f"t = {f['t_c']:.2f}); 90% interval (critical value {k20ze.CRIT}) [{f['borne_basse_ic90']:.3f}, "
         f"{f['borne_haute_ic90']:.3f}]. The prediction was +0.40.",
         f"- **Positive control passed** (`controle_positif_ok` = {f['controle_positif_ok']}): common slope "
         f"b_commun = {f['b_commun']:.3f} (se {f['et_b_commun_dk8']:.3f}, lower 90% bound "
         f"{f['borne_basse_b_commun_ic90']:.3f}); slope after small news {f['b_moyen']:.3f} (lower bound "
         f"{f['borne_basse_b_moyen_ic90']:.3f}); after large news {f['pente_moyenne_grandes']:.3f}. The consensus "
         "under-reacts, so a null c is not the silence of a blind instrument.",
         f"- Revision variance ratio large/small {f['rapport_variance_revision']:.2f}; computed mechanical bias "
         f"{f['biais_mecanique_nu20']:.3f}, so the survival floor is {f['seuil_survie_bas']:.3f}. Without each "
         f"episode c = {f['c_sans_E1']:.3f} (E1), {f['c_sans_E2']:.3f} (E2), {f['c_sans_E3']:.3f} (E3). Effective "
         f"observations {f['n_effectif']:.0f}.",
         f"- **Verdict from the sealed rule applied to this pipeline's numbers: {verdict}** (sealed verdict: "
         f"{sealed['verdict']}); no non-conclusion condition holds. Elimination case (a): the upper bound "
         f"{f['borne_haute_ic90']:.3f} is below 0.40.",
         f"- The floor ({f['seuil_survie_bas']:.2f}) turned out far above the 0.10 assumed in the preregistration's "
         "decisiveness simulation (calibrated on K20's variance ratio of about 3; here it is "
         f"{f['rapport_variance_revision']:.1f}): had c been near +0.40, the test would mostly have ended "
         "'non concluant'. The elimination does not depend on the floor: it comes from the upper bound, which the "
         "floor does not enter, and the mechanical bias pushes c up, not down.",
         "- Surprises are taken in double precision without rounding, as the letter of the preregistration says "
         "and as both the experimenter and the verifier did (`audit/K20-ZE/ecarts.md`, C1); the rounded reading "
         "gives c = -0.099 and the same verdict.", "",
         "Preregistered secondary analyses (computed by the rule, outside the verdict):", "",
         "| analysis | c | se |", "|---|---|---|",
         f"| S2: 4 / 12 / 0 lags; clustered by target year | {f['c']:.3f} | {f['et_c_dk4']:.3f} / {f['et_c_dk12']:.3f} / "
         f"{f['et_c_dk0']:.3f}; {f['et_c_grappes_annee']:.3f} |",
         f"| S3: with GDP and unemployment 2020-2021 | {f['c_avec_pandemie']:.3f} | {f['et_c_avec_pandemie_dk8']:.3f} |",
         f"| S4: target years to 2019 | {f['c_avant_2020']:.3f} | {f['et_c_avant_2020_dk8']:.3f} |",
         f"| S5: current year / next year | {f['c_annee_en_cours']:.3f} / {f['c_annee_suivante']:.3f} | "
         f"{f['et_c_annee_en_cours_dk8']:.3f} / {f['et_c_annee_suivante_dk8']:.3f} |",
         f"| S6: median consensus | {f['c_mediane']:.3f} | {f['et_c_mediane_dk8']:.3f} |",
         f"| S7: card's cut, \\|revision\\| > 1 s.d. | {f['c_coupure_revision']:.3f} | {f['et_c_coupure_revision_dk8']:.3f} |",
         f"| S8: surprise relative to the consensus ({f['n_surprise_consensus']} rows) | {f['c_surprise_consensus']:.3f} | "
         f"{f['et_c_surprise_consensus_dk8']:.3f} |",
         "", "### 1. Extra slope c by variable", "", LABEL,
         "The point estimates are the preregistered secondary S1; the intervals (critical value 1.708) are added here.", "",
         "| variable | c_v (se) | 90% interval |", "|---|---|---|"]
    for _, r in c_var.iterrows():
        L.append(f"| {r['label']} | {r['estimate']:.3f} ({r['se']:.3f}) | {ci(r)} |")
    L += ["", "### 2. c with and without the pandemic rows", "", LABEL,
          "The first two rows are preregistered (the main test and S3); the rows by variable are added here. Putting "
          f"back the 2020-2021 GDP and unemployment rows ({int(pand.iloc[1]['n']) - f['n_principal']} rows) turns c "
          "positive, and the change comes from "
          "unemployment. The preregistration excluded these rows before seeing any data, because a handful of "
          "targets that moved by several points in one round outweigh two decades; even with them, c stays well "
          "below +0.40.", "",
          "| sample | rows | c (se) | 90% interval |", "|---|---|---|---|"]
    for _, r in pand.iterrows():
        L.append(f"| {r['label']} | {r['n']} | {r['estimate']:+.3f} ({r['se']:.3f}) | {ci(r)} |")
    L += ["", "### 3. Base under-reaction slope by variable and by period", "", LABEL,
          "One constant per series (variable x horizon), no split by news size; 'pooled' is the preregistered "
          "positive control b_commun. Periods are of the target year (10, 10 and 6 target years).", "",
          "| variable or period | rows | slope (se) | 90% interval |", "|---|---|---|---|"]
    for _, r in slopes.iterrows():
        L.append(f"| {r['label']} | {r['n']} | {r['estimate']:.3f} ({r['se']:.3f}) | {ci(r)} |")
    for _, r in periods.iterrows():
        L.append(f"| target years {r['label']} ({r['rounds']} rounds) | {r['n']} | {r['estimate']:.3f} ({r['se']:.3f}) | {ci(r)} |")
    L += [""]
    ctx = {"fields": fields, "c_by_variable": c_var, "base_pooled": slopes.iloc[-1].to_dict()}
    return entry, L, (tid, n_ok, n, verdict, sealed["verdict"]), repro, ctx


# ------------------------------------------------------------------------------------------ comparison
def compare_studies(ctx):
    """US (K20) and euro area (K20-ZE) side by side, and figures 5-6. Returns (results entry, RESULTS.md lines,
    figure names)."""
    us, ea = ctx["K20"], ctx["K20-ZE"]
    u, e = us["fields"], ea["fields"]
    table = descriptive.comparison(u, us["base_pooled"], e)
    figs = ["fig5_forest_c_us_vs_euro_area.png", "fig6_base_slope_vs_c_two_surveys.png"]
    us_pooled = {"estimate": u["c"], "lo90": u["borne_basse_ic90"], "hi90": u["borne_haute_ic90"]}
    ea_pooled = {"estimate": e["c"], "lo90": e["borne_basse_ic90"], "hi90": e["borne_haute_ic90"]}
    figures.fig5_forest_c(us_pooled, us["c_by_variable"], ea_pooled, ea["c_by_variable"], FIGURES / figs[0])
    b_us, b_ea = us["base_pooled"], ea["base_pooled"]
    two = [{"survey": "US SPF, 1969-2026 (K20)", "quantity": "base", **{k: b_us[k] for k in ("estimate", "lo90", "hi90")}},
           {"survey": "US SPF, 1969-2026 (K20)", "quantity": "c", **us_pooled},
           {"survey": "ECB SPF, 2000-2025 (K20-ZE)", "quantity": "base", **{k: b_ea[k] for k in ("estimate", "lo90", "hi90")}},
           {"survey": "ECB SPF, 2000-2025 (K20-ZE)", "quantity": "c", **ea_pooled}]
    figures.fig6_base_vs_c(pd.DataFrame(two), e["c_avec_pandemie"], e["et_c_avec_pandemie_dk8"], FIGURES / figs[1])
    L = ["## Two surveys, two continents, the same answer", "", LABEL,
         "Side by side, the quantities that decide or frame the two preregistered tests. Both consensus forecasts "
         "under-react on average (positive base slope; in the euro area the preregistered positive control "
         "passes), and in neither does the under-reaction grow after large news: both intervals for c contain 0 "
         "and exclude the predicted +0.40. The euro-area floor for the mechanical bias "
         f"({e['seuil_survie_bas']:.2f}) is far above the 0.10 that the decisiveness simulation of its "
         "preregistration assumed (the variance ratio of revisions is "
         f"{e['rapport_variance_revision']:.1f}, not about 3); that would have mattered for a survival, not for "
         "the elimination, which rests on the upper bound of c alone.", "",
         "| quantity | US SPF (K20) | ECB SPF (K20-ZE) |", "|---|---|---|"]
    L += [f"| {r.quantity} | {r[2]} | {r[3]} |" for r in table.itertuples()]
    L += ["", "The US base slope is the descriptive pooled slope of section K20.1; the euro-area one is the "
          "preregistered b_commun. Both have one constant per series and one common slope, in standardised units.", ""]
    entry = {"table": records(table), "figures": [f"figures/{f}" for f in figs]}
    return entry, L, figs


STUDIES = {"K20": run_k20, "K20-ZE": run_k20ze}
# "K20-LIV": run_k20liv,   # US Livingston Survey: being preregistered; add its module, function and audit/K20-LIV/


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--seed":
        data.seed_from(sys.argv[2])
    for tid in STUDIES:
        check_seal(tid)
    data.get_all()
    data.write_provenance(data.compare_with_sealed(SEALED_TESTS) if SEALED_TESTS.exists() else None)
    (ROOT / "data" / "processed").mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)

    results, body, summary, repro, ctx, figs = {}, [], [], [], {}, []
    for tid, study in STUDIES.items():
        entry, lines, row, rlines, ctx[tid] = study()
        results[tid] = entry
        body += lines
        summary.append(row)
        figs += ctx[tid].get("figures", [])
        repro += rlines + ["", f"**{tid}: {row[1]} / {row[2]} fields within tolerance.**", ""]
    if {"K20", "K20-ZE"} <= set(ctx):
        results["comparison"], lines, more = compare_studies(ctx)
        body += lines
        figs += more
    body += ["## Figures", ""] + [f"{i}. `figures/{name}`" for i, name in enumerate(figs, start=1)] + [""]

    (RESULTS / "results.json").write_text(json.dumps(results, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    head = ["# Reproduction of the sealed verifier numbers", "",
            "Each pipeline value is computed by `run_all.py` from the raw files in `data/raw/` with the code in",
            "`src/snu/`. The sealed value is the independent verifier's number in `audit/<ID>/verdict.json`",
            "(`chiffres_verificateur`); the tolerance is the one written in the preregistration (its json block,",
            "copied in `verdict.json` under `regle`). Integers are shown without decimals.", "",
            "| test | fields within tolerance | verdict from pipeline numbers | sealed verdict |", "|---|---|---|---|"]
    head += [f"| {t} | {a} / {b} | {v} | {s} |" for t, a, b, v, s in summary] + [""]
    (RESULTS / "reproduction.md").write_text("\n".join(head + repro), encoding="utf-8")
    intro = ["# Results", "",
             "Does forecasters' under-reaction grow with the size of news? Two preregistered tests answer it on two",
             "surveys: K20 on the US Survey of Professional Forecasters (1969-2026) and K20-ZE, a blind replication",
             "on the ECB Survey of Professional Forecasters (2000-2025). For each, the primary statistic, its",
             "interval and the guards are computed exactly as sealed (see `../audit/`); only they enter the verdict.",
             "Every section marked *Descriptive, not preregistered* was added for this project and describes the",
             "data; none of it can change a verdict.", "",
             "| test | survey | extra slope after large news, c | 90% interval | verdict (sealed rule) |",
             "|---|---|---|---|---|"]
    for tid, survey in (("K20", "US SPF, 1969-2026"), ("K20-ZE", "ECB SPF, 2000-2025")):
        if tid in results:
            f = results[tid]["preregistered"]["fields"]
            intro.append(f"| {tid} | {survey} | {f['c']:.3f} | [{f['borne_basse_ic90']:.3f}, {f['borne_haute_ic90']:.3f}] | "
                         f"{results[tid]['preregistered']['verdict_from_pipeline_numbers']} |")
    (RESULTS / "RESULTS.md").write_text("\n".join(intro + [""] + body), encoding="utf-8")


if __name__ == "__main__":
    main()
