"""K20-LIV : contrôle croisé indépendant (statsmodels, formule) de c, et_c_dk2 et b_regroupe. Ne sert pas au verdict."""
import pathlib, json, numpy as np, pandas as pd, statsmodels.formula.api as smf
R = pathlib.Path(__file__).resolve().parent
df = pd.read_csv(R / "K20-LIV_analyse.csv", dtype={"episode": str}); P = df[df.principal == 1].copy()
for col, z in (("revision", "zr"), ("erreur", "ze")):
    P[z] = P.groupby("variable")[col].transform(lambda s: (s - s.mean()) / s.std(ddof=1))
P["L"] = P.grande_nouvelle.astype(float); P["sem"] = P.semestre.astype(int)
P = P.sort_values("sem").reset_index(drop=True)
m = smf.ols("ze ~ 0 + C(variable) + C(variable):L + C(variable):zr + zr:L", data=P)
r = m.fit(cov_type="hac-groupsum", cov_kwds={"time": P["sem"].values, "maxlags": 2, "use_correction": False})
nm = [n for n in r.params.index if n == "zr:L"][0]
c, se = r.params[nm], r.bse[nm]
m2 = smf.ols("ze ~ 0 + C(variable) + zr", data=P).fit(cov_type="hac-groupsum", cov_kwds={"time": P["sem"].values, "maxlags": 2, "use_correction": False})
T = json.load(open(R / "temoin.json"))
print(f"c            statsmodels {c:.6f}  analyse.py {T['c']:.6f}")
print(f"et_c_dk2     statsmodels {se:.6f}  analyse.py {T['et_c_dk2']:.6f}")
print(f"b_regroupe   statsmodels {m2.params['zr']:.6f}  analyse.py {T['b_regroupe']:.6f}")
print(f"et_b_regroupe statsmodels {m2.bse['zr']:.6f}  analyse.py {T['et_b_regroupe_dk2']:.6f}")
print(f"et_c_iid     statsmodels {smf.ols('ze ~ 0 + C(variable) + C(variable):L + C(variable):zr + zr:L', data=P).fit().bse[nm]:.6f}  analyse.py {T['et_c_iid']:.6f}")
