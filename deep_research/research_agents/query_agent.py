from agents import Agent
from pydantic import BaseModel
from datetime import datetime

QUERY_AGENT_PROMPT = f"""
Today's date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -
You are a helpfull assisstant that can generate search queries for research.
For each query, follow these steps:

1. First, think through and explain the topic you are researching:
    - Break down the key aspects that need to be researched.
    - Consider potential challenges and how you'll address them.
    - Explain your strategy for finding comprehensive information.

2. Then generate 3 search quesries that:
    - Are specific and focused on retrieving high-quality information.
    - Cover different aspects of the topic.
    - Will help find relevant and diverse information.

Always provide both your thought process and the generated queries in your response.
"""

class QueryResponse(BaseModel):
    queries: list[str]
    thoughts: str

query_agent = Agent(
    name = "Query Generator Agent",
    instructions = QUERY_AGENT_PROMPT,
    output_type= QueryResponse,
    model="gpt-4o-mini"
)