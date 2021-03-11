# Pro Data Team Comps Analysis

import os
import pandas as pd

wk_dir = os.getcwd()

ProData = pd.read_excel(wk_dir + '\\2019-summer-match-data-OraclesElixir-2019-09-16.xlsx')
region = 'LCK'
LCKProData = ProData.loc[(ProData['league'] == 'LCK') & (ProData['position'] == 'Team'), ['team', 'position', 'result']]
teams = list(LCKProData['team'].unique())
winners = LCKProData[LCKProData['result'] == True]
losers = LCKProData[LCKProData['result'] == False]
kr_wins_list = winners['team'].astype(str).tolist()
kr_losses_list = losers['team'].astype(str).tolist()
with open('kr_wins_losses.txt', 'w+') as f:
    wins_losses_list = f.write('')
    for i in range(len(kr_wins_list)):
        f.write('{} | {}\n'.format(kr_wins_list[i], kr_losses_list[i]))
        
