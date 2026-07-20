# Outlines Coverage Prediction Report

## Scope

- Included datasets: `Github_trivial`, `Github_easy`, `Github_medium`, `Github_ultra`
- Skipped datasets: none
- Framework: `outlines`
- Split: grouped by `schema_id` with train/validation/test partitions.
- Candidate models: tuned variants of `LogisticRegression`, `RandomForestClassifier`, `HistGradientBoostingClassifier`, and `LGBMClassifier` when LightGBM is installed.
- Model selection: best validation PR-AUC, then F1, recall, and precision as tie-breakers.
- Decision threshold: selected on validation to maximize F1 for each candidate model.

## Modeling Tables

- UNDER rows: 11176 ({'UNDER': 1242, 'CORRECT_INVALID': 9934})
- OVER rows: 6149 ({'CORRECT_VALID': 4436, 'OVER': 1713})

## Notes

- `dataset` is kept as metadata and is not used as an input feature.
- `Github_hard` can be added later by rerunning the script with it in `--datasets` once its Outlines run is complete.
