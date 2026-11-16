"""Génère le rapport : python -m tracewatch.rapport [--motif "nouvelles preuves"]

Recalcule les conclusions depuis les preuves vérifiées, les versionne si elles
ont changé, contrôle la traçabilité, puis écrit rapports/rapport_AAAA-MM-JJ.md
et rapports/dernier_rapport.md.
"""

from __future__ import annotations

import argparse
import sys

from tracewatch.collecte.commun import charger_profil
from tracewatch.db import get_connection, init_db
from tracewatch.rapport.generateur import LIBELLES_OPTIONS, RapportNonConforme, generer_rapport


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Génération du rapport TraceWatch")
    parser.add_argument("--db", default=None)
    parser.add_argument("--motif", default="génération du rapport", help="raison de la révision (historique)")
    args = parser.parse_args(argv)

    with get_connection(init_db(args.db)) as conn:
        try:
            r = generer_rapport(conn, charger_profil(), motif=args.motif)
        except RapportNonConforme as e:
            print(f"✗ {e}")
            return 1
    d = r.synthese.decision
    print(f"✓ Rapport écrit : {r.chemin}")
    print(f"  Décision recommandée : {LIBELLES_OPTIONS[d.option]} (confiance {d.confiance})")
    print("  Traçabilité : chaque phrase porte une preuve vérifiée (contrôle passé)")
    print("  Révisions : " + ("; ".join(r.changements) if r.changements else "aucune conclusion n'a changé"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
