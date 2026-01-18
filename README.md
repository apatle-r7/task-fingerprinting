Hi Team.

**Purpose**
- **Repo**: This project gathers system and software "fingerprints" from target hosts and writes a structured JSON report. It supports running locally, against a remote host via SSH, or by launching a container and executing commands there.

**How To Setup The Environment**
- **Python**: Use Python 3.8+ (3.10 recommended). Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```
- **Install Python deps**: install the requirements file:

```bash
pip install -r requirements.txt
```
- **OS / CLI dependencies**: for remote and docker execution you may need system packages:

- **ssh/sshpass**: `ssh` is required; `sshpass` is used by the remote executor for password-based SSH (optional if you use key-based auth). Install via your package manager (e.g., `brew install hudochenkov/sshpass/sshpass` on macOS or `apt install sshpass` on Debian/Ubuntu).
- **docker**: required if you use the Docker executor. Ensure the `docker` CLI and demon are installed and the current user can run containers.

**How To Run It**
- **CLI entry point**: Use the package CLI module. Example local run that writes `report.json`:

```bash
python -m fingerprint.cli --mode local --output report.json
```
- **Remote host** (password-based) example:

```bash
python -m fingerprint.cli --mode remote --target user@host --output remote_report.json
```

- **Docker executor** (runs a container and executes commands inside it via SSH):

```bash
python -m fingerprint.cli --mode remote --docker-image ubuntu:22.04 --output docker_report.json
```

- **Notes**: The executors return structured results (stdout/stderr, exit code and duration) so output is robust even on errors.

**Where Is The Starting Point**
- **Primary CLI**: The CLI entrypoint is `fingerprint/cli.py` — run it with `python -m fingerprint.cli` or by invoking the `main()` in that module. See [fingerprint/cli.py](fingerprint/cli.py) for the argument list and behavior.
- **Core modules**: Implementation lives under the `fingerprint/` package: `executors.py`, `collectors/`, `output.py`, and `evidence.py`.
- **Report builder**: The JSON report is created by `output.build_report()` and written by `output.write_report()`; a standalone top-level helper exists at `output.py` in the repository root as well.

**What I Understood / Assumptions**
- **Design**: The project runs a series of commands (local/remote/container) to collect OS and software information and assembles them into a timestamped JSON report.
- **Authentication**: Remote password auth is used by the `RemoteExecutor` via `sshpass`. If you prefer key-based auth, update the executor to use `ssh -i /path/to/key` or use an SSH agent.
- **Docker flow**: `DockerExecutor` attempts to run a container, expose an SSH port, and connect back to it. This requires an image that runs an SSH server.

**Files of interest**
- **CLI**: [fingerprint/cli.py](fingerprint/cli.py)
- **Executors**: [fingerprint/executors.py](fingerprint/executors.py)
- **Collectors**: [fingerprint/collectors/os_collector.py](fingerprint/collectors/os_collector.py) and [fingerprint/collectors/software_collector.py](fingerprint/collectors/software_collector.py)
- **Report output**: [output.py](output.py)
- **Requirements**: [requirements.txt](requirements.txt)

