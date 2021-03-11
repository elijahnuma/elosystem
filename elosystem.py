import os 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

cwd = os.getcwd()
    
def rating(name, observation):
    """
    gives team rating at specific observation; not found error if team isn't in dataset
    
    args:
        name (str): name of team
        observation (int): observation of match
        
    returns int
    """
    try:
        return team_ratings.loc[observation, name]
    except KeyError:
        return f'Error: Team "{name}" Not Found'

def record_match(winner, loser, observation):
    """
    updates team Elo rating after played match
    
    args:
        winner (str): winner of game
        loser (str): loser of game
        observation (int): observation of match
        
    """
    rating_diff = rating(loser, observation) - rating(winner, observation)
    E_1 = 1/(1+(10 ** (rating_diff/400)))   # this is winner's expected score
    E_2 = 1 - E_1                           # this is loser's expected score
    # updates next observation with previous observations Elo ratings
    team_ratings.loc[observation + 1, :] = team_ratings.loc[observation, :]
    team_ratings.loc[observation + 1, winner] += k*(1 - E_1)
    team_ratings.loc[observation + 1, loser] += k*(0 - E_2)
    
def estimate_win(team_1, team_2, observation):
    """
    estimates probablity of win given team 1 and team 2
    
    args:
        team_1 (str): team 1's name
        team_2 (str): team 2's name
        observation (int): observation of match
        
    returns tuple
    """
    rating_diff = rating(team_2, observation) - rating(team_1, observation)
    E_1 = 1/(1+(10 ** (rating_diff/400)))  
    E_2 = 1 - E_1
    return [E_1, E_2]

def leaderboard(observation):
    # might want to display real w-l alongside this
    """
    sorted team ratings from highest
    
    args:
        observation (int): observation of match
            
    returns list of tuples
    """
    ratings = team_ratings.loc[observation, :].tolist()
    rating_list = [(teams[i], ratings[i]) for i in range(len(ratings)) if not np.isnan(ratings[i])]
    return sorted(rating_list, key=lambda team: team[1], reverse=True)
         
def plot_chart(show_elo=True, show_bucket=False, team_list=None):
    """
    plots chart of team Elo ratings across time and expected win rate 
    distribution; default is to track all teams, can track multiple teams.
    
    args:
        show_elo (bool): plots Elo ratings across match
        show_bucket (bool): plots frequency of win rates       
        team_list (list of str): tracks multiple teams       
    """
    # checks if more than 60% the split has the same value. If so, 
    # sets all values equal to None between the split observations so it does
    # not plot
    for team in teams: 
        for i, j in zip(split_observations, split_observations[1:]):
            if team_ratings.loc[i[0]:j[0], team].value_counts().max() > 0.6*(j[0] - i[0]):
                team_ratings.loc[i[0]:j[0], team] = None
    team_ratings.columns.name = 'Team'
    team_ratings.index.name = 'Match'
    # checks if begin split and end split are the same, otherwise would print,
    # for example, "LCK Summer 2019 - Summer 2019"
    if f'{start_quarter} {start_year}' == f'{end_quarter} {end_year}':
        plot_title=f'{region} {start_quarter} {start_year}'
    else:
        plot_title=f'{region} {start_quarter} {start_year} - {end_quarter} {end_year}'
    plot_length = 12
    plot_height = 8
    if show_elo:
        # tries to plot seperate teams
        try:
            team_string = ', '.join(team_list)
            team_ratings[teams].plot(kind='line', y=team_list, figsize=(plot_length, plot_height), title=f'{plot_title} Elo Ratings ({team_string})')
        # if team_list=None, it plots every team
        except:
            team_ratings.plot(kind='line', y=teams, figsize=(plot_length, plot_height), title=f'{plot_title} Elo ratings')
        # adds vertical lines to seperate splits
        for split_observation in split_observations:
            plt.axvline(x=split_observation[0], color='k', linestyle='--')
        plt.show()
        plt.close()
    if show_bucket:
        plt.title(f'{plot_title} Win Rates')
        sns.distplot(expected_bucket['Team 1 Expected Win'], axlabel='Win rates')

