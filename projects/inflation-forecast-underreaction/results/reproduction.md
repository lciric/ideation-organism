# Reproduction of the sealed verifier numbers

Each pipeline value is computed by `run_all.py` from the raw files in `data/raw/` with the code in
`src/ifu/`. The sealed value is the independent verifier's number in `audit/<ID>/verdict.json`
(`chiffres_verificateur`); the tolerance is the one written in that test's preregistration (json block).
Integers are shown without decimals.

| test | fields within tolerance | verdict from pipeline numbers | sealed verdict |
|---|---|---|---|
| H03-v2 | 25 / 25 | éliminée | éliminée |
| J02 | 26 / 26 | survit | survit |
| K01 | 45 / 45 | éliminée | éliminée |
| K20 | 53 / 53 | non concluant | non concluant |
| K20-ZE (replication) | 65 / 65 in the sibling project `projects/spf-news-size-underreaction/` (not recomputed here) | éliminée (rule applied to the sealed numbers) | éliminée |

K20-ZE, the euro-area replication of K20, is not recomputed by this pipeline. The sibling project
`projects/spf-news-size-underreaction/` rebuilds it from the raw ECB and Eurostat files with its own code:
65 of 65 sealed verifier numbers within tolerance, an analysis file bit-identical to the sealed one, and the
same verdict (see its `results/reproduction.md`). Here `run_all.py` checks the K20-ZE seal on the byte-for-byte
copies in `audit/K20-ZE/` and applies the sealed rule to the sealed verifier numbers.

## H03-v2

| field | sealed verifier value | pipeline value | absolute gap | tolerance | status |
|---|---|---|---|---|---|
| `n_violations_schema` | 0 | 0 | 0.0e+00 | 0 | OK |
| `n_obs_evaluees` | 352 | 352 | 0.0e+00 | 0 | OK |
| `n_blocs` | 11 | 11 | 0.0e+00 | 0 | OK |
| `r_moyen` | 0.015586 | 0.015586 | 5.2e-18 | 0.005 | OK |
| `et_r_moyen` | 0.049312 | 0.049312 | 0.0e+00 | 0.005 | OK |
| `borne_basse_ic90` | -0.073791 | -0.073791 | 0.0e+00 | 0.01 | OK |
| `borne_haute_ic90` | 0.104964 | 0.104964 | 0.0e+00 | 0.01 | OK |
| `marge_indecision` | -0.115036 | -0.115036 | 0.0e+00 | 0.01 | OK |
| `r_hors_episode` | -0.030035 | -0.030035 | 1.0e-17 | 0.005 | OK |
| `rapport_eqm_geo` | 1.097165 | 1.097165 | 0.0e+00 | 0.005 | OK |
| `conflit_gardes` | 0 | 0 | 0.0e+00 | 0 | OK |
| `n_obs_h4_2020` | 21 | 21 | 0.0e+00 | 0 | OK |
| `rapport_eqm_h4_2020` | 1.010189 | 1.010189 | 2.2e-16 | 0.005 | OK |
| `p_dm_hln_h4_2020` | 0.910605 | 0.910605 | 1.1e-16 | 0.005 | OK |
| `rapport_eqm_global` | 0.969849 | 0.969849 | 0.0e+00 | 0.005 | OK |
| `rapport_eqm_hors_2021_2022` | 1.096179 | 1.096179 | 0.0e+00 | 0.005 | OK |
| `taux_amelioration` | 0.448052 | 0.448052 | 0.0e+00 | 0.005 | OK |
| `part_b_positif` | 0.599432 | 0.599432 | 0.0e+00 | 0.005 | OK |
| `r_moyen_h1` | 0.145180 | 0.145180 | 2.8e-17 | 0.005 | OK |
| `r_moyen_h2` | 0.127732 | 0.127732 | 0.0e+00 | 0.005 | OK |
| `r_moyen_h3` | 0.110537 | 0.110537 | 0.0e+00 | 0.005 | OK |
| `r_moyen_h4` | -0.086661 | -0.086661 | 5.6e-17 | 0.005 | OK |
| `r_moyen_placebo` | 0.074743 | 0.074743 | 0.0e+00 | 0.005 | OK |
| `et_r_placebo` | 0.062464 | 0.062464 | 0.0e+00 | 0.005 | OK |
| `n_blocs_placebo` | 11 | 11 | 0.0e+00 | 0 | OK |

