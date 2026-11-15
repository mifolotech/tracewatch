"""Révision : nouvelles preuves, recalcul des conclusions, historique (étape 8, responsable D).

Chaque conclusion a une clé stable (ex. "decision", "theme:usage_reel").
À chaque génération du rapport, les conclusions sont RECALCULÉES depuis les
preuves actuelles :
  - nouvelle clé           -> conclusion créée (version 1)
  - preuves, texte ou niveau changés -> version + 1, ancienne version gardée dans `revisions`
  - rien de changé         -> rien n'est écrit
L'historique permet de montrer comment la recommandation a évolué avec les preuves.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from tracewatch.analyse.niveau_preuve import evaluer_niveau
from tracewatch.rapport.tracabilite import creer_conclusion, identifiant


@dataclass
class Proposition:
    """Conclusion calculée par le générateur, avant enregistrement."""

    cle: str
    texte: str
    claim_ids: list[int]


def reviser(conn: sqlite3.Connection, propositions: list[Proposition], profil: dict,
            motif: str = "recalcul") -> list[str]:
    """Enregistre les conclusions recalculées. Renvoie la liste lisible des changements."""
    changements = []
    for p in propositions:
        if not p.claim_ids:
            continue
        ancienne = conn.execute("SELECT * FROM conclusions WHERE cle = ?", (p.cle,)).fetchone()
        if ancienne is None:
            cid = creer_conclusion(conn, p.texte, p.claim_ids, profil, motif=motif, cle=p.cle)
            changements.append(f"{p.cle} : nouvelle conclusion C{cid}")
            continue

        avant = {r[0] for r in conn.execute(
            "SELECT claim_id FROM conclusion_claims WHERE conclusion_id = ?", (ancienne["id"],))}
        apres = set(p.claim_ids)
        niveau = evaluer_niveau(conn, list(apres), profil).niveau
        if avant == apres and niveau == ancienne["niveau_preuve"] and p.texte == ancienne["texte"]:
            continue

        details = []
        if apres - avant:
            details.append("+ " + ", ".join(identifiant(i) for i in sorted(apres - avant)))
        if avant - apres:
            details.append("- " + ", ".join(identifiant(i) for i in sorted(avant - apres)))
        if niveau != ancienne["niveau_preuve"]:
            details.append(f"niveau {ancienne['niveau_preuve']} -> {niveau}")
        if p.texte != ancienne["texte"] and not details:
            details.append("formulation mise à jour")
        version = ancienne["version"] + 1

        conn.execute("UPDATE conclusions SET texte=?, niveau_preuve=?, version=?, date_maj=datetime('now') "
                     "WHERE id=?", (p.texte, niveau, version, ancienne["id"]))
        conn.execute("DELETE FROM conclusion_claims WHERE conclusion_id = ?", (ancienne["id"],))
        conn.executemany("INSERT INTO conclusion_claims (conclusion_id, claim_id) VALUES (?, ?)",
                         [(ancienne["id"], i) for i in sorted(apres)])
        conn.execute("INSERT INTO revisions (conclusion_id, version, texte, niveau_preuve, motif) "
                     "VALUES (?, ?, ?, ?, ?)",
                     (ancienne["id"], version, p.texte, niveau, f"{motif} ({'; '.join(details)})"))
        changements.append(f"{p.cle} : version {version} ({'; '.join(details)})")
    conn.commit()
    return changements


def historique(conn: sqlite3.Connection, cle: str) -> list[sqlite3.Row]:
    """Toutes les versions d'une conclusion, de la plus ancienne à la plus récente."""
    return conn.execute(
        """SELECT r.version, r.texte, r.niveau_preuve, r.motif, r.date_revision
           FROM revisions r JOIN conclusions c ON c.id = r.conclusion_id
           WHERE c.cle = ? ORDER BY r.version""",
        (cle,),
    ).fetchall()
