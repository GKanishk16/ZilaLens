# Power BI build guide

## Relationships

- `dim_district[district_id]` 1:* `fact_indicator_values[district_id]`
- `dim_indicator[indicator_key]` 1:* `fact_indicator_values[indicator_key]`
- `dim_round[round]` 1:* fact
- `dim_cluster[district_id]` 1:* district when cluster results become available

## Measures

1. `PP Change = [NFHS-5 Value] - [NFHS-4 Value]`

2. `NFHS-4 Value = CALCULATE(AVERAGE(fact_indicator_values[value]), dim_round[round] = "NFHS-4")`

3. `NFHS-5 Value = CALCULATE(AVERAGE(fact_indicator_values[value]), dim_round[round] = "NFHS-5")`

4. `District Count = DISTINCTCOUNT(dim_district[district_id])`

5. `Districts Improved = CALCULATE(DISTINCTCOUNT(dim_district[district_id]), FILTER(VALUES(dim_district[district_id]), [PP Change] > 0))`

6. `Districts Improved % = DIVIDE([Districts Improved], [District Count])`

7. `Index Score = AVERAGE(fact_indicator_values[index_score])`

8. `Aspirational Mean Change = CALCULATE([PP Change], dim_district[aspirational_flag] = TRUE())`

9. `Non-Aspirational Mean Change = CALCULATE([PP Change], dim_district[aspirational_flag] = FALSE())`

10. `Aspirational Gap = [Aspirational Mean Change] - [Non-Aspirational Mean Change]`

## Pages

1. National Overview: map, indicator selector, round values, distribution and improved share.
2. Aspirational Districts Comparison: descriptive changes and matched baseline subgroup; label as non-causal.
3. Uttar Pradesh Deep Dive: district ranks, Ghaziabad/Gautam Buddha Nagar callouts, state/national reference lines.

Four-indicator NFHS-4/NFHS-5 comparisons are available. Changed/new geographies are excluded from direct comparison. `Index Score` remains blank because both factsheet sources lack bank-use/mobile-use indicators.
