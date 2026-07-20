# Statistical study: Github_medium / guidance

This folder contains schema-level statistics and SVG plots generated from the dataset run files. Compile time is analyzed once per schema, not once per test, to avoid overweighting schemas that contain many tests.

## Inputs

- `per_test_results.jsonl`: 9210 rows
- `timing_profile.csv`: 9210 rows
- `timed_out_schemas.jsonl`: 0 rows

## Main summary

| metric | value |
| --- | ---: |
| schemas | 1823 |
| completed schemas | 1823 |
| timeout schemas | 0 |
| schema timeout rate | 0.0% |
| tests | 9210 |
| completed tests | 9210 |
| coverage rate | 100.0% |
| accuracy on completed tests | 75.4% |
| under-constraint rate | 0.0% |
| over-constraint rate | 73.4% |
| median compile_grammar_s | 0.0017 |
| p95 compile_grammar_s | 0.005 |
| max compile_grammar_s | 0.0172 |

## Timeout stages

| timeout_stage | schemas |
| --- | ---: |
| none | 0 |

Timeout stages are inferred from the timeout log when available, otherwise from partial checkpoints in `timing_profile.csv`.

## Expected validity among timeout tests

| expected_validity | tests | share |
| --- | ---: | ---: |
| valid | 0 | 0.0% |
| invalid | 0 | 0.0% |

## Timing by schema status

| status | phase | n | mean_s | std_s | median_s | p95_s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| completed | compile_grammar_s | 1823 | 0.00205 | 0.00177 | 0.0017 | 0.005 |
| completed | validation_loop_mean_s | 1454 | 0.00447 | 0.0054 | 0.00309 | 0.0119 |
| completed | compute_mask_mean_s | 1454 | 0.00396 | 0.00484 | 0.00269 | 0.0108 |
| completed | commit_token_mean_s | 1454 | 0.000232 | 0.000255 | 0.000175 | 0.00061 |

For timeout schemas, phase values are partial checkpoints when available; `timeout_elapsed_s` is the supervisor elapsed time.

## Feature extraction

Raw structural features are `has_*` indicators for explicit JSON Schema keywords or benchmark categories. `$ref`, `$anchor`, `$dynamicRef`, `$defs`/`definitions`, `if`/`then`/`else`, and content keywords are mapped directly from the schema; `boolean_schema` is detected from boolean schema nodes and the benchmark `_boolSchema` metadata. `infinite-loop-detection` is only read from benchmark metadata when present because it is not a JSON Schema keyword.

Derived indicators (`large_enum`, `many_required`, `many_properties`, `deep_schema`) are kept separate from raw keyword features. Pair rows are generated automatically with `itertools.combinations(BASE_FEATURES, 2)`; a pair is present only when both base features are present in the same schema.

## Features associated with timeout

| feature | schemas | timeout with | timeout without | lift |
| --- | ---: | ---: | ---: | ---: |
| `has_additionalProperties` | 852 | 0.0% | 0.0% | 0.00 |
| `has_allOf` | 42 | 0.0% | 0.0% | 0.00 |
| `has_anyOf` | 92 | 0.0% | 0.0% | 0.00 |
| `has_boolean_schema` | 825 | 0.0% | 0.0% | 0.00 |
| `has_const` | 19 | 0.0% | 0.0% | 0.00 |
| `has_contains` | 1 | 0.0% | 0.0% | 0.00 |
| `has_content` | 2 | 0.0% | 0.0% | 0.00 |
| `has_default` | 485 | 0.0% | 0.0% | 0.00 |
| `has_defs` | 471 | 0.0% | 0.0% | 0.00 |
| `has_enum` | 808 | 0.0% | 0.0% | 0.00 |

## Features associated with under/over-constraint

| feature | schemas | under_rate | over_rate | correct_rate |
| --- | ---: | ---: | ---: | ---: |
| `has_minProperties` | 29 | 0.0% | 100.0% | 68.0% |
| `has_not` | 20 | 0.0% | 100.0% | 68.9% |
| `has_maxProperties` | 10 | 0.0% | 100.0% | 70.6% |
| `has_if_then_else` | 4 | 0.0% | 100.0% | 65.0% |
| `has_propertyNames` | 3 | 0.0% | 100.0% | 76.5% |
| `has_contains` | 1 | 0.0% | 100.0% | 66.7% |
| `has_patternProperties` | 119 | 0.0% | 98.2% | 63.6% |
| `has_allOf` | 42 | 0.0% | 87.0% | 70.9% |
| `has_oneOf` | 182 | 0.0% | 85.9% | 68.2% |
| `has_multipleOf` | 9 | 0.0% | 83.3% | 58.3% |

## Simple feature pairs

