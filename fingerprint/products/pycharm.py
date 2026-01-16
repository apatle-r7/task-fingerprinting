from typing import Dict, Any
from ..evidence import make_evidence

PRODUCT_META = {
    "productName": "PyCharm Community Edition",
    "productFamily": "IDE",
    "vendor": "JetBrains"
}

def detect(executor) -> Dict[str, Any]:
    # macOS detection using Spotlight for PyCharm CE
    detect_cmd = "mdfind \"kMDItemCFBundleIdentifier == 'com.jetbrains.pycharm.ce'\""
    res_detect = executor.run(detect_cmd, use_shell=True)
    evidence = make_evidence(res_detect)
    if not res_detect.get("raw_output"):
        return None

    # Get version from Info.plist
    app_path = res_detect.get("raw_output").splitlines()[0]
    version_cmd = f"defaults read '{app_path}/Contents/Info' CFBundleShortVersionString"
    res_version = executor.run(version_cmd, use_shell=True)
    evidence_version = make_evidence(res_version)

    return {
        "productName": PRODUCT_META["productName"],
        "versionNumber": res_version.get("raw_output", "").strip(),
        "architecture": "arm64",  # Assuming macOS default
        "productFamily": PRODUCT_META["productFamily"],
        "vendor": PRODUCT_META["vendor"],
        "evidence": {
            "detection": evidence,
            "version": evidence_version
        }
    }