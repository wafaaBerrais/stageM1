# Statistical study: Github_trivial / xgr

This folder contains schema-level statistics and SVG plots generated from the dataset run files. Compile time is analyzed once per schema, not once per test, to avoid overweighting schemas that contain many tests.

## Inputs

- `per_test_results.jsonl`: 1211 rows
- `timing_profile.csv`: 1231 rows
- `timed_out_schemas.jsonl`: 5 rows

## Main summary

| metric | value |
| --- | ---: |
| schemas | 365 |
| completed schemas | 360 |
| timeout schemas | 5 |
| schema timeout rate | 1.4% |
| tests | 1231 |
| completed tests | 1211 |
| coverage rate | 98.4% |
| accuracy on completed tests | 89.3% |
| under-constraint rate | 9.3% |
| over-constraint rate | 13.0% |
| median compile_grammar_s | 0.912 |
| p95 compile_grammar_s | 4.19 |
| max compile_grammar_s | 135 |

## Timeout stages

| timeout_stage | schemas |
| --- | ---: |
| compile_grammar | 4 |
| validation | 1 |

Timeout stages are inferred from the timeout log when available, otherwise from partial checkpoints in `timing_profile.csv`.

## Expected validity among timeout tests

| expected_validity | tests | share |
| --- | ---: | ---: |
| valid | 5 | 25.0% |
| invalid | 15 | 75.0% |

## Timing by schema status

| status | phase | n | mean_s | std_s | median_s | p95_s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| completed | compile_grammar_s | 360 | 3.03 | 13.3 | 0.912 | 4.19 |
| completed | validation_loop_mean_s | 360 | 0.00229 | 0.00756 | 0.000256 | 0.00958 |
| completed | compute_mask_mean_s | 360 | 0.00218 | 0.00735 | 0.000221 | 0.00908 |
| completed | commit_token_mean_s | 360 | 4.26e-05 | 0.000125 | 1.58e-05 | 0.00012 |
| timeout | compile_grammar_s | 1 | 7.73 | 0 | 7.73 | 7.73 |
| timeout | compute_mask_mean_s | 1 | 0 | 0 | 0 | 0 |
| timeout | commit_token_mean_s | 1 | 0 | 0 | 0 | 0 |
| timeout | timeout_elapsed_s | 5 | 601 | 0.945 | 600 | 602 |

For timeout schemas, phase values are partial checkpoints when available; `timeout_elapsed_s` is the supervisor elapsed time.

## Feature extraction

Raw structural features are `has_*` indicators for explicit JSON Schema keywords or benchmark categories. `$ref`, `$anchor`, `$dynamicRef`, `$defs`/`definitions`, `if`/`then`/`else`, and content keywords are mapped directly from the schema; `boolean_schema` is detected from boolean schema nodes and the benchmark `_boolSchema` metadata. `infinite-loop-detection` is only read from benchmark metadata when present because it is not a JSON Schema keyword.

Derived indicators (`large_enum`, `many_required`, `many_properties`, `deep_schema`) are kept separate from raw keyword features. Pair rows are generated automatically with `itertools.combinations(BASE_FEATURES, 2)`; a pair is present only when both base features are present in the same schema.

## Features associated with timeout

| feature | schemas | timeout with | timeout without | lift |
| --- | ---: | ---: | ---: | ---: |
| `has_type` | 357 | 1.4% | 0.0% | inf |
| `has_maxLength` | 22 | 13.6% | 0.6% | 23.39 |
| `has_pattern` | 33 | 6.1% | 0.9% | 6.71 |
| `has_boolean_schema` | 112 | 2.7% | 0.8% | 3.39 |
| `has_additionalProperties` | 116 | 2.6% | 0.8% | 3.22 |
| `has_oneOf` | 46 | 2.2% | 1.3% | 1.73 |
| `has_properties` | 265 | 1.1% | 2.0% | 0.57 |
| `has_required` | 140 | 0.7% | 1.8% | 0.40 |
| `has_allOf` | 21 | 0.0% | 1.5% | 0.00 |
| `has_anyOf` | 26 | 0.0% | 1.5% | 0.00 |

## Features associated with under/over-constraint

| feature | schemas | under_rate | over_rate | correct_rate |
| --- | ---: | ---: | ---: | ---: |
| `has_patternProperties` | 22 | 0.0% | 93.9% | 55.7% |
| `has_not` | 7 | 50.0% | 25.0% | 59.1% |
| `has_minProperties` | 3 | 0.0% | 60.0% | 66.7% |
| `has_multipleOf` | 2 | 60.0% | 0.0% | 57.1% |
| `has_maxItems` | 5 | 25.0% | 33.3% | 71.4% |
| `has_allOf` | 21 | 48.5% | 0.0% | 76.1% |
| `has_minItems` | 15 | 29.3% | 15.0% | 75.4% |
| `has_minLength` | 28 | 12.3% | 25.7% | 83.0% |
| `has_oneOf` | 46 | 17.9% | 19.7% | 81.4% |
| `many_required` | 26 | 27.1% | 9.5% | 79.5% |

## Simple feature pairs

