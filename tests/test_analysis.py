import sys
from pathlib import Path
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from analysis import calculate_changes,construct_index

def test_change_calculation_pp():
    p=pd.DataFrame([{'district_id':'x','state':'s','district':'d','round':'NFHS-4','indicator':'Women who are literate (%)','value':60},{'district_id':'x','state':'s','district':'d','round':'NFHS-5','indicator':'Women who are literate (%)','value':70}])
    out=calculate_changes(p)
    assert out.iloc[0].change_pp==10
    assert round(out.iloc[0]["pct_change"],2)==16.67

def test_index_equal_weight_minmax():
    p=pd.DataFrame([
      {'district_id':'a','state':'s','district':'a','round':'NFHS-4','indicator':'A bank account','value':0},
      {'district_id':'a','state':'s','district':'a','round':'NFHS-4','indicator':'B literacy','value':0},
      {'district_id':'b','state':'s','district':'b','round':'NFHS-4','indicator':'A bank account','value':100},
      {'district_id':'b','state':'s','district':'b','round':'NFHS-4','indicator':'B literacy','value':100},])
    out,meta=construct_index(p,['A bank account','B literacy'])
    assert meta['status']=='computed'
    assert out.index_score.tolist()==[0,1]


def test_index_does_not_call_education_only_an_economic_index():
    p=pd.DataFrame([
      {'district_id':'a','state':'s','district':'a','round':'NFHS-4','indicator':'Women who are literate (%)','value':60},
      {'district_id':'a','state':'s','district':'a','round':'NFHS-4','indicator':'Women with 10 or more years of schooling (%)','value':20},
      {'district_id':'b','state':'s','district':'b','round':'NFHS-4','indicator':'Women who are literate (%)','value':80},
      {'district_id':'b','state':'s','district':'b','round':'NFHS-4','indicator':'Women with 10 or more years of schooling (%)','value':40},])
    out,meta=construct_index(p)
    assert out.empty
    assert meta['status']=='unavailable'
