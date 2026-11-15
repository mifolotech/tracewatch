"""Scénario 3 : affirmation d'un fournisseur contestée par une source indépendante.

La divergence doit apparaître dans l'analyse. Et règle d'or de l'étape 6 :
aucune affirmation dont la citation n'est pas vérifiée ne doit être utilisable.

Le LLM est remplacé par un faux LLM aux réponses connues : le test tourne
sans clé, sans réseau, et vérifie le CODE (vérification, contradictions, preuve).
"""

from __future__ import annotations

import pytest

from tracewatch.analyse.contradictions import affirmations_verifiees, detecter
from tracewatch.analyse.extraction import BilanExtraction, analyser_document
from tracewatch.analyse.llm_client import ClientLLM, LLMIndisponible
from tracewatch.analyse.niveau_preuve import evaluer_niveau
from tracewatch.analyse.verification import verifier_citation
from tracewatch.collecte.commun import Document, charger_profil, enregistrer
from tracewatch.db import get_connection, init_db
from tracewatch.normalisation.clusters import executer as regrouper

PROFIL = charger_profil()

FOURNISSEUR = (
    "Our new coding agent is ready for production. It resolves 80% of real customer issues "
    "end to end, so teams can now delegate routine bug fixes entirely to the agent."
)
INDEPENDANT = (
    "We replicated the vendor evaluation on 300 internal tickets. In real deployments the agent "
    "resolved only 31% of issues without human correction, far below the advertised figure."
)
LABO = (
    "Our audit of agent runs found that 22% of accepted patches introduced regressions that the "
    "provided tests did not catch, which suggests leaderboard scores overstate reliability."
)


class FauxLLM:
    """Répond selon le titre du document présent dans le prompt."""

    nom = "faux/llm"

    def __init__(self):
        self.appels = 0

    def generer(self, prompt: str) -> str:
        import json
        self.appels += 1
        if "Vendor launch" in prompt:
            reponse = [
                {"texte": "Le fournisseur affirme que son agent résout 80 % des tickets réels.",
                 "citation": "It resolves 80% of real customer issues end to end",
                 "categorie": "interpretation", "theme": "usage_reel", "position": "optimiste",
                 "sous_question": "SQ2"},
                # Hallucination : cette phrase N'EST PAS dans le document
                {"texte": "Le fournisseur garantit zéro régression.",
                 "citation": "The agent never introduces regressions in production code",
                 "categorie": "fait", "theme": "fiabilite_securite", "position": "optimiste",
                 "sous_question": "SQ4"},
            ]
        elif "Independent replication" in prompt:
            reponse = [{"texte": "En conditions réelles, l'agent ne résout que 31 % des tickets.",
                        "citation": "In real deployments the agent resolved only 31% of issues without human correction",
                        "categorie": "fait", "theme": "usage_reel", "position": "critique",
                        "sous_question": "SQ2"}]
        elif "Lab audit" in prompt:
            reponse = [{"texte": "22 % des correctifs acceptés introduisent des régressions.",
                        "citation": "22% of accepted patches introduced regressions",
                        "categorie": "fait", "theme": "usage_reel", "position": "critique",
                        "sous_question": "SQ2"}]
        else:
            reponse = []
        return json.dumps(reponse)


@pytest.fixture
def env_test(tmp_path):
    with get_connection(init_db(tmp_path / "t.db")) as conn:
        docs = [
            ("https://vendor.example.com/launch", "Vendor launch", FOURNISSEUR, "fournisseur"),
            ("https://lab.example.org/replication", "Independent replication", INDEPENDANT, "independant"),
            # Republication de la même réplication : ne doit PAS compter comme une 2e source
            ("https://news.example.net/replication-copy", "Independent replication (repost)", INDEPENDANT, "independant"),
            ("https://audit.example.edu/paper", "Lab audit", LABO, "publication"),
        ]
        for url, titre, texte, famille in docs:
            enregistrer(conn, Document(url=url, title=titre, text=texte, source_family=famille,
                                       source_name=titre, published_date="2026-06-01"))
        regrouper(conn, PROFIL)
        faux = FauxLLM()
        client = ClientLLM(faux, faux.nom, tmp_path / "cache")
        bilan = BilanExtraction()
        for d in conn.execute("SELECT * FROM documents ORDER BY id").fetchall():
            analyser_document(conn, client, d, PROFIL, bilan)
        conn.commit()
        yield conn, client, faux, bilan, tmp_path


