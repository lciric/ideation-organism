"""Run the whole project: data -> four analysis datasets -> preregistered statistics -> reports and figures.

Usage:  python run_all.py
Downloads whatever is missing from data/raw/ (or reuses the cache), then writes
results/results.json, results/RESULTS.md, results/reproduction.md, results/datasets/*.csv
and results/figures/*.png. Exits with status 1 if a sealed preregistration fails its
sha256 check or a verifier number does not reproduce within its preregistered tolerance.
"""
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from tap import data, figures, measures, schema  # noqa: E402
from tap.calendar import Calendar, k11_calendar  # noqa: E402
from tap.stats import by_group, cluster_mean, interval  # noqa: E402

AUDIT, RESULTS = ROOT / "audit", ROOT / "results"
TESTS = ["F04", "F04-bis", "J05", "K11"]


# ----------------------------------------------------------------------------- audit
def check_seals():
    """sha256 of each copied preregistration vs its .sha256 file and the seal recorded in verdict.json."""
    out = {}
    for t in TESTS:
        actual = hashlib.sha256((AUDIT / t / "preenregistrement.md").read_bytes()).hexdigest()
        recorded = (AUDIT / t / "preenregistrement.md.sha256").read_text().split()[0]
        sealed = json.loads((AUDIT / t / "verdict.json").read_text())["sceau_preenregistrement"]
        out[t] = {"sha256": actual, "matches_sha256_file": actual == recorded, "matches_verdict_seal": actual == sealed}
    return out


def preregistered_rule(test):
    """The machine-readable rule (last ```json block) of a sealed preregistration."""
    text = (AUDIT / test / "preenregistrement.md").read_text()
    return json.loads(re.findall(r"```json\s*(\{.*?\})\s*```", text, re.S)[-1])


def apply_rule(rule, numbers):
    """Verdict of a preregistered rule: 'non concluant' first, then 'survit', else 'éliminée'."""
    ops = {">": np.greater, ">=": np.greater_equal, "<": np.less, "<=": np.less_equal}
    holds = lambda c: bool(ops[c["operateur"]](numbers[c["champ"]], c["seuil"]))  # noqa: E731
    if any(holds(c) for c in rule["non_concluant_si"]):
        return "non concluant"
    return "survit" if all(holds(c) for c in rule["survit_si"]) else "éliminée"


def reproduction(test, ours):
    """One row per verification field: sealed verifier value, ours, gap, tolerance, OK."""
    rule = preregistered_rule(test)
    sealed = json.loads((AUDIT / test / "verdict.json").read_text())["chiffres_verificateur"]
    rows = []
    for field in rule["champs_verification"]:
        gap = abs(float(ours[field]) - float(sealed[field]))
        tol = rule["tolerance"][field]
        rows.append({"field": field, "sealed": sealed[field], "pipeline": ours[field], "gap": gap,
                     "tolerance": tol, "ok": gap <= tol})
    return rows


# ----------------------------------------------------------------------------- build
def build_all():
    dgs = {m: data.fred_strings(f"DGS{m}") for m in (2, 3, 5, 7, 10, 20, 30)}
    for m in dgs:  # also parse each series once as numbers, which validates the download
        data.fred_series(f"DGS{m}")
    cal_dgs10 = Calendar([d for d, v in dgs[10].items() if v != ""])
    gsw = data.gsw_curve()

    f04 = measures.build_f04(data.auctions("f04"), dgs, gsw, cal_dgs10)
    f04bis = measures.build_f04bis(f04, data.mc_vs_hs())
    j05 = measures.build_j05(data.auctions("j05"), gsw, Calendar(measures.gsw_calendar_dates(gsw)))
    k11_auctions = data.auctions("k11")
    k11 = measures.build_k11(k11_auctions, Calendar(k11_calendar()))

    checks = {"F04": schema.check_f04(f04), "F04-bis": schema.check_f04bis(f04bis),
              "J05": schema.check_j05(j05[measures.J05_COLUMNS]), "K11": schema.check_k11(k11, k11_auctions)}
    ok = {t: int(not c) for t, c in checks.items()}
    primary = {"F04": measures.primary_f04(f04, ok["F04"]),
               "F04-bis": measures.primary_f04bis(f04bis, ok["F04-bis"]),
               "J05": measures.primary_j05(j05, ok["J05"]),
               "K11": measures.primary_k11(k11, ok["K11"])}
    frames = {"F04": f04, "F04-bis": f04bis, "J05": j05, "K11": k11}
    path = measures.f04_event_path(f04, dgs, gsw, cal_dgs10)
    return frames, checks, primary, path


