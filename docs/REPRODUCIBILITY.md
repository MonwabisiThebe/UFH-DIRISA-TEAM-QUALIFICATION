# Reproducibility

## Environment

Python 3.10 or newer. Install with `pip install -r requirements.txt` (tested with Python 3.12, pandas 3.0, NumPy 2.4,
scikit-learn 1.8, statsmodels 0.15, Matplotlib 3.10, Shapely 2.1, Streamlit 1.64, Plotly 7.1). Each notebook prints the
exact package versions it ran with in its final cell.

## One command

```bash
python run_pipeline.py            # notebooks 01-06, then validation and tests
python run_pipeline.py --from 4   # resume from notebook 04
python run_pipeline.py --check-only
```

## Order and dependencies

```
01 elections ──► 02 demographics ──► 03 master panel ──► 04 turnout model ─┐
       │                                     │                              ├─► 06 scenarios ──► dashboard
       └──────────────── geojson ────────────┴──────► 05 party model ───────┘
```

Each notebook reads only files written by earlier notebooks (or raw inputs) and writes into its own folder under
`data/processed/`. Figures go to `reports/figures/phaseN/`.

## Determinism

All random forests use `random_state=42`; there are no random splits. Re-running reproduces identical outputs.

## Checks

- Each notebook stops on a failed quality-control gate.
- `src/validation/validate_submission.py`: end-to-end output checks (registered voters vs IEC, leakage rules,
  selection on validation folds only, coherent compositions, map geography).
- `pytest`: unit tests on core calculations, output-contract tests, and a smoke test of every dashboard page.

## Adding the 2026 registration snapshot

Save `data/raw/registration/ec_registration_2026.csv` (see the template in that folder), then run
`python run_pipeline.py --from 2`.
