"""Format unique de document (étape 4, responsable C).

Complète les champs du contrat de données que la collecte laisse vides :
- canonical_url : URL normalisée (https, sans www, sans paramètres de pistage...)
- doi           : en minuscules, sans préfixe https://doi.org/
- arxiv_id      : déduit du DOI arXiv (10.48550/arXiv.XXXX) ou de l'URL arXiv
- content_hash  : empreinte du titre + texte normalisés
"""

from __future__ import annotations

import hashlib
import re
import sqlite3
import unicodedata
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

# Paramètres d'URL qui ne changent pas le contenu (pistage, partage)
PARAMS_PISTAGE = re.compile(
    r"^(utm_\w+|fbclid|gclid|mc_cid|mc_eid|ref|ref_src|source|s|si|share|cmpid|igshid)$", re.I
)
ARXIV_URL = re.compile(r"arxiv\.org/(?:abs|pdf)/([\w.\-/]+?)(?:v\d+)?(?:\.pdf)?$", re.I)
ARXIV_DOI = re.compile(r"^10\.48550/arxiv\.(.+)$", re.I)


def normaliser_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    doi = re.sub(r"^(https?://)?(dx\.)?doi\.org/", "", doi.strip(), flags=re.I)
    return doi.lower() or None


def arxiv_depuis(url: str | None, doi: str | None) -> str | None:
    """Retrouve l'identifiant arXiv à partir d'une URL ou d'un DOI arXiv."""
    m = ARXIV_DOI.match(doi or "")
    if m:
        return re.sub(r"v\d+$", "", m.group(1))
    m = ARXIV_URL.search(url or "")
    return m.group(1) if m else None


def url_canonique(url: str) -> str:
    """Deux URL qui mènent au même contenu donnent la même URL canonique.

    Le fragment (#...) est GARDÉ : certaines sources (classement WebArena)
    l'utilisent pour distinguer des entrées différentes de la même page.
    """
    url = url.strip()
    arxiv = ARXIV_URL.search(url)
    if arxiv:
        return f"https://arxiv.org/abs/{arxiv.group(1)}"
    doi = re.match(r"^(https?://)?(dx\.)?doi\.org/(.+)$", url, re.I)
    if doi:
        return f"https://doi.org/{doi.group(3).lower()}"

    parts = urlsplit(url)
    hote = parts.netloc.lower().removeprefix("www.")
    chemin = re.sub(r"/+", "/", parts.path).rstrip("/") or "/"
    params = sorted(
        (k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if not PARAMS_PISTAGE.match(k)
    )
    return urlunsplit(("https", hote, chemin, urlencode(params), parts.fragment))


def texte_normalise(texte: str) -> str:
    """Minuscules, sans accents, sans ponctuation, espaces uniques."""
    texte = unicodedata.normalize("NFKD", texte or "")
    texte = "".join(c for c in texte if not unicodedata.combining(c)).lower()
    texte = re.sub(r"[^\w\s]", " ", texte)
    return re.sub(r"\s+", " ", texte).strip()


def empreinte(titre: str, texte: str) -> str:
    return hashlib.sha256(texte_normalise(f"{titre} {texte}").encode("utf-8")).hexdigest()


def normaliser_documents(conn: sqlite3.Connection) -> int:
    """Remplit canonical_url, doi, arxiv_id et content_hash pour tous les documents."""
    lignes = conn.execute("SELECT id, url, title, text, doi, arxiv_id FROM documents").fetchall()
    for d in lignes:
        doi = normaliser_doi(d["doi"])
        conn.execute(
            "UPDATE documents SET canonical_url=?, doi=?, arxiv_id=?, content_hash=? WHERE id=?",
            (
                url_canonique(d["url"]),
                doi,
                d["arxiv_id"] or arxiv_depuis(d["url"], doi),
                empreinte(d["title"], d["text"] or ""),
                d["id"],
            ),
        )
    return len(lignes)
