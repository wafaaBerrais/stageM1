# Prediction de coverage Outlines

Ce dossier contient le travail fait pour predire les erreurs de coverage du framework
`outlines` dans `extension_jsonschemabench`.

L'objectif est de detecter, a partir des caracteristiques des schemas JSON et des
instances de test, les cas ou Outlines se trompe sur la couverture de validation :

- `UNDER` : le test devrait etre valide, mais Outlines le rejette.
- `OVER` : le test devrait etre invalide, mais Outlines l'accepte.

Les deux problemes sont traites comme deux classifications binaires separees, car
les causes ne sont pas les memes. `UNDER` est surtout lie a des contraintes
numeriques et des cas limites, alors que `OVER` est davantage lie a
`patternProperties`, `additionalProperties` et aux combinateurs.

## Perimetre utilise

Datasets inclus dans l'entrainement final :

- `Github_trivial`
- `Github_easy`
- `Github_medium`
- `Github_ultra`

Dataset exclu :

- `Github_hard`

`Github_hard` a ete relance proprement pour Outlines et l'execution est terminee,
mais elle n'a pas produit de `per_test_results.jsonl` exploitable. Le run a fini
sur les `1240` schemas, avec `888` timeouts au `compile_grammar` et `0` test
termine sur `4898`. Pour cette raison, `Github_hard` n'est pas utilise dans les
modeles de prediction.

## Scripts crees

Les scripts principaux sont :

- `extension_jsonschemabench/scripts/build_outlines_coverage_prediction.py`
  - extrait les features raffinees par test ;
  - construit les datasets binaires `UNDER` et `OVER` ;
  - entraine plusieurs familles de modeles ;
  - selectionne le meilleur modele via validation PR-AUC ;
  - optimise le seuil de decision sur la validation pour maximiser le F1 ;
  - sauvegarde les modeles, metriques, features et rapports.

- `extension_jsonschemabench/scripts/plot_coverage_feature_importance.py`
  - genere les plots SVG d'importance des features ;
  - genere aussi une importance regroupee par famille de features.

- `extension_jsonschemabench/scripts/export_coverage_misclassifications.py`
  - recharge les modeles retenus ;
  - applique les seuils selectionnes ;
  - exporte les tests mal classes sur le split test.

## Dependances installees

Les dependances ajoutees pour ce travail sont :

- `scikit-learn`
- `scipy`
- `joblib`
- `lightgbm`

LightGBM est optionnel dans le script : si le package est installe, les modeles
`LGBMClassifier` sont testes ; sinon le pipeline continue avec les modeles
scikit-learn.

## Gestion du desequilibre

Les classes sont desequilibrees, surtout pour `UNDER`.

Tables de modelisation :

- `UNDER` : `11176` lignes
  - positifs `UNDER` : `1242`
  - negatifs `CORRECT_INVALID` : `9934`

- `OVER` : `6149` lignes
  - positifs `OVER` : `1713`
  - negatifs `CORRECT_VALID` : `4436`

Pour limiter l'effet du desequilibre :

- les modeles compatibles utilisent une ponderation de classe de type
  `class_weight="balanced"` ;
- les seuils ne sont pas fixes a `0.5` : ils sont choisis sur le split de
  validation pour maximiser le F1 ;
- la selection du modele se fait d'abord sur la PR-AUC validation, plus adaptee
  aux classes rares que l'accuracy.

Point important : pour `HistGradientBoostingClassifier`, on a evite de faire une
double compensation du desequilibre. Utiliser a la fois `class_weight="balanced"`
et des `sample_weight` peut degrader fortement la precision. Le pipeline retient
une seule strategie de ponderation.

## Modeles testes

Familles testees :

- `LogisticRegression`
- `RandomForestClassifier`
- `HistGradientBoostingClassifier`
- `LGBMClassifier`

Des variantes d'hyperparametres ont ete testees :

- regularisation `C` pour la regression logistique ;
- profondeur implicite, `min_samples_leaf` et `max_features` pour Random Forest ;
- `learning_rate`, `l2_regularization` et `max_leaf_nodes` pour HistGradientBoosting ;
- `learning_rate` et `num_leaves` pour LightGBM.

Tous les candidats sont sauvegardes dans :

```text
extension_jsonschemabench/coverage_prediction/outlines/models/
```

Les modeles finalement retenus sont :

```text
under_model.pkl
over_model.pkl
```

## Resultats retenus

Modele final `UNDER` :

- modele : `lightgbm_lr0.03_leaves15`
- seuil : `0.78`
- features : `20`
- test F1 : `0.726225`
- test precision : `0.741176`
- test recall : `0.711864`
- test PR-AUC : `0.715509`
- test ROC-AUC : `0.891194`

