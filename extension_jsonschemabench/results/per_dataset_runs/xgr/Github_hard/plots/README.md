# Statistical study: Github_hard / xgr

This folder contains schema-level statistics and SVG plots generated from the dataset run files. Compile time is analyzed once per schema, not once per test, to avoid overweighting schemas that contain many tests.

## Inputs

- `per_test_results.jsonl`: 4517 rows
- `timing_profile.csv`: 4898 rows
- `timed_out_schemas.jsonl`: 51 rows

## Main summary

| metric | value |
| --- | ---: |
| schemas | 888 |
| completed schemas | 837 |
| timeout schemas | 51 |
| schema timeout rate | 5.7% |
| tests | 4894 |
| completed tests | 4517 |
| coverage rate | 92.3% |
| accuracy on completed tests | 80.7% |
| under-constraint rate | 14.1% |
| over-constraint rate | 30.7% |
| median compile_grammar_s | 5.98 |
| p95 compile_grammar_s | 23.5 |
| max compile_grammar_s | 411 |

## Timeout stages

| timeout_stage | schemas |
| --- | ---: |
| compile_grammar | 31 |
| terminated_signal_15 | 12 |
| validation | 7 |
| terminated_signal_11 | 1 |

Timeout stages are inferred from the timeout log when available, otherwise from partial checkpoints in `timing_profile.csv`.

## Expected validity among timeout tests

| expected_validity | tests | share |
| --- | ---: | ---: |
| valid | 89 | 23.5% |
| invalid | 290 | 76.5% |

## Timing by schema status

| status | phase | n | mean_s | std_s | median_s | p95_s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| completed | compile_grammar_s | 837 | 10.1 | 22.5 | 5.98 | 23.5 |
| completed | validation_loop_mean_s | 829 | 0.101 | 0.918 | 0.00527 | 0.0878 |
| completed | compute_mask_mean_s | 829 | 0.0996 | 0.913 | 0.00487 | 0.0867 |
| completed | commit_token_mean_s | 829 | 0.000619 | 0.00825 | 9.45e-05 | 0.000692 |
| timeout | compile_grammar_s | 8 | 43.5 | 28.2 | 51.9 | 74.7 |
| timeout | validation_loop_mean_s | 7 | 479 | 129 | 520 | 553 |
| timeout | compute_mask_mean_s | 8 | 415 | 204 | 516 | 535 |
| timeout | commit_token_mean_s | 8 | 4.21 | 11.8 | 0.024 | 21.8 |
| timeout | timeout_elapsed_s | 51 | 534 | 125 | 600 | 600 |

For timeout schemas, phase values are partial checkpoints when available; `timeout_elapsed_s` is the supervisor elapsed time.

## Feature extraction

Raw structural features are `has_*` indicators for explicit JSON Schema keywords or benchmark categories. `$ref`, `$anchor`, `$dynamicRef`, `$defs`/`definitions`, `if`/`then`/`else`, and content keywords are mapped directly from the schema; `boolean_schema` is detected from boolean schema nodes and the benchmark `_boolSchema` metadata. `infinite-loop-detection` is only read from benchmark metadata when present because it is not a JSON Schema keyword.

Derived indicators (`large_enum`, `many_required`, `many_properties`, `deep_schema`) are kept separate from raw keyword features. Pair rows are generated automatically with `itertools.combinations(BASE_FEATURES, 2)`; a pair is present only when both base features are present in the same schema.

## Features associated with timeout

| feature | schemas | timeout with | timeout without | lift |
| --- | ---: | ---: | ---: | ---: |
| `many_properties` | 886 | 5.8% | 0.0% | inf |
| `has_properties` | 888 | 5.7% | 0.0% | inf |
| `has_type` | 888 | 5.7% | 0.0% | inf |
| `has_maxLength` | 97 | 39.2% | 1.6% | 23.84 |
| `has_minLength` | 140 | 25.0% | 2.1% | 11.69 |
| `has_maxItems` | 69 | 34.8% | 3.3% | 10.55 |
| `has_pattern` | 340 | 12.6% | 1.5% | 8.66 |
| `has_maximum` | 135 | 17.8% | 3.6% | 4.96 |
| `has_boolean_schema` | 502 | 8.4% | 2.3% | 3.59 |
| `has_minimum` | 218 | 12.4% | 3.6% | 3.46 |

## Features associated with under/over-constraint

