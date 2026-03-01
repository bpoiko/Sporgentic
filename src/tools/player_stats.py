from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players

def statsLookup(player_name):
    player_list = players.find_players_by_full_name(player_name)
    if not player_list:
        raise ValueError(f"Player {player_name}, not found")
    
    player_id = player_list[0]['id']

    info = playercareerstats.PlayerCareerStats(player_id=player_id)
    return info.get_data_frames()[0]


