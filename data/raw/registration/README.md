# IEC 2026 voter registration snapshot (optional)

The pipeline runs without this file. If the team extracts municipal registration figures from the IEC's Voter
Registration Statistics dashboard (https://www.elections.org.za/pw/StatsData/Voter-Registration-Statistics), save them
as `ec_registration_2026.csv` in this folder using the columns of `TEMPLATE_ec_registration_2026.csv`, then run
`python run_pipeline.py --from 2`.

Rules:
- One row per analytical municipality (33 rows, codes as in the template). Only `MuniCode` and `RegisteredVoters` are
  required; the age and gender columns are optional.
- Record the extraction date and URL. Do not estimate or fill missing values.
- The snapshot is used only as 2026 context (expected votes cast in scenarios, registration profile). It is **not** used in
  historical validation, because comparable snapshots for earlier elections are not in the repository.
