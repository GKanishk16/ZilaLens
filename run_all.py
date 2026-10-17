from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'work'/'pydeps'))
from harmonise import build
from analysis import build_quality_report,run_analysis
from qualitative import extract_documents,build_aspirational_list,build_review_matrix
from visualize import build_powerbi,build_workbook,make_map
from program_design import theory_of_change,logframe,xlsform,validate_xlsform
from deliverables import build_all
import pandas as pd
build_aspirational_list(); extract_documents(); build_review_matrix()
theory_of_change(); logframe(); xlsform(); validate_xlsform()
panel,cross=build(); build_quality_report(panel,cross)
changes,base,meta=run_analysis(panel)
build_powerbi(panel); build_workbook(panel)
for ind,slug in [('Women who are literate (%)','women_literate'),('Households using improved sanitation facility','improved_sanitation')]:
    if ind in set(panel.indicator):
        make_map(panel,ind,('District literacy varies across India (NFHS-4)' if slug=='women_literate' else 'Improved sanitation varies across India (NFHS-4)'),ROOT/'outputs'/'maps'/f'{slug}_nfhs4.png')
        make_map(panel,ind,('Uttar Pradesh district literacy (NFHS-4)' if slug=='women_literate' else 'Uttar Pradesh improved sanitation (NFHS-4)'),ROOT/'outputs'/'maps'/f'{slug}_up_nfhs4.png',state='Uttar Pradesh')
build_all()
print(f'Pipeline finished: {len(panel):,} panel rows, {len(changes):,} two-round changes.')
