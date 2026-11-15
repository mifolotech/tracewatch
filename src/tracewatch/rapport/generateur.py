"""Génération du rapport de veille (étape 8, responsable D).

Le rapport est construit UNIQUEMENT à partir des preuves vérifiées, sans
réécriture par un LLM : chaque phrase reprend une affirmation vérifiée (ou la
résume par des chiffres calculés) et porte ses références [Pn].
Avant d'être écrit, il passe le contrôle verifier_tracabilite() ; un rapport
non conforme n'est JAMAIS enregistré.

Sections : question, décision recommandée (proportionnée au niveau de preuve),
synthèse par thème, faits, contradictions, incertitudes, risques, points à
surveiller, annexe des preuves.

RÈGLE DE DÉCISION (niveaux : insuffisant 0 < faible 1 < moyen 2 < fort 3,
comptés en sources indépendantes, voir niveau_preuve.py) :
  1. EXCLURE      si critiques "fiabilité/sécurité" >= fort, critiques "usage réel" >= moyen,
                  aucune preuve optimiste en usage réel ET aucun résultat prometteur
                  (optimistes benchmarks et usage réel < moyen). Aligné sur CADRAGE.md :
                  exclure = échecs graves ET rien qui justifie même un essai encadré.
                  (Révision du 2026-11-15 : la première version testait EXCLURE sans regarder
                  les résultats prometteurs ; elle donnait « exclure » malgré 11 sources
                  optimistes indépendantes sur les benchmarks. Trace : historique de C1.)
  2. GÉNÉRALISER  si optimistes "usage réel" >= fort, optimistes "benchmarks" >= moyen,
                  et critiques "usage réel" et "fiabilité/sécurité" <= faible
  3. PILOTE       si résultats prometteurs (optimistes benchmarks ou usage réel >= moyen)
                  ET écart documenté (critiques validité, usage réel ou fiabilité >= moyen)
  4. DIFFÉRER     sinon (preuves insuffisantes ou trop contradictoires)
La confiance = le plus faible des niveaux qui ont déclenché la règle.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from tracewatch.analyse.contradictions import Divergence, detecter
from tracewatch.analyse.niveau_preuve import NiveauPreuve, evaluer_niveau
from tracewatch.db import PROJECT_ROOT
from tracewatch.rapport.revision import Proposition, reviser
from tracewatch.rapport.tracabilite import (
    FIN_DE_PHRASE,
    annexe_preuves,
    reference,
    references,
    verifier_tracabilite,
)

DOSSIER_RAPPORTS = PROJECT_ROOT / "rapports"
RANG = {"insuffisant": 0, "faible": 1, "moyen": 2, "fort": 3}
CONFIANCE = {0: "très faible", 1: "faible", 2: "moyenne", 3: "forte"}

LIBELLES_THEMES = {
    "performance_benchmark": "Scores sur les benchmarks",
    "validite_benchmark": "Validité des benchmarks",
    "usage_reel": "Résultats en usage réel",
    "fiabilite_securite": "Fiabilité et sécurité",
    "maturite_approches": "Maturité des techniques d'agents",
    "supervision_humaine": "Supervision humaine",
}
LIBELLES_OPTIONS = {
    "generaliser": "Généraliser",
    "pilote_controle": "Pilote contrôlé",
    "differer": "Différer",
    "exclure": "Exclure",
}
MAX_PAR_SECTION = 10
MAX_REFS = 4


class RapportNonConforme(RuntimeError):
    """Le rapport contient une phrase non sourcée ou une preuve interdite."""


# ---------------------------------------------------------------------
# Calcul de la synthèse
# ---------------------------------------------------------------------
@dataclass
class Theme:
    cle: str
    libelle: str
    optimistes: list[int] = field(default_factory=list)
    critiques: list[int] = field(default_factory=list)
    neutres: list[int] = field(default_factory=list)
    preuve_opt: NiveauPreuve | None = None
    preuve_crit: NiveauPreuve | None = None

    def o(self) -> int:
        return RANG[self.preuve_opt.niveau]

    def c(self) -> int:
        return RANG[self.preuve_crit.niveau]


@dataclass
class Decision:
    option: str
    confiance: str
    justification: list[tuple[str, list[int]]]  # (phrase, preuves)
    limites: list[str] = field(default_factory=list)  # pourquoi la confiance a été plafonnée


@dataclass
class Synthese:
    preuves: dict[int, sqlite3.Row]
    themes: dict[str, Theme]
    divergences: list[Divergence]
    decision: Decision
    stats: dict


def _preuves(conn: sqlite3.Connection) -> dict[int, sqlite3.Row]:
    """Preuves vérifiées, triées par fiabilité puis pertinence de leur document."""
    lignes = conn.execute(
        """SELECT c.*, d.source_family, d.source_name, d.title AS doc_titre,
                  COALESCE(s.fiabilite, 0) AS fiabilite, COALESCE(s.pertinence, 0) AS pertinence
           FROM claims c JOIN documents d ON d.id = c.document_id
           LEFT JOIN scores s ON s.document_id = d.id
           WHERE c.citation_verifiee = 1
           ORDER BY fiabilite DESC, pertinence DESC, c.id"""
    ).fetchall()
    return {l["id"]: l for l in lignes}


def recommander(themes: dict[str, Theme]) -> Decision:
    """Applique la règle, puis plafonne la confiance si l'usage réel n'est pas documenté :
    la question porte sur la fiabilité RÉELLE, des benchmarks seuls ne suffisent pas
    à une confiance forte."""
    d = _regle(themes)
    usage = themes["usage_reel"]
    if usage.o() + usage.c() == 0 and d.confiance in ("forte",):
        d.confiance = "moyenne"
        d.limites.append("Confiance plafonnée à « moyenne » : aucune source indépendante ne documente encore "
                         "les résultats en usage réel, qui sont le cœur de la question.")
    return d


def _regle(themes: dict[str, Theme]) -> Decision:
    def t(cle):
        return themes[cle]

    perf, valid, usage, fiab = (t("performance_benchmark"), t("validite_benchmark"),
                                t("usage_reel"), t("fiabilite_securite"))

    prometteur = max(perf.o(), usage.o())
    if fiab.c() >= 3 and usage.c() >= 2 and usage.o() == 0 and prometteur < 2:
        return Decision("exclure", CONFIANCE[min(fiab.c(), usage.c())], [
            ("Des échecs graves sont documentés par plusieurs sources indépendantes", fiab.critiques),
            ("Les retours en usage réel sont négatifs", usage.critiques),
        ])
    if usage.o() >= 3 and perf.o() >= 2 and usage.c() <= 1 and fiab.c() <= 1:
        return Decision("generaliser", CONFIANCE[min(usage.o(), perf.o())], [
            ("Les résultats en usage réel sont confirmés par des sources indépendantes", usage.optimistes),
            ("Les scores sur les benchmarks vont dans le même sens", perf.optimistes),
        ])
    ecart = max(valid.c(), usage.c(), fiab.c())
    if prometteur >= 2 and ecart >= 2:
        cote_prometteur = perf if perf.o() >= usage.o() else usage
        justification = [
            (f"Les résultats sont prometteurs ({cote_prometteur.libelle.lower()})", cote_prometteur.optimistes)]
        # Chaque écart documenté (niveau >= moyen) justifie que le pilote soit CONTRÔLÉ
        for th in sorted((valid, usage, fiab), key=lambda x: -x.c()):
            if th.c() >= 2:
                justification.append((f"Mais un écart est documenté : {th.libelle.lower()} "
                                      f"({th.preuve_crit.sources_independantes} sources indépendantes critiques)",
                                      th.critiques))
        return Decision("pilote_controle", CONFIANCE[min(prometteur, ecart)], justification)
    justification = []
    if perf.optimistes or usage.optimistes:
        justification.append(("Quelques résultats positifs existent", perf.optimistes + usage.optimistes))
    if valid.critiques or usage.critiques or fiab.critiques:
        justification.append(("Des limites sont signalées", valid.critiques + usage.critiques + fiab.critiques))
    return Decision("differer", CONFIANCE[min(max(prometteur, ecart), 1)], justification)


def calculer_synthese(conn: sqlite3.Connection, profil: dict) -> Synthese:
    preuves = _preuves(conn)
    themes = {k: Theme(k, LIBELLES_THEMES.get(k, k)) for k in profil["analyse"]["themes"]}
    for p in preuves.values():
        if p["theme"] in themes:
            {"optimiste": themes[p["theme"]].optimistes, "critique": themes[p["theme"]].critiques}.get(
                p["position"], themes[p["theme"]].neutres).append(p["id"])
    for th in themes.values():
        th.preuve_opt = evaluer_niveau(conn, th.optimistes, profil)
        th.preuve_crit = evaluer_niveau(conn, th.critiques, profil)

    stats = dict(zip(
        ("documents", "travaux", "familles"),
        conn.execute("SELECT COUNT(*), COUNT(DISTINCT cluster_id), COUNT(DISTINCT source_family) FROM documents").fetchone(),
    ))
    stats["docs_analyses"] = conn.execute("SELECT COUNT(DISTINCT document_id) FROM claims").fetchone()[0]
    stats["affirmations"], stats["verifiees"] = conn.execute(
        "SELECT COUNT(*), COALESCE(SUM(citation_verifiee), 0) FROM claims").fetchone()
    stats["modeles"] = ", ".join(r[0] for r in conn.execute(
        "SELECT DISTINCT modele FROM claims WHERE modele IS NOT NULL"))
    return Synthese(preuves, themes, detecter(conn, profil), recommander(themes), stats)


# ---------------------------------------------------------------------
# Rédaction
# ---------------------------------------------------------------------
def avec_refs(texte: str, ids: list[int]) -> str:
    """Ajoute les références à CHAQUE phrase du texte (contrôle phrase par phrase)."""
    refs = "".join(reference(i) for i in list(dict.fromkeys(ids))[:MAX_REFS])
    phrases = [p.strip() for p in FIN_DE_PHRASE.split(texte.strip()) if p.strip()]
    sorties = []
    for p in phrases:
        fin = p[-1] if p[-1] in ".!?" else "."
        corps = p[:-1] if p[-1] in ".!?" else p
        sorties.append(f"{corps.rstrip()} {refs}{fin}")
    return " ".join(sorties)


def puce(synthese: Synthese, claim_id: int, prefixe: str = "") -> str:
    p = synthese.preuves[claim_id]
    libelle = LIBELLES_THEMES.get(p["theme"], "")
    tete = f"**{libelle}** · " if libelle and not prefixe else prefixe
    return f"- {tete}{avec_refs(p['texte'], [claim_id])}"


def _choisir(synthese: Synthese, categories: tuple[str, ...]) -> list[int]:
    return [i for i, p in synthese.preuves.items() if p["categorie"] in categories][:MAX_PAR_SECTION]


def phrase_theme(th: Theme) -> tuple[str, list[int]]:
    o, c = th.preuve_opt, th.preuve_crit
    if not (th.optimistes or th.critiques):
        return "", []
    if c.sources_independantes > o.sources_independantes:
        tendance = "les sources critiques dominent"
    elif o.sources_independantes > c.sources_independantes:
        tendance = "les sources optimistes dominent"
    else:
        tendance = "les sources sont partagées"
    texte = (f"{th.libelle} : {tendance}, avec {c.sources_independantes} source(s) indépendante(s) "
             f"critique(s) (niveau {c.niveau}) contre {o.sources_independantes} optimiste(s) "
             f"(niveau {o.niveau}) et {o.sources_fournisseurs + c.sources_fournisseurs} source(s) fournisseur(s)")
    return texte, th.critiques[:2] + th.optimistes[:2]


def rediger(conn: sqlite3.Connection, synthese: Synthese, profil: dict) -> str:
    s, d = synthese.stats, synthese.decision
    lignes = [
        "# Rapport de veille TraceWatch",
        "",
        f"_Généré le {date.today().isoformat()} à partir de {s['documents']} documents ({s['travaux']} travaux "
        f"distincts, {s['familles']} familles de sources). {s['docs_analyses']} documents ont fourni des affirmations à l'analyse IA "
        f"({s['modeles'] or 'aucun modèle'}) : {s['verifiees']} affirmations à citation vérifiée sur "
        f"{s['affirmations']} proposées._",
        "",
        "> **Question de décision.** " + " ".join(profil["question"].split()),
        "",
        "## 1. Décision recommandée",
        "",
    ]
    ids_decision = [i for _, ids in d.justification for i in ids[:2]]
    if ids_decision:
        lignes.append(avec_refs(
            f"Décision recommandée : **{LIBELLES_OPTIONS[d.option]}**, avec une confiance {d.confiance}",
            ids_decision))
        lignes.append("")
        lignes += [f"- {avec_refs(phrase, ids[:3])}" for phrase, ids in d.justification if ids]
    else:
        lignes.append(f"_Décision recommandée : {LIBELLES_OPTIONS[d.option]} (aucune preuve vérifiée "
                      "suffisante pour aller plus loin)._")
    lignes += [f"_{limite}_" for limite in d.limites]
    hyp = profil.get("hypothese_depart")
    if hyp:
        verdict = "confirmée" if hyp == d.option else "remise en cause"
        lignes += ["", f"_Hypothèse de départ ({LIBELLES_OPTIONS.get(hyp, hyp)}) : {verdict} par les preuves "
                       "actuelles. La décision suit une règle fixe, documentée dans generateur.py, et sa "
                       "confiance est celle du niveau de preuve le plus faible qui l'a déclenchée._"]

    lignes += ["", "## 2. Synthèse par thème", "",
               "| Thème | Optimistes (sources indép.) | Critiques (sources indép.) | Fournisseurs |",
               "|---|---|---|---|"]
    for th in synthese.themes.values():
        lignes.append(f"| {th.libelle} | {th.preuve_opt.sources_independantes} ({th.preuve_opt.niveau}) | "
                      f"{th.preuve_crit.sources_independantes} ({th.preuve_crit.niveau}) | "
                      f"{th.preuve_opt.sources_fournisseurs + th.preuve_crit.sources_fournisseurs} |")
    lignes.append("")
    for th in synthese.themes.values():
        texte, ids = phrase_theme(th)
        if ids:
            lignes.append(f"- {avec_refs(texte, ids)}")

    def section(titre: str, ids: list[int], vide: str) -> None:
        lignes.extend(["", titre, ""])
        lignes.extend(puce(synthese, i) for i in ids)
        if not ids:
            lignes.append(f"_{vide}_")

    section("## 3. Faits établis", _choisir(synthese, ("fait",)), "Aucun fait vérifié pour l'instant.")

    lignes += ["", "## 4. Contradictions", ""]
    if not synthese.divergences:
        lignes.append("_Aucune contradiction détectée sur les preuves actuelles._")
    for dv in synthese.divergences:
        # Scénario 3 : montrer D'ABORD l'affirmation du fournisseur et les sources indépendantes qui la contestent
        opt = [c["id"] for c in sorted(dv.optimistes, key=lambda c: c["source_family"] != "fournisseur")]
        crit = [c["id"] for c in sorted(dv.critiques,
                                        key=lambda c: c["source_family"] not in ("independant", "publication"))]
        lignes.append("- " + avec_refs(
            f"{LIBELLES_THEMES.get(dv.theme, dv.theme)} ({dv.type}) : {len(opt)} affirmation(s) optimiste(s) "
            f"(niveau {dv.preuve_optimistes.niveau}) s'opposent à {len(crit)} critique(s) "
            f"(niveau {dv.preuve_critiques.niveau})", opt[:2] + crit[:2]))

        def camp(i: int, nom: str) -> str:
            p = synthese.preuves[i]
            return "  " + puce(synthese, i, f"{nom} ({p['source_family']}, {p['source_name']}) : ")

        lignes += [camp(i, "Optimiste") for i in opt[:2]]
        lignes += [camp(i, "Critique") for i in crit[:2]]

    section("## 5. Incertitudes et lacunes", _choisir(synthese, ("lacune",)), "Aucune lacune signalée.")
    sans_preuve = [th.libelle for th in synthese.themes.values()
                   if th.preuve_opt.sources_independantes + th.preuve_crit.sources_independantes == 0]
    if sans_preuve:
        lignes.append(f"_Thèmes sans aucune source indépendante à ce jour : {', '.join(sans_preuve)}._")
    lignes.append(f"_Couverture : {s['docs_analyses']} documents ont fourni des affirmations. Les conclusions évolueront "
                  "avec l'analyse des documents restants (voir l'historique des révisions)._")

    section("## 6. Risques", _choisir(synthese, ("risque",)), "Aucun risque documenté pour l'instant.")
    section("## 7. Points à surveiller", _choisir(synthese, ("signal", "interpretation")),
            "Aucun signal pour l'instant.")

    corps = "\n".join(lignes)
    return corps + "\n\n" + annexe_preuves(conn, references(corps))


def propositions(synthese: Synthese) -> list[Proposition]:
    """Conclusions à versionner : la décision et une conclusion par thème."""
    d = synthese.decision
    ids = [i for _, l in d.justification for i in l[:2]]
    props = [Proposition("decision", f"Décision recommandée : {LIBELLES_OPTIONS[d.option]} "
                                     f"(confiance {d.confiance})", ids)]
    for th in synthese.themes.values():
        texte, ids_t = phrase_theme(th)
        props.append(Proposition(f"theme:{th.cle}", texte, th.optimistes + th.critiques if ids_t else []))
    return props


@dataclass
class ResultatRapport:
    markdown: str
    chemin: Path | None
    synthese: Synthese
    changements: list[str]


def generer_rapport(conn: sqlite3.Connection, profil: dict, motif: str = "génération du rapport",
                    ecrire: bool = True, dossier: Path | None = None) -> ResultatRapport:
    """Calcule, révise les conclusions, rédige, CONTRÔLE la traçabilité, puis écrit."""
    synthese = calculer_synthese(conn, profil)
    changements = reviser(conn, propositions(synthese), profil, motif)
    markdown = rediger(conn, synthese, profil)

    problemes = verifier_tracabilite(markdown, conn)
    if problemes:
        raise RapportNonConforme("Rapport refusé :\n  " + "\n  ".join(problemes[:10]))

    chemin = None
    if ecrire:
        dossier = Path(dossier or DOSSIER_RAPPORTS)
        dossier.mkdir(parents=True, exist_ok=True)
        chemin = dossier / f"rapport_{date.today().isoformat()}.md"
        chemin.write_text(markdown, encoding="utf-8")
        (dossier / "dernier_rapport.md").write_text(markdown, encoding="utf-8")
    return ResultatRapport(markdown, chemin, synthese, changements)
