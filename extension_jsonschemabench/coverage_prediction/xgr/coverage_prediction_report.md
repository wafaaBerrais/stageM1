# xgr Coverage Prediction Report

## Scope

- Included datasets: `Github_trivial`, `Github_easy`, `Github_medium`, `Github_hard`, `Github_ultra`
- Skipped datasets: none
- Framework: `xgr`
- Split: grouped by `schema_id` with train/validation/test partitions.
- Candidate models: tuned variants of `LogisticRegression`, `RandomForestClassifier`, `HistGradientBoostingClassifier`, and `LGBMClassifier` when LightGBM is installed.
- Model selection: best validation PR-AUC, then F1, recall, and precision as tie-breakers.
- Decision threshold: selected on validation to maximize F1 for each candidate model.
- Trained targets: `under`, `over`

## Modeling Tables

- UNDER rows: 14169 ({'CORRECT_INVALID': 12010, 'UNDER': 2159})
- OVER rows: 7529 ({'CORRECT_VALID': 6061, 'OVER': 1468})

## Notes

- `dataset` is kept as metadata and is not used as an input feature.
- A target is skipped when it has only one class, because binary classifiers cannot be trained meaningfully.
