from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players
from langchain.tools import tool
@tool
def statsLookup(player_name: str) -> str:
    """"Check the last 3 seasons worth of stats of an NBA player by their full name"""
    player_list = players.find_players_by_full_name(player_name)
    if not player_list:
        raise ValueError(f"Player {player_name}, not found")
    
    player_id = player_list[0]['id']

    info = playercareerstats.PlayerCareerStats(player_id=player_id)
    df = info.get_data_frames()[0]
    return str(df.sort_values("SEASON_ID").tail(3)) # 3 most recent seasons

