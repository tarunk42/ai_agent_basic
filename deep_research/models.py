from pydantic import BaseModel

class SearchResults(BaseModel):
    """
    Represents the search results for a query.
    """
    title: str
    url: str
    summary: str