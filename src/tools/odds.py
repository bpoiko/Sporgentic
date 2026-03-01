import requests
import os
from dotenv import load_dotenv

load_dotenv()
odds_key = os.getenv("ODDS_KEY")
"""Note to self so I can dev this in the morning
This will work in a way where we cant look up a sole players props
Solution, filter the results so we can have that player and that player only
SO; get props;filter for that respective player; then decide
"""
def oddsFetcher(player_name):
    # use 
    pass