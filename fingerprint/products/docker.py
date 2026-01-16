from typing import Dict, Any
from ..evidence import make_evidence

PRODUCT_META = {
    "productName": "Docker",
    "productFamily": "Virtualization",
    "vendor": "Docker Inc."
}

def detect(executor) -> Dict[str, Any]:
    # Detect Docker CLI
    detect_cmd = "which docker"
    res_detect = executor.run(detect_cmd, use_shell=True)
    evidence = make_evidence(res_detect)
    if not res_detect.get("raw_output"):
        return None

    # Get Docker version
    version_cmd = "docker --version"
    res_version = executor.run(version_cmd, use_shell=True)
    evidence_version = make_evidence(res_version)

    version_output = res_version.get("raw_output", "")
    version = version_output.split()[2].strip(",") if version_output else ""

    return {
        "productName": PRODUCT_META["productName"],
        "versionNumber": version,
        "architecture": "arm64",  # Assuming macOS default
        "productFamily": PRODUCT_META["productFamily"],
        "vendor": PRODUCT_META["vendor"],
        "evidence": {
            "detection": evidence,
            "version": evidence_version
        }
    }