| feature | schemas | under_rate | over_rate | correct_rate |
| --- | ---: | ---: | ---: | ---: |
| `has_if_then_else` | 5 | 26.7% | 85.7% | 62.2% |
| `has_patternProperties` | 122 | 9.3% | 87.5% | 67.4% |
| `has_exclusiveMinimum` | 5 | 0.0% | 87.5% | 75.9% |
| `has_const` | 10 | 26.7% | 56.2% | 67.1% |
| `has_not` | 17 | 34.4% | 48.0% | 62.7% |
| `has_propertyNames` | 8 | 28.9% | 50.0% | 66.7% |
| `has_multipleOf` | 12 | 28.8% | 45.0% | 66.7% |
| `has_allOf` | 53 | 26.3% | 42.9% | 69.5% |
| `has_minProperties` | 24 | 13.6% | 52.5% | 76.6% |
| `has_maximum` | 135 | 20.0% | 45.8% | 73.4% |

## Simple feature pairs

| feature_pair | schemas | timeout_rate | under_rate | over_rate |
| --- | ---: | ---: | ---: | ---: |
| `has_maxItems__AND__has_minLength` | 30 | 73.3% | 27.5% | 35.3% |
| `has_maxItems__AND__has_patternProperties` | 16 | 56.2% | 4.8% | 70.0% |
| `has_maxItems__AND__has_maxLength` | 41 | 56.1% | 38.7% | 22.2% |
| `has_maxItems__AND__has_pattern` | 42 | 54.8% | 15.6% | 31.2% |
| `has_maxLength__AND__has_oneOf` | 21 | 52.4% | 21.1% | 70.6% |
| `has_maxLength__AND__has_patternProperties` | 23 | 52.2% | 34.5% | 71.4% |
| `has_maxLength__AND__has_minLength` | 70 | 48.6% | 16.7% | 50.0% |
| `has_maxLength__AND__has_pattern` | 67 | 46.3% | 19.7% | 49.2% |
| `has_maximum__AND__has_minLength` | 51 | 45.1% | 8.9% | 73.3% |
| `has_maxItems__AND__has_maximum` | 37 | 43.2% | 34.4% | 26.3% |

## Selected pair heatmap candidates

The pair heatmap keeps the most interesting generated pairs. The ranking first requires usable support, then prioritizes the number of signals among timeout/under/over, then capped lift, delta, and support. This avoids filling the plot with rare pairs that only look strong because the denominator is tiny.

| feature_pair | schemas | risk_count | interest_score | timeout_group | under_group | over_group |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `has_properties__AND__has_type` | 888 | 3 | 3.05e+06 | 100.0% | 100.0% | 100.0% |
| `has_maxLength__AND__has_properties` | 97 | 3 | 3.02e+06 | 74.5% | 12.5% | 8.6% |
| `has_maxLength__AND__has_type` | 97 | 3 | 3.02e+06 | 74.5% | 12.5% | 8.6% |
| `has_maxLength__AND__has_minLength` | 70 | 3 | 3.02e+06 | 66.7% | 5.6% | 6.7% |
| `has_enum__AND__has_maxLength` | 84 | 3 | 3.02e+06 | 66.7% | 11.1% | 6.7% |
| `has_maxLength__AND__has_pattern` | 67 | 3 | 3.02e+06 | 60.8% | 5.6% | 6.7% |
| `has_items__AND__has_maxLength` | 82 | 3 | 3.02e+06 | 64.7% | 11.6% | 6.7% |
| `has_maxLength__AND__has_required` | 92 | 3 | 3.02e+06 | 66.7% | 12.0% | 8.6% |
| `has_boolean_schema__AND__has_maxLength` | 75 | 3 | 3.02e+06 | 60.8% | 9.3% | 6.4% |
| `has_additionalProperties__AND__has_maxLength` | 77 | 3 | 3.02e+06 | 60.8% | 9.3% | 7.1% |

## Very slow completed schemas and errors

| group | schemas | compile_min_s | compile_max_s | under_rate | over_rate | accuracy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 210 | 0.000902 | 3.7 | 13.4% | 49.2% | 73.4% |
| medium | 209 | 3.71 | 5.98 | 13.6% | 27.4% | 82.5% |
| slow | 209 | 6 | 10.9 | 13.9% | 23.1% | 83.4% |
| very_slow | 209 | 10.9 | 411 | 15.6% | 22.5% | 82.2% |

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
