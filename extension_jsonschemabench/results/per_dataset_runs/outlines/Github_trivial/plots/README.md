# Statistical study: Github_trivial / outlines

This folder contains schema-level statistics and SVG plots generated from the dataset run files. Compile time is analyzed once per schema, not once per test, to avoid overweighting schemas that contain many tests.

## Inputs

- `per_test_results.jsonl`: 1207 rows
- `timing_profile.csv`: 1231 rows
- `timed_out_schemas.jsonl`: 6 rows

## Main summary

| metric | value |
| --- | ---: |
| schemas | 365 |
| completed schemas | 359 |
| timeout schemas | 6 |
| schema timeout rate | 1.6% |
| tests | 1231 |
| completed tests | 1207 |
| coverage rate | 98.1% |
| accuracy on completed tests | 86.3% |
| under-constraint rate | 6.2% |
| over-constraint rate | 26.0% |
| median compile_grammar_s | 0.25 |
| p95 compile_grammar_s | 27.1 |
| max compile_grammar_s | 404 |

## Timeout stages

| timeout_stage | schemas |
| --- | ---: |
| building_index | 6 |

Timeout stages are inferred from the timeout log when available, otherwise from partial checkpoints in `timing_profile.csv`.

## Expected validity among timeout tests

| expected_validity | tests | share |
| --- | ---: | ---: |
| valid | 7 | 29.2% |
| invalid | 17 | 70.8% |

## Timing by schema status

| status | phase | n | mean_s | std_s | median_s | p95_s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| completed | compile_grammar_s | 359 | 8.51 | 40.8 | 0.25 | 27.1 |
| completed | validation_loop_mean_s | 328 | 0.024 | 0.0497 | 0.00816 | 0.0921 |
| completed | compute_mask_mean_s | 328 | 0.0106 | 0.0222 | 0.00357 | 0.0415 |
| completed | commit_token_mean_s | 328 | 0.0134 | 0.0275 | 0.00445 | 0.0507 |
| timeout | timeout_elapsed_s | 6 | 601 | 0.47 | 601 | 601 |

For timeout schemas, phase values are partial checkpoints when available; `timeout_elapsed_s` is the supervisor elapsed time.

## Feature extraction

Raw structural features are `has_*` indicators for explicit JSON Schema keywords or benchmark categories. `$ref`, `$anchor`, `$dynamicRef`, `$defs`/`definitions`, `if`/`then`/`else`, and content keywords are mapped directly from the schema; `boolean_schema` is detected from boolean schema nodes and the benchmark `_boolSchema` metadata. `infinite-loop-detection` is only read from benchmark metadata when present because it is not a JSON Schema keyword.

Derived indicators (`large_enum`, `many_required`, `many_properties`, `deep_schema`) are kept separate from raw keyword features. Pair rows are generated automatically with `itertools.combinations(BASE_FEATURES, 2)`; a pair is present only when both base features are present in the same schema.

## Features associated with timeout

| feature | schemas | timeout with | timeout without | lift |
| --- | ---: | ---: | ---: | ---: |
| `has_type` | 357 | 1.7% | 0.0% | inf |
| `has_maxLength` | 22 | 22.7% | 0.3% | 77.95 |
| `has_maxItems` | 5 | 20.0% | 1.4% | 14.40 |
| `has_ref` | 10 | 10.0% | 1.4% | 7.10 |
| `has_minItems` | 15 | 6.7% | 1.4% | 4.67 |
| `has_boolean_schema` | 112 | 3.6% | 0.8% | 4.52 |
| `has_additionalProperties` | 116 | 3.4% | 0.8% | 4.29 |
| `has_anyOf` | 26 | 3.8% | 1.5% | 2.61 |
| `many_required` | 26 | 3.8% | 1.5% | 2.61 |
| `has_minLength` | 28 | 3.6% | 1.5% | 2.41 |

## Features associated with under/over-constraint

