from typing import Dict, Any
from ..evidence import make_evidence
import platform
import re

PRODUCT_META = {
    "productName": "Visual Studio Code",
    "productFamily": "IDE",
    "vendor": "Microsoft"
}

def parse_architecture(file_output: str, fallback: str = "") -> str:
    """Parse architecture from 'file' command output, preferring arm64 for universal binaries."""
    if not file_output:
        return fallback
    # Check for universal binary with arm64
    if "arm64" in file_output.lower():
        return "arm64"
    elif "x86_64" in file_output.lower() or "x86-64" in file_output.lower():
        return "x86_64"
    elif "i386" in file_output.lower():
        return "i386"
    return fallback

def detect(executor) -> Dict[str, Any]:
    # Strategy 1: Try to find the 'code' binary and get --version
    detect_cmd = "which code 2>/dev/null"
    res_detect = executor.run(detect_cmd, use_shell=True)
    
    if res_detect.get("exit_code", 0) == 0 and res_detect.get("raw_output"):
        # code binary found, get version
        res_ver = executor.run("code --version", use_shell=True)
        evidence_ver = make_evidence(res_ver)
        version_output = res_ver.get("raw_output", "").splitlines()[0] if res_ver.get("raw_output") else ""
        return {
            "productName": PRODUCT_META["productName"],
            "versionNumber": version_output,
            "architecture": platform.machine(),
            "productFamily": PRODUCT_META["productFamily"],
            "vendor": PRODUCT_META["vendor"],
            "evidence": {
                "detection": make_evidence(res_detect),
                "version": evidence_ver
            }
        }
    
    # Strategy 2: macOS - check for application bundle
    if platform.system() == "Darwin":
        app_path = "/Applications/Visual Studio Code.app"
        res_exists = executor.run(f"test -d '{app_path}' && echo 'exists' || echo 'not found'", use_shell=True)
        
        if "exists" in res_exists.get("raw_output", ""):
            # Get version from Info.plist
            plist_cmd = f"defaults read '{app_path}/Contents/Info' CFBundleShortVersionString 2>/dev/null"
            res_version = executor.run(plist_cmd, use_shell=True)
            
            # Get architecture
            arch_cmd = f"file '{app_path}/Contents/MacOS/Electron' | head -1"
            res_arch = executor.run(arch_cmd, use_shell=True)
            arch_output = res_arch.get("raw_output", "")
            # Parse architecture from file output using helper
            arch = parse_architecture(arch_output, platform.machine())
            
            version = res_version.get("raw_output", "").strip()
            if version:
                return {
                    "productName": PRODUCT_META["productName"],
                    "versionNumber": version,
                    "architecture": arch,
                    "productFamily": PRODUCT_META["productFamily"],
                    "vendor": PRODUCT_META["vendor"],
                    "evidence": {
                        "detection": make_evidence(res_exists),
                        "version": make_evidence(res_version),
                        "architecture": make_evidence(res_arch)
                    }
                }
    
    # Strategy 3: Linux - check common installation paths
    if platform.system() == "Linux":
        paths = ["/usr/share/code", "/opt/visual-studio-code", "~/.vscode"]
        for path in paths:
            res_check = executor.run(f"test -d {path} && echo '{path}' || true", use_shell=True)
            if res_check.get("raw_output"):
                # Try to find version via dpkg, rpm, or snap
                res_dpkg = executor.run("dpkg -l code 2>/dev/null | grep '^ii' | awk '{print $3}'", use_shell=True)
                if res_dpkg.get("raw_output"):
                    return {
                        "productName": PRODUCT_META["productName"],
                        "versionNumber": res_dpkg.get("raw_output", "").strip(),
                        "architecture": platform.machine(),
                        "productFamily": PRODUCT_META["productFamily"],
                        "vendor": PRODUCT_META["vendor"],
                        "evidence": {
                            "detection": make_evidence(res_check),
                            "version": make_evidence(res_dpkg)
                        }
                    }
                break
    
    # Not found
    return None