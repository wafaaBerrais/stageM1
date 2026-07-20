# Statistical study: Github_easy / xgr

This folder contains schema-level statistics and SVG plots generated from the dataset run files. Compile time is analyzed once per schema, not once per test, to avoid overweighting schemas that contain many tests.

## Inputs

- `per_test_results.jsonl`: 7131 rows
- `timing_profile.csv`: 7252 rows
- `timed_out_schemas.jsonl`: 24 rows

## Main summary

| metric | value |
| --- | ---: |
| schemas | 1789 |
| completed schemas | 1765 |
| timeout schemas | 24 |
| schema timeout rate | 1.3% |
| tests | 7252 |
| completed tests | 7131 |
| coverage rate | 98.3% |
| accuracy on completed tests | 87.6% |
| under-constraint rate | 13.4% |
| over-constraint rate | 10.7% |
| median compile_grammar_s | 1.09 |
| p95 compile_grammar_s | 6.55 |
| max compile_grammar_s | 597 |

## Timeout stages

| timeout_stage | schemas |
| --- | ---: |
| compile_grammar | 24 |

Timeout stages are inferred from the timeout log when available, otherwise from partial checkpoints in `timing_profile.csv`.

## Expected validity among timeout tests

| expected_validity | tests | share |
| --- | ---: | ---: |
| valid | 40 | 33.1% |
| invalid | 81 | 66.9% |

## Timing by schema status

| status | phase | n | mean_s | std_s | median_s | p95_s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| completed | compile_grammar_s | 1765 | 5.12 | 34.3 | 1.09 | 6.55 |
| completed | validation_loop_mean_s | 1757 | 0.0148 | 0.35 | 0.000766 | 0.0123 |
| completed | compute_mask_mean_s | 1757 | 0.0147 | 0.349 | 0.000668 | 0.0121 |
| completed | commit_token_mean_s | 1757 | 6.26e-05 | 0.00116 | 2.2e-05 | 8.15e-05 |
| timeout | compile_grammar_s | 4 | 600 | 0 | 600 | 600 |
| timeout | timeout_elapsed_s | 24 | 600 | 0 | 600 | 600 |

For timeout schemas, phase values are partial checkpoints when available; `timeout_elapsed_s` is the supervisor elapsed time.

## Feature extraction

Raw structural features are `has_*` indicators for explicit JSON Schema keywords or benchmark categories. `$ref`, `$anchor`, `$dynamicRef`, `$defs`/`definitions`, `if`/`then`/`else`, and content keywords are mapped directly from the schema; `boolean_schema` is detected from boolean schema nodes and the benchmark `_boolSchema` metadata. `infinite-loop-detection` is only read from benchmark metadata when present because it is not a JSON Schema keyword.

Derived indicators (`large_enum`, `many_required`, `many_properties`, `deep_schema`) are kept separate from raw keyword features. Pair rows are generated automatically with `itertools.combinations(BASE_FEATURES, 2)`; a pair is present only when both base features are present in the same schema.

## Features associated with timeout

| feature | schemas | timeout with | timeout without | lift |
| --- | ---: | ---: | ---: | ---: |
| `has_maxLength` | 154 | 15.6% | 0.0% | inf |
| `has_properties` | 1773 | 1.4% | 0.0% | inf |
| `has_type` | 1787 | 1.3% | 0.0% | inf |
| `has_minLength` | 196 | 11.2% | 0.1% | 89.40 |
| `has_boolean_schema` | 788 | 2.7% | 0.3% | 8.89 |
| `has_additionalProperties` | 810 | 2.6% | 0.3% | 8.46 |
| `has_oneOf` | 75 | 8.0% | 1.1% | 7.62 |
| `has_patternProperties` | 44 | 4.5% | 1.3% | 3.61 |
| `has_enum` | 419 | 2.9% | 0.9% | 3.27 |
| `has_maxItems` | 36 | 2.8% | 1.3% | 2.12 |

## Features associated with under/over-constraint

