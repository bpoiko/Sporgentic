from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from tools.odds import oddsFetcher
from tools.injury_live import injuryCheck
from tools.player_stats import statsLookup

tools = [oddsFetcher, injuryCheck, statsLookup]

llm = ChatOllama(model="mistral-nemo")

system_prompt = (
    "You are a sports analysis assistant that helps evaluate NBA player props. "
    "Use the available tools to look up stats, injury status, and betting odds before giving a recommendation."
)

agent = create_agent(llm, tools)

if __name__ == "__main__":
    user_qn = input("Ask me about a player: ")
    result = agent.invoke({"messages": [("human", user_qn)]})
    print(result["messages"][-1].content)


