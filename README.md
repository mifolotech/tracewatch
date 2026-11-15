# TraceWatch

**Système de veille scientifique et technologique : de la question de veille aux preuves traçables, puis à une recommandation proportionnée au niveau de preuve.**

Projet d'examen final, Option A (cours *Veille scientifique et technologique*, L3 Génie logiciel & Réseaux). Équipe de 4 étudiants.

> **Thème de veille (thème 5) :** une entreprise de services numériques peut-elle, d'ici 12 mois, s'appuyer sur les résultats des benchmarks d'agents LLM (SWE-bench, WebArena, etc.) pour confier des tâches de développement de routine à des agents autonomes, ou ces scores surestiment-ils leur fiabilité réelle ?

---

## 1. Où en est-on ? (état d'avancement)

| Étape | Contenu | Statut | Livrable |
|---|---|---|---|
| 0 | Cadrage de la question de veille | **Fait** | `CADRAGE.md` |
| 1 | Architecture et stack | **Fait** | `ARCHITECTURE.md` |
| 2 | Profil de veille + squelette du projet | À faire | `config/profil_veille.yaml`, dépôt Git |
| 3 | Collecte multi-sources | À faire | `src/tracewatch/collecte/` |
| 4 | Normalisation et dédoublonnage | À faire | `src/tracewatch/normalisation/` |
| 5 | Qualification (scores, filtres) | À faire | `src/tracewatch/scoring/` |
| 6 | Analyse contrôlée par IA | À faire | `src/tracewatch/analyse/` |
| 7 | Traçabilité | À faire | `src/tracewatch/rapport/tracabilite.py` |
| 8 | Rapport + tableau de bord | À faire | `src/tracewatch/rapport/`, `app/` |
| 9 | Tests, sécurité, reproductibilité | À faire | `tests/`, `.env.example`, README final |
| 10 | Documentation et défense | À faire | `docs/` |

Décisions déjà prises : nom du projet **TraceWatch**, stack **Python + Streamlit + SQLite**, LLM interchangeable avec cache, hypothèse de départ **« pilote contrôlé »** (le système doit pouvoir la réfuter).

---

## 2. Ce qu'on construit

Une application qui passe d'une **question de veille** à un ensemble de **preuves traçables**, puis à une **synthèse exploitable pour décider**.

**Les 4 options de décision :** généraliser, pilote contrôlé, différer, exclure.

**Principe clé :** l'IA aide (extraction, classement) mais ne décide jamais seule. Chaque affirmation doit citer un passage réel du document source, vérifié automatiquement. Sinon elle est rejetée.

**Les 5 tests que le système doit réussir (examen) :**
1. Même information republiée sur plusieurs sites : elle ne compte pas comme plusieurs confirmations indépendantes.
2. Publication ancienne mais très pertinente : pertinence et fraîcheur restent deux dimensions séparées.
3. Affirmation d'un fournisseur contestée par une source indépendante : la divergence apparaît dans l'analyse et le rapport.
4. Requête trop large, beaucoup de bruit : l'utilisateur peut resserrer le corpus ou voir la faible qualité.
5. Élément critique du rapport contesté : on retrouve vite le document original qui le soutient.

---

## 3. Arborescence du projet

