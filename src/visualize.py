"""Create map previews and Power BI/Excel handoff assets."""
from pathlib import Path
import json,re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colors
ROOT=Path(__file__).resolve().parents[1]

def norm(s): return ' '.join(re.sub(r'[^a-z0-9 ]',' ',str(s).lower()).split())
def _polygons(geom):
    if not geom: return []
    if geom['type']=='Polygon': return geom['coordinates']
    if geom['type']=='MultiPolygon': return [p for p in geom['coordinates']]
    return []

def make_map(panel, indicator, title, path, state=None):
    geo=json.loads((ROOT/'data'/'raw'/'india_districts.geojson').read_text())
    data=panel[(panel['round']=='NFHS-4')&(panel['indicator']==indicator)].copy()
    if state: data=data[data.state.map(norm)==norm(state)]
    vals={(norm(r.district),norm(r.state)):r.value for r in data.itertuples() if pd.notna(r.value)}
    fig,ax=plt.subplots(figsize=(7,8)); cmap=plt.get_cmap('YlGnBu'); normc=colors.Normalize(vmin=min(vals.values()) if vals else 0,vmax=max(vals.values()) if vals else 1)
    joined=0
    for feat in geo['features']:
        prop=feat['properties']; district=prop.get('district',''); st=prop.get('st_nm','')
        value=vals.get((norm(district),norm(st)))
        if value is not None: joined+=1
        fc=cmap(normc(value)) if value is not None else '#eeeeea'
        for poly in _polygons(feat['geometry']):
            ring=poly[0]
            ax.fill([p[0] for p in ring],[p[1] for p in ring],facecolor=fc,edgecolor='white',linewidth=.15)
    if state:
        ax.set_xlim(77,85); ax.set_ylim(23,31)
    else: ax.set_xlim(67,98); ax.set_ylim(6,38)
    ax.set_axis_off(); ax.set_title(title,loc='left',fontsize=13,weight='bold',pad=12)
    sm=plt.cm.ScalarMappable(cmap=cmap,norm=normc); fig.colorbar(sm,ax=ax,shrink=.6,label='Percent (%)')
    fig.text(.02,.018,f'n matched districts: {joined} | Source: NFHS-4 (2015-16), HindustanTimesLabs/nfhs-data; boundaries: HindustanTimesLabs/shapefiles, India district GeoJSON.',fontsize=7,wrap=True)
    fig.savefig(path,dpi=200,bbox_inches='tight'); plt.close(fig)
    return joined

def build_powerbi(panel):
    out=ROOT/'outputs'/'powerbi'; out.mkdir(parents=True,exist_ok=True)
    panel[['district_id','state','district','aspirational_flag']].drop_duplicates().to_csv(out/'dim_district.csv',index=False)
    pd.DataFrame({'round_key':[4,5],'round':['NFHS-4','NFHS-5'],'period':['2015-16','2019-21']}).to_csv(out/'dim_round.csv',index=False)
    fact=panel[['district_id','state','district','round','indicator','value','aspirational_flag']].copy()
    indicator_keys=panel[['indicator']].drop_duplicates().reset_index(drop=True)
    indicator_keys['indicator_key']=indicator_keys.index+1
    indicator_keys.to_csv(out/'dim_indicator.csv',index=False)
    fact=fact.merge(indicator_keys,on='indicator',how='left')
    fact.to_csv(out/'fact_indicator_values.csv',index=False)
    pd.DataFrame(columns=['district_id','cluster_id','cluster_name']).to_csv(out/'dim_cluster.csv',index=False)
    dax=['PP Change = [NFHS-5 Value] - [NFHS-4 Value]','NFHS-4 Value = CALCULATE(AVERAGE(fact_indicator_values[value]), dim_round[round] = "NFHS-4")','NFHS-5 Value = CALCULATE(AVERAGE(fact_indicator_values[value]), dim_round[round] = "NFHS-5")','District Count = DISTINCTCOUNT(dim_district[district_id])','Districts Improved = CALCULATE(DISTINCTCOUNT(dim_district[district_id]), FILTER(VALUES(dim_district[district_id]), [PP Change] > 0))','Districts Improved % = DIVIDE([Districts Improved], [District Count])','Index Score = AVERAGE(fact_indicator_values[index_score])','Aspirational Mean Change = CALCULATE([PP Change], dim_district[aspirational_flag] = TRUE())','Non-Aspirational Mean Change = CALCULATE([PP Change], dim_district[aspirational_flag] = FALSE())','Aspirational Gap = [Aspirational Mean Change] - [Non-Aspirational Mean Change]']
    (out/'powerbi_build_guide.md').write_text('# Power BI build guide\n\n## Relationships\n\n- `dim_district[district_id]` 1:* `fact_indicator_values[district_id]`\n- `dim_indicator[indicator_key]` 1:* fact (map indicator labels to keys during model load)\n- `dim_round[round]` 1:* fact\n- `dim_cluster[district_id]` 1:* district when cluster results become available\n\n## Measures\n\n'+''.join(f'{i+1}. `{m}`\n\n' for i,m in enumerate(dax))+'## Pages\n\n1. National Overview: map, indicator selector, round values, distribution and improved share.\n2. Aspirational Districts Comparison: descriptive changes and matched baseline subgroup; label as non-causal.\n3. Uttar Pradesh Deep Dive: district ranks, Ghaziabad/Gautam Buddha Nagar callouts, state/national reference lines.\n\nNFHS-5-dependent measures are blank until the official workbook is added. `Index Score` depends on an index column not yet available in the source fact CSV.\n')

