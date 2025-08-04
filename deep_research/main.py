import sys
import os

# Add the parent directory of 'deep_research' to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from deep_research.coordinator import ResearchCoordinator


load_dotenv()
console = Console()

async def main() -> None:
    console.print("[bold cyan]Deep Reaserach Tool[/bold cyan] - Console Edition")
    console.print("This tool performs in-depth research on various topics using AI agents.")

    # get user query
    query = Prompt.ask("\n[bold]What topic would you like to research?[/bold]")

    if not query:
        console.print("[bold red]Error:[/bold red] Please provide a valid topic to research.")

    research_coordinator = ResearchCoordinator(query=query)
    report = await research_coordinator.research()

    # console.print(f"\n[bold green]Research Report:[/bold green]{report}")

if __name__ == "__main__":
    asyncio.run(main())
    console.print(Panel("Execution completed successfully!", style="bold green"))
