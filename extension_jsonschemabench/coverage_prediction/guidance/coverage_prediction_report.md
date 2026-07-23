# guidance Coverage Prediction Report

## Scope

- Included datasets: `Github_trivial`, `Github_easy`, `Github_medium`, `Github_hard`, `Github_ultra`
- Skipped datasets: none
- Framework: `guidance`
- Split: grouped by `schema_id` with train/validation/test partitions.
- Candidate models: tuned variants of `LogisticRegression`, `RandomForestClassifier`, `HistGradientBoostingClassifier`, and `LGBMClassifier` when LightGBM is installed.
- Model selection: best validation PR-AUC, then F1, recall, and precision as tie-breakers.
- Decision threshold: selected on validation to maximize F1 for each candidate model.
- Trained targets: `over`

## Modeling Tables

- UNDER rows: 15208 ({'CORRECT_INVALID': 15208})
- OVER rows: 7845 ({'OVER': 4811, 'CORRECT_VALID': 3034})

## Notes

- `dataset` is kept as metadata and is not used as an input feature.
- A target is skipped when it has only one class, because binary classifiers cannot be trained meaningfully.
