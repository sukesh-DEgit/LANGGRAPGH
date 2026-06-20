import os
import requests
from tavily import TavilyClient
from dotenv import load_dotenv
load_dotenv()
client = TavilyClient(api_key = os.getenv("TAVILY_API_KEY"))

def tavily_search(query):
    response = client.search(
        query = query,
        max_results = 3
    )
    results = []

    for i,r in enumerate(response["results"],1):
        title = r.get("title","unknown")
        url = r.get("url","")
        snippet = r.get("content","").strip()

        if len(snippet)>300:
            snippet = snippet[:300].rsplit(" ",1)[0]

        results.append(f"""
                       {i}. {title},{url},{snippet}"""  )
        
    return "/n/n".join(results)
