from langchain_ollama import ChatOllama
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from tools.odds import oddsFetcher
from tools.injury_live import injuryCheck
from tools.player_stats import statsLookup

tools = [oddsFetcher,injuryCheck,statsLookup]

llm = ChatOllama(model="mistral-nemo")

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sports analysis assistant that helps evaluate NBA player props."
    "Use the available tools to look up stats, injury status, and betting odds before giving a reccomendation"),
    ("human", {input}),
    ("placeholder", "{agent_scratchpad}")
])
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

if __name__ == "__main__":
    user_qn = input()
    result = executor.invoke({"input": user_qn})
    print(result["output"])


