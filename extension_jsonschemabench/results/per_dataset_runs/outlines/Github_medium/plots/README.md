# Statistical study: Github_medium / outlines

This folder contains schema-level statistics and SVG plots generated from the dataset run files. Compile time is analyzed once per schema, not once per test, to avoid overweighting schemas that contain many tests.

## Inputs

- `per_test_results.jsonl`: 8542 rows
- `timing_profile.csv`: 9209 rows
- `timed_out_schemas.jsonl`: 88 rows

## Main summary

| metric | value |
| --- | ---: |
| schemas | 1823 |
| completed schemas | 1735 |
| timeout schemas | 88 |
| schema timeout rate | 4.8% |
| tests | 9209 |
| completed tests | 8542 |
| coverage rate | 92.8% |
| accuracy on completed tests | 80.9% |
| under-constraint rate | 11.7% |
| over-constraint rate | 33.3% |
| median compile_grammar_s | 2.98 |
| p95 compile_grammar_s | 113 |
| max compile_grammar_s | 577 |

## Timeout stages

| timeout_stage | schemas |
| --- | ---: |
| building_index | 84 |
| completed | 2 |
| building_regex | 1 |
| loading_schema | 1 |

Timeout stages are inferred from the timeout log when available, otherwise from partial checkpoints in `timing_profile.csv`.

## Expected validity among timeout tests

| expected_validity | tests | share |
| --- | ---: | ---: |
| valid | 153 | 22.9% |
| invalid | 516 | 77.1% |

## Timing by schema status

| status | phase | n | mean_s | std_s | median_s | p95_s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| completed | compile_grammar_s | 1735 | 21.8 | 63.9 | 2.98 | 113 |
| completed | validation_loop_mean_s | 1443 | 0.146 | 0.212 | 0.094 | 0.428 |
| completed | compute_mask_mean_s | 1443 | 0.0649 | 0.0955 | 0.042 | 0.195 |
| completed | commit_token_mean_s | 1443 | 0.0804 | 0.116 | 0.052 | 0.235 |
| timeout | compile_grammar_s | 2 | 2.88 | 0.414 | 2.88 | 3.14 |
| timeout | validation_loop_mean_s | 1 | 0.135 | 0 | 0.135 | 0.135 |
| timeout | compute_mask_mean_s | 1 | 0.0304 | 0 | 0.0304 | 0.0304 |
| timeout | commit_token_mean_s | 1 | 0.0369 | 0 | 0.0369 | 0.0369 |
| timeout | timeout_elapsed_s | 88 | 601 | 1.79 | 601 | 603 |

For timeout schemas, phase values are partial checkpoints when available; `timeout_elapsed_s` is the supervisor elapsed time.

## Feature extraction

Raw structural features are `has_*` indicators for explicit JSON Schema keywords or benchmark categories. `$ref`, `$anchor`, `$dynamicRef`, `$defs`/`definitions`, `if`/`then`/`else`, and content keywords are mapped directly from the schema; `boolean_schema` is detected from boolean schema nodes and the benchmark `_boolSchema` metadata. `infinite-loop-detection` is only read from benchmark metadata when present because it is not a JSON Schema keyword.

Derived indicators (`large_enum`, `many_required`, `many_properties`, `deep_schema`) are kept separate from raw keyword features. Pair rows are generated automatically with `itertools.combinations(BASE_FEATURES, 2)`; a pair is present only when both base features are present in the same schema.

## Features associated with timeout

| feature | schemas | timeout with | timeout without | lift |
| --- | ---: | ---: | ---: | ---: |
| `has_properties` | 1819 | 4.8% | 0.0% | inf |
| `has_type` | 1823 | 4.8% | 0.0% | inf |
| `has_maxLength` | 252 | 25.4% | 1.5% | 16.62 |
| `has_pattern` | 512 | 14.3% | 1.1% | 12.46 |
| `has_minLength` | 313 | 18.2% | 2.1% | 8.87 |
| `has_maxItems` | 90 | 17.8% | 4.2% | 4.28 |
| `has_enum` | 808 | 7.9% | 2.4% | 3.35 |
| `has_maximum` | 111 | 12.6% | 4.3% | 2.92 |
| `has_boolean_schema` | 825 | 7.5% | 2.6% | 2.88 |
| `has_additionalProperties` | 852 | 7.4% | 2.6% | 2.87 |

## Features associated with under/over-constraint

| feature | schemas | under_rate | over_rate | correct_rate |
| --- | ---: | ---: | ---: | ---: |
| `has_if_then_else` | 4 | 0.0% | 100.0% | 65.0% |
| `has_propertyNames` | 3 | 0.0% | 100.0% | 76.5% |
| `has_contains` | 1 | 0.0% | 100.0% | 66.7% |
| `has_patternProperties` | 119 | 3.9% | 84.1% | 66.4% |
| `has_not` | 20 | 5.5% | 81.8% | 70.8% |
| `has_allOf` | 42 | 5.3% | 76.0% | 71.1% |
| `has_maxProperties` | 10 | 0.0% | 69.2% | 79.1% |
| `has_maximum` | 111 | 30.5% | 37.5% | 67.7% |
| `has_anyOf` | 92 | 6.9% | 58.0% | 78.6% |
| `has_minimum` | 302 | 39.0% | 25.5% | 64.6% |

