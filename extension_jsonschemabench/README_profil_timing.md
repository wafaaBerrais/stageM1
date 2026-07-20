# Timing profile des executions XGrammar

Ce document explique le fichier `timing_profile.csv` produit par les scripts de
l'extension JSONSchemaBench. L'objectif est d'identifier dans quelle etape un
framework comme XGrammar passe du temps, et de garder une trace exploitable meme
quand un schema finit en timeout.

## Pipeline mesure

Pour chaque schema, le runner appelle XGrammar avec le pipeline suivant :

1. Charger le tokenizer et initialiser XGrammar.
2. Lire le fichier JSON du benchmark.
3. Compiler/generer la grammaire a partir du JSON Schema.
4. Pour chaque test du schema :
   - convertir l'instance JSON du test en texte JSON ;
   - tokenizer ce texte avec le tokenizer du modele ;
   - reinitialiser le matcher XGrammar ;
   - rejouer les tokens un par un ;
   - pour chaque token : calculer le masque (`compute_mask`) puis consommer le token (`commit_token`).

## Fichiers utiles

- `timing_profile.csv` : timings detailles par test.
- `timed_out_schemas.jsonl` : journal schema-level des timeouts. Ce fichier peut contenir plusieurs tentatives historiques pour un meme schema ; pour compter les schemas, utiliser les `schema_id` uniques.
- `supervisor.log` : logs detailles des appels du runner.

Pour les relances profilees actuelles :

- `Github_easy` a ete relance avec un timeout de 20 minutes par schema.
- `Github_trivial` a ete relance avec un timeout de 10 minutes par schema.

## Colonnes de `timing_profile.csv`

Les durees finissant par `_us` sont en microsecondes. Pour convertir en secondes :

secondes = valeur_us / 1_000_000

| Colonne | Signification |
| --- | --- |
| `schema_id` | Nom du fichier schema/test du benchmark. |
| `dataset_id` | Dataset d'origine, par exemple `Github_easy`. |
| `schema_path` | Chemin du fichier source dans `maskbench/data`. |
| `test_id` | Identifiant unique du test dans ce schema. |
| `test_index` | Position du test dans la liste `tests`. |
| `expected_validity` | Verite terrain du benchmark : `valid` ou `invalid`. |
| `framework_id` | Identifiant court du framework, ici `xgr`. |
| `framework` | Nom lisible du framework, ici `XGrammar`. |
| `actual_result` | Resultat produit : `passed`, `failed`, `timeout`, ou checkpoint partiel comme `running_compile_grammar`. |
| `accepted` | `True` si XGrammar accepte l'instance, `False` s'il la rejette. Vide si pas de resultat final. |
| `result_available` | `True` si le test a un resultat final, `False` si timeout ou checkpoint partiel. |
| `schema_file_bytes` | Taille du fichier JSON sur disque. |
| `schema_json_chars` | Taille en caracteres du schema JSON apres serialisation. |
| `instance_json_chars` | Taille en caracteres de l'instance JSON du test apres `json.dumps`. Vide si le test n'a pas encore ete prepare. |
| `engine_tokenizer_load_us` | Temps de chargement du tokenizer HuggingFace. |
| `engine_init_us` | Temps d'initialisation du moteur XGrammar : preparation du tokenizer info, buffer de mask, compiler, etc. |
| `schema_load_us` | Temps de lecture/parsing du fichier JSON du benchmark. |
| `compile_grammar_us` | Temps de compilation/generation de la grammaire XGrammar depuis le JSON Schema. Vide si la compilation n'a pas fini. |
| `test_json_dumps_us` | Temps pour convertir `test["data"]` en texte JSON via `json.dumps`. |
| `tokenize_us` | Temps pour convertir le texte JSON du test en tokens du modele. |
| `reset_matcher_us` | Temps pour remettre le matcher XGrammar au debut de la grammaire avant un test. |
| `validation_loop_us` | Temps total de la boucle de validation token par token. |
| `compute_mask_us` | Temps total passe a calculer les masques de vocabulaire autorise. |
| `commit_token_us` | Temps total passe a consommer les tokens reels de l'instance avec le matcher. |
| `max_compute_mask_us` | Plus gros temps observe pour un seul appel a `compute_mask`. |
| `max_commit_token_us` | Plus gros temps observe pour un seul appel a `commit_token`. |
| `num_tokens` | Nombre total de tokens de l'instance JSON. |
| `tokens_checked` | Nombre de tokens effectivement consommes avant acceptation ou rejet. |
| `first_rejected_token_index` | Index du premier token rejete, si l'instance est rejetee. |
| `error_message` | Message de checkpoint ou d'erreur. Pour un timeout, contient souvent `supervisor_timeout_after_seconds=...`. |

## Difference entre tokenizer load et tokenize

Il y a deux mesures liees au tokenizer :

- `engine_tokenizer_load_us` : chargement de l'outil tokenizer une fois au debut du runner.
- `tokenize_us` : application du tokenizer a une instance JSON precise.

Exemple conceptuel :

Texte JSON: {"name":"Ali"}
Tokens: [5018, 609, 3332, ...]


XGrammar travaille au niveau tokens car, dans un usage LLM, le mask sert a
interdire les tokens du vocabulaire qui violeraient la grammaire.

## compute_mask et commit_token

Pendant la validation, on rejoue l'instance JSON deja connue. A chaque position :

1. `compute_mask` calcule quels tokens du vocabulaire sont autorises par la grammaire.
2. `commit_token` donne le vrai token de l'instance au matcher.
3. Si le token est accepte, le matcher avance. Sinon, l'instance est rejetee.

