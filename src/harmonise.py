"""Create auditable tidy data and apply a documented geography screen."""
from pathlib import Path
import re
import pandas as pd
from rapidfuzz import process, fuzz
from ingest import read_round
import pymupdf

ROOT=Path(__file__).resolve().parents[1]
OVERRIDES=ROOT/'data'/'processed'/'district_name_overrides.csv'
HARVARD=ROOT/'data'/'raw'/'docs'/'harvard_nfhs_policy_tracker_technical_notes.pdf'

STATE_ALIASES={'Maharastra':'Maharashtra','NCT of Delhi':'NCT Delhi'}
# Spelling variants transcribed from Harvard Appendix A and the NFHS-5 workbook.
APPENDIX_ALIASES={
    ('Arunachal Pradesh','Langding'):'Longding',
    ('Assam','South Salmara-Mankachar'):'South Salmara Mancachar',
    ('Assam','Karbi Anglong West'):'West Karbi Anglong',
    ('Chhattisgarh','Gariaband'):'Gariaband',
    ('Gujarat','Devbhoomi Dwarka'):'Devbhumi Dwarka',
    ('Haryana','Dadri'):'Charkhi Dadri',
    ('Meghalaya','East Jaintia Hills'):'East Jantia Hills',
    ('Punjab','Ferozpur'):'Ferozepur',
    ('Telangana','Kumuram Bheem (Asifabad)'):'Komaram Bheem Asifabad',
    ('Telangana','Jagtial'):'Jagitial',
    ('Telangana','Peddapalle'):'Peddapalli',
    ('Telangana','Jogulambha Gadwal'):'Jogulamba Gadwal',
    ('Telangana','Mahbubnagar'):'Mahabubnagar',
    ('Telangana','Jangaon'):'Jangoan',
}

def norm(s):
    return re.sub(r'[^a-z0-9]','',str(s).lower())

def state_norm(s):
    return norm(STATE_ALIASES.get(str(s).strip(),str(s).strip()))

def appendix_rows():
    if not HARVARD.exists():
        return pd.DataFrame(columns=['state','district','calculation'])
    doc=pymupdf.open(HARVARD); rows=[]
    for page_no in range(50,54):
        tables=doc[page_no].find_tables().tables
        if not tables: continue
        for row in tables[0].extract()[1:]:
            cells=[str(v).strip() for v in row if v and str(v).strip()]
            if len(cells)==3 and cells[2].startswith('Example'):
                rows.append({'state':cells[0],'district':cells[1],'calculation':cells[2]})
    result=pd.DataFrame(rows).drop_duplicates()
    if len(result)!=130:
        raise ValueError(f'Expected 130 Harvard Appendix A geography rows, found {len(result)}')
    return result

def harmonise_names(df):
    out=df.copy()
    out['state']=out.state.map(lambda s: STATE_ALIASES.get(str(s).strip(),str(s).strip()))
    out['district_id']=out.state.map(state_norm)+'::'+out.district.map(norm)
    overrides=pd.read_csv(OVERRIDES) if OVERRIDES.exists() else pd.DataFrame(columns=['round','state','source_district','canonical_district'])
    for r in overrides.itertuples():
        m=(out['round']==r.round)&(out['state']==r.state)&(out['district']==r.source_district)
        out.loc[m,'district_id']=state_norm(r.state)+'::'+norm(r.canonical_district)
    changed=appendix_rows()
    changed_keys=set()
    for r in changed.itertuples():
        district=APPENDIX_ALIASES.get((r.state,r.district),r.district)
        changed_keys.add(state_norm(r.state)+'::'+norm(district))
    out['geography_status']=out.district_id.map(lambda k:'changed_or_new_per_Harvard_Appendix_A' if k in changed_keys else 'unchanged_name_candidate')
    # Keep unresolved geography out of direct comparisons. Parent values are not
    # imputed because Appendix A does not identify the relevant parent(s).
    out['geography_eligible']=out.geography_status.eq('unchanged_name_candidate')
    return out,changed

def build():
    frames=[]
    for n in ('nfhs4','nfhs5'):
        try: frames.append(read_round(n))
        except FileNotFoundError: pass
    if not frames: raise RuntimeError('No NFHS data files found')
    panel,changed=harmonise_names(pd.concat(frames,ignore_index=True))
    r4=set(panel.loc[panel['round']=='NFHS-4','district_id']); r5=set(panel.loc[panel['round']=='NFHS-5','district_id'])
    paired=r4&r5
    panel['comparison_eligible']=panel.district_id.isin(paired)&panel.geography_eligible
    cross=pd.DataFrame([{'district_id':x,'nfhs4_present':x in r4,'nfhs5_present':x in r5,'geography_status':panel.loc[panel.district_id.eq(x),'geography_status'].iloc[0],'geography_eligible':bool(panel.loc[panel.district_id.eq(x),'geography_eligible'].all()),'comparison_eligible':x in paired and bool(panel.loc[panel.district_id.eq(x),'geography_eligible'].all()),'mapping_decision':'normalized exact name; changed/new geographies excluded per Harvard Appendix A'} for x in sorted(r4|r5)])
    for col in ('nfhs4_present','nfhs5_present','geography_eligible','comparison_eligible'): cross[col]=cross[col].astype(bool)
    outdir=ROOT/'data'/'processed'; outdir.mkdir(parents=True,exist_ok=True)
    changed.to_csv(outdir/'harvard_changed_geographies.csv',index=False)
    asp_path=outdir/'aspirational_districts_112.csv'; panel['aspirational_flag']=pd.array([pd.NA]*len(panel),dtype='boolean')
    if asp_path.exists():
        asp=pd.read_csv(asp_path); aset={(state_norm(r.state),norm(r.district)) for r in asp.itertuples()}
        mr_path=outdir/'aspirational_list_match_report.csv'; ambiguous=set()
        if mr_path.exists():
            mr=pd.read_csv(mr_path); ambiguous={state_norm(s) for s in mr.loc[~mr.exact_nfhs4_name_match,'state'].unique()}
        flags=[True if (state_norm(s),norm(d)) in aset else (pd.NA if state_norm(s) in ambiguous else False) for s,d in zip(panel.state,panel.district)]
        panel['aspirational_flag']=pd.array(flags,dtype='boolean')
    panel.to_csv(outdir/'tidy_panel.csv',index=False); cross.to_csv(outdir/'district_crosswalk.csv',index=False)
    suggestions=[]
    for a in sorted(r4):
        b,score,_=process.extractOne(a,sorted(r5),scorer=fuzz.token_sort_ratio) if r5 else ('',0,None)
        if b and a!=b: suggestions.append({'nfhs4_district_id':a,'suggested_nfhs5_district_id':b,'similarity':score,'applied':False})
    pd.DataFrame(suggestions,columns=['nfhs4_district_id','suggested_nfhs5_district_id','similarity','applied']).to_csv(outdir/'crosswalk_suggestions.csv',index=False)
    return panel,cross

if __name__=='__main__':
    p,c=build(); print(f'{len(p):,} observations; {p.round.nunique()} rounds; {len(c):,} district ids; {c.comparison_eligible.sum():,} candidate direct comparisons')
