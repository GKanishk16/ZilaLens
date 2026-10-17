# ZilaLens
## Women's Financial Inclusion and Empowerment Across Indian Districts, NFHS-4 (2015-16) to NFHS-5 (2019-21)

**Author:** Kanishk Gupta  
**About the Author:** Kanishk Gupta, PGDM (Research & Business Analytics), Lal Bahadur Shastri Institute of Management, Delhi — [GitHub](https://github.com/GKanishk16)

"Zila" is Hindi for district; ZilaLens views women's financial inclusion through a district lens.

ZilaLens is a reproducible research project designed to compare women's financial inclusion and related empowerment indicators across Indian districts. All findings are intended to come from public source files and are subject to survey and boundary limitations.

## Current data status

NFHS-4 district factsheet compilation is present in `data/raw/nfhs_district-wise.csv`. The official NFHS-5 workbook listed in the data.gov.in catalog could not be downloaded in this environment (HTTP 403). Two-round results and all cross-round deliverables are therefore pending; no changes, rankings, clusters, or impact estimates are claimed. Download the catalog resource **“India Districts Factsheets of National Family Health Survey (NFHS) - 5, 2019-2021”** (Excel workbook, approximately 740 KB) and save it exactly as `data/raw/NFHS_5_India_Districts_Factsheet_Data.xls`, then rerun the pipeline. Source record: [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md).

## Key Findings

NFHS-5 has not been acquired, so these are data-readiness findings rather than outcome findings:

1. The NFHS-4 source CSV contains **59,241 district-indicator rows** across 10 columns ([source file](data/raw/nfhs_district-wise.csv)).
2. The source repository documents **93 district-level indicators** ([source README](data/raw/README.md)).
3. The parsed NFHS-4 panel currently has **637 district identifiers** ([crosswalk](data/processed/district_crosswalk.csv)).
4. **7.0%** of total NFHS-4 indicator values are missing in the parsed panel ([quality report](data_quality_report.md)).
5. **96 of 112** NITI list entries match NFHS-4 state–district names exactly; 16 need geography review ([match report](data/processed/aspirational_list_match_report.csv)).

None of these is a finding about change in women’s outcomes. See [`data_quality_report.md`](data_quality_report.md) for availability and missingness diagnostics.

## Setup and run

Python 3.11 is the target runtime.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run_all.py
```

## Repository guide

- `src/`: ingestion, harmonisation, and analysis code
- `data/raw/`: source files (large/raw files are not committed; download scripts and URLs are documented)
- `data/processed/`: tidy panel, crosswalk, and reviewed name overrides
- `docs/`: source register and qualitative codebook
- `outputs/`: tables, charts, maps, workbook, reports, and deck
- `tests/`: pipeline tests

Raw files over 50 MB must not be committed. Keep them reproducible through source links/download scripts. Never commit API keys or tokens. Data belongs to IIPS/MoHFW NFHS, data.gov.in, and NITI Aayog; the MIT licence covers code only.

## Preview maps

NFHS-4 baseline maps are included as interim previews; NFHS-5 levels and round-to-round change maps are pending the official workbook.

![NFHS-4 women literacy by district](outputs/maps/women_literate_nfhs4.png)

![NFHS-4 improved sanitation by district](outputs/maps/improved_sanitation_nfhs4.png)

## Deliverables

- [Research report](outputs/reports/ZilaLens_Research_Report.docx) — interim report; two-round findings pending NFHS-5
- [Policy brief](outputs/reports/ZilaLens_Policy_Brief.docx) — interim evidence brief
- [Concept note](outputs/reports/ZilaLens_Concept_Note.docx) — draft; district selection pending verified analysis
- [Deck](outputs/deck/ZilaLens_Deck.pptx) — interim evidence-gap deck; comparative findings pending NFHS-5
- [Analysis workbook](outputs/tables/ZilaLens_Analysis_Workbook.xlsx), [logframe](outputs/tables/ZilaLens_Logframe.xlsx), and [bilingual field tool](outputs/tables/ZilaLens_Field_Validation_XLSForm.xlsx)

## File inventory

The tracked project file list is in [ZilaLens_File_Manifest.md](outputs/reports/ZilaLens_File_Manifest.md).

## Citation

See [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md). Every statistic in the final deliverables will cite its source table and be traceable to a file in `data/`.