def test_la_citation_inventee_est_rejetee(env_test):
    conn, _, _, bilan, _ = env_test
    assert len(bilan.rejetees) == 1
    assert "never introduces regressions" in bilan.rejetees[0][1]
    ligne = conn.execute("SELECT citation_verifiee FROM claims WHERE citation LIKE '%never introduces%'").fetchone()
    assert ligne[0] == 0


def test_aucune_affirmation_non_verifiee_n_est_utilisable(env_test):
    conn, *_ = env_test
    utilisables = affirmations_verifiees(conn)
    assert utilisables, "il doit y avoir des affirmations vérifiées"
    assert all(c["citation_verifiee"] == 1 for c in utilisables)
    assert all(verifier_citation(c["citation"], f"{c['doc_titre']}\n" + conn.execute(
        "SELECT text FROM documents WHERE id=?", (c["document_id"],)).fetchone()[0]) for c in utilisables)


def test_la_contradiction_fournisseur_independant_est_detectee(env_test):
    conn, *_ = env_test
    divergences = detecter(conn, PROFIL)
    assert len(divergences) == 1
    d = divergences[0]
    assert d.theme == "usage_reel"
    assert d.type == "fournisseur vs indépendant"
    assert {c["source_family"] for c in d.optimistes} == {"fournisseur"}
    assert {c["source_family"] for c in d.critiques} == {"independant", "publication"}


def test_niveau_de_preuve_compte_les_sources_independantes(env_test):
    """Côté critique : 3 affirmations, mais la réplication et sa republication = 1 source.
    Total : 2 sources indépendantes (réplication + audit) -> preuve moyenne.
    Côté optimiste : seulement un fournisseur -> preuve insuffisante."""
    conn, *_ = env_test
    d = detecter(conn, PROFIL)[0]
    assert len(d.critiques) == 3
    assert d.preuve_critiques.sources_independantes == 2
    assert d.preuve_critiques.niveau == "moyen"
    assert d.preuve_optimistes.sources_independantes == 0
    assert d.preuve_optimistes.sources_fournisseurs == 1
    assert d.preuve_optimistes.niveau == "insuffisant"


def test_une_affirmation_rejetee_ne_compte_jamais_comme_preuve(env_test):
    conn, *_ = env_test
    rejetee = conn.execute("SELECT id FROM claims WHERE citation_verifiee=0").fetchone()[0]
    assert evaluer_niveau(conn, [rejetee], PROFIL).affirmations == 0


def test_le_cache_rend_l_analyse_reproductible(env_test):
    conn, client, faux, _, tmp_path = env_test
    appels_avant = faux.appels
    doc = conn.execute("SELECT * FROM documents WHERE title='Vendor launch'").fetchone()
    analyser_document(conn, client, doc, PROFIL, BilanExtraction())
    assert faux.appels == appels_avant  # servi par le cache, pas de nouvel appel

    sans_llm = ClientLLM(None, faux.nom, tmp_path / "cache")  # mode démo : pas de clé
    analyser_document(conn, sans_llm, doc, PROFIL, BilanExtraction())  # marche quand même
    inconnu = conn.execute("SELECT * FROM documents WHERE title='Lab audit'").fetchone()
    prompt_modifie = dict(inconnu)
    prompt_modifie["text"] = "texte jamais vu"
    with pytest.raises(LLMIndisponible):
        analyser_document(conn, sans_llm, prompt_modifie, PROFIL, BilanExtraction())


@pytest.mark.parametrize("citation, attendu", [
    ("It resolves 80% of real customer issues end to end", True),
    ("it   RESOLVES 80% of real\ncustomer issues", True),  # casse et espaces : toléré
    ("“It resolves 80% of real customer issues”", True),  # guillemets typographiques : toléré
    ("ready for production. It resolves 80%", True),  # passage à cheval sur 2 phrases : OK
    ("Our new coding agent is ready for production .", True),  # espace avant ponctuation : toléré
    ("It resolves 85% of real customer issues", False),  # un chiffre changé : rejet
    ("It solves 80% of real customer issues", False),  # un mot changé : rejet
    ("It resolves 80% ... teams can now delegate", False),  # passages collés : rejet
    ("80% of real", False),  # trop court pour prouver quoi que ce soit
])
def test_verification_stricte(citation, attendu):
    assert verifier_citation(citation, FOURNISSEUR) is attendu
