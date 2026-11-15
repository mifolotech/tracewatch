"""Tableau de bord Streamlit (étape 8, responsable D).

Lancer :  streamlit run src/tracewatch/app/streamlit_app.py

Onglets : Vue d'ensemble | Corpus (filtres + qualité) | Preuves (traçabilité)
          | Contradictions | Rapport | Révisions (historique + ajout de document)
"""

from __future__ import annotations


import altair as alt
import pandas as pd
import streamlit as st

from tracewatch.analyse.contradictions import detecter
from tracewatch.collecte.commun import Document, charger_profil, enregistrer, vers_iso
from tracewatch.db import SOURCE_FAMILIES, get_connection, init_db
from tracewatch.rapport.generateur import (
    LIBELLES_OPTIONS,
    LIBELLES_THEMES,
    RapportNonConforme,
    calculer_synthese,
    generer_rapport,
)
from tracewatch.rapport.revision import historique
from tracewatch.rapport.tracabilite import fiche_preuve, tracer_preuve
from tracewatch.scoring.qualite_corpus import Filtre, calculer_scores, evaluer, filtrer

st.set_page_config(page_title="TraceWatch", page_icon="🔎", layout="wide")

# ---------------------------------------------------------------------
# Couleurs (palette de référence validée : bleu = série unique / optimiste,
# rouge = critique ; paire divergente bleu <-> rouge). Pas pour le texte.
# ---------------------------------------------------------------------
SOMBRE = getattr(getattr(st.context, "theme", None), "type", "light") == "dark"
BLEU = "#3987e5" if SOMBRE else "#2a78d6"
ROUGE = "#e66767" if SOMBRE else "#e34948"
GRILLE = "#383835" if SOMBRE else "#e4e3df"


def style(chart: alt.Chart) -> alt.Chart:
    return chart.configure_axis(gridColor=GRILLE, domain=False, tickColor=GRILLE, labelFontSize=12,
                                titleFontSize=12).configure_view(strokeWidth=0)


PROFIL = charger_profil()
CHEMIN = init_db()


def conn():
    return get_connection(CHEMIN)


# ---------------------------------------------------------------------
# En-tête
# ---------------------------------------------------------------------
st.title("🔎 TraceWatch")
st.caption(" ".join(PROFIL["question"].split()))

onglets = st.tabs(["Vue d'ensemble", "Corpus", "Preuves", "Contradictions", "Rapport", "Révisions"])

