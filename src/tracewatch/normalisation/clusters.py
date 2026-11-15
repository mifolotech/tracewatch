"""Clusters : travail original vs republications (étape 4, responsable C).

Chaque document appartient à un cluster (seul, il forme un cluster de taille 1).
Un cluster = UN travail = UNE source indépendante, quel que soit le nombre de
republications. L'original est le document publié le plus tôt.
"""

from __future__ import annotations

import sqlite3
from collections import Counter, defaultdict
from dataclasses import dataclass, field

from tracewatch.normalisation.dedup import Paire, trouver_paires
from tracewatch.normalisation.schema import normaliser_documents


class UnionFind:
    """Regroupe les éléments liés, même indirectement (A~B et B~C => A, B, C ensemble)."""

    def __init__(self, elements):
        self.parent = {e: e for e in elements}

    def trouver(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def unir(self, a, b):
        ra, rb = self.trouver(a), self.trouver(b)
        if ra != rb:
            self.parent[max(ra, rb)] = min(ra, rb)

    def groupes(self) -> list[list]:
        g = defaultdict(list)
        for e in self.parent:
            g[self.trouver(e)].append(e)
        return list(g.values())


def choisir_original(docs: list[sqlite3.Row], priorite: list[str]) -> sqlite3.Row:
    """Le plus ancien ; à date égale, la famille la plus prioritaire ; puis le premier collecté."""
    rang = {f: i for i, f in enumerate(priorite)}
    return min(
        docs,
        key=lambda d: (d["published_date"] or "9999", rang.get(d["source_family"], len(rang)), d["id"]),
    )


@dataclass
class BilanClusters:
    documents: int = 0
    clusters: int = 0
    clusters_multiples: int = 0
    documents_regroupes: int = 0
    raisons: Counter = field(default_factory=Counter)
    plus_gros: list[tuple[int, str]] = field(default_factory=list)


def construire_clusters(conn: sqlite3.Connection, paires: list[Paire], profil: dict) -> BilanClusters:
    """Efface et reconstruit tous les clusters (relançable sans effet de bord)."""
    priorite = profil["dedoublonnage"].get("priorite_original", [])
    docs = {d["id"]: d for d in conn.execute(
        "SELECT id, title, published_date, source_family FROM documents"
    ).fetchall()}

    uf = UnionFind(docs)
    for p in paires:
        uf.unir(p.a, p.b)

    conn.execute("UPDATE documents SET cluster_id = NULL")
    conn.execute("DELETE FROM clusters")
    conn.execute("DELETE FROM sqlite_sequence WHERE name = 'clusters'")

    bilan = BilanClusters(documents=len(docs), raisons=Counter(p.raison for p in paires))
    for ids in sorted(uf.groupes(), key=min):
        original = choisir_original([docs[i] for i in ids], priorite)
        cid = conn.execute(
            "INSERT INTO clusters (document_original_id, taille) VALUES (?, ?)",
            (original["id"], len(ids)),
        ).lastrowid
        conn.executemany("UPDATE documents SET cluster_id=? WHERE id=?", [(cid, i) for i in ids])
        bilan.clusters += 1
        if len(ids) > 1:
            bilan.clusters_multiples += 1
            bilan.documents_regroupes += len(ids)
            bilan.plus_gros.append((len(ids), original["title"]))
    bilan.plus_gros.sort(reverse=True)
    return bilan


def executer(conn: sqlite3.Connection, profil: dict) -> BilanClusters:
    """Étape 4 complète : normaliser -> trouver les doublons -> construire les clusters."""
    normaliser_documents(conn)
    bilan = construire_clusters(conn, trouver_paires(conn, profil), profil)
    conn.commit()
    return bilan


def sources_independantes(conn: sqlite3.Connection, document_ids: list[int]) -> int:
    """Nombre de sources INDÉPENDANTES parmi des documents = nombre de clusters distincts.

    C'est ce chiffre (et non le nombre de documents) qui fixera le niveau de preuve à l'étape 6.
    """
    if not document_ids:
        return 0
    marques = ",".join("?" * len(document_ids))
    return conn.execute(
        f"SELECT COUNT(DISTINCT cluster_id) FROM documents WHERE id IN ({marques})", document_ids
    ).fetchone()[0]
