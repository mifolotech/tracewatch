# CADRAGE : Système de veille, thème 5 (agents autonomes LLM)

## 1. Question de décision

> **D'ici 12 mois, une entreprise de services numériques peut-elle s'appuyer sur les résultats des benchmarks d'agents LLM (SWE-bench, WebArena, etc.) pour confier des tâches de développement de routine à des agents autonomes, ou ces scores surestiment-ils leur fiabilité réelle, ce qui impose de se limiter à des expérimentations contrôlées ?**

**Enjeu :** distinguer les performances sur benchmarks, les démonstrations spectaculaires et la capacité réelle à travailler durablement dans un environnement professionnel.

## 2. Périmètre

**Tâches concernées (routine, risque faible à moyen) :**
- Correction de bugs simples et de tickets bien décrits
- Écriture et exécution de tests
- Revue de code de premier niveau
- Rédaction et mise à jour de la documentation technique
- Analyse de logs et tri d'alertes

**Exclus :**
- Décisions d'architecture et décisions métier
- Déploiement en production sans validation humaine
- Code critique pour la sécurité ou fortement réglementé
- Simples assistants de complétion de code (ce ne sont pas des agents) et agents grand public

**Définition retenue :** un agent autonome planifie et exécute plusieurs actions successives (lire une documentation, modifier du code, appeler des outils, lancer des tests, produire un compte rendu) sans validation humaine à chaque action.

## 3. Horizon

**12 mois.** Sources prioritaires : 2023 à 2026. Les sources plus anciennes servent de contexte (fraîcheur faible, pertinence éventuellement élevée).

## 4. Les 4 options de décision

| Option | Quand la recommander |
|---|---|
| **Généraliser** | Bons scores confirmés par des évaluations indépendantes sur des tâches réalistes, échecs rares et peu graves, contrôles de sécurité éprouvés. |
| **Pilote contrôlé** | Résultats prometteurs sur tâches à faible risque, mais écart avec l'usage réel et fiabilité durable encore peu démontrés. |
| **Différer** | Preuves insuffisantes ou contradictoires, benchmarks peu représentatifs du travail réel. |
| **Exclure** | Échecs graves documentés et risques structurels non résolus. |

**Hypothèse de départ :** pilote contrôlé. Le système doit pouvoir la réfuter si les preuves l'imposent.

## 5. Sous-questions de veille

1. Que mesurent réellement les benchmarks d'agents, et quelles sont leurs limites (contamination des données, tâches peu réalistes) ?
2. Quel écart observe-t-on entre scores publiés, évaluations indépendantes et retours d'expérience réels ?
3. Quelles approches d'agents (planification, mémoire, outils, multi-agents) sont réellement matures ?
4. Quels échecs et risques sont documentés (fiabilité, injection de prompt, actions destructrices) ?
5. Où les affirmations des fournisseurs divergent-elles des sources indépendantes ?

## Validation
- [x] Cadrage validé par l'équipe
- [x] Envoyé à l'enseignant pour validation
