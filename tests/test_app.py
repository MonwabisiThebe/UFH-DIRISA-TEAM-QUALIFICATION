"""Smoke test: every dashboard page renders without exceptions."""
from pathlib import Path

import pytest

from src import config as C

APP = Path(__file__).resolve().parents[1] / "app" / "app.py"
PAGES = ["Overview", "1. Participation", "2. Competition", "3. Socioeconomic context", "4. Historical validation",
         "5. 2026 scenarios", "6. Limitations", "Municipality profile", "Methods and QC", "Download the data"]
pytestmark = pytest.mark.skipif(not (C.DIRS["phase6"] / "municipality_scenarios_2026.csv").exists(),
                                reason="run the notebooks first")


@pytest.mark.parametrize("page", PAGES)
def test_page_renders(page):
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(str(APP), default_timeout=120).run()
    at.sidebar.radio[0].set_value(page).run()
    assert not at.exception, [e.value for e in at.exception]
