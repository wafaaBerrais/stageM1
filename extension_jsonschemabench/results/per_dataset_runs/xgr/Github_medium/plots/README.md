# Statistical study: Github_medium / xgr

This folder contains schema-level statistics and SVG plots generated from the dataset run files. Compile time is analyzed once per schema, not once per test, to avoid overweighting schemas that contain many tests.

## Inputs

- `per_test_results.jsonl`: 8390 rows
- `timing_profile.csv`: 9210 rows
- `timed_out_schemas.jsonl`: 107 rows

## Main summary

| metric | value |
| --- | ---: |
| schemas | 1823 |
| completed schemas | 1716 |
| timeout schemas | 107 |
| schema timeout rate | 5.9% |
| tests | 9210 |
| completed tests | 8390 |
| coverage rate | 91.1% |
| accuracy on completed tests | 80.6% |
| under-constraint rate | 18.0% |
| over-constraint rate | 22.0% |
| median compile_grammar_s | 2.39 |
| p95 compile_grammar_s | 16.7 |
| max compile_grammar_s | 575 |

## Timeout stages

| timeout_stage | schemas |
| --- | ---: |
| compile_grammar | 78 |
| terminated_signal_11 | 22 |
| terminated_sigterm | 4 |
| terminated_signal_15 | 2 |
| validation | 1 |

Timeout stages are inferred from the timeout log when available, otherwise from partial checkpoints in `timing_profile.csv`.

## Expected validity among timeout tests

| expected_validity | tests | share |
| --- | ---: | ---: |
| valid | 182 | 22.2% |
| invalid | 638 | 77.8% |

## Timing by schema status

| status | phase | n | mean_s | std_s | median_s | p95_s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| completed | compile_grammar_s | 1716 | 8.07 | 37.3 | 2.39 | 16.7 |
| completed | validation_loop_mean_s | 1706 | 0.0632 | 1.07 | 0.00258 | 0.0283 |
| completed | compute_mask_mean_s | 1706 | 0.0619 | 1.05 | 0.0023 | 0.0279 |
| completed | commit_token_mean_s | 1706 | 0.000734 | 0.0229 | 6.08e-05 | 0.000316 |
| timeout | compile_grammar_s | 4 | 302 | 344 | 302 | 600 |
| timeout | validation_loop_mean_s | 1 | 20.2 | 0 | 20.2 | 20.2 |
| timeout | compute_mask_mean_s | 2 | 10.1 | 14.3 | 10.1 | 19.2 |
| timeout | commit_token_mean_s | 2 | 0.000168 | 0.000238 | 0.000168 | 0.000319 |
| timeout | timeout_elapsed_s | 107 | 615 | 384 | 600 | 1.6e+03 |

For timeout schemas, phase values are partial checkpoints when available; `timeout_elapsed_s` is the supervisor elapsed time.

## Feature extraction

Raw structural features are `has_*` indicators for explicit JSON Schema keywords or benchmark categories. `$ref`, `$anchor`, `$dynamicRef`, `$defs`/`definitions`, `if`/`then`/`else`, and content keywords are mapped directly from the schema; `boolean_schema` is detected from boolean schema nodes and the benchmark `_boolSchema` metadata. `infinite-loop-detection` is only read from benchmark metadata when present because it is not a JSON Schema keyword.

Derived indicators (`large_enum`, `many_required`, `many_properties`, `deep_schema`) are kept separate from raw keyword features. Pair rows are generated automatically with `itertools.combinations(BASE_FEATURES, 2)`; a pair is present only when both base features are present in the same schema.

## Features associated with timeout

| feature | schemas | timeout with | timeout without | lift |
| --- | ---: | ---: | ---: | ---: |
| `has_properties` | 1819 | 5.9% | 0.0% | inf |
| `has_type` | 1823 | 5.9% | 0.0% | inf |
| `has_maxLength` | 252 | 38.1% | 0.7% | 54.41 |
| `has_pattern` | 512 | 19.1% | 0.7% | 27.88 |
| `has_minLength` | 313 | 29.1% | 1.1% | 27.44 |
| `has_maxItems` | 90 | 21.1% | 5.1% | 4.16 |
| `has_boolean_schema` | 825 | 9.7% | 2.7% | 3.58 |
| `has_additionalProperties` | 852 | 9.4% | 2.8% | 3.38 |
| `has_maximum` | 111 | 17.1% | 5.1% | 3.33 |
| `has_patternProperties` | 119 | 13.4% | 5.3% | 2.52 |

## Features associated with under/over-constraint

