import sys
import os
import time

# Add the parent directory of 'deep_research' to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import Runner, trace
from deep_research.research_agents.query_agent import query_agent
from deep_research.research_agents.query_agent import QueryResponse
from deep_research.research_agents.search_agent import search_agent
from deep_research.research_agents.synthesis_agent import synthesis_agent
from deep_research.research_agents.follow_up_agent import follow_up_decision_agent, FollowUpDecisionResponse
from deep_research.models import SearchResults


from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from ddgs import DDGS

console = Console()


class ResearchCoordinator:
    def __init__(self, query: str):
        self.query = query
        self.search_results = []
        self.iteration = 1

    async def research(self) -> str:
        with trace("Deep Research Workflow"):
            query_response = await self.generate_queries()
            await self.perform_search_for_queries(queries=query_response.queries)

            # follow up query agent to refine the search
            while self.iteration < 5:
                decision_response = await self.generate_followup()

                if not decision_response.should_follow_up:
                   console.print("[cyan]No more research needed. Synthesizing report...[/cyan]")
                   break

                self.iteration += 1
                console.print(f"[cyan]Conducting follow-up research (iteration {self.iteration})...[/cyan]")

                await self.perform_search_for_queries(queries=decision_response.queries)
                 

            final_report = await self.synthesize_report()
             
            console.print("[bold green]Research completed successfully![/bold green]")
            console.print(Markdown(final_report))

            return final_report

    async def generate_queries(self) -> QueryResponse:
            with console.status("[bold cyan]Analyzing query...[/bold cyan]") as status:

                # Run the query agent
                result = await Runner.run(query_agent, input=self.query)

                # Display the results
                console.print(Panel("[bold cyan]Query Analysis[/bold cyan]"))
                console.print(f"[yellow]Thoughts:[/yellow] {result.final_output.thoughts}")
                console.print("\n[yellow]Generated Search Queries:[/yellow]")
                for i, query in enumerate(result.final_output.queries, start=1):
                    console.print(f"{i}. {query}")
                return result.final_output
    
    
    def duckduckgo_search(self, query :str):
        try:
            results = DDGS().text(query, region="us-en", safesearch="off", TimeLimit="y", max_results=5)
            return results
        except Exception as ex:
            console.print(f"[bold red]Error during search:[/bold red] {str(ex)}")
            return []

    async def perform_search_for_queries(self, queries: list[str]) -> None:
        
        # get all search results for each query
        all_search_results = {}
        for query in queries:
            search_results = self.duckduckgo_search(query)
            all_search_results[query] = search_results

        for query in queries:
            console.print(f"\n[bold cyan]Searching for:[/bold cyan] {query}")

            for result in all_search_results[query]:
                
                console.print(f"    [green]Result:[/green] {result['title']}")
                console.print(f"    [dim]URL:[/dim] {result['href']}")
                console.print(f"    [cyan]Analyzing content...[/cyan]")

                start_analysis_time = time.time()
                search_input = f"Title: {result["title"]} \nURL: {result["href"]}\n"
                agent_result = await Runner.run(search_agent, input=search_input)
                analysis_time = time.time() - start_analysis_time

                search_result = SearchResults(
                    title=result["title"],
                    url=result["href"],
                    summary=agent_result.final_output
                )

                self.search_results.append(search_result)

                summary_preview = agent_result.final_output[:100] + "..." if len(agent_result.final_output) > 100 else agent_result.final_output

                console.print(f"    [green]Summary Preview:[/green] {summary_preview}")
                console.print(f"    [dim]Analysis Completed in:[/dim] {analysis_time:.2f} seconds\n")
        
    
        console.print(f"\n[bold green]Research round complete![/bold green] Found {len(all_search_results)} sources across {len(queries)} queries.")

    
    async def synthesize_report(self) -> str:
        """
        Synthesize a report from the search results.
        """
        with console.status("[bold cyan]Synthesizing research report...[/bold cyan]") as status:
            findings_text = f"Query: {self.query}\n\n Search Results:\n"
            for i, result in enumerate(self.search_results, start=1):
                findings_text += f"\n{i}. Title: {result.title}\n   URL: {result.url}\n   Summary: {result.summary}\n"

            result = await Runner.run(synthesis_agent, input=findings_text)
            return result.final_output
        
    
    async def generate_followup(self) -> FollowUpDecisionResponse:
        with console.status("[bold cyan]Evaluating if more research is needed...[/bold cyan]") as status:
            findings_text = f"Original Query: {self.query}\n\nCurrent Findings:\n"
            for i, result in enumerate(self.search_results, 1):
                findings_text += f"\n{i}. Title: {result.title}\n   URL: {result.url}\n   Summary: {result.summary}\n"

            result = await Runner.run(follow_up_decision_agent, input=findings_text)

            console.print(Panel(f"[bold cyan]Follow-up Decision[/bold cyan]"))
            console.print(f"[yellow]Decision:[/yellow] {'More research needed' if result.final_output.should_follow_up else 'Research complete'}")
            console.print(f"[yellow]Reasoning:[/yellow] {result.final_output.reasoning}")

            if result.final_output.should_follow_up:
                console.print("\n[yellow]Follow-up Queries:[/yellow]")
                for i, query in enumerate(result.final_output.queries, 1):
                    console.print(f"  {i}. {query}")

            return result.final_output