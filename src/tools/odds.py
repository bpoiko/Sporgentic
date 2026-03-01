import requests
import os
from dotenv import load_dotenv
from nba_api.stats.static import players
from nba_api.stats.endpoints import commonplayerinfo
load_dotenv()
odds_key = os.getenv("ODDS_KEY")
"""Note to self so I can dev this in the morning
This will work in a way where we cant look up a sole players props
Solution, filter the results so we can have that player and that player only
SO; get props;filter for that respective player; then decide
"""
def oddsFetcher(player_name):
    # use it
    player_list = players.find_players_by_full_name(player_name)
    if not player_list:
        raise ValueError("player not found")
    else:
        p_id = player_list[0]['id']
        needed_info = commonplayerinfo.CommonPlayerInfo(p_id)
        df = needed_info.get_data_frames()[0]
        team_name = df['TEAM_NAME'][0]
        team_id = df['TEAM_ID'][0]
        # has to be an nba player for now..
        REGIONS = 'us'
        markets = 'player_points'
        sport = 'basketball_nba'
    
    player_respective_odds = requests.get(
        f'https://api.the-odds-api.com/v4/sports/{sport}/odds',
        params={
            'api-key' : odds_key,
            'regions' : REGIONS,
            'markets' : markets,
            
        }
    )
    pass