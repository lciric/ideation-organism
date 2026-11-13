"""Run the whole project: python run_all.py

1. checks the sha256 of the four sealed preregistrations copied in audit/;
2. downloads every raw file (or reuses data/raw/) and writes data/raw/PROVENANCE.md;
3. builds the four analysis datasets (data/processed/*.csv);
4. computes every preregistered field of the four tests and the verdict their rules give;
5. writes results/results.json, results/RESULTS.md, results/reproduction.md and results/figures/*.png.

Optional: python run_all.py --seed <path to tests-de-mort> fills empty cache slots by copying the raw
files the sealed tests downloaded (recorded as such in PROVENANCE.md) instead of downloading them.
"""
import hashlib
import json
import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
warnings.filterwarnings("ignore", message="Cannot parse header or footer")

from ifu import data, figures, h03v2, j02, k01, k20, measures  # noqa: E402

TESTS = {  # id: (module, dataset builder, short question)
    "H03-v2": (h03v2, measures.build_h03v2,
               "Could a recursive real-time correction rule based on revisions reduce ECB staff inflation projection errors?"),
    "J02": (j02, measures.build_j02,
            "Is the full-sample error-on-revision slope of ECB staff projections (2 quarters ahead) positive and as large as 0.40?"),
    "K01": (k01, measures.build_k01,
            "Do individual ECB SPF forecasters over-react to their own news (2SLS slope < 0)?"),
    "K20": (k20, measures.build_k20,
            "Does the US SPF consensus under-react more after large surprises (extra slope c > 0)?"),
}
RESULTS = ROOT / "results"


def check_seals():
    """Each copied preregistration must hash to the sealed value (its .sha256 file and its verdict.json)."""
    for tid in TESTS:
        folder = ROOT / "audit" / tid
        sha = hashlib.sha256((folder / "preenregistrement.md").read_bytes()).hexdigest()
        sealed = (folder / "preenregistrement.md.sha256").read_text().split()[0]
        in_verdict = json.loads((folder / "verdict.json").read_text(encoding="utf-8"))["sceau_preenregistrement"]
        if not sha == sealed == in_verdict:
            raise SystemExit(f"{tid}: preregistration sha256 {sha} does not match the seal {sealed}")
        print(f"seal OK  {tid}  {sha}")


