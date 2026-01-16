import argparse
from .executors import LocalExecutor, RemoteExecutor, DockerExecutor
from .collectors.os_collector import collect_system_info
from .collectors.software_collector import collect_software_inventory
from .output import build_report, write_report

def parse_args():
    p = argparse.ArgumentParser(description="Fingerprinting Agent")
    p.add_argument("--mode", choices=["local", "remote"], required=True, help="Execution mode: local or remote")
    p.add_argument("--target", default="localhost", help="Target host (user@host for remote)")
    p.add_argument("--output", required=True, help="Path to the output JSON file")
    p.add_argument("--timeout", type=int, default=10)
    p.add_argument("--docker-image", help="Docker image to use for remote execution")
    return p.parse_args()

def main():
    args = parse_args()

    if args.mode == "local":
        executor = LocalExecutor(timeout=args.timeout)
    elif args.mode == "remote":
        if args.docker_image:
            executor = DockerExecutor(docker_image=args.docker_image)
        else:
            executor = RemoteExecutor()
    else:
        raise ValueError("Invalid mode specified")

    system_info = collect_system_info(executor)
    software_inventory = collect_software_inventory(executor)
    report = build_report(scan_type=args.mode, target_host=args.target, system_info=system_info, software_inventory=software_inventory)
    write_report(report, path=args.output)
    print(f"Wrote report to {args.output}")

if __name__ == "__main__":
    main()