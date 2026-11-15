"""Collecte des publications arXiv (étape 3, responsable B).

API : http://export.arxiv.org/api/query (Atom). Règle d'arXiv : 3 secondes entre deux appels.
Famille : publication.
"""

from __future__ import annotations

import re
import sqlite3

import feedparser

from tracewatch.collecte.commun import Bilan, Document, Http, nettoyer_html, vers_iso

API = "http://export.arxiv.org/api/query"


def construire_requete(requete: str, categories: list[str]) -> str:
    """'LLM agent evaluation' -> all:LLM AND all:agent AND all:evaluation AND (cat:cs.SE OR ...)."""
    mots = [f'all:"{m}"' if "-" in m else f"all:{m}" for m in requete.split()]
    cats = " OR ".join(f"cat:{c}" for c in categories)
    return f"({' AND '.join(mots)}) AND ({cats})"


def extraire_arxiv_id(id_url: str) -> str:
    """'http://arxiv.org/abs/2310.06770v3' -> '2310.06770'."""
    brut = id_url.rsplit("/abs/", 1)[-1]
    return re.sub(r"v\d+$", "", brut)


def collecter(conn: sqlite3.Connection, profil: dict, http: Http) -> Bilan:
    conf = profil["sources"]["arxiv"]
    bilan = Bilan("arxiv")
    for requete in conf["requetes"]:
        try:
            reponse = http.get(
                API,
                params={
                    "search_query": construire_requete(requete, conf["categories"]),
                    "start": 0,
                    "max_results": conf["max_resultats_par_requete"],
                    "sortBy": "relevance",
                },
            )
        except Exception as e:  # une requête qui échoue ne bloque pas les autres
            bilan.erreurs.append(f"{requete}: {e}")
            continue
        for entree in feedparser.parse(reponse.content).entries:
            arxiv_id = extraire_arxiv_id(entree.id)
            bilan.ajouter(
                conn,
                Document(
                    url=f"https://arxiv.org/abs/{arxiv_id}",
                    title=nettoyer_html(entree.title),
                    text=nettoyer_html(entree.get("summary")),
                    authors=[a.get("name", "") for a in entree.get("authors", [])],
                    organization=None,  # l'API arXiv ne donne pas l'affiliation
                    published_date=vers_iso(entree.get("published")),
                    source_family=conf["source_family"],
                    source_name="arXiv",
                    doi=entree.get("arxiv_doi"),
                    arxiv_id=arxiv_id,
                ),
                profil,
            )
    return bilan
