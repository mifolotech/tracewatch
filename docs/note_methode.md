# TraceWatch : note de méthode

**Système de veille à preuves traçables. Thème 5 : agents autonomes LLM.**
Données arrêtées au 15 novembre 2026.

## 1. Question et périmètre

> D'ici 12 mois, une entreprise de services numériques peut-elle s'appuyer sur les résultats des benchmarks d'agents LLM (SWE-bench, WebArena…) pour confier des tâches de développement de routine à des agents autonomes, ou ces scores surestiment-ils leur fiabilité réelle, ce qui impose de se limiter à des expérimentations contrôlées ?

Le périmètre couvre des tâches à risque faible ou moyen : correction de tickets bien décrits, écriture de tests, revue de code de premier niveau, documentation, tri d'alertes. En sont exclus les décisions d'architecture, la mise en production sans validation humaine et les simples assistants de complétion de code. Nous appelons agent autonome un système qui enchaîne plusieurs actions (lire, modifier, exécuter, tester) sans validation humaine à chaque étape.

La réponse attendue est l'une de quatre options : **généraliser**, **pilote contrôlé**, **différer** ou **exclure**. Nous sommes partis de l'hypothèse « pilote contrôlé », que le système devait pouvoir réfuter si les preuves l'imposaient. La question est découpée en cinq sous-questions : ce que mesurent les benchmarks, l'écart entre scores et usage réel, la maturité des techniques, les échecs documentés, et les divergences entre fournisseurs et sources indépendantes.

## 2. Méthode de veille

Le principe directeur : **l'IA aide, mais ne décide jamais seule**. Toute affirmation qui entre dans le rapport doit citer un passage réel d'un document, et ce passage est vérifié par le code. La chaîne comporte six étapes, chacune relançable et testée.

**Collecte multi-sources.** Le profil de veille (`config/profil_veille.yaml`) fixe la question, l'horizon (sources de 2023 à 2026, contexte à partir de 2020), les mots-clés et les sources. Cinq familles ont été collectées, soit 1 337 documents réels :

| Famille | Documents | Sources |
|---|---|---|
| publication | 397 | arXiv, OpenAlex |
| benchmark | 314 | classements SWE-bench (Verified, Lite) et WebArena |
| fournisseur | 284 | blogs OpenAI, GitHub, Google DeepMind |
| dépôt | 180 | dépôts d'agents et issues GitHub décrivant des échecs |
| indépendant | 162 | METR, Princeton (AI as Normal Technology), chercheurs et presse spécialisée |

Chaque document conserve son URL, sa date de publication et de collecte, sa famille et son auteur ou organisation. Les classements de benchmarks sont collectés entrée par entrée, en gardant une information décisive pour notre question : le résultat a-t-il été **vérifié par l'équipe du benchmark** ou est-il **auto-déclaré** ? Sur 314 entrées, 173 sont auto-déclarées, 93 vérifiées et 48 rapportées par des tiers.

**Normalisation et dédoublonnage.** Deux documents sont regroupés comme un même travail s'ils ont la même URL normalisée, le même DOI, le même identifiant arXiv, un texte identique, un texte très proche (similarité cosinus TF-IDF ≥ 0,85) ou si le titre de l'un contient celui de l'autre. Chaque rapprochement garde sa raison. Le corpus compte **1 288 travaux distincts**, dont 48 groupes de doublons (97 documents, surtout des articles présents à la fois sur arXiv et en revue). **Un groupe compte pour une seule source indépendante** : cinq articles sur une même étude font une preuve, pas cinq. Deux choix ont été validés sur les données. Les entrées de classement, qui suivent toutes le même gabarit de texte, sont exclues de la comparaison par similarité (dix fausses paires mesurées sinon). Et l'on compare le corps du texte plutôt que le titre, qu'une republication change souvent.

**Qualification.** Chaque document reçoit **trois scores séparés**, jamais fusionnés :
- la **pertinence**, calculée sur les mots-clés distincts présents, avec un bonus pour le titre et une pénalité hors périmètre ;
- la **fraîcheur**, avec une demi-vie de 12 mois ;
- la **fiabilité**, qui dépend de la famille, avec un bonus pour un résultat vérifié et un malus pour un résultat auto-déclaré.

Une publication ancienne mais centrale reste donc pertinente. Un indicateur de qualité signale le bruit, le manque de familles, le manque de sources indépendantes et l'excès de republications. Le corpus brut contient 26 % de bruit (66 % des articles du blog OpenAI sont hors sujet). Une fois resserré (pertinence ≥ 0,3, un document par travail), il n'en contient plus du tout et garde ses cinq familles.

