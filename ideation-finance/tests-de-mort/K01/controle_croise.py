"""K01 — contrôle croisé (hors préinscription, pour l'expérimentateur seulement).

1. b_IV par linearmodels.IV2SLS (indicatrices d'horizon, sans constante) ;
2. b_IV et son écart-type de Driscoll-Kraay par la forme matricielle complète du sandwich
   V = (Z'X)⁻¹ Ω (X'Z)⁻¹, Ω = Γ₀ + Σ_j (1 − j/9)(Γ_j + Γ_j'), Γ_j = Σ_t g_t g_{t−j}', g_t = Σ_{i∈t} Z_i u_i ;
3. MCO naïf et son écart-type par statsmodels, cov_type « hac-groupsum » (Driscoll-Kraay), sans correction.
"""
import json
import os

import numpy as np
import pandas as pd
import statsmodels.api as sm

ICI = os.path.dirname(os.path.abspath(__file__))
s = pd.read_csv(os.path.join(ICI, "K01_analyse.csv"), dtype={"id_prev": str})
E = s[s["echantillon_iv"] == 1].sort_values("t_tour").reset_index(drop=True)
D = np.column_stack([(E["horizon"] == 0).astype(float), (E["horizon"] == 1).astype(float)])
X = np.column_stack([D, E["revision"]])
Z = np.column_stack([D, E["instrument"]])
y = E["erreur"].to_numpy()
res = {}

from linearmodels.iv import IV2SLS  # noqa: E402
m = IV2SLS(y, pd.DataFrame(D, columns=["h0", "h1"]), E[["revision"]], E[["instrument"]]).fit(cov_type="unadjusted")
res["b_iv_linearmodels"] = float(m.params["revision"])

beta = np.linalg.solve(Z.T @ X, Z.T @ y)
u = y - X @ beta
tours = E["t_tour"].to_numpy()
g = pd.DataFrame(Z * u[:, None]).groupby(tours).sum()
G = {int(t): g.loc[t].to_numpy() for t in g.index}
Om = sum(np.outer(v, v) for v in G.values())
for j in range(1, 9):
    Gj = sum(np.outer(G[t], G[t - j]) for t in G if (t - j) in G)
    if isinstance(Gj, int):
        continue
    Om = Om + (1 - j / 9) * (Gj + Gj.T)
A = np.linalg.inv(Z.T @ X)
V = A @ Om @ A.T
res["b_iv_matriciel"] = float(beta[2])
res["et_b_iv_dk8_matriciel"] = float(np.sqrt(V[2, 2]))

ols = sm.OLS(y, X).fit(cov_type="hac-groupsum", cov_kwds={"time": pd.factorize(tours, sort=True)[0], "maxlags": 8,
                                                           "use_correction": False})
res["b_mco_naif_statsmodels"] = float(ols.params[2])
res["et_b_mco_naif_dk8_statsmodels_tours_consecutifs"] = float(ols.bse[2])
print(json.dumps(res, indent=1))
with open(os.path.join(ICI, "controle_croise.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1)
