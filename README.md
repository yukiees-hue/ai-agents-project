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
├── requirements.txt
└── main.py
```

## Getting Started

### 1. Setup

```bash
# Clone repository
git clone https://github.com/yukiees-hue/ai-agents-project.git
cd ai-agents-project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your API keys:
# - OPENAI_API_KEY (required)
# - GITHUB_TOKEN (required)
# - BING_SEARCH_KEY (optional)
```

### 3. Run the System

```bash
python main.py
```

## Agent Communication Flow

```
Planning Phase:
  Researcher → KB (findings) → Checker
                            ↓
                         Comparer → KB (corrections)
                            ↓
              Planner → KB (plan) → Checker

Development Phase:
  Developer → Code → Checker → {Approved/Needs Revision}
                        ↓
                  {Approved}
                        ↓
              Tester + Logic → Results
                        ↓
                  {All Passed}
                        ↓
                    Production Ready
                        
  If Errors Found:
    Error → Debugger → Researcher (find solution)
                            ↓
                         Checker → Developer (revise)
```

## Agent Responsibilities

### Researcher
- Searches GitHub for relevant repositories
- Performs web searches for documentation and best practices
- Compiles findings into shared knowledge base
- Provides project context for other agents

### Planner
- Analyzes research findings
- Creates architecture and project plan
- Defines implementation phases
- Ensures feasibility and completeness

### Checker/Confirmer
- Validates all agent outputs
- Unbiased review of code and plans
- Identifies issues and inconsistencies
- Ensures quality standards

### Comparer
- Cross-validates against real-world implementations
- Tests claimed capabilities
- Provides corrections and improvements
- Works with Researcher for refinement

### Developer
- Writes code following approved plan
- Incorporates validated research
- Follows best practices and design patterns
- Submits for review and testing

### Tester
- Generates comprehensive test cases
- Tests code to failure
- Validates all functionality
- Reports test coverage and results

### Logic
- Simulates user interactions
- Explores all code paths
- Validates edge cases
- Ensures user experience quality

### Debugger
- Analyzes errors from any source
- Identifies root causes
- Generates fixes
- Loops back to Researcher for solution validation

## Knowledge Base

All agents share a knowledge base stored as JSON files in `kb/`:

- `research_findings.json`: GitHub repos, web resources, documentation
- `project_plan.json`: Architecture, strategy, implementation phases
- `validation_reports.json`: All validation results and issues found
- `corrections.json`: Corrections and improvements from Comparer and Debugger

## Configuration Options

| Variable | Description | Default |
|----------|-------------|--------|
| OPENAI_API_KEY | OpenAI API key (required) | - |
| GITHUB_TOKEN | GitHub API token (required) | - |
| BING_SEARCH_KEY | Bing Search API key (optional) | - |
| AGENT_MODEL | LLM model to use | gpt-4 |
| MAX_ITERATIONS | Max development iterations | 10 |
| VERBOSE | Enable verbose logging | true |

## Example Project

The system includes an example project: "Web Scraper with Analytics"

Run it to see the full agent workflow:

```bash
python main.py
```

## Execution Results

After execution, results are saved to `execution_result.json` containing:
- Planning phase results
- Development phase results
- Test results
- Complete workflow log

## Future Enhancements

- [ ] Database integration for knowledge base
- [ ] Real-time agent monitoring dashboard
- [ ] Custom agent creation framework
- [ ] Integration with GitHub for automated deployments
- [ ] Slack/Discord notifications
- [ ] Multi-language support
- [ ] Agent performance metrics

## License

MIT

## Contributing

Contributions welcome! Please create an issue or pull request.