| feature | schemas | under_rate | over_rate | correct_rate |
| --- | ---: | ---: | ---: | ---: |
| `has_if_then_else` | 4 | 0.0% | 100.0% | 65.0% |
| `has_propertyNames` | 3 | 0.0% | 100.0% | 76.5% |
| `has_contains` | 1 | 0.0% | 100.0% | 66.7% |
| `has_not` | 20 | 46.6% | 51.5% | 51.9% |
| `has_patternProperties` | 119 | 3.7% | 86.7% | 64.0% |
| `has_allOf` | 42 | 60.8% | 27.3% | 50.4% |
| `has_minItems` | 227 | 31.9% | 39.3% | 66.1% |
| `has_anyOf` | 92 | 34.6% | 36.5% | 64.9% |
| `has_minProperties` | 29 | 23.0% | 46.8% | 69.4% |
| `has_maxProperties` | 10 | 8.3% | 53.3% | 78.4% |

## Simple feature pairs

| feature_pair | schemas | timeout_rate | under_rate | over_rate |
| --- | ---: | ---: | ---: | ---: |
| `has_maxLength__AND__has_patternProperties` | 23 | 69.6% | 0.0% | 72.7% |
| `has_maxItems__AND__has_maxLength` | 28 | 67.9% | 8.8% | 50.0% |
| `has_maxItems__AND__has_minLength` | 28 | 64.3% | 23.2% | 35.3% |
| `has_maxItems__AND__has_oneOf` | 24 | 54.2% | 25.0% | 45.0% |
| `has_maxLength__AND__has_pattern` | 169 | 51.5% | 19.1% | 22.5% |
| `has_const__AND__has_maxLength` | 2 | 50.0% | 0.0% | 100.0% |
| `has_minLength__AND__has_pattern` | 185 | 45.9% | 17.1% | 33.3% |
| `has_maxLength__AND__has_minLength` | 197 | 45.2% | 15.5% | 23.9% |
| `has_default__AND__has_maxLength` | 58 | 44.8% | 15.4% | 27.3% |
| `has_boolean_schema__AND__has_maxLength` | 164 | 44.5% | 15.5% | 20.1% |

## Selected pair heatmap candidates

The pair heatmap keeps the most interesting generated pairs. The ranking first requires usable support, then prioritizes the number of signals among timeout/under/over, then capped lift, delta, and support. This avoids filling the plot with rare pairs that only look strong because the denominator is tiny.

| feature_pair | schemas | risk_count | interest_score | timeout_group | under_group | over_group |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `has_maxItems__AND__has_oneOf` | 24 | 3 | 3.01e+06 | 12.1% | 1.2% | 1.2% |
| `has_maximum__AND__has_pattern` | 50 | 3 | 3.01e+06 | 16.8% | 3.8% | 2.4% |
| `has_enum__AND__has_maxItems` | 44 | 3 | 3.01e+06 | 15.0% | 3.3% | 3.1% |
| `has_minLength__AND__has_oneOf` | 58 | 3 | 3e+06 | 14.0% | 2.9% | 4.8% |
| `has_enum__AND__has_maximum` | 72 | 3 | 3e+06 | 16.8% | 6.7% | 4.6% |
| `has_minimum__AND__has_pattern` | 89 | 3 | 3e+06 | 18.7% | 7.4% | 4.8% |
| `has_boolean_schema__AND__has_maximum` | 68 | 3 | 3e+06 | 14.0% | 6.5% | 4.1% |
| `has_items__AND__has_maxItems` | 90 | 3 | 3e+06 | 17.8% | 6.7% | 5.1% |
| `has_maxItems__AND__has_properties` | 90 | 3 | 3e+06 | 17.8% | 6.7% | 5.1% |
| `has_maxItems__AND__has_type` | 90 | 3 | 3e+06 | 17.8% | 6.7% | 5.1% |

## Very slow completed schemas and errors

| group | schemas | compile_min_s | compile_max_s | under_rate | over_rate | accuracy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 429 | 0.000956 | 1.69 | 26.7% | 28.5% | 72.6% |
| medium | 429 | 1.69 | 2.38 | 20.5% | 20.2% | 79.6% |
| slow | 429 | 2.39 | 3.88 | 16.0% | 20.5% | 82.5% |
| very_slow | 429 | 3.88 | 575 | 11.9% | 18.9% | 86.0% |

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
| numeric bound: non-integer maximum | 7 | 63 |
| regex/string escape unsupported | 1 | 6 |
| boolean false schema | 1 | 4 |
| schema node is array | 1 | 3 |

Top feature lift signals:

| feature | schemas | rate | lift |
| --- | --- | ---: | ---: |
| has_maximum | 8 | 7.2% | 61.69 |
| has_maxLength | 8 | 3.2% | 24.94 |
| has_minimum | 8 | 2.6% | 20.15 |
| has_minLength | 7 | 2.2% | 11.26 |
| has_pattern | 6 | 1.2% | 3.84 |
| has_enum | 7 | 0.9% | 2.93 |
| has_boolean_schema | 7 | 0.8% | 2.82 |
| many_properties | 8 | 0.6% | 1.75 |
<!-- compile-error-causes:end -->
