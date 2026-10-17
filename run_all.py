from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from harmonise import build
from analysis import build_quality_report,calculate_changes
import pandas as pd
panel,cross=build(); build_quality_report(panel,cross)
changes=calculate_changes(panel)
(ROOT/'outputs'/'tables'/'district_changes.csv').parent.mkdir(parents=True,exist_ok=True)
changes.to_csv(ROOT/'outputs'/'tables'/'district_changes.csv',index=False)
print(f'Pipeline finished: {len(panel):,} panel rows, {len(changes):,} two-round changes.')
