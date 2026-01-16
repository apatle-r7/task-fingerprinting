from typing import List, Dict, Any
from ..products import vscode, pycharm, docker, slack, chrome
from ..evidence import make_evidence

PRODUCT_DETECTORS = [
    ("vscode", vscode.detect),
    ("pycharm", pycharm.detect),
    ("docker", docker.detect),
    ("slack", slack.detect),
    ("chrome", chrome.detect)
]

def collect_software_inventory(executor) -> List[Dict[str, Any]]:
    items = []
    for name, detector in PRODUCT_DETECTORS:
        try:
            res = detector(executor)
            if res:
                items.append(res)
        except Exception as e:
            # record a minimal failure artifact
            items.append({
                "productName": name,
                "error": str(e),
                "evidence": {"note": "detector-error"}
            })
    return items