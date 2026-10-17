"""Descriptive analysis that only emits two-round statistics when both rounds exist."""
from pathlib import Path
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
COMPARABLE_INDICATORS=(
    'Women who are literate (%)',
    'Women with 10 or more years of schooling (%)',
    'Women age 20-24 years married before age 18 years (%)',
    'Households using clean fuel for cooking (%)',
)

def calculate_changes(panel):
    p=panel.copy()
    p=p[p.indicator.isin(COMPARABLE_INDICATORS)]
    if 'comparison_eligible' in p: p=p[p.comparison_eligible.fillna(False)]
    p=p[p.value.notna()]
    # Geography is keyed by normalized state and district; use one display name
    # per ID to prevent punctuation differences from creating duplicate rows.
    attrs=p.groupby('district_id',as_index=False).agg(state=('state','first'),district=('district','first'))
    wide=p.pivot_table(index=['district_id','indicator'],columns='round',values='value',aggfunc='first').reset_index()
    if not {'NFHS-4','NFHS-5'}.issubset(wide.columns): return pd.DataFrame()
    wide=wide.dropna(subset=['NFHS-4','NFHS-5']).copy()
    wide=wide.merge(attrs,on='district_id',how='left')
    if not {'NFHS-4','NFHS-5'}.issubset(wide.columns): return pd.DataFrame(columns=list(wide.columns)+['change_pp','pct_change'])
    if 'aspirational_flag' in p:
        flags=p.groupby('district_id',as_index=False)['aspirational_flag'].first()
        wide=wide.merge(flags,on='district_id',how='left')
    wide['change_pp']=wide['NFHS-5']-wide['NFHS-4']
    wide['pct_change']=np.where(wide['NFHS-4'].ne(0),100*wide['change_pp']/wide['NFHS-4'],np.nan)
    return wide

def build_quality_report(panel,cross):
    lines=['# Data quality report','',f'- Rows in tidy panel: {len(panel):,}',f"- Rounds present: {', '.join(sorted(panel['round'].unique()))}",f'- District identifiers in crosswalk: {len(cross):,}',f"- Missing values: {panel.value.isna().sum():,} ({panel.value.isna().mean():.1%})",'','## Round availability','']
    lines += [f"- {r}: {panel.loc[panel['round']==r,'district_id'].nunique():,} district identifiers; {len(panel[panel['round']==r]):,} indicator rows" for r in sorted(panel['round'].unique())]
    elig=cross[cross.comparison_eligible] if 'comparison_eligible' in cross else cross.iloc[0:0]
    both=int((elig.nfhs4_present & elig.nfhs5_present).sum())
    changed=int((~cross.comparison_eligible).sum()) if 'comparison_eligible' in cross else 0
    lines += ['', '## Match availability','', f"- NFHS-4 district identifiers: {int(cross.nfhs4_present.sum()):,}; NFHS-5: {int(cross.nfhs5_present.sum()):,}.", f'- {both:,} normalized name candidates are present in both rounds and not listed as changed/new in Harvard Appendix A.', f'- {changed:,} district identifiers are screened out because Appendix A lists them as changed/new; parent/child baseline values are not imputed.', '', '## Interpretation and limits', '', 'Direct changes use only the four consistently worded indicators (women’s literacy, schooling, marriage before 18, and clean cooking fuel) and name-matched districts outside Harvard Appendix A. The appendix provides no complete parent crosswalk, so its 130 entries (128 unique district IDs) are excluded. Name normalization is not proof of boundary identity; these are candidate direct comparisons. Sanitation is excluded because the two rounds use different denominators. Neither factsheet source contains the requested bank-account-use or mobile-phone indicators, so the empowerment index and finance-linked typology remain unavailable.']
    (ROOT/'data_quality_report.md').write_text('\n'.join(lines)+'\n')

def baseline_summaries(panel):
    """Compute transparent NFHS-4 source distribution summaries for indicators available."""
    rows=panel[panel['round']=='NFHS-4'].groupby(['state','indicator'],as_index=False)['value'].agg(['count','mean','median','min','max']).reset_index()
    return rows

