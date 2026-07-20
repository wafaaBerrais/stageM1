# Statistical study: Github_ultra / outlines

This folder contains schema-level statistics and SVG plots generated from the dataset run files. Compile time is analyzed once per schema, not once per test, to avoid overweighting schemas that contain many tests.

## Inputs

- `per_test_results.jsonl`: 452 rows
- `timing_profile.csv`: 462 rows
- `timed_out_schemas.jsonl`: 3 rows

## Main summary

| metric | value |
| --- | ---: |
| schemas | 95 |
| completed schemas | 92 |
| timeout schemas | 3 |
| schema timeout rate | 3.2% |
| tests | 462 |
| completed tests | 452 |
| coverage rate | 97.8% |
| accuracy on completed tests | 72.1% |
| under-constraint rate | 2.0% |
| over-constraint rate | 76.9% |
| median compile_grammar_s | 2.19 |
| p95 compile_grammar_s | 382 |
| max compile_grammar_s | 538 |

## Timeout stages

| timeout_stage | schemas |
| --- | ---: |
| building_index | 3 |

Timeout stages are inferred from the timeout log when available, otherwise from partial checkpoints in `timing_profile.csv`.

## Expected validity among timeout tests

| expected_validity | tests | share |
| --- | ---: | ---: |
| valid | 4 | 40.0% |
| invalid | 6 | 60.0% |

## Timing by schema status

| status | phase | n | mean_s | std_s | median_s | p95_s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| completed | compile_grammar_s | 92 | 91.3 | 140 | 2.19 | 382 |
| completed | validation_loop_mean_s | 32 | 0.571 | 0.585 | 0.242 | 1.52 |
| completed | compute_mask_mean_s | 32 | 0.261 | 0.269 | 0.11 | 0.697 |
| completed | commit_token_mean_s | 32 | 0.309 | 0.316 | 0.13 | 0.816 |
| timeout | timeout_elapsed_s | 3 | 601 | 0.487 | 600 | 601 |

For timeout schemas, phase values are partial checkpoints when available; `timeout_elapsed_s` is the supervisor elapsed time.

## Feature extraction

Raw structural features are `has_*` indicators for explicit JSON Schema keywords or benchmark categories. `$ref`, `$anchor`, `$dynamicRef`, `$defs`/`definitions`, `if`/`then`/`else`, and content keywords are mapped directly from the schema; `boolean_schema` is detected from boolean schema nodes and the benchmark `_boolSchema` metadata. `infinite-loop-detection` is only read from benchmark metadata when present because it is not a JSON Schema keyword.

Derived indicators (`large_enum`, `many_required`, `many_properties`, `deep_schema`) are kept separate from raw keyword features. Pair rows are generated automatically with `itertools.combinations(BASE_FEATURES, 2)`; a pair is present only when both base features are present in the same schema.

## Features associated with timeout

| feature | schemas | timeout with | timeout without | lift |
| --- | ---: | ---: | ---: | ---: |
| `large_enum` | 59 | 5.1% | 0.0% | inf |
| `has_enum` | 72 | 4.2% | 0.0% | inf |
| `deep_schema` | 74 | 4.1% | 0.0% | inf |
| `many_required` | 82 | 3.7% | 0.0% | inf |
| `has_required` | 85 | 3.5% | 0.0% | inf |
| `has_items` | 90 | 3.3% | 0.0% | inf |
| `has_properties` | 95 | 3.2% | 0.0% | inf |
| `has_type` | 95 | 3.2% | 0.0% | inf |
| `many_properties` | 95 | 3.2% | 0.0% | inf |
| `has_maximum` | 19 | 10.5% | 1.3% | 8.00 |

## Features associated with under/over-constraint

