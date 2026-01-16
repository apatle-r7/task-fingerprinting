import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any

AGENT_VERSION = "1.0.0"

def build_report(scan_type: str, target_host: str, system_info: Dict[str, Any], software_inventory: list) -> Dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    scan_id = str(uuid.uuid4())
    report = {
        "agent_metadata": {
            "agent_version": AGENT_VERSION,
            "scan_id": scan_id,
            "timestamp": now,
            "scan_type": scan_type,
            "target_host": target_host
        },
        "system_info": system_info,
        "software_inventory": software_inventory
    }
    return report

def write_report(report: Dict[str, Any], path: str = "fingerprint_report.json"):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