**H03-v2: 25 / 25 fields within tolerance.**

## J02

| field | sealed verifier value | pipeline value | absolute gap | tolerance | status |
|---|---|---|---|---|---|
| `n_violations_schema` | 0 | 0 | 0.0e+00 | 0 | OK |
| `n_cibles` | 108 | 108 | 0.0e+00 | 0 | OK |
| `beta_z` | 0.443121 | 0.443121 | 1.1e-14 | 0.005 | OK |
| `et_beta_z_nw4` | 0.195502 | 0.195502 | 3.2e-15 | 0.005 | OK |
| `t_nw4` | 2.266578 | 2.266578 | 9.3e-14 | 0.02 | OK |
| `borne_basse_ic90` | 0.121520 | 0.121520 | 1.6e-14 | 0.01 | OK |
| `borne_haute_ic90` | 0.764721 | 0.764721 | 5.8e-15 | 0.01 | OK |
| `marge_indecision` | -0.121520 | -0.121520 | 1.6e-14 | 0.01 | OK |
| `beta_z_min_sans_deux_ans` | 0.050328 | 0.050328 | 2.3e-14 | 0.005 | OK |
| `annee_debut_min` | 2021 | 2021 | 0.0e+00 | 0 | OK |
| `conflit_robustesse` | 0 | 0 | 0.0e+00 | 0 | OK |
| `beta_brut` | 0.678263 | 0.678263 | 1.2e-14 | 0.005 | OK |
| `et_beta_brut_nw4` | 0.299245 | 0.299245 | 7.0e-15 | 0.005 | OK |
| `ecart_type_revision` | 0.619966 | 0.619966 | 0.0e+00 | 0.005 | OK |
| `ecart_type_erreur` | 0.948951 | 0.948951 | 6.9e-15 | 0.005 | OK |
| `n_avant_2020` | 81 | 81 | 0.0e+00 | 0 | OK |
| `beta_z_avant_2020` | 0.134249 | 0.134249 | 4.1e-14 | 0.005 | OK |
| `beta_brut_avant_2020` | 0.192375 | 0.192375 | 6.5e-14 | 0.005 | OK |
| `et_beta_brut_avant_2020_nw4` | 0.111402 | 0.111402 | 1.3e-14 | 0.005 | OK |
| `et_beta_z_nw8` | 0.161629 | 0.161629 | 5.9e-15 | 0.005 | OK |
| `bb_borne_basse_ic90` | 0.050706 | 0.050706 | 3.3e-14 | 0.02 | OK |
| `bb_borne_haute_ic90` | 0.592050 | 0.592050 | 9.0e-15 | 0.02 | OK |
| `n_hors_2021_2023` | 96 | 96 | 0.0e+00 | 0 | OK |
| `beta_z_hors_2021_2023` | 0.143625 | 0.143625 | 4.4e-14 | 0.005 | OK |
| `et_beta_z_hors_2021_2023_nw4` | 0.065409 | 0.065409 | 8.8e-15 | 0.005 | OK |
| `beta_z_min_sans_une_annee` | 0.084206 | 0.084206 | 2.4e-14 | 0.005 | OK |

**J02: 26 / 26 fields within tolerance.**

## K01

