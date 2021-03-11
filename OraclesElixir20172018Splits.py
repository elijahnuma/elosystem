# Pro Data Team Comps Analysis

import os
import pandas as pd

wk_dir = os.getcwd()
years = ['2016', '2017']
splits = ['Spring', 'Summer']
for year in years:
    ProData = pd.read_excel(wk_dir + f'\\{year}-Full-match-data-OraclesElixir.xlsx')     
    df = ProData.loc[ProData.split.str.contains(f'{year}-1[A-Z]*'), :]    
    df.to_excel(f'{year}-Spring-match-data-OraclesElixir.xlsx')
    df = ProData.loc[ProData.split.str.contains(f'{year}-[2|A-Z]+'), :]
    df.to_excel(f'{year}-Summer-match-data-OraclesElixir.xlsx')
