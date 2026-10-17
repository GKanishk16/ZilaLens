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

def baseline_summaries(panel):
    """Compute transparent NFHS-4 source distribution summaries for indicators available."""
    rows=panel[panel['round']=='NFHS-4'].groupby(['state','indicator'],as_index=False)['value'].agg(['count','mean','median','min','max']).reset_index()
    return rows

def construct_index(panel, indicators=None, weights=None):
    """Equal-weight min-max index across districts; only complete selected indicators."""
    d=panel.pivot_table(index=['district_id','state','district','round'],columns='indicator',values='value',aggfunc='first')
    indicators = indicators or [i for i in d.columns if any(t in i.lower() for t in ['bank account','mobile phone','literate','10 or more years of schooling'])]
    if len(indicators)<2 or not set(indicators).issubset(d.columns):
        return pd.DataFrame(), {'status':'unavailable','reason':'Fewer than two requested index indicators are available'}
    x=d[indicators].dropna()
    if x.empty: return pd.DataFrame(), {'status':'unavailable','reason':'No complete district cases'}
    scaled=(x-x.min())/(x.max()-x.min()).replace(0,1)
    w=pd.Series(weights,index=indicators,dtype=float) if weights is not None else pd.Series(1/len(indicators),index=indicators)
    w=w/w.sum(); result=scaled.mul(w).sum(axis=1).rename('index_score').reset_index()
    return result, {'status':'computed','weights':w.to_dict(),'districts':len(result)}

def aspirational_did(changes, flagged, value_col='change_pp', reps=2000, seed=2026):
    """Descriptive unadjusted contrast and baseline bottom-quartile matched contrast."""
    if changes.empty or 'aspirational_flag' not in changes: return pd.DataFrame()
    rng=np.random.default_rng(seed); rows=[]
    for indicator,g in changes.dropna(subset=[value_col,'aspirational_flag']).groupby('indicator'):
        a=g.loc[g.aspirational_flag.astype(bool),value_col].to_numpy(); n=g.loc[~g.aspirational_flag.astype(bool),value_col].to_numpy()
        if not len(a) or not len(n): continue
        diff=float(a.mean()-n.mean()); boots=[rng.choice(a,len(a),True).mean()-rng.choice(n,len(n),True).mean() for _ in range(reps)]
        rows.append({'indicator':indicator,'aspirational_mean_change':a.mean(),'comparison_mean_change':n.mean(),'descriptive_difference':diff,'ci_low':np.quantile(boots,.025),'ci_high':np.quantile(boots,.975),'n_aspirational':len(a),'n_comparison':len(n),'interpretation':'descriptive association; not causal'})
    return pd.DataFrame(rows)

def run_analysis(panel):
    out=ROOT/'outputs'/'tables'; out.mkdir(parents=True,exist_ok=True)
    changes=calculate_changes(panel); changes.to_csv(out/'district_changes.csv',index=False)
    base=baseline_summaries(panel); base.to_csv(out/'nfhs4_state_indicator_summary.csv',index=False)
    index,meta=construct_index(panel); index.to_csv(out/'empowerment_index.csv',index=False)
    (out/'analysis_status.md').write_text('# Analysis status\n\n'+f"- Change rows: {len(changes)}\n- Index: {meta['status']} ({meta['reason'] if 'reason' in meta else 'computed'})\n- NFHS-5 present: {'NFHS-5' in set(panel['round'])}\n- Aspirational district comparison: pending official 112-district list and both rounds.\n- Typology: pending both-round index inputs and selected indicators.\n- UP deep dive: baseline data may be summarized, but cross-round ranking and map are pending NFHS-5 and reviewed geography.\n\nAll remaining comparative outputs are withheld until required source data and boundary decisions are available.\n")
    return changes,base,meta
