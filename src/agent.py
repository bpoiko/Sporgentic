from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_core.tools.retriever import create_retriever_tool
from tools.odds import oddsFetcher
from tools.injury_live import injuryCheck
from tools.player_stats import statsLookup
from data.ingestion import get_retriever
from rich.console import Console
from rich.panel import Panel
from rich.spinner import Spinner
from rich.live import Live
from rich.text import Text
from rich import box

console = Console()

retriever_tool = create_retriever_tool(
    get_retriever(),
    name="player_data_search",
    description="Search stored player stats, injury reports, and odds. Use this first before calling live tools to avoid unnecessary API calls."
)

tools = [retriever_tool, oddsFetcher, injuryCheck, statsLookup]

llm = ChatOllama(model="mistral-nemo")

system_prompt = (
    "You are a sports analysis assistant that helps evaluate NBA player props. "
    "First search stored data using player_data_search, then use live tools only if the data is missing or outdated. "
    "Always respond in English only."
)

agent = create_agent(llm, tools, system_prompt=system_prompt)

TOOL_LABELS = {
    "player_data_search": "Searching stored data",
    "oddsFetcher":        "Fetching live odds",
    "injuryCheck":        "Checking injury report",
    "statsLookup":        "Looking up player stats",
}

if __name__ == "__main__":
    console.print(Panel.fit(
        "[bold green]Sporgentic[/bold green] — NBA Prop Analyzer",
        subtitle="powered by Ollama",
        box=box.DOUBLE_EDGE,
        border_style="purple"
    ))
    console.print()

    user_qn = console.input("[bold white]Ask me about a player:[/bold white] ")
    console.print()

    final_answer = ""
    all_agent_messages = []

    with Live(console=console, refresh_per_second=10) as live:
        for chunk in agent.stream({"messages": [("human", user_qn)]}):
            # Tool call in progress
            if "tools" in chunk:
                for msg in chunk["tools"].get("messages", []):
                    tool_name = getattr(msg, "name", "")
                    label = TOOL_LABELS.get(tool_name, f"Running {tool_name}")
                    live.update(Spinner("dots", text=Text(f" {label}...", style="yellow")))

            # Collect all agent messages
            if "agent" in chunk:
                msgs = chunk["agent"].get("messages", [])
                all_agent_messages.extend(msgs)
                live.update(Spinner("dots", text=Text(" Thinking...", style="cyan")))

    # Extract final answer from the last non-empty agent message
    for msg in reversed(all_agent_messages):
        content = getattr(msg, "content", "")
        if isinstance(content, str) and content:
            final_answer = content
            break
        elif isinstance(content, list):
            text = " ".join(c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text")
            if text:
                final_answer = text
                break

    console.print(Panel(
        final_answer,
        title="[bold green]Recommendation[/bold green]",
        border_style="green",
        box=box.ROUNDED,
        padding=(1, 2)
    ))


