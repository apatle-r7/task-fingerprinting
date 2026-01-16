import subprocess
from typing import Dict, Any, Tuple, Optional
import shlex
import time


class RemoteExecutor:
    def __init__(self, host: str, user: str, password: str, port: int = 22, timeout: int = 10):
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.timeout = timeout

    def run(self, command: str) -> Dict[str, Any]:
        """
        Run a command on a remote host via SSH.
        """
        start = time.time()
        try:
            ssh_command = [
                "sshpass", "-p", self.password,
                "ssh", "-o", "StrictHostKeyChecking=no",
                "-p", str(self.port),
                f"{self.user}@{self.host}", command
            ]
            result = subprocess.run(ssh_command, capture_output=True, text=True, timeout=self.timeout)
            raw = result.stdout.strip()
            err = result.stderr.strip()
            rc = result.returncode
        except subprocess.TimeoutExpired as e:
            raw = ""
            err = f"timeout: {str(e)}"
            rc = -1
        end = time.time()
        return {
            "command_run": " ".join(ssh_command),
            "raw_output": raw if raw else err,
            "exit_code": rc,
            "duration_seconds": end - start
        }


class LocalExecutor:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def run(self, command: str, use_shell: bool = False) -> Dict[str, Any]:
        start = time.time()
        try:
            if use_shell:
                proc = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=self.timeout)
            else:
                args = shlex.split(command)
                proc = subprocess.run(args, capture_output=True, text=True, timeout=self.timeout)
            raw = proc.stdout.strip()
            err = proc.stderr.strip()
            rc = proc.returncode
        except subprocess.TimeoutExpired as e:
            raw = ""
            err = f"timeout: {str(e)}"
            rc = -1
        end = time.time()
        return {
            "command_run": command,
            "raw_output": raw if raw else err,
            "exit_code": rc,
            "duration_seconds": end - start
        }

class DockerExecutor:
    def __init__(self, docker_image, ssh_user='root', ssh_password='root', ssh_port=22):
        self.docker_image = docker_image
        self.ssh_user = ssh_user
        self.ssh_password = ssh_password
        self.ssh_port = ssh_port

    def run_command(self, command):
        """
        Run a command inside the Docker container via SSH.
        """
        try:
            # Start the Docker container
            container_id = subprocess.check_output(
                ["docker", "run", "-d", "-p", f"{self.ssh_port}:22", self.docker_image]
            ).decode("utf-8").strip()

            # Execute the command via SSH
            ssh_command = [
                "sshpass", "-p", self.ssh_password, "ssh",
                f"-p {self.ssh_port}", f"{self.ssh_user}@localhost", command
            ]
            result = subprocess.run(ssh_command, capture_output=True, text=True)

            # Stop and remove the container after execution
            subprocess.run(["docker", "stop", container_id], check=True)
            subprocess.run(["docker", "rm", container_id], check=True)

            if result.returncode != 0:
                raise Exception(f"Command failed: {result.stderr}")

            return result.stdout

        except Exception as e:
            raise Exception(f"Error running command in Docker container: {str(e)}")