| feature_pair | schemas | timeout_rate | under_rate | over_rate |
| --- | ---: | ---: | ---: | ---: |
| `has_additionalProperties__AND__has_maxLength` | 14 | 21.4% | 7.7% | 28.6% |
| `has_boolean_schema__AND__has_maxLength` | 14 | 21.4% | 7.7% | 28.6% |
| `has_maxLength__AND__has_properties` | 18 | 16.7% | 5.0% | 20.0% |
| `has_maxLength__AND__has_oneOf` | 7 | 14.3% | 9.5% | 44.4% |
| `has_maxLength__AND__has_type` | 22 | 13.6% | 3.6% | 16.7% |
| `has_maxLength__AND__has_required` | 10 | 10.0% | 5.3% | 18.2% |
| `has_pattern__AND__has_type` | 33 | 6.1% | 10.8% | 10.5% |
| `has_additionalProperties__AND__has_oneOf` | 21 | 4.8% | 14.5% | 25.8% |
| `has_boolean_schema__AND__has_oneOf` | 22 | 4.5% | 18.5% | 24.2% |
| `has_additionalProperties__AND__has_properties` | 97 | 3.1% | 16.2% | 3.7% |

## Selected pair heatmap candidates

The pair heatmap keeps the most interesting generated pairs. The ranking first requires usable support, then prioritizes the number of signals among timeout/under/over, then capped lift, delta, and support. This avoids filling the plot with rare pairs that only look strong because the denominator is tiny.

| feature_pair | schemas | risk_count | interest_score | timeout_group | under_group | over_group |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `has_additionalProperties__AND__has_oneOf` | 21 | 3 | 3e+06 | 20.0% | 19.4% | 12.2% |
| `has_boolean_schema__AND__has_oneOf` | 22 | 3 | 3e+06 | 20.0% | 22.2% | 12.2% |
| `has_oneOf__AND__has_required` | 37 | 3 | 3e+06 | 20.0% | 30.6% | 12.2% |
| `has_oneOf__AND__has_properties` | 43 | 3 | 3e+06 | 20.0% | 33.3% | 14.6% |
| `has_oneOf__AND__has_type` | 46 | 3 | 3e+06 | 20.0% | 33.3% | 19.5% |
| `has_maxLength__AND__has_properties` | 18 | 2 | 2.03e+06 | 60.0% | 5.6% | 4.9% |
| `has_maxLength__AND__has_type` | 22 | 2 | 2.02e+06 | 60.0% | 5.6% | 4.9% |
| `has_additionalProperties__AND__has_properties` | 97 | 2 | 2e+06 | 60.0% | 50.0% | 7.3% |
| `has_boolean_schema__AND__has_properties` | 98 | 2 | 2e+06 | 60.0% | 50.0% | 7.3% |
| `has_minItems__AND__has_type` | 15 | 2 | 2e+06 | 0.0% | 25.0% | 7.3% |

## Very slow completed schemas and errors

| group | schemas | compile_min_s | compile_max_s | under_rate | over_rate | accuracy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 90 | 0.619 | 0.824 | 8.9% | 24.3% | 85.0% |
| medium | 90 | 0.825 | 0.912 | 7.0% | 13.9% | 90.1% |
| slow | 90 | 0.912 | 1.09 | 5.9% | 7.0% | 93.7% |
| very_slow | 90 | 1.1 | 135 | 13.5% | 7.0% | 88.5% |

## Generated files

- `schema_level_stats.csv`: one row per schema with timing, correctness, timeout status, and JSON Schema features.
- `feature_timeout_lift.csv`: P(timeout | feature), P(timeout | absence), and lift.
- `feature_under_lift.csv`: P(under | feature), P(under | absence), and lift using completed invalid tests.
- `feature_over_lift.csv`: P(over | feature), P(over | absence), and lift using completed valid tests.
- `feature_constraint_rates.csv`: under/over/correct rates for schemas containing each feature.
- `feature_group_heatmap.csv`: feature prevalence for correct, timeout, under, and over schema groups.
- `feature_pair_group_heatmap.csv`: selected pair prevalence for correct, timeout, under, and over schema groups.
- `feature_pair_rates.csv`: automatically generated pairwise rates over all raw base features.
- `feature_pair_timeout_lift.csv`: P(timeout | feature pair), P(timeout | absence), and lift.
- `feature_pair_under_lift.csv`: P(under | feature pair), P(under | absence), and lift using completed invalid tests.
- `feature_pair_over_lift.csv`: P(over | feature pair), P(over | absence), and lift using completed valid tests.
- `slow_completed_constraint_quartiles.csv`: under/over rates by compile-time quartile.
- `timeout_expected_validity.csv`: valid vs invalid expected tests among timeout schemas.
- `phase_timing_summary_by_status.csv`: mean/std timing by phase for completed and timeout schemas.
- `timing_by_result_case.csv`: per-test timing classified as correct_accept, correct_reject, under, over, or no_decision.
- `schema_characteristic_constraint_bins.csv`: non-feature schema characteristics binned by quartile with under/over rates.
- SVG plots: open directly from this folder.

## Plots to inspect first

- `schema_size_vs_compile.svg` and `schema_depth_vs_compile.svg` for the size/depth relationship.
- `feature_timeout_lift.svg`, `feature_under_lift.svg`, and `feature_over_lift.svg` for single-feature lift signals.
- `feature_under_over_rates.svg` and `feature_group_heatmap.svg` for isolated feature errors.
- `feature_pair_timeout_lift.svg`, `feature_pair_under_lift.svg`, and `feature_pair_over_lift.svg` for pairwise lift signals.
- `feature_pair_group_heatmap.svg` for the most interesting generated pairwise combinations.
- `phase_time_share_top_schemas.svg` to verify whether compile time dominates the slow completed schemas.
- `timeout_expected_validity_share.svg` for the valid/invalid mix inside timeout schemas.
- `compile_time_by_result_case_boxplot.svg` and `validation_time_by_result_case_boxplot.svg` for timing by result type.
- `schema_size_vs_*_constraint_group.svg` and `schema_size_quartiles_under_over_rates.svg` for schema size/complexity vs under/over.
