# Data Sources and Provenance

## Electoral data
Primary election inputs are IEC Local Government Election detailed results for 2000, 2006, 2011, 2016 and 2021. The pipeline reconstructs turnout, PR party shares and competition measures from the raw files.

## Demographic data
Municipality-level Census 2011 and Census 2022 variables are used as the historical/current demographic anchors available in the project. A province-level census file is retained separately and is not silently treated as municipality-level evidence.

## Provenance principle
Raw files remain unchanged. Each notebook writes processed outputs into a phase-specific directory. Derived/interpolated fields are labelled and documented. Final claims should be traceable to a notebook and processed output.
