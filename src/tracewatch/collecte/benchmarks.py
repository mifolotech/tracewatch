"""Collecte des classements de benchmarks : SWE-bench, WebArena (étape 3, responsable B).

Une entrée de classement = un document. Le texte précise si le résultat est
vérifié par l'équipe du benchmark ou auto-déclaré : c'est utile pour comparer
affirmations des fournisseurs et sources indépendantes (scénario 3).
Famille : benchmark.
"""

from __future__ import annotations

import csv
import io
import json
import re
import sqlite3

from tracewatch.collecte.commun import Bilan, Document, Http, vers_iso

EXPERIMENTS = "https://github.com/SWE-bench/experiments/tree/main/evaluation"


def _slug(texte: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", texte.lower()).strip("-")


def _swebench(conn, profil, http: Http, conf: dict, bilan: Bilan) -> None:
    page = http.get(conf["url"]).text
    m = re.search(r'<script[^>]*id="leaderboard-data"[^>]*>(.*?)</script>', page, re.S)
    if not m:
        raise ValueError("données du classement introuvables (la page a changé ?)")
    voulus = {c.lower() for c in conf.get("classements", [])}
    for classement in json.loads(m.group(1)):
        nom_lb = classement["name"]
        if voulus and nom_lb.lower() not in voulus:
            continue
        for e in classement["results"]:
            # Le dossier de soumission officiel : s3://swe-bench-submissions/<split>/<dossier>/logs
            split = (e.get("logs") or "").split("/")[3:4] or [nom_lb.lower()]
            verifie = "yes" if e.get("checked") else "no (self-reported by submitter)"
            texte = (
                f"{e['name']} resolved {e.get('resolved')}% of SWE-bench {nom_lb} tasks. "
                f"Agent: {e.get('agent') or 'n/a'} by {e.get('agent_org') or 'n/a'}. "
                f"Model: {e.get('model_display') or 'n/a'} by {e.get('model_org') or 'n/a'}. "
                f"Submitted on {e.get('date')}. Verified by the SWE-bench team: {verifie}. "
                f"Open-source model: {e.get('os_model')}. Open-source system: {e.get('os_system')}. "
                f"Cost: {e.get('cost')}. Warning: {e.get('warning') or 'none'}. "
                f"Website: {e.get('site') or 'n/a'}."
            )
            bilan.ajouter(
                conn,
                Document(
                    url=f"{EXPERIMENTS}/{split[0]}/{e['folder']}",
                    title=f"SWE-bench {nom_lb} : {e['name']} ({e.get('resolved')} %)",
                    text=texte,
                    authors=[],
                    organization=e.get("agent_org") or e.get("model_org"),
                    published_date=vers_iso(e.get("date")),
                    source_family=conf["source_family"],
                    source_name=f"SWE-bench leaderboard ({nom_lb})",
                ),
                profil,
            )


def _webarena(conn, profil, http: Http, conf: dict, bilan: Bilan) -> None:
    contenu = http.get(conf["url_csv"]).content.decode("utf-8")
    lignes = list(csv.reader(io.StringIO(contenu)))
    for ligne in lignes[1:]:
        # Colonnes : date (MM/AAAA), Open?, taille, Model, Success Rate, Result Source, Work, Traj, Note
        if len(ligne) < 7 or not ligne[3].strip():
            continue
        quand, ouvert, _taille, modele, taux, origine, travail = (c.strip() for c in ligne[:7])
        note = ligne[8].strip() if len(ligne) > 8 else ""
        auto = "self-reported" if "self" in origine.lower() else f"reported by {origine or 'n/a'}"
        texte = (
            f"{modele} achieved a {taux}% success rate on WebArena ({quand}). "
            f"Result source: {auto}. Work: {travail or 'n/a'}. "
            f"Open model: {'yes' if ouvert == '✔' else 'no'}. {('Note: ' + note) if note else ''}"
        ).strip()
        bilan.ajouter(
            conn,
            Document(
                url=f"{conf['url']}#{_slug(modele)}-{_slug(quand)}",
                title=f"WebArena : {modele} ({taux} %)",
                text=texte,
                organization=travail or None,
                published_date=vers_iso(quand),
                source_family=conf["source_family"],
                source_name="WebArena leaderboard",
            ),
            profil,
        )


def collecter(conn: sqlite3.Connection, profil: dict, http: Http) -> Bilan:
    conf = profil["sources"]["benchmarks"]
    bilan = Bilan("benchmarks")
    for lb in conf["leaderboards"]:
        lb = {"source_family": conf["source_family"], **lb}
        try:
            if lb["nom"] == "SWE-bench":
                _swebench(conn, profil, http, lb, bilan)
            elif lb["nom"] == "WebArena":
                _webarena(conn, profil, http, lb, bilan)
            else:
                bilan.erreurs.append(f"{lb['nom']}: pas de collecteur pour ce classement")
        except Exception as e:
            bilan.erreurs.append(f"{lb['nom']}: {e}")
    return bilan
