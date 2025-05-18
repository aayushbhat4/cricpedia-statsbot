
import pandas as pd
import numpy as np
def convert_dt(date_str):
    """Return pd.Timestamp or None."""
    if date_str is None:
        return None
    try:
        return pd.to_datetime(date_str, dayfirst=False, errors="raise")
    except Exception as e:
        raise ValueError(f"Unrecognised date '{date_str}': {e}")
def get_batter_stats_for_match(data,batter):
    # add & (data.innings.isin([1,2])) when you create the filter
    runs = data.loc[data.striker==batter,'runs_off_bat'].sum()
    balls =data.loc[(data.striker==batter) & (data.wides.isna()),'runs_off_bat'].shape[0]
    sr= (runs/balls*100).round(2) if balls>0 else 0.00
    fours= data.loc[(data.striker==batter) & (data.runs_off_bat==4),'runs_off_bat'].shape[0]
    sixes= data.loc[(data.striker==batter) & (data.runs_off_bat==6),'runs_off_bat'].shape[0]
    
    
    dismissal = data.loc[data.player_dismissed == batter,'wicket_type'] if data.player_dismissed.isin([batter]).any() else 'Not Out'
    batter_scorecard = pd.DataFrame([[data.match_id[0],batter,runs,balls,sr,fours,sixes, dismissal,data.venue[0]]],columns=['Match_id','Player','Runs','Balls_Faced','Strike_Rate','Fours','Sixes','Dismissal_Type','Venue'])
    return batter_scorecard


def get_bowler_stats_for_match(data,bowler):
    # add & (data.innings.isin([1,2])) when you create the filter
    data_b=data.copy()
    data_b[['wides', 'noballs', 'byes', 'legbyes', 'penalty']] = (
    data_b[['wides', 'noballs', 'byes', 'legbyes', 'penalty']].fillna(0)
)
    
    data_b['runs_given'] =data_b.runs_off_bat+data_b.wides+data_b.noballs
    
    runs_given=data_b.loc[data_b.bowler == bowler, ['runs_given']].sum().iloc[0]
    
    wickets = data_b[data_b.bowler ==bowler].loc[(data_b.wicket_type.notna()) & (data_b.wicket_type!='run out')].shape[0]
    balls= data_b[data_b.bowler ==bowler].loc[(data_b.wides==0) & (data_b.noballs==0)].shape[0]
    bowler_scorecard = pd.DataFrame([[data.match_id[0],bowler,runs_given,wickets,balls,data.venue[0]]],columns=['Match_id','Player','Runs','Wickets','Balls_Bowled','Venue'])
    return bowler_scorecard

def get_match_up_stats(data,batter,bowler,start_time,end_time):
    
    filtered = data.loc[(data.striker==batter) & (data.bowler==bowler) & (data.innings.isin([1,2]))].copy()
    start_time = convert_dt(start_time)
    end_time = convert_dt(end_time)

    if start_time is not None:
        filtered = filtered[filtered["start_date"] >= start_time]

    if end_time is not None:
        filtered = filtered[filtered["start_date"] <= end_time]
    filtered[['wides', 'noballs', 'byes', 'legbyes', 'penalty']] = (
    filtered[['wides', 'noballs', 'byes', 'legbyes', 'penalty']].fillna(0)
)
    runs = filtered.runs_off_bat.sum()
    balls=filtered.loc[(filtered.wides==0) & (filtered.noballs==0)].shape[0]
    wickets=filtered.loc[(filtered.wicket_type.notna()) & (filtered.wicket_type!='run out')].shape[0]
    sr= (runs/balls*100).round(2)
    innings =  filtered.match_id.nunique()
    average = (runs/wickets).round(2) if wickets >0 else 'inf'
    match_up = pd.DataFrame([[innings,batter, bowler,runs,balls,wickets,sr,average,start_time,end_time]],columns=['Innings','Batter','Bowler','Runs_scored','Balls_faced','Wickets','Strike Rate','Average'])
    return match_up

def aggregate_batter_stats(data,batter,start_time,end_time):
    filtered = data.loc[(data.striker==batter) & (data.innings.isin([1,2]))].copy()

    start_time = convert_dt(start_time)
    end_time = convert_dt(end_time)

    if start_time is not None:
        filtered = filtered[filtered["start_date"] >= start_time]

    if end_time is not None:
        filtered = filtered[filtered["start_date"] <= end_time]

    runs = filtered['runs_off_bat'].sum()
    balls =filtered.loc[data.wides.isna(),'runs_off_bat'].shape[0]
    sr= (runs/balls*100).round(2) if balls>0 else 0.00
    fours= filtered.loc[filtered.runs_off_bat==4,'runs_off_bat'].shape[0]
    sixes= filtered.loc[data.runs_off_bat==6,'runs_off_bat'].shape[0]
    innings= filtered.match_id.nunique()
    
    outs= filtered.loc[filtered.player_dismissed==batter].shape[0]
    average = (runs/outs).round(2) if outs>0 else 'inf'
    

    batter_scorecard = pd.DataFrame([[batter,innings,runs,balls,average,sr,fours,sixes]],columns=['Player','Innings','Runs','Balls_Faced','Average','Strike_Rate','Fours','Sixes'])
    return batter_scorecard
    

def aggregate_bowling_stats(data,bowler,start_time,end_time):


    filtered = data.loc[(data.striker==bowler)& (data.innings.isin([1,2]))].copy()

    start_time = convert_dt(start_time)
    end_time = convert_dt(end_time)

    if start_time is not None:
        filtered = filtered[filtered["start_date"] >= start_time]

    if end_time is not None:
        filtered = filtered[filtered["start_date"] <= end_time]
        
    filtered[['wides', 'noballs', 'byes', 'legbyes', 'penalty']] = filtered[['wides', 'noballs', 'byes', 'legbyes', 'penalty']].fillna(0)
    
    filtered['runs_given'] =filtered.runs_off_bat+filtered.wides+filtered.noballs
    runs_given=filtered.loc[:,'runs_given'].sum()
    innings=filtered.match_id.nunique()
    
    
    wickets = filtered.loc[(filtered.wicket_type.notna()) & (filtered.wicket_type!='run out')].shape[0]
    average = (runs_given/wickets).round(2)
    balls= filtered.loc[(filtered.wides==0) & (filtered.noballs==0)].shape[0]
    sr = np.round((balls/wickets), 2)
    bowler_scorecard = pd.DataFrame([[bowler,innings,runs_given,wickets,balls,average,sr]],columns=['Player','Innings','Runs','Wickets','Balls_Bowled','Average','Strike_Rate'])
    return bowler_scorecard

    
    