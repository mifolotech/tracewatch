"""Score de fraîcheur selon la date de publication (étape 5, responsable C).

Décroissance par demi-vie : un document perd la moitié de sa fraîcheur
tous les `demi_vie_mois` mois.
    aujourd'hui : 1.0   | 12 mois : 0.5   | 24 mois : 0.25   | 36 mois : 0.125
Sans date : None (inconnu), affiché comme tel plutôt qu'inventé.

La fraîcheur ne dépend JAMAIS du contenu (scénario 2).
"""

from __future__ import annotations

from datetime import date


def score_fraicheur(date_iso: str | None, profil: dict, reference: date | None = None) -> float | None:
    if not date_iso:
        return None
    reference = reference or date.today()
    publiee = date.fromisoformat(date_iso[:10])
    age_mois = max(0.0, (reference - publiee).days / 30.44)
    demi_vie = profil["scoring"]["fraicheur"]["demi_vie_mois"]
    return round(0.5 ** (age_mois / demi_vie), 3)
