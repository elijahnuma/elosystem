# Pro Data Team Comps Analysis

import os
import pandas as pd

wk_dir = os.getcwd()

ProData = pd.read_excel(wk_dir + '\\Pro_Team_Comps.xlsx')

na_teams = ['TL', 'TSM', 'OPT', 'FLY', 'CG', 'C9', 'FOX', 'CLG', 'GGS', '100']
eu_teams = ['SK', 'SPY', 'SO4', 'MSF', 'G2', 'XL', 'VIT', 'OG', 'FNC', 'RGE']

ProDataLCS = ProData[ProData['Winner'].isin(na_teams)][ProData['Region'] == 
                     'LCS'].dropna(axis = 1)
ProDataLEC = ProData[ProData['Winner'].isin(eu_teams)][ProData['Region'] == 
                     'LEC'].dropna(axis = 1)
ProDataMSI = ProData[ProData['Region'] == 'MSI'].dropna(axis = 1)

na_wins_list = ProDataLCS['Winner'].astype(str).tolist()
na_losses_list = ProDataLCS['Loser'].astype(str).tolist()
eu_wins_list = ProDataLEC['Winner'].astype(str).tolist()
eu_losses_list = ProDataLEC['Loser'].astype(str).tolist()

with open('na_wins_losses.txt', 'w+') as f:
    wins_losses_list = f.write('')
    for i in range(len(na_wins_list)):
        f.write('{} {} \n'.format(na_wins_list[i], na_losses_list[i]))

with open('eu_wins_losses.txt', 'w+') as f:
    wins_losses_list = f.write('')
    for i in range(len(eu_wins_list)):
        f.write('{} {} \n'.format(eu_wins_list[i], eu_losses_list[i]))
