"""Jeu de démo figé et reproductible (étape 9).

Le jeu de démo = data/demo/ (versionné dans Git) :
  - documents.json : un échantillon de documents RÉELS de la base (tous ceux analysés
    par l'IA + leurs doublons + des documents pertinents et du bruit pour chaque famille)
  - cache_llm/     : les réponses du LLM pour ces documents
  - manifeste.json : date de référence (fraîcheur figée), modèle, compteurs

Reconstruire la démo (sans clé, sans réseau, résultat identique à chaque fois) :
    python -m tracewatch.demo
    -> data/demo/tracewatch_demo.db + rapports/demo/dernier_rapport.md

Refiger la démo depuis la base réelle (après de nouvelles analyses) :
    python -m tracewatch.demo --exporter
"""

from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import sys
from datetime import date

from tracewatch.analyse.extraction import BilanExtraction, analyser_document, construire_prompt
from tracewatch.analyse.llm_client import CACHE_DEFAUT, ClientLLM
from tracewatch.analyse.verification import reverifier
from tracewatch.collecte.commun import charger_profil
from tracewatch.db import PROJECT_ROOT, get_connection, init_db
from tracewatch.normalisation.clusters import executer as regrouper
from tracewatch.rapport.generateur import ResultatRapport, generer_rapport
from tracewatch.scoring.qualite_corpus import calculer_scores

DEMO = PROJECT_ROOT / "data" / "demo"
DOCUMENTS = DEMO / "documents.json"
CACHE_DEMO = DEMO / "cache_llm"
MANIFESTE = DEMO / "manifeste.json"
BASE_DEMO = DEMO / "tracewatch_demo.db"
RAPPORTS_DEMO = PROJECT_ROOT / "rapports" / "demo"

CHAMPS = ("url", "title", "text", "authors", "organization", "published_date", "collected_date",
          "source_family", "source_name", "doi", "arxiv_id")
PAR_FAMILLE_PERTINENTS = 15
PAR_FAMILLE_BRUIT = 5
CLUSTERS_EN_PLUS = 5


def _modele(profil: dict) -> str:
    return f"{profil['analyse'].get('fournisseur', 'gemini')}/{profil['analyse']['modele']}"


def exporter(conn: sqlite3.Connection, profil: dict) -> dict:
    """Fige un échantillon de la base réelle et les réponses LLM correspondantes."""
    client = ClientLLM(None, _modele(profil), CACHE_DEFAUT)
    tronque = profil["analyse"]["longueur_max_document"]
    docs = {d["id"]: d for d in conn.execute(
        "SELECT d.*, s.pertinence FROM documents d LEFT JOIN scores s ON s.document_id = d.id")}

    # 1. Documents dont l'analyse IA est en cache (avec ou sans affirmation)
    analyses = {i for i, d in docs.items() if client._chemin(construire_prompt(d, profil)).exists()}
    choisis = set(analyses)
    # 2. Leurs doublons + quelques autres groupes de doublons (scénario 1)
    clusters = {docs[i]["cluster_id"] for i in analyses}
    clusters |= {r[0] for r in conn.execute(
        "SELECT cluster_id FROM clusters WHERE taille > 1 ORDER BY taille DESC, cluster_id LIMIT ?",
        (CLUSTERS_EN_PLUS,))}
    choisis |= {i for i, d in docs.items() if d["cluster_id"] in clusters}
    # 3. Par famille : des documents pertinents et du bruit (scénarios 2 et 4)
    seuil = profil["qualite_corpus"]["seuil_pertinence_min"]
    for famille in {d["source_family"] for d in docs.values()}:
        candidats = sorted((d for d in docs.values() if d["source_family"] == famille and d["id"] not in choisis),
                           key=lambda d: -(d["pertinence"] or 0))
        choisis |= {d["id"] for d in [d for d in candidats if (d["pertinence"] or 0) >= seuil][:PAR_FAMILLE_PERTINENTS]}
        choisis |= {d["id"] for d in [d for d in candidats if (d["pertinence"] or 0) < seuil][:PAR_FAMILLE_BRUIT]}

    # Le texte est tronqué comme dans le prompt : la réponse en cache reste valable
    sortie = []
    for i in sorted(choisis):
        d = dict(docs[i])
        d["text"] = (d["text"] or "")[:tronque]
        d["authors"] = json.loads(d["authors"] or "[]")
        sortie.append({k: d[k] for k in CHAMPS})

    if CACHE_DEMO.exists():
        shutil.rmtree(CACHE_DEMO)
    CACHE_DEMO.mkdir(parents=True)
    for i in analyses:
        src = client._chemin(construire_prompt(docs[i], profil))
        shutil.copy2(src, CACHE_DEMO / src.name)

    DEMO.mkdir(parents=True, exist_ok=True)
    DOCUMENTS.write_text(json.dumps(sortie, ensure_ascii=False, indent=1), encoding="utf-8")
    manifeste = {
        "date_export": date.today().isoformat(),
        "date_reference_fraicheur": date.today().isoformat(),
        "modele": _modele(profil),
        "documents": len(sortie),
        "documents_analyses": len(analyses),
    }
    MANIFESTE.write_text(json.dumps(manifeste, ensure_ascii=False, indent=1), encoding="utf-8")
    return manifeste


