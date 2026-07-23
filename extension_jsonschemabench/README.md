# Extension JSONSchemaBench

Ce dossier contient une couche d'analyse ajoutee autour de
JSONSchemaBench/MaskBench. Il sert a lancer des frameworks de decodage
contraint, enregistrer les resultats par test, analyser les erreurs, produire
des plots et construire des modeles de prediction.

Le dossier ne modifie pas les donnees originales de MaskBench. Les schemas et
tests restent dans:

```text
maskbench/data/
```

Les sorties propres a cette extension sont regroupees dans:

```text
extension_jsonschemabench/
```

## Structure generale

```text
extension_jsonschemabench/
├── README.md
├── README_features_raffinees.md
├── README_profil_timing.md
├── readme_comparer_framework.md
├── scripts/
├── results/
│   └── per_dataset_runs/
│       ├── xgr/
│       ├── outlines/
│       └── guidance/
└── coverage_prediction/
    └── outlines/
```

## Fichiers README utiles

- `README.md`: ce fichier, vue d'ensemble du dossier.
- `README_features_raffinees.md`: explication des features raffinees, des
  analyses UNDER/OVER et des resultats observes sur `outlines/Github_medium`.
- `README_profil_timing.md`: documentation du profiling timing, des CSV de
  temps et des plots de performance.
- `readme_comparer_framework.md`: notes pour comparer les frameworks.
- `coverage_prediction/outlines/README.md`: documentation du pipeline de
  prediction des erreurs de couverture pour `outlines`.

## Dossier `scripts/`

Le dossier `scripts/` contient les programmes Python utilises pour lancer les
runs, reconstruire les index, analyser les resultats et produire les plots.

Scripts principaux:

| Script | Role |
| --- | --- |
| `run_per_test_framework_logging.py` | Lance un framework et produit un resultat par test. |
| `run_dataset_with_timeouts.py` | Lance un dataset avec timeouts, reprise, profiling et logs superviseur. |
| `run_dataset_profile_csv_with_timeouts.py` | Variante orientee profiling CSV. |
| `build_schema_test_framework_index.py` | Reconstruit un index schema/test/framework a partir de `maskbench/data`. |
| `summarize_constraint_results.py` | Resume les resultats et les erreurs UNDER/OVER. |
| `analyze_dataset_statistics.py` | Genere les statistiques et les plots standards d'un run. |
| `analyze_cross_dataset_statistics.py` | Compare plusieurs datasets/runs. |
| `analyze_outlines_specific.py` | Analyses plus ciblees pour `outlines`. |
| `analyze_compile_error_causes.py` | Analyse les causes d'erreurs de compilation. |
| `analyze_refined_features.py` | Genere les features raffinees v1. |
| `analyze_refined_features_v2.py` | Genere les analyses conditionnelles v2. |
| `build_outlines_coverage_prediction.py` | Construit les datasets/modeles de prediction pour `outlines`. |
| `plot_coverage_feature_importance.py` | Produit les plots d'importance de features. |
| `export_coverage_misclassifications.py` | Exporte les erreurs de classification des modeles. |
| `run_hdd_minimization.py` | Lance des minimisations HDD pour tester des hypotheses causales. |
| `resume_outlines_hard_resilient.py` | Reprise resiliente du dataset `Github_hard` avec `outlines`. |

## Dossier `results/`

`results/` contient les resultats experimentaux produits par l'extension.

La structure principale est:

```text
results/per_dataset_runs/<framework>/<dataset>/
```

Exemples:

```text
results/per_dataset_runs/xgr/Github_medium/
results/per_dataset_runs/outlines/Github_medium/
results/per_dataset_runs/guidance/Github_medium/
```

Les frameworks actuellement presents sont:

- `xgr`
- `outlines`
- `guidance`

Les datasets Github utilises sont generalement:

- `Github_trivial`
- `Github_easy`
- `Github_medium`
- `Github_hard`
- `Github_ultra`

