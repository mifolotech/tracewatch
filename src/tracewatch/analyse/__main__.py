"""Lance l'étape 6 : python -m tracewatch.analyse [--max N]

1. Choisit les documents à analyser : les plus pertinents de chaque famille,
   un seul par travail (cluster), avec assez de texte (quotas dans le profil).
2. Fait extraire les affirmations par le LLM (cache d'abord), vérifie chaque citation.
3. Affiche : taux de citations vérifiées, rejets, contradictions, niveaux de preuve.

Relançable : un document déjà analysé par le même modèle est sauté.
Si le quota gratuit est épuisé, on s'arrête proprement : relancer plus tard.
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
import time
from collections import Counter

from tracewatch.analyse.contradictions import detecter
from tracewatch.analyse.extraction import BilanExtraction, analyser_document, deja_analyse
from tracewatch.analyse.llm_client import LLMIndisponible, QuotaDepasse, creer_client, creer_client_modele
from tracewatch.analyse.verification import reverifier
from tracewatch.collecte.commun import charger_profil
from tracewatch.db import get_connection, init_db
from tracewatch.scoring.qualite_corpus import Filtre, filtrer


def selectionner(conn: sqlite3.Connection, profil: dict) -> list[sqlite3.Row]:
    conf = profil["analyse"]
    seuil = profil["qualite_corpus"]["seuil_pertinence_min"]
    par_famille = []
    for famille, quota in conf["selection"].items():
        docs = filtrer(conn, Filtre(pertinence_min=seuil, familles=[famille], un_par_travail=True))
        docs = [d for d in docs if len(d["text"] or "") >= conf["longueur_min_document"]]
        par_famille.append(docs[:quota])
    # On alterne les familles (1 publication, 1 indépendant, 1 fournisseur...) : si le quota
    # gratuit coupe l'analyse en route, ce qui est fait reste équilibré entre les familles.
    choisis = []
    for rang in range(max((len(l) for l in par_famille), default=0)):
        choisis += [l[rang] for l in par_famille if rang < len(l)]
    return choisis


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Analyse contrôlée par IA TraceWatch")
    parser.add_argument("--db", default=None)
    parser.add_argument("--max", type=int, default=None, help="nombre maximum de documents à analyser")
    args = parser.parse_args(argv)

    profil = charger_profil()
    client = creer_client(profil)
    # Modèles de secours : chacun a son propre quota gratuit. Quand le quota du modèle
    # courant est épuisé, on bascule sur le suivant (le modèle reste tracé dans claims.modele).
    secours = list(profil["analyse"].get("modeles_secours", []))
    mode = "LLM + cache" if client.fournisseur else "CACHE SEUL (pas de clé)"
    print(f"Modèle : {client.nom}  |  mode : {mode}  |  cache : {client.cache}"
          + (f"  |  secours : {', '.join(secours)}" if secours and client.fournisseur else ""))
    appels_total, cache_total = 0, 0

    bilan = BilanExtraction()
    with get_connection(init_db(args.db)) as conn:
        docs = selectionner(conn, profil)
        a_faire = [d for d in docs if not deja_analyse(conn, d["id"])]
        if args.max is not None:
            a_faire = a_faire[: args.max]
        print(f"Documents sélectionnés : {len(docs)}  |  déjà analysés : {len(docs) - len(a_faire) if args.max is None else '…'}"
              f"  |  à analyser maintenant : {len(a_faire)}\n")

        i, arret, erreurs_reseau = 0, False, 0
        while i < len(a_faire) and not arret:
            doc = a_faire[i]
            print(f"  [{i + 1}/{len(a_faire)}] {doc['source_family']:<12} {doc['title'][:70]}", flush=True)
            avant = client.appels
            try:
                analyser_document(conn, client, doc, profil, bilan)
                conn.commit()
                i += 1
            except QuotaDepasse as e:
                appels_total += client.appels
                cache_total += client.depuis_cache
                if client.fournisseur and secours:
                    suivant = secours.pop(0)
                    print(f"    ⇄ quota de {client.nom} épuisé : bascule sur gemini/{suivant}")
                    client = creer_client_modele(profil, suivant)
                    continue  # on réessaie le même document avec le modèle suivant
                print(f"\n⏸ Quota gratuit atteint : arrêt propre. Relancer plus tard, le travail fait est gardé.\n  ({e})")
                arret = True
                continue
            except LLMIndisponible as e:
                print(f"    ↷ ignoré : {e}")
                i += 1
                continue
            except Exception as e:  # une réponse illisible ne bloque pas l'analyse
                print(f"    ⚠ erreur sur ce document : {type(e).__name__}: {str(e)[:150]}")
                i += 1
                if any(m in type(e).__name__ for m in ("Connect", "Protocol", "Timeout")):
                    erreurs_reseau += 1
                    if erreurs_reseau >= 3:
                        print("\n⏸ Connexion Internet perdue (3 erreurs réseau d'affilée) : arrêt propre. "
                              "Relancer quand la connexion revient, le travail fait est gardé.")
                        arret = True
                continue
            erreurs_reseau = 0
            if client.appels > avant:
                time.sleep(profil["analyse"]["pause_entre_appels"])

        changes = reverifier(conn, profil["analyse"]["longueur_min_citation"])
        if changes:
            print(f"\n↻ {changes} citation(s) au statut mis à jour par les règles de vérification actuelles")
        client.appels += appels_total
        client.depuis_cache += cache_total
        afficher_bilan(conn, profil, bilan, client)
    return 0


def afficher_bilan(conn, profil, bilan: BilanExtraction, client) -> None:
    print(f"\n== Cette exécution : {bilan.documents} documents, {client.appels} appels LLM, "
          f"{client.depuis_cache} réponses depuis le cache")
    if bilan.proposees:
        print(f"   affirmations proposées : {bilan.proposees}  |  citations vérifiées : {bilan.verifiees} "
              f"({bilan.verifiees / bilan.proposees:.0%})  |  rejetées : {len(bilan.rejetees)}")
        for titre, citation in bilan.rejetees[:5]:
            print(f"   ✗ rejetée ({titre[:40]}) : « {citation[:90]} »")

    total = conn.execute("SELECT COUNT(*), SUM(citation_verifiee) FROM claims").fetchone()
    print(f"\n== Base : {total[0]} affirmations, dont {total[1] or 0} à citation vérifiée "
          f"(seules celles-ci pourront entrer dans le rapport)")
    cats = Counter(r[0] for r in conn.execute("SELECT categorie FROM claims WHERE citation_verifiee=1"))
    print("   par catégorie : " + ", ".join(f"{k} {v}" for k, v in cats.most_common()))

    print("\n== Contradictions détectées")
    divergences = detecter(conn, profil)
    if not divergences:
        print("   aucune pour l'instant")
    for d in divergences:
        po, pc = d.preuve_optimistes, d.preuve_critiques
        print(f"   [{d.type}] thème « {d.theme} »")
        print(f"      optimistes : {len(d.optimistes)} affirmations, preuve {po.niveau} "
              f"({po.sources_independantes} sources indépendantes, {po.sources_fournisseurs} fournisseurs)")
        print(f"      critiques  : {len(d.critiques)} affirmations, preuve {pc.niveau} "
              f"({pc.sources_independantes} sources indépendantes, {pc.sources_fournisseurs} fournisseurs)")


if __name__ == "__main__":
    raise SystemExit(main())
