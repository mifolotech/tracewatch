"""Score de fiabilité selon le type de source (étape 5, responsable C).

Base : la confiance par famille du profil (independant 0.9 ... fournisseur 0.4).
Ajustements, chacun avec son motif lisible dans le profil :
  - résultat de classement VÉRIFIÉ par l'équipe du benchmark : bonus
  - résultat de classement AUTO-DÉCLARÉ par celui qui le soumet : malus
Le score reste entre 0 et 1.
"""

from __future__ import annotations

import re

VERIFIE = re.compile(r"verified by the [\w\- ]+ team: yes", re.I)
AUTO_DECLARE = re.compile(r"self-reported", re.I)


def score_fiabilite(famille: str, texte: str, profil: dict) -> float:
    conf = profil["scoring"]
    score = conf["fiabilite_par_famille"].get(famille, 0.5)
    ajust = conf.get("ajustements_fiabilite", {})
    if famille == "benchmark":
        if VERIFIE.search(texte or ""):
            score += ajust.get("benchmark_verifie", 0)
        elif AUTO_DECLARE.search(texte or ""):
            score += ajust.get("benchmark_auto_declare", 0)
    return round(min(1.0, max(0.0, score)), 3)