**Analyse contrôlée par IA.** Un LLM lit chaque document retenu : Gemini, à température 0, avec le modèle principal `gemini-3.5-flash`. Quand le quota gratuit d'un modèle est épuisé (20 appels par jour et par modèle), l'analyse bascule sur trois modèles de secours, et le modèle utilisé reste tracé pour chaque affirmation. Il propose au plus cinq affirmations, chacune avec une **citation copiée mot pour mot**, une catégorie (fait, interprétation, lacune, risque, signal), un thème parmi six imposés et une position (optimiste, critique ou neutre). **Le code vérifie ensuite que la citation figure dans le document.** Seules des différences typographiques sont tolérées : casse, espaces, guillemets, tirets. Un mot ou un chiffre modifié suffit à rejeter l'affirmation. Le niveau de preuve d'un ensemble d'affirmations dépend du nombre de travaux indépendants qui le soutiennent : fort à partir de 3, moyen à 2, faible à 1. Les blogs fournisseurs sont comptés à part. Toutes les réponses du LLM sont mises en cache, ce qui rend l'analyse reproductible sans clé.

**Traçabilité et rapport.** Chaque affirmation vérifiée devient une preuve identifiée (P1, P2…). Le rapport est **rédigé par le code et non par le LLM**, à partir de ces seules preuves. Chaque phrase porte ses références, qui mènent à la citation exacte, au document, puis au document original du travail lorsque la citation provient d'une republication. Avant d'être enregistré, le rapport est contrôlé phrase par phrase. Une phrase sans preuve, ou une référence à une preuve rejetée, entraîne le refus du rapport.

**Décision et révision.** La recommandation suit une règle fixe et publique (`rapport/generateur.py`) :
- **exclure** si des échecs graves sont fortement documentés, qu'aucune preuve positive n'existe en usage réel et qu'aucun résultat n'est prometteur ;
- **généraliser** si l'usage réel est fortement confirmé et que les critiques sont faibles ;
- **pilote contrôlé** si les résultats sont prometteurs **et** qu'un écart avec la fiabilité réelle est documenté ;
- **différer** dans les autres cas.

La confiance affichée est celle du plus faible niveau de preuve qui a déclenché la règle. Elle est plafonnée à « moyenne » tant qu'aucune source indépendante ne documente l'usage réel. Les conclusions sont versionnées : chaque recalcul qui change les preuves ou le niveau crée une nouvelle version, avec son motif.

## 3. Résultats

L'analyse a porté sur les 63 documents sélectionnés (les plus pertinents de chaque famille, un par travail). 48 d'entre eux ont fourni des affirmations : **146 proposées, 144 à citation vérifiée**. Les deux rejets sont de vraies erreurs du modèle : un mot modifié (« the blog post *do* report » au lieu de « *does* report ») et une phrase absente du document. Quatre faux rejets, dus au formatage Markdown et à une espace laissée par le nettoyage HTML, ont été corrigés par des tolérances typographiques, couvertes par des tests.

| Thème | Sources optimistes | Sources critiques |
|---|---|---|
| Scores sur les benchmarks | 11 (fort) | 12 (fort) |
| Validité des benchmarks | 0 | 30 (fort) |
| Résultats en usage réel | 0 (1 fournisseur) | 9 (fort) |
| Fiabilité et sécurité | 0 | 13 (fort) |
| Maturité des techniques | 4 (fort) | 7 (fort) |
| Supervision humaine | 0 | 1 (faible) |

**Contradictions entre fournisseurs et indépendants (scénario 3).** Elles apparaissent sur trois thèmes. Le plus net est l'usage réel : 3 affirmations optimistes d'un fournisseur, sans aucune source indépendante pour les appuyer, face à 13 affirmations critiques issues de 9 sources indépendantes.

**Recommandation : pilote contrôlé, confiance forte.** Les résultats sur les benchmarks sont prometteurs (11 sources indépendantes), mais trois écarts sont fortement documentés. Le premier porte sur la validité des benchmarks : tests défaillants, correctifs acceptés que des mainteneurs rejetteraient, contamination. Le deuxième porte sur l'usage réel. Le troisième porte sur la fiabilité et la sécurité : actions destructrices, erreurs non détectées par les humains qui supervisent. L'hypothèse de départ est confirmée, et ces écarts justifient que le pilote soit encadré par une revue humaine systématique.

