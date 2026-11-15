"""Scénario 4 : requête trop large, beaucoup de bruit.

L'utilisateur VOIT la faible qualité (alertes) et PEUT resserrer le corpus (filtres).
"""

from __future__ import annotations

from datetime import date

import pytest

from tracewatch.collecte.commun import Document, charger_profil, enregistrer
from tracewatch.db import get_connection, init_db
from tracewatch.normalisation.clusters import executer as regrouper
from tracewatch.scoring.qualite_corpus import Filtre, calculer_scores, evaluer, filtrer

PROFIL = charger_profil()

PERTINENTS = [
    ("publication", "Coding agents on SWE-bench Verified overestimate real issue resolution",
     "We evaluate LLM agents and coding agents on SWE-bench and find benchmark contamination."),
    ("independant", "Independent evaluation of autonomous agents on WebArena",
     "Our agent benchmark replication of WebArena shows lower success rates for LLM agents."),
    ("benchmark", "SWE-bench Verified : Agent X (55 %)",
     "Agent X resolved 55% of SWE-bench Verified tasks. Verified by the SWE-bench team: yes."),
    ("depot", "Coding agent deleted files during SWE-bench run",
     "The coding agent removed the repository while solving a SWE-bench issue."),
]
BRUIT = [
    "Our new office opens in Lisbon", "Quarterly earnings call transcript", "Holiday gift guide",
    "New pricing for enterprise customers", "Meet the team behind our mobile app",
    "Improving image generation for marketing", "How we hire designers", "Customer story: a bakery",
    "Data center sustainability report", "Introducing dark mode",
]


@pytest.fixture
def conn(tmp_path):
    with get_connection(init_db(tmp_path / "t.db")) as c:
        for i, (fam, titre, texte) in enumerate(PERTINENTS):
            enregistrer(c, Document(url=f"https://ok.org/{i}", title=titre, text=texte,
                                    source_family=fam, source_name="test", published_date="2026-06-01"))
        for i, titre in enumerate(BRUIT):
            enregistrer(c, Document(url=f"https://bruit.org/{i}", title=titre,
                                    text=f"{titre}. A short corporate announcement with no technical content.",
                                    source_family="fournisseur", source_name="blog", published_date="2026-06-01"))
        regrouper(c, PROFIL)
        calculer_scores(c, PROFIL, reference=date(2026, 11, 15))
        yield c


def test_le_bruit_est_visible(conn):
    q = evaluer(filtrer(conn), PROFIL)
    assert q.documents == 14
    assert q.part_bruit == pytest.approx(10 / 14, abs=0.01)
    assert any("bruit" in a.lower() for a in q.alertes)
    assert q.niveau in ("moyen", "faible")


def test_resserrer_par_pertinence_supprime_le_bruit(conn):
    seuil = PROFIL["qualite_corpus"]["seuil_pertinence_min"]
    docs = filtrer(conn, Filtre(pertinence_min=seuil))
    assert {d["url"] for d in docs} == {f"https://ok.org/{i}" for i in range(len(PERTINENTS))}
    q = evaluer(docs, PROFIL)
    assert q.part_bruit == 0
    assert q.niveau == "bon"
    assert q.alertes == []


def test_trop_resserrer_est_signale(conn):
    """Un filtre trop strict ne doit pas passer inaperçu."""
    q = evaluer(filtrer(conn, Filtre(familles=["publication"])), PROFIL)
    assert any("famille" in a for a in q.alertes)
    q = evaluer(filtrer(conn, Filtre(pertinence_min=0.99)), PROFIL)
    assert q.niveau == "vide" and q.alertes


def test_autres_filtres(conn):
    assert len(filtrer(conn, Filtre(familles=["benchmark", "depot"]))) == 2
    assert len(filtrer(conn, Filtre(contient="WebArena"))) == 1
    assert len(filtrer(conn, Filtre(date_min="2027-01-01"))) == 0
    assert len(filtrer(conn, Filtre(un_par_travail=True))) == 14  # aucun doublon ici
