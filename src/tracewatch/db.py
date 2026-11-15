"""Schéma SQLite de TraceWatch (étape 2).

Respecte le contrat de données de ARCHITECTURE.md §5.
Tous les modules passent par get_connection() pour accéder à la base.

Créer la base :
    python -m tracewatch.db
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

# Racine du projet : src/tracewatch/db.py -> remonter de 3 niveaux
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "tracewatch.db"

SOURCE_FAMILIES = ("publication", "benchmark", "depot", "fournisseur", "independant")
CLAIM_CATEGORIES = ("fait", "interpretation", "lacune", "risque", "signal")

SCHEMA = f"""
-- Documents normalisés (un par document collecté)
CREATE TABLE IF NOT EXISTS documents (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    url             TEXT NOT NULL UNIQUE,
    canonical_url   TEXT,
    title           TEXT NOT NULL,
    text            TEXT,
    authors         TEXT,            -- liste JSON
    organization    TEXT,
    published_date  TEXT,            -- ISO 8601 (AAAA-MM-JJ)
    collected_date  TEXT NOT NULL,   -- ISO 8601
    source_family   TEXT NOT NULL CHECK (source_family IN {SOURCE_FAMILIES}),
    source_name     TEXT,
    doi             TEXT,
    arxiv_id        TEXT,
    content_hash    TEXT,
    cluster_id      INTEGER REFERENCES clusters(cluster_id) ON DELETE SET NULL
);

-- Groupes "travail original / republications"
CREATE TABLE IF NOT EXISTS clusters (
    cluster_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    document_original_id  INTEGER REFERENCES documents(id) ON DELETE SET NULL,
    taille                INTEGER NOT NULL DEFAULT 1 CHECK (taille >= 1)
);

-- Trois scores séparés (0 à 1)
CREATE TABLE IF NOT EXISTS scores (
    document_id  INTEGER PRIMARY KEY REFERENCES documents(id) ON DELETE CASCADE,
    pertinence   REAL CHECK (pertinence BETWEEN 0 AND 1),
    fraicheur    REAL CHECK (fraicheur  BETWEEN 0 AND 1),
    fiabilite    REAL CHECK (fiabilite  BETWEEN 0 AND 1)
);

-- Affirmations extraites par le LLM, avec citation exacte
CREATE TABLE IF NOT EXISTS claims (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id        INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    texte              TEXT NOT NULL,
    citation           TEXT NOT NULL,
    citation_verifiee  INTEGER NOT NULL DEFAULT 0 CHECK (citation_verifiee IN (0, 1)),
    categorie          TEXT CHECK (categorie IN {CLAIM_CATEGORIES})
);

-- Conclusions du rapport
CREATE TABLE IF NOT EXISTS conclusions (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    texte          TEXT NOT NULL,
    niveau_preuve  TEXT,
    version        INTEGER NOT NULL DEFAULT 1
);

-- Lien conclusion <-> affirmations qui la soutiennent (traçabilité)
CREATE TABLE IF NOT EXISTS conclusion_claims (
    conclusion_id  INTEGER NOT NULL REFERENCES conclusions(id) ON DELETE CASCADE,
    claim_id       INTEGER NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    PRIMARY KEY (conclusion_id, claim_id)
);

-- Historique des conclusions (révisions)
CREATE TABLE IF NOT EXISTS revisions (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    conclusion_id  INTEGER NOT NULL REFERENCES conclusions(id) ON DELETE CASCADE,
    version        INTEGER NOT NULL,
    texte          TEXT NOT NULL,
    niveau_preuve  TEXT,
    motif          TEXT,
    date_revision  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_documents_canonical ON documents(canonical_url);
CREATE INDEX IF NOT EXISTS idx_documents_doi       ON documents(doi);
CREATE INDEX IF NOT EXISTS idx_documents_arxiv     ON documents(arxiv_id);
CREATE INDEX IF NOT EXISTS idx_documents_hash      ON documents(content_hash);
CREATE INDEX IF NOT EXISTS idx_documents_cluster   ON documents(cluster_id);
CREATE INDEX IF NOT EXISTS idx_claims_document     ON claims(document_id);
"""


def get_db_path() -> Path:
    """Chemin de la base : variable TRACEWATCH_DB du .env, sinon data/tracewatch.db."""
    load_dotenv(PROJECT_ROOT / ".env")
    custom = os.getenv("TRACEWATCH_DB")
    return Path(custom) if custom else DEFAULT_DB_PATH


def get_connection(db_path: Path | str | None = None) -> sqlite3.Connection:
    """Ouvre une connexion avec les clés étrangères activées et l'accès par nom de colonne."""
    path = Path(db_path) if db_path else get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: Path | str | None = None) -> Path:
    """Crée toutes les tables (sans effacer les données existantes)."""
    path = Path(db_path) if db_path else get_db_path()
    with get_connection(path) as conn:
        conn.executescript(SCHEMA)
    return path


def list_tables(db_path: Path | str | None = None) -> list[str]:
    with get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
    return [r["name"] for r in rows]


if __name__ == "__main__":
    created = init_db()
    print(f"Base prête : {created}")
    for name in list_tables(created):
        print(f"  - {name}")
