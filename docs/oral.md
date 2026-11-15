# Préparation de l'oral TraceWatch

Chaque membre doit savoir faire deux choses : (1) présenter le schéma global en 2 minutes, (2) expliquer **son** module et répondre **seul** aux questions dessus.

## 1. Le pitch commun (2 minutes, à savoir par cœur)

1. **La question.** Peut-on se fier aux scores des benchmarks d'agents (SWE-bench, WebArena) pour confier du développement de routine à des agents autonomes, ou ces scores surestiment-ils la fiabilité réelle ?
2. **Le principe.** L'IA propose, le code vérifie. Une affirmation n'entre dans le rapport que si sa citation figure **mot pour mot** dans le document source.
3. **La chaîne.** Collecte (5 familles, 1 337 documents) → dédoublonnage (1 288 travaux, 5 republications = 1 preuve) → 3 scores séparés → analyse IA avec citations vérifiées → preuves [Pn] → rapport traçable et révisable.
4. **Le résultat.** Pilote contrôlé, confiance forte. Les scores sont prometteurs (11 sources indépendantes), mais l'écart est fortement documenté : validité des benchmarks (30 sources), fiabilité et sécurité (13), usage réel (9). Un fournisseur optimiste sur l'usage réel est contredit par 9 sources indépendantes.
5. **La limite assumée.** L'IA a analysé les 63 documents les plus pertinents, pas les 1 337, avec 4 modèles Gemini à cause des quotas gratuits. Et nous avons révisé la règle de décision après avoir vu un résultat : c'est tracé dans l'historique.

## 2. Qui défend quoi

### A : cadrage, architecture, analyse IA (étapes 0, 1, 2, 6)
- **À savoir expliquer :** le prompt (citation verbatim obligatoire, catégories, thèmes imposés) ; `verification.py` (seules les tolérances typographiques sont acceptées : casse, espaces, guillemets, tirets) ; le cache (empreinte du modèle et du prompt) ; le niveau de preuve (clusters indépendants, fournisseurs comptés à part).
- **Chiffres :** 146 affirmations proposées, 144 vérifiées ; 2 vrais rejets (« do report » au lieu de « does report », et une phrase inventée), tous deux venant du modèle le plus léger ; 4 faux rejets typographiques corrigés (espace HTML, Markdown).
- **Questions probables :**
  - *« Et si le LLM cite un vrai passage, mais l'interprète mal ? »* C'est notre limite principale : seule la citation est vérifiée, pas l'interprétation. C'est pour ça que le rapport affiche la citation à côté de chaque affirmation, pour que le lecteur juge.
  - *« Pourquoi Gemini ? »* Gratuit sans carte bancaire, et le client est interchangeable. On a d'ailleurs dû changer de modèle pendant le projet : `gemini-2.5` est refusé aux nouveaux comptes.
  - *« Pourquoi une température de 0 ? »* Pour avoir des réponses les plus stables possibles. Le cache garantit ensuite la reproductibilité exacte.

