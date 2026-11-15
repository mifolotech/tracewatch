"""Étape 9 : le jeu de démo se reconstruit SANS clé ni réseau, et donne toujours le même résultat."""

from __future__ import annotations

import json

import pytest
import requests

from tracewatch import demo
from tracewatch.collecte.commun import charger_profil
from tracewatch.db import get_connection
from tracewatch.rapport.tracabilite import verifier_tracabilite

PROFIL = charger_profil()


@pytest.fixture
def hors_ligne(monkeypatch):
    """Toute tentative d'accès réseau fait échouer le test."""
    def interdit(*_a, **_k):
        raise AssertionError("La démo ne doit pas utiliser le réseau")
    monkeypatch.setattr(requests.Session, "request", interdit)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)


def construire(tmp_path, nom):
    return demo.construire(PROFIL, chemin_base=tmp_path / f"{nom}.db", dossier_rapports=tmp_path / nom)


def test_la_demo_est_versionnee():
    assert demo.DOCUMENTS.exists() and demo.MANIFESTE.exists()
    assert any(demo.CACHE_DEMO.glob("*.json")), "réponses LLM de la démo manquantes"


def test_demo_complete_sans_cle_ni_reseau(tmp_path, hors_ligne):
    r = construire(tmp_path, "a")
    s = r.synthese.stats
    manifeste = json.loads(demo.MANIFESTE.read_text(encoding="utf-8"))
    assert s["documents"] == manifeste["documents"]
    assert s["familles"] >= PROFIL["qualite_corpus"]["familles_min"]
    assert s["travaux"] < s["documents"]  # la démo contient des doublons (scénario 1)
    assert s["verifiees"] > 0, "le cache de la démo ne correspond plus au profil : relancer --exporter"
    with get_connection(tmp_path / "a.db") as conn:
        assert verifier_tracabilite(r.markdown, conn) == []


def test_demo_reproductible(tmp_path, hors_ligne):
    a, b = construire(tmp_path, "a"), construire(tmp_path, "b")
    assert a.markdown == b.markdown
    assert a.synthese.decision == b.synthese.decision