```
tracewatch/
├── README.md                  # ce fichier
├── CADRAGE.md                 # étape 0 (fait)
├── ARCHITECTURE.md            # étape 1 (fait)
├── requirements.txt
├── pyproject.toml             # rend "import tracewatch" possible partout
├── .env.example               # modèle de clé, sans secret
├── .gitignore                 # ignore .env, base, cache
│
├── config/
│   └── profil_veille.yaml     # étape 2 : question, mots-clés, sources, poids
│
├── data/
│   ├── demo/                  # jeu de démo figé + son cache LLM (versionné)
│   └── cache_llm/             # cache LLM de travail (ignoré par Git)
│
├── src/tracewatch/
│   ├── db.py                  # schéma SQLite
│   ├── collecte/              # étape 3 : python -m tracewatch.collecte
│   │   ├── __main__.py        # lance toutes les sources + bilan par famille
│   │   ├── commun.py          # profil, HTTP poli, dates, enregistrement
│   │   ├── arxiv.py
│   │   ├── openalex.py
│   │   ├── github.py
│   │   ├── rss.py
│   │   └── benchmarks.py
│   ├── normalisation/         # étape 4 : python -m tracewatch.normalisation
│   │   ├── __main__.py        # lance l'étape + bilan des doublons
│   │   ├── schema.py          # format unique de document
│   │   ├── dedup.py           # doublons (URL, DOI, similarité)
│   │   └── clusters.py        # travail original vs republications
│   ├── scoring/               # étape 5 : python -m tracewatch.scoring
│   │   ├── __main__.py        # calcule les scores + qualité complet vs resserré
│   │   ├── pertinence.py
│   │   ├── fraicheur.py
│   │   ├── fiabilite.py
│   │   └── qualite_corpus.py
│   ├── analyse/               # étape 6 : python -m tracewatch.analyse
│   │   ├── __main__.py        # sélection des documents, analyse, bilan
│   │   ├── llm_client.py      # LLM interchangeable + cache
│   │   ├── extraction.py      # affirmations + citations
│   │   ├── verification.py    # la citation existe-t-elle vraiment ?
│   │   ├── contradictions.py  # fournisseur vs indépendant
│   │   └── niveau_preuve.py
│   ├── rapport/               # étapes 7 et 8
│   │   ├── tracabilite.py     # phrase -> preuve -> source
│   │   ├── generateur.py
│   │   └── revision.py        # nouvelles preuves, historique
│   └── app/
│       └── streamlit_app.py   # tableau de bord
│
├── tests/                     # étape 9 : un fichier par scénario
│   ├── test_s1_doublons.py
│   ├── test_s2_fraicheur_pertinence.py
│   ├── test_s3_contradiction.py
│   ├── test_s4_bruit.py
│   └── test_s5_tracabilite.py
│
├── rapports/                  # rapports générés par le système
└── docs/                      # étape 10
    ├── architecture.md
    ├── schema_architecture.png
    └── note_methode.md        # note de 2 à 4 pages
```

---

## 4. Stack technique

| Besoin | Choix |
|---|---|
| Langage | Python 3.11+ |
| Interface | Streamlit |
| Base de données | SQLite |
| Collecte | `requests`, `feedparser` (arXiv, OpenAlex, GitHub, RSS) |
| Dédoublonnage | `scikit-learn` (TF-IDF, similarité cosinus) |
| Configuration | `PyYAML`, `python-dotenv` |
| Tests | `pytest` |
| LLM | Interchangeable (Gemini, Groq, Anthropic ou local), clé dans `.env` |

**Règle absolue :** aucune clé API dans le code ni dans les livrables. Les clés vont dans `.env`, qui n'est jamais envoyé sur GitHub.

---

## 5. Les étapes jusqu'au déploiement

### Étape 0. Cadrage (fait)
- [x] Question de décision, périmètre, horizon, 4 options
- [x] Faire valider `CADRAGE.md` par l'équipe
- [x] Envoyer la question à l'enseignant pour validation

### Étape 1. Architecture et stack (fait)
- [x] Stack, flux de données, contrat de données, module IA anti-hallucination
- [x] Faire valider `ARCHITECTURE.md` par l'équipe
- [x] Choisir le fournisseur LLM : **Gemini**
- [x] Créer **une seule clé** Gemini, gardée par un seul membre

### Étape 2. Profil de veille + squelette du projet
- [x] Créer l'arborescence ci-dessus
- [ ] Créer le dépôt GitHub et y envoyer le projet (voir section 7)
- [x] Écrire `requirements.txt`, `.gitignore`, `.env.example`, `pyproject.toml`
- [x] Écrire `config/profil_veille.yaml` : question, mots-clés, horizon, familles de sources, poids de scoring
- [x] Créer le schéma SQLite (`db.py`) selon le contrat de données
- **Fini quand :** `pip install -r requirements.txt` fonctionne et la base se crée (`python -m tracewatch.db`). ✅ Vérifié.

