# Prediction de coverage XGrammar

Ce dossier contient le travail de prediction des erreurs de coverage pour le framework `xgr`.

Les deux problemes sont traites comme deux classifications binaires separees :

- `UNDER` : le test est invalide, mais le framework l'accepte.
- `OVER` : le test est valide, mais le framework le rejette.

## Perimetre utilise

Datasets inclus :

- `Github_trivial`
- `Github_easy`
- `Github_medium`
- `Github_hard`
- `Github_ultra`

Datasets exclus : aucun.

## Tables de modelisation

- `UNDER` : 14169 lignes
  - positifs `UNDER` : 2159
  - negatifs `CORRECT_INVALID` : 12010

- `OVER` : 7529 lignes
  - positifs `OVER` : 1468
  - negatifs `CORRECT_VALID` : 6061

## Modeles retenus

Modele final `UNDER` :

- modele : `random_forest_leaf1_sqrt`
- seuil : `0.55`
- features : `20`
- test F1 : `0.334545`
- test precision : `0.378601`
- test recall : `0.299674`
- test PR-AUC : `0.314307`
- test ROC-AUC : `0.671604`

Modele final `OVER` :

- modele : `random_forest_leaf2_sqrt`
- seuil : `0.67`
- features : `59`
- test F1 : `0.696379`
- test precision : `0.827815`
- test recall : `0.600962`
- test PR-AUC : `0.730753`
- test ROC-AUC : `0.855443`

## Fichiers utiles

- `coverage_prediction_report.md`
- `features/all_datasets_refined_test_features.csv`
- `modeling/under_dataset.csv`
- `modeling/over_dataset.csv`
- `models/under_model.pkl`
- `models/over_model.pkl`
- `metrics/under_metrics.csv`
- `metrics/over_metrics.csv`
- `metrics/under_feature_importance.csv`
- `metrics/over_feature_importance.csv`
- `plots/feature_importance/feature_importance_index.html`
- `errors/all_test_misclassified_tests.csv`

## Commandes de reproduction

```bash
.venv/bin/python extension_jsonschemabench/scripts/build_outlines_coverage_prediction.py \
  --framework xgr \
  --datasets Github_trivial Github_easy Github_medium Github_hard Github_ultra \
  --output-root extension_jsonschemabench/coverage_prediction/xgr

.venv/bin/python extension_jsonschemabench/scripts/plot_coverage_feature_importance.py \
  --output-root extension_jsonschemabench/coverage_prediction/xgr

.venv/bin/python extension_jsonschemabench/scripts/export_coverage_misclassifications.py \
  --output-root extension_jsonschemabench/coverage_prediction/xgr
```
