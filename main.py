"""
Main entry point for AI Agents system
"""
import sys
from pathlib import Path
from core.config import Config
from core.orchestrator import Orchestrator
import json


def main():
    """Main execution function"""
    
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("Please set up your .env file with required API keys")
        sys.exit(1)
    
    print("=" * 60)
    print("AI AGENTS PROJECT PLANNING & DEVELOPMENT SYSTEM")
    print("=" * 60)
    
    # Example project specification
    project_spec = {
        "name": "Web Scraper with Analytics",
        "description": "A Python web scraper with data analytics capabilities",
        "search_queries": [
            "Python web scraper libraries",
            "data analytics Python",
            "web scraping best practices"
        ],
        "language": "python"
    }
    
    print(f"\nProject: {project_spec['name']}")
    print(f"Description: {project_spec['description']}")
    print("\n" + "-" * 60)
    
    # Initialize orchestrator
    orchestrator = Orchestrator()
    
    # Execute project
    result = orchestrator.execute_project(project_spec)
    
    # Display results
    print("\n" + "=" * 60)
    print("PROJECT EXECUTION SUMMARY")
    print("=" * 60)
    print(f"Status: {result.get('status')}")
    print(f"Project: {result.get('project_name')}")
    
    if result.get("planning"):
        print(f"\n✓ Planning Phase: {result['planning'].get('status')}")
    
    if result.get("development"):
        print(f"✓ Development Phase: {result['development'].get('status')}")
        print(f"  - Iterations: {result['development'].get('iterations')}")
        print(f"  - Code Length: {len(result['development'].get('final_code', ''))} chars")
        if result['development'].get("test_results"):
            test = result['development']["test_results"]
            print(f"  - Tests Passed: {test.get('passed')}/{test.get('total_tests')}")
    
    # Save results to file
    output_file = Path("execution_result.json")
    with open(output_file, 'w') as f:
        # Convert to JSON-serializable format
        json_result = json.dumps(result, indent=2, default=str)
        f.write(json_result)
    
    print(f"\n✓ Full results saved to: {output_file}")
    print("\n" + "=" * 60)
    
    return 0 if result.get('status') == 'SUCCESS' else 1


if __name__ == "__main__":
    sys.exit(main())