### Étape 3. Collecte multi-sources (au moins 4 familles)
- [x] arXiv et OpenAlex (publications)
- [x] Benchmarks (SWE-bench Verified + Lite, WebArena : leaderboards, avec mention vérifié / auto-déclaré)
- [x] GitHub (projets d'agents, issues sur les échecs)
- [x] Flux RSS (3 fournisseurs, 7 sources indépendantes, filtrés par mots-clés)
- [x] Chaque document garde URL, date, type de source, auteur/organisation, date de collecte
- Lancer : `python -m tracewatch.collecte` (ou `--sources arxiv rss` pour certaines sources). Relancer n'ajoute pas de doublon d'URL.
- ✅ Vérifié le 2026-11-15 : 1 337 documents réels, 5 familles (publication 397, benchmark 314, fournisseur 284, depot 180, independant 162).
- **Fini quand :** la base contient des documents réels d'au moins 4 familles.

### Étape 4. Normalisation et dédoublonnage (test 1)
- [x] Schéma unique de document (URL canonique, DOI, arXiv ID, empreinte du contenu)
- [x] Détection des doublons : URL canonique, DOI/arXiv ID, empreinte, similarité de texte (TF-IDF ≥ 0.85), titre inclus
- [x] Clusters « travail original » vs « republications » (5 articles sur la même étude = 1 preuve)
- Lancer : `python -m tracewatch.normalisation` (relançable, reconstruit les clusters)
- **Fini quand :** le test 1 passe. ✅ `pytest tests/test_s1_doublons.py` : 9/9. Sur la vraie base : 1 337 documents → 1 288 travaux distincts (48 groupes de doublons, tous vérifiés à la main).

### Étape 5. Qualification (tests 2 et 4)
- [x] Trois scores séparés : pertinence (mots-clés distincts, saturation), fraîcheur (demi-vie 12 mois), fiabilité (famille + vérifié/auto-déclaré)
- [x] Filtres de resserrement et indicateur de qualité du corpus (bruit, familles, indépendance, republications)
- Lancer : `python -m tracewatch.scoring`
- **Fini quand :** les tests 2 et 4 passent. ✅ 7/7 et 4/4. Vraie base : 26 % de bruit → 0 % après resserrement (944 travaux, 5 familles).

### Étape 6. Analyse contrôlée par IA (le cœur, 20 % de la note)
- [x] Client LLM interchangeable avec cache (Gemini `gemini-3.5-flash` ; sans clé : cache seul)
- [x] Extraction d'affirmations avec citation exacte
- [x] Vérification automatique que la citation existe dans le document (sinon rejet), revérifiée à chaque lancement
- [x] Classement : fait / interprétation / lacune / risque / signal (+ thème, position optimiste/critique, sous-question)
- [x] Détection des contradictions fournisseur vs indépendant (par thème, positions opposées)
- [x] Niveau de preuve selon le nombre de sources **indépendantes** (clusters, fournisseurs comptés à part)
- Lancer : `python -m tracewatch.analyse` (relançable : reprend là où le quota l'a arrêtée)
- **Fini quand :** le test 3 passe et aucune affirmation sans citation vérifiée n'entre dans le rapport. ✅ 15/15.
- ⚠ Quota gratuit Gemini : **20 appels par jour et par modèle**. Analyse réelle en cours : 19 documents sur 63 sélectionnés (48 affirmations, 100 % vérifiées).

### Étape 7. Traçabilité (test 5)
- [ ] Chaque phrase du rapport pointe vers un identifiant de preuve, puis vers le document original
- **Fini quand :** le test 5 passe et on retrouve la source d'une conclusion en un clic.

### Étape 8. Rapport + tableau de bord
- [ ] Rapport généré : question, décision recommandée proportionnée au niveau de preuve, faits, contradictions, incertitudes, risques, points à surveiller
- [ ] Tableau de bord Streamlit : sources par famille, fraîcheur, niveau de preuve, contradictions
- [ ] Révision : ajouter de nouvelles preuves, recalculer la conclusion, garder l'historique
- **Fini quand :** un rapport complet est généré depuis le jeu de démo.

### Étape 9. Tests, sécurité, reproductibilité
- [ ] Un test automatisé par scénario (les 5 ci-dessus)
- [ ] Jeu de démo figé dans `data/demo/`
- [ ] Vérifier qu'aucun secret n'est dans le dépôt (voir section 7)
- [ ] README d'installation testé sur une machine propre
- **Fini quand :** `pytest` est vert et quelqu'un d'extérieur lance l'application en suivant le README.

### Étape 10. Documentation et défense
- [ ] Note de 2 à 4 pages : méthode de veille, limites, risques
- [ ] Schéma d'architecture
- [ ] Déclaration des bibliothèques et services IA utilisés, sources citées
- [ ] Répétition de l'oral : chaque membre explique son module et répond individuellement

---

## 6. Répartition à 4

| Étape | Responsable | Soutien |
|---|---|---|
| 0, 1, 2 | A (lead) | Toute l'équipe |
| 3 Collecte | B | D |
| 4 Dédoublonnage, 5 Scoring | C | B, A |
| 6 Analyse IA | A | C |
| 7 Traçabilité, 8 Rapport et tableau de bord | D | A |
| 9 Tests et sécurité | C (tests), B (README, `.env`) | Tous |
| 10 Documentation | D (note), A (architecture) | Tous répètent l'oral |

Règles : une branche Git par personne, A fusionne, personne ne modifie le module d'un autre sans le prévenir. Chacun doit pouvoir expliquer le schéma global en 2 minutes.

---

## 7. Déployer sur GitHub

**Une seule fois (A) :**

```bash
git init
git add .
git commit -m "Initial commit: TraceWatch"
git branch -M main
git remote add origin https://github.com/<utilisateur>/tracewatch.git
git push -u origin main
```

Avant de créer le dépôt sur GitHub : **crée-le vide**, sans README ni `.gitignore` ajoutés par GitHub, puisqu'ils existent déjà ici. Ajoute les 3 autres membres comme collaborateurs (Settings, Collaborators).

**`.gitignore` minimal :**

```
.env
*.db
*.sqlite
data/cache_llm/*      # le cache de la démo, lui, est dans data/demo/
__pycache__/
.venv/
```

**Travail quotidien (chaque membre) :**

```bash
git checkout -b prenom-module        # une fois
git add . && git commit -m "message clair"
git push -u origin prenom-module
```

Puis ouvrir une Pull Request sur GitHub, que A fusionne dans `main`.

**Contrôle avant le rendu :**

```bash
git grep -n -i "api_key\|secret\|token"    # aucune vraie clé ne doit apparaître
git ls-files | grep -i "\.env"             # doit afficher seulement .env.example
```

Si une clé a été envoyée par erreur sur GitHub, **révoque-la et crée-en une nouvelle** : la supprimer d'un commit ne suffit pas.

**Rendu final :** tag de version et dépôt propre.

```bash
git tag v1.0
git push origin v1.0
```

---

## 8. Installation et lancement (à finaliser à l'étape 9)

```bash
git clone https://github.com/<utilisateur>/tracewatch.git
cd tracewatch
python -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # puis renseigner la clé LLM (facultatif en mode démo)
streamlit run src/tracewatch/app/streamlit_app.py
```

Le **mode démo** utilise `data/demo/` et le cache LLM : il fonctionne sans clé.

---

## 9. Livrables à rendre (checklist de l'examen)

- [ ] Application ou prototype exécutable
- [ ] Code source propre et documenté, sans secrets
- [ ] README d'installation et de lancement
- [ ] Description courte de l'architecture et des décisions techniques
- [ ] Jeu de données ou profil de démonstration
- [ ] Rapport de veille produit par le système
- [ ] Note de 2 à 4 pages (méthode, limites, risques)
- [ ] Présentation et démonstration orale, avec défense individuelle

**Barème indicatif :** question et méthode 15 %, collecte et traçabilité 15 %, normalisation et dédoublonnage 15 %, analyse des preuves 20 %, rapport 15 %, technique et sécurité 10 %, interface et défense 10 %.

**Ce que le sujet valorise :** une solution simple mais méthodologiquement juste, qui sait expliquer l'origine de ses conclusions, vaut mieux qu'une application spectaculaire.

---

## 10. Déclarations

- Bibliothèques : à compléter avec `requirements.txt`.
- Services IA utilisés : à déclarer (fournisseur et modèle).
- Toute source externe utilisée doit être citée.