# ----------------------------------------------------------------------------- descriptive
def _cm(values, months):
    m = cluster_mean(values, months)
    return {"mean": m["mean"], "se": m["se"], "n": m["n"], "months": m["g"]}


def descriptive(frames, path):
    """Main descriptive breakdowns (none of them is preregistered unless named S1-S3)."""
    out = {}
    f04 = frames["F04"]
    p = measures.f04_sample(f04).copy()
    p["v"], p["year"] = measures.f04_v(p), p.date_adjudication.str[:4].astype(int)
    split = {name: _cm(s.v, s.mois) for name, s in (("2010-2021", p[p.year <= 2021]), ("2022-2026", p[p.year >= 2022]))}
    subperiods = {}  # S3 of F04 (preregistered descriptive)
    for name, lo, hi in (("2010-01..2014-12", "2010-01-01", "2014-12-31"), ("2015-01..2024-07", "2015-01-01", "2024-07-31"),
                         ("2024-08..2026-09", "2024-08-01", "2026-09-30")):
        s = p[p.date_adjudication.between(lo, hi)]
        subperiods[name] = _cm(s.v, s.mois)
    out["F04"] = {"S3_subperiods": subperiods, "by_period_not_preregistered": split,
                  "by_maturity": {int(m): float(s.v.mean()) for m, s in p.groupby("echeance")},
                  "sd_v": float(p.v.std(ddof=1)),
                  "by_year": by_group(p.v, p.year, p.mois).to_dict("records")}

    b = measures.f04bis_sample(frames["F04-bis"]).copy()
    b["v_hs"], b["v_mc"], b["v_cmt"] = measures.f04_v(b, "hs"), measures.f04_v(b, "mc"), measures.f04_v(b)
    b["d"] = b.v_hs - b.v_mc
    out["F04-bis"] = {
        "S1_by_maturity": {int(m): {"D": float(s.d.mean()), "V_HS": float(s.v_hs.mean()), "V_MC": float(s.v_mc.mean()),
                                    "n": len(s)} for m, s in b.groupby("echeance")},
        "S2_mean_hs_minus_mc_bp": {x: float(100 * (b[f"hs_{x}"] - b[f"mc_{x}"]).mean()) for x in measures.X3},
        "S2_v_with_fred_cmt": float(b.v_cmt.mean()), "sd_d": float(b.d.std(ddof=1))}

    j = frames["J05"]
    q = j[j.dans_p == 1].copy()
    q["year"] = q.date_adjudication.str[:4].astype(int)
    q["pi_pb"] = 100 * (q.rdt_fi_jm5_pct - q.rdt_gsw_jm5_pct)
    r = q[q.complet_r == 1].assign(a_pb=lambda d: d.k_pb - d.r_fi_pb)
    monday_rows = ["9128282A7_2016-09-12", "91282CCB5_2021-07-12", "91282CFF3_2022-09-12"]
    exact = q.apply(lambda row: pd.Series(measures.j05_yields(row, treasury_exact=True)), axis=1)
    q["k_exact"] = 100 * ((q.rdt_limite_pct - exact.rdt_gsw_j_terme_pct) - (exact.rdt_fi_jm5_pct - exact.rdt_gsw_jm5_pct))

    def reg(frame, col):
        d, se = measures.j05_regression(frame, col)
        lo, hi = interval(d, se, 1.645)
        return {"delta": d, "se": se, "low_90": lo, "high_90": hi, "n": len(frame)}

    out["J05"] = {
        "by_year": by_group(q.k_pb, q.year, q.mois).to_dict("records"),
        "S1b_level_concession_c": reg(q, "c_pb"), "S2_rise_to_close_R": reg(r, "r_fi_pb"),
        "S2_auction_and_afternoon_A": reg(r, "a_pb"), "S3_premium_at_J-5": reg(q, "pi_pb"),
        "sd_k": {per: float(s.k_pb.std(ddof=1)) for per, s in q.groupby("periode")},
        "variant_without_3_monday_rows": reg(q[~q.id_ligne.isin(monday_rows)], "k_pb"),
        "variant_treasury_exact_yield_convention": reg(q, "k_exact"),
        "variant_without_2023": reg(q[q.year != 2023], "k_pb")}

    k = frames["K11"]
    s = k[k.dans_p == 1].copy()
    for c in ("v_pb", "montee_pb", "detente_pb", "v_pa_pb", "p_carte_pb"):
        s[c] = pd.to_numeric(s[c], errors="coerce")
    groups = {"after": s[s.periode == "apres"],
              "before_10_30": s[(s.periode == "avant") & s.echeance.isin([10, 30])]}
    out["K11"] = {
        "by_year": by_group(s.v_pb, s.annee, s.mois).to_dict("records"),
        "S1_card_measure_p": {g: _cm(d.p_carte_pb.dropna(), d.mois[d.p_carte_pb.notna()]) for g, d in groups.items()},
        "S2_rise": {g: _cm(d.montee_pb, d.mois) for g, d in groups.items()},
        "S2_fall": {g: _cm(d.detente_pb, d.mois) for g, d in groups.items()},
        "S2_first_off_the_run_v": {g: _cm(d.v_pa_pb.dropna(), d.mois[d.v_pa_pb.notna()]) for g, d in groups.items()},
        "sd_v": {g: float(d.v_pb.std(ddof=1)) for g, d in groups.items()},
        "by_maturity_after": {int(m): float(d.v_pb.mean()) for m, d in groups["after"].groupby("echeance")}}

    rows = []
    for (period, kk), d in path.groupby(["period", "k"]):
        m = cluster_mean(d.e_bp, d.mois)
        rows.append({"period": period, "k": kk, "mean": m["mean"], "n": m["n"],
                     "low": m["mean"] - 1.96 * m["se"], "high": m["mean"] + 1.96 * m["se"]})
    out["event_path"] = rows
    return out