# ---------------------------------------------------------------------
# 1. Vue d'ensemble
# ---------------------------------------------------------------------
with onglets[0]:
    with conn() as c:
        synthese = calculer_synthese(c, PROFIL)
        tous = filtrer(c)
        qualite = evaluer(tous, PROFIL)
    s, d = synthese.stats, synthese.decision

    st.subheader(f"Décision recommandée : {LIBELLES_OPTIONS[d.option]}")
    st.write(f"Confiance **{d.confiance}**. Hypothèse de départ : "
             f"{LIBELLES_OPTIONS.get(PROFIL.get('hypothese_depart'), '—')}.")
    for limite in d.limites:
        st.info(limite, icon="ℹ️")

    k = st.columns(5)
    k[0].metric("Documents", s["documents"])
    k[1].metric("Travaux distincts", s["travaux"], help="Un travail republié plusieurs fois compte une seule fois.")
    k[2].metric("Familles de sources", s["familles"])
    k[3].metric("Preuves vérifiées", f"{s['verifiees']} / {s['affirmations']}",
                help="Affirmations dont la citation a été retrouvée mot pour mot dans le document.")
    k[4].metric("Qualité du corpus", qualite.niveau.upper())
    for a in qualite.alertes:
        st.warning(a, icon="⚠️")

    g1, g2 = st.columns(2)
    familles = pd.DataFrame([{"famille": f, "documents": n} for f, n in qualite.par_famille.items()])
    with g1:
        st.markdown("**Sources par famille**")
        base = alt.Chart(familles).encode(
            y=alt.Y("famille:N", sort="-x", title=None),
            x=alt.X("documents:Q", title="Documents"),
            tooltip=["famille", "documents"],
        )
        st.altair_chart(style(base.mark_bar(color=BLEU, cornerRadiusEnd=4, size=18)
                              + base.mark_text(align="left", dx=4).encode(text="documents:Q")),
                        width="stretch")
    with g2:
        st.markdown("**Fraîcheur : documents par année de publication**")
        annees = pd.DataFrame([{"année": (d_["published_date"] or "inconnue")[:4]} for d_ in tous])
        annees = annees.value_counts().reset_index(name="documents")
        st.altair_chart(style(alt.Chart(annees).mark_bar(color=BLEU, cornerRadiusEnd=4).encode(
            x=alt.X("année:O", title=None), y=alt.Y("documents:Q", title="Documents"),
            tooltip=["année", "documents"])), width="stretch")

    st.markdown("**Niveau de preuve par thème** (sources indépendantes ; un travail republié = 1 source)")
    lignes = []
    for th in synthese.themes.values():
        lignes += [
            {"thème": th.libelle, "camp": "Optimiste", "sources": th.preuve_opt.sources_independantes,
             "niveau": th.preuve_opt.niveau, "fournisseurs": th.preuve_opt.sources_fournisseurs},
            {"thème": th.libelle, "camp": "Critique", "sources": th.preuve_crit.sources_independantes,
             "niveau": th.preuve_crit.niveau, "fournisseurs": th.preuve_crit.sources_fournisseurs},
        ]
    df_themes = pd.DataFrame(lignes)
    st.altair_chart(style(alt.Chart(df_themes).mark_bar(cornerRadiusEnd=4, size=12).encode(
        y=alt.Y("thème:N", title=None),
        yOffset=alt.YOffset("camp:N", sort=["Optimiste", "Critique"]),
        x=alt.X("sources:Q", title="Sources indépendantes"),
        color=alt.Color("camp:N", scale=alt.Scale(domain=["Optimiste", "Critique"], range=[BLEU, ROUGE]),
                        legend=alt.Legend(title=None, orient="top")),
        tooltip=["thème", "camp", "sources", "niveau", "fournisseurs"],
    ).properties(height=320)), width="stretch")
    with st.expander("Voir le tableau"):
        st.dataframe(df_themes, hide_index=True, width="stretch")

# ---------------------------------------------------------------------
# 2. Corpus : filtres de resserrement + indicateur de qualité
# ---------------------------------------------------------------------
with onglets[1]:
    st.markdown("Resserrer le corpus : les trois scores restent **séparés** et se filtrent indépendamment.")
    f1, f2, f3, f4 = st.columns(4)
    p_min = f1.slider("Pertinence min.", 0.0, 1.0, 0.0, 0.05)
    fr_min = f2.slider("Fraîcheur min.", 0.0, 1.0, 0.0, 0.05)
    fi_min = f3.slider("Fiabilité min.", 0.0, 1.0, 0.0, 0.05)
    un_par_travail = f4.toggle("Un document par travail", value=False)
    f5, f6 = st.columns([2, 1])
    familles_choisies = f5.multiselect("Familles", SOURCE_FAMILIES, default=list(SOURCE_FAMILIES))
    contient = f6.text_input("Contient le mot")
    filtre = Filtre(pertinence_min=p_min or None, fraicheur_min=fr_min or None, fiabilite_min=fi_min or None,
                    familles=familles_choisies, contient=contient or None, un_par_travail=un_par_travail)
    with conn() as c:
        docs = filtrer(c, filtre)
    q = evaluer(docs, PROFIL)
    m = st.columns(5)
    m[0].metric("Documents", q.documents)
    m[1].metric("Travaux distincts", q.travaux_distincts)
    m[2].metric("Bruit", f"{q.part_bruit:.0%}", help=f"Pertinence < {PROFIL['qualite_corpus']['seuil_pertinence_min']}")
    m[3].metric("Indépendants / scientifiques", f"{q.part_independante:.0%}")
    m[4].metric("Qualité", q.niveau.upper())
    for a in q.alertes:
        st.warning(a, icon="⚠️")
    st.dataframe(
        pd.DataFrame([{
            "titre": d_["title"], "famille": d_["source_family"], "source": d_["source_name"],
            "date": d_["published_date"], "pertinence": d_["pertinence"], "fraîcheur": d_["fraicheur"],
            "fiabilité": d_["fiabilite"], "lien": d_["url"],
        } for d_ in docs]),
        hide_index=True, width="stretch", height=480,
        column_config={"lien": st.column_config.LinkColumn("lien", display_text="ouvrir"),
                       "pertinence": st.column_config.ProgressColumn(min_value=0, max_value=1, format="%.2f"),
                       "fraîcheur": st.column_config.NumberColumn(format="%.2f"),
                       "fiabilité": st.column_config.NumberColumn(format="%.2f")},
    )

