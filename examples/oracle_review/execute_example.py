"""Execute exact example cells in a fresh Python process and retain evidence.

This runner does not claim Jupyter/Colab UI execution. Install IPython in the
host first; all scientific dependencies are isolated by the notebook setup.
"""
import argparse
import hashlib
import json
import platform
import time
import traceback
from pathlib import Path


def execute(notebook, report_path):
    path = Path(notebook).resolve()
    book = json.loads(path.read_text())
    namespace = {"__name__": "__main__"}
    cells = []
    started = time.monotonic()
    for index, cell in enumerate(book["cells"]):
        if cell["cell_type"] != "code":
            continue
        print(f"Executing code cell {index}", flush=True)
        before = time.monotonic()
        try:
            exec(compile("".join(cell["source"]), f"<notebook-cell-{index}>", "exec"), namespace)
            cells.append({"cell": index, "passed": True, "seconds": round(time.monotonic() - before, 3)})
        except Exception as exc:
            cells.append({"cell": index, "passed": False, "error": str(exc)})
            traceback.print_exc()
            break
    expected = sum(c["cell_type"] == "code" for c in book["cells"])
    report = {
        "runtime_kind": "fresh Python process, not hosted Colab/Jupyter UI",
        "host_python": platform.python_version(),
        "notebook_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "scientific_code_commit": namespace.get("CODE_REF"),
        "data_version": namespace.get("DATA_VERSION"),
        "expected_code_cells": expected, "cells": cells,
        "passed": len(cells) == expected and all(x["passed"] for x in cells),
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "scope": "one real case; same-code deterministic repeat; not full-resource or human review",
        "hosted_colab": "not_evaluated", "evidence_zip": namespace.get("export"),
    }
    target = Path(report_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if not report["passed"]:
        raise RuntimeError("Example execution failed; retain the report and full diagnostic.")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--notebook", default="notebooks/Oracle_Atlas_Colab_Example.ipynb")
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    execute(args.notebook, args.report)
