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

**Analyse contrôlée par IA.** Un LLM (Gemini, modèle `gemini-3.5-flash`, température 0) lit chaque document retenu. Il propose au plus cinq affirmations, chacune avec une **citation copiée mot pour mot**, une catégorie (fait, interprétation, lacune, risque, signal), un thème parmi six imposés et une position (optimiste, critique ou neutre). **Le code vérifie ensuite que la citation figure dans le document.** Seules des différences typographiques sont tolérées : casse, espaces, guillemets, tirets. Un mot ou un chiffre modifié suffit à rejeter l'affirmation. Le niveau de preuve d'un ensemble d'affirmations dépend du nombre de travaux indépendants qui le soutiennent : fort à partir de 3, moyen à 2, faible à 1. Les blogs fournisseurs sont comptés à part. Toutes les réponses du LLM sont mises en cache, ce qui rend l'analyse reproductible sans clé.

**Traçabilité et rapport.** Chaque affirmation vérifiée devient une preuve identifiée (P1, P2…). Le rapport est **rédigé par le code et non par le LLM**, à partir de ces seules preuves. Chaque phrase porte ses références, qui mènent à la citation exacte, au document, puis au document original du travail lorsque la citation provient d'une republication. Avant d'être enregistré, le rapport est contrôlé phrase par phrase. Une phrase sans preuve, ou une référence à une preuve rejetée, entraîne le refus du rapport.

**Décision et révision.** La recommandation suit une règle fixe et publique (`rapport/generateur.py`) :
- **exclure** si des échecs graves sont fortement documentés et qu'aucune preuve positive n'existe en usage réel ;
- **généraliser** si l'usage réel est fortement confirmé et que les critiques sont faibles ;
- **pilote contrôlé** si les résultats sont prometteurs **et** qu'un écart avec la fiabilité réelle est documenté ;
- **différer** dans les autres cas.

La confiance affichée est celle du plus faible niveau de preuve qui a déclenché la règle. Elle est plafonnée à « moyenne » tant qu'aucune source indépendante ne documente l'usage réel. Les conclusions sont versionnées : chaque recalcul qui change les preuves ou le niveau crée une nouvelle version, avec son motif.

## 3. Résultats

L'analyse a porté sur 19 documents (17 ont fourni des affirmations) : **48 affirmations proposées, 48 citations vérifiées**. Le seul rejet observé était un faux rejet dû à une espace laissée par le nettoyage HTML. Nous l'avons corrigé en ajoutant une tolérance typographique et un test.

| Thème | Sources optimistes | Sources critiques |
|---|---|---|
| Scores sur les benchmarks | 4 (fort) | 5 (fort) |
| Validité des benchmarks | 0 | 13 (fort) |
| Fiabilité et sécurité | 0 | 3 (fort) |
| Maturité des techniques | 2 (moyen) | 4 (fort) |
| Usage réel, supervision humaine | 0 | 0 |

**Recommandation : pilote contrôlé, confiance moyenne.** Les résultats sont prometteurs, avec des taux de résolution élevés sur SWE-bench Verified. Mais treize travaux indépendants mettent en cause la validité des benchmarks : tests défaillants, correctifs acceptés que des mainteneurs rejetteraient, données contaminées, écarts de plus de 50 % entre benchmarks publics et internes. L'hypothèse de départ est confirmée. La confiance reste moyenne, parce qu'aucune source analysée ne documente encore l'usage en conditions réelles, qui est pourtant le cœur de la question.

## 4. Limites

- **Analyse partielle.** L'offre gratuite de Gemini est limitée à 20 appels par jour. Seuls 19 des 63 documents sélectionnés sont analysés, presque tous des publications scientifiques. La contradiction entre fournisseurs et indépendants (scénario 3) est démontrée par un test automatisé, mais elle n'apparaît pas encore sur les données réelles. Les conclusions évolueront à mesure que l'analyse progresse, et l'historique des révisions en gardera la trace.
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
| Non-reproductibilité (sites qui changent, quotas) | Jeu de démo figé (125 documents réels et réponses du LLM), reconstruit sans clé ni réseau, avec un rapport identique |

## 6. Validation

Le projet compte 55 tests automatisés, dont un fichier par scénario d'examen :
1. doublons ;
2. fraîcheur et pertinence ;
3. contradiction ;
4. bruit ;
5. traçabilité.

S'y ajoutent des tests sur le rapport, la démo hors ligne, la sécurité et le tableau de bord. L'installation a été testée sur une copie propre du dépôt. Le test du scénario 3 remplace le LLM par un faux modèle aux réponses connues. Il vérifie ainsi le code (rejet d'une citation inventée, détection de la contradiction, comptage des sources) indépendamment du comportement du modèle réel.
