"""
Orchestrator: Coordinates all agents and manages workflow
"""
from typing import Any, Dict, List
from pathlib import Path
from core.config import Config
from agents.researcher import Researcher
from agents.planner import Planner
from agents.checker import Checker
from agents.developer import Developer
from agents.tester import Tester
import json


class Orchestrator:
    """Main orchestrator that manages agent workflow"""
    
    def __init__(self):
        self.researcher = Researcher()
        self.planner = Planner()
        self.checker = Checker()
        self.developer = Developer()
        self.tester = Tester()
        self.workflow_log = []
    
    def log_workflow(self, step: str, details: Dict[str, Any] = None):
        """Log workflow execution"""
        entry = {
            "step": step,
            "details": details or {}
        }
        self.workflow_log.append(entry)
        if Config.VERBOSE:
            print(f"\n[ORCHESTRATOR] {step}")
    
    def planning_phase(self, project_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Execute planning phase with all planning agents"""
        self.log_workflow("Starting planning phase")
        
        # Step 1: Research
        self.log_workflow("Phase 1: Research")
        research_result = self.researcher.execute({
            "project_name": project_spec.get("name", "Unknown"),
            "description": project_spec.get("description", ""),
            "search_queries": project_spec.get("search_queries", []),
            "search_language": project_spec.get("language", "python")
        })
        
        # Step 2: Checker validates research
        self.log_workflow("Phase 1b: Validating research")
        validation = self.checker.execute({
            "validation_type": "research",
            "content": research_result
        })
        
        if "INVALID" in validation.get("status", ""):
            self.log_workflow("Research validation failed", {"status": validation})
            return {"status": "FAILED", "phase": "research_validation"}
        
        # Step 3: Planning
        self.log_workflow("Phase 2: Planning")
        plan_result = self.planner.execute({
            "research_findings": research_result
        })
        
        # Step 4: Validate plan
        self.log_workflow("Phase 2b: Validating plan")
        plan_validation = self.checker.execute({
            "validation_type": "plan",
            "content": plan_result
        })
        
        if "INVALID" in plan_validation.get("status", ""):
            self.log_workflow("Plan revision needed", {"status": plan_validation})
            # Could loop back to planner for revision
        
        self.log_workflow("Planning phase completed")
        
        return {
            "status": "SUCCESS",
            "phase": "planning",
            "research": research_result,
            "plan": plan_result,
            "validations": {
                "research": validation,
                "plan": plan_validation
            }
        }
    
    def development_phase(self, plan: Dict[str, Any], max_iterations: int = 3) -> Dict[str, Any]:
        """Execute development phase with code generation and testing"""
        self.log_workflow("Starting development phase")
        
        iteration = 0
        current_code = ""
        
        while iteration < max_iterations:
            iteration += 1
            self.log_workflow(f"Development iteration {iteration}")
            
            # Generate code
            self.log_workflow(f"Development iteration {iteration}: Code generation")
            if iteration == 1:
                dev_result = self.developer.execute({
                    "plan": plan.get("plan", ""),
                    "language": "python"
                })
            else:
                dev_result = self.developer.execute({
                    "plan": plan.get("plan", ""),
                    "language": "python",
                    "feedback": self.last_feedback,
                    "existing_code": current_code
                })
            
            current_code = dev_result.get("code", "")
            
            # Code review
            self.log_workflow(f"Development iteration {iteration}: Code review")
            review = self.checker.execute({
                "validation_type": "code",
                "content": current_code,
                "plan": plan.get("plan", "")
            })
            
            self.last_feedback = review.get("report", "")
            
            if "APPROVED" in review.get("status", ""):
                self.log_workflow("Code approved, moving to testing")
                break
            elif "REJECTED" in review.get("status", ""):
                self.log_workflow("Code rejected, requesting revision")
            else:
                self.log_workflow("Code needs revision")
        
        # Testing
        self.log_workflow("Development phase: Testing")
        test_result = self.tester.execute({
            "code": current_code,
            "generate_tests": True
        })
        
        self.log_workflow("Development phase completed")
        
        return {
            "status": "SUCCESS" if test_result.get("status") == "PASSED" else "NEEDS_DEBUG",
            "phase": "development",
            "final_code": current_code,
            "iterations": iteration,
            "code_review": review,
            "test_results": test_result
        }
    
    def execute_project(self, project_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Execute full project workflow"""
        self.log_workflow("Project execution started", {"project": project_spec.get("name")})
        
        # Planning phase
        planning_result = self.planning_phase(project_spec)
        
        if planning_result.get("status") != "SUCCESS":
            return planning_result
        
        # Development phase
        dev_result = self.development_phase(planning_result.get("plan", {}))
        
        # Final summary
        final_result = {
            "project_name": project_spec.get("name"),
            "status": dev_result.get("status"),
            "planning": planning_result,
            "development": dev_result,
            "workflow_log": self.workflow_log
        }
        
        self.log_workflow("Project execution completed", {"status": final_result.get("status")})
        
        return final_result
