# Statistical study: Github_easy / outlines

This folder contains schema-level statistics and SVG plots generated from the dataset run files. Compile time is analyzed once per schema, not once per test, to avoid overweighting schemas that contain many tests.

## Inputs

- `per_test_results.jsonl`: 7124 rows
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
| completed tests | 7124 |
| coverage rate | 98.2% |
| accuracy on completed tests | 85.5% |
| under-constraint rate | 11.8% |
| over-constraint rate | 19.0% |
| median compile_grammar_s | 0.891 |
| p95 compile_grammar_s | 26.2 |
| max compile_grammar_s | 573 |

## Timeout stages

| timeout_stage | schemas |
| --- | ---: |
| building_index | 24 |

Timeout stages are inferred from the timeout log when available, otherwise from partial checkpoints in `timing_profile.csv`.

## Expected validity among timeout tests

| expected_validity | tests | share |
| --- | ---: | ---: |
| valid | 41 | 32.0% |
| invalid | 87 | 68.0% |

## Timing by schema status

| status | phase | n | mean_s | std_s | median_s | p95_s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| completed | compile_grammar_s | 1765 | 8.3 | 38.5 | 0.891 | 26.2 |
| completed | validation_loop_mean_s | 1620 | 0.0575 | 0.193 | 0.0306 | 0.178 |
| completed | compute_mask_mean_s | 1620 | 0.0256 | 0.0863 | 0.0137 | 0.0796 |
| completed | commit_token_mean_s | 1620 | 0.0318 | 0.106 | 0.0169 | 0.099 |
| timeout | timeout_elapsed_s | 24 | 601 | 0.414 | 601 | 601 |

For timeout schemas, phase values are partial checkpoints when available; `timeout_elapsed_s` is the supervisor elapsed time.

## Feature extraction

Raw structural features are `has_*` indicators for explicit JSON Schema keywords or benchmark categories. `$ref`, `$anchor`, `$dynamicRef`, `$defs`/`definitions`, `if`/`then`/`else`, and content keywords are mapped directly from the schema; `boolean_schema` is detected from boolean schema nodes and the benchmark `_boolSchema` metadata. `infinite-loop-detection` is only read from benchmark metadata when present because it is not a JSON Schema keyword.

Derived indicators (`large_enum`, `many_required`, `many_properties`, `deep_schema`) are kept separate from raw keyword features. Pair rows are generated automatically with `itertools.combinations(BASE_FEATURES, 2)`; a pair is present only when both base features are present in the same schema.

## Features associated with timeout

| feature | schemas | timeout with | timeout without | lift |
| --- | ---: | ---: | ---: | ---: |
| `has_properties` | 1773 | 1.4% | 0.0% | inf |
| `has_type` | 1787 | 1.3% | 0.0% | inf |
| `has_maxLength` | 154 | 13.0% | 0.2% | 53.08 |
| `has_minLength` | 196 | 9.2% | 0.4% | 24.38 |
| `has_maxItems` | 36 | 11.1% | 1.1% | 9.74 |
| `has_additionalProperties` | 810 | 2.6% | 0.3% | 8.46 |
| `has_boolean_schema` | 788 | 2.5% | 0.4% | 6.35 |
| `has_oneOf` | 75 | 6.7% | 1.1% | 6.01 |
| `has_pattern` | 214 | 3.3% | 1.1% | 3.03 |
| `has_enum` | 419 | 2.6% | 0.9% | 2.77 |

## Features associated with under/over-constraint

