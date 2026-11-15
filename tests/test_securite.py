"""Étape 9 : aucun secret dans les fichiers destinés au dépôt Git.

Les fichiers contrôlés sont ceux que Git enverrait : suivis + nouveaux non ignorés.
En cas d'échec, le test affiche le FICHIER et le TYPE de secret, jamais sa valeur.
"""

from __future__ import annotations

import re
import subprocess

import pytest
from dotenv import dotenv_values

from tracewatch.db import PROJECT_ROOT

MOTIFS = {
    "clé Google (AIza...)": re.compile(r"AIza[0-9A-Za-z_\-]{30,}"),
    "clé Google (AQ....)": re.compile(r"\bAQ\.[0-9A-Za-z_\-]{20,}"),
    "jeton GitHub": re.compile(r"\b(gh[pousr]_[0-9A-Za-z]{30,}|github_pat_[0-9A-Za-z_]{30,})"),
    "clé OpenAI/Anthropic (sk-...)": re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}"),
    "clé Groq (gsk_...)": re.compile(r"\bgsk_[A-Za-z0-9]{20,}"),
    "clé privée": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
}


def fichiers_du_depot() -> list:
    sortie = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=PROJECT_ROOT, capture_output=True, text=True, check=True,
    ).stdout
    return [PROJECT_ROOT / f for f in sortie.splitlines() if (PROJECT_ROOT / f).is_file()]


@pytest.fixture(scope="module")
def fichiers():
    try:
        return fichiers_du_depot()
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("pas de dépôt Git ici")


def lire(chemin) -> str:
    try:
        return chemin.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return ""  # fichier binaire


def test_env_jamais_versionne(fichiers):
    noms = {f.relative_to(PROJECT_ROOT).as_posix() for f in fichiers}
    assert ".env" not in noms
    assert ".env.example" in noms
    ignore = subprocess.run(["git", "check-ignore", "-q", ".env"], cwd=PROJECT_ROOT)
    assert ignore.returncode == 0, ".env doit être ignoré par .gitignore"


def test_env_example_sans_valeur_secrete():
    valeurs = dotenv_values(PROJECT_ROOT / ".env.example")
    autorisees = {"LLM_PROVIDER"}  # valeur publique (nom du fournisseur)
    remplies = [k for k, v in valeurs.items() if v and k not in autorisees]
    assert remplies == [], f"variables remplies dans .env.example : {remplies}"


def test_aucun_motif_de_secret(fichiers):
    trouves = [f"{f.relative_to(PROJECT_ROOT)} : {nom}"
               for f in fichiers for nom, motif in MOTIFS.items() if motif.search(lire(f))]
    assert trouves == [], "secrets possibles :\n" + "\n".join(trouves)


def test_les_vraies_cles_du_env_n_apparaissent_nulle_part(fichiers):
    env = PROJECT_ROOT / ".env"
    if not env.exists():
        pytest.skip("pas de .env sur cette machine")
    secrets = {k: v for k, v in dotenv_values(env).items() if v and len(v) >= 12}
    fuites = [f"{f.relative_to(PROJECT_ROOT)} contient la valeur de {k}"
              for f in fichiers for k, v in secrets.items() if v in lire(f)]
    assert fuites == [], "\n".join(fuites)
