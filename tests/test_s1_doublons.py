"""Scénario 1 : même information republiée sur plusieurs sites.

Elle ne doit PAS compter comme plusieurs confirmations indépendantes.
On construit un petit corpus dont on connaît la bonne réponse.
"""

from __future__ import annotations

import pytest

from tracewatch.collecte.commun import Document, charger_profil, enregistrer
from tracewatch.db import get_connection, init_db
from tracewatch.normalisation.clusters import executer, sources_independantes
from tracewatch.normalisation.schema import url_canonique

ETUDE = (
    "We find that coding agents evaluated on SWE-bench Verified frequently produce patches "
    "that pass the provided tests but are semantically incorrect. After manual review of "
    "500 resolved issues, 29.6 percent of accepted patches were wrong or incomplete, which "
    "means published leaderboard scores overestimate real resolution rates by a large margin."
)


def doc(url, titre, texte, famille="independant", date="2025-03-10", **kw) -> Document:
    return Document(url=url, title=titre, text=texte, source_family=famille,
                    source_name=kw.pop("source", "test"), published_date=date, **kw)


@pytest.fixture
def conn(tmp_path):
    chemin = init_db(tmp_path / "test.db")
    with get_connection(chemin) as c:
        yield c


@pytest.fixture
def corpus(conn):
    docs = {
        # Le travail original : la prépublication arXiv
        "original": doc("https://arxiv.org/abs/2503.11111v2", "Are Solved Issues in SWE-bench Really Solved?",
                        ETUDE, famille="publication", date="2025-03-01", arxiv_id="2503.11111"),
        # Même article via OpenAlex : DOI arXiv, autre URL
        "openalex": doc("https://doi.org/10.48550/arXiv.2503.11111", "Are Solved Issues in SWE-bench Really Solved?",
                        ETUDE, famille="publication", date="2025-03-02", doi="10.48550/arXiv.2503.11111"),
        # Un blog relaie l'étude en reprenant le résumé presque mot pour mot
        "blog": doc("https://blog.example.com/swe-bench-patches", "New study: SWE-bench patches often wrong",
                    "New study. " + ETUDE),
        # Le même billet partagé avec des paramètres de pistage
        "blog_partage": doc("https://www.blog.example.com/swe-bench-patches/?utm_source=twitter&utm_medium=social",
                            "New study: SWE-bench patches often wrong", "New study. " + ETUDE, date="2025-03-12"),
        # Un site de presse copie le texte à l'identique
        "presse": doc("https://news.example.org/ai/agents-overrated", "Coding agents overrated, says study",
                      ETUDE, date="2025-03-15"),
        # Un travail DIFFÉRENT sur un sujet voisin : doit rester séparé
        "autre": doc("https://metr.example.org/time-horizons", "Measuring AI ability to complete long tasks",
                     "We measure the length of software tasks that frontier models can complete autonomously "
                     "with fifty percent reliability, and find this horizon has been doubling every seven months.",
                     date="2025-03-19"),
        # Deux entrées de classement au même gabarit : résultats DIFFÉRENTS, à ne pas fusionner
        "lb1": doc("https://github.com/SWE-bench/experiments/tree/main/evaluation/verified/a",
                   "SWE-bench Verified : Agent A (60 %)",
                   "Agent A resolved 60% of SWE-bench Verified tasks. Agent: A by Org1. Model: M by Org2. "
                   "Submitted on 2025-01-01. Verified by the SWE-bench team: yes.", famille="benchmark"),
        "lb2": doc("https://github.com/SWE-bench/experiments/tree/main/evaluation/verified/b",
                   "SWE-bench Verified : Agent B (61 %)",
                   "Agent B resolved 61% of SWE-bench Verified tasks. Agent: B by Org1. Model: M by Org2. "
                   "Submitted on 2025-01-01. Verified by the SWE-bench team: yes.", famille="benchmark"),
    }
    ids = {}
    for cle, d in docs.items():
        assert enregistrer(conn, d)
        ids[cle] = conn.execute("SELECT id FROM documents WHERE url=?", (d.url,)).fetchone()[0]
    executer(conn, charger_profil())
    return ids


REPUBLICATIONS = ["original", "openalex", "blog", "blog_partage", "presse"]


def cluster_de(conn, doc_id):
    return conn.execute("SELECT cluster_id FROM documents WHERE id=?", (doc_id,)).fetchone()[0]


def test_republications_comptent_pour_une_seule_source(conn, corpus):
    """5 documents sur la même étude = 1 seule confirmation indépendante."""
    ids = [corpus[k] for k in REPUBLICATIONS]
    assert len({cluster_de(conn, i) for i in ids}) == 1
    assert sources_independantes(conn, ids) == 1


def test_original_est_le_plus_ancien(conn, corpus):
    cid = cluster_de(conn, corpus["original"])
    original, taille = conn.execute(
        "SELECT document_original_id, taille FROM clusters WHERE cluster_id=?", (cid,)
    ).fetchone()
    assert original == corpus["original"]
    assert taille == len(REPUBLICATIONS)


def test_travail_different_reste_separe(conn, corpus):
    assert cluster_de(conn, corpus["autre"]) != cluster_de(conn, corpus["original"])
    assert sources_independantes(conn, [corpus["original"], corpus["presse"], corpus["autre"]]) == 2


def test_entrees_de_classement_au_meme_gabarit_non_fusionnees(conn, corpus):
    assert cluster_de(conn, corpus["lb1"]) != cluster_de(conn, corpus["lb2"])


def test_relancer_donne_le_meme_resultat(conn, corpus):
    avant = conn.execute("SELECT COUNT(*) FROM clusters").fetchone()[0]
    executer(conn, charger_profil())
    assert conn.execute("SELECT COUNT(*) FROM clusters").fetchone()[0] == avant
    assert sources_independantes(conn, [corpus[k] for k in REPUBLICATIONS]) == 1


@pytest.mark.parametrize("a, b", [
    ("https://www.Example.com/post/?utm_source=x&id=3", "https://example.com/post?id=3"),
    ("http://arxiv.org/abs/2310.06770v3", "https://arxiv.org/pdf/2310.06770"),
    ("https://doi.org/10.1145/ABC", "https://dx.doi.org/10.1145/abc"),
])
def test_url_canonique(a, b):
    assert url_canonique(a) == url_canonique(b)


def test_url_canonique_garde_le_fragment():
    """Le classement WebArena distingue ses entrées par le fragment (#...)."""
    assert url_canonique("https://x.org/sheet#model-a") != url_canonique("https://x.org/sheet#model-b")