| feature | schemas | under_rate | over_rate | correct_rate |
| --- | ---: | ---: | ---: | ---: |
| `has_patternProperties` | 22 | 18.9% | 69.7% | 57.1% |
| `has_allOf` | 21 | 9.1% | 79.4% | 55.2% |
| `has_multipleOf` | 2 | 80.0% | 0.0% | 42.9% |
| `has_maximum` | 8 | 50.0% | 25.0% | 55.6% |
| `has_defs` | 33 | 7.1% | 64.6% | 62.2% |
| `deep_schema` | 29 | 2.5% | 65.3% | 62.9% |
| `has_minimum` | 21 | 36.1% | 29.2% | 65.9% |
| `many_properties` | 29 | 2.0% | 59.6% | 70.4% |
| `has_minProperties` | 3 | 0.0% | 60.0% | 66.7% |
| `large_enum` | 29 | 0.0% | 54.5% | 73.3% |

## Simple feature pairs

| feature_pair | schemas | timeout_rate | under_rate | over_rate |
| --- | ---: | ---: | ---: | ---: |
| `has_anyOf__AND__has_maxItems` | 1 | 100.0% | 0.0% | 0.0% |
| `has_defs__AND__has_minItems` | 1 | 100.0% | 0.0% | 0.0% |
| `has_maxItems__AND__has_ref` | 1 | 100.0% | 0.0% | 0.0% |
| `has_minItems__AND__has_ref` | 1 | 100.0% | 0.0% | 0.0% |
| `has_additionalProperties__AND__has_maxItems` | 2 | 50.0% | 0.0% | 100.0% |
| `has_anyOf__AND__has_minItems` | 2 | 50.0% | 0.0% | 0.0% |
| `has_boolean_schema__AND__has_maxItems` | 2 | 50.0% | 0.0% | 100.0% |
| `has_defs__AND__has_maxItems` | 2 | 50.0% | 0.0% | 100.0% |
| `has_items__AND__has_ref` | 2 | 50.0% | 0.0% | 0.0% |
| `has_additionalProperties__AND__has_ref` | 3 | 33.3% | 0.0% | 0.0% |

## Selected pair heatmap candidates

The pair heatmap keeps the most interesting generated pairs. The ranking first requires usable support, then prioritizes the number of signals among timeout/under/over, then capped lift, delta, and support. This avoids filling the plot with rare pairs that only look strong because the denominator is tiny.

| feature_pair | schemas | risk_count | interest_score | timeout_group | under_group | over_group |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `has_maxLength__AND__has_type` | 22 | 3 | 3.05e+06 | 83.3% | 7.7% | 7.4% |
| `has_maxLength__AND__has_properties` | 18 | 3 | 3.02e+06 | 50.0% | 7.7% | 4.9% |
| `has_additionalProperties__AND__has_properties` | 97 | 3 | 3.01e+06 | 66.7% | 30.8% | 37.0% |
| `has_boolean_schema__AND__has_properties` | 98 | 3 | 3.01e+06 | 66.7% | 30.8% | 35.8% |
| `has_additionalProperties__AND__has_boolean_schema` | 109 | 3 | 3e+06 | 66.7% | 30.8% | 45.7% |
| `has_boolean_schema__AND__has_type` | 111 | 3 | 3e+06 | 66.7% | 30.8% | 45.7% |
| `has_boolean_schema__AND__has_oneOf` | 22 | 3 | 3e+06 | 16.7% | 11.5% | 7.4% |
| `has_additionalProperties__AND__has_items` | 27 | 3 | 3e+06 | 16.7% | 7.7% | 18.5% |
| `has_boolean_schema__AND__has_items` | 28 | 3 | 3e+06 | 16.7% | 7.7% | 18.5% |
| `has_additionalProperties__AND__has_required` | 60 | 3 | 3e+06 | 33.3% | 23.1% | 22.2% |

## Very slow completed schemas and errors

| group | schemas | compile_min_s | compile_max_s | under_rate | over_rate | accuracy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 90 | 0.0281 | 0.155 | 1.3% | 68.6% | 69.5% |
| medium | 90 | 0.157 | 0.25 | 6.3% | 9.7% | 92.5% |
| slow | 89 | 0.252 | 0.488 | 4.2% | 5.4% | 95.3% |
| very_slow | 90 | 0.49 | 404 | 11.4% | 17.5% | 86.5% |

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
