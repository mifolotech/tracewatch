"""Vérification que la citation existe dans le document (étape 6, responsable A).

C'est le garde-fou anti-hallucination : le LLM PROPOSE une citation, le CODE
vérifie qu'elle figure mot pour mot dans le document. Sinon l'affirmation est
rejetée (gardée en base pour audit, mais jamais utilisée dans le rapport).

Tolérances (purement typographiques, jamais sur les mots) :
  - majuscules/minuscules, espaces multiples, retours à la ligne
  - guillemets et apostrophes typographiques (’ “ ”) vs droits (' ")
  - tirets (– —) vs trait d'union (-)
  - ponctuation ou guillemets en début/fin de citation
  - marques Markdown * et ` (gras, code) présentes dans les issues GitHub
Exemples réels de VRAIS rejets : « the blog post do report » (le document dit
« does report ») ; une phrase entière absente du document.
"""

from __future__ import annotations

import re
import unicodedata

EQUIVALENTS = str.maketrans({
    "‘": "'", "’": "'", "‚": "'", "′": "'",
    "“": '"', "”": '"', "„": '"', "«": '"', "»": '"',
    "–": "-", "—": "-", "−": "-", " ": " ",
})


def normaliser(texte: str) -> str:
    texte = unicodedata.normalize("NFKC", texte or "").translate(EQUIVALENTS)
    # Marques de mise en forme Markdown (**gras**, `code`) : l'IA les enlève en recopiant
    texte = texte.replace("*", "").replace("`", "")
    texte = re.sub(r"\s+", " ", texte)
    # "online , exploiting" (reste du nettoyage HTML) == "online, exploiting"
    texte = re.sub(r" ([,.;:!?)\]])", r"\1", texte)
    return texte.strip().lower()


def verifier_citation(citation: str, document: str, longueur_min: int = 20) -> bool:
    """True seulement si la citation (assez longue) est un passage continu du document."""
    c = normaliser(citation).strip(" \"'.,;:")
    if len(c) < longueur_min:
        return False
    return c in normaliser(document)


def reverifier(conn, longueur_min: int = 20) -> int:
    """Revérifie toutes les citations avec les règles actuelles. Renvoie le nombre de changements.

    Garantit que le statut `citation_verifiee` en base suit toujours le code de vérification.
    Une affirmation sans catégorie valide reste non vérifiée (inexploitable).
    """
    lignes = conn.execute(
        """SELECT c.id, c.citation, c.citation_verifiee, c.categorie, d.title, d.text
           FROM claims c JOIN documents d ON d.id = c.document_id"""
    ).fetchall()
    changements = 0
    for l in lignes:
        ok = int(l["categorie"] is not None and
                 verifier_citation(l["citation"], f"{l['title']}\n{l['text'] or ''}", longueur_min))
        if ok != l["citation_verifiee"]:
            conn.execute("UPDATE claims SET citation_verifiee=? WHERE id=?", (ok, l["id"]))
            changements += 1
    conn.commit()
    return changements