def construire(profil: dict, chemin_base=BASE_DEMO, dossier_rapports=RAPPORTS_DEMO) -> ResultatRapport:
    """Reconstruit la démo de zéro : base -> doublons -> scores -> analyse (cache) -> rapport."""
    manifeste = json.loads(MANIFESTE.read_text(encoding="utf-8"))
    documents = json.loads(DOCUMENTS.read_text(encoding="utf-8"))
    for suffixe in ("", "-journal", "-wal", "-shm"):
        chemin = chemin_base.parent / (chemin_base.name + suffixe)
        if chemin.exists():
            chemin.unlink()

    with get_connection(init_db(chemin_base)) as conn:
        conn.executemany(
            f"INSERT INTO documents ({', '.join(CHAMPS)}) VALUES ({', '.join('?' * len(CHAMPS))})",
            [tuple(json.dumps(d[k], ensure_ascii=False) if k == "authors" else d[k] for k in CHAMPS)
             for d in documents],
        )
        regrouper(conn, profil)
        calculer_scores(conn, profil, reference=date.fromisoformat(manifeste["date_reference_fraicheur"]))

        client = ClientLLM(None, manifeste["modele"], CACHE_DEMO)  # cache seul : pas de clé, pas de réseau
        bilan = BilanExtraction()
        for doc in conn.execute("SELECT * FROM documents ORDER BY id").fetchall():
            if client._chemin(construire_prompt(doc, profil)).exists():
                analyser_document(conn, client, doc, profil, bilan)
        conn.commit()
        reverifier(conn, profil["analyse"]["longueur_min_citation"])
        return generer_rapport(conn, profil, motif="construction de la démo", dossier=dossier_rapports)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Jeu de démo TraceWatch")
    parser.add_argument("--exporter", action="store_true", help="refiger la démo depuis la base réelle")
    args = parser.parse_args(argv)
    profil = charger_profil()

    if args.exporter:
        with get_connection(init_db()) as conn:
            m = exporter(conn, profil)
        print(f"✓ Démo figée dans {DEMO} : {m['documents']} documents, dont {m['documents_analyses']} "
              f"avec analyse IA en cache ({m['modele']}).")
        return 0

    r = construire(profil)
    s = r.synthese.stats
    print(f"✓ Démo reconstruite sans clé ni réseau : {BASE_DEMO}")
    print(f"  {s['documents']} documents, {s['travaux']} travaux distincts, {s['familles']} familles, "
          f"{s['verifiees']} preuves vérifiées")
    print(f"  Décision : {r.synthese.decision.option} (confiance {r.synthese.decision.confiance})")
    print(f"  Rapport : {r.chemin}")
    print("  Tableau de bord sur la démo : choisir « Démo » dans la barre latérale.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
