"""Run the full analysis pipeline from raw data to 2026 scenarios.

Executes the six notebooks in order (each saves its outputs and figures), then
runs the submission validator and the test suite, and finally regenerates
data/processed/verification/headline_metrics.csv and docs/VERIFICATION_REPORT.md.

Usage
-----
    python run_pipeline.py              # run notebooks 01-06, validate, test
    python run_pipeline.py --from 4     # resume from notebook 04
    python run_pipeline.py --check-only # only run the validator and tests
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NOTEBOOKS = sorted((ROOT / "notebooks").glob("0[1-6]_*.ipynb"))


def run_notebook(path: Path, timeout: int = 1800) -> None:
    import nbformat
    from nbclient import NotebookClient

    nb = nbformat.read(path, as_version=4)
    client = NotebookClient(nb, timeout=timeout, kernel_name="python3",
                            resources={"metadata": {"path": str(path.parent)}})
    client.execute()
    nbformat.write(nb, path)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from", dest="start", type=int, default=1, help="first notebook number to run")
    ap.add_argument("--check-only", action="store_true", help="skip notebooks; validate and test only")
    args = ap.parse_args()

    if not args.check_only:
        for nb in NOTEBOOKS:
            if int(nb.name[:2]) < args.start:
                continue
            t0 = time.time()
            print(f"Running {nb.name} ...", flush=True)
            run_notebook(nb)
            print(f"  done in {time.time() - t0:.0f}s")

    print("Validating submission outputs ...")
    v = subprocess.run([sys.executable, str(ROOT / "src" / "validation" / "validate_submission.py")],
                       cwd=ROOT, capture_output=True, text=True)
    print(v.stdout)
    if v.returncode:
        return v.returncode
    n_checks = v.stdout.count("PASS ")
    print("Running tests ...")
    t = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=ROOT,
                       capture_output=True, text=True)
    print(t.stdout[-600:])
    last = [ln for ln in t.stdout.splitlines() if "passed" in ln or "failed" in ln]
    summary = f"validator {n_checks} checks passed; pytest: {last[-1].strip() if last else 'no summary'}"
    print("Writing headline metrics and verification report ...")
    subprocess.call([sys.executable, str(ROOT / "src" / "validation" / "headline_metrics.py"), summary], cwd=ROOT)
    return t.returncode


if __name__ == "__main__":
    sys.exit(main())
