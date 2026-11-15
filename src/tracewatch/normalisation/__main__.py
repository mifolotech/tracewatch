"""Lance l'étape 4 : python -m tracewatch.normalisation"""

from __future__ import annotations

import argparse
import sys

from tracewatch.collecte.commun import charger_profil
from tracewatch.db import get_connection, init_db
from tracewatch.normalisation.clusters import executer

EXPLICATIONS = {
    "url": "même URL canonique",
    "doi": "même DOI",
    "arxiv": "même identifiant arXiv",
    "empreinte": "texte identique",
    "similarite": "texte très similaire (TF-IDF)",
    "titre": "titre inclus dans l'autre",
}


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Normalisation et dédoublonnage TraceWatch")
    parser.add_argument("--db", default=None)
    args = parser.parse_args(argv)

    chemin = init_db(args.db)
    with get_connection(chemin) as conn:
        b = executer(conn, charger_profil())

    print(f"Documents          : {b.documents}")
    print(f"Travaux distincts  : {b.clusters}  (= sources indépendantes)")
    print(f"Groupes de doublons: {b.clusters_multiples}  ({b.documents_regroupes} documents regroupés)")
    print("\nRaisons des rapprochements :")
    for raison, n in b.raisons.most_common():
        print(f"  {n:>4}  {EXPLICATIONS.get(raison, raison)}")
    print("\nPlus gros groupes :")
    for taille, titre in b.plus_gros[:10]:
        print(f"  {taille} docs  {titre[:80]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
