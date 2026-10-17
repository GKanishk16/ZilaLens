"""Text extraction and reproducible policy-review workbook generation."""
from pathlib import Path
import re
import pandas as pd
import pymupdf
ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'data'/'raw'/'docs'

def extract_documents():
    DOCS.mkdir(parents=True,exist_ok=True)
    manifest=[]
    for path in sorted(DOCS.glob('*.pdf')):
        doc=pymupdf.open(path); pages=[]
        for i,page in enumerate(doc,1): pages.append(f'\n[PAGE {i}]\n'+page.get_text())
        txt=''.join(pages); (DOCS/(path.stem+'.txt')).write_text(txt)
        manifest.append({'document':path.name,'pages':len(doc),'text_file':path.stem+'.txt'})
    return pd.DataFrame(manifest)

def build_aspirational_list():
    text='\n'.join(p.get_text() for p in pymupdf.open(DOCS/'aspirational_112.pdf'))
    lines=[x.strip() for x in text.splitlines() if x.strip()]
    states={'Andhra Pradesh','Arunachal Pradesh','Assam','Bihar','Chhattisgarh','Gujarat','Haryana','Himachal Pradesh','Jammu & Kashmir','Jharkhand','Karnataka','Kerala','Madhya Pradesh','Maharashtra','Manipur','Meghalaya','Mizoram','Nagaland','Odisha','Punjab','Rajasthan','Sikkim','Tamil Nadu','Telangana','Tripura','Uttar Pradesh','Uttarakhand'}
    rows=[]
    for i,line in enumerate(lines[:-1]):
        m=re.match(r"^(\d+)\s+(.+)$",line)
        if not m: continue
        number=int(m.group(1)); tail=m.group(2)
        if not 1<=number<=112: continue
        state=next((st for st in sorted(states,key=len,reverse=True) if tail==st),None)
        if state:
            rows.append({'number':number,'state':state,'district':lines[i+1]})
    if len(rows)!=112: raise ValueError(f'Expected 112 official list entries, parsed {len(rows)}')
    out=ROOT/'data'/'processed'/'aspirational_districts_112.csv'; asp=pd.DataFrame(rows); asp.to_csv(out,index=False)
    source=ROOT/'data'/'raw'/'nfhs_district-wise.csv'
    nf=pd.read_csv(source,encoding='latin1')[['state','district']].drop_duplicates()
    norm=lambda x:' '.join(re.sub(r'[^a-z0-9 ]',' ',str(x).lower()).split())
    existing={(norm(r.state),norm(r.district)) for r in nf.itertuples()}
    report=asp.copy(); report['exact_nfhs4_name_match']=[(norm(r.state),norm(r.district)) in existing for r in report.itertuples()]
    report['mapping_status']=report.exact_nfhs4_name_match.map({True:'exact name match',False:'unmatched; parent/child mapping pending'})
    report.to_csv(ROOT/'data'/'processed'/'aspirational_list_match_report.csv',index=False)
    return asp

def build_review_matrix():
    # Curated paraphrases with physical PDF page numbers; these summarize specific cited pages.
    rows=[
      ('pmjdy_brochure.pdf',18,'program design','The mission prioritizes extending banking access through a broader branch and business correspondent network.'),
      ('pmjdy_brochure.pdf',20,'implementation capacity','Interoperability and reliable service points are treated as necessary for account transactions.'),
      ('pmjdy_brochure.pdf',30,'digital access','The document identifies unreliable telecom networks in tribal and hilly areas as an obstacle to correspondent banking.'),
      ('pmjdy_brochure.pdf',30,'implementation capacity','The document calls for coordination and monitoring structures to address implementation and grievance handling.'),
      ('adp_appraisal.pdf',15,'implementation capacity','The appraisal reports stronger district technical and administrative capacity while identifying further capacity-building needs.'),
      ('adp_appraisal.pdf',20,'program design','The programme combines convergence, collaboration, competition, and real-time monitoring in its district governance model.'),
      ('adp_appraisal.pdf',28,'implementation capacity','The appraisal chooses a pre-pandemic observation window to avoid pandemic-related distortion in its own analysis.'),
    ]
    df=pd.DataFrame(rows,columns=['document','page','code','paraphrased_excerpt'])
    df.to_excel(ROOT/'outputs'/'tables'/'policy_coding_matrix.xlsx',index=False)
    convergence=pd.DataFrame([
      {'finding':'District variation and change in women’s account use','supporting_evidence':'Pending NFHS-4/NFHS-5 comparison','contradicting_evidence':'Not assessed; do not infer from programme documents'},
      {'finding':'Account ownership may not equal active independent use','supporting_evidence':'NFHS wording measures women who have and themselves use an account; programme materials describe access infrastructure','contradicting_evidence':'No reviewed passage directly measures independent use; field validation required'},
      {'finding':'Connectivity and local delivery shape service access','supporting_evidence':'PMJDY brochure, p. 30, notes unreliable telecom in some tribal/hilly locations','contradicting_evidence':'Document is a national mission design source, not a district outcome evaluation'},
    ])
    convergence.to_csv(ROOT/'outputs'/'tables'/'convergence_table.csv',index=False)
    return df

if __name__=='__main__':
    print(extract_documents().to_string(index=False)); print('Aspirational list entries:',len(build_aspirational_list())); print('Coded passages:',len(build_review_matrix()))
