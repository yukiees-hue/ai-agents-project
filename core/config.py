"""
Configuration management for AI Agents system
"""
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Config:
    """Central configuration for all agents"""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    BING_SEARCH_KEY = os.getenv("BING_SEARCH_KEY", "")
    
    # GitHub Configuration
    GITHUB_OWNER = os.getenv("GITHUB_OWNER", "")
    GITHUB_REPO = os.getenv("GITHUB_REPO", "")
    
    # Agent Configuration
    AGENT_MODEL = os.getenv("AGENT_MODEL", "gpt-4")
    MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "10"))
    VERBOSE = os.getenv("VERBOSE", "true").lower() == "true"
    
    # Paths
    KB_DIR = Path("kb")
    AGENTS_DIR = Path("agents")
    PROJECTS_DIR = Path("projects")
    
    # KB File Paths
    RESEARCH_FINDINGS = KB_DIR / "research_findings.json"
    PROJECT_PLAN = KB_DIR / "project_plan.json"
    VALIDATION_REPORTS = KB_DIR / "validation_reports.json"
    CORRECTIONS_FILE = KB_DIR / "corrections.json"
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required = ["OPENAI_API_KEY", "GITHUB_TOKEN"]
        missing = [key for key in required if not getattr(cls, key)]
        if missing:
            raise ValueError(f"Missing required config: {', '.join(missing)}")
        
        # Create directories
        for directory in [cls.KB_DIR, cls.AGENTS_DIR, cls.PROJECTS_DIR]:
            directory.mkdir(exist_ok=True)
