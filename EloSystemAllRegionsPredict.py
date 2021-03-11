import numpy as np
import pandas as pd

class Team:
    begin_rating = 2700
    def __init__(self, name, rating):
        self.name = name
        self.rating = Team.begin_rating

# updates Elo rating after win/loss
def record_match(winner, loser, show_ratings = False):
    winner = team_dictionary[winner]
    loser = team_dictionary[loser]
    rating_diff = loser.rating - winner.rating
    E_A = 1/(1+(10 ** (rating_diff/400)))   # This is Team 1's expected score
    E_B = 1/(1+(10 ** (-rating_diff/400)))  # This is Team 2's expected score
    winner.rating += k*(1 - E_A)            # 1 is recorded win
    loser.rating += k*(0 - E_B)             # 0 is recorded loss
    if show_ratings == True:
        print('{winner.name}\'s rating is now {winner.rating}, {loser.name}\'s' 
              'rating is now {loser.rating}')
        
# returns ratings at specific observation
def observation_ratings(observation):
    ratings = match_ratings[observation]
    for i in range(len(teams)):
        teams[i].rating = ratings[i]
    return teams

# calls rating of team from team name's string for specific observation      
def rating(name, observation):
    try:
        observation_ratings(observation)
        return team_dictionary[name].rating
    except KeyError:
        return 'Team Not Found'
    
# estimates probablity of win given team 1 and team 2
def estimate_win(team_1, team_2, observation):
    observation_ratings(observation)
    team_1 = team_dictionary[team_1]
    team_2 = team_dictionary[team_2]
    rating_diff = team_2.rating - team_1.rating
    E_A = 1/(1+(10 ** (rating_diff/400)))  
    E_B = 1/(1+(10 ** (-rating_diff/400)))
    return E_A, E_B

# gives ratings from highest to lowest given the observation
def leaderboard(observation):
    ratings = match_ratings[observation]
    rating_list = [(team_names[i], ratings[i]) for i in range(len(ratings))]
    return sorted(rating_list, key = lambda team: team[1], reverse = True)

# Plots chart of team Elos across time
def plot_chart():
    df = pd.DataFrame(np.array(match_ratings), columns = team_names)
    df.columns.name = 'Team'
    df.index.name = 'Match'
    df.plot(kind = 'line', y = team_names, figsize = (12,8), title = 
            f'{region} {split} {year} Elo Ratings')

# Predicts wins based on elo diff
def predictor(elo_diff, start_observation, end_observation):
    range_number = end_observation - start_observation
    correct_predictions = 0
    for i in range(start_observation, end_observation):
        if elo_diff[i] == 0:
            correct_predictions += 0.5
        else: 
            correct_predictions += elo_diff[i] > 0
    return (correct_predictions/range_number) * 100

# loads winners and losers, as well as team names
# pick region to study'
years = ['2016', '2017', '2018', '2019']
splits = ['Spring', 'Summer']
regions = np.loadtxt('unique_region_list.txt', usecols = (0), dtype = str, 
                     unpack = True)       
predict_rate = 0
count = 0                                 
for year in years:
    for split in splits:
        for region in regions:
            try:
                winners, losers = np.loadtxt(f'{region}_{year}_{split}_wins_losses.txt', 
                                             usecols = (0,1), dtype = str, unpack = True, 
                                             delimiter = ' | ')
                
                team_names = np.loadtxt(f'{region}_{year}_{split}_team_names.txt', 
                                        usecols = (0), dtype = str, unpack = True, 
                                        delimiter = ' | ')
                
                last_observation = len(winners)
                
                teams = [Team(team, rating) for team in team_names]
                team_dictionary = {team_names[i] : teams[i] for i in range(len(team_names))}
                
                # match-by-match Elo score, k_type handles 'simple' and 'complex' k-factor 
                match_ratings = [[Team.begin_rating for i in range(len(teams))]]
                k_type = 'simple'
                for i in range(len(winners)):
                    if k_type == 'simple':
                        k = 12
                    elif k_type == 'complex':
                        k = 10
                        if i < 50:
                            k = 20
                        elif i > 90 and i < 140:
                            k = 15
                    record_match(winners[i], losers[i])
                    match_update = [teams[i].rating for i in range(len(team_names))]
                    match_ratings.append(match_update)
                
                elo_diff = [(rating(winners[i], i) - rating(losers[i], i)) for i in range(len(winners))]
                predict_rate += predictor(elo_diff, 0, last_observation)
                count += 1
            except:
                continue
print(predict_rate / count)
print(count)

# =============================================================================
# Notes:
# Adjust Elo System so it knows where the end of each split is
# Over multiple splits would be interesting
# =============================================================================
