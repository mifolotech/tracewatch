"""Traçabilité : phrase -> preuve -> document -> document original (étape 7, responsable D).

Vocabulaire :
  - PREUVE      : une affirmation à citation VÉRIFIÉE, identifiée "P<id>" (ex. P12).
  - CONCLUSION  : une phrase du rapport, reliée à une ou plusieurs preuves (table conclusion_claims).
  - CHAÎNE      : conclusion -> preuves -> document cité -> document ORIGINAL du travail (cluster).

Le document original compte : si une preuve a été extraite d'une republication
(un blog qui relaie une étude), la chaîne remonte jusqu'à l'étude elle-même.

Règle du rapport : chaque phrase porte au moins une référence [Pn] vers une preuve vérifiée.
verifier_tracabilite() contrôle cette règle automatiquement.

Ligne de commande (retrouver une source en une commande) :
    python -m tracewatch.rapport.tracabilite P12
    python -m tracewatch.rapport.tracabilite C3
"""

from __future__ import annotations

import re
import sqlite3
import sys
from dataclasses import dataclass, field

from tracewatch.analyse.niveau_preuve import evaluer_niveau

REF = re.compile(r"\[P(\d+)\]")
FIN_DE_PHRASE = re.compile(r"(?<=[.!?])\s+(?=[A-ZÀ-ÖØ-Ý«\"])")
TITRE_ANNEXE = "## Preuves"


def identifiant(claim_id: int) -> str:
    return f"P{claim_id}"


def reference(claim_id: int) -> str:
    """Référence cliquable dans le rapport Markdown : [P12](#p12)."""
    return f"[P{claim_id}](#p{claim_id})"


def references(texte: str) -> list[int]:
    """Identifiants de preuve cités dans un texte, dans l'ordre, sans doublon."""
    return list(dict.fromkeys(int(n) for n in REF.findall(texte)))


# ---------------------------------------------------------------------
# Chaîne de preuve
# ---------------------------------------------------------------------
@dataclass
class DocumentTrace:
    id: int
    titre: str
    url: str
    source: str
    famille: str
    date: str | None


@dataclass
class Preuve:
    id: int
    texte: str
    citation: str
    categorie: str
    position: str | None
    verifiee: bool
    document: DocumentTrace
    original: DocumentTrace  # document original du travail (lui-même si pas de republication)
    republications: int  # nombre d'autres documents du même travail

    @property
    def identifiant(self) -> str:
        return identifiant(self.id)

    @property
    def est_republication(self) -> bool:
        return self.document.id != self.original.id


@dataclass
class Trace:
    conclusion_id: int
    texte: str
    niveau_preuve: str
    version: int
    preuves: list[Preuve] = field(default_factory=list)


def _doc(ligne: sqlite3.Row, prefixe: str) -> DocumentTrace:
    return DocumentTrace(
        id=ligne[f"{prefixe}id"], titre=ligne[f"{prefixe}title"], url=ligne[f"{prefixe}url"],
        source=ligne[f"{prefixe}source_name"], famille=ligne[f"{prefixe}source_family"],
        date=ligne[f"{prefixe}published_date"],
    )


def tracer_preuve(conn: sqlite3.Connection, claim_id: int | str) -> Preuve | None:
    """P12 (ou 12) -> la preuve, son document et le document original du travail."""
    if isinstance(claim_id, str):
        claim_id = int(claim_id.lstrip("Pp"))
    l = conn.execute(
        """SELECT c.id, c.texte, c.citation, c.categorie, c.position, c.citation_verifiee,
                  d.id AS d_id, d.title AS d_title, d.url AS d_url, d.source_name AS d_source_name,
                  d.source_family AS d_source_family, d.published_date AS d_published_date,
                  o.id AS o_id, o.title AS o_title, o.url AS o_url, o.source_name AS o_source_name,
                  o.source_family AS o_source_family, o.published_date AS o_published_date,
                  COALESCE(k.taille, 1) AS taille
           FROM claims c
           JOIN documents d ON d.id = c.document_id
           LEFT JOIN clusters k ON k.cluster_id = d.cluster_id
           LEFT JOIN documents o ON o.id = COALESCE(k.document_original_id, d.id)
           WHERE c.id = ?""",
        (claim_id,),
    ).fetchone()
    if l is None:
        return None
    return Preuve(
        id=l["id"], texte=l["texte"], citation=l["citation"], categorie=l["categorie"],
        position=l["position"], verifiee=bool(l["citation_verifiee"]),
        document=_doc(l, "d_"), original=_doc(l, "o_"), republications=l["taille"] - 1,
    )


