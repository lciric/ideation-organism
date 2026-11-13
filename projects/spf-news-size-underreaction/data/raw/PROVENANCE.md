# Provenance of the raw data cache

Every file below is kept exactly as received. `origin` says whether it was downloaded by
`src/snu/data.py` or copied, byte for byte, from the raw-download folder of a sealed test
(`ideation-finance/tests-de-mort/<ID>/donnees/`, listed in that folder's own PROVENANCE.md). Only raw
source files were copied, never an analysis CSV. Delete the
files in `data/raw/` (keep this one if you like) and run `python run_all.py` to download everything
again. `date (UTC)` is the date the file entered this cache. `rows` = data rows (CSV: lines minus
header; zip: rows of `1_HICP.csv`; xlsx: rows of the first sheet minus header). `same as sealed`
says whether the file is byte-identical (sha256) to the copy in the sealed test's `donnees/` folder.

| file | URL | origin | date (UTC) | sha256 | bytes | rows | same as sealed |
|---|---|---|---|---|---|---|---|
| `ecb_spf/SPF_microdata_by_variable.zip` | https://www.ecb.europa.eu/stats/prices/indic/forecast/shared/files/SPF_microdata_by_variable.zip | downloaded (1 attempt(s)) | 2026-11-13T09:39:48Z | `49348fa33c5e5d58aa3e05aac56cf5df23ab29439862ab6e3ccafe68797b51f4` | 12035888 | 354060 | yes |
| `eurostat/nama_10_gdp_A_CLV_PCH_PRE_B1GQ_EA.csv` | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nama_10_gdp/A.CLV_PCH_PRE.B1GQ.EA?format=SDMX-CSV | downloaded (1 attempt(s)) | 2026-11-13T09:39:49Z | `0b8e98ab2fb2a8445bb263eecb493d93551b5894483b3406b4d98a62b0431534` | 2341 | 30 | yes |
| `eurostat/prc_hicp_ainr_A_RCH_A_AVG_TOTAL_EA.csv` | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/prc_hicp_ainr/A.RCH_A_AVG.TOTAL.EA?format=SDMX-CSV | downloaded (1 attempt(s)) | 2026-11-13T09:39:49Z | `43ef7b6b85ff0268d912b1e7d405a8790f7ad049aea427387a53f2781ad0505e` | 2292 | 29 | yes |
| `eurostat/une_rt_m_M_NSA_TOTAL_PC_ACT_T_EA21.csv` | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/une_rt_m/M.NSA.TOTAL.PC_ACT.T.EA21?format=SDMX-CSV | downloaded (1 attempt(s)) | 2026-11-13T09:39:49Z | `7842067c58b6b283d99eb35e8779e1a11350cc45073ba442b2766d74d4beb10e` | 25530 | 321 | yes |
| `fred/CPIAUCSL.csv` | https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL | copied from sealed test folder tests-de-mort/K20/donnees/CPIAUCSL.csv | 2026-11-13T08:58:26Z | `c9be2d4909ffd28d91f07df5d113151b0fe7ba602144ee6fd453d3bc8426efde` | 17782 | 958 | yes |
| `fred/TB3MS.csv` | https://fred.stlouisfed.org/graph/fredgraph.csv?id=TB3MS | copied from sealed test folder tests-de-mort/K20/donnees/TB3MS.csv | 2026-11-13T08:58:26Z | `33fae406051a658c316580f8e8b5e461157e6663bc03b35648cc7cd3e89ee26b` | 17881 | 1114 | yes |
| `fred/UNRATE.csv` | https://fred.stlouisfed.org/graph/fredgraph.csv?id=UNRATE | copied from sealed test folder tests-de-mort/K20/donnees/UNRATE.csv | 2026-11-13T08:58:26Z | `fb669461abc34e00324b940be6bad1c7f89117652f28587196a7b8bf4a9f56a1` | 14226 | 946 | yes |
| `fred/USRECQP.csv` | https://fred.stlouisfed.org/graph/fredgraph.csv?id=USRECQP | copied from sealed test folder tests-de-mort/K20/donnees/USRECQP.csv | 2026-11-13T08:58:26Z | `fae37d07129f12682fde3584a8511408eeaef1554b33141f15c6e7886fea627e` | 8969 | 688 | yes |
| `philly_rtdsm/pQvQd.xlsx` | https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/real-time-data/data-files/xlsx/pQvQd.xlsx | copied from sealed test folder tests-de-mort/K20/donnees/pQvQd.xlsx | 2026-11-13T08:58:26Z | `9726209d1cd370bd44bc22f18a1c715405e4e8f329d9779229ae8914203a11c6` | 247472 | 319 | yes |
| `philly_rtdsm/routputQvQd.xlsx` | https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/real-time-data/data-files/xlsx/routputQvQd.xlsx | copied from sealed test folder tests-de-mort/K20/donnees/routputQvQd.xlsx | 2026-11-13T08:58:26Z | `6a7971b31b7336551705465de8a0855826f3652abe112406f52b2c2ed0994c0c` | 244845 | 319 | yes |
| `philly_spf/meanGrowth.xlsx` | https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/survey-of-professional-forecasters/historical-data/meanGrowth.xlsx | copied from sealed test folder tests-de-mort/K20/donnees/meanGrowth.xlsx | 2026-11-13T08:58:26Z | `4888e773cb4d577970dd24227bca5c7feb2ff79d931de7d0fb70b5bf628ea517` | 146159 | 232 | yes |
| `philly_spf/meanLevel.xlsx` | https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/survey-of-professional-forecasters/historical-data/meanLevel.xlsx | copied from sealed test folder tests-de-mort/K20/donnees/meanLevel.xlsx | 2026-11-13T08:58:26Z | `f2b53e0cb911c71348eddf367eb3bfada1dd9dfcb728c4199efa8846fdfcbee4` | 599838 | 232 | yes |
| `philly_spf/medianGrowth.xlsx` | https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/survey-of-professional-forecasters/historical-data/medianGrowth.xlsx | copied from sealed test folder tests-de-mort/K20/donnees/medianGrowth.xlsx | 2026-11-13T08:58:26Z | `fdcf9ca0299de022c58f8fc35fd20761d8e52b45e038781ae3c4826d1a3cbb5c` | 144611 | 232 | yes |
| `philly_spf/medianLevel.xlsx` | https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/survey-of-professional-forecasters/historical-data/medianLevel.xlsx | copied from sealed test folder tests-de-mort/K20/donnees/medianLevel.xlsx | 2026-11-13T08:58:26Z | `d296e737331c406f7680414504a0d005472743709387f8fda6d969a1d2200977` | 554444 | 232 | yes |