| feature | schemas | under_rate | over_rate | correct_rate |
| --- | ---: | ---: | ---: | ---: |
| `has_patternProperties` | 44 | 13.3% | 83.8% | 57.8% |
| `has_allOf` | 22 | 70.9% | 15.2% | 45.5% |
| `has_minProperties` | 21 | 29.6% | 40.6% | 66.3% |
| `has_maxItems` | 36 | 36.4% | 26.0% | 66.5% |
| `has_not` | 5 | 22.2% | 37.5% | 73.1% |
| `has_multipleOf` | 10 | 57.1% | 0.0% | 62.8% |
| `has_minItems` | 114 | 38.4% | 16.9% | 68.2% |
| `has_if_then_else` | 1 | 50.0% | 0.0% | 66.7% |
| `deep_schema` | 51 | 24.2% | 24.7% | 75.6% |
| `has_oneOf` | 75 | 27.6% | 20.4% | 75.0% |

## Simple feature pairs

| feature_pair | schemas | timeout_rate | under_rate | over_rate |
| --- | ---: | ---: | ---: | ---: |
| `has_maxLength__AND__has_oneOf` | 15 | 40.0% | 22.6% | 30.8% |
| `has_maximum__AND__has_minLength` | 5 | 40.0% | 33.3% | 0.0% |
| `has_maxLength__AND__has_maximum` | 6 | 33.3% | 47.8% | 0.0% |
| `has_maxLength__AND__has_patternProperties` | 7 | 28.6% | 28.6% | 66.7% |
| `has_minLength__AND__has_oneOf` | 19 | 26.3% | 13.6% | 26.3% |
| `has_enum__AND__has_maxLength` | 48 | 25.0% | 19.4% | 17.3% |
| `has_minLength__AND__has_patternProperties` | 8 | 25.0% | 23.5% | 72.7% |
| `has_enum__AND__has_minLength` | 47 | 23.4% | 12.9% | 16.0% |
| `has_maxLength__AND__has_minimum` | 14 | 21.4% | 14.5% | 0.0% |
| `has_maxLength__AND__has_minLength` | 103 | 21.4% | 16.8% | 12.4% |

## Selected pair heatmap candidates

The pair heatmap keeps the most interesting generated pairs. The ranking first requires usable support, then prioritizes the number of signals among timeout/under/over, then capped lift, delta, and support. This avoids filling the plot with rare pairs that only look strong because the denominator is tiny.

| feature_pair | schemas | risk_count | interest_score | timeout_group | under_group | over_group |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `has_enum__AND__has_maxLength` | 48 | 3 | 3.04e+06 | 50.0% | 4.5% | 2.7% |
| `has_items__AND__has_maxLength` | 30 | 3 | 3.02e+06 | 20.8% | 3.0% | 1.6% |
| `has_boolean_schema__AND__has_oneOf` | 44 | 3 | 3.01e+06 | 25.0% | 4.1% | 5.9% |
| `has_additionalProperties__AND__has_oneOf` | 46 | 3 | 3.01e+06 | 25.0% | 4.5% | 5.9% |
| `has_maxLength__AND__has_pattern` | 39 | 3 | 3.01e+06 | 16.7% | 4.8% | 2.7% |
| `has_additionalProperties__AND__has_patternProperties` | 32 | 3 | 3.01e+06 | 8.3% | 1.9% | 13.0% |
| `has_boolean_schema__AND__has_patternProperties` | 32 | 3 | 3.01e+06 | 8.3% | 1.9% | 13.0% |
| `has_items__AND__has_minLength` | 53 | 3 | 3.01e+06 | 20.8% | 4.5% | 2.7% |
| `has_minLength__AND__has_pattern` | 43 | 3 | 3.01e+06 | 16.7% | 4.1% | 2.7% |
| `has_items__AND__has_oneOf` | 32 | 3 | 3.01e+06 | 12.5% | 3.0% | 3.8% |

## Very slow completed schemas and errors

| group | schemas | compile_min_s | compile_max_s | under_rate | over_rate | accuracy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 442 | 3.8e-05 | 0.891 | 15.2% | 16.4% | 84.3% |
| medium | 441 | 0.892 | 1.09 | 12.6% | 8.7% | 89.0% |
| slow | 441 | 1.09 | 1.42 | 14.6% | 7.2% | 88.1% |
| very_slow | 441 | 1.43 | 597 | 11.8% | 11.0% | 88.4% |

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