## Simple feature pairs

| feature_pair | schemas | timeout_rate | under_rate | over_rate |
| --- | ---: | ---: | ---: | ---: |
| `has_maxItems__AND__has_multipleOf` | 1 | 100.0% | 0.0% | 0.0% |
| `has_maximum__AND__has_multipleOf` | 1 | 100.0% | 0.0% | 0.0% |
| `has_minItems__AND__has_multipleOf` | 1 | 100.0% | 0.0% | 0.0% |
| `has_minLength__AND__has_multipleOf` | 1 | 100.0% | 0.0% | 0.0% |
| `has_multipleOf__AND__has_pattern` | 1 | 100.0% | 0.0% | 0.0% |
| `has_maxItems__AND__has_maxLength` | 28 | 50.0% | 4.1% | 87.5% |
| `has_default__AND__has_maxItems` | 4 | 50.0% | 0.0% | 0.0% |
| `has_defs__AND__has_maxProperties` | 2 | 50.0% | 0.0% | 100.0% |
| `has_maxLength__AND__has_maxProperties` | 2 | 50.0% | 0.0% | 100.0% |
| `has_maxLength__AND__has_multipleOf` | 2 | 50.0% | 33.3% | 0.0% |

## Selected pair heatmap candidates

The pair heatmap keeps the most interesting generated pairs. The ranking first requires usable support, then prioritizes the number of signals among timeout/under/over, then capped lift, delta, and support. This avoids filling the plot with rare pairs that only look strong because the denominator is tiny.

| feature_pair | schemas | risk_count | interest_score | timeout_group | under_group | over_group |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `has_properties__AND__has_type` | 1819 | 3 | 3.05e+06 | 100.0% | 100.0% | 100.0% |
| `has_default__AND__has_maxLength` | 58 | 3 | 3.01e+06 | 25.0% | 4.4% | 3.2% |
| `has_maxLength__AND__has_maximum` | 45 | 3 | 3.01e+06 | 15.9% | 3.0% | 3.1% |
| `has_maximum__AND__has_pattern` | 50 | 3 | 3.01e+06 | 15.9% | 5.4% | 2.9% |
| `has_maxLength__AND__has_minimum` | 64 | 3 | 3.01e+06 | 15.9% | 9.1% | 3.4% |
| `has_enum__AND__has_maximum` | 72 | 3 | 3e+06 | 15.9% | 7.0% | 5.0% |
| `has_minimum__AND__has_pattern` | 89 | 3 | 3e+06 | 15.9% | 12.4% | 5.3% |
| `has_boolean_schema__AND__has_default` | 199 | 3 | 3e+06 | 30.7% | 13.8% | 11.8% |
| `has_minLength__AND__has_minimum` | 70 | 3 | 3e+06 | 12.5% | 9.4% | 3.9% |
| `has_additionalProperties__AND__has_default` | 213 | 3 | 3e+06 | 31.8% | 13.8% | 13.0% |

## Very slow completed schemas and errors

| group | schemas | compile_min_s | compile_max_s | under_rate | over_rate | accuracy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 434 | 0.0253 | 1.5 | 6.7% | 70.9% | 68.4% |
| medium | 434 | 1.52 | 2.98 | 21.0% | 13.3% | 81.8% |
| slow | 433 | 2.98 | 10.3 | 8.9% | 19.8% | 87.6% |
| very_slow | 434 | 10.3 | 577 | 9.9% | 30.9% | 83.4% |

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
| boolean false schema | 58 | 316 |
| format: path | 37 | 95 |
| unsupported schema structure | 32 | 122 |
| tokenizer/regex incompatible | 29 | 196 |
| DFA state limit | 29 | 154 |
| annotation-only/metadata schema | 27 | 123 |
| format: topic | 16 | 35 |
| format: url | 14 | 81 |

Top feature lift signals:

| feature | schemas | rate | lift |
| --- | --- | ---: | ---: |
| has_patternProperties | 66 | 55.5% | 4.18 |
| has_not | 11 | 55.0% | 3.53 |
| has_minProperties | 10 | 34.5% | 2.19 |
| has_allOf | 14 | 33.3% | 2.14 |
| has_additionalProperties | 178 | 20.9% | 1.78 |
| has_oneOf | 48 | 26.4% | 1.77 |
| has_required | 245 | 17.9% | 1.75 |
| has_boolean_schema | 171 | 20.7% | 1.71 |
<!-- compile-error-causes:end -->