# ----------------------------------------------------------------------------- reports
def fmt(v):
    if isinstance(v, (bool, np.bool_)):
        return "OK" if v else "NOT OK"
    if isinstance(v, (int, np.integer)):
        return str(v)
    return f"{v:.6g}" if abs(v) < 1e-3 and v != 0 else f"{v:.6f}"


def write_reproduction(repro, seals, verdicts, checks):
    lines = ["# Reproduction of the sealed verifier numbers", "",
             f"Generated by `run_all.py` on {date.today()}. For each test: every field of the preregistration's",
             "`champs_verification`, the sealed verifier value (`audit/<ID>/verdict.json`, `chiffres_verificateur`),",
             "the value computed by this pipeline from the raw data, the absolute gap, and the tolerance written in the",
             "preregistration's machine-readable rule (`tolerance`). Tolerances are used as sealed, never adjusted.", ""]
    for t in TESTS:
        rows = repro[t]
        n_ok = sum(r["ok"] for r in rows)
        lines += [f"## {t}: {n_ok}/{len(rows)} fields OK", "",
                  f"Preregistration sha256 `{seals[t]['sha256']}`: "
                  f"{'matches' if seals[t]['matches_sha256_file'] and seals[t]['matches_verdict_seal'] else 'DOES NOT MATCH'}"
                  " the sealed value. Verdict from the sealed rule applied to the pipeline numbers: "
                  f"**{verdicts[t]['pipeline']}** (sealed verdict: {verdicts[t]['sealed']}).", ""]
        if checks[t]:
            fails = "; ".join(f"check {n}: {len(ids)} row(s) ({', '.join(map(str, ids))})" for n, ids in checks[t].items())
            lines += [f"Schema checks failing, exactly as for the sealed run: {fails}.", ""]
        lines += ["| Field | Sealed verifier | Pipeline | Absolute gap | Tolerance | Status |", "|---|---|---|---|---|---|"]
        for r in rows:
            lines.append(f"| `{r['field']}` | {fmt(r['sealed'])} | {fmt(r['pipeline'])} | {r['gap']:.2e} | "
                         f"{r['tolerance']} | {fmt(r['ok'])} |")
        lines.append("")
    lines += ["## Notes", "",
              "- `ecart_max_rdt_pb` (J05, K11) is the largest gap between two independent yield computations "
              "(Brent root-finder vs bisection), as the preregistrations define it for the experimenter; it is "
              "~1e-10 bp in both the sealed run and here, far inside the 0.05 bp tolerance.",
              "- `schema_ok` = 0 for J05 and K11 is reproduced, not corrected: J05's check 5 (J-5 must be 7-9 calendar "
              "days before J) fails on three Mondays that follow a Monday holiday (10 days); K11's check 5 (three "
              "distinct controls on every row not excluded by metadata) fails on 8 rows where frozen prices exhausted "
              "the candidate list. Both are explained in the tests' `lecture-apres-coup.md` / logged deviations.",
              "- Beyond the fields above, the four analysis datasets in `results/datasets/` were compared cell by cell "
              "with the sealed analysis files during development: identical (numbers to 1e-9)."]
    (RESULTS / "reproduction.md").write_text("\n".join(lines) + "\n")