def build_workbook(panel):
    from openpyxl import Workbook
    from openpyxl.styles import Font,PatternFill
    from openpyxl.chart import BarChart,Reference
    from openpyxl.formatting.rule import ColorScaleRule
    out=ROOT/'outputs'/'tables'/'ZilaLens_Analysis_Workbook.xlsx'
    with pd.ExcelWriter(out,engine='openpyxl') as writer:
        panel.to_excel(writer,sheet_name='Data',index=False)
        summary=panel[panel['round']=='NFHS-4'].groupby(['state','indicator'],as_index=False).value.mean()
        summary.to_excel(writer,sheet_name='NFHS4 Summary',index=False)
        changes=pd.read_csv(ROOT/'outputs'/'tables'/'district_changes.csv')
        changes.to_excel(writer,sheet_name='Change Summary',index=False)
    from openpyxl import load_workbook
    wb=load_workbook(out); ws=wb['NFHS4 Summary']; ws.freeze_panes='A2'; ws.auto_filter.ref=ws.dimensions
    for c in ws[1]: c.font=Font(bold=True,color='FFFFFF'); c.fill=PatternFill('solid',fgColor='17365D')
    if ws.max_row>1: ws.conditional_formatting.add(f'C2:C{ws.max_row}',ColorScaleRule(start_type='min',start_color='F8696B',mid_type='percentile',mid_value=50,mid_color='FFEB84',end_type='max',end_color='63BE7B'))
    # Chart first indicator's state means as a native Excel chart.
    inds=list(dict.fromkeys(ws.cell(r,2).value for r in range(2,ws.max_row+1)))
    if inds:
        chosen=inds[0]; rows=[r for r in range(2,ws.max_row+1) if ws.cell(r,2).value==chosen]
        if rows:
            chart=BarChart(); chart.title=f'NFHS-4 state values: {chosen}'; chart.y_axis.title='Percent'; chart.x_axis.title='State'; chart.add_data(Reference(ws,min_col=3,min_row=1,max_row=ws.max_row),titles_from_data=True); chart.set_categories(Reference(ws,min_col=1,min_row=2,max_row=ws.max_row)); chart.height=8; chart.width=16; ws.add_chart(chart,'F2')
    wb.save(out)

if __name__=='__main__':
    p=pd.read_csv(ROOT/'data'/'processed'/'tidy_panel.csv'); build_powerbi(p); build_workbook(p)
    for ind,slug in [('Women who are literate (%)','women_literate'),('Households using improved sanitation facility','improved_sanitation')]:
        if ind in set(p.indicator): make_map(p,ind,'NFHS-4 baseline: '+ind,ROOT/'outputs'/'maps'/f'{slug}_nfhs4.png')