def creer_conclusion(conn: sqlite3.Connection, texte: str, claim_ids: list[int], profil: dict,
                     motif: str = "création", cle: str | None = None) -> int:
    """Enregistre une conclusion reliée à ses preuves. Refuse toute preuve non vérifiée.

    Le niveau de preuve est CALCULÉ (sources indépendantes), jamais saisi à la main.
    """
    if not claim_ids:
        raise ValueError("Une conclusion sans preuve ne peut pas entrer dans le rapport.")
    marques = ",".join("?" * len(claim_ids))
    verifiees = {r[0] for r in conn.execute(
        f"SELECT id FROM claims WHERE id IN ({marques}) AND citation_verifiee = 1", claim_ids)}
    refusees = [identifiant(i) for i in claim_ids if i not in verifiees]
    if refusees:
        raise ValueError(f"Preuves inexistantes ou à citation non vérifiée : {', '.join(refusees)}")

    niveau = evaluer_niveau(conn, claim_ids, profil).niveau
    cid = conn.execute(
        "INSERT INTO conclusions (texte, niveau_preuve, version, cle, date_maj) "
        "VALUES (?, ?, 1, ?, datetime('now'))",
        (texte, niveau, cle),
    ).lastrowid
    conn.executemany("INSERT INTO conclusion_claims (conclusion_id, claim_id) VALUES (?, ?)",
                     [(cid, i) for i in dict.fromkeys(claim_ids)])
    conn.execute(
        "INSERT INTO revisions (conclusion_id, version, texte, niveau_preuve, motif) VALUES (?, 1, ?, ?, ?)",
        (cid, texte, niveau, motif),
    )
    return cid


def tracer_conclusion(conn: sqlite3.Connection, conclusion_id: int | str) -> Trace | None:
    """C3 (ou 3) -> la conclusion, puis chacune de ses preuves jusqu'au document original."""
    if isinstance(conclusion_id, str):
        conclusion_id = int(conclusion_id.lstrip("Cc"))
    c = conn.execute("SELECT * FROM conclusions WHERE id = ?", (conclusion_id,)).fetchone()
    if c is None:
        return None
    ids = [r[0] for r in conn.execute(
        "SELECT claim_id FROM conclusion_claims WHERE conclusion_id = ? ORDER BY claim_id", (conclusion_id,))]
    return Trace(c["id"], c["texte"], c["niveau_preuve"], c["version"],
                 [p for p in (tracer_preuve(conn, i) for i in ids) if p])


# ---------------------------------------------------------------------
# Rendu Markdown et contrôle du rapport
# ---------------------------------------------------------------------
def fiche_preuve(p: Preuve) -> str:
    """Bloc de l'annexe "Preuves" : ancre cliquable, citation exacte, source, original."""
    lignes = [
        f'<a id="p{p.id}"></a>**{p.identifiant}** · {p.categorie} · {p.texte}',
        f"> « {p.citation} »",
        f"Source : [{p.document.titre}]({p.document.url}) ({p.document.source}, "
        f"{p.document.famille}, {p.document.date or 'date inconnue'})",
    ]
    if p.est_republication:
        lignes.append(f"Document original du travail : [{p.original.titre}]({p.original.url}) "
                      f"({p.original.source}, {p.original.date or 'date inconnue'})")
    if p.republications:
        lignes.append(f"Ce travail a {p.republications} autre(s) version(s) ou republication(s), "
                      "comptées comme UNE seule source.")
    return "  \n".join(lignes)


