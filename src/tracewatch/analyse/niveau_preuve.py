"""Niveau de preuve selon le nombre de sources indépendantes (étape 6, responsable A).

Règles (seuils dans le profil) :
  - seules les affirmations à citation VÉRIFIÉE comptent ;
  - une source = un CLUSTER (5 republications de la même étude = 1 source, étape 4) ;
  - les blogs FOURNISSEURS ne comptent pas comme sources indépendantes
    (ils sont comptés à part : leur intérêt commercial est en jeu).
  fort >= 3 sources indépendantes | moyen = 2 | faible = 1 | insuffisant = 0
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

NON_INDEPENDANTES = ("fournisseur",)


@dataclass
class NiveauPreuve:
    niveau: str  # fort | moyen | faible | insuffisant
    sources_independantes: int
    sources_fournisseurs: int
    affirmations: int


def niveau_depuis_compte(n: int, profil: dict) -> str:
    seuils = profil["niveau_preuve"]
    for nom in ("fort", "moyen", "faible"):
        if n >= seuils[nom]:
            return nom
    return "insuffisant"


def evaluer_niveau(conn: sqlite3.Connection, claim_ids: list[int], profil: dict) -> NiveauPreuve:
    if not claim_ids:
        return NiveauPreuve("insuffisant", 0, 0, 0)
    marques = ",".join("?" * len(claim_ids))
    lignes = conn.execute(
        f"""SELECT c.id, d.source_family, COALESCE(d.cluster_id, -d.id) AS travail
            FROM claims c JOIN documents d ON d.id = c.document_id
            WHERE c.id IN ({marques}) AND c.citation_verifiee = 1""",
        claim_ids,
    ).fetchall()
    independants = {l["travail"] for l in lignes if l["source_family"] not in NON_INDEPENDANTES}
    fournisseurs = {l["travail"] for l in lignes if l["source_family"] in NON_INDEPENDANTES}
    return NiveauPreuve(niveau_depuis_compte(len(independants), profil),
                        len(independants), len(fournisseurs), len(lignes))