Dans une generation LLM reelle, le mask serait applique aux logits du modele
pour forcer la sortie a respecter le schema. Ici, on utilise le meme mecanisme
pour tester si une instance benchmark est compatible avec la grammaire generee.

## Exemple sans timeout

Exemple issu de `Github_easy/timing_profile.csv` :

schema_id: Github_easy---o9778.json
test_id: Github_easy---o9778.json::test_00000
expected_validity: valid
actual_result: passed
accepted: True
result_available: True
schema_file_bytes: 4273
schema_json_chars: 571
instance_json_chars: 185
engine_tokenizer_load_us: 1328740
engine_init_us: 838528
schema_load_us: 613
compile_grammar_us: 111397261
test_json_dumps_us: 22
tokenize_us: 1000
reset_matcher_us: 24
validation_loop_us: 6387
compute_mask_us: 6189
commit_token_us: 79
num_tokens: 54
tokens_checked: 54

Lecture :

- Le test est attendu `valid`.
- XGrammar l'a accepte, donc le resultat est `passed`.
- Le chargement du tokenizer prend environ 1.33 s.
- L'initialisation XGrammar prend environ 0.84 s.
- La compilation de grammaire prend environ 111.40 s.
- La tokenisation de l'instance prend environ 0.001 s.
- La validation token par token prend environ 0.006 s.
- Les 54 tokens ont ete consommes : `tokens_checked = num_tokens = 54`.

Ici, le cout dominant est clairement `compile_grammar_us`, pas la validation.

## Exemple avec timeout

Exemple issu de `Github_easy/timing_profile.csv` :

schema_id: Github_easy---o9966.json
test_id: Github_easy---o9966.json::test_00002
expected_validity: invalid
actual_result: timeout
accepted:
result_available: False
schema_file_bytes: 4815
schema_json_chars: 564
instance_json_chars:
engine_tokenizer_load_us: 1485862
engine_init_us: 836235
schema_load_us: 213
compile_grammar_us:
error_message: stage=compile_grammar; partial checkpoint before grammar compilation. supervisor_timeout_after_seconds=1200.114

Lecture :

- Le benchmark dit que ce test devrait etre `invalid`.
- XGrammar n'a pas donne de resultat final : `actual_result = timeout`.
- `accepted` est vide car on n'est jamais arrive a la validation.
- `result_available = False` confirme que ce n'est ni un `passed` ni un `failed`.
- Le tokenizer et XGrammar ont bien ete initialises.
- La lecture du schema est terminee.
- `compile_grammar_us` est vide car la generation/compilation de grammaire n'a jamais rendu la main.
- Le superviseur a coupe apres environ 1200 s, donc 20 minutes.

Ce cas ne doit pas etre classe comme under-constraint ou over-constraint. C'est
un cas de non-couverture / timeout du framework.

## Statistiques observees

Les chiffres ci-dessous concernent les fichiers disponibles au moment de la
redaction de ce document.

### Github_easy

- `timing_profile.csv` contient 151 lignes de tests profilees.
- 49 lignes ont un resultat final normal : 45 `passed`, 4 `failed`.
- 102 lignes sont marquees `timeout`.
- Ces 102 lignes correspondent a 20 schemas uniques en timeout.
- Tous les timeouts profiles de `Github_easy` coupent pendant `compile_grammar`.
- Le timeout utilise pour ces relances est 20 minutes par schema.

Schemas `Github_easy` en timeout dans `timing_profile.csv` :

```text
Github_easy---o6176.json
Github_easy---o9765.json
Github_easy---o9768.json
Github_easy---o9772.json
Github_easy---o9773.json
Github_easy---o9774.json
Github_easy---o9783.json
Github_easy---o9812.json
Github_easy---o9861.json
Github_easy---o9870.json
Github_easy---o9871.json
Github_easy---o9892.json
Github_easy---o9893.json
Github_easy---o9896.json
Github_easy---o9931.json
Github_easy---o9945.json
Github_easy---o9955.json
Github_easy---o9959.json
Github_easy---o9966.json
Github_easy---o9967.json
```

### Github_trivial

- `timing_profile.csv` contient 1174 lignes de tests profilees.
- 1154 lignes ont un resultat final normal : 1033 `passed`, 121 `failed`.
- 9 lignes sont marquees `timeout`.
- Ces 9 lignes correspondent a 3 schemas uniques en timeout.
- Les 9 timeouts propres de `Github_trivial` coupent pendant `compile_grammar`.
- Le timeout utilise pour ces relances est 10 minutes par schema.

Schemas `Github_trivial` avec timeout propre :

```text
Github_trivial---o9790.json
Github_trivial---o9912.json
Github_trivial---o9933.json
```

Deux schemas `Github_trivial` ont aussi des checkpoints partiels mais pas un
timeout propre, car le processus a ete interrompu avec `exit_-15` avant le
timeout superviseur :

```text
Github_trivial---o64546.json : checkpoints `compiled` et `running_validation`
Github_trivial---o67212.json : checkpoints `running_compile_grammar`
```

Ces deux schemas restent utiles pour l'analyse car ils indiquent quand meme la
derniere etape connue avant interruption, mais ils doivent etre distingues des
timeouts propres.

## Interpretation pour l'analyse

- `passed` : le framework donne le resultat attendu par le benchmark.
- `failed` avec `expected_validity=valid` : le framework est trop strict, cas possible d'over-constraint.
- `failed` avec `expected_validity=invalid` : le framework est trop permissif, cas possible d'under-constraint.
- `timeout` : pas de resultat final de validation ; c'est un probleme de couverture/performance du framework.

Dans les timeouts observes ici, le blocage se produit majoritairement, et pour
les timeouts propres de `Github_easy` et `Github_trivial` exclusivement, pendant
la generation/compilation de grammaire (`compile_grammar`).
