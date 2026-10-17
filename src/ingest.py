"""Acquire and parse source factsheets. Raw files are never silently replaced."""
from pathlib import Path
from datetime import date
import urllib.request
import pandas as pd
import re

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
SOURCES = {
    'nfhs4': ('https://raw.githubusercontent.com/HindustanTimesLabs/nfhs-data/master/nfhs_district-wise.csv', RAW / 'nfhs_district-wise.csv'),
    'nfhs5': ('https://data.gov.in/files/ogdpv2dms/s3fs-public/datafile/NFHS_5_India_Districts_Factsheet_Data.xls', RAW / 'NFHS_5_India_Districts_Factsheet_Data.xls'),
}

def download(name):
    url, path = SOURCES[name]
    path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={'User-Agent': 'ZilaLens reproducible research'})
    with urllib.request.urlopen(req, timeout=60) as response:
        payload = response.read()
    path.write_bytes(payload)
    return path

def read_round(name):
    path = SOURCES[name][1]
    if not path.exists():
        raise FileNotFoundError(f'{name} source missing: {path}')
    if name == 'nfhs4':
        df = pd.read_csv(path, encoding='latin1')
        needed = {'district','state','indicator_name','total'}
        if not needed.issubset(df.columns): raise ValueError(f'Unexpected NFHS-4 columns: {df.columns.tolist()}')
        df = df.rename(columns={'indicator_name':'indicator','total':'value'})
    else:
        df = pd.read_excel(path, sheet_name=0, engine='xlrd')
        # The official catalog workbook uses "District Names" and "State/UT".
        # Preserve its raw indicator labels for source traceability.
        cols = {str(c).strip().lower(): c for c in df.columns}
        def find(*terms):
            return next((cols[t] for t in terms if t in cols), None)
        dcol, scol = find('district','district names'), find('state','state/ut')
        if not dcol or not scol: raise ValueError(f'Could not identify district/state columns: {df.columns.tolist()}')
        long = df.melt(id_vars=[scol,dcol], var_name='indicator', value_name='value')
        df = long.rename(columns={scol:'state',dcol:'district'})
    df['round'] = name.upper().replace('NFHS','NFHS-')
    df['source_file'] = str(path.relative_to(ROOT))
    df['source_indicator'] = df['indicator'].astype(str).str.strip()
    if name == 'nfhs5':
        aliases = {
            'women (age 15-49) who are literate4 (%)': 'Women who are literate (%)',
            'women (age 15-49)  with 10 or more years of schooling (%)': 'Women with 10 or more years of schooling (%)',
            'women (age 15-49) with 10 or more years of schooling (%)': 'Women with 10 or more years of schooling (%)',
            'women age 20-24 years married before age 18 years (%)': 'Women age 20-24 years married before age 18 years (%)',
            'households using clean fuel for cooking3 (%)': 'Households using clean fuel for cooking (%)',
        }
        df['indicator'] = df['indicator'].map(lambda x: aliases.get(re.sub(r'\s+',' ',str(x).strip()).lower(), str(x).strip()))
    else:
        aliases = {
            'women who are literate (%)': 'Women who are literate (%)',
            'women with 10 or more years of schooling (%)': 'Women with 10 or more years of schooling (%)',
            'women age 20-24 years married before age 18 years (%)': 'Women age 20-24 years married before age 18 years (%)',
            'households using clean fuel for cooking': 'Households using clean fuel for cooking (%)',
        }
        df['indicator'] = df['indicator'].map(lambda x: aliases.get(re.sub(r'\s+',' ',str(x).strip()).lower(), str(x).strip()))
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df['district'] = df['district'].astype(str).str.strip()
    df['state'] = df['state'].astype(str).str.strip()
    return df[['state','district','round','indicator','source_indicator','value','source_file']]

if __name__ == '__main__':
    for n in SOURCES:
        try: print(n, len(read_round(n)))
        except Exception as exc: print(n, exc)
