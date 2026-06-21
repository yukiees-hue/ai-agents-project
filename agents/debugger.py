"""
Debugger Agent: Fixes errors found by Checker, Tester, or Logic
"""
from typing import Any, Dict
from core.agent_base import Agent
from core.config import Config
import openai


class Debugger(Agent):
    """
    Fixes code errors by:
    - Analyzing error messages and stack traces
    - Identifying root causes
    - Generating fixes
    - Consulting Researcher for solution validation
    - Looping feedback through Checker
    """
    
    def __init__(self):
        super().__init__("Debugger")
        openai.api_key = Config.OPENAI_API_KEY
    
    def analyze_error(self, error: str, code: str) -> Dict[str, Any]:
        """Analyze error and identify root cause"""
        self.log_action("Analyzing error", {"error_length": len(error)})
        
        prompt = f"""
        Analyze this error and identify the root cause:
        
        Error/Issue:
        {error}
        
        Code:
        {code[:2000]}...
        
        Provide:
        1. Root cause analysis
        2. Why this error occurred
        3. Severity (critical/high/medium/low)
        4. Potential fixes
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=1000
            )
            analysis = response.choices[0].message.content
            return {
                "analysis": analysis,
                "status": "ANALYZED"
            }
        except Exception as e:
            self.log_action("Error analysis failed", {"error": str(e)})
            return {"status": "FAILED", "error": str(e)}
    
    def generate_fix(self, error: str, code: str, analysis: str) -> str:
        """Generate a fix for the identified error"""
        self.log_action("Generating fix")
        
        prompt = f"""
        Generate a fix for this error:
        
        Original Code:
        {code}
        
        Error:
        {error}
        
        Analysis:
        {analysis}
        
        Provide corrected code that:
        1. Fixes the error
        2. Maintains original functionality
        3. Follows best practices
        4. Includes error handling
        
        Return only the fixed code.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000
            )
            fixed_code = response.choices[0].message.content
            return fixed_code
        except Exception as e:
            self.log_action("Fix generation failed", {"error": str(e)})
            return code
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Debug and fix code
        Task format:
        {
            "code": str,
            "error": str,
            "error_source": str (checker|tester|logic)
        }
        """
        self.log_action("Starting debugging", task)
        
        code = task.get("code", "")
        error = task.get("error", "")
        error_source = task.get("error_source", "unknown")
        
        if not code or not error:
            return {
                "status": "FAILED",
                "reason": "Missing code or error information"
            }
        
        # Analyze error
        analysis_result = self.analyze_error(error, code)
        
        if analysis_result.get("status") == "FAILED":
            return analysis_result
        
        analysis = analysis_result.get("analysis", "")
        
        # Generate fix
        fixed_code = self.generate_fix(error, code, analysis)
        
        result = {
            "status": "FIXED" if fixed_code != code else "FAILED",
            "error_source": error_source,
            "original_code": code,
            "fixed_code": fixed_code,
            "error_analysis": analysis,
            "ready_for_revalidation": True
        }
        
        # Store fix in KB for tracking
        self.append_kb(Config.CORRECTIONS_FILE, "debug_fixes", {
            "error": error,
            "analysis": analysis,
            "fix_applied": True
        })
        
        self.log_action("Debugging completed", {"status": result["status"]})
        
        return result
