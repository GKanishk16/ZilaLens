"""Acquire and parse source factsheets. Raw files are never silently replaced."""
from pathlib import Path
from datetime import date
import urllib.request
import pandas as pd

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
        df = pd.read_excel(path)
        # Preserve source headers, normalizing only known name/value columns.
        cols = {str(c).strip().lower(): c for c in df.columns}
        def find(*terms):
            return next((cols[t] for t in terms if t in cols), None)
        dcol, scol = find('district'), find('state','state/ut')
        if not dcol or not scol: raise ValueError(f'Could not identify district/state columns: {df.columns.tolist()}')
        long = df.melt(id_vars=[scol,dcol], var_name='indicator', value_name='value')
        df = long.rename(columns={scol:'state',dcol:'district'})
    df['round'] = name.upper().replace('NFHS','NFHS-')
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df['district'] = df['district'].astype(str).str.strip()
    df['state'] = df['state'].astype(str).str.strip()
    return df[['state','district','round','indicator','value']]

if __name__ == '__main__':
    for n in SOURCES:
        try: print(n, len(read_round(n)))
        except Exception as exc: print(n, exc)
