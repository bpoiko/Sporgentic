from nbainjuries import injury
from nba_api.stats.static import players
from datetime import datetime



def injuryCheck(player_name):
    # Validate the player exists before hitting any report
    player_list = players.find_players_by_full_name(player_name)
    if not player_list:
        raise ValueError(f"Player '{player_name}' not found")

    # Pull the most recent official NBA injury report PDF
    try:
        df = injury.get_reportdata(datetime.now(), return_df=True)
    except Exception as e:
        return {"error": f"Could not fetch injury report: {e}"}

    if df is None or df.empty:
        return {"message": "No injury report available right now. Check back closer to game time."}

    # Filter down to just this player
    match = df[df["Player Name"].str.lower() == player_name.lower()]

    if match.empty:
        return {
            "player": player_name,
            "status": "Available",
            "reason": "Not listed on today's injury report",
        }

    row = match.iloc[0]
    return {
        "player": player_name,
        "status": row["Current Status"],   # Out / Questionable / Available
        "reason": row["Reason"],
        "game": row["Matchup"],
        "game_time": row["Game Time"],
    }
