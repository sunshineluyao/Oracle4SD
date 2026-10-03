"""Set up the immutable one-case tutorial without relying on host ensurepip.

Only standard-library imports are needed in the notebook kernel. Scientific
dependencies go into a separate Python 3.12 environment. This is setup and
case replay, not reproduction of the complete cross-protocol data resource.
"""

import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO_URL = "https://github.com/virusLuke3/Oracle4SD-Atlas.git"
CODE_REF = "5ee23c5ee76394233b26c89c1ebd9acae7328aa0"
DATA_VERSION = "uma-public-rpc-case-v1"
UV_VERSION = "0.12.19"


def command(args, cwd=None, extra_env=None, timeout=300):
    env = os.environ.copy()
    env.update({"MPLBACKEND": "Agg", "UV_NO_PROGRESS": "1"})
    env.update(extra_env or {})
    result = subprocess.run(
        [str(a) for a in args], cwd=cwd, env=env, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout,
    )
    if result.returncode:
        raise RuntimeError(
            f"Setup/stage failed (exit {result.returncode}): {args!r}\n"
            f"stdout:\n{result.stdout[-6000:]}\nstderr:\n{result.stderr[-6000:]}\n"
            "Keep this diagnostic. Do not continue with partly generated outputs."
        )
    return result.stdout


def scientific_python_selector(version_info=None, executable=None):
    """Use a compatible host, otherwise ask uv for managed Python 3.12."""
    version_info = version_info or sys.version_info
    executable = executable or sys.executable
    return executable if tuple(version_info[:2]) == (3, 12) else "3.12"


def bootstrap():
    started = time.monotonic()
    work = Path(tempfile.mkdtemp(prefix="oracle-atlas-example-"))
    repo = work / "repository"
    if shutil.which("git") is None:
        raise RuntimeError("Git is required. Colab provides it; install Git for a local run.")
    command(["git", "clone", "--quiet", "--no-checkout", REPO_URL, repo])
    command(["git", "checkout", "--quiet", "--detach", CODE_REF], cwd=repo)
    actual = command(["git", "rev-parse", "HEAD"], cwd=repo).strip()
    if actual != CODE_REF:
        raise RuntimeError(f"Code identity mismatch: expected {CODE_REF}, got {actual}")

    # Installing into a temporary target does not upgrade the notebook kernel.
    # uv creates/seeds an environment without calling the host's ensurepip.
    tools_dir = work / "setup-tools"
    command([
        sys.executable, "-m", "pip", "install", "--disable-pip-version-check",
        "--target", tools_dir, f"uv=={UV_VERSION}",
    ])
    uv_env = {"PYTHONPATH": str(tools_dir)}
    uv = [sys.executable, "-m", "uv"]
    env = work / "scientific-environment"
    selector = scientific_python_selector()
    # If the host changed to another Python minor version, uv installs a
    # managed compatible interpreter. No sudo or system-package edits are used.
    command(uv + ["venv", "--python", selector, "--seed", env], extra_env=uv_env)
    python = env / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    version = command([python, "-c", "import sys; print('.'.join(map(str,sys.version_info[:2])))"]).strip()
    if version != "3.12":
        raise RuntimeError(f"Scientific environment must be Python 3.12; got {version}")
    print(command([
        python, "-m", "pip", "install", "--disable-pip-version-check",
        "-r", repo / "requirements.txt",
    ])[-1200:])
    command([python, "-m", "pip", "check"])
    command([python, "-c", "import pandas, pyarrow, eth_abi, eth_utils, matplotlib, jsonschema"])
    run = repo / "runs/tutorial-example"
    run.mkdir(parents=True)
    cfg_bytes = (repo / "configs/project.json").read_bytes()
    identity = {
        "host_python": platform.python_version(),
        "scientific_python_minor": version,
        "python_selector": selector,
        "setup_tool": f"uv=={UV_VERSION}",
        "code_commit": actual,
        "data_version": DATA_VERSION,
        "configuration_sha256": hashlib.sha256(cfg_bytes).hexdigest(),
        "setup_seconds": round(time.monotonic() - started, 3),
        "scope": "one real UMA case; not the full candidate dataset",
    }
    (work / "setup_identity.json").write_text(json.dumps(identity, indent=2) + "\n")
    print(json.dumps(identity, indent=2))
    return {"WORK": work, "REPO": repo, "PYTHON": python, "RUN": run, "ENV": env}


if __name__ == "__main__":
    globals().update(bootstrap())
