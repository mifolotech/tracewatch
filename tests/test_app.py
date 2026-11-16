"""Tableau de bord : s'ouvre sans erreur, y compris pour un nouvel utilisateur dont la base est vide."""

from __future__ import annotations

from pathlib import Path

import pytest

AppTest = pytest.importorskip("streamlit.testing.v1").AppTest
APP = str(Path(__file__).parents[1] / "src" / "tracewatch" / "app" / "streamlit_app.py")


@pytest.fixture(autouse=True)
def demo_temporaire(tmp_path, monkeypatch):
    """La démo construite par les tests va dans un dossier temporaire : le projet n'est jamais modifié."""
    from tracewatch import demo
    monkeypatch.setattr(demo, "BASE_DEMO", tmp_path / "demo" / "tracewatch_demo.db")
    monkeypatch.setattr(demo, "RAPPORTS_DEMO", tmp_path / "demo" / "rapports")


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


def test_reconstruire_la_demo_depuis_le_tableau_de_bord():
    """Bug trouvé sous Windows : la base démo restait verrouillée (connexions jamais fermées)."""
    at = AppTest.from_file(APP, default_timeout=300).run()
    at.sidebar.radio[0].set_value("Démo (figée)").run()
    bouton = next(b for b in at.sidebar.button if b.label == "Reconstruire la démo")
    bouton.click().run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.metric[0].value != "0"


def test_les_connexions_se_ferment(tmp_path):
    import sqlite3

    from tracewatch.db import get_connection, init_db
    chemin = init_db(tmp_path / "t.db")
    with get_connection(chemin) as c:
        c.execute("SELECT 1")
    with pytest.raises(sqlite3.ProgrammingError):  # connexion fermée
        c.execute("SELECT 1")
    chemin.unlink()  # sous Windows, échouait si la connexion restait ouverte
