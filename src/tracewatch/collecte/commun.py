"""Boîte à outils partagée par tous les collecteurs (étape 3).

- charger_profil()   : lit config/profil_veille.yaml
- Http               : téléchargements polis (pause par site, nouvel essai si erreur)
- vers_iso()         : convertit n'importe quelle date en AAAA-MM-JJ
- dans_horizon()     : la date est-elle dans l'horizon de veille ?
- contient_mot_cle() : le texte parle-t-il de notre sujet ?
- enregistrer()      : range un document dans la base (ignoré si l'URL existe déjà)
"""

from __future__ import annotations

import html
import json
import os
import re
import sqlite3
import time
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from urllib.parse import urlparse

import requests
import yaml
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from tracewatch.db import PROJECT_ROOT, SOURCE_FAMILIES

PROFIL_PATH = PROJECT_ROOT / "config" / "profil_veille.yaml"
USER_AGENT = "TraceWatch/0.1 (projet etudiant de veille technologique)"
TEXTE_MAX = 50_000  # on tronque les textes très longs (README, pages)

load_dotenv(PROJECT_ROOT / ".env")


def charger_profil() -> dict:
    with open(PROFIL_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def env(nom: str) -> str | None:
    """Valeur d'une variable du .env, ou None si absente/vide."""
    valeur = os.getenv(nom, "").strip()
    return valeur or None


# ---------------------------------------------------------------------
# Téléchargement
# ---------------------------------------------------------------------
class Http:
    """Session HTTP partagée : pause minimale par site + nouvels essais automatiques."""

    def __init__(self, pauses: dict[str, float] | None = None, pause_defaut: float = 1.0):
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        essais = Retry(
            total=4,
            backoff_factor=2,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET",),
            respect_retry_after_header=True,
        )
        self.session.mount("https://", HTTPAdapter(max_retries=essais))
        self.session.mount("http://", HTTPAdapter(max_retries=essais))
        self.pauses = pauses or {}
        self.pause_defaut = pause_defaut
        self._dernier_appel: dict[str, float] = {}

    def get(self, url: str, **kwargs) -> requests.Response:
        hote = urlparse(url).netloc
        pause = self.pauses.get(hote, self.pause_defaut)
        attente = self._dernier_appel.get(hote, 0) + pause - time.monotonic()
        if attente > 0:
            time.sleep(attente)
        kwargs.setdefault("timeout", 30)
        try:
            reponse = self.session.get(url, **kwargs)
        finally:
            self._dernier_appel[hote] = time.monotonic()
        reponse.raise_for_status()
        return reponse


# ---------------------------------------------------------------------
# Dates
# ---------------------------------------------------------------------
def vers_iso(valeur) -> str | None:
    """Convertit une date (str, datetime, struct_time, 20251217, '09/2026'...) en 'AAAA-MM-JJ'."""
    if valeur is None or valeur == "":
        return None
    if isinstance(valeur, datetime):
        return valeur.date().isoformat()
    if isinstance(valeur, date):
        return valeur.isoformat()
    if isinstance(valeur, time.struct_time):
        return date(valeur.tm_year, valeur.tm_mon, valeur.tm_mday).isoformat()
    if isinstance(valeur, int):
        valeur = str(valeur)
    texte = str(valeur).strip()
    if re.fullmatch(r"\d{8}", texte):  # 20251217
        return f"{texte[:4]}-{texte[4:6]}-{texte[6:]}"
    m = re.fullmatch(r"(\d{1,2})/(\d{4})", texte)  # 09/2026
    if m:
        return f"{m.group(2)}-{int(m.group(1)):02d}-01"
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", texte)  # 2025-12-05T...
    if m:
        return m.group(0)
    m = re.fullmatch(r"(\d{4})", texte)
    if m:
        return f"{texte}-01-01"
    return None


def maintenant_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def dans_horizon(date_iso: str | None, profil: dict) -> bool:
    """Garde les documents sans date (on ne sait pas) et ceux >= annee_min_contexte."""
    if not date_iso:
        return True
    return int(date_iso[:4]) >= profil["horizon"]["annee_min_contexte"]


# ---------------------------------------------------------------------
# Texte
# ---------------------------------------------------------------------
def nettoyer_html(texte: str | None) -> str:
    if not texte:
        return ""
    texte = re.sub(r"<(script|style)\b.*?</\1>", " ", texte, flags=re.S | re.I)
    texte = re.sub(r"<[^>]+>", " ", texte)
    return re.sub(r"\s+", " ", html.unescape(texte)).strip()


def _motif(mot: str) -> re.Pattern:
    # Bornes de mot souples : "agent" trouve "agents" mais pas "reagent"
    return re.compile(r"(?<![A-Za-z0-9])" + re.escape(mot.lower()), re.I)


def contient_mot_cle(texte: str, mots: list[str]) -> bool:
    texte = texte.lower()
    return any(_motif(m).search(texte) for m in mots)


# ---------------------------------------------------------------------
# Enregistrement
# ---------------------------------------------------------------------
@dataclass
class Document:
    """Document brut au format du contrat de données (ARCHITECTURE.md §5).

    canonical_url, content_hash et cluster_id sont remplis à l'étape 4.
    """

    url: str
    title: str
    source_family: str
    source_name: str
    text: str = ""
    authors: list[str] = field(default_factory=list)
    organization: str | None = None
    published_date: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None


def enregistrer(conn: sqlite3.Connection, doc: Document) -> bool:
    """Insère le document. Renvoie True s'il est nouveau, False si l'URL existe déjà."""
    if doc.source_family not in SOURCE_FAMILIES:
        raise ValueError(f"Famille de source inconnue : {doc.source_family}")
    if not doc.url or not doc.title:
        raise ValueError("Un document doit avoir une URL et un titre")
    curseur = conn.execute(
        """INSERT OR IGNORE INTO documents
           (url, title, text, authors, organization, published_date, collected_date,
            source_family, source_name, doi, arxiv_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            doc.url.strip(),
            doc.title.strip()[:500],
            (doc.text or "")[:TEXTE_MAX],
            json.dumps(doc.authors, ensure_ascii=False),
            doc.organization,
            doc.published_date,
            maintenant_iso(),
            doc.source_family,
            doc.source_name,
            doc.doi,
            doc.arxiv_id,
        ),
    )
    return curseur.rowcount == 1


@dataclass
class Bilan:
    """Compteurs d'un collecteur, affichés à la fin."""

    source: str
    trouves: int = 0
    nouveaux: int = 0
    deja_la: int = 0
    hors_sujet: int = 0
    hors_horizon: int = 0
    erreurs: list[str] = field(default_factory=list)

    def ajouter(self, conn: sqlite3.Connection, doc: Document, profil: dict) -> None:
        self.trouves += 1
        if not dans_horizon(doc.published_date, profil):
            self.hors_horizon += 1
        elif enregistrer(conn, doc):
            self.nouveaux += 1
        else:
            self.deja_la += 1

    def __str__(self) -> str:
        txt = (
            f"{self.source:<11} trouvés={self.trouves:<4} nouveaux={self.nouveaux:<4} "
            f"déjà en base={self.deja_la:<4} hors horizon={self.hors_horizon:<3} "
            f"hors sujet={self.hors_sujet}"
        )
        if self.erreurs:
            txt += f"  ⚠ {len(self.erreurs)} erreur(s)"
        return txt
