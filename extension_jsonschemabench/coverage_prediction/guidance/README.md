# Prediction de coverage Guidance

Ce dossier contient le travail de prediction des erreurs de coverage pour le framework `guidance`.

Les resultats guidance sont stockes dans les runs avec l'alias interne `llg`; le script de prediction accepte maintenant cet alias.

Les deux problemes possibles sont :

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

- `UNDER` : 15208 lignes
  - positifs `UNDER` : 0
  - negatifs `CORRECT_INVALID` : 15208
  - modele non entraine, car il n'y a qu'une seule classe.

- `OVER` : 7845 lignes
  - positifs `OVER` : 4811
  - negatifs `CORRECT_VALID` : 3034

## Modeles retenus

Modele final `UNDER` :

- non entraine : aucun positif `UNDER` dans la data globale guidance.

Modele final `OVER` :

- modele : `random_forest_leaf2_sqrt`
- seuil : `0.33`
- features : `59`
- test F1 : `0.744491`
- test precision : `0.635809`
- test recall : `0.897989`
- test PR-AUC : `0.798214`
- test ROC-AUC : `0.715741`

## Fichiers utiles

- `coverage_prediction_report.md`
- `features/all_datasets_refined_test_features.csv`
- `modeling/under_dataset.csv`
- `modeling/over_dataset.csv`
- `models/over_model.pkl`
- `metrics/under_metrics.csv`
- `metrics/over_metrics.csv`
- `metrics/over_feature_importance.csv`
- `plots/feature_importance/feature_importance_index.html`
- `errors/all_test_misclassified_tests.csv`

## Commandes de reproduction

```bash
.venv/bin/python extension_jsonschemabench/scripts/build_outlines_coverage_prediction.py \
  --framework guidance \
  --datasets Github_trivial Github_easy Github_medium Github_hard Github_ultra \
  --output-root extension_jsonschemabench/coverage_prediction/guidance

.venv/bin/python extension_jsonschemabench/scripts/plot_coverage_feature_importance.py \
  --output-root extension_jsonschemabench/coverage_prediction/guidance

.venv/bin/python extension_jsonschemabench/scripts/export_coverage_misclassifications.py \
  --output-root extension_jsonschemabench/coverage_prediction/guidance
```
