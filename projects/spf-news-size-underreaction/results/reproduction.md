# Reproduction of the sealed verifier numbers

Each pipeline value is computed by `run_all.py` from the raw files in `data/raw/` with the code in
`src/snu/`. The sealed value is the independent verifier's number in `audit/<ID>/verdict.json`
(`chiffres_verificateur`); the tolerance is the one written in the preregistration (its json block,
copied in `verdict.json` under `regle`). Integers are shown without decimals.

| test | fields within tolerance | verdict from pipeline numbers | sealed verdict |
|---|---|---|---|
| K20 | 53 / 53 | non concluant | non concluant |

## K20

| field | sealed verifier value | pipeline value | absolute gap | tolerance | status |
|---|---|---|---|---|---|
| `n_violations_schema` | 1 | 1 | 0.0e+00 | 0 | OK |
| `n_principal` | 1004 | 1004 | 0.0e+00 | 0 | OK |
| `c` | -0.029780 | -0.029780 | 1.7e-14 | 0.005 | OK |
| `et_c_dk4` | 0.070685 | 0.070685 | 4.4e-16 | 0.005 | OK |
| `t_c` | -0.421300 | -0.421300 | 2.3e-13 | 0.02 | OK |
| `borne_basse_ic90` | -0.146057 | -0.146057 | 1.8e-14 | 0.01 | OK |
| `borne_haute_ic90` | 0.086498 | 0.086498 | 1.6e-14 | 0.01 | OK |
| `rapport_variance_revision` | 3.063543 | 3.063543 | 0.0e+00 | 0.01 | OK |
| `b_moyen` | 0.193576 | 0.193576 | 2.9e-15 | 0.005 | OK |
| `k_moyen` | 0.294269 | 0.294269 | 2.5e-15 | 0.005 | OK |
| `pente_moyenne_grandes` | 0.163797 | 0.163797 | 2.0e-14 | 0.005 | OK |
| `biais_mecanique_nu20` | 0.080675 | 0.080675 | 9.7e-16 | 0.005 | OK |
| `seuil_survie_bas` | 0.100000 | 0.100000 | 0.0e+00 | 0.01 | OK |
| `borne_basse_moins_seuil` | -0.246057 | -0.246057 | 1.8e-14 | 0.01 | OK |
| `marge_indecision` | -0.313502 | -0.313502 | 1.6e-14 | 0.01 | OK |
| `t_min_sans_episode` | -1.518918 | -1.518918 | 2.3e-13 | 0.02 | OK |
| `c_min_sans_episode` | -0.083734 | -0.083734 | 1.6e-14 | 0.005 | OK |
| `episode_t_min` | 2 | 2 | 0.0e+00 | 0 | OK |
| `conflit_robustesse` | 0 | 0 | 0.0e+00 | 0 | OK |
| `n_grands` | 334 | 334 | 0.0e+00 | 0 | OK |
| `n_trimestres` | 223 | 223 | 0.0e+00 | 0 | OK |
| `n_trimestres_grands` | 184 | 184 | 0.0e+00 | 0 | OK |
| `et_c_iid` | 0.063872 | 0.063872 | 2.8e-16 | 0.005 | OK |
| `n_effectif` | 819.775346 | 819.775346 | 3.2e-12 | 1 | OK |
| `c_sans_E1` | -0.032507 | -0.032507 | 1.9e-14 | 0.005 | OK |
| `c_sans_E2` | -0.083734 | -0.083734 | 1.6e-14 | 0.005 | OK |
| `c_sans_E3` | 0.014180 | 0.014180 | 1.8e-14 | 0.005 | OK |
| `c_sans_E4` | -0.020555 | -0.020555 | 1.7e-14 | 0.005 | OK |
| `c_sans_E5` | -0.027682 | -0.027682 | 1.5e-14 | 0.005 | OK |
| `c_sans_E6` | -0.007431 | -0.007431 | 6.9e-15 | 0.005 | OK |
| `c_sans_E7` | -0.026717 | -0.026717 | 1.7e-14 | 0.005 | OK |
| `et_c_dk8` | 0.068217 | 0.068217 | 1.9e-16 | 0.005 | OK |
| `et_c_dk0` | 0.073107 | 0.073107 | 1.2e-15 | 0.005 | OK |
| `c_avec_pandemie` | -0.094945 | -0.094945 | 1.2e-14 | 0.005 | OK |
| `et_c_avec_pandemie_dk4` | 0.073887 | 0.073887 | 1.1e-15 | 0.005 | OK |
| `c_depuis_1985` | -0.066884 | -0.066884 | 3.2e-14 | 0.005 | OK |
| `et_c_depuis_1985_dk4` | 0.083346 | 0.083346 | 1.8e-15 | 0.005 | OK |
| `c_avant_2020` | -0.037148 | -0.037148 | 2.0e-14 | 0.005 | OK |
| `et_c_avant_2020_dk4` | 0.079498 | 0.079498 | 5.4e-16 | 0.005 | OK |
| `c_mediane` | 0.074609 | 0.074609 | 1.2e-14 | 0.005 | OK |
| `et_c_mediane_dk4` | 0.069380 | 0.069380 | 5.6e-17 | 0.005 | OK |
| `c_coupure_revision` | -0.002621 | -0.002621 | 2.8e-14 | 0.005 | OK |
| `et_c_coupure_revision_dk4` | 0.085581 | 0.085581 | 1.0e-14 | 0.005 | OK |
| `c_PGDP` | 0.173353 | 0.173353 | 5.1e-15 | 0.005 | OK |
| `c_RGDP` | -0.053129 | -0.053129 | 1.5e-14 | 0.005 | OK |
| `c_UNEMP` | -0.103285 | -0.103285 | 5.6e-14 | 0.005 | OK |
| `c_CPI` | 0.046509 | 0.046509 | 1.8e-14 | 0.005 | OK |
| `c_TBILL` | -0.311018 | -0.311018 | 1.7e-14 | 0.005 | OK |
| `et_c_PGDP_dk4` | 0.183231 | 0.183231 | 3.7e-15 | 0.005 | OK |
| `et_c_RGDP_dk4` | 0.158495 | 0.158495 | 2.1e-15 | 0.005 | OK |
| `et_c_UNEMP_dk4` | 0.148942 | 0.148942 | 1.8e-14 | 0.005 | OK |
| `et_c_CPI_dk4` | 0.150982 | 0.150982 | 1.2e-14 | 0.005 | OK |
| `et_c_TBILL_dk4` | 0.180348 | 0.180348 | 5.6e-15 | 0.005 | OK |

**K20: 53 / 53 fields within tolerance.**
