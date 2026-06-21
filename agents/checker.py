"""
Checker/Confirmer Agent: Validates all agent outputs
"""
from typing import Any, Dict
from core.agent_base import Agent
from core.config import Config
import openai


class Checker(Agent):
    """
    Validates:
    - Researcher findings (accuracy, relevance)
    - Project plan (feasibility, clarity)
    - Code quality (against plan, best practices)
    - Test results (coverage, edge cases)
    """
    
    def __init__(self):
        super().__init__("Checker")
        openai.api_key = Config.OPENAI_API_KEY
    
    def validate_research(self, research_findings: Dict) -> Dict[str, Any]:
        """Validate research findings for accuracy and relevance"""
        self.log_action("Validating research findings")
        
        prompt = f"""
        Review these research findings for accuracy and relevance:
        
        Project: {research_findings.get('project_name')}
        GitHub Repos Found: {len(research_findings.get('github_repos', []))}
        Web Results: {len(research_findings.get('web_results', []))}
        
        Evaluate:
        1. Are the findings relevant to the project?
        2. Is the information current and accurate?
        3. Are there any obvious gaps or missing resources?
        4. Quality of sources (repos, articles, documentation)
        
        Provide a validation report with:
        - Findings assessment (VALID/NEEDS_REVIEW/INVALID)
        - Issues found (if any)
        - Recommendations for improvement
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=1000
            )
            report = response.choices[0].message.content
            return {
                "type": "research_validation",
                "report": report,
                "status": "VALIDATED"
            }
        except Exception as e:
            self.log_action("Research validation failed", {"error": str(e)})
            return {"type": "research_validation", "status": "FAILED", "error": str(e)}
    
    def validate_plan(self, plan: Dict) -> Dict[str, Any]:
        """Validate project plan for feasibility and clarity"""
        self.log_action("Validating project plan")
        
        prompt = f"""
        Review this project plan for feasibility and clarity:
        
        {plan.get('plan', 'No plan provided')}
        
        Evaluate:
        1. Is the architecture sound?
        2. Are all components clearly defined?
        3. Are integration points explicit?
        4. Is the timeline realistic?
        5. Are there missing considerations?
        
        Provide a validation report with:
        - Plan assessment (VALID/NEEDS_REVISION/INVALID)
        - Issues found
        - Required revisions
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=1000
            )
            report = response.choices[0].message.content
            return {
                "type": "plan_validation",
                "report": report,
                "status": "VALIDATED"
            }
        except Exception as e:
            self.log_action("Plan validation failed", {"error": str(e)})
            return {"type": "plan_validation", "status": "FAILED", "error": str(e)}
    
    def validate_code(self, code: str, plan: str) -> Dict[str, Any]:
        """Validate code against plan and best practices"""
        self.log_action("Validating code", {"code_length": len(code)})
        
        prompt = f"""
        Review this code against the project plan:
        
        Project Plan:
        {plan}
        
        Code to Review:
        {code[:2000]}...  # Truncated for context
        
        Validate:
        1. Does code follow the plan?
        2. Code quality and best practices?
        3. Potential bugs or issues?
        4. Missing implementations?
        5. Performance concerns?
        
        Provide a report with:
        - Code assessment (APPROVED/NEEDS_REVISION/REJECTED)
        - Issues found with line references
        - Required fixes before merge
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=1500
            )
            report = response.choices[0].message.content
            return {
                "type": "code_validation",
                "report": report,
                "status": "REVIEWED"
            }
        except Exception as e:
            self.log_action("Code validation failed", {"error": str(e)})
            return {"type": "code_validation", "status": "FAILED", "error": str(e)}
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate any agent output
        Task format:
        {
            "validation_type": "research|plan|code",
            "content": Dict or str
        }
        """
        self.log_action("Starting validation", task)
        
        validation_type = task.get("validation_type", "").lower()
        content = task.get("content", {})
        
        result = {}
        
        if validation_type == "research":
            result = self.validate_research(content)
        elif validation_type == "plan":
            result = self.validate_plan(content)
        elif validation_type == "code":
            plan = task.get("plan", "")
            result = self.validate_code(content, plan)
        
        # Store validation in KB
        validations = self.read_kb(Config.VALIDATION_REPORTS)
        if "validations" not in validations:
            validations["validations"] = []
        validations["validations"].append(result)
        self.write_kb(Config.VALIDATION_REPORTS, validations)
        
        return result
