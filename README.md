# AI Agents Project Planning & Development System

A multi-agent AI system designed to automate project planning and development through specialized agents that collaborate and validate each other's work.

## Agent Architecture

### Planning Phase
- **Researcher**: Gathers information from web and GitHub, stores in shared knowledge base
- **Planner**: Creates overall project scheme and architecture
- **Checker/Confirmer**: Validates findings with unbiased review
- **Comparer**: Cross-validates against real-world proof and provides corrections

### Development Phase
- **Developer**: Writes code following the plan
- **Tester**: Tests code to failure, ensures functionality
- **Logic**: User-path validation and edge case exploration
- **Debugger**: Fixes errors, loops back to Researcher for solutions

## Project Structure

```
ai-agents-project/
├── agents/                 # Agent implementations
│   ├── researcher.py
│   ├── planner.py
│   ├── checker.py
│   ├── comparer.py
│   ├── developer.py
│   ├── tester.py
│   ├── logic.py
│   └── debugger.py
├── kb/                     # Knowledge Base (shared between agents)
│   ├── research_findings.json
│   ├── project_plan.json
│   ├── validation_reports.json
│   └── corrections.json
├── core/                   # Core infrastructure
│   ├── agent_base.py
│   ├── orchestrator.py
│   └── config.py
├── projects/               # Individual project workspaces
│   └── .gitkeep
├── requirements.txt
└── main.py
```

## Getting Started

1. Install dependencies: `pip install -r requirements.txt`
2. Configure API keys in `.env`
3. Run: `python main.py`

## Agent Communication Flow

```
Researcher → KB (findings) → Planner → Plan
                           ↓
                        Checker (validates)
                           ↓
                       Comparer (cross-checks)
                           ↓
                        Developer (codes)
                           ↓
                    Checker (code review)
                           ↓
                  Tester + Logic (testing)
                           ↓
                    Debugger (if errors)
                           ↓
                    Researcher (find solutions)
```
