"""Détection des contradictions fournisseur vs indépendant (étape 6, responsable A).

Deux affirmations VÉRIFIÉES se contredisent quand elles portent sur le même
THÈME avec des positions opposées (optimiste vs critique).
Le type est "fournisseur vs indépendant" (scénario 3) quand le côté optimiste
contient un fournisseur et le côté critique une source indépendante ou
scientifique ; sinon c'est une divergence "entre sources".

On raisonne par thème (et non paire par paire) pour que le rapport puisse
montrer les deux camps côte à côte, avec leur niveau de preuve.
"""

from __future__ import annotations

import sqlite3
from collections import defaultdict
from dataclasses import dataclass, field

from tracewatch.analyse.niveau_preuve import NiveauPreuve, evaluer_niveau

FOURNISSEURS = {"fournisseur"}
INDEPENDANTS = {"independant", "publication"}


@dataclass
class Divergence:
    theme: str
    type: str  # "fournisseur vs indépendant" | "entre sources"
    optimistes: list[sqlite3.Row] = field(default_factory=list)
    critiques: list[sqlite3.Row] = field(default_factory=list)
    preuve_optimistes: NiveauPreuve | None = None
    preuve_critiques: NiveauPreuve | None = None


def affirmations_verifiees(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        """SELECT c.*, d.title AS doc_titre, d.url AS doc_url, d.source_name, d.source_family,
                  d.published_date, d.cluster_id
           FROM claims c JOIN documents d ON d.id = c.document_id
           WHERE c.citation_verifiee = 1 ORDER BY c.id"""
    ).fetchall()


def detecter(conn: sqlite3.Connection, profil: dict) -> list[Divergence]:
    par_theme: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    for c in affirmations_verifiees(conn):
        if c["theme"] and c["position"] in ("optimiste", "critique"):
            par_theme[c["theme"]][c["position"]].append(c)

    divergences = []
    for theme, camps in par_theme.items():
        opt, crit = camps["optimiste"], camps["critique"]
        if not opt or not crit:
            continue
        fournisseur_optimiste = any(c["source_family"] in FOURNISSEURS for c in opt)
        independant_critique = any(c["source_family"] in INDEPENDANTS for c in crit)
        divergences.append(Divergence(
            theme=theme,
            type="fournisseur vs indépendant" if fournisseur_optimiste and independant_critique else "entre sources",
            optimistes=opt,
            critiques=crit,
            preuve_optimistes=evaluer_niveau(conn, [c["id"] for c in opt], profil),
            preuve_critiques=evaluer_niveau(conn, [c["id"] for c in crit], profil),
        ))
    # Les oppositions fournisseur vs indépendant d'abord : ce sont elles que le rapport doit montrer
    return sorted(divergences, key=lambda d: (d.type != "fournisseur vs indépendant", d.theme))
