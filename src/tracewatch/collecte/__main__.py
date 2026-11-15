"""Lance toute la collecte : python -m tracewatch.collecte

Options :
    --sources arxiv rss     ne lancer que certaines sources
    --db chemin.db          utiliser une autre base
"""

from __future__ import annotations

import argparse
import sys

from tracewatch.collecte import arxiv, benchmarks, github, openalex, rss
from tracewatch.collecte.commun import Http, charger_profil
from tracewatch.db import get_connection, init_db

COLLECTEURS = {
    "arxiv": arxiv.collecter,
    "openalex": openalex.collecter,
    "github": github.collecter,
    "benchmarks": benchmarks.collecter,
    "rss": rss.collecter,
}

# Pauses minimales entre deux appels au même site (secondes)
PAUSES = {
    "export.arxiv.org": 3.0,  # règle officielle d'arXiv
    "api.github.com": 2.0,
}


def main(argv: list[str] | None = None) -> int:
    # La console Windows n'aime pas les accents et symboles : on force l'UTF-8
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Collecte multi-sources TraceWatch")
    parser.add_argument("--sources", nargs="+", choices=list(COLLECTEURS), default=list(COLLECTEURS))
    parser.add_argument("--db", default=None)
    args = parser.parse_args(argv)

    profil = charger_profil()
    chemin = init_db(args.db)
    http = Http(pauses=PAUSES)
    print(f"Base : {chemin}\n")

    with get_connection(chemin) as conn:
        for nom in args.sources:
            print(f"→ {nom}…", flush=True)
            try:
                bilan = COLLECTEURS[nom](conn, profil, http)
            except Exception as e:  # une source en panne ne bloque pas les autres
                print(f"  ✗ {nom} a échoué : {e}")
                continue
            conn.commit()
            print(f"  {bilan}")
            for err in bilan.erreurs:
                print(f"    ⚠ {err}")

        familles = conn.execute(
            "SELECT source_family, COUNT(*) AS n FROM documents GROUP BY source_family ORDER BY n DESC"
        ).fetchall()

    total = sum(f["n"] for f in familles)
    print(f"\nContenu de la base : {total} documents")
    for f in familles:
        print(f"  {f['source_family']:<12} {f['n']}")

    minimum = profil["qualite_corpus"]["familles_min"]
    ok = len(familles) >= minimum
    print(f"\n{'✓' if ok else '✗'} {len(familles)} familles de sources (minimum exigé : {minimum})")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