def annexe_preuves(conn: sqlite3.Connection, claim_ids: list[int]) -> str:
    fiches = [fiche_preuve(p) for p in (tracer_preuve(conn, i) for i in dict.fromkeys(claim_ids)) if p]
    return f"{TITRE_ANNEXE}\n\n" + "\n\n".join(fiches) + "\n"


def phrases_a_controler(rapport: str) -> list[str]:
    """Phrases du corps du rapport (avant l'annexe) qui doivent porter une référence.

    Exemptés : titres (#), lignes vides, citations de contexte (>), lignes en
    italique (_..._ : notes de méthode), lignes de tableau (|), séparateurs (---).
    """
    corps = rapport.split(TITRE_ANNEXE, 1)[0]
    phrases = []
    for ligne in corps.splitlines():
        l = ligne.strip()
        if not l or l.startswith(("#", ">", "|", "---", "<!--")) or (l.startswith("_") and l.endswith("_")):
            continue
        l = re.sub(r"^([-*]|\d+\.)\s+", "", l)  # puce de liste
        phrases += [p for p in FIN_DE_PHRASE.split(l) if p.strip()]
    return phrases


def verifier_tracabilite(rapport: str, conn: sqlite3.Connection) -> list[str]:
    """Liste des problèmes de traçabilité du rapport (vide = rapport conforme).

    1. chaque phrase du corps porte au moins une référence [Pn] ;
    2. chaque référence désigne une preuve existante à citation VÉRIFIÉE ;
    3. chaque référence a sa fiche dans l'annexe (le clic mène quelque part).
    """
    problemes = []
    for phrase in phrases_a_controler(rapport):
        if not REF.search(phrase):
            problemes.append(f"Phrase sans preuve : « {phrase[:100]} »")
    corps, _, annexe = rapport.partition(TITRE_ANNEXE)
    for i in references(corps):
        p = tracer_preuve(conn, i)
        if p is None:
            problemes.append(f"P{i} : preuve inexistante")
        elif not p.verifiee:
            problemes.append(f"P{i} : citation non vérifiée, interdite dans le rapport")
        if f'<a id="p{i}"></a>' not in annexe:
            problemes.append(f"P{i} : absente de l'annexe des preuves")
    return problemes


# ---------------------------------------------------------------------
# Ligne de commande
# ---------------------------------------------------------------------
def _afficher_preuve(p: Preuve, retrait: str = "") -> None:
    statut = "citation vérifiée" if p.verifiee else "CITATION NON VÉRIFIÉE (rejetée)"
    print(f"{retrait}{p.identifiant} [{p.categorie}, {p.position}] {statut}")
    print(f"{retrait}  affirmation : {p.texte}")
    print(f"{retrait}  citation    : « {p.citation} »")
    print(f"{retrait}  document    : {p.document.titre} ({p.document.source}, {p.document.date})")
    print(f"{retrait}                {p.document.url}")
    if p.est_republication:
        print(f"{retrait}  ORIGINAL    : {p.original.titre} ({p.original.source}, {p.original.date})")
        print(f"{retrait}                {p.original.url}")
    if p.republications:
        print(f"{retrait}  ({p.republications} autre(s) version(s) du même travail, comptées comme une seule source)")


def main(argv: list[str] | None = None) -> int:
    from tracewatch.db import get_connection, init_db

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("Usage : python -m tracewatch.rapport.tracabilite P12 [C3 ...]")
        return 1
    with get_connection(init_db()) as conn:
        for cible in args:
            if cible.upper().startswith("C"):
                t = tracer_conclusion(conn, cible)
                if t is None:
                    print(f"{cible} : conclusion introuvable")
                    continue
                print(f"C{t.conclusion_id} (version {t.version}, preuve {t.niveau_preuve}) : {t.texte}")
                for p in t.preuves:
                    _afficher_preuve(p, "  ")
            else:
                p = tracer_preuve(conn, cible)
                print(f"{cible} : preuve introuvable" if p is None else "", end="")
                if p:
                    _afficher_preuve(p)
            print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
