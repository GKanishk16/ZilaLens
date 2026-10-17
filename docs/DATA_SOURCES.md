# Data sources and acquisition log

Acquisition date: 2026-10-18 (UTC date). Source URLs and status are recorded here; rerunning `python run_all.py` re-download is not automatic for cached sources, preventing overwriting user-provided files.

| Source | URL | Local file | Status |
|---|---|---|---|
| NFHS-4 district factsheet compilation, HindustanTimesLabs | https://github.com/HindustanTimesLabs/nfhs-data (raw CSV: https://raw.githubusercontent.com/HindustanTimesLabs/nfhs-data/master/nfhs_district-wise.csv) | `data/raw/nfhs_district-wise.csv` | Downloaded 2026-10-18; 9,053,904 bytes; repository README identifies NFHS-4 (2015-16), district-wise, 93 indicators. |
| NFHS-5 India Districts Factsheet Data, data.gov.in | https://www.data.gov.in/catalog/national-family-health-survey-5-nfhs-5-india-districts-factsheet-data-provisional | `data/raw/NFHS_5_India_Districts_Factsheet_Data.xls` | Catalog resource workbook listed at 740 KB; direct resource URL https://data.gov.in/files/ogdpv2dms/s3fs-public/datafile/NFHS_5_India_Districts_Factsheet_Data.xls returned HTTP 403 on 2026-10-18. Place the official workbook manually at the exact path above. |
| Harvard Geographic Insights / district policy tracker methodology | https://geographicinsights.iq.harvard.edu/ | N/A | Methodology to be consulted and documented before parent/child district crosswalk decisions; no mappings inferred from fuzzy names. |
| Aspirational Districts Programme | https://www.niti.gov.in/aspirational-districts-programme | pending | Official 112-district list to be downloaded and versioned before comparisons. |
| District boundaries | https://github.com/HindustanTimesLabs/shapefiles/tree/master/india | pending | Candidate public district boundary repository; confirm vintage and licence before maps. |
| PMJDY | https://pmjdy.gov.in/ | pending | Official guidance/progress pages; qualitative review pending source capture. |
| NITI Aayog programme reports | https://www.niti.gov.in/ | pending | Official reports; qualitative review pending source capture. |

The NFHS-4 source contains district indicators for literacy, schooling, marriage before 18, clean cooking fuel, and sanitation. Bank-account and mobile-phone core indicators are not present in this compilation under the requested wording. Exact common indicators will be determined only after the NFHS-5 workbook is available.

Underlying survey data belong to their original publishers (IIPS/MoHFW NFHS, data.gov.in, and NITI Aayog). This repository's MIT licence applies to code, not source data.
