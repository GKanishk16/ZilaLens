# Data sources and acquisition log

Acquisition date: 2026-10-18 (UTC date). Source URLs and status are recorded here; rerunning `python run_all.py` re-download is not automatic for cached sources, preventing overwriting user-provided files.

| Source | URL | Local file | Status |
|---|---|---|---|
| NFHS-4 district factsheet compilation, HindustanTimesLabs | https://github.com/HindustanTimesLabs/nfhs-data (raw CSV: https://raw.githubusercontent.com/HindustanTimesLabs/nfhs-data/master/nfhs_district-wise.csv) | `data/raw/nfhs_district-wise.csv` | Downloaded 2026-10-18; 9,053,904 bytes; repository README identifies NFHS-4 (2015-16), district-wise, 93 indicators. |
| NFHS-5 India Districts Factsheet Data, data.gov.in | https://www.data.gov.in/catalog/national-family-health-survey-5-nfhs-5-india-districts-factsheet-data-provisional | `data/raw/NFHS_5_India_Districts_Factsheet_Data.xls` | Official workbook supplied by the user on 2026-10-18 after the catalog's direct resource URL returned HTTP 403. Contains 707 district records and 107 indicator columns. |
| Harvard Geographic Insights, NFHS Policy Tracker for Districts: User Guide and Technical Notes (Feb. 7, 2022) | https://geographicinsights.iq.harvard.edu/ | `data/raw/docs/harvard_nfhs_policy_tracker_technical_notes.pdf`; extracted text in same folder | Retrieved as an archived copy from https://web.archive.org/web/20220216163748id_/https://geographicinsights.iq.harvard.edu/files/geographicinsights2/files/user_guide_and_technical_notes_feb7_2022.pdf after the original host was unavailable. Appendix A lists 130 changed/new NFHS-5 geographies; these are excluded from direct comparison. The appendix does not identify all parent districts, so no parent-value imputation is attempted. |
| Aspirational Districts Programme | https://www.niti.gov.in/aspirational-districts-programme | `data/raw/docs/aspirational_112.pdf`; `data/processed/aspirational_districts_112.csv` | The official 112-district 2022 roster was downloaded and parsed. Exact NFHS-4 state–district name matches: 96/112; 16 roster entries remain unresolved and are not force-mapped. |
| District boundaries | https://github.com/HindustanTimesLabs/shapefiles/tree/master/india | `data/raw/india_districts.geojson` | Downloaded 2026-10-18 (752 KB; 645 features). Used for illustrative NFHS-4 maps only. The source notes accuracy is not guaranteed and its boundary vintage is not confirmed to match either survey round. |
| PMJDY | https://pmjdy.gov.in/ | `data/raw/docs/pmjdy_brochure.pdf`; `data/raw/docs/pmjdy_brochure.txt` | Official Department of Financial Services PMJDY brochure downloaded and text extracted with page markers. Coded excerpts are paraphrases, cited to physical PDF pages; the 2014 brochure is treated as policy design material, not outcome evidence. |
| NITI Aayog programme reports | https://www.niti.gov.in/ | `data/raw/docs/adp_appraisal.pdf`; `data/raw/docs/adp_appraisal.txt` | NITI Aayog/UNDP Aspirational Districts Programme appraisal downloaded and text extracted with page markers. Coded excerpts are paraphrases, cited to physical PDF pages. |

The two source files share four comparable indicators used for change analysis: women’s literacy, women’s schooling (10+ years), marriage before age 18, and clean cooking fuel. Sanitation is excluded because NFHS-4 and NFHS-5 use different denominators. Bank-account-use and mobile-phone indicators are absent from both factsheet sources, so a finance-linked index cannot be estimated. The project reports a separate four-indicator outcome typology, which is not finance-specific.

Underlying survey data belong to their original publishers (IIPS/MoHFW NFHS, data.gov.in, and NITI Aayog). This repository's MIT licence applies to code, not source data.

Additional files downloaded to `data/raw/docs/` on 2026-10-18:

| Source | URL | Local file | Status |
|---|---|---|---|
| NITI Aayog, List of 112 Aspirational Districts | https://www.niti.gov.in/sites/default/files/2022-09/List-of-Aspirational-Districts.pdf | `data/raw/docs/aspirational_112.pdf` | Downloaded (143 KB); parsed to `data/processed/aspirational_districts_112.csv`, 112 rows. List vintage is 2022; retained as the requested 112-district cohort. |
| Department of Financial Services, PMJDY Mission Document/Brochure | https://pmjdy.gov.in/files/E-Documents/PMJDY_BROCHURE_ENG.pdf | `data/raw/docs/pmjdy_brochure.pdf` | Downloaded (4.2 MB); text extracted with physical page markers. |
| NITI Aayog / UNDP, Aspirational Districts Programme: An Appraisal | https://www.niti.gov.in/sites/default/files/2023-03/Aspirational-Districts-Programme-An-Appraisal.pdf | `data/raw/docs/adp_appraisal.pdf` | Downloaded (4.0 MB); text extracted with physical page markers. |

PMJDY material is a 2014 mission brochure. The coded excerpts are paraphrases, cited by physical PDF page, and should be read as policy design statements rather than independent evidence of district-level results.

| District boundaries, HindustanTimesLabs | https://raw.githubusercontent.com/HindustanTimesLabs/shapefiles/master/india/district/india_district.json | `data/raw/india_districts.geojson` | Downloaded 2026-10-18 (752 KB), 645 district features; README describes source accuracy as not guaranteed. Used for illustrative NFHS-4 preview maps only; boundary vintage is not assured to match either survey round. |

The field survey XLSForm is an original research instrument, not a source dataset. Pyxform conversion to XForm XML succeeds with no warnings. ODK Validate's additional Java-based validation was unavailable because no Java runtime is installed in the bundled runtime; the form passed pyxform conversion/structure checks.

The exact-name match report is generated by comparing the official 112-entry NITI roster against distinct NFHS-4 state–district names. It finds 96 exact matches and retains 16 unmatched roster names in `data/processed/aspirational_list_match_report.csv`. Unresolved states are treated as unknown for non-matching panel rows rather than automatically assigning them to the non-aspirational group.