# ---------------------------------------------------------------------
# 3. Preuves : de l'affirmation au document original
# ---------------------------------------------------------------------
with onglets[2]:
    with conn() as c:
        claims = c.execute(
            """SELECT c.id, c.texte, c.categorie, c.theme, c.position, c.citation_verifiee, d.source_family,
                      d.title FROM claims c JOIN documents d ON d.id = c.document_id ORDER BY c.id"""
        ).fetchall()
    if not claims:
        st.info("Aucune affirmation pour l'instant : lancer `python -m tracewatch.analyse`.")
    else:
        v1, v2, v3 = st.columns(3)
        statut = v1.selectbox("Statut", ["Vérifiées", "Rejetées", "Toutes"])
        cats = v2.multiselect("Catégories", sorted({c_["categorie"] or "—" for c_ in claims}))
        themes = v3.multiselect("Thèmes", sorted({c_["theme"] or "—" for c_ in claims}))
        sel = [c_ for c_ in claims
               if (statut == "Toutes" or c_["citation_verifiee"] == (statut == "Vérifiées"))
               and (not cats or (c_["categorie"] or "—") in cats)
               and (not themes or (c_["theme"] or "—") in themes)]
        st.dataframe(pd.DataFrame([{
            "preuve": f"P{c_['id']}", "affirmation": c_["texte"], "catégorie": c_["categorie"],
            "thème": LIBELLES_THEMES.get(c_["theme"], c_["theme"]), "position": c_["position"],
            "famille": c_["source_family"], "vérifiée": bool(c_["citation_verifiee"]),
        } for c_ in sel]), hide_index=True, width="stretch", height=320)
        choix = st.selectbox("Remonter à la source d'une preuve", [f"P{c_['id']}" for c_ in sel])
        if choix:
            with conn() as c:
                p = tracer_preuve(c, choix)
            st.markdown(fiche_preuve(p), unsafe_allow_html=True)
            if not p.verifiee:
                st.error("Citation introuvable dans le document : cette affirmation est exclue du rapport.")

# ---------------------------------------------------------------------
# 4. Contradictions
# ---------------------------------------------------------------------
with onglets[3]:
    with conn() as c:
        divergences = detecter(c, PROFIL)
    if not divergences:
        st.info("Aucune contradiction détectée sur les preuves actuelles.")
    for dv in divergences:
        st.subheader(f"{LIBELLES_THEMES.get(dv.theme, dv.theme)} · {dv.type}")
        a, b = st.columns(2)
        for col, titre, liste, preuve in ((a, "Optimistes", dv.optimistes, dv.preuve_optimistes),
                                          (b, "Critiques", dv.critiques, dv.preuve_critiques)):
            col.markdown(f"**{titre}** : niveau {preuve.niveau} ({preuve.sources_independantes} sources "
                         f"indépendantes, {preuve.sources_fournisseurs} fournisseurs)")
            for cl in liste:
                col.markdown(f"- **P{cl['id']}** ({cl['source_family']}) {cl['texte']}  \n"
                             f"  [{cl['doc_titre'][:70]}]({cl['doc_url']})")

