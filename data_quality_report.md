# Data quality report

- Rows in tidy panel: 59,241
- Rounds present: NFHS-4
- District identifiers in crosswalk: 637
- Missing values: 4,142 (7.0%)

## Round availability

- NFHS-4: 637 district identifiers; 59,241 indicator rows

## Match availability

- NFHS-4 round presence: 637/637 provisional district identifiers (100% of the NFHS-4 identifiers by construction).
- NFHS-5 round presence: unavailable; the official workbook could not be retrieved.

## Interpretation and limits

The NFHS-5 workbook could not be retrieved from data.gov.in in this environment (HTTP 403). Consequently no two-round changes, index, typology, matched comparison, or UP change analysis is computed. Crosswalk rows are normalized-name candidates, not a completed parent/child boundary crosswalk. Add the official workbook at `data/raw/NFHS_5_India_Districts_Factsheet_Data.xls`, review `data/processed/crosswalk_suggestions.csv`, and document approved mappings in the override file before interpreting changes.