| field | sealed verifier value | pipeline value | absolute gap | tolerance | status |
|---|---|---|---|---|---|
| `n_violations_schema` | 0 | 0 | 0.0e+00 | 0 | OK |
| `n_obs_iv` | 8595 | 8595 | 0.0e+00 | 0 | OK |
| `n_previsionnistes_iv` | 94 | 94 | 0.0e+00 | 0 | OK |
| `n_tours_iv` | 96 | 96 | 0.0e+00 | 0 | OK |
| `b_iv` | 1.150705 | 1.150705 | 2.2e-16 | 0.005 | OK |
| `et_b_iv_dk8` | 0.463353 | 0.463353 | 5.6e-17 | 0.005 | OK |
| `t_iv` | 2.483432 | 2.483432 | 0.0e+00 | 0.02 | OK |
| `borne_basse_ic90` | 0.356519 | 0.356519 | 1.1e-16 | 0.01 | OK |
| `borne_haute_ic90` | 1.944892 | 1.944892 | 2.2e-16 | 0.01 | OK |
| `marge_indecision` | -0.506519 | -0.506519 | 1.1e-16 | 0.01 | OK |
| `coef_premiere_etape` | 0.496125 | 0.496125 | 0.0e+00 | 0.005 | OK |
| `f_premiere_etape` | 513.724583 | 513.724583 | 6.8e-13 | 1 | OK |
| `t_forme_reduite` | 2.591799 | 2.591799 | 4.4e-16 | 0.02 | OK |
| `et_b_iv_grappes_tour` | 0.460128 | 0.460128 | 5.6e-17 | 0.005 | OK |
| `et_b_iv_grappes_cible` | 0.292651 | 0.292651 | 1.7e-16 | 0.005 | OK |
| `n_obs_iv_hors_2021_2023` | 7425 | 7425 | 0.0e+00 | 0 | OK |
| `b_iv_hors_2021_2023` | 0.168348 | 0.168348 | 1.4e-16 | 0.005 | OK |
| `et_b_iv_hors_2021_2023_dk8` | 0.466177 | 0.466177 | 0.0e+00 | 0.005 | OK |
| `borne_haute_ic90_hors_2021_2023` | 0.967375 | 0.967375 | 1.1e-16 | 0.01 | OK |
| `f_premiere_etape_hors_2021_2023` | 315.447818 | 315.447818 | 0.0e+00 | 1 | OK |
| `conflit_episode` | 0 | 0 | 0.0e+00 | 0 | OK |
| `b_iv_max_sans_une_annee` | 1.319787 | 1.319787 | 2.2e-16 | 0.005 | OK |
| `b_iv_ef_prev` | 1.099004 | 1.099004 | 0.0e+00 | 0.005 | OK |
| `et_b_iv_ef_prev_dk8` | 0.434192 | 0.434192 | 5.6e-17 | 0.005 | OK |
| `b_mco_naif` | 0.419426 | 0.419426 | 1.1e-16 | 0.005 | OK |
| `et_b_mco_naif_dk8` | 0.188360 | 0.188360 | 2.8e-17 | 0.005 | OK |
| `b_intra_tour_naif` | -0.452042 | -0.452042 | 0.0e+00 | 0.005 | OK |
| `et_b_intra_tour_naif_grappes_tour` | 0.065594 | 0.065594 | 1.4e-17 | 0.005 | OK |
| `sigma_bruit_necessaire_mco` | 0.000000 | 0.000000 | 0.0e+00 | 0.005 | OK |
| `sigma_bruit_commun_necessaire_iv` | 0.000000 | 0.000000 | 0.0e+00 | 0.005 | OK |
| `n_obs_avant_2020` | 6269 | 6269 | 0.0e+00 | 0 | OK |
| `b_iv_avant_2020` | 0.133758 | 0.133758 | 1.7e-16 | 0.005 | OK |
| `et_b_iv_avant_2020_dk8` | 0.604449 | 0.604449 | 1.1e-16 | 0.005 | OK |
| `b_mco_ef_avant_2020` | 0.043285 | 0.043285 | 6.9e-18 | 0.005 | OK |
| `et_b_mco_ef_avant_2020_dk8` | 0.094860 | 0.094860 | 6.9e-17 | 0.005 | OK |
| `n_consensus` | 188 | 188 | 0.0e+00 | 0 | OK |
| `b_consensus` | 0.917537 | 0.917537 | 0.0e+00 | 0.005 | OK |
| `et_b_consensus_dk8` | 0.238283 | 0.238283 | 2.8e-17 | 0.005 | OK |
| `n_bce` | 188 | 188 | 0.0e+00 | 0 | OK |
| `b_bce` | 0.774347 | 0.774347 | 1.1e-16 | 0.005 | OK |
| `et_b_bce_dk8` | 0.294082 | 0.294082 | 5.6e-17 | 0.005 | OK |
| `diff_bce_moins_consensus` | -0.143191 | -0.143191 | 1.1e-16 | 0.005 | OK |
| `et_diff_dk8` | 0.146167 | 0.146167 | 2.8e-17 | 0.005 | OK |
| `b_consensus_hors_2021_2023` | 0.514872 | 0.514872 | 0.0e+00 | 0.005 | OK |
| `b_bce_hors_2021_2023` | 0.162106 | 0.162106 | 5.6e-17 | 0.005 | OK |

**K01: 45 / 45 fields within tolerance.**

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
