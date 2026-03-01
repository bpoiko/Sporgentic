import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from tools.player_stats import statsLookup
from tools.injury_live import injuryCheck
from tools.odds import oddsFetcher

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")

embeddings = OllamaEmbeddings(model="nomic-embed-text")
vector_store = Chroma(embedding_function=embeddings, persist_directory=CHROMA_PATH)


def ingest_player(player_name: str):
    """Pull live data for a player from all tools and store in the vector store."""
    docs = []

    try:
        stats = statsLookup.invoke({"player_name": player_name})
        docs.append(Document(
            page_content=stats,
            metadata={"player": player_name, "source": "nba_api", "type": "stats"}
        ))
    except Exception as e:
        print(f"Stats fetch failed: {e}")

    try:
        injury = injuryCheck.invoke({"player_name": player_name})
        docs.append(Document(
            page_content=injury,
            metadata={"player": player_name, "source": "nba_injury_report", "type": "injury"}
        ))
    except Exception as e:
        print(f"Injury fetch failed: {e}")

    try:
        odds = oddsFetcher.invoke({"player_name": player_name})
        docs.append(Document(
            page_content=odds,
            metadata={"player": player_name, "source": "odds_api", "type": "odds"}
        ))
    except Exception as e:
        print(f"Odds fetch failed: {e}")

    if docs:
        vector_store.add_documents(docs)
        print(f"Ingested {len(docs)} documents for {player_name}")

    return vector_store


def get_retriever():
    """Return a retriever the agent can query against stored player data."""
    return vector_store.as_retriever(search_kwargs={"k": 5})


if __name__ == "__main__":
    player = input("Enter player name to ingest: ")
    ingest_player(player)
