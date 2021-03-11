# Pro Data Team Comps Analysis
# A more optimazed, cleaner version of ProTeamComps0.py

#%%  Import Data

import os
import pandas as pd
import statsmodels.api as sm
from scipy import stats
import numpy as np

wk_dir = os.getcwd()
ProData = pd.read_excel(wk_dir + '\\Pro_Team_Comps.xlsx')
ProDataWinLoss = ProData[['Win Team Comp','Lose Team Comp']]
ProDataWinLoss.columns = ['Win_Team_Comp','Lose_Team_Comp']


InverseReplacementDict = {'CatchAttack':'AttackCatch','ProtectAttack':'AttackProtect',
                          'SiegeAttack':'AttackSiege','SplitAttack':'AttackSplit',
                          'ProtectCatch':'CatchProtect','SiegeCatch':'CatchSiege',
                          'SplitCatch':'CatchSplit','SiegeProtect':'ProtectSiege',
                          'SplitProtect':'ProtectSplit','SplitSiege':'SiegeSplit'}

#InverseConditions: A list of team comps in Combined_Comp that are inverse
InverseConditionList = list(InverseReplacementDict.keys())

#gets dummy variables for independent team comps
def IndividualDummies(DataFrame):
    Dummies = pd.get_dummies(DataFrame)
    return(Dummies)
     
#gets dummy variables for team comp combonations
def PairedDummies(DataFrame,wincolumn,losecolumn,InverseCondition,InverseReplacement):
    DataFrame['Combined_Comp'] = DataFrame[wincolumn] + DataFrame[losecolumn]
    DataFrame = AddWinColumn(DataFrame)
    DataFrame = FlipInverseMatches(DataFrame,InverseCondition,InverseReplacement)
    Dummies = pd.get_dummies(DataFrame['Combined_Comp'])
    return(Dummies)
    
#gathers both individual and paired dummies and returns    
def GatherDummies(DataFrame,InverseCondition,InverseReplacement):
    ColumnName1 = 'Win_Team_Comp'
    ColumnName2 = 'Lose_Team_Comp'
    DataFrame = DataFrame.join((IndividualDummies(DataFrame)),how='inner')
    DataFrame = DataFrame.join((PairedDummies(DataFrame,ColumnName1, ColumnName2,InverseCondition,
                                              InverseReplacement)), how = 'inner')
    return(DataFrame)

def AddWinColumn(DataFrame):
    DataFrame['Win'] = 1    
    return(DataFrame)
    
#flips inverse matches    
def FlipInverseMatches(DataFrame,InverseCondition,InverseReplacement):
    DataFrame = AddWinColumn(DataFrame)
    DataFrame['IsInverse'] = DataFrame['Combined_Comp'].isin(InverseCondition)
    DataFrame['UpdatedWin'] = np.logical_and(DataFrame['Win'], np.logical_not(DataFrame['IsInverse']))
    
    DataFrame = RenameInverseMatches(DataFrame,InverseReplacement)
    
    return(DataFrame)

#renames inverse matches after the appropriate flipping has been done
def RenameInverseMatches(DataFrame,InverseReplacement):
    DataFrame['Combined_Comp'] = DataFrame[['Combined_Comp']].replace(InverseReplacement)
    return(DataFrame)
    
def AllFunctions(ProDataFrame,InverseCondition,InverseReplacement):
    DataFrame = GatherDummies(ProDataFrame,InverseCondition,InverseReplacement)
    return(DataFrame)
        

ProDataAllDummies = AllFunctions(ProDataWinLoss,InverseConditionList,InverseReplacementDict)    


#%% MERGE BACK ON LEC/LCS
#Seperate into Na and Eu

def SplitRegion(DummiesDataFrame,AllProDataDF):

    
    na_teams = ['TL', 'TSM', 'OPT', 'FLY', 'CG', 'C9', 'FOX', 'CLG', 'GGS', '100']
    eu_teams = ['SK', 'SPY', 'SO4', 'MSF', 'G2', 'XL', 'VIT', 'OG', 'FNC', 'RGE']
    
    NaDataFrame = ProData[ProData['Winner'].isin(na_teams)][ProData['Region'] == 
                         'LCS'].dropna(axis = 1)
    EuDataFrame = ProData[ProData['Winner'].isin(eu_teams)][ProData['Region'] == 
                         'LEC'].dropna(axis = 1)
    MSIDataFrame= ProData[ProData['Region'] == 'MSI'].dropna(axis = 1)
    
    
    Naindex = NaDataFrame.index
    Euindex = EuDataFrame.index
    
    NaDummyDataFrame = ProDataAllDummies.iloc[Naindex,:]
    EuDummyDataFrame = ProDataAllDummies.iloc[Euindex,:]
    return(NaDummyDataFrame,EuDummyDataFrame,MSIDataFrame)

[NaDF, EuDF, _ ] = SplitRegion(ProDataAllDummies,ProData)


#%% ADD IN ELO

#load in Elo

NaElo_Diff = pd.read_csv(wk_dir + '\\NaElo_Data.csv')
NaElo_Diff.columns = ['Elo_Diff']
EuElo_Diff = pd.read_csv(wk_dir + '\\EuElo_Data.csv')
EuElo_Diff.columns = ['Elo_Diff']

#merge to NaDF and EuDF
NaDF = NaDF.reset_index().join(NaElo_Diff).drop('index',axis=1)
EuDF = EuDF.reset_index().join(EuElo_Diff).drop('index',axis=1)

#Drop Unneccessary columns
NaDF.drop(['Win_Team_Comp','Lose_Team_Comp','Combined_Comp','Win','IsInverse'],axis=1,inplace=True)
EuDF.drop(['Win_Team_Comp','Lose_Team_Comp','Combined_Comp','Win','IsInverse'],axis=1,inplace=True)

#Convert UpdatedWin to 0/1
NaDF['UpdatedWin'] = NaDF['UpdatedWin'].astype('int')
EuDF['UpdatedWin'] = EuDF['UpdatedWin'].astype('int')

#%% Logistic Regession
def logregression(DataFrame):
    
    stats.chisqprob = lambda chisq, df: stats.chi2.sf(chisq, df)

    logit = sm.Logit(DataFrame['UpdatedWin'],DataFrame.loc[:,DataFrame.columns != 'UpdatedWin'].astype(float))
    
    result = logit.fit(method='bfgs',maxiter = 100)
    
    coeffs = result.params.values
    
    DataFrame['Prediction'] = np.round(result.predict())
    accuracy = sum(DataFrame['Prediction'] == DataFrame['UpdatedWin'])/len(DataFrame)
    
    return(accuracy,DataFrame,coeffs)
    
    
#[NaAccuracy,NaDF,nacoefs] = logregression(NaDF)
#[EuAccuracy,EuDF,eucoefs] = logregression(EuDF)    


#%% Tree

# Model (can also use single decision tree)
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier(n_estimators=10)


# Train
model.fit(NaDF.loc[:,NaDF.columns != 'UpdatedWin'], NaDF['UpdatedWin'])
# Extract single tree
estimator = model.estimators_[5]

from sklearn.tree import export_graphviz
# Export as dot file
export_graphviz(estimator, out_file='tree.dot', 
                feature_names = NaDF.columns[NaDF.columns != 'UpdatedWin'],
                class_names = 'Prediction',
                rounded = True, proportion = False, 
                precision = 2, filled = True)

# Convert to png using system command (requires Graphviz)
from subprocess import call
call(['dot', '-Tpng', 'tree.dot', '-o', 'tree.png', '-Gdpi=600'])

# Display in jupyter notebook
from IPython.display import Image
Image(filename = 'tree.png')