"""Collecte des publications OpenAlex (étape 3, responsable B).

API : https://api.openalex.org/works
Sans clé, le budget gratuit est partagé. Clé gratuite facultative : OPENALEX_API_KEY dans .env.
Famille : publication.
"""

from __future__ import annotations

import re
import sqlite3

from tracewatch.collecte.commun import Bilan, Document, Http, env, nettoyer_html, vers_iso

API = "https://api.openalex.org/works"
CHAMPS = (
    "id,doi,title,publication_date,abstract_inverted_index,authorships,"
    "primary_location,locations,ids"
)


def reconstruire_resume(index_inverse: dict | None) -> str:
    """OpenAlex stocke le résumé sous forme {mot: [positions]} : on le remet dans l'ordre."""
    if not index_inverse:
        return ""
    positions = {pos: mot for mot, liste in index_inverse.items() for pos in liste}
    return " ".join(positions[i] for i in sorted(positions))


def _arxiv_id(oeuvre: dict) -> str | None:
    for loc in oeuvre.get("locations") or []:
        url = (loc or {}).get("landing_page_url") or ""
        m = re.search(r"arxiv\.org/abs/([\w.\-/]+?)(?:v\d+)?$", url)
        if m:
            return m.group(1)
    return None


def collecter(conn: sqlite3.Connection, profil: dict, http: Http) -> Bilan:
    conf = profil["sources"]["openalex"]
    bilan = Bilan("openalex")
    annee_min = profil["horizon"]["annee_min_contexte"]
    params_communs = {
        "filter": f"from_publication_date:{annee_min}-01-01",
        "per-page": conf["max_resultats_par_requete"],
        "select": CHAMPS,
    }
    if env("OPENALEX_API_KEY"):
        params_communs["api_key"] = env("OPENALEX_API_KEY")
    if env("OPENALEX_EMAIL"):
        params_communs["mailto"] = env("OPENALEX_EMAIL")

    for requete in conf["requetes"]:
        try:
            reponse = http.get(API, params={**params_communs, "search": requete})
        except Exception as e:
            bilan.erreurs.append(f"{requete}: {e}")
            continue
        for oeuvre in reponse.json().get("results", []):
            if not oeuvre.get("title"):
                continue
            doi = (oeuvre.get("doi") or "").replace("https://doi.org/", "") or None
            loc = oeuvre.get("primary_location") or {}
            source = (loc.get("source") or {}).get("display_name")
            auteurs = oeuvre.get("authorships") or []
            institutions = [
                i.get("display_name") for a in auteurs for i in (a.get("institutions") or [])
            ]
            url = (
                oeuvre.get("doi")
                or loc.get("landing_page_url")
                or oeuvre["id"]  # https://openalex.org/W...
            )
            bilan.ajouter(
                conn,
                Document(
                    url=url,
                    title=nettoyer_html(oeuvre["title"]),
                    text=reconstruire_resume(oeuvre.get("abstract_inverted_index")),
                    authors=[(a.get("author") or {}).get("display_name", "") for a in auteurs],
                    organization=institutions[0] if institutions else None,
                    published_date=vers_iso(oeuvre.get("publication_date")),
                    source_family=conf["source_family"],
                    source_name=f"OpenAlex ({source})" if source else "OpenAlex",
                    doi=doi,
                    arxiv_id=_arxiv_id(oeuvre),
                ),
                profil,
            )
    return bilan
