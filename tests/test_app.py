"""Tableau de bord : s'ouvre sans erreur, y compris pour un nouvel utilisateur dont la base est vide."""

from __future__ import annotations

from pathlib import Path

import pytest

AppTest = pytest.importorskip("streamlit.testing.v1").AppTest
APP = str(Path(__file__).parents[1] / "src" / "tracewatch" / "app" / "streamlit_app.py")


@pytest.fixture
def base_vide(tmp_path, monkeypatch):
    monkeypatch.setenv("TRACEWATCH_DB", str(tmp_path / "vide.db"))


def test_premiere_ouverture_bascule_sur_la_demo(base_vide):
    at = AppTest.from_file(APP, default_timeout=180).run()
    assert not at.exception
    assert at.sidebar.radio[0].value == "Démo (figée)"
    assert at.metric[0].value != "0"


def test_base_vide_affiche_un_message_clair(base_vide):
    at = AppTest.from_file(APP, default_timeout=180).run()
    at.sidebar.radio[0].set_value("Base réelle").run()
    assert not at.exception
    assert any("base réelle est vide" in i.value for i in at.info)