# picks region to study, loads winners and losers for quarters
# to make sure code is working, the complex prediction for LCS Summer 2019 at 
# k = 20 for all observations is 0.5568181818181818
start_quarter = 'Spring'
start_year = '2016'
end_quarter = 'Summer'
end_year = '2019'
years = ['2016', '2017', '2018', '2019']
quarters = ['Spring', 'Summer']
# All regions 
regions = np.loadtxt(cwd + '\\wins_losses\\unique_region_list.txt', usecols=(0,), dtype=str, unpack=True).tolist()
# Empty dataframes to concatenate existing dataframes
team_ratings_csv = expected_bucket_csv = pd.DataFrame()
for region in ['LCS']:
    print(region, '- Compiling')
    winners, losers, teams = [], [], []
    split_observations = [(0, start_quarter, start_year)]
    for year in years[years.index(start_year):years.index(end_year) + 1]:
        for quarter in quarters:
            # Checks if starting on summer, so if calling for a certain year
            # the code starts on summer and not spring
            if (start_quarter == 'Summer') and (year == start_year) and (quarter == 'Spring'):
                continue
            # Checks if ending on spring, so if calling for a certain year
            # the code ends on spring and not summer
            if (end_quarter == 'Spring') and (year == end_year) and (quarter == 'Summer'):
                continue
            try:
                winners += list(cwd + np.loadtxt(f'\\wins_losses\\{region}_{year}_{quarter}_wins_losses.txt', usecols=(0,1), dtype=str, unpack=True, delimiter=' | ')[0])
                losers += list(cwd + np.loadtxt(f'\\wins_losses\\{region}_{year}_{quarter}_wins_losses.txt', usecols=(0,1), dtype=str, unpack=True, delimiter=' | ')[1])
                teams += list(cwd + np.loadtxt(f'\\wins_losses\\{region}_{year}_{quarter}_team_names.txt', usecols=(0), dtype=str, unpack=True, delimiter=' | '))
                split_observations.append((len(winners)+1, quarter, year))
            except:
                continue
    teams = list(set(teams))
    last_observation = len(winners)
    start_rating = 2700 
    # match-by-match Elo score, each team starts with the same beginning rating
    team_ratings = pd.DataFrame([[start_rating for i in range(len(teams))] for j in range(len(winners)+1)], columns=teams)
    expected_bucket = pd.DataFrame([[0 for i in range(4)] + [region] for j in range(len(winners))], columns=['Team 1 Expected Win', 'Team 2 Expected Win', 'Team 1', 'Team 2', 'Region'])
    for ob in range(len(winners)):
        # soft resets k-factor after every split to account for swapping
        # rosters, meta changes, etc
        soft_reset_ranges = [j[0] + i for j in split_observations for i in range(50)]
        k = 20
        if ob < 50:
            k = 40
        elif ob in soft_reset_ranges:
            k = 35
        win_los_ob = [str(winners[ob]), str(losers[ob]), ob]
        record_match(*win_los_ob)
        expected_bucket.loc[ob, :] = estimate_win(*win_los_ob) + win_los_ob[:2] + [region]
    
    def predictor(start_observation=0, end_observation=last_observation):
        """
        predicts win based from Elo rating difference
        
        args:
            start_observation (int): start observation
            end_observation (int): end observation
            
        returns float
        """
        elo_diff = [(rating(winners[i], i) - rating(losers[i], i)) for i in range(start_observation, end_observation)]
        correct_predictions = 0
        for i in range(len(elo_diff)):
            if elo_diff[i] == 0:
                correct_predictions += 0.5
            else: 
                correct_predictions += elo_diff[i] > 0
        return correct_predictions/(end_observation - start_observation)
    
    def split_array(access):
        """
        gives readable information from split_observations to dataframe to give information about region, year, 
        and qurater for specific observations
        
        args:
            access (str): Information from split_observations trying to access
                
        returns list of lists
        """
        if access == 'Year':
            k = 1
        if access == 'Quarter':
            k = 2
        return [split_observations[i+1][k] for i in range(len(split_observations)-1) for j in range(split_observations[i][0], split_observations[i+1][0])]
    
    plot_chart(show_elo=True, show_bucket=False)
    print('Prediction Rate:', predictor())
    team_ratings = team_ratings.assign(Region=[region for i in range(team_ratings.shape[0])], Quarter=split_array(access='Year'), Year=split_array(access='Quarter'), Observation=team_ratings.index).melt(id_vars=['Observation', 'Region', 'Quarter', 'Year'], var_name='Team_name', value_name='Elo').sort_values(by='Observation').reset_index(drop=True)
    team_ratings_csv = pd.concat([team_ratings_csv, team_ratings]).reset_index(drop=True)
    expected_bucket_csv = pd.concat([expected_bucket_csv, expected_bucket]).reset_index(drop=True)
team_ratings_csv.to_csv(cwd + '\\csvs\\team_ratings.csv', index=False)
expected_bucket_csv.to_csv(cwd + '\\csvs\\expected_win_rates.csv', index=False)
