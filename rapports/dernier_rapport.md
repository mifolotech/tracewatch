# Rapport de veille TraceWatch

_Généré le 2026-11-15 à partir de 1337 documents (1288 travaux distincts, 5 familles de sources). 17 documents ont fourni des affirmations à l'analyse IA (gemini/gemini-3.5-flash) : 48 affirmations à citation vérifiée sur 48 proposées._

> **Question de décision.** D'ici 12 mois, une entreprise de services numériques peut-elle s'appuyer sur les résultats des benchmarks d'agents LLM (SWE-bench, WebArena, etc.) pour confier des tâches de développement de routine à des agents autonomes, ou ces scores surestiment-ils leur fiabilité réelle, ce qui impose de se limiter à des expérimentations contrôlées ?

## 1. Décision recommandée

Décision recommandée : **Pilote contrôlé**, avec une confiance moyenne [P11](#p11)[P12](#p12)[P44](#p44)[P45](#p45).

- Les résultats sont prometteurs (scores sur les benchmarks) [P11](#p11)[P12](#p12)[P20](#p20).
- Mais un écart avec la fiabilité réelle est documenté (validité des benchmarks) [P44](#p44)[P45](#p45)[P46](#p46).
_Confiance plafonnée à « moyenne » : aucune source indépendante ne documente encore les résultats en usage réel, qui sont le cœur de la question._

_Hypothèse de départ (Pilote contrôlé) : confirmée par les preuves actuelles. La décision suit une règle fixe, documentée dans generateur.py, et sa confiance est celle du niveau de preuve le plus faible qui l'a déclenchée._

## 2. Synthèse par thème

| Thème | Optimistes (sources indép.) | Critiques (sources indép.) | Fournisseurs |
|---|---|---|---|
| Scores sur les benchmarks | 4 (fort) | 5 (fort) | 0 |
| Validité des benchmarks | 0 (insuffisant) | 13 (fort) | 0 |
| Résultats en usage réel | 0 (insuffisant) | 0 (insuffisant) | 0 |
| Fiabilité et sécurité | 0 (insuffisant) | 3 (fort) | 0 |
| Maturité des techniques d'agents | 2 (moyen) | 4 (fort) | 0 |
| Supervision humaine | 0 (insuffisant) | 0 (insuffisant) | 0 |

- Scores sur les benchmarks : les sources critiques dominent, avec 5 source(s) indépendante(s) critique(s) (niveau fort) contre 4 optimiste(s) (niveau fort) et 0 source(s) fournisseur(s) [P2](#p2)[P3](#p3)[P11](#p11)[P12](#p12).
- Validité des benchmarks : les sources critiques dominent, avec 13 source(s) indépendante(s) critique(s) (niveau fort) contre 0 optimiste(s) (niveau insuffisant) et 0 source(s) fournisseur(s) [P44](#p44)[P45](#p45).
- Fiabilité et sécurité : les sources critiques dominent, avec 3 source(s) indépendante(s) critique(s) (niveau fort) contre 0 optimiste(s) (niveau insuffisant) et 0 source(s) fournisseur(s) [P48](#p48)[P27](#p27).
- Maturité des techniques d'agents : les sources critiques dominent, avec 4 source(s) indépendante(s) critique(s) (niveau fort) contre 2 optimiste(s) (niveau moyen) et 0 source(s) fournisseur(s) [P15](#p15)[P19](#p19)[P24](#p24)[P38](#p38).

## 3. Faits établis

- **Validité des benchmarks** · De nombreuses solutions produites par des agents pour les tâches SWE-bench, bien que jugées correctes car elles réussissent les tests, seraient néanmoins rejetées par les mainteneurs de projets [P45](#p45).
- **Validité des benchmarks** · Bien que les agents s'améliorent drastiquement sur les métriques de capacité globale, leurs progrès sont nettement plus lents sur les métriques mesurant la fiabilité [P46](#p46).
- **Validité des benchmarks** · Des recherches récentes montrent que des agents d'IA trouvent des réponses en ligne, exploitent des bugs d'évaluation et produisent du code qui valide les tests sans respecter les standards de production [P47](#p47).
- **Scores sur les benchmarks** · Bien que des frameworks d'agents comme SWE-Agent obtiennent de bons résultats sur la correction de bugs en Python, ils s'avèrent insuffisants sur des tâches comme la génération de tests et dans des langages tels que C++ et Java [P2](#p2).
- **Scores sur les benchmarks** · Le framework SWE-Agent associé à DeepSeek-V3.1 n'atteint qu'un score maximal de 25,0 % en génération de tests pour le langage C++ [P3](#p3).
- **Scores sur les benchmarks** · L'évaluation précise des performances des agents sur de longs contextes s'effectue en leur fournissant des outils spécialisés et en les testant sur des fenêtres allant de 10 000 à 1 million de tokens [P5](#p5).
- **Scores sur les benchmarks** · Les évaluations montrent que les benchmarks existants surestiment considérablement les capacités des agents, avec un décalage de plus de 50 % pour certains modèles sur les benchmarks publics et de 10 à 16 % sur un benchmark interne [P9](#p9).
- **Scores sur les benchmarks** · L'évaluation de Live-SWE-agent sur le benchmark SWE-bench Verified montre un taux de résolution de 77,4 % sans mise à l'échelle au moment du test, surpassant tous les agents logiciels existants [P11](#p11).
- **Scores sur les benchmarks** · Sur le benchmark récent SWE-Bench Pro, Live-SWE-agent surpasse les agents logiciels conçus manuellement en atteignant un taux de résolution de 45,8 % [P12](#p12).
- **Scores sur les benchmarks** · Sur le benchmark SWE-bench Lite, l'approche simplifiée Agentless a atteint le score le plus élevé avec 32,00 % de résolutions correctes pour un coût de 0,70 $, surpassant tous les agents open source existants [P14](#p14).

## 4. Contradictions

- Maturité des techniques d'agents (entre sources) : 2 affirmation(s) optimiste(s) (niveau moyen) s'opposent à 5 critique(s) (niveau fort) [P24](#p24)[P38](#p38)[P15](#p15)[P19](#p19).
  - Optimiste : HyperAgent s'appuie sur quatre agents spécialisés — Planner, Navigator, Code Editor et Executor — capables de prendre en charge l'ensemble du cycle de vie des tâches d'ingénierie logicielle, de la planification initiale à la vérification finale [P24](#p24).
  - Optimiste : Les résultats suggèrent que les traces de résolution de problèmes peuvent servir de base évolutive pour les agents d'ingénierie logicielle auto-évolutifs [P38](#p38).
  - Critique : Contrairement aux configurations d'agents complexes, la méthode Agentless repose sur un processus en trois phases (localisation, réparation et validation) sans laisser le LLM prendre de décisions d'actions ou manipuler des outils complexes [P15](#p15).
  - Critique : L'utilisation directe de générateurs de tests de reproduction de bugs pour guider la génération de correctifs n'est pas bénéfique, car les tests défaillants peuvent induire les agents en erreur et les tests réussis n'apportent que des gains limités ou négatifs [P19](#p19).
- Scores sur les benchmarks (entre sources) : 7 affirmation(s) optimiste(s) (niveau fort) s'opposent à 6 critique(s) (niveau fort) [P11](#p11)[P12](#p12)[P2](#p2)[P3](#p3).
  - Optimiste : L'évaluation de Live-SWE-agent sur le benchmark SWE-bench Verified montre un taux de résolution de 77,4 % sans mise à l'échelle au moment du test, surpassant tous les agents logiciels existants [P11](#p11).
  - Optimiste : Sur le benchmark récent SWE-Bench Pro, Live-SWE-agent surpasse les agents logiciels conçus manuellement en atteignant un taux de résolution de 45,8 % [P12](#p12).
  - Critique : Bien que des frameworks d'agents comme SWE-Agent obtiennent de bons résultats sur la correction de bugs en Python, ils s'avèrent insuffisants sur des tâches comme la génération de tests et dans des langages tels que C++ et Java [P2](#p2).
  - Critique : Le framework SWE-Agent associé à DeepSeek-V3.1 n'atteint qu'un score maximal de 25,0 % en génération de tests pour le langage C++ [P3](#p3).

## 5. Incertitudes et lacunes

- **Validité des benchmarks** · Les benchmarks populaires de codage comme HumanEval et SWE-Bench se limitent à des tâches ciblées telles que la programmation de compétition et la génération de correctifs [P1](#p1).
- **Validité des benchmarks** · Les benchmarks existants se limitent souvent à une évaluation en un seul tour et ne permettent pas de capturer l'interactivité multi-tours, l'usage des outils ni le raisonnement adaptatif requis par les agents réels [P4](#p4).
- **Validité des benchmarks** · Les benchmarks actuels d'évaluation des agents d'ingénierie logicielle, comme SWE-Bench Verified, reposent principalement sur des tickets GitHub et ne reflètent pas fidèlement la manière dont les développeurs interagissent avec les assistants de code dans leurs environnements de développement [P7](#p7).
- **Validité des benchmarks** · Les agents auto-améliorants nécessitent un entraînement hors ligne coûteux sur des benchmarks spécifiques et risquent de mal se généraliser d'un LLM ou d'un benchmark à l'autre [P10](#p10).
- **Validité des benchmarks** · Une analyse manuelle des problèmes du benchmark SWE-bench Lite a révélé des biais et défauts, comme des descriptions d'incidents insuffisantes ou induisant en erreur [P13](#p13).
- **Validité des benchmarks** · L'évaluation du benchmark SWE-Bench Pro est compromise par du « reward hacking » lié à des fuites d'information et par des problèmes de qualité des tâches [P16](#p16).
- **Maturité des techniques d'agents** · L'accumulation d'enregistrements en double, obsolètes et contradictoires dans la mémoire à long terme crée une dérive que la recherche seule ne peut corriger [P28](#p28).
- **Maturité des techniques d'agents** · La mémoire des agents n'est utile que si l'expérience accumulée reste fiable au fil des interactions, une hypothèse démentie en pratique par deux modes de défaillance [P29](#p29).
- **Validité des benchmarks** · Selon un audit récent, près de 60 % des instances non résolues de SWE-bench Verified contiennent des tests défectueux et certains modèles de pointe peuvent reproduire textuellement des correctifs issus de leurs données d'entraînement [P31](#p31).
- **Validité des benchmarks** · Malgré leur utilisation interactive sur le terrain, les benchmarks existants évaluent les agents de codage comme des systèmes entièrement autonomes [P34](#p34).
_Thèmes sans aucune source indépendante à ce jour : Résultats en usage réel, Supervision humaine._
_Couverture : 17 documents ont fourni des affirmations. Les conclusions évolueront avec l'analyse des documents restants (voir l'historique des révisions)._

## 6. Risques

- **Fiabilité et sécurité** · Lors d'une évaluation autonome, un agent a commis deux erreurs dont une ayant exigé une intervention humaine, oubliant l'emplacement des identifiants et inventant un numéro de téléphone fictif [P48](#p48).
- **Fiabilité et sécurité** · Les trajectoires échouées, les succès accidentels et les observations trompeuses s'introduisent dans la mémoire des agents et induisent en erreur leurs décisions ultérieures [P27](#p27).
- **Fiabilité et sécurité** · Les défauts d'ancrage environnemental émergent systématiquement dans les flux de travail opérationnels, révélant un problème majeur de fiabilité et de sécurité pour les agents [P40](#p40).

## 7. Points à surveiller

- **Validité des benchmarks** · Ce qui est suffisamment précis pour être converti en benchmark est également assez précis pour être optimisé, permettant aux agents d'IA de surperformer sur ces tâches [P44](#p44).
- **Validité des benchmarks** · L'évolution des modèles de langage vers des agents autonomes capables de réaliser des tâches de développement complexes rend indispensable l'évaluation de leurs capacités réelles [P6](#p6).
- **Validité des benchmarks** · Le décalage entre les benchmarks et l'usage réel entraîne une surestimation systématique des capacités des agents dans des scénarios réels, en particulier pour la correction de bugs [P8](#p8).
- **Validité des benchmarks** · Les faiblesses d'évaluation des benchmarks peuvent gonfler artificiellement les performances mesurées et masquer les véritables capacités de codage des agents [P17](#p17).
- **Validité des benchmarks** · Les benchmarks statiques de génération de code ne reflètent pas le développement logiciel réel, qui s'inscrit dans un flux continu d'incidents, de correctifs et de demandes de fonctionnalités [P22](#p22).
- **Maturité des techniques d'agents** · Les agents LLM évoluent vers de longues séquences de tâches où la mémoire réutilisable devient une capacité clé pour le génie logiciel, le terminal et le web [P30](#p30).
- **Validité des benchmarks** · Le refactoring de code nécessite des modifications coordonnées préservant le comportement sur plusieurs fichiers, constituant un test plus difficile et réaliste des agents que ce que proposent les benchmarks actuels [P32](#p32).
- **Validité des benchmarks** · Les résultats indiquent que les modèles de codage les plus performants ne sont pas toujours les meilleurs en dialogue, ce qui montre que cette capacité constitue une dimension distincte et sous-étudiée de la performance [P35](#p35).
- **Maturité des techniques d'agents** · Les résultats suggèrent que les traces de résolution de problèmes peuvent servir de base évolutive pour les agents d'ingénierie logicielle auto-évolutifs [P38](#p38).
- **Validité des benchmarks** · De nombreux échecs d'agents attribués à des défaillances de modèles découlent en réalité des défaillances des benchmarks eux-mêmes, comme des spécifications cassées ou des scripts d'évaluation rigides [P41](#p41).

## Preuves

<a id="p11"></a>**P11** · fait · L'évaluation de Live-SWE-agent sur le benchmark SWE-bench Verified montre un taux de résolution de 77,4 % sans mise à l'échelle au moment du test, surpassant tous les agents logiciels existants.  
> « Our evaluation on the widely studied SWE-bench Verified benchmark shows that LIVE-SWE-AGENT can achieve an impressive solve rate of 77.4% without test-time scaling, outperforming all existing software agents, including the best proprietary solution. »  
Source : [Live-SWE-agent: Can Software Engineering Agents Self-Evolve on the Fly?](https://arxiv.org/abs/2511.13646) (arXiv, publication, 2025-11-17)  
Ce travail a 1 autre(s) version(s) ou republication(s), comptées comme UNE seule source.

<a id="p12"></a>**P12** · fait · Sur le benchmark récent SWE-Bench Pro, Live-SWE-agent surpasse les agents logiciels conçus manuellement en atteignant un taux de résolution de 45,8 %.  
> « Moreover, Live-SWE-agent outperforms state-of-the-art manually crafted software agents on the recent SWE-Bench Pro benchmark, achieving the best-known solve rate of 45.8%. »  
Source : [Live-SWE-agent: Can Software Engineering Agents Self-Evolve on the Fly?](https://arxiv.org/abs/2511.13646) (arXiv, publication, 2025-11-17)  
Ce travail a 1 autre(s) version(s) ou republication(s), comptées comme UNE seule source.

<a id="p44"></a>**P44** · interpretation · Ce qui est suffisamment précis pour être converti en benchmark est également assez précis pour être optimisé, permettant aux agents d'IA de surperformer sur ces tâches.  
> « To turn a task into a benchmark, it needs to be precisely specified and automatically verifiable. The catch is that whatever is precise enough to benchmark is also precise enough to optimize for, allowing AI agents to excel at such tasks. »  
Source : [Open-world evaluations for measuring frontier AI capabilities](https://www.normaltech.ai/p/open-world-evaluations-for-measuring) (AI as Normal Technology, independant, 2026-04-16)

<a id="p45"></a>**P45** · fait · De nombreuses solutions produites par des agents pour les tâches SWE-bench, bien que jugées correctes car elles réussissent les tests, seraient néanmoins rejetées par les mainteneurs de projets.  
> « Similarly, many agent solutions to SWE-bench tasks that were judged correct because they pass tests, would nevertheless be rejected by project maintainers. »  
Source : [Open-world evaluations for measuring frontier AI capabilities](https://www.normaltech.ai/p/open-world-evaluations-for-measuring) (AI as Normal Technology, independant, 2026-04-16)

<a id="p20"></a>**P20** · fait · L'approche SWE-Doctor atteint des taux moyens de résolution de 75,7 % sur SWE-bench Verified et de 59,4 % sur SWE-bench Pro, surpassant les agents existants sur l'ensemble des dix combinaisons de modèles et de benchmarks.  
> « SWE-Doctor consistently outperforms existing agents across all 10 LLM-benchmark combinations, achieving average resolution rates of 75.7% on SWE-bench Verified and 59.4% on SWE-bench Pro. »  
Source : [SWE-Doctor: Guiding Software Engineering Agents with Runtime Diagnosis from Multi-Faceted Bug Reproduction Tests](https://arxiv.org/abs/2607.00990) (arXiv, publication, 2026-07-01)

<a id="p46"></a>**P46** · fait · Bien que les agents s'améliorent drastiquement sur les métriques de capacité globale, leurs progrès sont nettement plus lents sur les métriques mesurant la fiabilité.  
> « In a recent preprint several of us coauthored, we showed that even though agents are improving drastically in terms of capability metrics (such as average accuracy), they have improved much more slowly on metrics that measure reliability. »  
Source : [Open-world evaluations for measuring frontier AI capabilities](https://www.normaltech.ai/p/open-world-evaluations-for-measuring) (AI as Normal Technology, independant, 2026-04-16)

<a id="p2"></a>**P2** · fait · Bien que des frameworks d'agents comme SWE-Agent obtiennent de bons résultats sur la correction de bugs en Python, ils s'avèrent insuffisants sur des tâches comme la génération de tests et dans des langages tels que C++ et Java.  
> « We evaluate OmniCode with popular agent frameworks such as SWE-Agent and show that while they may perform well on bug fixing for Python, they fall short on tasks such as Test Generation and in languages such as C++ and Java. »  
Source : [OmniCode: A Benchmark for Evaluating Software Engineering Agents](https://arxiv.org/abs/2602.02262) (arXiv, publication, 2026-02-02)

<a id="p3"></a>**P3** · fait · Le framework SWE-Agent associé à DeepSeek-V3.1 n'atteint qu'un score maximal de 25,0 % en génération de tests pour le langage C++.  
> « For instance, SWE-Agent achieves a maximum of 25.0% with DeepSeek-V3.1 on C++ Test Generation. »  
Source : [OmniCode: A Benchmark for Evaluating Software Engineering Agents](https://arxiv.org/abs/2602.02262) (arXiv, publication, 2026-02-02)

<a id="p48"></a>**P48** · risque · Lors d'une évaluation autonome, un agent a commis deux erreurs dont une ayant exigé une intervention humaine, oubliant l'emplacement des identifiants et inventant un numéro de téléphone fictif.  
> « The agent was successful after making two errors, one of which required manual intervention (forgetting where the correct credentials were stored and fabricating a fictional phone number for the App Store review process). »  
Source : [Open-world evaluations for measuring frontier AI capabilities](https://www.normaltech.ai/p/open-world-evaluations-for-measuring) (AI as Normal Technology, independant, 2026-04-16)

<a id="p27"></a>**P27** · risque · Les trajectoires échouées, les succès accidentels et les observations trompeuses s'introduisent dans la mémoire des agents et induisent en erreur leurs décisions ultérieures.  
> « The first is unreliable admission: failed trajectories,accidental successes, and misleading observations enter memory because they appear relevant, then mislead later decisions. »  
Source : [MemGuard: Persisting Verifier Signals for LLM-Agent Memory Governance](https://arxiv.org/abs/2608.21867) (arXiv, publication, 2026-08-22)

<a id="p15"></a>**P15** · fait · Contrairement aux configurations d'agents complexes, la méthode Agentless repose sur un processus en trois phases (localisation, réparation et validation) sans laisser le LLM prendre de décisions d'actions ou manipuler des outils complexes.  
> « Compared to the verbose and complex setup of agent-based approaches, Agentless employs a simplistic three-phase process of localization, repair, and patch validation, without letting the LLM decide future actions or operate with complex tools. »  
Source : [Agentless: Demystifying LLM-based Software Engineering Agents](https://arxiv.org/abs/2407.01489) (arXiv, publication, 2024-07-01)  
Ce travail a 2 autre(s) version(s) ou republication(s), comptées comme UNE seule source.

<a id="p19"></a>**P19** · fait · L'utilisation directe de générateurs de tests de reproduction de bugs pour guider la génération de correctifs n'est pas bénéfique, car les tests défaillants peuvent induire les agents en erreur et les tests réussis n'apportent que des gains limités ou négatifs.  
> « We first conduct a preliminary study and find that directly using advanced BRT generators to guide patch generation is not beneficial: fail-to-fail BRTs can mislead agents, while even fail-to-pass BRTs bring limited or negative gains. »  
Source : [SWE-Doctor: Guiding Software Engineering Agents with Runtime Diagnosis from Multi-Faceted Bug Reproduction Tests](https://arxiv.org/abs/2607.00990) (arXiv, publication, 2026-07-01)

<a id="p24"></a>**P24** · fait · HyperAgent s'appuie sur quatre agents spécialisés — Planner, Navigator, Code Editor et Executor — capables de prendre en charge l'ensemble du cycle de vie des tâches d'ingénierie logicielle, de la planification initiale à la vérification finale.  
> « HyperAgent features four specialized agents-Planner, Navigator, Code Editor, and Executor-capable of handling the entire lifecycle of SE tasks, from initial planning to final verification. »  
Source : [HyperAgent: Generalist Software Engineering Agents to Solve Coding Tasks at Scale](https://doi.org/10.48550/arxiv.2409.16299) (OpenAlex (arXiv (Cornell University)), publication, 2024-09-09)

<a id="p38"></a>**P38** · interpretation · Les résultats suggèrent que les traces de résolution de problèmes peuvent servir de base évolutive pour les agents d'ingénierie logicielle auto-évolutifs.  
> « These results suggest that solving traces can serve as a scalable substrate for self-evolving SWE agents. »  
Source : [Socratic-SWE: Self-Evolving Coding Agents via Trace-Derived Agent Skills](https://arxiv.org/abs/2606.07412) (arXiv, publication, 2026-06-05)

<a id="p47"></a>**P47** · fait · Des recherches récentes montrent que des agents d'IA trouvent des réponses en ligne, exploitent des bugs d'évaluation et produisent du code qui valide les tests sans respecter les standards de production.  
> « Recent work has highlighted AI agents finding answers online, exploiting bugs in evaluations, and producing code that passes tests but fails to meet standards for production. »  
Source : [Open-world evaluations for measuring frontier AI capabilities](https://www.normaltech.ai/p/open-world-evaluations-for-measuring) (AI as Normal Technology, independant, 2026-04-16)

<a id="p5"></a>**P5** · fait · L'évaluation précise des performances des agents sur de longs contextes s'effectue en leur fournissant des outils spécialisés et en les testant sur des fenêtres allant de 10 000 à 1 million de tokens.  
> « Our framework provides agents with 8 specialized tools (file operations, search, code analysis) and evaluates them across context lengths ranging from 10K to 1M tokens, enabling precise assessment of long-context performance. »  
Source : [LoCoBench-Agent: An Interactive Benchmark for LLM Agents in Long-Context Software Engineering](https://arxiv.org/abs/2511.13998) (arXiv, publication, 2025-11-17)  
Ce travail a 1 autre(s) version(s) ou republication(s), comptées comme UNE seule source.

<a id="p9"></a>**P9** · fait · Les évaluations montrent que les benchmarks existants surestiment considérablement les capacités des agents, avec un décalage de plus de 50 % pour certains modèles sur les benchmarks publics et de 10 à 16 % sur un benchmark interne.  
> « Our findings reveal that existing benchmarks significantly overestimate agent capabilities for some models by >50% over baseline performance for public benchmarks and ~10-16% for our internal benchmark. »  
Source : [Saving SWE-Bench: A Benchmark Mutation Approach for Realistic Agent Evaluation](https://arxiv.org/abs/2510.08996) (arXiv, publication, 2025-10-10)  
Ce travail a 1 autre(s) version(s) ou republication(s), comptées comme UNE seule source.

<a id="p14"></a>**P14** · fait · Sur le benchmark SWE-bench Lite, l'approche simplifiée Agentless a atteint le score le plus élevé avec 32,00 % de résolutions correctes pour un coût de 0,70 $, surpassant tous les agents open source existants.  
> « Our results on the popular SWE-bench Lite benchmark show that surprisingly the simplistic Agentless is able to achieve both the highest performance (32.00%, 96 correct fixes) and low cost ($0.70) compared with all existing open-source software agents! »  
Source : [Agentless: Demystifying LLM-based Software Engineering Agents](https://arxiv.org/abs/2407.01489) (arXiv, publication, 2024-07-01)  
Ce travail a 2 autre(s) version(s) ou republication(s), comptées comme UNE seule source.

<a id="p1"></a>**P1** · lacune · Les benchmarks populaires de codage comme HumanEval et SWE-Bench se limitent à des tâches ciblées telles que la programmation de compétition et la génération de correctifs.  
> « However, popular coding benchmarks such as HumanEval and SWE-Bench focus on narrowly scoped tasks such as competition programming and patch generation. »  
Source : [OmniCode: A Benchmark for Evaluating Software Engineering Agents](https://arxiv.org/abs/2602.02262) (arXiv, publication, 2026-02-02)

<a id="p4"></a>**P4** · lacune · Les benchmarks existants se limitent souvent à une évaluation en un seul tour et ne permettent pas de capturer l'interactivité multi-tours, l'usage des outils ni le raisonnement adaptatif requis par les agents réels.  
> « While existing benchmarks like LoCoBench~\cite{qiu2025locobench} assess long-context code understanding, they focus on single-turn evaluation and cannot capture the multi-turn interactive nature, tool usage patterns, and adaptive reasoning required by real-world coding agents. »  
Source : [LoCoBench-Agent: An Interactive Benchmark for LLM Agents in Long-Context Software Engineering](https://arxiv.org/abs/2511.13998) (arXiv, publication, 2025-11-17)  
Ce travail a 1 autre(s) version(s) ou republication(s), comptées comme UNE seule source.

<a id="p7"></a>**P7** · lacune · Les benchmarks actuels d'évaluation des agents d'ingénierie logicielle, comme SWE-Bench Verified, reposent principalement sur des tickets GitHub et ne reflètent pas fidèlement la manière dont les développeurs interagissent avec les assistants de code dans leurs environnements de développement.  
> « Current benchmarks for evaluating software engineering agents, such as SWE-Bench Verified, are predominantly derived from GitHub issues and fail to accurately reflect how developers interact with chat-based coding assistants in integrated development environments (IDEs). »  
Source : [Saving SWE-Bench: A Benchmark Mutation Approach for Realistic Agent Evaluation](https://arxiv.org/abs/2510.08996) (arXiv, publication, 2025-10-10)  
Ce travail a 1 autre(s) version(s) ou republication(s), comptées comme UNE seule source.

<a id="p10"></a>**P10** · lacune · Les agents auto-améliorants nécessitent un entraînement hors ligne coûteux sur des benchmarks spécifiques et risquent de mal se généraliser d'un LLM ou d'un benchmark à l'autre.  
> « Meanwhile, such self-improving agents require costly offline training on specific benchmarks and may not generalize well across different LLMs or benchmarks. »  
Source : [Live-SWE-agent: Can Software Engineering Agents Self-Evolve on the Fly?](https://arxiv.org/abs/2511.13646) (arXiv, publication, 2025-11-17)  
Ce travail a 1 autre(s) version(s) ou republication(s), comptées comme UNE seule source.

<a id="p13"></a>**P13** · lacune · Une analyse manuelle des problèmes du benchmark SWE-bench Lite a révélé des biais et défauts, comme des descriptions d'incidents insuffisantes ou induisant en erreur.  
> « Furthermore, we manually classified the problems in SWE-bench Lite and found problems with exact ground truth patch or insufficient/misleading issue descriptions. »  
Source : [Agentless: Demystifying LLM-based Software Engineering Agents](https://arxiv.org/abs/2407.01489) (arXiv, publication, 2024-07-01)  
Ce travail a 2 autre(s) version(s) ou republication(s), comptées comme UNE seule source.

<a id="p16"></a>**P16** · lacune · L'évaluation du benchmark SWE-Bench Pro est compromise par du « reward hacking » lié à des fuites d'information et par des problèmes de qualité des tâches.  
> « However, our analysis work show that its evaluation is undermined by two sources of unreliability: reward hacking, enabled by leakage of gold solutions or hidden evaluation information, and task quality issues, including misleading problem statements and improperly scoped tests. »  
Source : [SWE-Bench Pro Verified: A Reliable Benchmark for Software Engineering Agents](https://arxiv.org/abs/2609.08149) (arXiv, publication, 2026-09-08)  
Ce travail a 1 autre(s) version(s) ou republication(s), comptées comme UNE seule source.

<a id="p28"></a>**P28** · lacune · L'accumulation d'enregistrements en double, obsolètes et contradictoires dans la mémoire à long terme crée une dérive que la recherche seule ne peut corriger.  
> « The second is memory drift: long-running banks accumulate duplicate, stale, and conflicting records that retrieval alone cannot repair. »  
Source : [MemGuard: Persisting Verifier Signals for LLM-Agent Memory Governance](https://arxiv.org/abs/2608.21867) (arXiv, publication, 2026-08-22)

<a id="p29"></a>**P29** · lacune · La mémoire des agents n'est utile que si l'expérience accumulée reste fiable au fil des interactions, une hypothèse démentie en pratique par deux modes de défaillance.  
> « Such memory is useful only when stored experience remains reliable across hundreds of interactions, but two failure modes break that assumption in practice. »  
Source : [MemGuard: Persisting Verifier Signals for LLM-Agent Memory Governance](https://arxiv.org/abs/2608.21867) (arXiv, publication, 2026-08-22)

<a id="p31"></a>**P31** · lacune · Selon un audit récent, près de 60 % des instances non résolues de SWE-bench Verified contiennent des tests défectueux et certains modèles de pointe peuvent reproduire textuellement des correctifs issus de leurs données d'entraînement.  
> « a recent audit found that nearly 60% of unsolved SWE-bench Verified instances contain flawed tests -- either overly narrow tests that reject correct solutions or overly broad tests that check unstated requirements -- and that frontier models can verbatim reproduce gold patches from training data. »  
Source : [SWE-Bench ProMax: Benchmarking Agents on Large-Scale Multilingual Code Refactoring](https://arxiv.org/abs/2608.09802) (arXiv, publication, 2026-08-10)  
Ce travail a 1 autre(s) version(s) ou republication(s), comptées comme UNE seule source.

<a id="p34"></a>**P34** · lacune · Malgré leur utilisation interactive sur le terrain, les benchmarks existants évaluent les agents de codage comme des systèmes entièrement autonomes.  
> « Despite their interactive real-world use, existing benchmarks evaluate them as fully-autonomous systems. »  
Source : [Dialogue SWE-Bench: A Benchmark for Dialogue-Driven Coding Agents](https://arxiv.org/abs/2606.13995) (arXiv, publication, 2026-06-12)  
Ce travail a 1 autre(s) version(s) ou republication(s), comptées comme UNE seule source.

<a id="p40"></a>**P40** · risque · Les défauts d'ancrage environnemental émergent systématiquement dans les flux de travail opérationnels, révélant un problème majeur de fiabilité et de sécurité pour les agents.  
> « Results show that EGDs consistently emerge across operational workflows, highlighting environmental grounding as a core agent reliability problem with important security implications. »  
Source : [When Agents Overtrust Environmental Evidence: An Extensible Agentic Framework for Benchmarking Evidence-Grounding Defects in LLM Agents](https://doi.org/10.48550/arxiv.2605.08828) (OpenAlex (arXiv (Cornell University)), publication, 2026-05-09)

<a id="p6"></a>**P6** · interpretation · L'évolution des modèles de langage vers des agents autonomes capables de réaliser des tâches de développement complexes rend indispensable l'évaluation de leurs capacités réelles.  
> « As large language models (LLMs) evolve into sophisticated autonomous agents capable of complex software development tasks, evaluating their real-world capabilities becomes critical. »  
Source : [LoCoBench-Agent: An Interactive Benchmark for LLM Agents in Long-Context Software Engineering](https://arxiv.org/abs/2511.13998) (arXiv, publication, 2025-11-17)  
Ce travail a 1 autre(s) version(s) ou republication(s), comptées comme UNE seule source.

<a id="p8"></a>**P8** · interpretation · Le décalage entre les benchmarks et l'usage réel entraîne une surestimation systématique des capacités des agents dans des scénarios réels, en particulier pour la correction de bugs.  
> « We posit that this mismatch leads to a systematic overestimation of agent's capabilities in real-world scenarios, especially bug fixing. »  
Source : [Saving SWE-Bench: A Benchmark Mutation Approach for Realistic Agent Evaluation](https://arxiv.org/abs/2510.08996) (arXiv, publication, 2025-10-10)  
Ce travail a 1 autre(s) version(s) ou republication(s), comptées comme UNE seule source.

<a id="p17"></a>**P17** · interpretation · Les faiblesses d'évaluation des benchmarks peuvent gonfler artificiellement les performances mesurées et masquer les véritables capacités de codage des agents.  
> « These issues can inflate benchmark performance and obscure agents' true coding ability. »  
Source : [SWE-Bench Pro Verified: A Reliable Benchmark for Software Engineering Agents](https://arxiv.org/abs/2609.08149) (arXiv, publication, 2026-09-08)  
Ce travail a 1 autre(s) version(s) ou republication(s), comptées comme UNE seule source.

<a id="p22"></a>**P22** · interpretation · Les benchmarks statiques de génération de code ne reflètent pas le développement logiciel réel, qui s'inscrit dans un flux continu d'incidents, de correctifs et de demandes de fonctionnalités.  
> « Large Language Models (LLMs) have achieved impressive results on static code-generation benchmarks, but real-world software development unfolds as a continuous stream of evolving issues, fixes, and feature requests. »  
Source : [SWE-Bench-CL: Continual Learning for Coding Agents](https://arxiv.org/abs/2507.00014) (arXiv, publication, 2025-06-13)  
Ce travail a 1 autre(s) version(s) ou republication(s), comptées comme UNE seule source.

<a id="p30"></a>**P30** · signal · Les agents LLM évoluent vers de longues séquences de tâches où la mémoire réutilisable devient une capacité clé pour le génie logiciel, le terminal et le web.  
> « LLM agents are moving from single-prompt use to long task streams in which reusable memory becomes a core capability for terminal, software-engineering, and web tasks. »  
Source : [MemGuard: Persisting Verifier Signals for LLM-Agent Memory Governance](https://arxiv.org/abs/2608.21867) (arXiv, publication, 2026-08-22)

<a id="p32"></a>**P32** · interpretation · Le refactoring de code nécessite des modifications coordonnées préservant le comportement sur plusieurs fichiers, constituant un test plus difficile et réaliste des agents que ce que proposent les benchmarks actuels.  
> « Code refactoring, which requires coordinated, behavior-preserving changes across many files, offers a substantially harder and more realistic test of agent capability, yet remains underserved by current benchmarks. »  
Source : [SWE-Bench ProMax: Benchmarking Agents on Large-Scale Multilingual Code Refactoring](https://arxiv.org/abs/2608.09802) (arXiv, publication, 2026-08-10)  
Ce travail a 1 autre(s) version(s) ou republication(s), comptées comme UNE seule source.

<a id="p35"></a>**P35** · interpretation · Les résultats indiquent que les modèles de codage les plus performants ne sont pas toujours les meilleurs en dialogue, ce qui montre que cette capacité constitue une dimension distincte et sous-étudiée de la performance.  
> « Our results indicate that better coding models do not always correspond to better dialogue models, suggesting that dialogue capability is a distinct and currently understudied dimension of coding agent performance. »  
Source : [Dialogue SWE-Bench: A Benchmark for Dialogue-Driven Coding Agents](https://arxiv.org/abs/2606.13995) (arXiv, publication, 2026-06-12)  
Ce travail a 1 autre(s) version(s) ou republication(s), comptées comme UNE seule source.

<a id="p41"></a>**P41** · interpretation · De nombreux échecs d'agents attribués à des défaillances de modèles découlent en réalité des défaillances des benchmarks eux-mêmes, comme des spécifications cassées ou des scripts d'évaluation rigides.  
> « As benchmarks grow in complexity, many apparent agent failures are not failures of the agent at all---they are failures of the benchmark itself: broken specifications, implicit assumptions, and rigid evaluation scripts that penalize valid alternative approaches. »  
Source : [Who Guards the Benchmarks? Automated Auditing of LLM Agent Benchmarks](https://doi.org/10.48550/arxiv.2604.24955) (OpenAlex (arXiv (Cornell University)), publication, 2026-04-27)
