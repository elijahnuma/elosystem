# Pro Data Team Comps Analysis

import os
import pandas as pd

cwd = os.getcwd()
years = ['2016', '2017', '2018', '2019']
splits = ['Spring', 'Summer']
region_list = []
for year in years:
    for split in splits:
        try:
            ProData = pd.read_excel(cwd + f'\\OraclesElixirData\\{year}-{split}-match-data-OraclesElixir.xlsx')
            regions = ProData['league'].unique().astype(str).tolist()
            for region in regions:
                ProDataSubset = ProData.loc[(ProData['league'] == 
                                             f'{region}') & (ProData['position'] 
                                             == 'Team'), ['team', 'position', 'result']]
                team_names = list(ProDataSubset['team'].unique())
                winners = ProDataSubset[ProDataSubset['result'] == True]
                losers = ProDataSubset[ProDataSubset['result'] == False]
                wins_list = winners['team'].astype(str).tolist()
                losses_list = losers['team'].astype(str).tolist()
                
                with open(cwd + f'\\wins_losses\\{region}_{year}_{split}_wins_losses.txt', 'w+') as f:
                    for i in range(len(wins_list)):
                        f.write(f'{wins_list[i]} | {losses_list[i]}\n')
                        
                with open(cwd + f'\\wins_losses\\{region}_{year}_{split}_team_names.txt', 'w+') as f:
                    for i in range(len(team_names)):
                        f.write(f'{team_names[i]} | _\n')
                
                region_list.append(region)
                
        except:
            continue
        
region_list_set = list(set(region_list))
with open(cwd + '\\wins_losses\\unique_region_list.txt', 'w+') as f:
    f.write('')
    for i in range(len(region_list_set)):
        f.write(f'{region_list_set[i]}\n')
