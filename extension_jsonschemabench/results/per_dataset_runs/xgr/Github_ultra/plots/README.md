# Statistical study: Github_ultra / xgr

This folder contains schema-level statistics and SVG plots generated from the dataset run files. Compile time is analyzed once per schema, not once per test, to avoid overweighting schemas that contain many tests.

## Inputs

- `per_test_results.jsonl`: 449 rows
- `timing_profile.csv`: 462 rows
- `timed_out_schemas.jsonl`: 3 rows

## Main summary

| metric | value |
| --- | ---: |
| schemas | 95 |
| completed schemas | 92 |
| timeout schemas | 3 |
| schema timeout rate | 3.2% |
| tests | 459 |
| completed tests | 449 |
| coverage rate | 97.8% |
| accuracy on completed tests | 74.6% |
| under-constraint rate | 19.2% |
| over-constraint rate | 36.7% |
| median compile_grammar_s | 28.8 |
| p95 compile_grammar_s | 81.4 |
| max compile_grammar_s | 84.6 |

## Timeout stages

| timeout_stage | schemas |
| --- | ---: |
| validation | 3 |

Timeout stages are inferred from the timeout log when available, otherwise from partial checkpoints in `timing_profile.csv`.

## Expected validity among timeout tests

| expected_validity | tests | share |
| --- | ---: | ---: |
| valid | 3 | 25.0% |
| invalid | 9 | 75.0% |

## Timing by schema status

| status | phase | n | mean_s | std_s | median_s | p95_s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| completed | compile_grammar_s | 92 | 34.2 | 22.1 | 28.8 | 81.4 |
| completed | validation_loop_mean_s | 91 | 0.308 | 0.905 | 0.025 | 1.56 |
| completed | compute_mask_mean_s | 91 | 0.305 | 0.903 | 0.0221 | 1.55 |
| completed | commit_token_mean_s | 91 | 0.00177 | 0.00388 | 0.000339 | 0.00821 |
| timeout | compile_grammar_s | 3 | 44.4 | 25.1 | 35.4 | 69 |
| timeout | validation_loop_mean_s | 3 | 395 | 224 | 485 | 553 |
| timeout | compute_mask_mean_s | 3 | 380 | 209 | 484 | 514 |
| timeout | commit_token_mean_s | 3 | 14.6 | 24.3 | 1.2 | 38.5 |
| timeout | timeout_elapsed_s | 3 | 600 | 0.0283 | 600 | 600 |

For timeout schemas, phase values are partial checkpoints when available; `timeout_elapsed_s` is the supervisor elapsed time.

## Feature extraction

Raw structural features are `has_*` indicators for explicit JSON Schema keywords or benchmark categories. `$ref`, `$anchor`, `$dynamicRef`, `$defs`/`definitions`, `if`/`then`/`else`, and content keywords are mapped directly from the schema; `boolean_schema` is detected from boolean schema nodes and the benchmark `_boolSchema` metadata. `infinite-loop-detection` is only read from benchmark metadata when present because it is not a JSON Schema keyword.

Derived indicators (`large_enum`, `many_required`, `many_properties`, `deep_schema`) are kept separate from raw keyword features. Pair rows are generated automatically with `itertools.combinations(BASE_FEATURES, 2)`; a pair is present only when both base features are present in the same schema.

## Features associated with timeout

| feature | schemas | timeout with | timeout without | lift |
| --- | ---: | ---: | ---: | ---: |
| `has_minItems` | 32 | 9.4% | 0.0% | inf |
| `has_minimum` | 33 | 9.1% | 0.0% | inf |
| `has_pattern` | 36 | 8.3% | 0.0% | inf |
| `large_enum` | 59 | 5.1% | 0.0% | inf |
| `has_enum` | 72 | 4.2% | 0.0% | inf |
| `many_required` | 82 | 3.7% | 0.0% | inf |
| `has_required` | 85 | 3.5% | 0.0% | inf |
| `has_items` | 90 | 3.3% | 0.0% | inf |
| `has_properties` | 95 | 3.2% | 0.0% | inf |
| `has_type` | 95 | 3.2% | 0.0% | inf |

## Features associated with under/over-constraint

