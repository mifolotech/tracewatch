"""Collecte des flux RSS : blogs fournisseurs et sources indépendantes (étape 3, responsable B).

Chaque flux a sa propre famille (fournisseur ou independant) dans le profil.
Les blogs parlent de tout : on ne garde que les articles qui contiennent
au moins un mot-clé du profil (principaux, secondaires ou filtre_rss).
"""

from __future__ import annotations

import sqlite3

import feedparser

from tracewatch.collecte.commun import (
    Bilan,
    Document,
    Http,
    contient_mot_cle,
    nettoyer_html,
    vers_iso,
)


def _mots_filtre(profil: dict) -> list[str]:
    mc = profil["mots_cles"]
    return mc["principaux"] + mc["secondaires"] + profil["sources"]["rss"].get("filtre_rss", [])


def collecter(conn: sqlite3.Connection, profil: dict, http: Http) -> Bilan:
    conf = profil["sources"]["rss"]
    bilan = Bilan("rss")
    mots = _mots_filtre(profil)
    for flux in conf["flux"]:
        try:
            contenu = http.get(flux["url"]).content
        except Exception as e:
            bilan.erreurs.append(f"{flux['nom']}: {e}")
            continue
        for entree in feedparser.parse(contenu).entries:
            titre = nettoyer_html(entree.get("title"))
            corps = entree.get("content", [{}])[0].get("value") or entree.get("summary")
            texte = nettoyer_html(corps)
            if not titre or not entree.get("link"):
                continue
            if not contient_mot_cle(f"{titre} {texte}", mots):
                bilan.trouves += 1
                bilan.hors_sujet += 1
                continue
            date = entree.get("published_parsed") or entree.get("updated_parsed")
            bilan.ajouter(
                conn,
                Document(
                    url=entree["link"],
                    title=titre,
                    text=texte,
                    authors=[entree["author"]] if entree.get("author") else [],
                    organization=flux["nom"],
                    published_date=vers_iso(date),
                    source_family=flux["source_family"],
                    source_name=flux["nom"],
                ),
                profil,
            )
    return bilan