| feature | schemas | under_rate | over_rate | correct_rate |
| --- | ---: | ---: | ---: | ---: |
| `has_allOf` | 22 | 3.8% | 87.9% | 71.4% |
| `has_patternProperties` | 44 | 16.0% | 70.4% | 62.1% |
| `has_not` | 5 | 11.1% | 75.0% | 69.2% |
| `has_maximum` | 79 | 62.9% | 18.9% | 49.3% |
| `has_multipleOf` | 10 | 53.6% | 26.7% | 55.8% |
| `has_minimum` | 195 | 56.2% | 14.2% | 56.1% |
| `has_maxProperties` | 2 | 0.0% | 50.0% | 87.5% |
| `has_if_then_else` | 1 | 50.0% | 0.0% | 66.7% |
| `deep_schema` | 51 | 7.7% | 41.0% | 81.3% |
| `has_oneOf` | 75 | 9.8% | 38.1% | 79.9% |

## Simple feature pairs

| feature_pair | schemas | timeout_rate | under_rate | over_rate |
| --- | ---: | ---: | ---: | ---: |
| `has_maxItems__AND__has_maxLength` | 5 | 60.0% | 27.3% | 33.3% |
| `has_maxItems__AND__has_minLength` | 6 | 50.0% | 35.0% | 0.0% |
| `has_maximum__AND__has_minLength` | 5 | 40.0% | 46.7% | 0.0% |
| `has_maxItems__AND__has_pattern` | 11 | 36.4% | 26.1% | 38.5% |
| `has_maxLength__AND__has_oneOf` | 15 | 33.3% | 14.7% | 40.0% |
| `has_maxLength__AND__has_maximum` | 6 | 33.3% | 30.4% | 16.7% |
| `has_minLength__AND__has_oneOf` | 19 | 21.1% | 12.8% | 38.1% |
| `has_items__AND__has_maxLength` | 30 | 20.0% | 14.3% | 25.0% |
| `has_boolean_schema__AND__has_maxItems` | 20 | 20.0% | 7.4% | 15.0% |
| `has_additionalProperties__AND__has_maxLength` | 99 | 19.2% | 8.2% | 19.3% |

## Selected pair heatmap candidates

The pair heatmap keeps the most interesting generated pairs. The ranking first requires usable support, then prioritizes the number of signals among timeout/under/over, then capped lift, delta, and support. This avoids filling the plot with rare pairs that only look strong because the denominator is tiny.

| feature_pair | schemas | risk_count | interest_score | timeout_group | under_group | over_group |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `has_items__AND__has_maxLength` | 30 | 3 | 3.02e+06 | 25.0% | 2.9% | 1.8% |
| `has_minLength__AND__has_pattern` | 43 | 3 | 3.01e+06 | 20.8% | 5.8% | 2.7% |
| `has_enum__AND__has_maximum` | 21 | 3 | 3.01e+06 | 8.3% | 5.8% | 1.5% |
| `has_maxItems__AND__has_required` | 27 | 3 | 3.01e+06 | 8.3% | 1.6% | 1.5% |
| `has_minItems__AND__has_pattern` | 14 | 3 | 3.01e+06 | 4.2% | 2.1% | 1.5% |
| `has_maximum__AND__has_required` | 54 | 3 | 3.01e+06 | 4.2% | 14.8% | 3.5% |
| `has_boolean_schema__AND__has_maximum` | 41 | 3 | 3.01e+06 | 8.3% | 11.5% | 3.2% |
| `has_additionalProperties__AND__has_maximum` | 40 | 3 | 3.01e+06 | 8.3% | 11.5% | 2.9% |
| `has_maxLength__AND__has_minLength` | 103 | 2 | 2.05e+06 | 75.0% | 8.6% | 6.2% |
| `has_maxItems__AND__has_minLength` | 6 | 2 | 2.04e+06 | 12.5% | 0.8% | 0.0% |

## Very slow completed schemas and errors

| group | schemas | compile_min_s | compile_max_s | under_rate | over_rate | accuracy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 442 | 0.0255 | 0.585 | 13.0% | 46.0% | 74.2% |
| medium | 441 | 0.586 | 0.891 | 13.0% | 8.7% | 88.7% |
| slow | 441 | 0.892 | 1.61 | 10.7% | 7.7% | 90.4% |
| very_slow | 441 | 1.63 | 573 | 11.2% | 16.2% | 87.2% |

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