def verdict_from_rule(rule, fields):
    """The machine-readable rule of each preregistration: 'non concluant' if any non-conclusion condition
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


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--seed":
        data.seed_from(sys.argv[2])
    check_seals()
    data.get_all()
    data.write_provenance()
    (ROOT / "data" / "processed").mkdir(parents=True, exist_ok=True)
    (RESULTS / "figures").mkdir(parents=True, exist_ok=True)

    results, extras, repro, summary = {}, {}, [], []
    for tid, (module, build, question) in TESTS.items():
        df = build()
        df.to_csv(ROOT / "data" / "processed" / f"{tid}_analysis.csv", index=False)
        fields, extra = module.run(df)
        sealed = json.loads((ROOT / "audit" / tid / "verdict.json").read_text(encoding="utf-8"))
        # counts and indicators as integers (the sealed file says which fields are integers), the rest as floats
        fields = {k: int(v) if isinstance(sealed["chiffres_verificateur"].get(k), int) else float(v)
                  for k, v in fields.items()}
        verdict, held = verdict_from_rule(sealed["regle"], fields)
        lines, n_ok, n = reproduction_table(tid, fields, sealed)
        repro += lines + ["", f"**{tid}: {n_ok} / {n} fields within tolerance.**", ""]
        results[tid] = {"question": question, "fields": fields, "verdict_from_pipeline_numbers": verdict,
                        "non_conclusion_conditions_held": held, "sealed_verdict": sealed["verdict"],
                        "fields_reproduced": f"{n_ok}/{n}"}
        extras[tid] = extra
        summary.append((tid, n_ok, n, verdict, sealed["verdict"]))
        print(f"{tid}: {n_ok}/{n} fields reproduced; verdict from rule: {verdict} (sealed: {sealed['verdict']})")

    (RESULTS / "results.json").write_text(json.dumps(results, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    head = ["# Reproduction of the sealed verifier numbers", "",
            "Each pipeline value is computed by `run_all.py` from the raw files in `data/raw/` with the code in",
            "`src/ifu/`. The sealed value is the independent verifier's number in `audit/<ID>/verdict.json`",
            "(`chiffres_verificateur`); the tolerance is the one written in that test's preregistration (json block).",
            "Integers are shown without decimals.", "",
            "| test | fields within tolerance | verdict from pipeline numbers | sealed verdict |", "|---|---|---|---|"]
    head += [f"| {t} | {a} / {b} | {v} | {s} |" for t, a, b, v, s in summary] + [""]
    (RESULTS / "reproduction.md").write_text("\n".join(head + repro), encoding="utf-8")
    write_results_md(results, extras)
    make_figures(results, extras)


def write_results_md(results, extras):
    """Main statistics and descriptive breakdowns, in English."""
    f = {t: results[t]["fields"] for t in results}
    L = ["# Results", "",
         "Do inflation forecasters under-react to news? Four preregistered tests, recomputed from raw data.",
         "Primary statistics are computed exactly as preregistered (see `audit/`). Only the primary statistic,",
         "its interval and the preregistered guards enter a verdict; every other number below is descriptive.", "",
         "| test | question | primary statistic | 90% interval | verdict (sealed rule) |", "|---|---|---|---|---|"]
    h, j, k, u = f["H03-v2"], f["J02"], f["K01"], f["K20"]
    L.append(f"| H03-v2 | {results['H03-v2']['question']} | mean block correlation R = {h['r_moyen']:.3f} "
             f"(se {h['et_r_moyen']:.3f}) | [{h['borne_basse_ic90']:.3f}, {h['borne_haute_ic90']:.3f}] | "
             f"{results['H03-v2']['verdict_from_pipeline_numbers']} |")
    L.append(f"| J02 | {results['J02']['question']} | standardised slope {j['beta_z']:.3f} (NW4 se {j['et_beta_z_nw4']:.3f}, "
             f"t = {j['t_nw4']:.2f}) | [{j['borne_basse_ic90']:.3f}, {j['borne_haute_ic90']:.3f}] | "
             f"{results['J02']['verdict_from_pipeline_numbers']} |")
    L.append(f"| K01 | {results['K01']['question']} | 2SLS slope {k['b_iv']:.3f} (DK8 se {k['et_b_iv_dk8']:.3f}; "
             f"first-stage F {k['f_premiere_etape']:.0f}) | [{k['borne_basse_ic90']:.3f}, {k['borne_haute_ic90']:.3f}] | "
             f"{results['K01']['verdict_from_pipeline_numbers']} |")
    L.append(f"| K20 | {results['K20']['question']} | extra slope c = {u['c']:.3f} (DK4 se {u['et_c_dk4']:.3f}) | "
             f"[{u['borne_basse_ic90']:.3f}, {u['borne_haute_ic90']:.3f}] | "
             f"{results['K20']['verdict_from_pipeline_numbers']} (schema guard: n_violations_schema = "
             f"{u['n_violations_schema']}) |")
    L += ["", "## H03-v2 — real-time correction rule (ECB staff, horizons 1-4, targets 2004-2025)", "",
          f"- {h['n_obs_evaluees']} evaluated rows in {h['n_blocs']} valid blocks. Without blocks 2020-2023: "
          f"R = {h['r_hors_episode']:.3f}. Geometric mean of block MSE ratios (corrected / published): "
          f"{h['rapport_eqm_geo']:.3f} (above 1: the correction makes errors larger in a typical block).",
          f"- Descriptive: overall MSE ratio {h['rapport_eqm_global']:.3f}, without 2021-2022 targets "
          f"{h['rapport_eqm_hors_2021_2022']:.3f}; share of rows improved {h['taux_amelioration']:.3f}; share of "
          f"positive real-time slopes {h['part_b_positif']:.3f}; by horizon R = {h['r_moyen_h1']:.3f}, "
          f"{h['r_moyen_h2']:.3f}, {h['r_moyen_h3']:.3f}, {h['r_moyen_h4']:.3f} (h = 1..4); placebo (two-year-old "
          f"revision) R = {h['r_moyen_placebo']:.3f} (se {h['et_r_placebo']:.3f}); the card's own test (h = 4, "
          f"vintages from 2020): MSE ratio {h['rapport_eqm_h4_2020']:.3f}, DM-HLN p = {h['p_dm_hln_h4_2020']:.3f}.",
          "", "| block (target years) | rows | R_k | MSE ratio Q_k |", "|---|---|---|---|"]
    for _, b in extras["H03-v2"]["blocks"].iterrows():
        L.append(f"| {b['years']} | {b['n']} | {b['R']:.3f} | {b['Q']:.3f} |")
    L += ["", "## J02 — full-sample error-on-revision slope (ECB staff, 2 quarters ahead, targets 1999Q4-2026Q3)", "",
          f"- {j['n_cibles']} targets; raw slope {j['beta_brut']:.3f} points per point (se {j['et_beta_brut_nw4']:.3f}); "
          f"NW8 se {j['et_beta_z_nw8']:.3f}; moving-block bootstrap 90% interval [{j['bb_borne_basse_ic90']:.3f}, "
          f"{j['bb_borne_haute_ic90']:.3f}].",
          f"- Survival guard: the smallest correlation after removing two consecutive years is "
          f"{j['beta_z_min_sans_deux_ans']:.3f} (removing {j['annee_debut_min']}-{j['annee_debut_min'] + 1}); after "
          f"removing one year, {j['beta_z_min_sans_une_annee']:.3f}.",
          f"- Descriptive: before 2020 (targets 1999Q4-2019Q4, n = {j['n_avant_2020']}) the standardised slope is "
          f"{j['beta_z_avant_2020']:.3f}, raw {j['beta_brut_avant_2020']:.3f} (se {j['et_beta_brut_avant_2020_nw4']:.3f}), "
          f"to compare with 0.20 (0.21) in Granziera, Jalasjoki and Paloviita (2021); without 2021-2023 targets "
          f"(n = {j['n_hors_2021_2023']}) {j['beta_z_hors_2021_2023']:.3f} (se {j['et_beta_z_hors_2021_2023_nw4']:.3f}).",
          "", "| year(s) removed | correlation, one year removed | correlation, years Y and Y+1 removed |",
          "|---|---|---|"]
    d1, d2 = extras["J02"]["drop_one_year"], extras["J02"]["drop_two_years"]
    for y in sorted(d1):
        L.append(f"| {y} | {d1[y]:.3f} | {d2[y]:.3f} |" if y in d2 else f"| {y} | {d1[y]:.3f} | – |")
    L += ["", "## K01 — individual ECB SPF forecasters (target years 2002-2025)", "",
          f"- {k['n_obs_iv']} revisions, {k['n_previsionnistes_iv']} forecasters, {k['n_tours_iv']} rounds. First stage "
          f"{k['coef_premiere_etape']:.3f} (F = {k['f_premiere_etape']:.0f}); reduced-form t = {k['t_forme_reduite']:.2f}; "
          f"se clustered by round {k['et_b_iv_grappes_tour']:.3f}, by target year {k['et_b_iv_grappes_cible']:.3f}.",
          f"- Without target years 2021-2023: 2SLS {k['b_iv_hors_2021_2023']:.3f} (se {k['et_b_iv_hors_2021_2023_dk8']:.3f}, "
          f"F = {k['f_premiere_etape_hors_2021_2023']:.0f}); largest 2SLS slope when one target year is removed "
          f"{k['b_iv_max_sans_une_annee']:.3f}; with forecaster fixed effects {k['b_iv_ef_prev']:.3f} "
          f"(se {k['et_b_iv_ef_prev_dk8']:.3f}); before 2020 {k['b_iv_avant_2020']:.3f} (se {k['et_b_iv_avant_2020_dk8']:.3f}), "
          f"OLS with fixed effects before 2020 {k['b_mco_ef_avant_2020']:.3f} (se {k['et_b_mco_ef_avant_2020_dk8']:.3f}; "
          f"Broer and Kohlhas: -0.169 (0.182)).",
          f"- The naive within-round slope {k['b_intra_tour_naif']:.3f} (se {k['et_b_intra_tour_naif_grappes_tour']:.3f}) "
          "measures the change in the dispersion of forecasts, not their accuracy (it is -1/2 by construction when "
          "dispersion is stable). Noise bounds: both 0, because the pooled OLS and 2SLS slopes are positive "
          "(there is no negative slope for reporting noise to explain).",
          f"- Consensus slope {k['b_consensus']:.3f} (se {k['et_b_consensus_dk8']:.3f}), ECB staff {k['b_bce']:.3f} "
          f"(se {k['et_b_bce_dk8']:.3f}), difference ECB - consensus {k['diff_bce_moins_consensus']:.3f} "
          f"(se {k['et_diff_dk8']:.3f}); without 2021-2023: consensus {k['b_consensus_hors_2021_2023']:.3f}, ECB "
          f"{k['b_bce_hors_2021_2023']:.3f}.", "",
          "| estimate | sample | slope | se |", "|---|---|---|---|"]
    for _, r in extras["K01"]["slopes"].iterrows():
        L.append(f"| {r['estimate']} | {r['sample']} | {r['b']:.3f} | {r['se']:.3f} |")
    L += ["", "## K20 — US SPF consensus, five variables, large vs small surprises (targets 1969-2026)", "",
          f"- {u['n_principal']} variable-quarter rows ({u['n_trimestres']} quarters; {u['n_grands']} after large "
          f"surprises); base slope (mean of b_v) {u['b_moyen']:.3f}, slope after large surprises "
          f"{u['pente_moyenne_grandes']:.3f}; revision variance ratio large/small {u['rapport_variance_revision']:.2f}; "
          f"mechanical-bias floor {u['seuil_survie_bas']:.2f}; effective observations {u['n_effectif']:.0f}.",
          f"- The sealed verdict is 'non concluant' because schema check 9 fails on one row (CPI 2026-Q1: October 2025 "
          f"is missing in FRED, so the previous-quarter CPI level is missing). That row enters no regression. With the "
          f"check passed the rule would have given 'éliminée' (upper bound {u['borne_haute_ic90']:.3f} < 0.40).",
          f"- Without each episode window, c ranges from {u['c_min_sans_episode']:.3f} to "
          f"{max(u[f'c_sans_E{i}'] for i in range(1, 8)):.3f}; NW8 se {u['et_c_dk8']:.3f}, no-lag se {u['et_c_dk0']:.3f}; "
          f"with the pandemic quarters {u['c_avec_pandemie']:.3f}; since 1985 {u['c_depuis_1985']:.3f}; before 2020 "
          f"{u['c_avant_2020']:.3f}; medians {u['c_mediane']:.3f}; the card's own cut on |revision| > 1 s.d. "
          f"{u['c_coupure_revision']:.3f}.", "",
          "| variable | slope after small surprises | slope after large surprises | c_v (se) |", "|---|---|---|---|"]
    for _, r in extras["K20"]["per_variable"].iterrows():
        L.append(f"| {r['variable']} | {r['b_small']:.3f} | {r['b_large']:.3f} | {r['c']:.3f} "
                 f"({f['K20'][f'et_c_{r.variable}_dk4']:.3f}) |")
    L += ["", "## Figures", "", "1. `figures/fig1_ecb_error_vs_revision.png`", "2. `figures/fig2_j02_leave_years_out.png`",
          "3. `figures/fig3_h03v2_blocks.png`", "4. `figures/fig4_k01_slopes.png`", "5. `figures/fig5_k20_by_variable.png`", ""]
    (RESULTS / "RESULTS.md").write_text("\n".join(L), encoding="utf-8")


def make_figures(results, extras):
    fd = RESULTS / "figures"
    j, h = results["J02"]["fields"], results["H03-v2"]["fields"]
    figures.fig1_ecb_scatter(extras["J02"]["sample"], j["beta_z"], j["beta_z_hors_2021_2023"],
                             fd / "fig1_ecb_error_vs_revision.png")
    figures.fig2_leave_out(extras["J02"]["drop_one_year"], extras["J02"]["drop_two_years"], j["beta_z"],
                           fd / "fig2_j02_leave_years_out.png")
    figures.fig3_h03_blocks(extras["H03-v2"]["blocks"], h["r_moyen"], h["borne_basse_ic90"], h["borne_haute_ic90"],
                            fd / "fig3_h03v2_blocks.png")
    figures.fig4_k01_slopes(extras["K01"]["slopes"], fd / "fig4_k01_slopes.png")
    figures.fig5_k20_by_variable(extras["K20"]["per_variable"], fd / "fig5_k20_by_variable.png")


if __name__ == "__main__":
    main()
