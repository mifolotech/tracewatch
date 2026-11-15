"""Score de pertinence par rapport à la question (étape 5, responsable C).

Principe explicable : on compte les mots-clés DISTINCTS du profil présents
dans le document (un mot répété 50 fois compte une fois, pour ne pas favoriser
les textes longs).
  - mot principal : 1.0   - mot secondaire : 0.5   - présent dans le titre : x bonus_titre
Le total brut est ramené entre 0 et 1 par une courbe qui sature :
    score = 1 - exp(-brut / saturation)
Un document dominé par des termes hors périmètre (code completion, chatbot...)
voit son score multiplié par penalite_exclusion.

La pertinence ne dépend JAMAIS de la date (scénario 2).
"""

from __future__ import annotations

import math

from tracewatch.collecte.commun import _motif


def _presents(texte: str, mots: list[str]) -> set[str]:
    return {m for m in mots if _motif(m).search(texte)}


def score_pertinence(titre: str, texte: str, profil: dict) -> float:
    mc = profil["mots_cles"]
    conf = profil["scoring"]["pertinence"]
    titre, texte = (titre or "").lower(), (texte or "").lower()

    brut = 0.0
    for mots, poids in ((mc["principaux"], conf["poids_mot_principal"]),
                        (mc["secondaires"], conf["poids_mot_secondaire"])):
        dans_titre = _presents(titre, mots)
        dans_texte = _presents(texte, mots) - dans_titre
        brut += poids * (conf["bonus_titre"] * len(dans_titre) + len(dans_texte))

    exclus = _presents(f"{titre} {texte}", mc["exclure"])
    principaux = _presents(f"{titre} {texte}", mc["principaux"])
    if exclus and len(exclus) >= len(principaux):
        brut *= conf["penalite_exclusion"]

    return round(1 - math.exp(-brut / conf["saturation"]), 3)
