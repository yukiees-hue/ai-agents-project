"""
Base class for all AI agents
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List
from datetime import datetime
import json
from pathlib import Path
from core.config import Config


class Agent(ABC):
    """Base agent class with common functionality"""
    
    def __init__(self, name: str, model: str = None):
        self.name = name
        self.model = model or Config.AGENT_MODEL
        self.created_at = datetime.now()
        self.log = []
        
    def log_action(self, action: str, details: Dict[str, Any] = None):
        """Log agent actions for audit trail"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "action": action,
            "details": details or {}
        }
        self.log.append(entry)
        if Config.VERBOSE:
            print(f"[{self.name}] {action}")
    
    def read_kb(self, kb_file: Path) -> Dict:
        """Read from knowledge base"""
        if kb_file.exists():
            with open(kb_file, 'r') as f:
                return json.load(f)
        return {}
    
    def write_kb(self, kb_file: Path, data: Dict):
        """Write to knowledge base"""
        kb_file.parent.mkdir(parents=True, exist_ok=True)
        with open(kb_file, 'w') as f:
            json.dump(data, f, indent=2)
        self.log_action(f"Wrote to {kb_file.name}", {"size": len(data)})
    
    def append_kb(self, kb_file: Path, key: str, value: Any):
        """Append to knowledge base"""
        data = self.read_kb(kb_file)
        if key not in data:
            data[key] = []
        data[key].append(value)
        self.write_kb(kb_file, data)
    
    @abstractmethod
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent's main task - implemented by subclasses"""
        pass
    
    def get_log(self) -> List[Dict]:
        """Return action log"""
        return self.log