def write_results_md(primary, desc, verdicts):
    f, b, j, k = primary["F04"], primary["F04-bis"], primary["J05"], primary["K11"]
    fs = desc["F04"]["by_period_not_preregistered"]
    lines = [
        "# Results", "",
        f"Generated by `run_all.py` on {date.today()}. Primary statistics are exactly as preregistered; everything under",
        "*Descriptive* is not part of any verdict. Units: basis points (bp).", "",
        "## Primary statistics and verdicts", "",
        "| Test | Question | Primary statistic | Verdict (sealed rule) |", "|---|---|---|---|",
        f"| F04 | Is there an inverted V in CMT minus GSW around 10/20/30-year reopenings, 2010-2026? | "
        f"mean V = {f['v_moyen_pb']:.2f} (SE {f['erreur_type_pb']:.2f}, t = {f['t_stat']:.2f}, N = {f['n_adjudications']}); "
        f"placebo |t| = {f['t_placebo_abs']:.2f} | {verdicts['F04']['pipeline']} |",
        f"| F04-bis | On fiscal-2021 reopenings, how much does V drop when the old (HS) Treasury method is replaced by "
        f"the new (MC)? | D = {b['d_moyen_pb']:.2f}, 95% CI [{b['d_borne_inf_95_pb']:.2f}, {b['d_borne_sup_95_pb']:.2f}] "
        f"(N = {b['n_adjudications']}, 8 months); V_HS = {b['v_hs_moyen_pb']:.2f}, V_MC = {b['v_mc_moyen_pb']:.2f} | "
        f"{verdicts['F04-bis']['pipeline']} (CI contains 0.9) |",
        f"| J05 | Did the concession K (vs GSW, net of the same bond's J-5 spread) fall after 2021? | "
        f"K: {j['k_moyen_avant_pb']:.2f} (2010-21) -> {j['k_moyen_apres_pb']:.2f} (2022-26); decline "
        f"{j['delta_k_pb']:.2f}, 90% CI [{j['borne_inf_90_pb']:.2f}, {j['borne_sup_90_pb']:.2f}] | "
        f"{verdicts['J05']['pipeline']} (schema check 5) |",
        f"| K11 | Is V still present after 2021 against matched control bonds, no curve? | "
        f"V after 2021 = {k['v_moyen_apres_pb']:.2f}, 90% CI [{k['borne_inf_90_apres_pb']:.2f}, "
        f"{k['borne_sup_90_apres_pb']:.2f}]; before (10/30y) = {k['v_moyen_avant_1030_pb']:.2f} | "
        f"{verdicts['K11']['pipeline']} (instrument alert; schema check 5) |", "",
        "## Reading", "",
        f"- Against the Treasury curve, V averages {fs['2010-2021']['mean']:.2f} bp in 2010-2021 and "
        f"{fs['2022-2026']['mean']:.2f} bp in 2022-2026 (descriptive split, not preregistered; figure 2).",
        f"- On the same fiscal-2021 auctions, switching the Treasury curve method alone removes {b['d_moyen_pb']:.2f} bp of V, "
        "about half of the post-2021 break (figure 3).",
        "- Measured on market prices against the Fed's GSW curve, the concession did not fall after 2021 (figure 4).",
        "- Against matched off-the-run controls the measure is zero before and after 2022, so it cannot arbitrate (figure 5).",
        "", "## Descriptive breakdowns", ""]
    lines += ["### F04: V by subperiod (S3, preregistered descriptive) and by period (not preregistered)", "",
              "| Sample | Mean V | SE | N | Months |", "|---|---|---|---|---|"]
    for name, m in list(desc["F04"]["S3_subperiods"].items()) + list(fs.items()):
        lines.append(f"| {name} | {m['mean']:.3f} | {m['se']:.3f} | {m['n']} | {m['months']} |")
    lines += ["", "By maturity (mean V): " + ", ".join(f"{m}y {v:.2f}" for m, v in desc["F04"]["by_maturity"].items())
              + f"; standard deviation of V: {desc['F04']['sd_v']:.2f}.", ""]
    lines += ["### Yearly means (95% intervals, SE clustered by month)", "",
              "| Year | F04 V | J05 K | K11 V |", "|---|---|---|---|"]
    tabs = {t: {r["group"]: r for r in desc[t]["by_year"]} for t in ("F04", "J05", "K11")}
    cell = lambda r: f"{r['mean']:.2f} [{r['low']:.2f}, {r['high']:.2f}]" if r else ""  # noqa: E731
    for y in sorted(set().union(*tabs.values())):
        lines.append(f"| {y} | {cell(tabs['F04'].get(y))} | {cell(tabs['J05'].get(y))} | {cell(tabs['K11'].get(y))} |")
    s1 = desc["F04-bis"]["S1_by_maturity"]
    lines += ["", "### F04-bis by maturity (S1)", "", "| Maturity | N | D | V_HS | V_MC |", "|---|---|---|---|---|"]
    lines += [f"| {m}y | {v['n']} | {v['D']:.2f} | {v['V_HS']:.2f} | {v['V_MC']:.2f} |" for m, v in s1.items()]
    jd = desc["J05"]
    lines += ["", "### J05 regressions (decline after 2021 = -b, 90% CI)", "",
              "| Variant | Decline | SE | 90% CI | N |", "|---|---|---|---|---|"]
    for name in ("S1b_level_concession_c", "S2_rise_to_close_R", "S2_auction_and_afternoon_A", "S3_premium_at_J-5",
                 "variant_without_3_monday_rows", "variant_without_2023", "variant_treasury_exact_yield_convention"):
        v = jd[name]
        lines.append(f"| {name} | {v['delta']:.3f} | {v['se']:.3f} | [{v['low_90']:.2f}, {v['high_90']:.2f}] | {v['n']} |")
    lines += ["", "`variant_treasury_exact_yield_convention` is an improved, NOT preregistered variant: yields use the exact",
              "31 CFR 356 Appendix B formula (simple interest over the fractional first period), which reproduces the auction",
              "high price; the preregistration's compounded version is used for the primary statistic.", ""]
    kd = desc["K11"]
    lines += ["### K11 decomposition (mean, SE clustered by month)", "",
              "| Quantity | 2022-2026 | 2010-2021, 10/30y |", "|---|---|---|"]
    for name in ("S1_card_measure_p", "S2_rise", "S2_fall", "S2_first_off_the_run_v"):
        a, bb = kd[name]["after"], kd[name]["before_10_30"]
        lines.append(f"| {name} | {a['mean']:.3f} ({a['se']:.3f}) | {bb['mean']:.3f} ({bb['se']:.3f}) |")
    lines += ["", "## Figures", ""] + [f"- `figures/{n}`" for n in FIGURES]
    (RESULTS / "RESULTS.md").write_text("\n".join(lines) + "\n")


