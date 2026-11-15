"""Scénario 5 : élément critique du rapport contesté.

On doit retrouver VITE le document original qui le soutient :
phrase du rapport -> [Pn] -> citation exacte -> document cité -> document ORIGINAL.
"""

from __future__ import annotations

import pytest

from tracewatch.collecte.commun import Document, charger_profil, enregistrer
from tracewatch.db import get_connection, init_db
from tracewatch.normalisation.clusters import executer as regrouper
from tracewatch.rapport.tracabilite import (
    annexe_preuves,
    creer_conclusion,
    reference,
    references,
    tracer_conclusion,
    tracer_preuve,
    verifier_tracabilite,
)

PROFIL = charger_profil()

ETUDE = (
    "We manually reviewed 500 patches accepted on SWE-bench Verified. We find that 29.6% of the "
    "patches counted as resolved are incorrect or incomplete, so leaderboard scores overestimate "
    "the real resolution rate of coding agents."
)


def ajouter(conn, url, titre, texte, famille, date):
    enregistrer(conn, Document(url=url, title=titre, text=texte, source_family=famille,
                               source_name=titre, published_date=date))
    return conn.execute("SELECT id FROM documents WHERE url=?", (url,)).fetchone()[0]


def ajouter_claim(conn, doc_id, texte, citation, verifiee=1, position="critique"):
    return conn.execute(
        """INSERT INTO claims (document_id, texte, citation, citation_verifiee, categorie, theme, position)
           VALUES (?, ?, ?, ?, 'fait', 'validite_benchmark', ?)""",
        (doc_id, texte, citation, verifiee, position),
    ).lastrowid


@pytest.fixture
def base(tmp_path):
    with get_connection(init_db(tmp_path / "t.db")) as conn:
        ids = {
            "etude": ajouter(conn, "https://arxiv.org/abs/2503.00001", "Are solved issues really solved?",
                             ETUDE, "publication", "2025-03-01"),
            # Un blog relaie l'étude (même corps de texte) : c'est LUI que le LLM a cité
            "blog": ajouter(conn, "https://blog.example.com/patches", "Study: a third of SWE-bench fixes are wrong",
                            ETUDE, "independant", "2025-03-20"),
            "audit": ajouter(conn, "https://lab.example.org/audit", "Agent audit",
                             "Our audit found that agents broke unrelated tests in 18% of runs.",
                             "independant", "2025-06-01"),
        }
        regrouper(conn, PROFIL)
        p_blog = ajouter_claim(conn, ids["blog"], "29,6 % des correctifs comptés comme résolus sont faux.",
                               "29.6% of the patches counted as resolved are incorrect or incomplete")
        p_audit = ajouter_claim(conn, ids["audit"], "Les agents cassent des tests sans rapport dans 18 % des cas.",
                                "agents broke unrelated tests in 18% of runs")
        p_rejetee = ajouter_claim(conn, ids["audit"], "Affirmation inventée.", "texte absent", verifiee=0)
        texte = (f"Les scores des classements surestiment le taux réel de résolution "
                 f"{reference(p_blog)}{reference(p_audit)}.")
        c = creer_conclusion(conn, texte, [p_blog, p_audit], PROFIL)
        conn.commit()
        yield conn, ids, {"blog": p_blog, "audit": p_audit, "rejetee": p_rejetee, "conclusion": c}


def rapport(conn, refs):
    t = tracer_conclusion(conn, refs["conclusion"])
    return (
        "# Rapport de veille\n\n"
        "> Question : les benchmarks surestiment-ils la fiabilité des agents ?\n\n"
        "## Conclusions\n\n"
        f"- {t.texte}\n\n"
        + annexe_preuves(conn, [p.id for p in t.preuves])
    )


def test_element_conteste_remonte_au_document_original(base):
    """Le cœur du scénario : de la phrase contestée à l'étude originale, en deux appels."""
    conn, ids, refs = base
    phrase_contestee = tracer_conclusion(conn, refs["conclusion"]).texte
    preuves = [tracer_preuve(conn, i) for i in references(phrase_contestee)]

    p = next(p for p in preuves if p.id == refs["blog"])
    assert p.document.id == ids["blog"]  # la citation vient du blog...
    assert p.est_republication
    assert p.original.id == ids["etude"]  # ...mais la chaîne remonte à l'étude originale
    assert p.original.url == "https://arxiv.org/abs/2503.00001"
    assert p.republications == 1
    assert p.citation in ETUDE  # la citation exacte est là pour vérification


def test_conclusion_et_ses_preuves(base):
    conn, ids, refs = base
    t = tracer_conclusion(conn, f"C{refs['conclusion']}")
    assert {p.id for p in t.preuves} == {refs["blog"], refs["audit"]}
    assert all(p.verifiee for p in t.preuves)
    assert t.niveau_preuve == "moyen"  # 2 travaux indépendants (étude + audit)
    assert t.version == 1
    historique = conn.execute("SELECT version, motif FROM revisions WHERE conclusion_id=?",
                              (refs["conclusion"],)).fetchall()
    assert [tuple(h) for h in historique] == [(1, "création")]


def test_une_preuve_non_verifiee_est_refusee(base):
    conn, _, refs = base
    with pytest.raises(ValueError, match="non vérifiée"):
        creer_conclusion(conn, "Phrase douteuse.", [refs["rejetee"]], PROFIL)
    with pytest.raises(ValueError, match="sans preuve"):
        creer_conclusion(conn, "Phrase sans source.", [], PROFIL)


def test_rapport_conforme(base):
    conn, _, refs = base
    r = rapport(conn, refs)
    assert verifier_tracabilite(r, conn) == []
    assert f'<a id="p{refs["blog"]}"></a>' in r  # le clic sur [Pn] mène à la fiche
    assert "https://arxiv.org/abs/2503.00001" in r  # la fiche donne le lien vers l'original


def test_phrase_sans_preuve_detectee(base):
    conn, _, refs = base
    r = rapport(conn, refs).replace("## Conclusions\n\n", "## Conclusions\n\n- Les agents sont prêts pour la production.\n")
    problemes = verifier_tracabilite(r, conn)
    assert len(problemes) == 1 and "Phrase sans preuve" in problemes[0]


def test_deux_phrases_une_seule_sourcee(base):
    """Le contrôle se fait PHRASE par phrase, pas ligne par ligne."""
    conn, _, refs = base
    r = rapport(conn, refs).replace(".\n\n## Preuves", ". Les fournisseurs le contestent.\n\n## Preuves")
    assert any("fournisseurs le contestent" in p for p in verifier_tracabilite(r, conn))


def test_reference_interdite_detectee(base):
    conn, _, refs = base
    r = rapport(conn, refs).replace("## Preuves", f"- Phrase douteuse [P{refs['rejetee']}] [P9999].\n\n## Preuves")
    problemes = " ".join(verifier_tracabilite(r, conn))
    assert f"P{refs['rejetee']} : citation non vérifiée" in problemes
    assert "P9999 : preuve inexistante" in problemes
    assert f"P{refs['rejetee']} : absente de l'annexe" in problemes