| feature | schemas | under_rate | over_rate | correct_rate |
| --- | ---: | ---: | ---: | ---: |
| `has_maxProperties` | 8 | 0.0% | 100.0% | 72.5% |
| `has_minProperties` | 8 | 0.0% | 100.0% | 72.5% |
| `has_patternProperties` | 7 | 0.0% | 100.0% | 74.4% |
| `has_exclusiveMaximum` | 3 | 0.0% | 100.0% | 73.7% |
| `has_anyOf` | 34 | 0.8% | 94.3% | 72.0% |
| `has_ref` | 66 | 0.4% | 92.5% | 70.2% |
| `has_defs` | 68 | 0.4% | 90.8% | 70.4% |
| `has_allOf` | 11 | 1.9% | 88.2% | 77.1% |
| `has_oneOf` | 26 | 2.2% | 87.8% | 70.8% |
| `has_default` | 39 | 0.0% | 89.2% | 68.1% |

## Simple feature pairs

| feature_pair | schemas | timeout_rate | under_rate | over_rate |
| --- | ---: | ---: | ---: | ---: |
| `has_default__AND__has_maxItems` | 1 | 100.0% | 0.0% | 0.0% |
| `has_default__AND__has_maximum` | 4 | 50.0% | 0.0% | 100.0% |
| `has_default__AND__has_oneOf` | 3 | 33.3% | 0.0% | 100.0% |
| `has_default__AND__has_minItems` | 8 | 25.0% | 0.0% | 80.0% |
| `has_maximum__AND__has_minItems` | 10 | 20.0% | 0.0% | 72.7% |
| `has_maxItems__AND__has_maximum` | 5 | 20.0% | 0.0% | 100.0% |
| `has_maxItems__AND__has_oneOf` | 5 | 20.0% | 7.1% | 66.7% |
| `has_default__AND__has_minimum` | 11 | 18.2% | 0.0% | 100.0% |
| `has_default__AND__has_pattern` | 7 | 14.3% | 0.0% | 80.0% |
| `has_maximum__AND__has_required` | 16 | 12.5% | 0.0% | 85.0% |

## Selected pair heatmap candidates

The pair heatmap keeps the most interesting generated pairs. The ranking first requires usable support, then prioritizes the number of signals among timeout/under/over, then capped lift, delta, and support. This avoids filling the plot with rare pairs that only look strong because the denominator is tiny.

| feature_pair | schemas | risk_count | interest_score | timeout_group | under_group | over_group |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `has_properties__AND__has_type` | 95 | 3 | 3.05e+06 | 100.0% | 100.0% | 100.0% |
| `has_minimum__AND__has_properties` | 33 | 3 | 3e+06 | 66.7% | 50.0% | 37.5% |
| `has_minimum__AND__has_type` | 33 | 3 | 3e+06 | 66.7% | 50.0% | 37.5% |
| `has_items__AND__has_properties` | 90 | 2 | 2.05e+06 | 100.0% | 75.0% | 98.6% |
| `has_items__AND__has_type` | 90 | 2 | 2.05e+06 | 100.0% | 75.0% | 98.6% |
| `has_enum__AND__has_items` | 70 | 2 | 2.05e+06 | 100.0% | 75.0% | 83.3% |
| `has_enum__AND__has_properties` | 72 | 2 | 2.05e+06 | 100.0% | 75.0% | 83.3% |
| `has_enum__AND__has_type` | 72 | 2 | 2.05e+06 | 100.0% | 75.0% | 83.3% |
| `has_enum__AND__has_required` | 66 | 2 | 2.05e+06 | 100.0% | 50.0% | 76.4% |
| `has_items__AND__has_required` | 82 | 2 | 2.05e+06 | 100.0% | 50.0% | 90.3% |

## Very slow completed schemas and errors

| group | schemas | compile_min_s | compile_max_s | under_rate | over_rate | accuracy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 23 | 0.0302 | 0.0601 | 0.0% | 100.0% | 68.7% |
| medium | 23 | 0.0604 | 0.138 | 0.0% | 100.0% | 62.6% |
| slow | 23 | 4.25 | 157 | 8.3% | 35.7% | 80.4% |
| very_slow | 23 | 175 | 538 | 1.1% | 76.3% | 76.6% |

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