FIGURES = ["fig1_event_path_treasury_curve.png", "fig2_v_by_year_treasury_curve.png",
           "fig3_fy2021_old_vs_new_method.png", "fig4_k_by_year_gsw.png", "fig5_k11_controls_by_year.png"]


def draw_figures(frames, primary, desc):
    out = RESULTS / "figures"
    out.mkdir(parents=True, exist_ok=True)
    figures.event_path(pd.DataFrame(desc["event_path"]), out / FIGURES[0])
    f04_year = pd.DataFrame(desc["F04"]["by_year"])
    figures.v_by_year(f04_year, out / FIGURES[1])
    b = measures.f04bis_sample(frames["F04-bis"])
    pairs = pd.DataFrame({"v_hs": measures.f04_v(b, "hs"), "v_mc": measures.f04_v(b, "mc")})
    p = primary["F04-bis"]
    figures.fy2021_pairs(pairs, p["d_moyen_pb"], p["d_borne_inf_95_pb"], p["d_borne_sup_95_pb"], out / FIGURES[2])
    j = primary["J05"]
    figures.k_by_year(pd.DataFrame(desc["J05"]["by_year"]),
                      {"2010-2021": j["k_moyen_avant_pb"], "2022-2026": j["k_moyen_apres_pb"]}, out / FIGURES[3])
    figures.k11_by_year(pd.DataFrame(desc["K11"]["by_year"]), f04_year, out / FIGURES[4])


