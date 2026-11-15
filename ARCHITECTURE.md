# TraceWatch : Architecture et stack (Étape 1)

## 1. Principe

TraceWatch transforme une **question de veille** en **preuves traçables**, puis en **recommandation proportionnée au niveau de preuve**. L'IA aide (extraction, classement) mais ne décide jamais seule : toute affirmation doit citer un passage réel du document source, vérifié automatiquement.

## 2. Stack et justification

| Besoin | Choix | Pourquoi |
|---|---|---|
| Langage | **Python 3.11+** | Maîtrisé par l'équipe, riche en bibliothèques de données et d'IA |
| Interface | **Streamlit** | Tableau de bord rapide à livrer et facile à démontrer |
| Base de données | **SQLite** | Un seul fichier, aucune installation, reproductible |
| Collecte | `requests`, `feedparser` | APIs publiques (arXiv, OpenAlex, GitHub) et flux RSS |
| Dédoublonnage | `scikit-learn` (TF-IDF, similarité cosinus) | Simple, explicable à l'oral, sans modèle lourd |
| Configuration | `PyYAML` + `python-dotenv` | Profil de veille en YAML, clés dans `.env` |
| Tests | `pytest` | Un test par scénario de l'examen |
| LLM | **Interchangeable** (Gemini, Groq, Anthropic, local) | Clé dans `.env`, jamais dans le code |

**Règles de sécurité :** `.env` ignoré par Git, `.env.example` sans secret, aucune clé dans le code ni dans les livrables.

## 3. Flux de données

```
Profil de veille (YAML)
        |
        v
  [1 Collecte] --> documents bruts (arXiv, OpenAlex, GitHub, RSS, benchmarks)
        |
        v
  [2 Normalisation + dédoublonnage] --> clusters "travail original / republications"
        |
        v
  [3 Scoring] --> pertinence | fraîcheur | fiabilité (trois scores séparés)
        |
        v
  [4 Analyse IA contrôlée] --> affirmations + citation vérifiée
        |                       contradictions, niveau de preuve
        v
  [5 Rapport + traçabilité] --> phrase -> preuve -> document source
        |
        v
  [6 Tableau de bord + révision] --> nouvelles preuves, historique
```

## 4. Module IA : comment on évite la boîte noire

1. Le LLM reçoit un document et doit renvoyer des affirmations avec une **citation exacte**.
2. Le système **vérifie** que la citation existe dans le texte du document. Sinon, l'affirmation est **rejetée**.
3. Les réponses du LLM sont **mises en cache** : la démo est reproductible, même sans clé.
4. Chaque affirmation est classée : **fait / interprétation / lacune / risque / signal**.
5. Le niveau de preuve d'une conclusion dépend du nombre de sources **indépendantes** (un cluster de republications compte pour une seule).

## 5. Contrat de données (à respecter par tous les modules)

**Document normalisé**

| Champ | Description |
|---|---|
| `id` | Identifiant interne unique |
| `url`, `canonical_url` | Lien d'origine et lien normalisé |
| `title`, `text` | Titre et texte (ou résumé) |
| `authors`, `organization` | Auteurs et organisation |
| `published_date`, `collected_date` | Date de publication et de collecte |
| `source_family` | publication, benchmark, depot, fournisseur, independant |
| `source_name` | Nom du site ou du dépôt |
| `doi`, `arxiv_id` | Identifiants, s'ils existent |
| `content_hash` | Empreinte du texte |
| `cluster_id` | Groupe de documents du même travail |

**Tables SQLite**

- `documents` : documents normalisés (ci-dessus)
- `clusters` : `cluster_id`, `document_original_id`, `taille`
- `scores` : `document_id`, `pertinence`, `fraicheur`, `fiabilite`
- `claims` : `id`, `document_id`, `texte`, `citation`, `citation_verifiee`, `categorie`
- `conclusions` : `id`, `texte`, `niveau_preuve`, `version`
- `conclusion_claims` : lien entre conclusion et affirmations
- `revisions` : historique des conclusions

## 6. Répartition par module

| Dossier | Responsable | Étape |
|---|---|---|
| `collecte/` | B | 3 |
| `normalisation/`, `scoring/` | C | 4 et 5 |
| `analyse/` | A | 6 |
| `rapport/`, `app/` | D | 7 et 8 |

## 7. Décisions à valider par l'équipe

- [x] Stack : Python + Streamlit + SQLite
- [x] Fournisseur LLM : Gemini (interchangeable si besoin)
- [x] Contrat de données ci-dessus
