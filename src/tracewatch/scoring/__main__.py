"""Lance l'étape 5 : python -m tracewatch.scoring

Calcule les 3 scores, puis compare la qualité du corpus complet et du corpus resserré.
"""

from __future__ import annotations

import argparse
import sys

from tracewatch.collecte.commun import charger_profil
from tracewatch.db import get_connection, init_db
from tracewatch.scoring.qualite_corpus import Filtre, QualiteCorpus, calculer_scores, evaluer, filtrer


def afficher(titre: str, q: QualiteCorpus) -> None:
    print(f"\n== {titre} : qualité {q.niveau.upper()}")
    print(f"  documents={q.documents}  travaux distincts={q.travaux_distincts}  "
          f"bruit={q.part_bruit:.0%}  récents={q.part_recente:.0%}  indépendants/scientifiques={q.part_independante:.0%}")
    print("  familles : " + ", ".join(f"{k} {v}" for k, v in q.par_famille.items()))
    for a in q.alertes:
        print(f"  ⚠ {a}")


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Scoring et qualité du corpus TraceWatch")
    parser.add_argument("--db", default=None)
    args = parser.parse_args(argv)

    profil = charger_profil()
    chemin = init_db(args.db)
    with get_connection(chemin) as conn:
        n = calculer_scores(conn, profil)
        print(f"Scores calculés pour {n} documents (pertinence | fraîcheur | fiabilité, séparés)")

        afficher("Corpus complet", evaluer(filtrer(conn), profil))
        seuil = profil["qualite_corpus"]["seuil_pertinence_min"]
        resserre = Filtre(pertinence_min=seuil, un_par_travail=True)
        afficher(f"Corpus resserré (pertinence ≥ {seuil}, un document par travail)",
                 evaluer(filtrer(conn, resserre), profil))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
