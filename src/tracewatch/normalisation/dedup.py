"""Détection des doublons (étape 4, responsable C).

Deux documents sont considérés comme le MÊME TRAVAIL si :
1. même URL canonique
2. même DOI
3. même identifiant arXiv
4. même empreinte de contenu (texte identique republié ailleurs)
5. textes très similaires : similarité cosinus TF-IDF >= seuil du profil
   (sauf familles exclues, ex. classements dont les textes suivent tous le même gabarit)
6. publications dont un titre contient l'autre (version conférence vs prépublication)

Chaque paire garde la RAISON du rapprochement : c'est explicable à l'oral.
"""

from __future__ import annotations

import sqlite3
from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from tracewatch.normalisation.schema import texte_normalise


@dataclass(frozen=True)
class Paire:
    a: int
    b: int
    raison: str  # url | doi | arxiv | empreinte | similarite | titre
    score: float = 1.0


def _par_cle(lignes, champ: str, raison: str) -> list[Paire]:
    groupes: dict[str, list[int]] = defaultdict(list)
    for d in lignes:
        if d[champ]:
            groupes[d[champ]].append(d["id"])
    return [Paire(a, b, raison) for ids in groupes.values() for a, b in combinations(sorted(ids), 2)]


def _par_similarite(lignes, conf: dict) -> list[Paire]:
    exclues = set(conf.get("familles_sans_similarite", []))
    lg_min = conf.get("longueur_min_texte", 100)

    def contenu(d) -> str:
        # Une republication change souvent le TITRE mais garde le CORPS :
        # on compare le corps seul quand il est assez long.
        texte = d["text"] or ""
        return texte if len(texte) >= lg_min else f"{d['title']} {texte}"

    candidats = [d for d in lignes if d["source_family"] not in exclues and len(contenu(d)) >= lg_min]
    if len(candidats) < 2:
        return []
    matrice = TfidfVectorizer(stop_words="english", sublinear_tf=True, ngram_range=(1, 2)).fit_transform(
        [contenu(d) for d in candidats]
    )
    sim = cosine_similarity(matrice)
    i, j = np.where(np.triu(sim >= conf["seuil_similarite"], k=1))
    return [
        Paire(min(candidats[x]["id"], candidats[y]["id"]), max(candidats[x]["id"], candidats[y]["id"]),
              "similarite", round(float(sim[x, y]), 3))
        for x, y in zip(i, j)
    ]


def _par_titre(lignes, conf: dict) -> list[Paire]:
    """'Demystifying LLM-Based SE Agents' est contenu dans 'Agentless: Demystifying LLM-based SE Agents'."""
    lg_min = conf.get("longueur_min_titre_inclus", 30)
    pubs = [(d["id"], texte_normalise(d["title"])) for d in lignes if d["source_family"] == "publication"]
    paires = []
    for (ia, ta), (ib, tb) in combinations(pubs, 2):
        court, long_ = sorted((ta, tb), key=len)
        if len(court) >= lg_min and court in long_:
            paires.append(Paire(min(ia, ib), max(ia, ib), "titre"))
    return paires


def trouver_paires(conn: sqlite3.Connection, profil: dict) -> list[Paire]:
    conf = profil["dedoublonnage"]
    lignes = conn.execute(
        "SELECT id, title, text, source_family, canonical_url, doi, arxiv_id, content_hash FROM documents"
    ).fetchall()
    paires = (
        _par_cle(lignes, "canonical_url", "url")
        + _par_cle(lignes, "doi", "doi")
        + _par_cle(lignes, "arxiv_id", "arxiv")
        + _par_cle(lignes, "content_hash", "empreinte")
        + _par_similarite(lignes, conf)
        + _par_titre(lignes, conf)
    )
    # Une même paire peut être trouvée par plusieurs règles : on garde la première raison
    vues: dict[tuple[int, int], Paire] = {}
    for p in paires:
        vues.setdefault((p.a, p.b), p)
    return list(vues.values())
