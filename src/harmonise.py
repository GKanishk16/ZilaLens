"""Create auditable tidy data and an explicitly reviewed district crosswalk."""
from pathlib import Path
import pandas as pd
from rapidfuzz import process, fuzz
from ingest import read_round
ROOT=Path(__file__).resolve().parents[1]
OVERRIDES=ROOT/'data'/'processed'/'district_name_overrides.csv'

def norm(s): return ' '.join(str(s).lower().replace('&','and').replace('.',' ').split())

def harmonise_names(df):
    overrides = pd.read_csv(OVERRIDES) if OVERRIDES.exists() else pd.DataFrame(columns=['round','state','source_district','canonical_district'])
    out=df.copy(); out['district_id']=out['state'].map(norm)+'::'+out['district'].map(norm)
    for _,r in overrides.iterrows():
        m=(out['round']==r['round'])&(out['state']==r['state'])&(out['district']==r['source_district'])
        out.loc[m,'district_id']=norm(r['state'])+'::'+norm(r['canonical_district'])
    return out

def build():
    frames=[]
    for n in ('nfhs4','nfhs5'):
        try: frames.append(read_round(n))
        except FileNotFoundError: pass
    if not frames: raise RuntimeError('No NFHS data files found')
    panel=harmonise_names(pd.concat(frames,ignore_index=True))
    # No automatic fuzzy merges: suggestions are recorded for human review.
    r4=set(panel.loc[panel['round']=='NFHS-4','district_id']); r5=set(panel.loc[panel['round']=='NFHS-5','district_id'])
    cross=pd.DataFrame([{'district_id':x,'nfhs4_present':x in r4,'nfhs5_present':x in r5,'mapping_decision':'exact normalized name; review boundary changes manually'} for x in sorted(r4|r5)])
    for col in ('nfhs4_present','nfhs5_present'): cross[col]=cross[col].astype(bool)
    outdir=ROOT/'data'/'processed'; outdir.mkdir(parents=True,exist_ok=True)
    asp_path=ROOT/'data'/'processed'/'aspirational_districts_112.csv'
    panel['aspirational_flag']=False
    if asp_path.exists():
        asp=pd.read_csv(asp_path)
        aset={(norm(r.state),norm(r.district)) for r in asp.itertuples()}
        match_report=ROOT/'data'/'processed'/'aspirational_list_match_report.csv'
        ambiguous_states=set()
        if match_report.exists():
            mr=pd.read_csv(match_report)
            ambiguous_states={norm(s) for s in mr.loc[~mr.exact_nfhs4_name_match,'state'].unique()}
        flags=[]
        for state,district in zip(panel.state,panel.district):
            key=(norm(state),norm(district))
            flags.append(True if key in aset else (pd.NA if norm(state) in ambiguous_states else False))
        panel['aspirational_flag']=pd.array(flags,dtype='boolean')
    panel.to_csv(outdir/'tidy_panel.csv',index=False)
    cross.to_csv(outdir/'district_crosswalk.csv',index=False)
    # Name suggestions are audit aids and never applied without an override.
    suggestions=[]
    for a in sorted(r4):
        b,score,_=process.extractOne(a,sorted(r5),scorer=fuzz.token_sort_ratio) if r5 else ('',0,None)
        if b and a!=b: suggestions.append({'nfhs4_district_id':a,'suggested_nfhs5_district_id':b,'similarity':score,'applied':False})
    pd.DataFrame(suggestions,columns=['nfhs4_district_id','suggested_nfhs5_district_id','similarity','applied']).to_csv(outdir/'crosswalk_suggestions.csv',index=False)
    return panel,cross

if __name__=='__main__':
    p,c=build(); print(f'{len(p):,} observations; {p.round.nunique()} rounds; {len(c):,} district ids')
