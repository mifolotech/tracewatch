"""Collecte GitHub : projets d'agents et issues sur les échecs (étape 3, responsable B).

API : https://api.github.com
Sans jeton : 60 requêtes/heure et 10 recherches/minute. Jeton facultatif : GITHUB_TOKEN dans .env.
Famille : depot.
"""

from __future__ import annotations

import sqlite3

from tracewatch.collecte.commun import Bilan, Document, Http, env, vers_iso

API = "https://api.github.com"


def _entetes(raw: bool = False) -> dict:
    h = {"Accept": "application/vnd.github.raw" if raw else "application/vnd.github+json"}
    if env("GITHUB_TOKEN"):
        h["Authorization"] = f"Bearer {env('GITHUB_TOKEN')}"
    return h


def _depot(conn, profil, http: Http, nom: str, famille: str, bilan: Bilan) -> None:
    info = http.get(f"{API}/repos/{nom}", headers=_entetes()).json()
    try:
        readme = http.get(f"{API}/repos/{nom}/readme", headers=_entetes(raw=True)).text
    except Exception:
        readme = ""
    description = info.get("description") or ""
    bilan.ajouter(
        conn,
        Document(
            url=info["html_url"],
            title=f"{info['full_name']} : {description}".strip(" :"),
            text=f"{description}\n\n{readme}".strip(),
            authors=[info["owner"]["login"]],
            organization=info["owner"]["login"],
            published_date=vers_iso(info.get("created_at")),
            source_family=famille,
            source_name=f"GitHub ({info['full_name']})",
        ),
        profil,
    )


def _issues(conn, profil, http: Http, conf: dict, recherche: str, bilan: Bilan) -> None:
    annee_min = profil["horizon"]["annee_min_contexte"]
    depots = " ".join(f"repo:{d}" for d in conf["depots"])
    q = f"{recherche} is:issue created:>={annee_min}-01-01 {depots}"
    resultat = http.get(
        f"{API}/search/issues",
        params={"q": q, "per_page": conf["max_issues_par_requete"], "sort": "reactions"},
        headers=_entetes(),
    ).json()
    for issue in resultat.get("items", []):
        depot = issue["repository_url"].split("/repos/", 1)[-1]
        bilan.ajouter(
            conn,
            Document(
                url=issue["html_url"],
                title=issue["title"],
                text=issue.get("body") or "",
                authors=[issue["user"]["login"]],
                organization=depot.split("/")[0],
                published_date=vers_iso(issue.get("created_at")),
                source_family=conf["source_family"],
                source_name=f"GitHub issues ({depot})",
            ),
            profil,
        )


def collecter(conn: sqlite3.Connection, profil: dict, http: Http) -> Bilan:
    conf = profil["sources"]["github"]
    bilan = Bilan("github")
    for nom in conf["depots"]:
        try:
            _depot(conn, profil, http, nom, conf["source_family"], bilan)
        except Exception as e:
            bilan.erreurs.append(f"{nom}: {e}")
    for recherche in conf["recherche_issues"]:
        try:
            _issues(conn, profil, http, conf, recherche, bilan)
        except Exception as e:
            bilan.erreurs.append(f"issues '{recherche}': {e}")
    return bilan