## Contenu d'un dossier de run

Un dossier comme:

```text
results/per_dataset_runs/outlines/Github_medium/
```

peut contenir:

| Fichier ou dossier | Description |
| --- | --- |
| `per_test_results.jsonl` | Resultats detailles, une ligne par test. |
| `timed_out_schemas.jsonl` | Schemas ayant depasse un timeout. |
| `timing_profile.csv` | Temps mesures par schema/test ou phase. |
| `schema_compile_profile.csv` | Profil de compilation des schemas, surtout utile pour `outlines`. |
| `timeout_checkpoints.jsonl` | Checkpoints de progression pendant les runs longs. |
| `supervisor.log` | Log principal du run supervise. |
| `plots/` | Graphiques et CSV d'analyse generes apres le run. |
| `refined_feature_analysis/` | Tables de features raffinees v1. |
| `refined_feature_analysis_v2/` | Tables d'analyse conditionnelle v2. |

Tous les dossiers ne contiennent pas exactement les memes fichiers. Par
exemple, `xgr` n'a pas forcement `schema_compile_profile.csv`, alors que ce
fichier est important pour `outlines`.

## Dossier `plots/` dans un run

Les plots standards sont generes par:

```bash
.venv/bin/python extension_jsonschemabench/scripts/analyze_dataset_statistics.py \
  --framework outlines \
  --dataset Github_medium
```

Par defaut, ils sont ecrits dans:

```text
results/per_dataset_runs/<framework>/<dataset>/plots/
```

Ce dossier peut contenir:

- des fichiers `.svg` pour les graphiques;
- des fichiers `.csv` resumant les statistiques;
- des sous-dossiers pour les analyses specialisees, par exemple
  `refined_feature_analysis/` et `refined_feature_analysis_v2/`.

## Features raffinees

Les features raffinees servent a expliquer les erreurs avec plus de contexte
que les simples mots-cles presents dans un schema.

Elles couvrent notamment:

- les contraintes numeriques (`minimum`, `maximum`, `multipleOf`, type cible,
  champ requis, cas de frontiere);
- `patternProperties`, les regex et `additionalProperties`;
- les combinateurs (`allOf`, `anyOf`, `oneOf`) et leurs branches;
- `not` et le contenu du sous-schema nie;
- les cooccurrences locales de mots-cles.

Pour `outlines/Github_medium`, les resultats montrent principalement:

- UNDER est fortement associe aux contraintes numeriques et aux cas de
  frontiere (`below_min`, `above_max`, champs requis, types numeriques);
- OVER est fortement associe a `patternProperties`, `additionalProperties` et
  aux regex;
- les combinateurs contribuent surtout aux OVER quand plusieurs branches ou
  proprietes se recouvrent;
- les signaux autour de `not` ne sont pas robustes sur ce dataset.

Voir le document detaille:

```text
README_features_raffinees.md
```

## Profiling timing

Les runs peuvent etre lances avec profiling pour mesurer les temps de
compilation, generation, validation et autres phases.

Les fichiers principaux sont:

- `timing_profile.csv`
- `schema_compile_profile.csv`
- `timeout_checkpoints.jsonl`
- `plots/phase_*.svg`
- `plots/*timing*.csv`

Voir:

```text
README_profil_timing.md
```

## Prediction de couverture

Le dossier:

```text
coverage_prediction/outlines/
```

contient un pipeline separe pour predire les erreurs de couverture de
`outlines` a partir des features raffinees.

Structure:

```text
coverage_prediction/outlines/
├── features/
├── modeling/
├── metrics/
├── models/
├── plots/
├── errors/
├── README.md
└── coverage_prediction_report.md
```

Role des sous-dossiers:

- `features/`: tables de features utilisees par les modeles;
- `modeling/`: datasets prepares pour l'entrainement;
- `metrics/`: rapports de classification, matrices de confusion, importances;
- `models/`: modeles entraines serialises en `.pkl`;
- `plots/`: figures associees aux modeles;
- `errors/`: exemples de tests mal classes.

