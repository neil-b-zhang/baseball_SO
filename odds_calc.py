# -*- coding: utf-8 -*-
"""
Created on Wed May 29 12:14:56 2019

@author: neilb
"""

import pandas as pd
from datetime import datetime
import sys

COLUMN_LABELS = ['u2.5', 'o2.5', 'u3', 'o3', 'u3.5', 'o3.5', 'u4', 'o4', 
                 'u4.5', 'o4.5', 'u5', 'o5', 'u5.5', 'o5.5', 'u6', 'o6',
                 'u6.5', 'o6.5', 'u7', 'o7', 'u7.5', 'o7.5', 'u8', 'o8',
                 'u8.5', 'o8.5', 'u9', 'o9', 'u9.5', 'o9.5', 'u10', 'o10']

TEAM_LIST = ['TOR', 'SLN', 'TEX', 'COL', 'KCA', 'NYA', 'OAK', 'CHN', 'BOS',
             'BAL', 'HOU', 'MIN', 'SFN', 'PIT', 'ANA', 'ATL', 'CHA', 'SEA',
             'SDN', 'DET', 'WAS', 'ARI', 'PHI', 'LAN', 'TBA', 'CIN', 'NYN', 
             'MIA', 'MIL', 'CLE']

def odds_calc():
    df = pd.read_csv('data/data.csv')
    print(df)
    # save name and team columns in lowercase format
    output_df = pd.DataFrame()
    output_df['name'] = df['Name'].str.lower()
    output_df['team'] = df['Team'].str.lower()
        
    # iterate through each o/u line
    for column in COLUMN_LABELS:
        output_df[column] = 1/(df[column]/100)
    
    # save output based on date run
    now = datetime.now() # current date and time
    output_df.round(2).to_csv('data/calculated_odds_{}.csv'.format(now.strftime("%m%d%Y")), index = False)
    
    return output_df


def kelly_crit_calc(label, deci_odds, implied_odds, tbr, SO, name, team):
    """
    Function for running kelly criterion calculation and creating
    outputs. 
    
       deci_odds = odds from sports book in decimal form
    implied_odds = odds from input data in decimal form
             tbr = total bank roll  
              SO = strikeout line
            name = pitcher's name
            team = pitcher's team
    """
    #TODO: add automatic logging of bets with positive value

    # create variables for kelly crit
    B = deci_odds-1
    P = 1/implied_odds
    Q = 1-P 

    # kelly crit formula
    output = (B*P-Q)/B
        
    # generate outputs
    if output > 0:
        bet_amount = round(output*tbr, 2)
        implied_edge = round((deci_odds-implied_odds)/deci_odds*100, 1)
        to_win = round(bet_amount*deci_odds, 2)
        temp_df = pd.DataFrame({'name': name,
                                'team': team,
                                'edge': implied_edge,
                                'bet': bet_amount,
                                'odds': deci_odds,
                                'to_win': [to_win]})

        print('temp_df')
        print(temp_df)
        return temp_df
    else:
        print('    No value on the {}.'.format(label))
        return pd.DataFrame()

def kelly_crit(odds_df, tbr, pit, SO, o_odds, u_odds):
    """
    Function for setting up the kelly criterion in order to get
    value and betting size based on bank roll
    
    odds_df = dataframe created from pastebin probabilities
        tbr = total bankroll
        pit = pitcher name
         SO = strikeouts line
       io_o = implied odds for over
       io_u = implied odds for under
    """
    
    # get o/u columns for given SO
    ou_cols = [col for col in COLUMN_LABELS if col[1:] == SO]
    o_col = ou_cols[1]
    u_col = ou_cols[0]

    # find odds from calculated dataframe
    io_o = None
    io_u = None
    name = ''
    team = ''
    
    # if team name was given, find name
    if len(pit) == 3:
        io_o = odds_df.loc[odds_df['team'] == pit, o_col].item()
        io_u = odds_df.loc[odds_df['team'] == pit, u_col].item()
        
        # save name and team
        name = odds_df.loc[odds_df['team'] == pit, 'name'].item()
        team = pit
        
    # else find team
    else:
        io_o = odds_df.loc[odds_df['name'] == pit, o_col].item()
        io_u = odds_df.loc[odds_df['name'] == pit, u_col].item()
        
        # save name and team
        name = pit
        team = odds_df.loc[odds_df['name'] == pit, 'team'].item()   
    
    print('\nGetting outputs for: {}'.format(name))
    
    # run kelly crit to find value/bet size
    o_df = kelly_crit_calc('over', o_odds, io_o, tbr, SO, name, team)
    u_df = kelly_crit_calc('under', u_odds, io_u, tbr, SO, name, team)
    
    print('o_df')
    print(o_df)
    print('u_df')
    print(u_df)
    
    # save bets to dataframe
    bets_df = pd.DataFrame()
    if len(o_df)>0:
        print('over')
        bets_df = pd.concat([bets_df, o_df])
    if len(u_df)>0:
        print('under')
        bets_df = pd.concat([bets_df, u_df])
    
    print('bets_df')
    print(bets_df)
    return bets_df
        
def main():
    # get odds in decimal form from probabilities
    calc_odds_df = odds_calc()
    
    value_checking = False
    user_input = input('\nWould you like to check for value? Y/N\n').lower()
    if user_input == "y":
        value_checking = True
    else: 
        sys.exit('done')
    
    total_bankroll = int(input('What is your total bankroll?\n'))
    
    saved_bets = pd.DataFrame()
    while value_checking:    
        # getting user inputs
        #TODO: error catching is probably useful
        
        # get pitcher based on name or team of pitcher
        pitcher = ''
        checking_pitcher = True
        while checking_pitcher:
            pitcher = input('\nWhich pitcher or team?\n').lower()
            if len(pitcher) == 3:
                if pitcher.upper() not in TEAM_LIST:
                    print('    INVALID TEAM ACRONYM. PLEASE CHECK YOUR INPUT')
                else:
                    print('    The pitcher for {} is: {}'.format(pitcher.upper(),
                          calc_odds_df.loc[calc_odds_df['team'] == pitcher,'name'].item()))
                    checking_pitcher = False
            elif pitcher == 'q':
                sys.exit('\nUSER QUIT')
            elif pitcher not in calc_odds_df.name.tolist():
                print('     INVALID PITCHER. PLEASE CHECK YOUR INPUT')
            else:
                checking_pitcher = False
            
        num_SO = input('What is the SO line?\n').lower()
        o_odds = float(input('what are the odds for the over?\n'))
        u_odds = float(input('what are the odds for the under?\n'))
        
        # start kelly crit process 
        #try:
        bets_df = kelly_crit(calc_odds_df, total_bankroll, pitcher, num_SO, 
                             o_odds, u_odds)
        saved_bets = pd.concat([saved_bets, bets_df])
    
        #except ValueError:
        #    print('Value not found, please check your inputs')
            
        user_cont = input('\nWould you like to keep checking? Y/N\n').lower()
        if user_cont == 'n':
            value_checking = False
   
    # save all bets with value to csv
    now = datetime.now() # current date and time
    saved_bets.to_csv('data/saved_bets_{}.csv'.format(now.strftime("%m%d%Y")), index = False)
    
    print('done')
    
if __name__== "__main__":
    main()        
