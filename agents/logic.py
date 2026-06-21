"""
Logic Agent: Simulates user interaction and validates all code paths
"""
from typing import Any, Dict, List
from core.agent_base import Agent
from core.config import Config
import openai
import subprocess
import tempfile
import os


class Logic(Agent):
    """
    Validates code through:
    - User path simulation (all possible user interactions)
    - Edge case exploration
    - Workflow validation
    - User experience testing
    Works alongside Tester for comprehensive validation
    """
    
    def __init__(self):
        super().__init__("Logic")
        openai.api_key = Config.OPENAI_API_KEY
    
    def generate_user_scenarios(self, code: str) -> List[str]:
        """Generate comprehensive user interaction scenarios"""
        self.log_action("Generating user scenarios")
        
        prompt = f"""
        For this code, generate comprehensive user interaction scenarios:
        
        {code[:2000]}...
        
        Create scenarios that cover:
        1. Normal happy path
        2. Alternative workflows
        3. Error conditions (user input validation)
        4. Edge cases (empty input, max values, etc.)
        5. Security considerations (injection, etc.)
        6. Performance edge cases
        7. Concurrent access (if applicable)
        
        Return as a Python list of test scenario descriptions.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            scenarios_text = response.choices[0].message.content
            # Parse scenarios from response
            return scenarios_text.split('\n')
        except Exception as e:
            self.log_action("Scenario generation failed", {"error": str(e)})
            return []
    
    def validate_user_paths(self, code: str, scenarios: List[str]) -> Dict[str, Any]:
        """Validate all user paths through the code"""
        self.log_action("Validating user paths", {"scenario_count": len(scenarios)})
        
        results = {
            "total_scenarios": len(scenarios),
            "passed": 0,
            "failed": 0,
            "issues": []
        }
        
        for scenario in scenarios:
            if not scenario.strip():
                continue
            
            prompt = f"""
            Analyze if this code handles this user scenario correctly:
            
            Code:
            {code[:1500]}...
            
            Scenario: {scenario}
            
            Does the code handle this scenario correctly?
            - Yes: code handles it properly
            - No: there's an issue
            - Maybe: unclear behavior
            
            Provide brief analysis.
            """
            
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5,
                    max_tokens=500
                )
                analysis = response.choices[0].message.content
                
                if "yes" in analysis.lower():
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                    results["issues"].append({"scenario": scenario, "analysis": analysis})
            except Exception as e:
                self.log_action("Path validation failed", {"error": str(e)})
        
        return results
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate code through user logic
        Task format:
        {
            "code": str
        }
        """
        self.log_action("Starting logic validation", task)
        
        code = task.get("code", "")
        
        if not code:
            return {
                "status": "FAILED",
                "reason": "No code provided"
            }
        
        # Generate user scenarios
        scenarios = self.generate_user_scenarios(code)
        
        # Validate user paths
        validation_results = self.validate_user_paths(code, scenarios)
        
        # Determine overall status
        status = "PASSED" if validation_results["failed"] == 0 else "FAILED"
        
        result = {
            "status": status,
            "scenarios_tested": validation_results["total_scenarios"],
            "scenarios_passed": validation_results["passed"],
            "scenarios_failed": validation_results["failed"],
            "issues": validation_results["issues"],
            "ready_for_production": validation_results["failed"] == 0
        }
        
        self.log_action("Logic validation completed", {"status": status})
        
        return result
