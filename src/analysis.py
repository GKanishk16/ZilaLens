"""Descriptive analysis that only emits two-round statistics when both rounds exist."""
from pathlib import Path
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
CORE_TERMS=['bank','mobile','literate','10 or more years of schooling','married before age 18','clean fuel','improved sanitation']

def calculate_changes(panel):
    p=panel.copy(); p=p[p.indicator.str.lower().map(lambda x:any(t in x for t in CORE_TERMS))]
    wide=p.pivot_table(index=['district_id','state','district','indicator'],columns='round',values='value',aggfunc='first').reset_index()
    if not {'NFHS-4','NFHS-5'}.issubset(wide.columns): return pd.DataFrame(columns=list(wide.columns)+['change_pp','pct_change'])
    wide['change_pp']=wide['NFHS-5']-wide['NFHS-4']
    wide['pct_change']=np.where(wide['NFHS-4'].ne(0),100*wide['change_pp']/wide['NFHS-4'],np.nan)
    return wide

def build_quality_report(panel,cross):
    lines=['# Data quality report','',f'- Rows in tidy panel: {len(panel):,}',f"- Rounds present: {', '.join(sorted(panel['round'].unique()))}",f'- District identifiers in crosswalk: {len(cross):,}',f"- Missing values: {panel.value.isna().sum():,} ({panel.value.isna().mean():.1%})",'','## Round availability','']
    lines += [f"- {r}: {panel.loc[panel['round']==r,'district_id'].nunique():,} district identifiers; {len(panel[panel['round']==r]):,} indicator rows" for r in sorted(panel['round'].unique())]
    lines += ['', '## Interpretation and limits','', 'The NFHS-5 workbook could not be retrieved from data.gov.in in this environment (HTTP 403). Consequently no two-round changes, index, typology, matched comparison, or UP change analysis is computed. Crosswalk rows are normalized-name candidates, not a completed parent/child boundary crosswalk. Add the official workbook at `data/raw/NFHS_5_India_Districts_Factsheet_Data.xls`, review `data/processed/crosswalk_suggestions.csv`, and document approved mappings in the override file before interpreting changes.']
    (ROOT/'data_quality_report.md').write_text('\n'.join(lines)+'\n')
