from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from harmonise import build
from analysis import build_quality_report,run_analysis
from qualitative import extract_documents,build_aspirational_list,build_review_matrix
import pandas as pd
build_aspirational_list(); extract_documents(); build_review_matrix()
panel,cross=build(); build_quality_report(panel,cross)
changes,base,meta=run_analysis(panel)
print(f'Pipeline finished: {len(panel):,} panel rows, {len(changes):,} two-round changes.')