| feature | schemas | under_rate | over_rate | correct_rate |
| --- | ---: | ---: | ---: | ---: |
| `has_exclusiveMaximum` | 3 | 9.1% | 100.0% | 62.5% |
| `has_maxProperties` | 8 | 0.0% | 100.0% | 72.5% |
| `has_minProperties` | 8 | 0.0% | 100.0% | 72.5% |
| `has_patternProperties` | 7 | 6.9% | 80.0% | 74.4% |
| `has_pattern` | 36 | 29.3% | 56.4% | 63.4% |
| `has_multipleOf` | 4 | 84.2% | 0.0% | 38.5% |
| `has_maxLength` | 20 | 44.3% | 36.7% | 57.8% |
| `has_minimum` | 33 | 32.1% | 48.0% | 63.0% |
| `has_allOf` | 11 | 56.6% | 23.5% | 51.4% |
| `has_oneOf` | 26 | 29.4% | 47.6% | 64.6% |

## Simple feature pairs

| feature_pair | schemas | timeout_rate | under_rate | over_rate |
| --- | ---: | ---: | ---: | ---: |
| `has_additionalProperties__AND__has_exclusiveMaximum` | 3 | 33.3% | 9.1% | 100.0% |
| `has_boolean_schema__AND__has_exclusiveMaximum` | 3 | 33.3% | 9.1% | 100.0% |
| `has_enum__AND__has_exclusiveMaximum` | 3 | 33.3% | 9.1% | 100.0% |
| `has_exclusiveMaximum__AND__has_items` | 3 | 33.3% | 9.1% | 100.0% |
| `has_exclusiveMaximum__AND__has_maxItems` | 3 | 33.3% | 9.1% | 100.0% |
| `has_exclusiveMaximum__AND__has_maxLength` | 3 | 33.3% | 9.1% | 100.0% |
| `has_exclusiveMaximum__AND__has_minItems` | 3 | 33.3% | 9.1% | 100.0% |
| `has_exclusiveMaximum__AND__has_minLength` | 3 | 33.3% | 9.1% | 100.0% |
| `has_exclusiveMaximum__AND__has_minimum` | 3 | 33.3% | 9.1% | 100.0% |
| `has_exclusiveMaximum__AND__has_pattern` | 3 | 33.3% | 9.1% | 100.0% |

## Selected pair heatmap candidates

The pair heatmap keeps the most interesting generated pairs. The ranking first requires usable support, then prioritizes the number of signals among timeout/under/over, then capped lift, delta, and support. This avoids filling the plot with rare pairs that only look strong because the denominator is tiny.

| feature_pair | schemas | risk_count | interest_score | timeout_group | under_group | over_group |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `has_properties__AND__has_type` | 95 | 3 | 3.05e+06 | 100.0% | 100.0% | 100.0% |
| `has_items__AND__has_pattern` | 36 | 3 | 3.05e+06 | 100.0% | 61.5% | 50.0% |
| `has_pattern__AND__has_properties` | 36 | 3 | 3.05e+06 | 100.0% | 61.5% | 50.0% |
| `has_pattern__AND__has_type` | 36 | 3 | 3.05e+06 | 100.0% | 61.5% | 50.0% |
| `has_pattern__AND__has_required` | 34 | 3 | 3.05e+06 | 100.0% | 57.7% | 47.2% |
| `has_minimum__AND__has_pattern` | 19 | 3 | 3.05e+06 | 100.0% | 42.3% | 19.4% |
| `has_enum__AND__has_pattern` | 33 | 3 | 3.05e+06 | 100.0% | 57.7% | 44.4% |
| `has_minItems__AND__has_pattern` | 15 | 3 | 3.05e+06 | 100.0% | 30.8% | 16.7% |
| `has_minimum__AND__has_properties` | 33 | 3 | 3.05e+06 | 100.0% | 53.8% | 38.9% |
| `has_minimum__AND__has_type` | 33 | 3 | 3.05e+06 | 100.0% | 53.8% | 38.9% |

## Very slow completed schemas and errors

| group | schemas | compile_min_s | compile_max_s | under_rate | over_rate | accuracy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 23 | 0.00502 | 20.1 | 48.4% | 27.0% | 59.6% |
| medium | 23 | 20.6 | 28.8 | 6.2% | 45.2% | 80.5% |
| slow | 23 | 28.9 | 46.1 | 10.3% | 44.7% | 78.4% |
| very_slow | 23 | 46.5 | 84.6 | 18.8% | 27.5% | 78.0% |

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
