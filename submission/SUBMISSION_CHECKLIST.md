# Submission checklist: DIRISA SDC 2026 Teams Qualification

**Deadline: 08:00, 5 October 2026.** Upload to NextCloud (https://sdcdata.dirisa.ac.za/index.php/login) and email the share
link to Ms Boitshepo Sebusho (bsebusho@csir.co.za).

## Required deliverables

| Deliverable | Where | Status |
|---|---|---|
| Problem statement | `README.md` (Problem statement), slide 2 | Done |
| Notebook / codebase, data to model | `notebooks/01-06`, `src/`, `run_pipeline.py` | Done; runs end to end |
| Trained model | Selected methods saved in `data/processed/models/phase4-5/`; refit in Notebook 06 | Done |
| Deployed tool | `streamlit run app/app.py` (optionally deploy to Streamlit Community Cloud) | Done locally; deployment optional |
| Slides with references | `presentation/DIRISA_UFH_Presentation.pptx` | Done |
| 15-minute video, every member presents | Script: `presentation/PRESENTATION_SCRIPT.md` | **Team to record** |

## Team actions before upload

- [ ] Run `python run_pipeline.py` on your own machine and confirm the final line shows all tests passed.
- [ ] Open the dashboard (`streamlit run app/app.py`) and click through every page.
- [ ] Census provenance: if anyone knows which Stats SA tables produced `clean_census.csv`, record them in
      `docs/DATA_SOURCES.md` section 3; otherwise leave the limitation statement as is.
- [ ] Check every reference URL and add access dates (`docs/DATA_SOURCES.md`, slide 20).
- [ ] Optional: extract the IEC 2026 registration snapshot into `data/raw/registration/ec_registration_2026.csv`
      (template provided) and rerun `python run_pipeline.py --from 2`; then rebuild the slides
      (`python presentation/build/export_deck_data.py`, `node presentation/build/build_deck.js`).
- [ ] Replace "Presenter 1-4" in the script with names; add team member names to slide 1 if wanted.
- [ ] Record the video (15 minutes, every member presenting); export as MP4.
- [ ] Optional: deploy the dashboard and add its URL to the README and slide 17.
- [ ] Upload the repository ZIP, slides and video to NextCloud; create a share link.
- [ ] Email the share link to bsebusho@csir.co.za before 08:00 on 5 October 2026.

## Rubric map

| Criterion | Evidence |
|---|---|
| Data cleaning, EDA, feature engineering | Notebooks 01-03; IEC external validation; QC gates; within-election analysis |
| Model selection and evaluation | Notebooks 04-05; rolling-origin validation; locked 2021 test; baselines |
| Interpretation and honest limitations | Absolute vs relative error; scenarios not forecasts; `docs/LIMITATIONS.md` |
| Deployment | Streamlit dashboard with maps, scenario explorer, downloads |
| Code documentation | `README.md`, `docs/`, docstrings, `docs/VERIFICATION_REPORT.md` |
| Presentation | 20-slide deck with native charts, maps, dashboard screenshots, references |
| Innovation | Level-vs-relative decomposition; evidence/assumption separation in the dashboard |
