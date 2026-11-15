"""Client LLM interchangeable avec cache (étape 6, responsable A).

- Un fournisseur LLM = une petite classe avec un attribut `nom` et une méthode
  `generer(prompt) -> str`. Gemini est branché ; en ajouter un autre (Groq,
  Anthropic, modèle local) = écrire une classe de ~15 lignes et l'ajouter à FOURNISSEURS.
- ClientLLM ajoute le CACHE : chaque réponse est enregistrée dans un fichier JSON
  dont le nom est l'empreinte (modèle + prompt). Même question = même réponse,
  sans rappeler le LLM. La démo est donc reproductible, même sans clé.
- Sans clé : seul le cache est utilisé ; une question absente du cache lève LLMIndisponible.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from tracewatch.collecte.commun import env
from tracewatch.db import PROJECT_ROOT

CACHE_DEFAUT = PROJECT_ROOT / "data" / "cache_llm"


class LLMIndisponible(RuntimeError):
    """Pas de clé et réponse absente du cache."""


class QuotaDepasse(RuntimeError):
    """Le fournisseur refuse : quota gratuit épuisé. Relancer plus tard (le cache garde tout)."""


class Fournisseur(Protocol):
    nom: str

    def generer(self, prompt: str) -> str: ...


class Gemini:
    def __init__(self, modele: str, temperature: float = 0.0, cle: str | None = None):
        from google import genai  # import ici : inutile en mode cache seul

        cle = cle or env("GEMINI_API_KEY")
        if not cle:
            raise LLMIndisponible("GEMINI_API_KEY absente du fichier .env")
        self._client = genai.Client(api_key=cle)
        self._types = genai.types
        self.modele = modele
        self.temperature = temperature
        self.nom = f"gemini/{modele}"

    def generer(self, prompt: str) -> str:
        config = self._types.GenerateContentConfig(
            temperature=self.temperature, response_mime_type="application/json"
        )
        essais = 6
        for essai in range(essais):
            try:
                return self._client.models.generate_content(
                    model=self.modele, contents=prompt, config=config
                ).text
            except Exception as e:
                message = str(e)
                if "RESOURCE_EXHAUSTED" in message or "429" in message:
                    i = message.find("Quota exceeded for metric")
                    detail = message[i:i + 250] if i >= 0 else message[:250]
                    if "PerDay" in message or "per day" in message.lower() or essai == essais - 1:
                        raise QuotaDepasse(detail) from e
                    time.sleep(60)  # limite PAR MINUTE : on attend que la fenêtre se libère
                elif any(code in message for code in ("500", "502", "503", "504", "UNAVAILABLE")):
                    time.sleep(10 * (essai + 1))
                else:
                    raise
        raise RuntimeError(f"Gemini ne répond pas après {essais} essais")


FOURNISSEURS = {"gemini": Gemini}


def extraire_json(texte: str):
    """Tolère les réponses entourées de ```json ... ```."""
    texte = texte.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", texte, re.S)
    return json.loads(m.group(1) if m else texte)


class ClientLLM:
    """Point d'entrée unique de l'analyse : cache d'abord, LLM ensuite."""

    def __init__(self, fournisseur: Fournisseur | None, nom_modele: str, dossier_cache: Path | str | None = None):
        self.fournisseur = fournisseur
        self.nom = fournisseur.nom if fournisseur else nom_modele
        self.cache = Path(dossier_cache or env("TRACEWATCH_CACHE") or CACHE_DEFAUT)
        self.cache.mkdir(parents=True, exist_ok=True)
        self.appels = 0
        self.depuis_cache = 0

    def _chemin(self, prompt: str) -> Path:
        cle = hashlib.sha256(f"{self.nom}\n{prompt}".encode("utf-8")).hexdigest()
        return self.cache / f"{cle}.json"

    def generer_json(self, prompt: str):
        chemin = self._chemin(prompt)
        if chemin.exists():
            self.depuis_cache += 1
            return json.loads(chemin.read_text(encoding="utf-8"))["reponse"]
        if self.fournisseur is None:
            raise LLMIndisponible("Réponse absente du cache et aucun LLM configuré (clé manquante ?)")
        brut = self.fournisseur.generer(prompt)
        self.appels += 1
        reponse = extraire_json(brut)
        chemin.write_text(
            json.dumps(
                {"modele": self.nom, "date": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                 "prompt": prompt, "reponse": reponse},
                ensure_ascii=False, indent=1,
            ),
            encoding="utf-8",
        )
        return reponse


def creer_client(profil: dict, dossier_cache: Path | str | None = None) -> ClientLLM:
    """Utilise le fournisseur du .env (LLM_PROVIDER) s'il a une clé, sinon le cache seul."""
    conf = profil["analyse"]
    nom_fournisseur = env("LLM_PROVIDER") or conf.get("fournisseur", "gemini")
    nom_modele = f"{nom_fournisseur}/{conf['modele']}"
    try:
        fournisseur = FOURNISSEURS[nom_fournisseur](conf["modele"], conf.get("temperature", 0.0))
    except LLMIndisponible:
        fournisseur = None  # mode démo : cache seul
    except KeyError as e:
        raise ValueError(f"Fournisseur LLM inconnu : {nom_fournisseur} (connus : {list(FOURNISSEURS)})") from e
    return ClientLLM(fournisseur, nom_modele, dossier_cache)
