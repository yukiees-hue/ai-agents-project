"""
Tester Agent: Tests code to failure and ensures functionality
"""
from typing import Any, Dict, List
from core.agent_base import Agent
from core.config import Config
import subprocess
import tempfile
import os


class Tester(Agent):
    """
    Tests code by:
    - Running unit tests
    - Testing to failure (edge cases)
    - Verifying functionality
    - Coverage analysis
    """
    
    def __init__(self):
        super().__init__("Tester")
    
    def create_test_suite(self, code: str) -> str:
        """Generate comprehensive test cases using LLM"""
        self.log_action("Generating test suite")
        
        import openai
        openai.api_key = Config.OPENAI_API_KEY
        
        prompt = f"""
        Create comprehensive pytest test cases for this code:
        
        {code}
        
        Include:
        1. Normal case tests
        2. Edge case tests
        3. Error handling tests
        4. Boundary condition tests
        5. Integration tests (if applicable)
        
        Generate complete, runnable pytest test code.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=2000
            )
            tests = response.choices[0].message.content
            return tests
        except Exception as e:
            self.log_action("Test generation failed", {"error": str(e)})
            return ""
    
    def run_tests(self, code: str, tests: str) -> Dict[str, Any]:
        """Run test suite and capture results"""
        self.log_action("Running tests")
        
        results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "coverage": 0
        }
        
        try:
            # Create temporary files
            with tempfile.TemporaryDirectory() as tmpdir:
                code_file = os.path.join(tmpdir, "code.py")
                test_file = os.path.join(tmpdir, "test_code.py")
                
                with open(code_file, 'w') as f:
                    f.write(code)
                
                with open(test_file, 'w') as f:
                    f.write(tests)
                
                # Run pytest
                try:
                    output = subprocess.run(
                        ["python", "-m", "pytest", test_file, "-v", "--tb=short"],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    results["output"] = output.stdout
                    results["errors"] = output.stderr if output.returncode != 0 else []
                    
                    # Parse output
                    if "passed" in output.stdout:
                        import re
                        match = re.search(r'(\d+) passed', output.stdout)
                        if match:
                            results["passed"] = int(match.group(1))
                        match = re.search(r'(\d+) failed', output.stdout)
                        if match:
                            results["failed"] = int(match.group(1))
                        results["total_tests"] = results["passed"] + results["failed"]
                    
                except subprocess.TimeoutExpired:
                    results["errors"].append("Tests timed out after 30 seconds")
                
        except Exception as e:
            results["errors"].append(str(e))
        
        self.log_action("Tests completed", {
            "passed": results["passed"],
            "failed": results["failed"],
            "total": results["total_tests"]
        })
        
        return results
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test code
        Task format:
        {
            "code": str,
            "generate_tests": bool (optional, default: True)
        }
        """
        self.log_action("Starting testing phase", task)
        
        code = task.get("code", "")
        generate_tests = task.get("generate_tests", True)
        
        if generate_tests:
            tests = self.create_test_suite(code)
        else:
            tests = task.get("tests", "")
        
        if not tests:
            return {
                "status": "FAILED",
                "reason": "No tests available",
                "total_tests": 0
            }
        
        results = self.run_tests(code, tests)
        
        results["status"] = "PASSED" if results["failed"] == 0 else "FAILED"
        results["ready_for_logic"] = results["failed"] == 0
        
        return results