def construct_index(panel, indicators=None, weights=None):
    """Equal-weight min-max index across districts; only complete selected indicators."""
    d=panel.pivot_table(index=['district_id','state','district','round'],columns='indicator',values='value',aggfunc='first')
    indicators = indicators or [i for i in d.columns if any(t in i.lower() for t in ['bank','mobile phone','mobile','literate','10 or more years of schooling'])]
    has_financial=any(any(t in i.lower() for t in ['bank','mobile']) for i in indicators)
    has_related=any(any(t in i.lower() for t in ['literate','literacy','schooling']) for i in indicators)
    if len(indicators)<2 or not has_financial or not has_related or not set(indicators).issubset(d.columns):
        return pd.DataFrame(), {'status':'unavailable','reason':'Requires at least one financial access/use indicator and one related empowerment indicator'}
    x=d[indicators].dropna()
    if x.empty: return pd.DataFrame(), {'status':'unavailable','reason':'No complete district cases'}
    scaled=(x-x.min())/(x.max()-x.min()).replace(0,1)
    w=pd.Series(weights,index=indicators,dtype=float) if weights is not None else pd.Series(1/len(indicators),index=indicators)
    w=w/w.sum(); result=scaled.mul(w).sum(axis=1).rename('index_score').reset_index()
    return result, {'status':'computed','weights':w.to_dict(),'districts':len(result)}

def aspirational_did(changes, value_col='change_pp', reps=2000, seed=2026):
    """Non-causal overall and bottom-baseline-quartile contrasts with bootstrap CIs."""
    if changes.empty or 'aspirational_flag' not in changes or 'NFHS-4' not in changes: return pd.DataFrame()
    rng=np.random.default_rng(seed); rows=[]
    for indicator,g in changes.dropna(subset=[value_col,'aspirational_flag','NFHS-4']).groupby('indicator'):
        q=float(g['NFHS-4'].quantile(.25))
        for sample,label in [(g,'all districts'),(g[g['NFHS-4']<=q],'NFHS-4 bottom quartile')]:
            a=sample.loc[sample.aspirational_flag.astype(bool),value_col].to_numpy(); n=sample.loc[~sample.aspirational_flag.astype(bool),value_col].to_numpy()
            if not len(a) or not len(n): continue
            diff=float(a.mean()-n.mean()); boots=[rng.choice(a,len(a),True).mean()-rng.choice(n,len(n),True).mean() for _ in range(reps)]
            rows.append({'indicator':indicator,'comparison':label,'aspirational_mean_change':a.mean(),'comparison_mean_change':n.mean(),'descriptive_difference':diff,'ci_low':np.quantile(boots,.025),'ci_high':np.quantile(boots,.975),'n_aspirational':len(a),'n_comparison':len(n),'interpretation':'descriptive association; not causal'})
    return pd.DataFrame(rows)

def index_sensitivity(panel):
    from scipy.stats import spearmanr
    from sklearn.decomposition import PCA
    outputs=[]
    p=panel.pivot_table(index=['district_id','state','district','round'],columns='indicator',values='value',aggfunc='first')
    candidates=[c for c in p.columns if any(t in c.lower() for t in ['bank','mobile','literate','10 or more years of schooling'])]
    has_financial=any(any(t in c.lower() for t in ['bank','mobile']) for c in candidates)
    has_related=any(any(t in c.lower() for t in ['literate','literacy','schooling']) for c in candidates)
    if len(candidates)<2 or not has_financial or not has_related: return pd.DataFrame(), {'status':'unavailable','reason':'Requires a financial indicator and a related empowerment indicator'}
    results=[]
    for rnd in ('NFHS-4','NFHS-5'):
        if rnd not in p.index.get_level_values('round'): continue
        x=p.xs(rnd,level='round')[candidates].dropna()
        if len(x)<3: continue
        scaled=(x-x.min())/(x.max()-x.min()).replace(0,1)
        equal=scaled.mean(axis=1)
        pc=PCA(n_components=1).fit(scaled)
        weights=np.abs(pc.components_[0]); weights=weights/weights.sum()
        pca_score=scaled.mul(pd.Series(weights,index=candidates),axis=1).sum(axis=1)
        altw=np.array([2 if any(t in c.lower() for t in ['bank','mobile']) else 1 for c in candidates],dtype=float); altw/=altw.sum()
        alt_score=scaled.mul(pd.Series(altw,index=candidates),axis=1).sum(axis=1)
        results.append(pd.DataFrame({'district_id':x.index,'round':rnd,'equal_weight':equal.values,'pca_weight':pca_score.values,'alternative_weight':alt_score.values}))
    if not results: return pd.DataFrame(), {'status':'unavailable','reason':'Insufficient complete cases'}
    scores=pd.concat(results,ignore_index=True)
    corr={}
    for rnd,g in scores.groupby('round'):
        corr[rnd]={a+'__'+b:float(spearmanr(g[a],g[b]).statistic) for a,b in [('equal_weight','pca_weight'),('equal_weight','alternative_weight'),('pca_weight','alternative_weight')]}
    return scores,{'status':'computed','rank_correlations':corr}

