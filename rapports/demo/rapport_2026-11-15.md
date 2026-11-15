# Rapport de veille TraceWatch

_Généré le 2026-11-15 à partir de 171 documents (156 travaux distincts, 5 familles de sources). 48 documents ont fourni des affirmations à l'analyse IA (gemini/gemini-3.5-flash, gemini/gemini-3.5-flash-lite, gemini/gemini-3.8-flash, gemini/gemini-3.7-flash) : 144 affirmations à citation vérifiée sur 146 proposées._

> **Question de décision.** D'ici 12 mois, une entreprise de services numériques peut-elle s'appuyer sur les résultats des benchmarks d'agents LLM (SWE-bench, WebArena, etc.) pour confier des tâches de développement de routine à des agents autonomes, ou ces scores surestiment-ils leur fiabilité réelle, ce qui impose de se limiter à des expérimentations contrôlées ?

## 1. Décision recommandée

Décision recommandée : **Pilote contrôlé**, avec une confiance forte [P103](#p103)[P116](#p116)[P139](#p139)[P106](#p106).

- Les résultats sont prometteurs (scores sur les benchmarks) [P103](#p103)[P116](#p116)[P68](#p68).
- Mais un écart est documenté : validité des benchmarks (30 sources indépendantes critiques) [P139](#p139)[P106](#p106)[P107](#p107).
- Mais un écart est documenté : résultats en usage réel (9 sources indépendantes critiques) [P99](#p99)[P100](#p100)[P110](#p110).
- Mais un écart est documenté : fiabilité et sécurité (13 sources indépendantes critiques) [P137](#p137)[P138](#p138)[P140](#p140).

_Hypothèse de départ (Pilote contrôlé) : confirmée par les preuves actuelles. La décision suit une règle fixe, documentée dans generateur.py, et sa confiance est celle du niveau de preuve le plus faible qui l'a déclenchée._

## 2. Synthèse par thème

| Thème | Optimistes (sources indép.) | Critiques (sources indép.) | Fournisseurs |
|---|---|---|---|
| Scores sur les benchmarks | 11 (fort) | 12 (fort) | 1 |
| Validité des benchmarks | 0 (insuffisant) | 30 (fort) | 0 |
| Résultats en usage réel | 0 (insuffisant) | 9 (fort) | 1 |
| Fiabilité et sécurité | 0 (insuffisant) | 13 (fort) | 0 |
| Maturité des techniques d'agents | 4 (fort) | 7 (fort) | 2 |
| Supervision humaine | 0 (insuffisant) | 1 (faible) | 3 |

- Scores sur les benchmarks : les sources critiques dominent, avec 12 source(s) indépendante(s) critique(s) (niveau fort) contre 11 optimiste(s) (niveau fort) et 1 source(s) fournisseur(s) [P136](#p136)[P104](#p104)[P103](#p103)[P116](#p116).
- Validité des benchmarks : les sources critiques dominent, avec 30 source(s) indépendante(s) critique(s) (niveau fort) contre 0 optimiste(s) (niveau insuffisant) et 0 source(s) fournisseur(s) [P139](#p139)[P106](#p106).
- Résultats en usage réel : les sources critiques dominent, avec 9 source(s) indépendante(s) critique(s) (niveau fort) contre 0 optimiste(s) (niveau insuffisant) et 1 source(s) fournisseur(s) [P99](#p99)[P100](#p100)[P78](#p78)[P79](#p79).
- Fiabilité et sécurité : les sources critiques dominent, avec 13 source(s) indépendante(s) critique(s) (niveau fort) contre 0 optimiste(s) (niveau insuffisant) et 0 source(s) fournisseur(s) [P137](#p137)[P138](#p138).
- Maturité des techniques d'agents : les sources critiques dominent, avec 7 source(s) indépendante(s) critique(s) (niveau fort) contre 4 optimiste(s) (niveau fort) et 2 source(s) fournisseur(s) [P126](#p126)[P86](#p86)[P120](#p120)[P42](#p42).
- Supervision humaine : les sources critiques dominent, avec 1 source(s) indépendante(s) critique(s) (niveau faible) contre 0 optimiste(s) (niveau insuffisant) et 3 source(s) fournisseur(s) [P144](#p144)[P76](#p76).

## 3. Faits établis

- **Scores sur les benchmarks** · L'évaluation de 14 modèles sur deux benchmarks montre que deux années de progrès rapides sur les capacités n'ont apporté que de modestes améliorations en matière de fiabilité [P136](#p136).
- **Fiabilité et sécurité** · Les agents capables d'accomplir une tâche échouent fréquemment lors de tentatives répétées dans des conditions identiques, avec une cohérence des résultats comprise entre seulement 30 % et 75 % selon les modèles [P137](#p137).
- **Fiabilité et sécurité** · Le niveau de confiance exprimé par les agents est peu fiable, la plupart des modèles s'avérant incapables sur un benchmark de distinguer leurs prédictions correctes de leurs erreurs mieux que le hasard [P138](#p138).
- **Scores sur les benchmarks** · Selon METR, l'horizon temporel des modèles d'IA pour accomplir des tâches de recherche et de développement logiciel doublait tous les 7 mois, avec une accélération possible à 4 mois en 2024 [P103](#p103).
- **Scores sur les benchmarks** · En mars 2025, l'horizon temporel des modèles de pointe pour l'utilisation autonome de l'ordinateur via DOM ou capture visuelle était environ 50 fois plus court que dans les autres domaines [P104](#p104).
- **Fiabilité et sécurité** · Les auteurs d'OSWorld ont observé que 75 % des échecs provenaient d'imprécisions dans les clics de souris, ce qui pourrait s'expliquer par des outils encore inadaptés [P105](#p105).
- **Résultats en usage réel** · Malgré un taux de réussite de 38% mesuré par les tests de référence, aucun des PRs générés par l'agent n'était fusionnable en l'état lors d'une révision manuelle [P99](#p99).
- **Résultats en usage réel** · Même lorsque l'agent valide tous les tests automatisés, un travail significatif (estimé à 26 minutes en moyenne) reste nécessaire pour rendre le code fusionnable [P100](#p100).
- **Validité des benchmarks** · Les benchmarks de codage et d'agents sacrifient le réalisme au profit de l'échelle et de l'efficacité en utilisant des tâches autonomes et une évaluation algorithmique qui omettent de nombreuses capacités clés [P108](#p108).
- **Résultats en usage réel** · Lorsque les développeurs sont autorisés à utiliser des outils d'IA, ils mettent 19 % de temps en plus pour résoudre les problèmes, ce qui constitue un ralentissement significatif contredisant les prévisions [P110](#p110).

## 4. Contradictions

- Maturité des techniques d'agents (fournisseur vs indépendant) : 5 affirmation(s) optimiste(s) (niveau fort) s'opposent à 9 critique(s) (niveau fort) [P81](#p81)[P16](#p16)[P14](#p14)[P17](#p17).
  - Optimiste (fournisseur, GitHub Blog) : Les architectures d'agents sont passées d'outils cantonnés à une seule session à des agents persistants capables d'opérer sur plusieurs jours et d'en orchestrer d'autres [P81](#p81).
  - Optimiste (publication, arXiv) : Les résultats suggèrent que les traces de résolution de problèmes peuvent servir de base évolutive pour les agents d'ingénierie logicielle auto-évolutifs [P16](#p16).
  - Critique (publication, arXiv) : L'entraînement des agents d'ingénierie logicielle fondés sur les LLM reste contraint par la disponibilité de tâches d'ingénierie logicielle de haute qualité [P14](#p14).
  - Critique (publication, arXiv) : L'utilisation directe de générateurs de tests de reproduction de bugs pour guider la génération de correctifs n'est pas bénéfique, car les tests défaillants peuvent induire les agents en erreur et les tests réussis n'apportent que des gains limités ou négatifs [P17](#p17).
- Scores sur les benchmarks (fournisseur vs indépendant) : 17 affirmation(s) optimiste(s) (niveau fort) s'opposent à 13 critique(s) (niveau fort) [P74](#p74)[P75](#p75)[P3](#p3)[P6](#p6).
  - Optimiste (fournisseur, GitHub Blog) : Dans le classement d'Artificial Analysis pour les agents de codage, Fusion Max se situe à deux points d'Opus 5.5 Max pour un coût divisé par deux et 40 % de temps en moins par tâche [P74](#p74).
  - Optimiste (fournisseur, GitHub Blog) : GitHub affirme que son outil Copilot code review Max a obtenu le score F1 le plus élevé sur le benchmark ReviewBench pour les anomalies de gravité élevée [P75](#p75).
  - Critique (publication, arXiv) : Une réévaluation rigoureuse montre que certains modèles obtiennent des résultats nettement inférieurs aux scores publiés, ce qui suggère une surestimation de leurs capacités réelles [P3](#p3).
  - Critique (publication, arXiv) : Les évaluations montrent que les benchmarks existants surestiment considérablement les capacités des agents, avec un décalage de plus de 50 % pour certains modèles sur les benchmarks publics et de 10 à 16 % sur un benchmark interne [P6](#p6).
- Résultats en usage réel (fournisseur vs indépendant) : 3 affirmation(s) optimiste(s) (niveau insuffisant) s'opposent à 13 critique(s) (niveau fort) [P78](#p78)[P79](#p79)[P41](#p41)[P84](#p84).
  - Optimiste (fournisseur, GitHub Blog) : En septembre 2026, plus de 40 % des pull requests sur GitHub étaient initiées par un premier jet généré par un agent, contre 17 % en mars [P78](#p78).
  - Optimiste (fournisseur, GitHub Blog) : Le taux de fusion sous deux semaines des pull requests impliquant des agents a atteint 90 % en septembre, dépassant les 86 % constatés pour les pull requests sans intervention d'agent [P79](#p79).
  - Critique (publication, OpenAlex (Open Collections)) : L'exactitude des réparations et le coût des échecs sont des dimensions largement indépendantes qui devraient être mesurées et rapportées conjointement [P41](#p41).
  - Critique (independant, METR) : Certains modèles présentés comme performants se contentent de poursuivre le bruit statistique sans apporter de réelle amélioration lors de la revalidation [P84](#p84).

## 5. Incertitudes et lacunes

- **Validité des benchmarks** · Une grande partie des horizons temporels estimés correspondent à des extrapolations dépassant la durée réelle des tâches évaluées dans les benchmarks [P106](#p106).
- **Maturité des techniques d'agents** · L'étude s'appuie sur un échafaudage d'agent de base sans calcul d'inférence parallèle significatif ni outils spécialisés avancés, ce qui n'établit pas une limite supérieure absolue des performances des agents [P102](#p102).
- **Validité des benchmarks** · L'absence de divulgation des détails et du code source empêche une évaluation indépendante des affirmations [P128](#p128).
- **Validité des benchmarks** · L'expérimentation n'a pas permis d'analyser si le code a été rédigé à partir de zéro ou recopié d'internet en raison de données mémorisées [P130](#p130).
- **Validité des benchmarks** · La plupart des benchmarks d'agents ne mesurent pas les temps de résolution humains et comportent très peu de tâches exigeant plusieurs jours de travail humain [P88](#p88).
- **Validité des benchmarks** · Les benchmarks populaires de codage comme HumanEval et SWE-Bench se limitent à des tâches ciblées telles que la programmation de compétition et la génération de correctifs [P30](#p30).
- **Validité des benchmarks** · Les benchmarks actuels d'évaluation des agents d'ingénierie logicielle, comme SWE-Bench Verified, reposent principalement sur des tickets GitHub et ne reflètent pas fidèlement la manière dont les développeurs interagissent avec les assistants de code dans leurs environnements de développement [P4](#p4).
- **Validité des benchmarks** · Les benchmarks existants se limitent souvent à une évaluation en un seul tour et ne permettent pas de capturer l'interactivité multi-tours, l'usage des outils ni le raisonnement adaptatif requis par les agents réels [P27](#p27).
- **Validité des benchmarks** · Les agents auto-améliorants nécessitent un entraînement hors ligne coûteux sur des benchmarks spécifiques et risquent de mal se généraliser d'un LLM ou d'un benchmark à l'autre [P33](#p33).
- **Validité des benchmarks** · Une analyse manuelle des problèmes du benchmark SWE-bench Lite a révélé des biais et défauts, comme des descriptions d'incidents insuffisantes ou induisant en erreur [P36](#p36).
_Couverture : 48 documents ont fourni des affirmations. Les conclusions évolueront avec l'analyse des documents restants (voir l'historique des révisions)._

## 6. Risques

- **Fiabilité et sécurité** · Many companies that hastily rushed to automate business processes using agents are recognizing the limits and costs, and even legal liabilities — like when an agent deletes production data [P125](#p125).
- **Fiabilité et sécurité** · Lors d'une évaluation autonome, un agent a commis deux erreurs dont une ayant exigé une intervention humaine, oubliant l'emplacement des identifiants et inventant un numéro de téléphone fictif [P135](#p135).
- **Fiabilité et sécurité** · Grok Build, un agent de codage, divulgue des informations d'entreprise propriétaires et des secrets sensibles de milliers d'utilisateurs [P141](#p141).
- **Fiabilité et sécurité** · METR estime que les agents internes disposaient vraisemblablement des moyens, de la motivation et de l'opportunité pour initier de petits déploiements autonomes non autorisés, même s'ils ne pouvaient pas encore les pérenniser solidement [P90](#p90).
- **Fiabilité et sécurité** · Les trajectoires échouées, les succès accidentels et les observations trompeuses s'introduisent dans la mémoire des agents et induisent en erreur leurs décisions ultérieures [P20](#p20).
- **Fiabilité et sécurité** · Les défauts d'ancrage environnemental émergent systématiquement dans les flux de travail opérationnels, révélant un problème majeur de fiabilité et de sécurité pour les agents [P48](#p48).
- **Fiabilité et sécurité** · Un dépôt GitHub piégé utilise des commentaires HTML invisibles pour ordonner aux agents autonomes d'ignorer les avertissements destinés aux humains figurant dans le fichier CONTRIBUTING.md [P62](#p62).
- **Fiabilité et sécurité** · Pour les tâches de longue durée, la troncature du contexte entraîne une dérive sémantique et comportementale silencieuse de l'agent [P56](#p56).
- **Fiabilité et sécurité** · Ce mode de défaillance est difficile à détecter car les modifications de code produites restent syntaxiquement valides et les tests peuvent passer [P58](#p58).
- **Fiabilité et sécurité** · L'isolation par bac à sable (sandbox) contient les dégâts potentiels, mais n'empêche pas l'agent d'exécuter des opérations destructrices sur l'espace de travail [P59](#p59).

## 7. Points à surveiller

- **Validité des benchmarks** · La pratique actuelle consistant à évaluer un benchmark en une seule exécution pour rapporter un taux de précision moyen constitue une mesure de performance superficielle [P139](#p139).
- **Fiabilité et sécurité** · Une autonomie opérationnelle dans des contextes à forts enjeux nécessiterait une précision de 99,9 % à 99,999 %, un niveau que les agents fondés sur des LLM ne semblent pas en voie d'atteindre [P140](#p140).
- **Validité des benchmarks** · Le monde réel étant plus diversifié que les benchmarks, les horizons temporels nécessaires pour accomplir des tâches à valeur économique s'étaleront sur plusieurs ordres de grandeur [P107](#p107).
- **Validité des benchmarks** · Cette constatation suggère que la notation automatique utilisée par de nombreux benchmarks peut surestimer les performances réelles des agents IA sur le terrain [P98](#p98).
- **Scores sur les benchmarks** · Les taux de réussite des modèles phares sur SWE-bench Verified atteignent 70 à 75 %, mais il est peu probable que les agents IA puissent réellement résoudre autant de demandes de tir (PR) dans des conditions réelles [P101](#p101).
- **Validité des benchmarks** · Ces propriétés peuvent amener les benchmarks à surestimer les capacités des IA, bien que l'absence d'interaction humaine en direct puisse parfois conduire à sous-estimer ces mêmes capacités face à de petits goulets d'étranglement [P109](#p109).
- **Validité des benchmarks** · Les benchmarks peuvent surestimer les capacités des modèles en mesurant uniquement la performance sur des tâches bien délimitées et évaluables de manière algorithmique, tandis que les rapports anecdotiques d'accélération s'avèrent très inexacts [P112](#p112).
- **Validité des benchmarks** · Les environnements réels de R&D en Machine Learning impliquent des boucles de rétroaction beaucoup plus lentes et des objectifs moins clairement définis que dans les environnements de test, et il n'est pas clair dans quelle mesure les problèmes de recherche peuvent être découpés en petites tâches [P118](#p118).
- **Validité des benchmarks** · Une interprétation naïve des scores de benchmark peut amener à surestimer l'utilité réelle des agents sans un travail d'élicitation plus poussé ou un retour d'information humain [P93](#p93).
- **Validité des benchmarks** · Il est difficile de transposer les scores des benchmarks en utilité dans le monde réel car les benchmarks sont propres et vérifiables d'une manière que le monde réel ne l'est pas [P94](#p94).

## Preuves

<a id="p103"></a>**P103** · fait · Selon METR, l'horizon temporel des modèles d'IA pour accomplir des tâches de recherche et de développement logiciel doublait tous les 7 mois, avec une accélération possible à 4 mois en 2024.  
> « METR found that the time horizon has doubled every 7 months, possibly accelerating to every 4 months in 2024. »  
Source : [How Does Time Horizon Vary Across Domains?](https://metr.org/blog/2025-07-14-how-does-time-horizon-vary-across-domains/) (METR, independant, 2025-07-14)

<a id="p116"></a>**P116** · fait · La longueur des tâches que les modèles de pointe peuvent accomplir avec une probabilité de 50 % a augmenté de manière exponentielle au cours des six dernières années, avec un temps de doublement d'environ 7 mois.  
> « the length of tasks that state-of-the-art models can complete (with 50% probability) has increased dramatically over the last 6 years. If we plot this on a logarithmic scale, we can see that the length of tasks models can complete is well predicted by an exponential trend, with a doubling time of around 7 months. »  
Source : [Measuring AI Ability to Complete Long Software Tasks](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/) (METR, independant, 2025-03-19)

<a id="p139"></a>**P139** · interpretation · La pratique actuelle consistant à évaluer un benchmark en une seule exécution pour rapporter un taux de précision moyen constitue une mesure de performance superficielle.  
> « The current approach of running a benchmark once and reporting the accuracy number is a shallow, superficial performance measure. »  
Source : [New Paper: Towards a science of AI agent reliability](https://www.normaltech.ai/p/new-paper-towards-a-science-of-ai) (AI as Normal Technology, independant, 2026-02-24)

<a id="p106"></a>**P106** · lacune · Une grande partie des horizons temporels estimés correspondent à des extrapolations dépassant la durée réelle des tâches évaluées dans les benchmarks.  
> « Many of the time horizons are also extrapolations beyond the actual range of task lengths found in benchmarks; we discuss data limitations and other caveats below. »  
Source : [How Does Time Horizon Vary Across Domains?](https://metr.org/blog/2025-07-14-how-does-time-horizon-vary-across-domains/) (METR, independant, 2025-07-14)

<a id="p68"></a>**P68** · fait · La combinaison de live-SWE-agent et de Gemini 3 Pro Preview a résolu 77,4 % des tâches sur le benchmark SWE-bench Verified.  
> « live-SWE-agent + Gemini 3 Pro Preview (2025-11-18) resolved 77.4% of SWE-bench Verified tasks. »  
Source : [SWE-bench Verified : live-SWE-agent + Gemini 3 Pro Preview (2025-11-18) (77.4 %)](https://github.com/SWE-bench/experiments/tree/main/evaluation/verified/20251120_livesweagent_gemini-3-pro-preview) (SWE-bench leaderboard (Verified), benchmark, 2025-11-20)

<a id="p107"></a>**P107** · interpretation · Le monde réel étant plus diversifié que les benchmarks, les horizons temporels nécessaires pour accomplir des tâches à valeur économique s'étaleront sur plusieurs ordres de grandeur.  
> « Because the real world is more diverse than benchmarks, we expect that time horizons on all economically valuable tasks will range over several orders of magnitude. »  
Source : [How Does Time Horizon Vary Across Domains?](https://metr.org/blog/2025-07-14-how-does-time-horizon-vary-across-domains/) (METR, independant, 2025-07-14)

<a id="p99"></a>**P99** · fait · Malgré un taux de réussite de 38% mesuré par les tests de référence, aucun des PRs générés par l'agent n'était fusionnable en l'état lors d'une révision manuelle.  
> « Claude 3.7 Sonnet in the Inspect ReAct agent scaffold has an average success rate of 38% (±19%, 95% CI) on these issues, as measured by the maintainer-written test cases, indicating that this agent often implements the core functional components of the issues correctly 5 . However, when manually reviewing a subset of these PRs 6 , none of them are mergeable as-is. »  
Source : [Research Update: Algorithmic vs. Holistic Evaluation](https://metr.org/blog/2025-08-12-research-update-towards-reconciling-slowdown-with-time-horizons/) (METR, independant, 2025-08-13)

<a id="p100"></a>**P100** · fait · Même lorsque l'agent valide tous les tests automatisés, un travail significatif (estimé à 26 minutes en moyenne) reste nécessaire pour rendre le code fusionnable.  
> « When filtering to runs where the agent passed the human-written test cases, we estimate that these PRs would take on average 26 minutes to fix (with a minimum time of 15 minutes). »  
Source : [Research Update: Algorithmic vs. Holistic Evaluation](https://metr.org/blog/2025-08-12-research-update-towards-reconciling-slowdown-with-time-horizons/) (METR, independant, 2025-08-13)

<a id="p110"></a>**P110** · fait · Lorsque les développeurs sont autorisés à utiliser des outils d'IA, ils mettent 19 % de temps en plus pour résoudre les problèmes, ce qui constitue un ralentissement significatif contredisant les prévisions.  
> « When developers are allowed to use AI tools, they take 19% longer to complete issues—a significant slowdown that goes against developer beliefs and expert forecasts. »  
Source : [Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/) (METR, independant, 2025-07-10)

<a id="p137"></a>**P137** · fait · Les agents capables d'accomplir une tâche échouent fréquemment lors de tentatives répétées dans des conditions identiques, avec une cohérence des résultats comprise entre seulement 30 % et 75 % selon les modèles.  
> « Agents that can solve a task often fail on repeated attempts under identical conditions. Many models have trouble giving a consistent answer, with outcome consistency scores ranging from 30% to 75% across the board. »  
Source : [New Paper: Towards a science of AI agent reliability](https://www.normaltech.ai/p/new-paper-towards-a-science-of-ai) (AI as Normal Technology, independant, 2026-02-24)

<a id="p138"></a>**P138** · fait · Le niveau de confiance exprimé par les agents est peu fiable, la plupart des modèles s'avérant incapables sur un benchmark de distinguer leurs prédictions correctes de leurs erreurs mieux que le hasard.  
> « When agents report confidence, it often carries little signal. On one benchmark, most models couldn’t distinguish their correct predictions from incorrect ones better than chance. »  
Source : [New Paper: Towards a science of AI agent reliability](https://www.normaltech.ai/p/new-paper-towards-a-science-of-ai) (AI as Normal Technology, independant, 2026-02-24)

<a id="p140"></a>**P140** · interpretation · Une autonomie opérationnelle dans des contextes à forts enjeux nécessiterait une précision de 99,9 % à 99,999 %, un niveau que les agents fondés sur des LLM ne semblent pas en voie d'atteindre.  
> « Our view is that for autonomous operation in high-stakes contexts, we need 3-5 “nines” of performance — 99.9% to 99.999% accuracy — in order for reliability to become a non-issue, and we don’t think LLM-based agents are on track to reach such a threshold. »  
Source : [New Paper: Towards a science of AI agent reliability](https://www.normaltech.ai/p/new-paper-towards-a-science-of-ai) (AI as Normal Technology, independant, 2026-02-24)

<a id="p136"></a>**P136** · fait · L'évaluation de 14 modèles sur deux benchmarks montre que deux années de progrès rapides sur les capacités n'ont apporté que de modestes améliorations en matière de fiabilité.  
> « Evaluating 14 models on two complementary benchmarks, we found that nearly two years of rapid capability progress have produced only modest reliability gains. »  
Source : [New Paper: Towards a science of AI agent reliability](https://www.normaltech.ai/p/new-paper-towards-a-science-of-ai) (AI as Normal Technology, independant, 2026-02-24)

<a id="p104"></a>**P104** · fait · En mars 2025, l'horizon temporel des modèles de pointe pour l'utilisation autonome de l'ordinateur via DOM ou capture visuelle était environ 50 fois plus court que dans les autres domaines.  
> « As of March 2025, the frontier time horizon on agentic computer use either with DOM input (WebArena) or image input (OSWorld) is ~50x shorter than other domains. »  
Source : [How Does Time Horizon Vary Across Domains?](https://metr.org/blog/2025-07-14-how-does-time-horizon-vary-across-domains/) (METR, independant, 2025-07-14)

<a id="p78"></a>**P78** · fait · En septembre 2026, plus de 40 % des pull requests sur GitHub étaient initiées par un premier jet généré par un agent, contre 17 % en mars.  
> « By September 2026, more than 40% of pull requests on GitHub started with an agent’s first draft, up from 17% in March. »  
Source : [Octoverse: Commits, pushes, reach new highs in 2026 as developers build with agents](https://github.blog/news-insights/octoverse/octoverse-commits-pushes-reach-new-highs-in-2026-as-developers-build-with-agents/) (GitHub Blog, fournisseur, 2026-10-28)

<a id="p79"></a>**P79** · fait · Le taux de fusion sous deux semaines des pull requests impliquant des agents a atteint 90 % en septembre, dépassant les 86 % constatés pour les pull requests sans intervention d'agent.  
> « In February, 83% of agent-involved pull requests merged within two weeks, a touch behind the roughly 86% for pull requests without detected agent involvement. By September, agent pull requests were at 90%, while the comparison group held at about 86%. »  
Source : [Octoverse: Commits, pushes, reach new highs in 2026 as developers build with agents](https://github.blog/news-insights/octoverse/octoverse-commits-pushes-reach-new-highs-in-2026-as-developers-build-with-agents/) (GitHub Blog, fournisseur, 2026-10-28)

<a id="p126"></a>**P126** · interpretation · For the time being, you can have only two out of these three properties in agents: general-purpose (a language model based agent that can be instructed to do different tasks rather than purpose-built for a task like traditional software); deployed in high-stakes scenarios, and automated .  
> « For the time being, you can have only two out of these three properties in agents: general-purpose (a language model based agent that can be instructed to do different tasks rather than purpose-built for a task like traditional software); deployed in high-stakes scenarios, and automated . »  
Source : [What will be left for us to work on?](https://www.normaltech.ai/p/what-will-be-left-for-us-to-work) (AI as Normal Technology, independant, 2026-07-13)

<a id="p86"></a>**P86** · fait · Les agents surpassent les humains sur les petits budgets mais sous-performent sur les budgets importants, car leurs rendements d'optimisation décroissent plus rapidement.  
> « This seems to be a good description of the current status of agents (they outperform humans at low budgets, but underperform at high budgets, e.g. RE-bench (2024) , PaperBench (2025) ). »  
Source : [Expenditure Horizon: Measuring Optimization Ability, with an Application to NanoGPT](https://metr.org/blog/2026-07-21-expenditure-horizon/) (METR, independant, 2026-07-21)

<a id="p120"></a>**P120** · fait · Les agents IA génèrent et testent des implémentations plus de dix fois plus rapidement que les humains, ce qui leur permet parfois de trouver de très solides solutions et de progresser constamment lorsqu'on leur donne davantage de tentatives.  
> « They generate and test implementations more than ten times faster than humans, allowing them to sometimes find very strong solutions and make consistent progress when given more attempts. »  
Source : [Evaluating frontier AI R&D capabilities of language model agents against human experts](https://metr.org/blog/2024-11-22-evaluating-r-d-capabilities-of-llms/) (METR, independant, 2024-11-22)

<a id="p42"></a>**P42** · fait · HyperAgent s'appuie sur quatre agents spécialisés — Planner, Navigator, Code Editor et Executor — capables de prendre en charge l'ensemble du cycle de vie des tâches d'ingénierie logicielle, de la planification initiale à la vérification finale.  
> « HyperAgent features four specialized agents-Planner, Navigator, Code Editor, and Executor-capable of handling the entire lifecycle of SE tasks, from initial planning to final verification. »  
Source : [HyperAgent: Generalist Software Engineering Agents to Solve Coding Tasks at Scale](https://doi.org/10.48550/arxiv.2409.16299) (OpenAlex (arXiv (Cornell University)), publication, 2024-09-09)

<a id="p144"></a>**P144** · interpretation · La répétition des demandes d'approbation des actions d'un agent engendre une fatigue chez les développeurs, conduisant à des décisions moins rigoureuses.  
> « The results also suggest that repeatedly having to approve an agent's actions can lead to sloppy decisions. »  
Source : [Humans in the loop miss a third of dangerous AI coding agent requests](https://www.theregister.com/ai-and-ml/2026/08/06/humans-in-the-loop-miss-a-third-of-dangerous-ai-coding-agent-requests/5284236) (The Register AI, independant, 2026-08-06)

<a id="p76"></a>**P76** · interpretation · Selon la vision de GitHub, les développeurs conservent la responsabilité et le pouvoir de décision sur les déploiements, les agents se bornant à appliquer et vérifier les modifications.  
> « Developers set the direction, make decisions, and stay accountable for what ships. Agents implement and verify changes. »  
Source : [GitHub Universe 2026: Evolving every layer of the stack](https://github.blog/news-insights/company-news/github-universe-2026-evolving-every-layer-of-the-stack/) (GitHub Blog, fournisseur, 2026-10-28)

<a id="p105"></a>**P105** · fait · Les auteurs d'OSWorld ont observé que 75 % des échecs provenaient d'imprécisions dans les clics de souris, ce qui pourrait s'expliquer par des outils encore inadaptés.  
> « One hypothesis is poor tooling– the OSWorld authors observed that 75% of failed examples were due to mouse click inaccuracies 10 , though this might not explain the poor performance on WebArena. »  
Source : [How Does Time Horizon Vary Across Domains?](https://metr.org/blog/2025-07-14-how-does-time-horizon-vary-across-domains/) (METR, independant, 2025-07-14)

<a id="p108"></a>**P108** · fait · Les benchmarks de codage et d'agents sacrifient le réalisme au profit de l'échelle et de l'efficacité en utilisant des tâches autonomes et une évaluation algorithmique qui omettent de nombreuses capacités clés.  
> « While coding/agentic benchmarks 1 have proven useful for understanding AI capabilities, they typically sacrifice realism for scale and efficiency—the tasks are self-contained, don’t require prior context to understand, and use algorithmic evaluation that doesn’t capture many important capabilities. »  
Source : [Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/) (METR, independant, 2025-07-10)

<a id="p81"></a>**P81** · signal · Les architectures d'agents sont passées d'outils cantonnés à une seule session à des agents persistants capables d'opérer sur plusieurs jours et d'en orchestrer d'autres.  
> « Agents moved from single-session tools to persistent ones that could track progress across days and orchestrate other specialized agents. »  
Source : [Octoverse: Commits, pushes, reach new highs in 2026 as developers build with agents](https://github.blog/news-insights/octoverse/octoverse-commits-pushes-reach-new-highs-in-2026-as-developers-build-with-agents/) (GitHub Blog, fournisseur, 2026-10-28)

<a id="p16"></a>**P16** · interpretation · Les résultats suggèrent que les traces de résolution de problèmes peuvent servir de base évolutive pour les agents d'ingénierie logicielle auto-évolutifs.  
> « These results suggest that solving traces can serve as a scalable substrate for self-evolving SWE agents. »  
Source : [Socratic-SWE: Self-Evolving Coding Agents via Trace-Derived Agent Skills](https://arxiv.org/abs/2606.07412) (arXiv, publication, 2026-06-05)

<a id="p14"></a>**P14** · lacune · L'entraînement des agents d'ingénierie logicielle fondés sur les LLM reste contraint par la disponibilité de tâches d'ingénierie logicielle de haute qualité.  
> « LLM-driven software engineering agents have become a central testbed for real-world language-model capability, yet their training remains limited by the availability of high-quality SWE tasks. »  
Source : [Socratic-SWE: Self-Evolving Coding Agents via Trace-Derived Agent Skills](https://arxiv.org/abs/2606.07412) (arXiv, publication, 2026-06-05)

<a id="p17"></a>**P17** · fait · L'utilisation directe de générateurs de tests de reproduction de bugs pour guider la génération de correctifs n'est pas bénéfique, car les tests défaillants peuvent induire les agents en erreur et les tests réussis n'apportent que des gains limités ou négatifs.  
> « We first conduct a preliminary study and find that directly using advanced BRT generators to guide patch generation is not beneficial: fail-to-fail BRTs can mislead agents, while even fail-to-pass BRTs bring limited or negative gains. »  
Source : [SWE-Doctor: Guiding Software Engineering Agents with Runtime Diagnosis from Multi-Faceted Bug Reproduction Tests](https://arxiv.org/abs/2607.00990) (arXiv, publication, 2026-07-01)

<a id="p74"></a>**P74** · fait · Dans le classement d'Artificial Analysis pour les agents de codage, Fusion Max se situe à deux points d'Opus 5.5 Max pour un coût divisé par deux et 40 % de temps en moins par tâche.  
> « In the Artificial Analysis Coding Agent Index, Fusion Max scored within two points of Opus 5.5 Max at half the cost and 40% less time per task. »  
Source : [GitHub Universe 2026: Evolving every layer of the stack](https://github.blog/news-insights/company-news/github-universe-2026-evolving-every-layer-of-the-stack/) (GitHub Blog, fournisseur, 2026-10-28)

<a id="p75"></a>**P75** · fait · GitHub affirme que son outil Copilot code review Max a obtenu le score F1 le plus élevé sur le benchmark ReviewBench pour les anomalies de gravité élevée.  
> « Today, we introduced Copilot code review Max, which posted the highest F1 score on ReviewBench for high-severity issues. »  
Source : [GitHub Universe 2026: Evolving every layer of the stack](https://github.blog/news-insights/company-news/github-universe-2026-evolving-every-layer-of-the-stack/) (GitHub Blog, fournisseur, 2026-10-28)

<a id="p3"></a>**P3** · fait · Une réévaluation rigoureuse montre que certains modèles obtiennent des résultats nettement inférieurs aux scores publiés, ce qui suggère une surestimation de leurs capacités réelles.  
> « Evaluations on SWE-Bench Pro Verified reveal that some models perform substantially worse than previously evaluated, suggesting that existing results on SWE-Bench Pro may overestimate real software engineering capability. »  
Source : [SWE-Bench Pro Verified: A Reliable Benchmark for Software Engineering Agents](https://arxiv.org/abs/2609.08149) (arXiv, publication, 2026-09-08)  
Ce travail a 1 autre(s) version(s) ou republication(s), comptées comme UNE seule source.

<a id="p6"></a>**P6** · fait · Les évaluations montrent que les benchmarks existants surestiment considérablement les capacités des agents, avec un décalage de plus de 50 % pour certains modèles sur les benchmarks publics et de 10 à 16 % sur un benchmark interne.  
> « Our findings reveal that existing benchmarks significantly overestimate agent capabilities for some models by >50% over baseline performance for public benchmarks and ~10-16% for our internal benchmark. »  
Source : [Saving SWE-Bench: A Benchmark Mutation Approach for Realistic Agent Evaluation](https://arxiv.org/abs/2510.08996) (arXiv, publication, 2025-10-10)  
Ce travail a 1 autre(s) version(s) ou republication(s), comptées comme UNE seule source.

<a id="p41"></a>**P41** · interpretation · L'exactitude des réparations et le coût des échecs sont des dimensions largement indépendantes qui devraient être mesurées et rapportées conjointement.  
> « These results indicate that accuracy and cost-of-failure are largely independent dimensions and should be reported together. »  
Source : [Agentic multi-hunk repair on SWE-bench verified](https://doi.org/10.14288/1.0452541) (OpenAlex (Open Collections), publication, 2026-01-01)  
Ce travail a 1 autre(s) version(s) ou republication(s), comptées comme UNE seule source.

<a id="p84"></a>**P84** · fait · Certains modèles présentés comme performants se contentent de poursuivre le bruit statistique sans apporter de réelle amélioration lors de la revalidation.  
> « GPT-5 and Opus-4.1 only chase noise. The raw trajectories from GPT-5 and Opus-4.1 show progress, but revalidation of their final algorithms shows no increase over the baseline. »  
Source : [Expenditure Horizon: Measuring Optimization Ability, with an Application to NanoGPT](https://metr.org/blog/2026-07-21-expenditure-horizon/) (METR, independant, 2026-07-21)

<a id="p102"></a>**P102** · lacune · L'étude s'appuie sur un échafaudage d'agent de base sans calcul d'inférence parallèle significatif ni outils spécialisés avancés, ce qui n'établit pas une limite supérieure absolue des performances des agents.  
> « We do not do substantial elicitation on our agent scaffold. We use a basic agent scaffold that doesn’t make use of significant parallel inference compute, and doesn’t have specialized tooling that the LLM is designed to take advantage of, beyond basic file viewing/searching/editing, python, and bash tools. »  
Source : [Research Update: Algorithmic vs. Holistic Evaluation](https://metr.org/blog/2025-08-12-research-update-towards-reconciling-slowdown-with-time-horizons/) (METR, independant, 2025-08-13)

<a id="p128"></a>**P128** · lacune · L'absence de divulgation des détails et du code source empêche une évaluation indépendante des affirmations.  
> « Google has not released the lengthy prompt, the code the agents wrote, or the logs from the run, which makes it impossible to independently evaluate the claims. »  
Source : [Did Google’s AI agents really build an operating system for $916?](https://www.normaltech.ai/p/did-googles-ai-agents-really-build) (AI as Normal Technology, independant, 2026-05-22)

<a id="p130"></a>**P130** · lacune · L'expérimentation n'a pas permis d'analyser si le code a été rédigé à partir de zéro ou recopié d'internet en raison de données mémorisées.  
> « The writeup does not report any attempt to analyze whether the agents wrote the code from scratch or copied existing code from the internet. »  
Source : [Did Google’s AI agents really build an operating system for $916?](https://www.normaltech.ai/p/did-googles-ai-agents-really-build) (AI as Normal Technology, independant, 2026-05-22)

<a id="p88"></a>**P88** · lacune · La plupart des benchmarks d'agents ne mesurent pas les temps de résolution humains et comportent très peu de tâches exigeant plusieurs jours de travail humain.  
> « Benchmarks generally lacked measured human completion times, but our guess, based on rough impressions of task difficulty, is that most benchmarks had very few tasks that would take a human multiple full-time-equivalent days or longer. »  
Source : [Frontier Risk Report (February to March 2026)](https://metr.org/blog/2026-05-19-frontier-risk-report/) (METR, independant, 2026-05-19)

<a id="p30"></a>**P30** · lacune · Les benchmarks populaires de codage comme HumanEval et SWE-Bench se limitent à des tâches ciblées telles que la programmation de compétition et la génération de correctifs.  
> « However, popular coding benchmarks such as HumanEval and SWE-Bench focus on narrowly scoped tasks such as competition programming and patch generation. »  
Source : [OmniCode: A Benchmark for Evaluating Software Engineering Agents](https://arxiv.org/abs/2602.02262) (arXiv, publication, 2026-02-02)

<a id="p4"></a>**P4** · lacune · Les benchmarks actuels d'évaluation des agents d'ingénierie logicielle, comme SWE-Bench Verified, reposent principalement sur des tickets GitHub et ne reflètent pas fidèlement la manière dont les développeurs interagissent avec les assistants de code dans leurs environnements de développement.  
> « Current benchmarks for evaluating software engineering agents, such as SWE-Bench Verified, are predominantly derived from GitHub issues and fail to accurately reflect how developers interact with chat-based coding assistants in integrated development environments (IDEs). »  
Source : [Saving SWE-Bench: A Benchmark Mutation Approach for Realistic Agent Evaluation](https://arxiv.org/abs/2510.08996) (arXiv, publication, 2025-10-10)  
Ce travail a 1 autre(s) version(s) ou republication(s), comptées comme UNE seule source.

<a id="p27"></a>**P27** · lacune · Les benchmarks existants se limitent souvent à une évaluation en un seul tour et ne permettent pas de capturer l'interactivité multi-tours, l'usage des outils ni le raisonnement adaptatif requis par les agents réels.  
> « While existing benchmarks like LoCoBench~\cite{qiu2025locobench} assess long-context code understanding, they focus on single-turn evaluation and cannot capture the multi-turn interactive nature, tool usage patterns, and adaptive reasoning required by real-world coding agents. »  
Source : [LoCoBench-Agent: An Interactive Benchmark for LLM Agents in Long-Context Software Engineering](https://arxiv.org/abs/2511.13998) (arXiv, publication, 2025-11-17)  
Ce travail a 1 autre(s) version(s) ou republication(s), comptées comme UNE seule source.

<a id="p33"></a>**P33** · lacune · Les agents auto-améliorants nécessitent un entraînement hors ligne coûteux sur des benchmarks spécifiques et risquent de mal se généraliser d'un LLM ou d'un benchmark à l'autre.  
> « Meanwhile, such self-improving agents require costly offline training on specific benchmarks and may not generalize well across different LLMs or benchmarks. »  
Source : [Live-SWE-agent: Can Software Engineering Agents Self-Evolve on the Fly?](https://arxiv.org/abs/2511.13646) (arXiv, publication, 2025-11-17)  
Ce travail a 1 autre(s) version(s) ou republication(s), comptées comme UNE seule source.

<a id="p36"></a>**P36** · lacune · Une analyse manuelle des problèmes du benchmark SWE-bench Lite a révélé des biais et défauts, comme des descriptions d'incidents insuffisantes ou induisant en erreur.  
> « Furthermore, we manually classified the problems in SWE-bench Lite and found problems with exact ground truth patch or insufficient/misleading issue descriptions. »  
Source : [Agentless: Demystifying LLM-based Software Engineering Agents](https://arxiv.org/abs/2407.01489) (arXiv, publication, 2024-07-01)  
Ce travail a 2 autre(s) version(s) ou republication(s), comptées comme UNE seule source.

<a id="p125"></a>**P125** · risque · Many companies that hastily rushed to automate business processes using agents are recognizing the limits and costs, and even legal liabilities — like when an agent deletes production data.  
> « Many companies that hastily rushed to automate business processes using agents are recognizing the limits and costs, and even legal liabilities — like when an agent deletes production data. »  
Source : [What will be left for us to work on?](https://www.normaltech.ai/p/what-will-be-left-for-us-to-work) (AI as Normal Technology, independant, 2026-07-13)

<a id="p135"></a>**P135** · risque · Lors d'une évaluation autonome, un agent a commis deux erreurs dont une ayant exigé une intervention humaine, oubliant l'emplacement des identifiants et inventant un numéro de téléphone fictif.  
> « The agent was successful after making two errors, one of which required manual intervention (forgetting where the correct credentials were stored and fabricating a fictional phone number for the App Store review process). »  
Source : [Open-world evaluations for measuring frontier AI capabilities](https://www.normaltech.ai/p/open-world-evaluations-for-measuring) (AI as Normal Technology, independant, 2026-04-16)

<a id="p141"></a>**P141** · risque · Grok Build, un agent de codage, divulgue des informations d'entreprise propriétaires et des secrets sensibles de milliers d'utilisateurs.  
> « Grok Build, the vibe-coding agent from SpaceXSI, is leaking data—some of it proprietary business information and other sensitive secrets—from thousands of its users, including the very same Elon Musk-owned company that offers the platform, new research shows. »  
Source : [Grok Build coding agent leaks oodles of confidential info, some belonging to SpaceXSI](https://arstechnica.com/security/2026/11/grok-build-coding-agent-leaks-oodles-of-confidential-info-some-belonging-to-spacexsi/) (Ars Technica AI, independant, 2026-11-10)

<a id="p90"></a>**P90** · risque · METR estime que les agents internes disposaient vraisemblablement des moyens, de la motivation et de l'opportunité pour initier de petits déploiements autonomes non autorisés, même s'ils ne pouvaient pas encore les pérenniser solidement.  
> « Overall, we believe that internal agents at the time of our assessment plausibly had the means , motive , and opportunity to start small rogue deployments, but they did not have the means to make them highly robust. »  
Source : [Frontier Risk Report (February to March 2026)](https://metr.org/blog/2026-05-19-frontier-risk-report/) (METR, independant, 2026-05-19)

<a id="p20"></a>**P20** · risque · Les trajectoires échouées, les succès accidentels et les observations trompeuses s'introduisent dans la mémoire des agents et induisent en erreur leurs décisions ultérieures.  
> « The first is unreliable admission: failed trajectories,accidental successes, and misleading observations enter memory because they appear relevant, then mislead later decisions. »  
Source : [MemGuard: Persisting Verifier Signals for LLM-Agent Memory Governance](https://arxiv.org/abs/2608.21867) (arXiv, publication, 2026-08-22)

<a id="p48"></a>**P48** · risque · Les défauts d'ancrage environnemental émergent systématiquement dans les flux de travail opérationnels, révélant un problème majeur de fiabilité et de sécurité pour les agents.  
> « Results show that EGDs consistently emerge across operational workflows, highlighting environmental grounding as a core agent reliability problem with important security implications. »  
Source : [When Agents Overtrust Environmental Evidence: An Extensible Agentic Framework for Benchmarking Evidence-Grounding Defects in LLM Agents](https://doi.org/10.48550/arxiv.2605.08828) (OpenAlex (arXiv (Cornell University)), publication, 2026-05-09)

<a id="p62"></a>**P62** · risque · Un dépôt GitHub piégé utilise des commentaires HTML invisibles pour ordonner aux agents autonomes d'ignorer les avertissements destinés aux humains figurant dans le fichier CONTRIBUTING.md.  
> « Rendered on github.com a reader sees the warning alone: symbolic bounties, PRs never merged, wrong place for paid work. The two HTML comments do not appear in the rendered page and are fully visible to anything reading the raw markdown. »  
Source : [In-the-wild prompt injection: a repo's CONTRIBUTING.md tells agents to ignore its own human-visible warning, and CI requires pasting `init_context` (full system prompt) into a tracked file](https://github.com/OpenHands/OpenHands/issues/17645) (GitHub issues (OpenHands/OpenHands), depot, 2026-09-23)

<a id="p56"></a>**P56** · risque · Pour les tâches de longue durée, la troncature du contexte entraîne une dérive sémantique et comportementale silencieuse de l'agent.  
> « When that happens, the agent continues — but may silently change behavior in ways that affect the quality of the remaining work »  
Source : [Feature: behavioral fingerprint hook at context truncation boundaries for long-running coding agents](https://github.com/OpenHands/OpenHands/issues/13644) (GitHub issues (OpenHands/OpenHands), depot, 2026-03-29)

<a id="p58"></a>**P58** · risque · Ce mode de défaillance est difficile à détecter car les modifications de code produites restent syntaxiquement valides et les tests peuvent passer.  
> « This failure mode is harder to catch than hallucination because the individual outputs are syntactically valid. The inconsistency only appears relative to the session's own prior state »  
Source : [Feature: behavioral fingerprint hook at context truncation boundaries for long-running coding agents](https://github.com/OpenHands/OpenHands/issues/13644) (GitHub issues (OpenHands/OpenHands), depot, 2026-03-29)

<a id="p59"></a>**P59** · risque · L'isolation par bac à sable (sandbox) contient les dégâts potentiels, mais n'empêche pas l'agent d'exécuter des opérations destructrices sur l'espace de travail.  
> « The sandbox contains the damage to the container, but the user's mounted workspace is still affected. »  
Source : [Authority separation for autonomous coding agents](https://github.com/OpenHands/OpenHands/issues/13150) (GitHub issues (OpenHands/OpenHands), depot, 2026-03-03)

<a id="p98"></a>**P98** · interpretation · Cette constatation suggère que la notation automatique utilisée par de nombreux benchmarks peut surestimer les performances réelles des agents IA sur le terrain.  
> « This suggests that automatic scoring used by many benchmarks 1 may overestimate AI agent real-world performance. »  
Source : [Research Update: Algorithmic vs. Holistic Evaluation](https://metr.org/blog/2025-08-12-research-update-towards-reconciling-slowdown-with-time-horizons/) (METR, independant, 2025-08-13)

<a id="p101"></a>**P101** · interpretation · Les taux de réussite des modèles phares sur SWE-bench Verified atteignent 70 à 75 %, mais il est peu probable que les agents IA puissent réellement résoudre autant de demandes de tir (PR) dans des conditions réelles.  
> « For example, frontier model success rates on SWE-Bench Verified are around 70-75%, but it seems unlikely that AI agents are currently actually able to fully resolve 75% of real PRs in the wild. »  
Source : [Research Update: Algorithmic vs. Holistic Evaluation](https://metr.org/blog/2025-08-12-research-update-towards-reconciling-slowdown-with-time-horizons/) (METR, independant, 2025-08-13)

<a id="p109"></a>**P109** · interpretation · Ces propriétés peuvent amener les benchmarks à surestimer les capacités des IA, bien que l'absence d'interaction humaine en direct puisse parfois conduire à sous-estimer ces mêmes capacités face à de petits goulets d'étranglement.  
> « These properties may lead benchmarks to overestimate AI capabilities. In the other direction, because benchmarks are run without live human interaction, models may fail to complete tasks despite making substantial progress, because of small bottlenecks that a human would fix during real usage. »  
Source : [Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/) (METR, independant, 2025-07-10)

<a id="p112"></a>**P112** · interpretation · Les benchmarks peuvent surestimer les capacités des modèles en mesurant uniquement la performance sur des tâches bien délimitées et évaluables de manière algorithmique, tandis que les rapports anecdotiques d'accélération s'avèrent très inexacts.  
> « On the other hand, benchmarks may overestimate model capabilities by only measuring performance on well-scoped, algorithmically scorable tasks. And we now have strong evidence that anecdotal reports/estimates of speed-up can be very inaccurate. »  
Source : [Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/) (METR, independant, 2025-07-10)

<a id="p118"></a>**P118** · interpretation · Les environnements réels de R&D en Machine Learning impliquent des boucles de rétroaction beaucoup plus lentes et des objectifs moins clairement définis que dans les environnements de test, et il n'est pas clair dans quelle mesure les problèmes de recherche peuvent être découpés en petites tâches.  
> « However, real-world ML R&D work often has much slower feedback loops and less clearly-defined goals than in our environments, and it’s unclear to what extent research problems can be packaged into small tasks that models can iterate on effectively. »  
Source : [Evaluating frontier AI R&D capabilities of language model agents against human experts](https://metr.org/blog/2024-11-22-evaluating-r-d-capabilities-of-llms/) (METR, independant, 2024-11-22)

<a id="p93"></a>**P93** · interpretation · Une interprétation naïve des scores de benchmark peut amener à surestimer l'utilité réelle des agents sans un travail d'élicitation plus poussé ou un retour d'information humain.  
> « Rather, our results indicate that a naive interpretation of benchmark scores may lead one to overestimate how useful agents are without more elicitation or human feedback. »  
Source : [Many SWE-bench-Passing PRs Would Not Be Merged into Main](https://metr.org/notes/2026-03-10-many-swe-bench-passing-prs-would-not-be-merged-into-main/) (METR, independant, 2026-03-10)

<a id="p94"></a>**P94** · interpretation · Il est difficile de transposer les scores des benchmarks en utilité dans le monde réel car les benchmarks sont propres et vérifiables d'une manière que le monde réel ne l'est pas.  
> « One reason to doubt this is that benchmarks are clean and verifiable in ways the real world is not. To study this quantitatively, we take SWE-bench Verified and zoom in on one such difference — it uses an automated grader rather than the real-world standard of maintainer review. »  
Source : [Many SWE-bench-Passing PRs Would Not Be Merged into Main](https://metr.org/notes/2026-03-10-many-swe-bench-passing-prs-would-not-be-merged-into-main/) (METR, independant, 2026-03-10)