**Une révision de la règle, assumée.** Avec l'analyse complète, la première version de la règle a recommandé « exclure ». Elle testait l'exclusion en premier, sans regarder les résultats prometteurs, alors que le CADRAGE réserve « exclure » aux cas où rien ne justifie même un essai encadré. Nous avons aligné la règle sur le CADRAGE. Modifier une règle après avoir vu le résultat est un risque méthodologique, c'est pourquoi le changement est tracé : la version « exclure » reste consultable dans l'historique de la conclusion (5 versions), et des tests fixent le nouveau comportement.

## 4. Limites

- **Analyse ciblée et hétérogène.** L'IA a analysé 63 documents, les plus pertinents, et non les 1 337. Quatre modèles Gemini ont été utilisés, à cause des quotas gratuits. Les deux vrais rejets viennent tous deux du modèle le plus léger, ce qui suggère une fidélité inégale entre modèles. Le modèle de chaque affirmation est tracé, ce qui permet de filtrer.
- **Équilibre des familles.** Les blogs fournisseurs ont fourni peu d'affirmations (3 documents) face aux indépendants (17) et aux publications (18). La littérature scientifique et indépendante est, par nature, plus critique. Le déséquilibre est visible dans le rapport, qui compte les fournisseurs à part.
- **Seule la citation est vérifiée, pas l'interprétation.** La catégorie, le thème et la position sont attribués par le LLM sans contrôle automatique. Une affirmation peut citer un passage réel et en forcer le sens. Pour cette raison, le rapport affiche la citation à côté de chaque affirmation, et le lecteur peut en juger.
- **Pertinence par mots-clés.** La méthode est explicable, mais elle se trompe parfois : un article d'économie sur le modèle « principal-agent » passe le seuil. Le bruit reste visible et filtrable.
- **Indépendance approximée.** Un groupe de doublons vaut une source. En revanche, deux articles distincts d'un même laboratoire comptent pour deux sources, et les financements ou affiliations communs ne sont pas détectés.
- **Couverture des sources.** Les sources sont en anglais uniquement. Il n'y a que trois blogs fournisseurs, Anthropic ne publiant pas de flux RSS. Les flux RSS ne donnent que les articles récents. Les retours d'expérience d'entreprises sont rares dans les sources ouvertes.
- **Seuils conventionnels.** La demi-vie de 12 mois, le seuil de similarité de 0,85, les poids de fiabilité et les seuils de la règle de décision sont des choix raisonnés mais arbitraires. Ils sont centralisés dans le profil et dans le code, donc modifiables et discutables.

## 5. Risques et parades

| Risque | Parade |
|---|---|
| Hallucination du LLM | Citation vérifiée mot pour mot, rejet automatique, revérification à chaque lancement |
| Injection de consignes cachées dans un document collecté | Le LLM ne déclenche aucune action et ne fait que proposer du texte ; toute sortie est vérifiée contre le document |
| Confiance excessive de l'utilisateur dans la machine | Niveau de preuve et confiance affichés, plafonnement explicite, citation visible pour chaque affirmation |
| Retrait d'un modèle par le fournisseur (vécu pendant le projet : `gemini-2.5` est refusé aux nouveaux comptes) | Client LLM interchangeable, modèle déclaré dans le profil, cache |
| Fuite de la clé d'API | `.env` ignoré par Git, test automatique qui cherche les clés et leur valeur réelle dans tous les fichiers du dépôt |
| Biais des sources (surreprésentation académique, intérêt commercial des fournisseurs) | Fiabilité par famille, fournisseurs comptés à part, alerte si les sources indépendantes manquent |
| Non-reproductibilité (sites qui changent, quotas) | Jeu de démo figé (171 documents réels et réponses du LLM), reconstruit sans clé ni réseau, avec un rapport identique |

## 6. Validation

Le projet compte 62 tests automatisés, dont un fichier par scénario d'examen :
1. doublons ;
2. fraîcheur et pertinence ;
3. contradiction ;
4. bruit ;
5. traçabilité.

S'y ajoutent des tests sur le rapport et la règle de décision, la démo hors ligne, la sécurité et le tableau de bord. L'installation a été testée sur une copie propre du dépôt. Le test du scénario 3 remplace le LLM par un faux modèle aux réponses connues. Il vérifie ainsi le code (rejet d'une citation inventée, détection de la contradiction, comptage des sources) indépendamment du comportement du modèle réel.
