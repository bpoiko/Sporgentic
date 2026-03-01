import requests
import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from nba_api.stats.static import players
from nba_api.stats.endpoints import commonplayerinfo
from langchain.tools import tool
load_dotenv()
odds_key = os.getenv("ODDS_KEY")

BASE_URL = "https://api.the-odds-api.com/v4"
SPORT = "basketball_nba"
REGIONS = "us"
MARKETS = "player_points"

@tool
def oddsFetcher(player_name: str) -> str:
    """Fetch today's betting odds, and player props for an NBA player by their full name
    ."""
    # Step 1: Resolve player name → team via nba_api
    player_list = players.find_players_by_full_name(player_name)
    if not player_list:
        raise ValueError(f"Player '{player_name}' not found")

    player_id = player_list[0]["id"]
    df = commonplayerinfo.CommonPlayerInfo(player_id).get_data_frames()[0]
    full_team_name = f"{df['TEAM_CITY'][0]} {df['TEAM_NAME'][0]}"  # e.g. "Los Angeles Lakers"

    # Step 2: Guard rail — check if the team is playing today before spending API calls
    now = datetime.now(timezone.utc)
    today_start = now.strftime("%Y-%m-%dT00:00:00Z")
    today_end = (now + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z")

    events_resp = requests.get(
        f"{BASE_URL}/sports/{SPORT}/events",
        params={
            "apiKey": odds_key,
            "commenceTimeFrom": today_start,
            "commenceTimeTo": today_end,
        },
    )
    events_resp.raise_for_status()
    events = events_resp.json()

    target_event = None
    for event in events:
        if full_team_name in (event["home_team"], event["away_team"]):
            target_event = event
            break

    if not target_event:
        return {"message": f"{full_team_name} is not playing today. Skipping odds call."}

    # Step 3: Pull player props for that specific game only
    event_id = target_event["id"]
    opponent = (
        target_event["away_team"]
        if full_team_name == target_event["home_team"]
        else target_event["home_team"]
    )

    odds_resp = requests.get(
        f"{BASE_URL}/sports/{SPORT}/events/{event_id}/odds",
        params={
            "apiKey": odds_key,
            "regions": REGIONS,
            "markets": MARKETS,
            "oddsFormat": "american",
        },
    )
    odds_resp.raise_for_status()
    odds_data = odds_resp.json()

    # Step 4: Filter outcomes to just this player via the description field
    player_odds = []
    for bookmaker in odds_data.get("bookmakers", []):
        for market in bookmaker.get("markets", []):
            for outcome in market.get("outcomes", []):
                if outcome.get("description", "").lower() == player_name.lower():
                    player_odds.append({
                        "bookmaker": bookmaker["title"],
                        "market": market["key"],
                        "name": outcome["name"],   # "Over" or "Under"
                        "line": outcome.get("point"),
                        "price": outcome["price"],
                    })

    if not player_odds:
        return {"message": f"No props found for {player_name} today."}

    return str({
        "player": player_name,
        "team": full_team_name,
        "opponent": opponent,
        "game_time": target_event["commence_time"],
        "odds": player_odds,
    })
