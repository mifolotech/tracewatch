"""Étape 8 : rapport complet, décision proportionnée, révision avec historique."""

from __future__ import annotations

import pytest

from tracewatch.collecte.commun import Document, charger_profil, enregistrer
from tracewatch.db import get_connection, init_db
from tracewatch.normalisation.clusters import executer as regrouper
from tracewatch.rapport.generateur import generer_rapport
from tracewatch.rapport.revision import historique
from tracewatch.rapport.tracabilite import verifier_tracabilite

PROFIL = charger_profil()


def doc(conn, i, famille, texte):
    url = f"https://src{i}.example.org/doc"
    enregistrer(conn, Document(url=url, title=f"Source {i}", text=texte, source_family=famille,
                               source_name=f"Source {i}", published_date="2026-05-01"))
    return conn.execute("SELECT id FROM documents WHERE url=?", (url,)).fetchone()[0]


def claim(conn, doc_id, texte, citation, categorie, theme, position):
    conn.execute("""INSERT INTO claims (document_id, texte, citation, citation_verifiee, categorie, theme, position)
                    VALUES (?, ?, ?, 1, ?, ?, ?)""", (doc_id, texte, citation, categorie, theme, position))


@pytest.fixture
def conn(tmp_path):
    with get_connection(init_db(tmp_path / "t.db")) as c:
        textes = [f"Unique finding number {i} about coding agents and benchmark number {i * 7}." for i in range(8)]
        ids = [doc(c, i, "publication" if i < 6 else "fournisseur", t) for i, t in enumerate(textes)]
        regrouper(c, PROFIL)
        # 2 sources optimistes sur les benchmarks, 2 critiques sur leur validité -> pilote contrôlé
        claim(c, ids[0], "L'agent A atteint 70 % sur SWE-bench.", textes[0], "fait", "performance_benchmark", "optimiste")
        claim(c, ids[1], "L'agent B atteint 65 % sur SWE-bench. Il bat l'état de l'art.", textes[1], "fait",
              "performance_benchmark", "optimiste")
        claim(c, ids[2], "Les tests du benchmark sont souvent défaillants.", textes[2], "lacune", "validite_benchmark", "critique")
        claim(c, ids[3], "Les scores sont gonflés par la contamination.", textes[3], "fait", "validite_benchmark", "critique")
        claim(c, ids[4], "Un agent a supprimé des fichiers en production.", textes[4], "risque", "fiabilite_securite", "critique")
        claim(c, ids[6], "Notre agent est prêt pour la production.", textes[6], "interpretation", "usage_reel", "optimiste")
        c.commit()
        yield c, ids, textes


def test_rapport_complet_et_tracable(conn, tmp_path):
    conn, _, _ = conn
    r = generer_rapport(conn, PROFIL, dossier=tmp_path / "rapports")
    for section in ("Question de décision", "## 1. Décision recommandée", "## 2. Synthèse par thème",
                    "## 3. Faits établis", "## 4. Contradictions", "## 5. Incertitudes et lacunes",
                    "## 6. Risques", "## 7. Points à surveiller", "## Preuves"):
        assert section in r.markdown
    assert verifier_tracabilite(r.markdown, conn) == []
    assert r.chemin.exists() and (tmp_path / "rapports" / "dernier_rapport.md").exists()


def test_decision_proportionnee(conn, tmp_path):
    conn, _, _ = conn
    r = generer_rapport(conn, PROFIL, dossier=tmp_path)
    d = r.synthese.decision
    assert d.option == "pilote_controle"  # prometteur (2 sources) + écart documenté (2 sources)
    assert d.confiance == "moyenne"
    # Le fournisseur seul ne fait pas une preuve indépendante en usage réel
    assert r.synthese.themes["usage_reel"].preuve_opt.niveau == "insuffisant"


def test_phrase_a_deux_phrases_toutes_sourcees(conn, tmp_path):
    """L'affirmation de l'agent B contient deux phrases : chacune reçoit sa référence."""
    conn, _, _ = conn
    md = generer_rapport(conn, PROFIL, dossier=tmp_path).markdown
    ligne = next(l for l in md.splitlines() if "L'agent B" in l)
    assert ligne.count("[P2]") == 2


def test_revision_quand_une_preuve_arrive(conn, tmp_path):
    conn, ids, textes = conn
    generer_rapport(conn, PROFIL, motif="premier rapport", dossier=tmp_path)
    assert generer_rapport(conn, PROFIL, dossier=tmp_path).changements == []  # rien n'a changé

    claim(conn, ids[5], "Une troisième étude confirme des tests défaillants.", textes[5], "fait",
          "validite_benchmark", "critique")
    conn.commit()
    r = generer_rapport(conn, PROFIL, motif="nouvelle étude", dossier=tmp_path)
    assert any(c.startswith("theme:validite_benchmark : version 2") for c in r.changements)

    h = historique(conn, "theme:validite_benchmark")
    assert [x["version"] for x in h] == [1, 2]
    assert h[0]["niveau_preuve"] == "moyen" and h[1]["niveau_preuve"] == "fort"  # 2 -> 3 sources
    assert "nouvelle étude" in h[1]["motif"] and "+ P7" in h[1]["motif"]
