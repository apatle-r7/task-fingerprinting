import platform
from typing import Dict, Any
from ..evidence import make_evidence

# OS name normalization mapping
OS_NAME_MAP = {
    "Darwin": "macOS",
    "Linux": "Linux",
    "Windows": "Windows"
}

def collect_system_info(executor) -> Dict[str, Any]:
    sys_info = {
        "os": None,
        "version": None,
        "kernel": None,
        "cpu": None,
        "evidence": {}
    }
    # Detect OS name and version using platform and platform-specific commands as evidence
    try:
        name = platform.system()
        sys_info["os"] = OS_NAME_MAP.get(name, name)
    except Exception:
        sys_info["os"] = "unknown"

    if platform.system() == "Darwin":
        cmd_name = "sw_vers -productName"
        cmd_ver = "sw_vers -productVersion"
        cmd_kernel = "uname -r"
        cmd_cpu = "uname -m"
        res_name = executor.run(cmd_name)
        res_ver = executor.run(cmd_ver)
        res_kernel = executor.run(cmd_kernel)
        res_cpu = executor.run(cmd_cpu)
        sys_info["version"] = res_ver.get("raw_output", "")
        sys_info["kernel"] = res_kernel.get("raw_output", "")
        sys_info["cpu"] = res_cpu.get("raw_output", "")
        sys_info["evidence"]["os_name"] = make_evidence(res_name)
        sys_info["evidence"]["os_version"] = make_evidence(res_ver)
        sys_info["evidence"]["kernel"] = make_evidence(res_kernel)
        sys_info["evidence"]["cpu"] = make_evidence(res_cpu)
    elif platform.system() == "Linux":
        cmd_osrel = "cat /etc/os-release"
        res_osrel = executor.run(cmd_osrel, use_shell=True)
        sys_info["version"] = res_osrel.get("raw_output", "")
        res_kernel = executor.run("uname -r")
        res_cpu = executor.run("uname -m")
        sys_info["kernel"] = res_kernel.get("raw_output", "")
        sys_info["cpu"] = res_cpu.get("raw_output", "")
        sys_info["evidence"]["os_release"] = make_evidence(res_osrel)
        sys_info["evidence"]["kernel"] = make_evidence(res_kernel)
        sys_info["evidence"]["cpu"] = make_evidence(res_cpu)
    elif platform.system() == "Windows":
        # On Windows, prefer PowerShell commands; executor must handle running them (local will)
        cmd_ver = "powershell -Command \"Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version | ConvertTo-Json\""
        res_ver = executor.run(cmd_ver, use_shell=True)
        sys_info["version"] = res_ver.get("raw_output", "")
        res_kernel = executor.run("ver", use_shell=True)
        sys_info["kernel"] = res_kernel.get("raw_output", "")
        # CPU
        cmd_cpu = "powershell -Command \"Get-CimInstance Win32_ComputerSystem | Select-Object -Property Manufacturer,Model,SystemType | ConvertTo-Json\""
        res_cpu = executor.run(cmd_cpu, use_shell=True)
        sys_info["cpu"] = res_cpu.get("raw_output", "")
        sys_info["evidence"]["os_version"] = make_evidence(res_ver)
        sys_info["evidence"]["kernel"] = make_evidence(res_kernel)
        sys_info["evidence"]["cpu"] = make_evidence(res_cpu)
    else:
        # Fallback generic commands
        res_uname = executor.run("uname -a")
        sys_info["version"] = ""
        sys_info["kernel"] = res_uname.get("raw_output", "")
        sys_info["cpu"] = platform.machine()
        sys_info["evidence"]["uname"] = make_evidence(res_uname)
    return sys_info