### B : collecte (étape 3)
- **À savoir expliquer :** les 5 familles et leurs API (arXiv : 3 s entre deux appels, c'est leur règle ; OpenAlex ; GitHub sans jeton ; RSS) ; pourquoi les classements sont collectés entrée par entrée (pour savoir si un résultat est vérifié ou auto-déclaré) ; le filtre par mots-clés des flux RSS.
- **Chiffres :** 173 résultats auto-déclarés, 93 vérifiés, 48 rapportés par des tiers ; 66 % du blog OpenAI est hors sujet.
- **Questions probables :**
  - *« Pourquoi pas Anthropic ? »* Pas de flux RSS public. On a pris Google DeepMind à la place.
  - *« Que se passe-t-il si une source tombe ? »* Les autres continuent, l'erreur est affichée, et relancer n'ajoute pas de doublon.

### C : normalisation, scoring, tests (étapes 4, 5, 9)
- **À savoir expliquer :** les 6 règles de doublon, chacune avec sa raison ; le fait qu'un cluster vaut une source ; pourquoi les classements sont exclus de la similarité (même gabarit de texte, 10 fausses paires mesurées) ; les 3 scores jamais fusionnés ; les alertes de qualité.
- **Chiffres :** 48 groupes de doublons ; bruit 26 % → 0 % après resserrement ; 61 tests.
- **Questions probables :**
  - *« Pourquoi TF-IDF et pas des embeddings ? »* C'est explicable, rapide, et suffisant ici : on a relu tous les groupes, sans faux doublon trouvé.
  - *« Pourquoi une demi-vie de 12 mois ? »* C'est l'horizon de la question. C'est un choix conventionnel, réglable dans le profil.
  - *« Comment testez-vous l'IA sans dépendre du modèle ? »* Le test 3 utilise un faux LLM aux réponses connues, qui contient une citation inventée que le code doit rejeter.

### D : traçabilité, rapport, tableau de bord, note (étapes 7, 8, 10)
- **À savoir expliquer :** la chaîne phrase → [Pn] → citation → document → document original ; le contrôle phrase par phrase (un rapport non conforme est refusé) ; la règle de décision et le plafonnement de la confiance ; les révisions versionnées.
- **Questions probables :**
  - *« Pourquoi le rapport n'est-il pas rédigé par le LLM ? »* Un texte libre réintroduirait des phrases non vérifiées. Le code assemble uniquement des preuves vérifiées.
  - *« La règle de décision n'est-elle pas arbitraire ? »* Ses seuils sont conventionnels, mais elle est explicite, publique et proportionnée au niveau de preuve. Un LLM qui « recommande » serait arbitraire **et** opaque.
  - *« Montrez une révision. »* Onglet Révisions, conclusion `decision` : version 2, confiance plafonnée (usage réel non documenté) ; version 3, « exclure » après l'analyse complète ; version 4, retour à « pilote » une fois la règle alignée sur le CADRAGE. Chaque version garde son motif et les preuves ajoutées ou retirées.
  - *« Vous avez changé la règle parce que le résultat ne vous plaisait pas ? »* La règle testait « exclure » sans regarder les 11 sources optimistes, contrairement à la définition du CADRAGE. Nous l'avons corrigée, et le changement est tracé, testé et discuté dans la note. La version « exclure » reste consultable.

## 3. Script de démonstration (environ 6 minutes, mode Démo)

Avant l'oral : `python -m tracewatch.demo`, puis `streamlit run src/tracewatch/app/streamlit_app.py`, et choisir **Démo (figée)**. Tout fonctionne sans Internet.

| Scénario | Où | Ce qu'on montre |
|---|---|---|
| Vue d'ensemble | Vue d'ensemble | Décision, confiance plafonnée et pourquoi, sources par famille, niveau de preuve par thème |
| 1. Doublons | Corpus, interrupteur « Un document par travail » | Le nombre de documents baisse, celui des travaux distincts ne change pas |
| 2. Ancien mais pertinent | Corpus, curseur Pertinence à 0,5 | Des documents de 2023 restent : la fraîcheur n'est filtrée que si on le demande |
| 4. Bruit | Corpus : curseurs à 0, puis Pertinence à 0,3 | L'alerte de bruit disparaît, la qualité passe à BON |
| 5. Élément contesté | Rapport : cliquer sur un [Pn] ; ou Preuves : choisir une preuve | Citation exacte, lien vers le document, puis vers l'original |
| 3. Contradiction | Contradictions | Thème « Résultats en usage réel » : fournisseur optimiste contre 9 sources indépendantes critiques |
| Garde-fou | Terminal : `pytest -q` | 61 tests verts, dont la citation inventée rejetée |

## 4. Questions transversales (tout le monde)

- *« Votre système peut-il réfuter votre hypothèse ? »* Oui. La règle donnerait « différer » sans résultats prometteurs, ou « exclure » avec des échecs graves fortement documentés. L'hypothèse n'intervient pas dans le calcul : elle n'est comparée au résultat qu'à la fin.
- *« Qu'est-ce qui changerait votre recommandation ? »* Des retours d'usage réel documentés par au moins 3 sources indépendantes. S'ils sont positifs, la confiance monte ; s'ils sont négatifs, et accompagnés d'échecs graves, la recommandation glisse vers « exclure ».
- *« Comment évitez-vous les fuites de clé ? »* `.env` est ignoré par Git, et un test cherche les formats de clés **et** la valeur réelle de la clé dans tous les fichiers du dépôt.
- *« Quels services IA avez-vous utilisés ? »* Voir la section Déclarations du README : Gemini dans le produit, et un assistant de code pendant le développement.
