"""
Developer Agent: Writes code based on plan and validated research
"""
from typing import Any, Dict
from core.agent_base import Agent
from core.config import Config
import openai


class Developer(Agent):
    """
    Generates code based on:
    - Validated research findings
    - Approved project plan
    - Validation reports
    
    Follows plan strictly and submits to Checker for review
    """
    
    def __init__(self):
        super().__init__("Developer")
        openai.api_key = Config.OPENAI_API_KEY
    
    def generate_code(self, plan: str, language: str = "python") -> str:
        """Generate code based on validated plan"""
        self.log_action("Generating code", {"language": language})
        
        prompt = f"""
        Write production-ready {language} code based on this project plan:
        
        {plan}
        
        Requirements:
        1. Follow the plan exactly
        2. Include error handling
        3. Add logging statements
        4. Include docstrings/comments
        5. Use best practices and design patterns
        6. Make code testable and modular
        7. Include configuration management
        
        Provide complete, runnable code.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=3000
            )
            code = response.choices[0].message.content
            return code
        except Exception as e:
            self.log_action("Code generation failed", {"error": str(e)})
            return ""
    
    def refactor_code(self, code: str, feedback: str) -> str:
        """Refactor code based on Checker feedback"""
        self.log_action("Refactoring code", {"feedback_length": len(feedback)})
        
        prompt = f"""
        Refactor this code based on the following feedback:
        
        Feedback:
        {feedback}
        
        Original Code:
        {code}
        
        Provide the corrected code that addresses all feedback points.
        Keep the same functionality but fix all issues mentioned.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=3000
            )
            refactored = response.choices[0].message.content
            return refactored
        except Exception as e:
            self.log_action("Code refactoring failed", {"error": str(e)})
            return code
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate code from plan
        Task format:
        {
            "plan": str,
            "language": str (optional, default: python),
            "feedback": str (optional - if refactoring)
        }
        """
        self.log_action("Starting code generation", task)
        
        plan = task.get("plan", "")
        language = task.get("language", "python")
        feedback = task.get("feedback")
        
        if feedback:
            # Refactor based on feedback
            code = self.refactor_code(task.get("existing_code", ""), feedback)
            status = "REFACTORED"
        else:
            # Generate new code
            code = self.generate_code(plan, language)
            status = "GENERATED"
        
        result = {
            "status": status,
            "language": language,
            "code": code,
            "ready_for_review": bool(code)
        }
        
        self.log_action("Code generation completed", {"status": status, "code_length": len(code)})
        
        return result