def cluster_districts(panel, changes):
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    p=panel.copy()
    if 'comparison_eligible' in p: p=p[p.comparison_eligible.fillna(False)]
    p=p[p.indicator.isin(COMPARABLE_INDICATORS)]
    p=p.pivot_table(index=['district_id','state','district'],columns=['round','indicator'],values='value',aggfunc='first')
    base=[c for c in p.columns if c[0]=='NFHS-4']
    if len(base)<2 or changes.empty: return pd.DataFrame(),{'status':'unavailable','reason':'Requires paired values for common indicators'}
    levels=p[base].copy(); levels.columns=[c[1] for c in levels.columns]
    ch=changes.pivot_table(index=['district_id','state','district'],columns='indicator',values='change_pp')
    early='Women age 20-24 years married before age 18 years (%)'
    # Orient all features so higher values mean a better outcome / faster progress.
    if early in levels: levels[early]=-levels[early]
    if early in ch: ch[early]=-ch[early]
    X=levels.join(ch,rsuffix='_change').dropna()
    if len(X)<4:return pd.DataFrame(),{'status':'unavailable','reason':'Fewer than four complete districts'}
    from sklearn.preprocessing import StandardScaler
    Z=StandardScaler().fit_transform(X)
    candidates=[]
    for k in range(2,min(7,len(X))):
        labels=KMeans(n_clusters=k,random_state=2026,n_init=20).fit_predict(Z)
        candidates.append((silhouette_score(Z,labels),k,labels))
    if not candidates:return pd.DataFrame(),{'status':'unavailable','reason':'No valid cluster count'}
    score,k,labels=max(candidates,key=lambda r:r[0]); result=X.reset_index()[['district_id','state','district']].copy();result['cluster_id']=labels
    baseline_cols=[c for c in X.columns if not c.endswith('_change')]
    change_cols=[c for c in X.columns if c.endswith('_change')]
    overall_base=X[baseline_cols].mean().mean(); overall_change=X[change_cols].mean().mean() if change_cols else 0
    names={}
    for cid,g in X.assign(cluster_id=labels).groupby('cluster_id'):
        hb=g[baseline_cols].mean().mean()>=overall_base if baseline_cols else False
        fc=g[change_cols].mean().mean()>=overall_change if change_cols else False
        names[cid]=('Stronger' if hb else 'Weaker')+' baseline, '+('faster improvement' if fc else 'slower improvement')
    result['cluster_name']=result['cluster_id'].map(names)
    return result,{'status':'computed','k':k,'silhouette':float(score),'names':names}

