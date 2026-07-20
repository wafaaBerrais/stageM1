# Refined Feature Analysis v2

## Baseline

- Total tests: 8542
- Total valid tests: 2940
- Total invalid tests: 5602
- UNDER rate among invalid tests: 0.1166
- OVER rate among valid tests: 0.3333

## Numeric UNDER Results

Among invalid tests, the strongest non-low-support numeric contexts are:
- `numeric_boundary_case=below_min`: rate=0.715, lift=6.13, invalid_tests=568, schemas=194.
- `numeric_has_default=true`: rate=0.632, lift=5.42, invalid_tests=427, schemas=105.
- `numeric_target_type=mixed`: rate=0.545, lift=4.68, invalid_tests=253, schemas=60.
- `numeric_boundary_case=above_max`: rate=0.484, lift=4.15, invalid_tests=122, schemas=63.
- `numeric_target_type=number`: rate=0.474, lift=4.07, invalid_tests=392, schemas=93.
- `numeric_property_required=true`: rate=0.455, lift=3.91, invalid_tests=784, schemas=173.
- `numeric_parent_keyword=properties`: rate=0.415, lift=3.56, invalid_tests=1161, schemas=254.
- `numeric_is_in_properties=true`: rate=0.407, lift=3.49, invalid_tests=1271, schemas=273.

Interpretation: these rates condition on invalid examples only, so boundary cases are compared against the right denominator rather than all tests.

## PatternProperties OVER Results

- `patternProperties_regex_has_alternation=true`: rate=1.000, lift=3.00, valid_tests=28, schemas=15.
- `additionalProperties_value=false`: rate=0.983, lift=2.95, valid_tests=119, schemas=66.
- `patternProperties_has_additionalProperties=true`: rate=0.975, lift=2.93, valid_tests=121, schemas=68.
- `instance_has_unmatched_keys=true`: rate=0.938, lift=2.81, valid_tests=340, schemas=243.
- `instance_matching_pattern_keys_count_bucket=2`: rate=0.921, lift=2.76, valid_tests=76, schemas=45.
- `patternProperties_with_properties=true`: rate=0.920, lift=2.76, valid_tests=50, schemas=28.
- `patternProperties_regex_has_charclass=true`: rate=0.906, lift=2.72, valid_tests=117, schemas=65.
- `patternProperties_regex_has_anchor=true`: rate=0.893, lift=2.68, valid_tests=169, schemas=93.

Interpretation: high patternProperties lifts should be read together with support; the support-vs-lift plot separates rare sharp signals from broader effects.

## Combinator OVER Results

- `combinator_branch_count_bucket=6+`: rate=0.905, lift=2.71, valid_tests=21, schemas=14.
- `combinator_type=mixed`: rate=0.789, lift=2.37, valid_tests=76, schemas=42.
- `anyOf_satisfied_branch_count=2`: rate=0.750, lift=2.25, valid_tests=20, schemas=12.
- `anyOf_satisfied_branch_count_bucket=2`: rate=0.750, lift=2.25, valid_tests=20, schemas=12.
- `branches_overlapping_properties=true`: rate=0.733, lift=2.20, valid_tests=60, schemas=36.
- `branches_have_enum=true`: rate=0.722, lift=2.17, valid_tests=90, schemas=52.
- `combinator_type=allOf`: rate=0.714, lift=2.14, valid_tests=21, schemas=11.
- `branches_have_properties=true`: rate=0.706, lift=2.12, valid_tests=143, schemas=80.

Interpretation: branch count and matched-branch buckets help distinguish combinator presence from branch interaction cases.

## Test-Level vs Schema-Level

UNDER comparison:
- `numeric_boundary_case=below_min`: test lift 6.13; schema lift 5.07; schemas 194.
- `numeric_has_default=true`: test lift 5.42; schema lift 5.06; schemas 106.
- `numeric_target_type=mixed`: test lift 4.68; schema lift 4.95; schemas 60.
- `numeric_boundary_case=above_max`: test lift 4.15; schema lift 3.42; schemas 63.
- `numeric_target_type=number`: test lift 4.07; schema lift 4.23; schemas 95.
- `numeric_property_required=true`: test lift 3.91; schema lift 4.53; schemas 175.
- `numeric_parent_keyword=properties`: test lift 3.56; schema lift 4.24; schemas 257.
- `numeric_is_in_properties=true`: test lift 3.49; schema lift 4.16; schemas 276.

OVER comparison:
- `patternProperties_regex_has_alternation=true`: test lift 3.00; schema lift 2.80; schemas 15.
- `additionalProperties_value=false`: test lift 2.95; schema lift 2.75; schemas 66.
- `patternProperties_has_additionalProperties=true`: test lift 2.93; schema lift 2.71; schemas 68.
- `instance_has_unmatched_keys=true`: test lift 2.81; schema lift 1.33; schemas 816.
- `instance_matching_pattern_keys_count_bucket=2`: test lift 2.76; schema lift 2.52; schemas 50.
- `patternProperties_with_properties=true`: test lift 2.76; schema lift 2.60; schemas 28.
- `patternProperties_regex_has_charclass=true`: test lift 2.72; schema lift 2.54; schemas 65.
- `combinator_branch_count_bucket=6+`: test lift 2.71; schema lift 2.40; schemas 14.

If a context has high test-level lift but modest schema-level lift, it may be amplified by a smaller number of schemas with many tests.

## Limitations

- Results remain correlational.
- HDD or controlled mutations are still needed for causal validation.
- Low-support contexts should not be overinterpreted.