Modele final `OVER` :

- modele : `random_forest_leaf2_sqrt`
- seuil : `0.38`
- features : `59`
- test F1 : `0.658273`
- test precision : `0.628866`
- test recall : `0.690566`
- test PR-AUC : `0.780778`
- test ROC-AUC : `0.823703`

Les metriques completes sont dans :

```text
extension_jsonschemabench/coverage_prediction/outlines/metrics/
```

Fichiers utiles :

- `under_metrics.csv`
- `over_metrics.csv`
- `under_model_selection.csv`
- `over_model_selection.csv`
- `under_confusion_matrix.csv`
- `over_confusion_matrix.csv`
- `under_classification_report.csv`
- `over_classification_report.csv`

## Feature importance

Les importances de features sont exportees dans :

```text
extension_jsonschemabench/coverage_prediction/outlines/metrics/
```

Fichiers principaux :

- `under_feature_importance.csv`
- `over_feature_importance.csv`

Les plots sont dans :

```text
extension_jsonschemabench/coverage_prediction/outlines/plots/feature_importance/
```

Plots generes :

- `under_top25_feature_importance.svg`
- `under_top25_grouped_feature_importance.svg`
- `over_top25_feature_importance.svg`
- `over_top25_grouped_feature_importance.svg`
- `feature_importance_index.html`

## Tests mal classes

Les tests mal classes du split test sont exportes dans :

```text
extension_jsonschemabench/coverage_prediction/outlines/errors/
```

Fichiers generes :

- `under_test_misclassified_tests.csv`
- `over_test_misclassified_tests.csv`
- `all_test_misclassified_tests.csv`
- `test_misclassification_summary.csv`

Nombre de lignes exportees :

- `UNDER` : `95` erreurs, plus l'en-tete CSV
- `OVER` : `190` erreurs, plus l'en-tete CSV

Ces fichiers sont ceux a utiliser pour inspecter les cas concrets ou les modeles
retenus se trompent.

## Commandes de reproduction

Installer les dependances dans le venv :

```bash
.venv/bin/python -m pip install scikit-learn lightgbm
```

Reconstruire les features, datasets, modeles et metriques sans `Github_hard` :

```bash
.venv/bin/python extension_jsonschemabench/scripts/build_outlines_coverage_prediction.py \
  --datasets Github_trivial Github_easy Github_medium Github_ultra
```

Regenerer les plots de feature importance :

```bash
.venv/bin/python extension_jsonschemabench/scripts/plot_coverage_feature_importance.py
```

Regenerer les fichiers de tests mal classes :

```bash
.venv/bin/python extension_jsonschemabench/scripts/export_coverage_misclassifications.py
```

## Structure des artefacts

```text
extension_jsonschemabench/coverage_prediction/outlines/
|-- coverage_prediction_report.md
|-- README.md
|-- features/
|   |-- Github_trivial_refined_test_features.csv
|   |-- Github_easy_refined_test_features.csv
|   |-- Github_medium_refined_test_features.csv
|   |-- Github_ultra_refined_test_features.csv
|   `-- all_datasets_refined_test_features.csv
|-- modeling/
|   |-- under_dataset.csv
|   |-- over_dataset.csv
|   |-- selected_under_features.txt
|   `-- selected_over_features.txt
|-- models/
|   |-- under_model.pkl
|   |-- over_model.pkl
|   `-- *_model.pkl
|-- metrics/
|   |-- under_metrics.csv
|   |-- over_metrics.csv
|   |-- under_feature_importance.csv
|   `-- over_feature_importance.csv
|-- plots/
|   `-- feature_importance/
`-- errors/
    |-- under_test_misclassified_tests.csv
    |-- over_test_misclassified_tests.csv
    |-- all_test_misclassified_tests.csv
    `-- test_misclassification_summary.csv
```

## Interpretation rapide

Les scores ne sont pas parfaits pour trois raisons principales :

- le signal est difficile : les erreurs Outlines dependent souvent de details de
  compilation de grammaire, pas seulement de features statiques du schema ;
- les classes sont desequilibrees, surtout pour `UNDER` ;
- certains datasets ont tres peu de positifs sur le split test, ce qui rend les
  metriques par dataset instables.

La gestion du desequilibre a ameliore la situation, mais elle ne suffit pas a
elle seule. Les meilleurs gains viennent surtout de la separation `UNDER`/`OVER`,
du choix de features specialisees et de l'optimisation du seuil sur validation.
