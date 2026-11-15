"""Filtres de resserrement et indicateur de qualité du corpus (étape 5, responsable C).

- calculer_scores() : remplit la table `scores` (3 colonnes séparées)
- Filtre / filtrer() : resserrer le corpus (pertinence, fraîcheur, fiabilité,
  familles, dates, mot dans le texte, un seul document par travail)
- evaluer()          : indicateur de qualité + alertes lisibles (scénario 4)
"""

from __future__ import annotations

import sqlite3
from collections import Counter
from dataclasses import dataclass, field
from datetime import date

from tracewatch.scoring.fiabilite import score_fiabilite
from tracewatch.scoring.fraicheur import score_fraicheur
from tracewatch.scoring.pertinence import score_pertinence


def calculer_scores(conn: sqlite3.Connection, profil: dict, reference: date | None = None) -> int:
    """Calcule les 3 scores de chaque document et les enregistre (relançable)."""
    docs = conn.execute("SELECT id, title, text, published_date, source_family FROM documents").fetchall()
    conn.executemany(
        "INSERT OR REPLACE INTO scores (document_id, pertinence, fraicheur, fiabilite) VALUES (?, ?, ?, ?)",
        [
            (
                d["id"],
                score_pertinence(d["title"], d["text"], profil),
                score_fraicheur(d["published_date"], profil, reference),
                score_fiabilite(d["source_family"], d["text"], profil),
            )
            for d in docs
        ],
    )
    conn.commit()
    return len(docs)


@dataclass
class Filtre:
    """Chaque critère vaut None = pas de filtre. Les 3 scores sont filtrés SÉPARÉMENT."""

    pertinence_min: float | None = None
    fraicheur_min: float | None = None
    fiabilite_min: float | None = None
    familles: list[str] | None = None
    date_min: str | None = None  # AAAA-MM-JJ
    date_max: str | None = None
    contient: str | None = None  # mot ou expression dans le titre ou le texte
    un_par_travail: bool = False  # ne garder que l'original de chaque cluster


def filtrer(conn: sqlite3.Connection, f: Filtre | None = None) -> list[sqlite3.Row]:
    f = f or Filtre()
    sql = """SELECT d.*, s.pertinence, s.fraicheur, s.fiabilite
             FROM documents d LEFT JOIN scores s ON s.document_id = d.id WHERE 1=1"""
    params: list = []
    for colonne, seuil in (("s.pertinence", f.pertinence_min), ("s.fraicheur", f.fraicheur_min),
                           ("s.fiabilite", f.fiabilite_min)):
        if seuil is not None:
            sql += f" AND {colonne} >= ?"
            params.append(seuil)
    if f.familles:
        sql += f" AND d.source_family IN ({','.join('?' * len(f.familles))})"
        params += list(f.familles)
    if f.date_min:
        sql += " AND d.published_date >= ?"
        params.append(f.date_min)
    if f.date_max:
        sql += " AND d.published_date <= ?"
        params.append(f.date_max)
    if f.contient:
        sql += " AND (d.title LIKE ? OR d.text LIKE ?)"
        params += [f"%{f.contient}%"] * 2
    if f.un_par_travail:
        sql += " AND (d.cluster_id IS NULL OR d.id IN (SELECT document_original_id FROM clusters))"
    sql += " ORDER BY s.pertinence DESC, d.published_date DESC"
    return conn.execute(sql, params).fetchall()


@dataclass
class QualiteCorpus:
    documents: int = 0
    travaux_distincts: int = 0
    part_bruit: float = 0.0
    part_recente: float = 0.0
    part_independante: float = 0.0
    par_famille: dict[str, int] = field(default_factory=dict)
    alertes: list[str] = field(default_factory=list)
    niveau: str = "vide"  # bon | moyen | faible | vide


def evaluer(docs: list[sqlite3.Row], profil: dict) -> QualiteCorpus:
    """Indicateur de qualité d'un ensemble de documents (le corpus entier ou filtré)."""
    q = QualiteCorpus(documents=len(docs))
    if not docs:
        q.alertes.append("Corpus vide : les filtres sont trop stricts.")
        return q
    conf = profil["qualite_corpus"]
    n = len(docs)
    q.travaux_distincts = len({d["cluster_id"] if d["cluster_id"] is not None else -d["id"] for d in docs})
    q.part_bruit = round(sum((d["pertinence"] or 0) < conf["seuil_pertinence_min"] for d in docs) / n, 3)
    annee_prio = str(profil["horizon"]["annee_min_prioritaire"])
    q.part_recente = round(sum((d["published_date"] or "") >= annee_prio for d in docs) / n, 3)
    q.part_independante = round(sum(d["source_family"] in ("independant", "publication") for d in docs) / n, 3)
    q.par_famille = dict(Counter(d["source_family"] for d in docs).most_common())

    if q.part_bruit > conf["alerte_part_bruit"]:
        q.alertes.append(
            f"Beaucoup de bruit : {q.part_bruit:.0%} des documents ont une pertinence < "
            f"{conf['seuil_pertinence_min']}. Resserrer avec un seuil de pertinence."
        )
    if len(q.par_famille) < conf["familles_min"]:
        q.alertes.append(
            f"Seulement {len(q.par_famille)} famille(s) de sources (minimum {conf['familles_min']}) : "
            "risque de vision partielle."
        )
    if q.part_independante < conf.get("part_independante_min", 0):
        q.alertes.append(
            f"Peu de sources indépendantes ou scientifiques ({q.part_independante:.0%}) : "
            "conclusions fragiles."
        )
    if q.travaux_distincts < n * conf.get("ratio_travaux_min", 0):
        q.alertes.append("Beaucoup de republications : peu de travaux réellement distincts.")

    q.niveau = "bon" if not q.alertes else ("moyen" if len(q.alertes) == 1 else "faible")
    return q