## Commandes courantes

Lister les datasets:

```bash
.venv/bin/python extension_jsonschemabench/scripts/run_per_test_framework_logging.py \
  --list-datasets \
  maskbench/data
```

Lancer un framework sur un dataset avec sortie separee:

```bash
.venv/bin/python extension_jsonschemabench/scripts/run_per_test_framework_logging.py \
  --framework xgr \
  --split-by-dataset \
  --dataset Github_easy \
  maskbench/data
```

Lancer un dataset avec timeouts et profiling:

```bash
.venv/bin/python extension_jsonschemabench/scripts/run_dataset_with_timeouts.py \
  --framework outlines \
  --dataset Github_medium \
  --timeout-minutes 10 \
  --progress-interval-minutes 1 \
  --profile-timings \
  --profile-checkpoint-interval-seconds 10 \
  --trace-stages \
  maskbench/data
```

Regenerer les plots standards:

```bash
.venv/bin/python extension_jsonschemabench/scripts/analyze_dataset_statistics.py \
  --framework outlines \
  --dataset Github_medium
```

Regenerer les features raffinees v1:

```bash
.venv/bin/python extension_jsonschemabench/scripts/analyze_refined_features.py \
  --framework outlines \
  --dataset Github_medium \
  --output-data-dir extension_jsonschemabench/results/per_dataset_runs/outlines/Github_medium/refined_feature_analysis \
  --output-plot-dir extension_jsonschemabench/results/per_dataset_runs/outlines/Github_medium/plots/refined_feature_analysis
```

Regenerer les features raffinees v2:

```bash
.venv/bin/python extension_jsonschemabench/scripts/analyze_refined_features_v2.py \
  --dataset Github_medium \
  --input-dir extension_jsonschemabench/results/per_dataset_runs/outlines/Github_medium/refined_feature_analysis \
  --output-data-dir extension_jsonschemabench/results/per_dataset_runs/outlines/Github_medium/refined_feature_analysis_v2 \
  --output-plot-dir extension_jsonschemabench/results/per_dataset_runs/outlines/Github_medium/plots/refined_feature_analysis_v2
```

## Identifiants stables

Les analyses utilisent les identifiants suivants:

- `schema_id`: nom du fichier MaskBench, par exemple
  `Github_easy---o10008.json`;
- `test_id`: identifiant de test sous la forme
  `schema_id::test_<index>`;
- `test_index`: position du test dans le tableau `tests` du fichier source.

Ces identifiants restent stables tant que les fichiers dans `maskbench/data/`
et l'ordre des tests ne changent pas.

## Notes de nettoyage

Certains fichiers sont utiles pendant un run mais peuvent devenir temporaires
apres verification:

- anciens logs de relance;
- fichiers `.bak-*`;
- dossiers de replay timing;
- fichiers `.nfs*` seulement quand aucun processus ne les garde ouverts.

En revanche, il faut conserver:

- `per_test_results.jsonl`;
- `timing_profile.csv`;
- `schema_compile_profile.csv` pour `outlines`;
- `timed_out_schemas.jsonl`;
- les dossiers `plots/` si les graphiques sont encore utilises;
- les dossiers `refined_feature_analysis/` et `refined_feature_analysis_v2/`
  si on veut eviter de regenerer les features.

## Relation avec MaskBench original

MaskBench fournit les schemas, les tests et les runners de base.
`extension_jsonschemabench` ajoute une couche de logging et d'analyse plus fine.

Le runner original produit surtout des resultats au niveau schema. Cette
extension produit des sorties au niveau test, ce qui permet de distinguer:

- les tests corrects;
- les erreurs UNDER: le framework accepte une instance attendue invalide;
- les erreurs OVER: le framework rejette une instance attendue valide;
- les erreurs de compilation;
- les timeouts.