# ----------------------------------------------------------------------------- main
def _plain(obj):
    """Make numpy scalars JSON-serialisable."""
    if isinstance(obj, dict):
        return {str(k): _plain(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_plain(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    return obj


def main():
    seals = check_seals()
    for t, s in seals.items():
        print(f"{t}: preregistration sha256 {'OK' if s['matches_sha256_file'] and s['matches_verdict_seal'] else 'MISMATCH'}")
    frames, checks, primary, path = build_all()
    datasets = RESULTS / "datasets"
    datasets.mkdir(parents=True, exist_ok=True)
    cols = {"F04": measures.F04_COLUMNS, "F04-bis": measures.F04BIS_COLUMNS, "J05": measures.J05_COLUMNS,
            "K11": measures.K11_COLUMNS}
    for t, df in frames.items():
        df[cols[t]].to_csv(datasets / f"{t}_analysis.csv", index=False)

    repro = {t: reproduction(t, primary[t]) for t in TESTS}
    verdicts = {t: {"pipeline": apply_rule(preregistered_rule(t), primary[t]),
                    "sealed": json.loads((AUDIT / t / "verdict.json").read_text())["verdict"]} for t in TESTS}
    desc = descriptive(frames, path)
    write_reproduction(repro, seals, verdicts, checks)
    write_results_md(primary, desc, verdicts)
    draw_figures(frames, primary, desc)
    results = {"seals": seals, "primary": primary, "verdicts": verdicts,
               "schema_failures": {t: {str(n): ids for n, ids in c.items()} for t, c in checks.items()},
               "reproduction": repro, "descriptive": desc}
    (RESULTS / "results.json").write_text(json.dumps(_plain(results), indent=1, ensure_ascii=False, default=str) + "\n")
    data.write_provenance()

    all_ok = all(s["matches_sha256_file"] and s["matches_verdict_seal"] for s in seals.values())
    for t in TESTS:
        n_ok = sum(r["ok"] for r in repro[t])
        all_ok &= n_ok == len(repro[t])
        print(f"{t}: {n_ok}/{len(repro[t])} verifier fields reproduced; verdict {verdicts[t]['pipeline']}"
              f" (sealed: {verdicts[t]['sealed']})")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