| feature_pair | schemas | timeout_rate | under_rate | over_rate |
| --- | ---: | ---: | ---: | ---: |
| `has_properties__AND__has_type` | 1819 | 0.0% | 0.0% | 73.3% |
| `has_properties__AND__has_required` | 1365 | 0.0% | 0.0% | 72.2% |
| `has_required__AND__has_type` | 1365 | 0.0% | 0.0% | 72.2% |
| `has_items__AND__has_properties` | 990 | 0.0% | 0.0% | 73.7% |
| `has_items__AND__has_type` | 990 | 0.0% | 0.0% | 73.7% |
| `has_additionalProperties__AND__has_properties` | 852 | 0.0% | 0.0% | 74.9% |
| `has_additionalProperties__AND__has_type` | 852 | 0.0% | 0.0% | 74.9% |
| `has_boolean_schema__AND__has_properties` | 825 | 0.0% | 0.0% | 75.4% |
| `has_boolean_schema__AND__has_type` | 825 | 0.0% | 0.0% | 75.4% |
| `has_additionalProperties__AND__has_boolean_schema` | 820 | 0.0% | 0.0% | 75.2% |

## Selected pair heatmap candidates

The pair heatmap keeps the most interesting generated pairs. The ranking first requires usable support, then prioritizes the number of signals among timeout/under/over, then capped lift, delta, and support. This avoids filling the plot with rare pairs that only look strong because the denominator is tiny.

| feature_pair | schemas | risk_count | interest_score | timeout_group | under_group | over_group |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `has_patternProperties__AND__has_required` | 92 | 1 | 1e+06 | 0.0% | 0.0% | 6.8% |
| `has_minLength__AND__has_patternProperties` | 39 | 1 | 1e+06 | 0.0% | 0.0% | 2.9% |
| `has_minItems__AND__has_patternProperties` | 33 | 1 | 1e+06 | 0.0% | 0.0% | 2.4% |
| `has_patternProperties__AND__has_properties` | 119 | 1 | 1e+06 | 0.0% | 0.0% | 8.6% |
| `has_patternProperties__AND__has_type` | 119 | 1 | 1e+06 | 0.0% | 0.0% | 8.6% |
| `has_additionalProperties__AND__has_patternProperties` | 89 | 1 | 1e+06 | 0.0% | 0.0% | 6.5% |
| `has_oneOf__AND__has_patternProperties` | 28 | 1 | 1e+06 | 0.0% | 0.0% | 2.1% |
| `has_minProperties__AND__has_type` | 29 | 1 | 1e+06 | 0.0% | 0.0% | 2.1% |
| `has_boolean_schema__AND__has_patternProperties` | 87 | 1 | 1e+06 | 0.0% | 0.0% | 6.3% |
| `has_minProperties__AND__has_properties` | 25 | 1 | 1e+06 | 0.0% | 0.0% | 1.8% |

## Very slow completed schemas and errors

| group | schemas | compile_min_s | compile_max_s | under_rate | over_rate | accuracy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 456 | 0.000261 | 0.00119 | 0.0% | 87.8% | 65.7% |
| medium | 457 | 0.0012 | 0.0017 | 0.0% | 63.0% | 77.1% |
| slow | 454 | 0.0017 | 0.00236 | 0.0% | 67.1% | 77.7% |
| very_slow | 456 | 0.00236 | 0.0172 | 0.0% | 74.8% | 79.4% |

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

<!-- compile-error-causes:start -->
## Compile-error causes

These files summarize compile errors by explicit framework message and by JSON Schema features present in the affected schemas.

- `compile_error_top_causes.csv` / `compile_error_top_causes.svg`: normalized causes extracted from `error_message`.
- `compile_error_top_schema_features.csv` / `compile_error_top_schema_features.svg`: most frequent schema features among compile-error schemas.
- `compile_error_feature_lift.csv` / `compile_error_feature_lift.svg`: features with the strongest compile-error lift compared with schemas that do not contain the feature.

Top causes by affected schemas:

| cause | schemas | tests |
| --- | ---: | ---: |
| keyword: patternProperties | 108 | 535 |
| keyword: oneOf | 54 | 238 |
| format: uri | 47 | 216 |
| format: path | 37 | 95 |
| keyword: minProperties | 25 | 123 |
| keyword: dependencies | 21 | 98 |
| format: topic | 16 | 35 |
| format: url | 13 | 72 |

Top feature lift signals:

| feature | schemas | rate | lift |
| --- | --- | ---: | ---: |
| has_patternProperties | 116 | 97.5% | 6.57 |
| has_minProperties | 29 | 100.0% | 5.28 |
| has_not | 20 | 100.0% | 5.17 |
| has_maxProperties | 10 | 100.0% | 5.05 |
| has_oneOf | 118 | 64.8% | 4.24 |
| has_allOf | 27 | 64.3% | 3.35 |
| has_const | 11 | 57.9% | 2.92 |
| has_ref | 153 | 34.6% | 2.21 |
<!-- compile-error-causes:end -->
