"""
Planner Agent: Creates project architecture and plan
"""
from typing import Any, Dict, List
from core.agent_base import Agent
from core.config import Config
import openai


class Planner(Agent):
    """
    Creates overall project scheme and architecture based on researcher findings
    Determines how components work together
    """
    
    def __init__(self):
        super().__init__("Planner")
        openai.api_key = Config.OPENAI_API_KEY
    
    def create_plan(self, research_findings: Dict) -> str:
        """Generate project plan using LLM"""
        self.log_action("Generating project plan")
        
        prompt = f"""
        Based on the following research findings, create a detailed project plan:
        
        Project: {research_findings.get('project_name', 'Unknown')}
        
        GitHub Repos Found:
        {self._format_repos(research_findings.get('github_repos', []))}
        
        Web Resources:
        {self._format_web_results(research_findings.get('web_results', []))}
        
        Create a comprehensive plan that includes:
        1. Project Architecture (components, modules, services)
        2. Technology Stack (based on research)
        3. Implementation Strategy (phases, steps)
        4. Integration Points (how components interact)
        5. Potential Challenges & Solutions
        6. Success Criteria
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            plan = response.choices[0].message.content
            return plan
        except Exception as e:
            self.log_action("Plan generation failed", {"error": str(e)})
            return ""
    
    def _format_repos(self, repos: List[Dict]) -> str:
        """Format GitHub repos for LLM context"""
        formatted = []
        for repo in repos[:5]:
            formatted.append(f"- {repo.get('name', 'Unknown')}: {repo.get('description', 'No description')}")
        return "\n".join(formatted) if formatted else "No repositories found"
    
    def _format_web_results(self, results: List[Dict]) -> str:
        """Format web results for LLM context"""
        formatted = []
        for result in results[:5]:
            formatted.append(f"- {result.get('name', 'Unknown')}: {result.get('snippet', 'No snippet')}")
        return "\n".join(formatted) if formatted else "No web results found"
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create plan based on research
        Task format:
        {
            "research_findings": Dict
        }
        """
        self.log_action("Starting planning", task)
        
        research_findings = task.get("research_findings", {})
        
        if not research_findings:
            research_findings = self.read_kb(Config.RESEARCH_FINDINGS)
        
        plan_text = self.create_plan(research_findings)
        
        plan_output = {
            "project_name": research_findings.get("project_name", "Unknown"),
            "plan": plan_text,
            "research_based_on": research_findings.get("project_name"),
            "planning_completed": bool(plan_text)
        }
        
        # Store in KB
        self.write_kb(Config.PROJECT_PLAN, plan_output)
        
        self.log_action("Planning completed", {"plan_length": len(plan_text)})
        
        return plan_output
