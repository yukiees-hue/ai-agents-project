"""
Researcher Agent: Gathers information from web and GitHub
"""
from typing import Any, Dict
from core.agent_base import Agent
from core.config import Config
import requests
import json


class Researcher(Agent):
    """
    Gathers information from:
    - GitHub repositories
    - Web searches (Bing)
    - Documentation
    Stores findings in shared KB for other agents
    """
    
    def __init__(self):
        super().__init__("Researcher")
        self.github_api = "https://api.github.com"
    
    def search_github(self, query: str, language: str = None) -> Dict[str, Any]:
        """Search GitHub for relevant repositories and code"""
        self.log_action("Searching GitHub", {"query": query, "language": language})
        
        headers = {"Authorization": f"token {Config.GITHUB_TOKEN}"}
        search_query = query
        if language:
            search_query += f" language:{language}"
        
        params = {
            "q": search_query,
            "sort": "stars",
            "order": "desc",
            "per_page": 10
        }
        
        try:
            response = requests.get(
                f"{self.github_api}/search/repositories",
                params=params,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.log_action("GitHub search failed", {"error": str(e)})
            return {"items": []}
    
    def search_web(self, query: str) -> Dict[str, Any]:
        """Search web using Bing (or other search API)"""
        self.log_action("Searching web", {"query": query})
        
        if not Config.BING_SEARCH_KEY:
            self.log_action("Bing search disabled - no API key")
            return {"webPages": {"value": []}}
        
        headers = {"Ocp-Apim-Subscription-Key": Config.BING_SEARCH_KEY}
        params = {"q": query, "count": 10}
        
        try:
            response = requests.get(
                "https://api.bing.microsoft.com/v7.0/search",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.log_action("Web search failed", {"error": str(e)})
            return {"webPages": {"value": []}}
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Research task format:
        {
            "project_name": str,
            "description": str,
            "search_queries": List[str],
            "search_language": str (optional)
        }
        """
        self.log_action("Starting research", task)
        
        findings = {
            "project_name": task.get("project_name", "Unknown"),
            "github_repos": [],
            "web_results": [],
            "research_completed": False
        }
        
        # Search GitHub
        for query in task.get("search_queries", []):
            github_results = self.search_github(query, task.get("search_language"))
            if github_results.get("items"):
                findings["github_repos"].extend(github_results["items"][:3])
        
        # Search Web
        for query in task.get("search_queries", []):
            web_results = self.search_web(query)
            if web_results.get("webPages", {}).get("value"):
                findings["web_results"].extend(web_results["webPages"]["value"][:3])
        
        findings["research_completed"] = True
        
        # Store in KB
        self.write_kb(Config.RESEARCH_FINDINGS, findings)
        
        self.log_action("Research completed", {
            "repos_found": len(findings["github_repos"]),
            "web_results": len(findings["web_results"])
        })
        
        return findings