def run_analysis(panel):
    out=ROOT/'outputs'/'tables'; out.mkdir(parents=True,exist_ok=True)
    changes=calculate_changes(panel); changes.to_csv(out/'district_changes.csv',index=False)
    base=baseline_summaries(panel); base.to_csv(out/'nfhs4_state_indicator_summary.csv',index=False)
    if not changes.empty:
        summary=changes.groupby(['state','indicator'],as_index=False).change_pp.agg(['count','mean','median','min','max']).reset_index(); summary.to_csv(out/'change_state_summary.csv',index=False)
        ranked=[]
        for indicator,g in changes.dropna(subset=['change_pp']).groupby('indicator'):
            for label,part in [('top20',g.nlargest(20,'change_pp')),('bottom20',g.nsmallest(20,'change_pp'))]:
                tmp=part.copy();tmp['rank_group']=label;ranked.append(tmp)
        pd.concat(ranked,ignore_index=True).to_csv(out/'district_rankings.csv',index=False)
    else:
        pd.DataFrame(columns=['state','indicator','count','mean','median','min','max']).to_csv(out/'change_state_summary.csv',index=False)
        pd.DataFrame(columns=list(changes.columns)+['rank_group']).to_csv(out/'district_rankings.csv',index=False)
    # Explicitly label this as a descriptive four-indicator typology, not a
    # finance or empowerment index (bank/mobile indicators are unavailable).
    index,meta=construct_index(panel)
    if index.empty:index=pd.DataFrame(columns=['district_id','state','district','round','index_score'])
    index.to_csv(out/'empowerment_index.csv',index=False)
    sensitivity,smeta=index_sensitivity(panel)
    if sensitivity.empty:sensitivity=pd.DataFrame(columns=['district_id','round','equal_weight','pca_weight','alternative_weight'])
    sensitivity.to_csv(out/'index_sensitivity.csv',index=False)
    clusters,cmeta=cluster_districts(panel,changes)
    if clusters.empty:clusters=pd.DataFrame(columns=['district_id','state','district','cluster_id','cluster_name'])
    clusters.to_csv(out/'district_clusters.csv',index=False)
    did=aspirational_did(changes)
    if did.empty:did=pd.DataFrame(columns=['indicator','comparison','aspirational_mean_change','comparison_mean_change','descriptive_difference','ci_low','ci_high','n_aspirational','n_comparison','interpretation'])
    did.to_csv(out/'aspirational_comparison.csv',index=False)
    # Transparent UP cross-section ranking. Marriage before 18 is reversed so
    # lower mean rank indicates comparatively weaker outcomes; this is not the
    # finance-linked index requested in the original design.
    up=panel[(panel['round']=='NFHS-5') & (panel.state=='Uttar Pradesh') & panel.indicator.isin(COMPARABLE_INDICATORS)].pivot_table(index=['district_id','state','district'],columns='indicator',values='value',aggfunc='first').reset_index()
    rank_cols=[]
    for indicator in COMPARABLE_INDICATORS:
        if indicator not in up: continue
        better_high=indicator!='Women age 20-24 years married before age 18 years (%)'
        col=indicator+'__rank'; up[col]=up[indicator].rank(ascending=not better_high,method='average'); rank_cols.append(col)
    up['mean_rank']=up[rank_cols].mean(axis=1) if rank_cols else np.nan
    up['rank']=up['mean_rank'].rank(method='min').astype('Int64') if rank_cols else pd.NA
    up['ranking_note']='Mean rank across available NFHS-5 literacy, schooling, early marriage (reverse), and clean-fuel indicators; descriptive, not a financial inclusion index.'
    up.sort_values(['rank','district']).to_csv(out/'up_district_rankings.csv',index=False)
    import json
    (out/'index_sensitivity_status.json').write_text(json.dumps(smeta,indent=2,ensure_ascii=False))
    (out/'analysis_status.md').write_text('# Analysis status\n\n'+f"- Change rows: {len(changes)}\n- Comparable indicators: {len(COMPARABLE_INDICATORS)}\n- Complete matched districts with all four indicators: {changes.district_id.nunique() if not changes.empty else 0}\n- NFHS-5 present: {'NFHS-5' in set(panel['round'])}\n- District screen: Harvard Appendix A changed/new geography entries excluded from direct comparisons; parent values not imputed.\n- Index: {meta['status']} ({meta['reason'] if 'reason' in meta else 'computed'})\n- Aspirational district comparison: {len(did)} descriptive contrasts; unknown roster mappings retained as missing.\n- Index sensitivity: {smeta['status']} ({smeta.get('reason','rank correlations computed')}).\n- Typology: {cmeta['status']} ({cmeta.get('reason','four-indicator descriptive typology; silhouette-selected k')}).\n- UP rankings: {len(up)} NFHS-5 district records, using a mean rank over the four comparable indicators (not a finance index).\n\nChanges are descriptive and do not establish causal effects. Finance/mobile indicators are absent from both factsheet sources; no finance-linked index is computed.\n")
    return changes,base,meta
