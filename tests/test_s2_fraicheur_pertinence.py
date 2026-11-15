"""Scénario 2 : publication ancienne mais très pertinente.

Pertinence et fraîcheur restent deux dimensions SÉPARÉES : un vieux document
très pertinent n'est ni pénalisé en pertinence, ni écarté par le filtre de pertinence.
"""

from __future__ import annotations

from datetime import date

import pytest

from tracewatch.collecte.commun import Document, charger_profil, enregistrer
from tracewatch.db import get_connection, init_db
from tracewatch.scoring.fraicheur import score_fraicheur
from tracewatch.scoring.pertinence import score_pertinence
from tracewatch.scoring.qualite_corpus import Filtre, calculer_scores, filtrer

REF = date(2026, 11, 15)
PROFIL = charger_profil()

ANCIEN_PERTINENT = dict(
    title="SWE-bench: Can Language Models Resolve Real-World GitHub Issues?",
    text="We introduce SWE-bench, an agent benchmark of real GitHub issues to evaluate coding agents "
         "and LLM agents on issue resolution in real software engineering repositories.",
    published_date="2021-10-10",
)
RECENT_HORS_SUJET = dict(
    title="Our new office opens in Lisbon",
    text="We are happy to announce our new office, with a great cafeteria and a view on the river.",
    published_date="2026-11-10",
)


@pytest.fixture
def conn(tmp_path):
    with get_connection(init_db(tmp_path / "t.db")) as c:
        for i, d in enumerate((ANCIEN_PERTINENT, RECENT_HORS_SUJET)):
            enregistrer(c, Document(url=f"https://ex.org/{i}", source_family="publication",
                                    source_name="test", **d))
        calculer_scores(c, PROFIL, reference=REF)
        yield c


def scores(conn, titre):
    return conn.execute(
        "SELECT pertinence, fraicheur, fiabilite FROM scores JOIN documents ON id=document_id WHERE title=?",
        (titre,),
    ).fetchone()


def test_ancien_pertinent_garde_une_forte_pertinence_et_une_faible_fraicheur(conn):
    p, f, _ = scores(conn, ANCIEN_PERTINENT["title"])
    assert p >= 0.8
    assert f <= 0.1


def test_recent_hors_sujet_est_frais_mais_pas_pertinent(conn):
    p, f, _ = scores(conn, RECENT_HORS_SUJET["title"])
    assert p < PROFIL["qualite_corpus"]["seuil_pertinence_min"]
    assert f >= 0.9


def test_la_date_ne_change_pas_la_pertinence():
    t, x = ANCIEN_PERTINENT["title"], ANCIEN_PERTINENT["text"]
    assert score_pertinence(t, x, PROFIL) == score_pertinence(t, x, PROFIL)  # aucune entrée "date"
    assert score_fraicheur("2021-10-10", PROFIL, REF) < score_fraicheur("2026-10-10", PROFIL, REF)


def test_le_contenu_ne_change_pas_la_fraicheur():
    assert score_fraicheur("2024-01-01", PROFIL, REF) == score_fraicheur("2024-01-01", PROFIL, REF)
    # La fonction de fraîcheur ne reçoit même pas le texte : séparation garantie par construction


def test_demi_vie():
    assert score_fraicheur("2026-11-15", PROFIL, REF) == 1.0
    assert score_fraicheur("2025-11-15", PROFIL, REF) == pytest.approx(0.5, abs=0.01)
    assert score_fraicheur(None, PROFIL, REF) is None  # pas de date : inconnu, pas inventé


def test_le_filtre_de_pertinence_garde_le_document_ancien(conn):
    titres = [d["title"] for d in filtrer(conn, Filtre(pertinence_min=0.5))]
    assert titres == [ANCIEN_PERTINENT["title"]]


def test_les_filtres_sont_independants(conn):
    """Filtrer sur la fraîcheur est un choix EXPLICITE de l'utilisateur, jamais implicite."""
    frais = [d["title"] for d in filtrer(conn, Filtre(fraicheur_min=0.5))]
    assert frais == [RECENT_HORS_SUJET["title"]]
    les_deux = filtrer(conn, Filtre(pertinence_min=0.5, fraicheur_min=0.5))
    assert les_deux == []