# ---------------------------------------------------------------------
# 5. Rapport
# ---------------------------------------------------------------------
with onglets[4]:
    st.markdown("Le rapport n'utilise que des preuves vérifiées ; il est refusé si une phrase n'est pas sourcée.")
    if st.button("Générer le rapport", type="primary"):
        with conn() as c:
            try:
                r = generer_rapport(c, PROFIL, motif="génération depuis le tableau de bord")
                st.session_state["rapport"] = r.markdown
                st.success(f"Rapport écrit : {r.chemin.name}. Contrôle de traçabilité passé. "
                           + ("Révisions : " + "; ".join(r.changements) if r.changements else "Aucune conclusion n'a changé."))
            except RapportNonConforme as e:
                st.error(str(e))
    texte = st.session_state.get("rapport")
    if texte is None:
        from tracewatch.rapport.generateur import DOSSIER_RAPPORTS
        dernier = DOSSIER_RAPPORTS / "dernier_rapport.md"
        texte = dernier.read_text(encoding="utf-8") if dernier.exists() else None
    if texte:
        st.download_button("Télécharger (.md)", texte, file_name="rapport_tracewatch.md")
        st.markdown(texte, unsafe_allow_html=True)

# ---------------------------------------------------------------------
# 6. Révisions : historique + ajouter une preuve
# ---------------------------------------------------------------------
with onglets[5]:
    with conn() as c:
        conclusions = c.execute("SELECT * FROM conclusions WHERE cle IS NOT NULL ORDER BY id").fetchall()
        if not conclusions:
            st.info("Aucune conclusion : générer le rapport une première fois.")
        for cc in conclusions:
            h = historique(c, cc["cle"])
            with st.expander(f"C{cc['id']} · {cc['cle']} · version {cc['version']} · niveau {cc['niveau_preuve']}"):
                st.write(cc["texte"])
                st.dataframe(pd.DataFrame([dict(x) for x in h]), hide_index=True, width="stretch")

    st.divider()
    st.subheader("Ajouter un document (nouvelle preuve)")
    st.caption("Le document est enregistré, dédoublonné et noté, puis analysé par l'IA si le quota le permet. "
               "Régénérer ensuite le rapport : les conclusions changées passent à la version suivante.")
    with st.form("ajout"):
        url = st.text_input("URL *")
        titre = st.text_input("Titre *")
        texte_doc = st.text_area("Texte ou résumé *", height=150)
        a1, a2 = st.columns(2)
        famille = a1.selectbox("Famille", SOURCE_FAMILIES, index=SOURCE_FAMILIES.index("independant"))
        date_pub = a2.date_input("Date de publication")
        envoyer = st.form_submit_button("Ajouter et analyser")
    if envoyer:
        if not (url and titre and texte_doc):
            st.error("URL, titre et texte sont obligatoires.")
        else:
            from tracewatch.analyse.extraction import BilanExtraction, analyser_document
            from tracewatch.analyse.llm_client import LLMIndisponible, QuotaDepasse, creer_client
            from tracewatch.normalisation.clusters import executer as regrouper

            with conn() as c:
                nouveau = enregistrer(c, Document(url=url, title=titre, text=texte_doc, source_family=famille,
                                                  source_name="ajout manuel", published_date=vers_iso(date_pub)))
                if not nouveau:
                    st.warning("Cette URL est déjà dans la base.")
                else:
                    regrouper(c, PROFIL)
                    calculer_scores(c, PROFIL)
                    doc = c.execute("SELECT * FROM documents WHERE url = ?", (url,)).fetchone()
                    bilan = BilanExtraction()
                    try:
                        analyser_document(c, creer_client(PROFIL), doc, PROFIL, bilan)
                        c.commit()
                        st.success(f"Document ajouté et analysé : {bilan.verifiees} affirmation(s) vérifiée(s), "
                                   f"{len(bilan.rejetees)} rejetée(s). Régénérer le rapport pour réviser les conclusions.")
                    except (QuotaDepasse, LLMIndisponible) as e:
                        st.warning(f"Document ajouté, mais analyse IA impossible pour l'instant : {e}")
