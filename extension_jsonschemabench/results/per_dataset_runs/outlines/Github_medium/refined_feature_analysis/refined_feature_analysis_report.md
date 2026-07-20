# Refined Feature Analysis

- Dataset: `Github_medium`
- Framework: `outlines`
- Schemas analyzed: 1736
- Tests analyzed: 8542
- Baseline UNDER rate: 0.0764
- Baseline OVER rate: 0.1147

## Numeric Results

- `numeric_boundary_case=below_min`: under_rate=0.715, lift=9.35, support_tests=568, support_schemas=194.
- `numeric_boundary_case=above_max`: under_rate=0.484, lift=6.33, support_tests=122, support_schemas=63.
- `numeric_has_default=true`: under_rate=0.448, lift=5.86, support_tests=603, support_schemas=106.
- `numeric_target_type=mixed`: under_rate=0.394, lift=5.16, support_tests=350, support_schemas=60.
- `numeric_target_type=number`: under_rate=0.334, lift=4.37, support_tests=557, support_schemas=95.

## PatternProperties Results

- `patternProperties_regex_has_alternation=true`: over_rate=0.400, lift=3.49, support_tests=70, support_schemas=15.
- `instance_matching_pattern_keys_count_bucket=2`: over_rate=0.398, lift=3.47, support_tests=176, support_schemas=50.
- `additionalProperties_value=false`: over_rate=0.333, lift=2.91, support_tests=351, support_schemas=66.
- `instance_matching_pattern_keys_count_bucket=6+`: over_rate=0.324, lift=2.82, support_tests=71, support_schemas=18.
- `patternProperties_regex_has_anchor=true`: over_rate=0.320, lift=2.79, support_tests=472, support_schemas=93.

## Not Results

No non-low-support context exceeded the support thresholds.

## Combinator Results

- `anyOf_satisfied_branch_count_bucket=2`: over_rate=0.300, lift=2.61, support_tests=50, support_schemas=16.
- `combinator_branch_count_bucket=6+`: over_rate=0.279, lift=2.44, support_tests=68, support_schemas=14.
- `oneOf_satisfied_branch_count_bucket=1`: over_rate=0.271, lift=2.36, support_tests=451, support_schemas=121.
- `combinator_type=mixed`: over_rate=0.270, lift=2.36, support_tests=222, support_schemas=42.
- `branches_have_properties=true`: over_rate=0.249, lift=2.17, support_tests=405, support_schemas=80.

## Top UNDER Contexts By Lift

- `numeric_boundary_case=below_min`: lift=9.35, rate=0.715, tests=568.
- `numeric_boundary_case=above_max`: lift=6.33, rate=0.484, tests=122.
- `numeric_has_default=true`: lift=5.86, rate=0.448, tests=603.
- `numeric_target_type=mixed`: lift=5.16, rate=0.394, tests=350.
- `numeric_target_type=number`: lift=4.37, rate=0.334, tests=557.
- `numeric_property_required=true`: lift=4.31, rate=0.330, tests=1083.
- `numeric_parent_keyword=properties`: lift=3.94, rate=0.301, tests=1602.
- `numeric_is_in_properties=true`: lift=3.88, rate=0.296, tests=1745.
- `numeric_parent_keyword=mixed`: lift=3.03, rate=0.232, tests=151.
- `numeric_has_min_and_max=true`: lift=2.95, rate=0.225, tests=644.
- `numeric_target_type=integer`: lift=2.82, rate=0.216, tests=978.
- `instance_has_unmatched_keys=false`: lift=1.22, rate=0.093, tests=6813.
- `combinator_branch_count_bucket=0`: lift=1.09, rate=0.084, tests=7219.
- `combinator_type=absent`: lift=1.09, rate=0.084, tests=7219.
- `branches_have_same_type=false`: lift=1.07, rate=0.082, tests=7554.
- `patternProperties_regex_has_anchor=false`: lift=1.05, rate=0.080, tests=8070.

## Top OVER Contexts By Lift

- `patternProperties_regex_has_alternation=true`: lift=3.49, rate=0.400, tests=70.
- `instance_matching_pattern_keys_count_bucket=2`: lift=3.47, rate=0.398, tests=176.
- `additionalProperties_value=false`: lift=2.91, rate=0.333, tests=351.
- `instance_matching_pattern_keys_count_bucket=6+`: lift=2.82, rate=0.324, tests=71.
- `patternProperties_regex_has_anchor=true`: lift=2.79, rate=0.320, tests=472.
- `patternProperties_regex_has_charclass=true`: lift=2.77, rate=0.317, tests=334.
- `patternProperties_with_properties=true`: lift=2.75, rate=0.315, tests=146.
- `instance_matching_pattern_keys_count_bucket=4-5`: lift=2.74, rate=0.315, tests=54.
- `patternProperties_regex_has_dotstar=true`: lift=2.68, rate=0.308, tests=130.
- `anyOf_satisfied_branch_count_bucket=2`: lift=2.61, rate=0.300, tests=50.
- `combinator_branch_count_bucket=6+`: lift=2.44, rate=0.279, tests=68.
- `oneOf_satisfied_branch_count_bucket=1`: lift=2.36, rate=0.271, tests=451.
- `combinator_type=mixed`: lift=2.36, rate=0.270, tests=222.
- `branches_have_properties=true`: lift=2.17, rate=0.249, tests=405.
- `branches_have_not=true`: lift=2.14, rate=0.246, tests=57.
- `instance_matching_pattern_keys_count_bucket=1`: lift=2.08, rate=0.238, tests=84.
- `branches_have_enum=true`: lift=2.06, rate=0.236, tests=275.
- `branches_overlapping_properties=true`: lift=2.05, rate=0.235, tests=187.
- `combinator_type=allOf`: lift=2.01, rate=0.231, tests=65.
- `instance_matching_pattern_keys_count_bucket=3`: lift=1.96, rate=0.225, tests=89.

## Limitations

- These results are correlational.
- A feature with high lift is not automatically the exact cause of the observed failure.
- Low-support contexts should be interpreted cautiously.
- HDD validation or controlled schema mutations can be used next to test causal hypotheses.
