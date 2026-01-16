from typing import Dict, Any

def make_evidence(result: Dict[str, Any]) -> Dict[str, Any]:
    evidence = {
        "command_run": result.get("command_run", ""),
        "raw_output": result.get("raw_output", ""),
        "exit_code": result.get("exit_code", 0),
    }
    # Include optional timing information if available
    if "duration_seconds" in result:
        evidence["duration_seconds"] = result["duration_seconds"]
    return evidence