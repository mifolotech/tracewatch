"""Extraction d'affirmations avec citation exacte (étape 6, responsable A).

Pour chaque document : le LLM propose des affirmations (texte en français +
citation copiée mot pour mot + catégorie + thème + position). Chaque citation
est VÉRIFIÉE par verification.py avant d'être acceptée.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field

from tracewatch.analyse.llm_client import ClientLLM
from tracewatch.analyse.verification import verifier_citation
from tracewatch.collecte.commun import maintenant_iso
from tracewatch.db import CLAIM_CATEGORIES, CLAIM_POSITIONS

PROMPT = """You are a rigorous analyst working for a technology watch team.

DECISION QUESTION:
{question}

SUB-QUESTIONS:
{sous_questions}

TASK: read the DOCUMENT below and extract at most {max_claims} claims that help answer the decision question.
If the document is not useful for the question, return [].

RULES (mandatory):
1. "citation": copy ONE passage VERBATIM from the document: the exact same characters, 1 or 2 consecutive
   sentences, between 30 and 300 characters. Never paraphrase, never translate, never merge separate passages,
   never use "...". If you cannot quote a passage that supports the claim, do not output the claim.
2. "texte": the claim restated in FRENCH, in one sentence, faithful to the citation, adding nothing.
3. "categorie", one of:
   - "fait": verifiable fact or measured result
   - "interpretation": opinion, analysis or conclusion of the author
   - "lacune": missing evidence, unknown, limitation of what has been measured
   - "risque": documented failure, incident or risk
   - "signal": weak signal or emerging trend
4. "theme", one of:
{themes}
5. "position" with respect to the question:
   - "optimiste": supports that agents / benchmark scores are reliable enough for routine development tasks
   - "critique": suggests scores overestimate real reliability, or documents failures, risks or limits
   - "neutre": neither
6. "sous_question": "SQ1" to "SQ5", or null.

Answer with JSON only: a list of objects with keys "texte", "citation", "categorie", "theme", "position", "sous_question".

DOCUMENT
Title: {titre}
Source: {source} ({famille}), published {date}
Text:
\"\"\"
{texte}
\"\"\"
"""


def construire_prompt(doc: sqlite3.Row, profil: dict) -> str:
    conf = profil["analyse"]
    return PROMPT.format(
        question=" ".join(profil["question"].split()),
        sous_questions="\n".join(f"- {sq['id']}: {sq['texte']}" for sq in profil["sous_questions"]),
        max_claims=conf["max_affirmations_par_document"],
        themes="\n".join(f'   - "{k}": {v}' for k, v in conf["themes"].items()),
        titre=doc["title"],
        source=doc["source_name"],
        famille=doc["source_family"],
        date=doc["published_date"] or "unknown",
        texte=(doc["text"] or "")[: conf["longueur_max_document"]],
    )


@dataclass
class BilanExtraction:
    documents: int = 0
    proposees: int = 0
    verifiees: int = 0
    rejetees: list[tuple[str, str]] = field(default_factory=list)  # (titre doc, citation)
    invalides: int = 0  # format inutilisable (catégorie inconnue, champ manquant)


def deja_analyse(conn: sqlite3.Connection, document_id: int) -> bool:
    """Un document déjà analysé (par n'importe quel modèle) n'est pas réanalysé.
    Le modèle utilisé reste tracé dans claims.modele."""
    return conn.execute(
        "SELECT 1 FROM claims WHERE document_id=? LIMIT 1", (document_id,)
    ).fetchone() is not None


def analyser_document(conn: sqlite3.Connection, client: ClientLLM, doc: sqlite3.Row,
                      profil: dict, bilan: BilanExtraction) -> None:
    conf = profil["analyse"]
    reponse = client.generer_json(construire_prompt(doc, profil))
    bilan.documents += 1
    if not isinstance(reponse, list):
        bilan.invalides += 1
        return
    source = f"{doc['title']}\n{doc['text'] or ''}"
    themes = set(conf["themes"])
    for a in reponse[: conf["max_affirmations_par_document"]]:
        if not isinstance(a, dict) or not a.get("texte") or not a.get("citation"):
            bilan.invalides += 1
            continue
        bilan.proposees += 1
        categorie = a.get("categorie") if a.get("categorie") in CLAIM_CATEGORIES else None
        position = a.get("position") if a.get("position") in CLAIM_POSITIONS else "neutre"
        theme = a.get("theme") if a.get("theme") in themes else None
        verifiee = verifier_citation(a["citation"], source, conf["longueur_min_citation"])
        if verifiee and categorie is None:
            verifiee = False  # sans catégorie valide, l'affirmation n'est pas exploitable
        conn.execute(
            """INSERT INTO claims (document_id, texte, citation, citation_verifiee, categorie,
                                   theme, position, sous_question, modele, date_extraction)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (doc["id"], a["texte"].strip(), a["citation"].strip(), int(verifiee), categorie,
             theme, position, a.get("sous_question"), client.nom, maintenant_iso()),
        )
        if verifiee:
            bilan.verifiees += 1
        else:
            bilan.rejetees.append((doc["title"], a["citation"]))
