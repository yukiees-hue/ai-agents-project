"""
Comparer Agent: Cross-validates against real-world proof and provides corrections
"""
from typing import Any, Dict, List
from core.agent_base import Agent
from core.config import Config
import openai
import requests


class Comparer(Agent):
    """
    Validates research and code against real-world implementations:
    - Compares against live GitHub repos
    - Tests claimed capabilities
    - Provides corrections and improvements
    - Works with Researcher to refine findings
    """
    
    def __init__(self):
        super().__init__("Comparer")
        openai.api_key = Config.OPENAI_API_KEY
    
    def compare_with_implementations(self, findings: Dict, repos: List[Dict]) -> Dict[str, Any]:
        """Compare research findings against real implementations"""
        self.log_action("Comparing with real implementations")
        
        prompt = f"""
        Compare these research findings against real-world implementations:
        
        Research Findings:
        {findings}
        
        Reference Implementations:
        {self._format_repo_info(repos[:3])}
        
        Analyze:
        1. Are the findings consistent with real implementations?
        2. What differences exist?
        3. What best practices are missing?
        4. Are there better approaches?
        5. What production considerations are overlooked?
        
        Provide corrections and recommendations.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=1500
            )
            return {
                "comparison": response.choices[0].message.content,
                "status": "COMPARED"
            }
        except Exception as e:
            self.log_action("Comparison failed", {"error": str(e)})
            return {"status": "FAILED", "error": str(e)}
    
    def validate_code_against_examples(self, code: str, reference_repos: List[Dict]) -> Dict[str, Any]:
        """Validate code against reference implementations"""
        self.log_action("Validating code against examples")
        
        prompt = f"""
        Validate this code against reference implementations:
        
        Code to Validate:
        {code[:1500]}...
        
        Reference Repos:
        {self._format_repo_info(reference_repos[:3])}
        
        Check:
        1. Does it follow established patterns?
        2. Are error handling approaches consistent?
        3. Performance considerations vs references?
        4. Security practices aligned?
        5. Code style and conventions?
        
        Provide corrections needed.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=1500
            )
            return {
                "validation": response.choices[0].message.content,
                "status": "VALIDATED"
            }
        except Exception as e:
            self.log_action("Code validation failed", {"error": str(e)})
            return {"status": "FAILED", "error": str(e)}
    
    def _format_repo_info(self, repos: List[Dict]) -> str:
        """Format repository information for LLM"""
        formatted = []
        for repo in repos:
            formatted.append(f"""
- Name: {repo.get('name', 'Unknown')}
  Description: {repo.get('description', 'N/A')}
  Stars: {repo.get('stargazers_count', 0)}
  Language: {repo.get('language', 'Unknown')}
            """)
        return "\n".join(formatted)
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare findings and code against real-world implementations
        Task format:
        {
            "comparison_type": "research|code",
            "content": Dict or str,
            "reference_repos": List[Dict]
        }
        """
        self.log_action("Starting comparison", task)
        
        comparison_type = task.get("comparison_type", "").lower()
        content = task.get("content", {})
        repos = task.get("reference_repos", [])
        
        result = {}
        
        if comparison_type == "research":
            result = self.compare_with_implementations(content, repos)
        elif comparison_type == "code":
            result = self.validate_code_against_examples(content, repos)
        
        # Store corrections in KB
        corrections = self.read_kb(Config.CORRECTIONS_FILE)
        if "comparisons" not in corrections:
            corrections["comparisons"] = []
        corrections["comparisons"].append(result)
        self.write_kb(Config.CORRECTIONS_FILE, corrections)
        
        return result
