#!/usr/bin/env python3
"""Build refined contextual feature tables for one dataset/framework run."""

from __future__ import annotations

import argparse
import csv
import html
import json
import math
import re
import statistics
import warnings
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

warnings.filterwarnings("ignore", message="jsonschema.RefResolver is deprecated.*")

from jsonschema import RefResolver, validators
from jsonschema.exceptions import ValidationError


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RESULTS_ROOT = ROOT / "extension_jsonschemabench" / "results" / "per_dataset_runs"
DEFAULT_DATA_ROOT = ROOT / "maskbench" / "data"

NUMERIC_KEYWORDS = ("minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf")
LOWER_NUMERIC = {"minimum", "exclusiveMinimum"}
UPPER_NUMERIC = {"maximum", "exclusiveMaximum"}
COMBINATORS = ("allOf", "anyOf", "oneOf")
OBJECT_KEYWORDS = ("properties", "required", "additionalProperties", "minProperties", "maxProperties", "propertyNames")
STRING_KEYWORDS = ("pattern", "minLength", "maxLength", "format")
ARRAY_KEYWORDS = ("items", "prefixItems", "minItems", "maxItems", "uniqueItems", "contains", "minContains", "maxContains")
COMPLEX_KEYWORDS = (
    "not",
    "allOf",
    "anyOf",
    "oneOf",
    "patternProperties",
    "additionalProperties",
    "properties",
    "required",
    "minProperties",
    "maxProperties",
    "enum",
    "const",
    "pattern",
    "items",
    "prefixItems",
)
LOCAL_PAIR_FEATURES = (
    "same_node_not_and_enum",
    "same_node_not_and_type",
    "same_node_not_and_pattern",
    "same_node_allOf_and_not",
    "same_node_allOf_and_required",
    "same_node_allOf_and_properties",
    "same_node_oneOf_and_required",
    "same_node_not_and_properties",
    "same_node_not_and_required",
    "same_node_patternProperties_and_additionalProperties",
    "same_node_properties_and_patternProperties",
    "same_node_properties_and_required",
    "same_node_properties_and_additionalProperties",
    "same_node_minProperties_and_required",
    "same_node_combinator_and_patternProperties",
    "same_node_combinator_and_numeric",
    "same_node_combinator_and_required",
    "same_node_combinator_and_properties",
)

MIN_SUPPORT_SCHEMAS = 10
MIN_SUPPORT_TESTS = 20

PALETTE = {
    "blue": "#2F6BFF",
    "teal": "#008C7D",
    "orange": "#D96C06",
    "red": "#C43C39",
    "purple": "#7557B8",
    "gray": "#5C6670",
    "grid": "#D9DEE5",
    "text": "#1F2933",
    "bg": "#FFFFFF",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--framework", default="outlines")
    parser.add_argument("--dataset", default="Github_medium")
    parser.add_argument("--results-root", default=str(DEFAULT_RESULTS_ROOT))
    parser.add_argument("--data-root", default=str(DEFAULT_DATA_ROOT))
    parser.add_argument("--output-data-dir", default=None)
    parser.add_argument("--output-plot-dir", default=None)
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_dataset_file(data_root: Path, schema_id: str) -> dict[str, Any]:
    path = data_root / schema_id
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        keys: list[str] = []
        seen: set[str] = set()
        for row in rows:
            for key in row:
                if key not in seen:
                    seen.add(key)
                    keys.append(key)
        fieldnames = keys
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: format_value(row.get(key, "")) for key in fieldnames})


def format_value(value: Any) -> Any:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        if math.isnan(value):
            return ""
        return f"{value:.6g}"
    if value is None:
        return ""
    if isinstance(value, (list, tuple, set)):
        return "|".join(str(v) for v in value)
    return value


def pct(part: float, total: float) -> float:
    return part / total if total else 0.0


def mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def aggregate_value(values: list[str], absent: str = "absent", mixed: str = "mixed") -> str:
    cleaned = sorted({v for v in values if v and v != absent})
    if not cleaned:
        return absent
    if len(cleaned) == 1:
        return cleaned[0]
    return mixed


def bool_any(values: list[bool]) -> bool:
    return any(values)


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def schema_type_value(node: dict[str, Any], inherited_type: str | None) -> str:
    raw = node.get("type", inherited_type)
    if raw is None:
        return "absent"
    if isinstance(raw, str):
        return raw
    if isinstance(raw, list):
        vals = set(str(v) for v in raw)
        if {"integer", "number"}.issubset(vals):
            return "integer_or_number"
        if vals == {"integer"}:
            return "integer"
        if vals == {"number"}:
            return "number"
        if "number" in vals:
            return "number"
        if "integer" in vals:
            return "integer"
        return "other"
    return "other"


def normalize_numeric_target(value: str) -> str:
    if value in {"integer", "number", "integer_or_number", "absent"}:
        return value
    return "other"


def child_inherited_type(parent_type: str, child_keyword: str) -> str | None:
    if child_keyword in {"allOf", "anyOf", "oneOf", "not"}:
        return None if parent_type == "absent" else parent_type
    return None


def regex_complexity(pattern: str) -> int:
    return (
        len(pattern)
        + 2 * pattern.count("|")
        + 2 * pattern.count("*")
        + 2 * pattern.count("+")
        + 2 * pattern.count("?")
        + 2 * pattern.count("[")
        + 2 * pattern.count("(")
    )


def type_set(type_value: Any) -> set[str]:
    if isinstance(type_value, str):
        return {type_value}
    if isinstance(type_value, list):
        return {str(v) for v in type_value}
    return set()


def contains_keyword(node: Any, keyword: str) -> bool:
    if isinstance(node, dict):
        if keyword in node:
            return True
        return any(contains_keyword(value, keyword) for value in node.values())
    if isinstance(node, list):
        return any(contains_keyword(value, keyword) for value in node)
    return False


def direct_properties(branch: Any) -> set[str]:
    if isinstance(branch, dict) and isinstance(branch.get("properties"), dict):
        return set(str(k) for k in branch["properties"])
    return set()


def required_names(node: Any) -> set[str]:
    if isinstance(node, dict) and isinstance(node.get("required"), list):
        return {str(value) for value in node["required"]}
    return set()


def additional_properties_value(node: dict[str, Any]) -> str:
    additional = node.get("additionalProperties", "__absent__")
    if additional == "__absent__":
        return "absent"
    if isinstance(additional, bool):
        return "true" if additional else "false"
    return "schema"


def schema_bound_bucket(has_lower: bool, has_upper: bool) -> str:
    if has_lower and has_upper:
        return "min_and_max"
    if has_lower:
        return "min_only"
    if has_upper:
        return "max_only"
    return "absent"


def analyze_schema(schema: Any) -> dict[str, Any]:
    numeric_occurrences: list[dict[str, Any]] = []
    pattern_contexts: list[dict[str, Any]] = []
    not_contexts: list[dict[str, Any]] = []
    combinator_contexts: list[dict[str, Any]] = []
    object_contexts: list[dict[str, Any]] = []
    enum_contexts: list[dict[str, Any]] = []
    const_contexts: list[dict[str, Any]] = []
    string_contexts: list[dict[str, Any]] = []
    array_contexts: list[dict[str, Any]] = []
    complex_counts: list[int] = []
    local_pairs = {name: False for name in LOCAL_PAIR_FEATURES}
    cooccurrence_counts: Counter[tuple[str, str]] = Counter()

    def visit(node: Any, depth: int, parent_keyword: str, inherited_type: str | None, prop_required: bool) -> None:
        if isinstance(node, bool):
            return
        if not isinstance(node, dict):
            if isinstance(node, list):
                for item in node:
                    visit(item, depth + 1, "other", None, False)
            return

        keys = set(node)
        present_complex = [key for key in COMPLEX_KEYWORDS if key in keys]
        complex_counts.append(len(present_complex))
        for i, key_a in enumerate(present_complex):
            for key_b in present_complex[i + 1 :]:
                cooccurrence_counts[(key_a, key_b)] += 1
        local_pairs["same_node_not_and_enum"] |= "not" in keys and "enum" in keys
        local_pairs["same_node_not_and_type"] |= "not" in keys and "type" in keys
        local_pairs["same_node_not_and_pattern"] |= "not" in keys and "pattern" in keys
        local_pairs["same_node_allOf_and_not"] |= "allOf" in keys and "not" in keys
        local_pairs["same_node_allOf_and_required"] |= "allOf" in keys and "required" in keys
        local_pairs["same_node_allOf_and_properties"] |= "allOf" in keys and "properties" in keys
        local_pairs["same_node_oneOf_and_required"] |= "oneOf" in keys and "required" in keys
        local_pairs["same_node_not_and_properties"] |= "not" in keys and "properties" in keys
        local_pairs["same_node_not_and_required"] |= "not" in keys and "required" in keys
        local_pairs["same_node_patternProperties_and_additionalProperties"] |= "patternProperties" in keys and "additionalProperties" in keys
        local_pairs["same_node_properties_and_patternProperties"] |= "properties" in keys and "patternProperties" in keys
        local_pairs["same_node_properties_and_required"] |= "properties" in keys and "required" in keys
        local_pairs["same_node_properties_and_additionalProperties"] |= "properties" in keys and "additionalProperties" in keys
        local_pairs["same_node_minProperties_and_required"] |= "minProperties" in keys and "required" in keys
        local_pairs["same_node_combinator_and_patternProperties"] |= any(k in keys for k in COMBINATORS) and "patternProperties" in keys
        local_pairs["same_node_combinator_and_numeric"] |= any(k in keys for k in COMBINATORS) and any(k in keys for k in NUMERIC_KEYWORDS)
        local_pairs["same_node_combinator_and_required"] |= any(k in keys for k in COMBINATORS) and "required" in keys
        local_pairs["same_node_combinator_and_properties"] |= any(k in keys for k in COMBINATORS) and "properties" in keys

        node_type = schema_type_value(node, inherited_type)
        numeric_here = [key for key in NUMERIC_KEYWORDS if key in node]
        for keyword in numeric_here:
            numeric_occurrences.append(
                {
                    "keyword": keyword,
                    "target_type": normalize_numeric_target(node_type),
                    "parent_keyword": parent_keyword,
                    "depth": depth,
                    "in_properties": parent_keyword == "properties",
                    "property_required": bool(prop_required),
                    "has_default": "default" in node,
                    "has_min_and_max": any(k in node for k in LOWER_NUMERIC) and any(k in node for k in UPPER_NUMERIC),
                }
            )

        if any(key in node for key in OBJECT_KEYWORDS) or node_type == "object":
            props = node.get("properties") if isinstance(node.get("properties"), dict) else {}
            required = required_names(node)
            object_contexts.append(
                {
                    "parent_keyword": parent_keyword,
                    "target_type": node_type,
                    "properties_count": len(props),
                    "required_count": len(required),
                    "additionalProperties_value": additional_properties_value(node),
                    "has_minProperties": "minProperties" in node,
                    "has_maxProperties": "maxProperties" in node,
                    "has_min_and_max_properties": "minProperties" in node and "maxProperties" in node,
                    "has_propertyNames": "propertyNames" in node,
                    "required_subset_of_properties": bool(required) and required.issubset({str(key) for key in props}),
                    "depth": depth,
                }
            )

        if "enum" in node and isinstance(node.get("enum"), list):
            enum_contexts.append(
                {
                    "target_type": node_type,
                    "parent_keyword": parent_keyword,
                    "enum_size": len(node["enum"]),
                    "contains_null": any(value is None for value in node["enum"]),
                    "contains_mixed_types": len({type(value).__name__ for value in node["enum"]}) > 1,
                    "depth": depth,
                }
            )

        if "const" in node:
            const_value = node.get("const")
            const_contexts.append(
                {
                    "target_type": node_type,
                    "parent_keyword": parent_keyword,
                    "const_type": type(const_value).__name__,
                    "depth": depth,
                }
            )

        if any(key in node for key in STRING_KEYWORDS) or node_type == "string":
            string_contexts.append(
                {
                    "parent_keyword": parent_keyword,
                    "target_type": node_type,
                    "has_pattern": "pattern" in node,
                    "has_minLength": "minLength" in node,
                    "has_maxLength": "maxLength" in node,
                    "has_min_and_max_length": "minLength" in node and "maxLength" in node,
                    "has_format": "format" in node,
                    "format_value": str(node.get("format", "absent")),
                    "pattern_complexity": regex_complexity(str(node.get("pattern", ""))) if "pattern" in node else 0,
                    "depth": depth,
                }
            )

        if any(key in node for key in ARRAY_KEYWORDS) or node_type == "array":
            items = node.get("items", "__absent__")
            if isinstance(items, list):
                items_kind = "list"
            elif isinstance(items, dict):
                items_kind = "schema"
            elif items == "__absent__":
                items_kind = "absent"
            else:
                items_kind = "other"
            array_contexts.append(
                {
                    "parent_keyword": parent_keyword,
                    "target_type": node_type,
                    "items_kind": items_kind,
                    "prefixItems_count": len(node["prefixItems"]) if isinstance(node.get("prefixItems"), list) else 0,
                    "has_minItems": "minItems" in node,
                    "has_maxItems": "maxItems" in node,
                    "has_min_and_max_items": "minItems" in node and "maxItems" in node,
                    "has_uniqueItems": bool(node.get("uniqueItems")) if "uniqueItems" in node else False,
                    "has_contains": "contains" in node,
                    "has_minContains": "minContains" in node,
                    "has_maxContains": "maxContains" in node,
                    "depth": depth,
                }
            )

        if isinstance(node.get("patternProperties"), dict):
            additional_value = additional_properties_value(node)
            patterns = [str(p) for p in node["patternProperties"]]
            pattern_contexts.append(
                {
                    "pattern_count": len(patterns),
                    "with_properties": isinstance(node.get("properties"), dict),
                    "has_additionalProperties": "additionalProperties" in node,
                    "additionalProperties_value": additional_value,
                    "regex_has_anchor": any("^" in p or "$" in p for p in patterns),
                    "regex_has_dotstar": any(".*" in p for p in patterns),
                    "regex_has_alternation": any("|" in p for p in patterns),
                    "regex_has_charclass": any("[" in p and "]" in p for p in patterns),
                    "regex_complexity_score": sum(regex_complexity(p) for p in patterns),
                }
            )

        if "not" in node:
            sub = node.get("not")
            target = "absent"
            if isinstance(sub, dict):
                target = schema_type_value(sub, None)
            not_contexts.append(
                {
                    "depth": depth,
                    "parent_keyword": parent_keyword,
                    "target_type": target if target in {"string", "number", "integer", "object", "array", "boolean", "null", "absent"} else "mixed",
                    "contains_enum": contains_keyword(sub, "enum"),
                    "contains_const": contains_keyword(sub, "const"),
                    "contains_pattern": contains_keyword(sub, "pattern"),
                    "contains_properties": contains_keyword(sub, "properties"),
                    "contains_required": contains_keyword(sub, "required"),
                    "contains_numeric": any(contains_keyword(sub, keyword) for keyword in NUMERIC_KEYWORDS),
                    "contains_anyOf": contains_keyword(sub, "anyOf"),
                    "contains_allOf": contains_keyword(sub, "allOf"),
                    "contains_oneOf": contains_keyword(sub, "oneOf"),
                    "sibling_keyword_count": len([key for key in node if key != "not"]),
                }
            )

        for combinator in COMBINATORS:
            branches = node.get(combinator)
            if not isinstance(branches, list):
                continue
            declared_types = [type_set(branch.get("type")) for branch in branches if isinstance(branch, dict) and branch.get("type") is not None]
            flat_declared = [tuple(sorted(t)) for t in declared_types if t]
            same_type = len(set(flat_declared)) <= 1 if flat_declared else True
            conflicting = False
            if combinator == "allOf" and declared_types:
                intersection = set.intersection(*declared_types) if declared_types else set()
                conflicting = not intersection and len(declared_types) >= 2
            prop_sets = [direct_properties(branch) for branch in branches]
            overlapping = False
            seen_props: set[str] = set()
            for props in prop_sets:
                if seen_props.intersection(props):
                    overlapping = True
                seen_props.update(props)
            combinator_contexts.append(
                {
                    "type": combinator,
                    "depth": depth,
                    "branch_count": len(branches),
                    "branches_have_same_type": same_type,
                    "branches_conflicting_types": conflicting,
                    "branches_have_required": any(contains_keyword(branch, "required") for branch in branches),
                    "branches_have_properties": any(contains_keyword(branch, "properties") for branch in branches),
                    "branches_have_not": any(contains_keyword(branch, "not") for branch in branches),
                    "branches_have_enum": any(contains_keyword(branch, "enum") for branch in branches),
                    "branches_have_const": any(contains_keyword(branch, "const") for branch in branches),
                    "branches_have_pattern": any(contains_keyword(branch, "pattern") for branch in branches),
                    "branches_have_numeric": any(any(contains_keyword(branch, keyword) for keyword in NUMERIC_KEYWORDS) for branch in branches),
                    "branches_have_object_bounds": any(contains_keyword(branch, "minProperties") or contains_keyword(branch, "maxProperties") for branch in branches),
                    "branches_overlapping_properties": overlapping,
                }
            )

        for key, value in node.items():
            next_inherited = child_inherited_type(node_type, key)
            if key == "properties" and isinstance(value, dict):
                required = set(str(x) for x in node.get("required", []) if isinstance(node.get("required"), list))
                for prop_name, sub in value.items():
                    visit(sub, depth + 2, "properties", None, str(prop_name) in required)
            elif key in {"patternProperties", "$defs", "definitions", "dependentSchemas"} and isinstance(value, dict):
                keyword = "$defs" if key in {"$defs", "definitions"} else key
                for sub in value.values():
                    visit(sub, depth + 2, keyword, None, False)
            elif key in COMBINATORS and isinstance(value, list):
                for sub in value:
                    visit(sub, depth + 2, key, next_inherited, False)
            elif key == "prefixItems" and isinstance(value, list):
                for sub in value:
                    visit(sub, depth + 2, "prefixItems", None, False)
            elif key == "items":
                if isinstance(value, list):
                    for sub in value:
                        visit(sub, depth + 2, "items", None, False)
                else:
                    visit(value, depth + 1, "items", None, False)
            elif key in {"not", "additionalProperties", "propertyNames", "contains", "if", "then", "else", "unevaluatedItems", "unevaluatedProperties"}:
                visit(value, depth + 1, key, next_inherited, False)
            elif isinstance(value, (dict, list)) and key not in {"enum", "const", "default", "examples"}:
                visit(value, depth + 1, "other", None, False)

    visit(schema, 0, "root", None, False)

    numeric_keywords = [occ["keyword"] for occ in numeric_occurrences]
    numeric_depths = [occ["depth"] for occ in numeric_occurrences]
    pattern_complexities = [ctx["regex_complexity_score"] for ctx in pattern_contexts]
    not_depths = [ctx["depth"] for ctx in not_contexts]
    comb_depths = [ctx["depth"] for ctx in combinator_contexts]
    branch_counts = [ctx["branch_count"] for ctx in combinator_contexts]
    object_depths = [ctx["depth"] for ctx in object_contexts]
    object_property_counts = [ctx["properties_count"] for ctx in object_contexts]
    object_required_counts = [ctx["required_count"] for ctx in object_contexts]
    enum_sizes = [ctx["enum_size"] for ctx in enum_contexts]
    string_complexities = [ctx["pattern_complexity"] for ctx in string_contexts]
    array_prefix_counts = [ctx["prefixItems_count"] for ctx in array_contexts]

    features: dict[str, Any] = {
        "numeric_keyword_count": len(numeric_occurrences),
        "numeric_keywords_present": "|".join(sorted(set(numeric_keywords))),
        "numeric_target_type": aggregate_value([occ["target_type"] for occ in numeric_occurrences]),
        "numeric_is_in_properties": bool_any([occ["in_properties"] for occ in numeric_occurrences]),
        "numeric_property_required": bool_any([occ["property_required"] for occ in numeric_occurrences]),
        "numeric_has_default": bool_any([occ["has_default"] for occ in numeric_occurrences]),
        "numeric_has_min_and_max": bool_any([occ["has_min_and_max"] for occ in numeric_occurrences]),
        "numeric_parent_keyword": aggregate_value([occ["parent_keyword"] for occ in numeric_occurrences], mixed="mixed"),
        "numeric_depth": max(numeric_depths) if numeric_depths else 0,
        "patternProperties_occurrence_count": len(pattern_contexts),
        "patternProperties_pattern_count": sum(ctx["pattern_count"] for ctx in pattern_contexts),
        "patternProperties_with_properties": bool_any([ctx["with_properties"] for ctx in pattern_contexts]),
        "patternProperties_has_additionalProperties": bool_any([ctx["has_additionalProperties"] for ctx in pattern_contexts]),
        "additionalProperties_value": aggregate_value([ctx["additionalProperties_value"] for ctx in pattern_contexts]),
        "patternProperties_regex_has_anchor": bool_any([ctx["regex_has_anchor"] for ctx in pattern_contexts]),
        "patternProperties_regex_has_dotstar": bool_any([ctx["regex_has_dotstar"] for ctx in pattern_contexts]),
        "patternProperties_regex_has_alternation": bool_any([ctx["regex_has_alternation"] for ctx in pattern_contexts]),
        "patternProperties_regex_has_charclass": bool_any([ctx["regex_has_charclass"] for ctx in pattern_contexts]),
        "patternProperties_regex_complexity_score": sum(pattern_complexities),
        "not_count": len(not_contexts),
        "not_depth_min": min(not_depths) if not_depths else 0,
        "not_depth_max": max(not_depths) if not_depths else 0,
        "not_depth_avg": mean([float(v) for v in not_depths]),
        "not_parent_keyword": aggregate_value([ctx["parent_keyword"] for ctx in not_contexts], mixed="mixed"),
        "not_target_type": aggregate_value([ctx["target_type"] for ctx in not_contexts], mixed="mixed"),
        "not_contains_enum": bool_any([ctx["contains_enum"] for ctx in not_contexts]),
        "not_contains_const": bool_any([ctx["contains_const"] for ctx in not_contexts]),
        "not_contains_pattern": bool_any([ctx["contains_pattern"] for ctx in not_contexts]),
        "not_contains_properties": bool_any([ctx["contains_properties"] for ctx in not_contexts]),
        "not_contains_required": bool_any([ctx["contains_required"] for ctx in not_contexts]),
        "not_contains_numeric": bool_any([ctx["contains_numeric"] for ctx in not_contexts]),
        "not_contains_anyOf": bool_any([ctx["contains_anyOf"] for ctx in not_contexts]),
        "not_contains_allOf": bool_any([ctx["contains_allOf"] for ctx in not_contexts]),
        "not_contains_oneOf": bool_any([ctx["contains_oneOf"] for ctx in not_contexts]),
        "not_sibling_keyword_count": max([ctx["sibling_keyword_count"] for ctx in not_contexts], default=0),
        "allOf_count": sum(1 for ctx in combinator_contexts if ctx["type"] == "allOf"),
        "anyOf_count": sum(1 for ctx in combinator_contexts if ctx["type"] == "anyOf"),
        "oneOf_count": sum(1 for ctx in combinator_contexts if ctx["type"] == "oneOf"),
        "combinator_count": len(combinator_contexts),
        "combinator_type": aggregate_value([ctx["type"] for ctx in combinator_contexts], mixed="mixed"),
        "combinator_depth_min": min(comb_depths) if comb_depths else 0,
        "combinator_depth_max": max(comb_depths) if comb_depths else 0,
        "combinator_depth_avg": mean([float(v) for v in comb_depths]),
        "combinator_branch_count_min": min(branch_counts) if branch_counts else 0,
        "combinator_branch_count_max": max(branch_counts) if branch_counts else 0,
        "combinator_branch_count_avg": mean([float(v) for v in branch_counts]),
        "branches_have_same_type": bool_any([ctx["branches_have_same_type"] for ctx in combinator_contexts]),
        "branches_conflicting_types": bool_any([ctx["branches_conflicting_types"] for ctx in combinator_contexts]),
        "branches_have_required": bool_any([ctx["branches_have_required"] for ctx in combinator_contexts]),
        "branches_have_properties": bool_any([ctx["branches_have_properties"] for ctx in combinator_contexts]),
        "branches_have_not": bool_any([ctx["branches_have_not"] for ctx in combinator_contexts]),
        "branches_have_enum": bool_any([ctx["branches_have_enum"] for ctx in combinator_contexts]),
        "branches_have_const": bool_any([ctx["branches_have_const"] for ctx in combinator_contexts]),
        "branches_have_pattern": bool_any([ctx["branches_have_pattern"] for ctx in combinator_contexts]),
        "branches_have_numeric": bool_any([ctx["branches_have_numeric"] for ctx in combinator_contexts]),
        "branches_have_object_bounds": bool_any([ctx["branches_have_object_bounds"] for ctx in combinator_contexts]),
        "branches_overlapping_properties": bool_any([ctx["branches_overlapping_properties"] for ctx in combinator_contexts]),
        "object_context_count": len(object_contexts),
        "object_parent_keyword": aggregate_value([ctx["parent_keyword"] for ctx in object_contexts], mixed="mixed"),
        "object_target_type": aggregate_value([ctx["target_type"] for ctx in object_contexts], mixed="mixed"),
        "object_properties_count_max": max(object_property_counts, default=0),
        "object_required_count_max": max(object_required_counts, default=0),
        "object_additionalProperties_value": aggregate_value([ctx["additionalProperties_value"] for ctx in object_contexts], mixed="mixed"),
        "object_has_minProperties": bool_any([ctx["has_minProperties"] for ctx in object_contexts]),
        "object_has_maxProperties": bool_any([ctx["has_maxProperties"] for ctx in object_contexts]),
        "object_has_min_and_max_properties": bool_any([ctx["has_min_and_max_properties"] for ctx in object_contexts]),
        "object_has_propertyNames": bool_any([ctx["has_propertyNames"] for ctx in object_contexts]),
        "object_required_subset_of_properties": bool_any([ctx["required_subset_of_properties"] for ctx in object_contexts]),
        "object_depth_max": max(object_depths, default=0),
        "enum_context_count": len(enum_contexts),
        "enum_target_type": aggregate_value([ctx["target_type"] for ctx in enum_contexts], mixed="mixed"),
        "enum_parent_keyword": aggregate_value([ctx["parent_keyword"] for ctx in enum_contexts], mixed="mixed"),
        "enum_size_max": max(enum_sizes, default=0),
        "enum_contains_null": bool_any([ctx["contains_null"] for ctx in enum_contexts]),
        "enum_contains_mixed_types": bool_any([ctx["contains_mixed_types"] for ctx in enum_contexts]),
        "const_context_count": len(const_contexts),
        "const_target_type": aggregate_value([ctx["target_type"] for ctx in const_contexts], mixed="mixed"),
        "const_parent_keyword": aggregate_value([ctx["parent_keyword"] for ctx in const_contexts], mixed="mixed"),
        "const_type": aggregate_value([ctx["const_type"] for ctx in const_contexts], mixed="mixed"),
        "string_context_count": len(string_contexts),
        "string_parent_keyword": aggregate_value([ctx["parent_keyword"] for ctx in string_contexts], mixed="mixed"),
        "string_target_type": aggregate_value([ctx["target_type"] for ctx in string_contexts], mixed="mixed"),
        "string_has_pattern": bool_any([ctx["has_pattern"] for ctx in string_contexts]),
        "string_has_minLength": bool_any([ctx["has_minLength"] for ctx in string_contexts]),
        "string_has_maxLength": bool_any([ctx["has_maxLength"] for ctx in string_contexts]),
        "string_has_min_and_max_length": bool_any([ctx["has_min_and_max_length"] for ctx in string_contexts]),
        "string_has_format": bool_any([ctx["has_format"] for ctx in string_contexts]),
        "string_format_value": aggregate_value([ctx["format_value"] for ctx in string_contexts], mixed="mixed"),
        "string_pattern_complexity_score": sum(string_complexities),
        "array_context_count": len(array_contexts),
        "array_parent_keyword": aggregate_value([ctx["parent_keyword"] for ctx in array_contexts], mixed="mixed"),
        "array_target_type": aggregate_value([ctx["target_type"] for ctx in array_contexts], mixed="mixed"),
        "array_items_kind": aggregate_value([ctx["items_kind"] for ctx in array_contexts], mixed="mixed"),
        "array_prefixItems_count_max": max(array_prefix_counts, default=0),
        "array_has_minItems": bool_any([ctx["has_minItems"] for ctx in array_contexts]),
        "array_has_maxItems": bool_any([ctx["has_maxItems"] for ctx in array_contexts]),
        "array_has_min_and_max_items": bool_any([ctx["has_min_and_max_items"] for ctx in array_contexts]),
        "array_has_uniqueItems": bool_any([ctx["has_uniqueItems"] for ctx in array_contexts]),
        "array_has_contains": bool_any([ctx["has_contains"] for ctx in array_contexts]),
        "array_has_minContains": bool_any([ctx["has_minContains"] for ctx in array_contexts]),
        "array_has_maxContains": bool_any([ctx["has_maxContains"] for ctx in array_contexts]),
        "complex_keywords_same_node_max": max(complex_counts, default=0),
        "complex_keywords_same_node_avg": mean([float(v) for v in complex_counts]),
        "local_cooccurrence_pairs": "|".join(f"{a}+{b}:{n}" for (a, b), n in sorted(cooccurrence_counts.items())),
    }
    for keyword in NUMERIC_KEYWORDS:
        features[f"has_{keyword}"] = keyword in numeric_keywords
    features["has_patternProperties"] = bool(pattern_contexts)
    features["has_not"] = bool(not_contexts)
    for combinator in COMBINATORS:
        features[f"has_{combinator}"] = features[f"{combinator}_count"] > 0
    features.update(local_pairs)
    return features


def count_numeric_values(instance: Any) -> int:
    if is_number(instance):
        return 1
    if isinstance(instance, dict):
        return sum(count_numeric_values(value) for value in instance.values())
    if isinstance(instance, list):
        return sum(count_numeric_values(value) for value in instance)
    return 0


def boundary_case_for_value(value: float, schema_node: dict[str, Any]) -> str:
    if "multipleOf" in schema_node:
        divisor = schema_node.get("multipleOf")
        if is_number(divisor) and divisor != 0:
            quotient = value / divisor
            if abs(quotient - round(quotient)) < 1e-9:
                return "multiple_ok"
            return "multiple_violation"
    lower_hit = False
    upper_hit = False
    if "minimum" in schema_node and is_number(schema_node["minimum"]):
        if value < schema_node["minimum"]:
            return "below_min"
        if value == schema_node["minimum"]:
            return "equal_min"
        lower_hit = True
    if "exclusiveMinimum" in schema_node and is_number(schema_node["exclusiveMinimum"]):
        if value <= schema_node["exclusiveMinimum"]:
            return "below_min" if value < schema_node["exclusiveMinimum"] else "equal_min"
        lower_hit = True
    if "maximum" in schema_node and is_number(schema_node["maximum"]):
        if value > schema_node["maximum"]:
            return "above_max"
        if value == schema_node["maximum"]:
            return "equal_max"
        upper_hit = True
    if "exclusiveMaximum" in schema_node and is_number(schema_node["exclusiveMaximum"]):
        if value >= schema_node["exclusiveMaximum"]:
            return "above_max" if value > schema_node["exclusiveMaximum"] else "equal_max"
        upper_hit = True
    if lower_hit or upper_hit:
        return "inside_range"
    return "unknown"


def select_boundary_case(cases: list[str], schema_has_numeric: bool) -> str:
    if not cases:
        return "not_applicable" if schema_has_numeric else "not_applicable"
    for preferred in ("below_min", "above_max", "multiple_violation", "equal_min", "equal_max", "outside_range", "inside_range", "multiple_ok"):
        if preferred in cases:
            return preferred
    return cases[0] if cases else "unknown"


def select_preferred(cases: list[str], preferred: tuple[str, ...], empty_value: str) -> str:
    if not cases:
        return empty_value
    for value in preferred:
        if value in cases:
            return value
    return cases[0]


def instance_type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, str):
        return "string"
    if isinstance(value, int) and not isinstance(value, bool):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    return "other"


def json_hashable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def make_validator(root_schema: Any, subschema: Any):
    cls = validators.validator_for(root_schema)
    resolver = RefResolver.from_schema(root_schema)
    return cls(subschema, resolver=resolver)


def is_valid_subschema(root_schema: Any, subschema: Any, instance: Any) -> bool | None:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            make_validator(root_schema, subschema).validate(instance)
        return True
    except ValidationError:
        return False
    except Exception:
        return None


def analyze_instance(schema: Any, instance: Any, schema_features: dict[str, Any]) -> dict[str, Any]:
    boundary_cases: list[str] = []
    object_required_cases: list[str] = []
    object_property_bound_cases: list[str] = []
    object_additional_cases: list[str] = []
    object_missing_required_counts: list[int] = []
    object_extra_property_counts: list[int] = []
    enum_cases: list[str] = []
    const_cases: list[str] = []
    string_cases: list[str] = []
    array_cases: list[str] = []
    array_invalid_item_counts: list[int] = []
    pattern_key_matches = 0
    has_unmatched_keys = False
    not_satisfies: list[bool] = []
    satisfied_counts: dict[str, list[int]] = {key: [] for key in COMBINATORS}
    branch_counts: dict[str, list[int]] = {key: [] for key in COMBINATORS}

    def visit(schema_node: Any, inst: Any) -> None:
        nonlocal pattern_key_matches, has_unmatched_keys
        if isinstance(schema_node, bool):
            return
        if not isinstance(schema_node, dict):
            return
        if any(key in schema_node for key in NUMERIC_KEYWORDS) and is_number(inst):
            boundary_cases.append(boundary_case_for_value(float(inst), schema_node))

        if "enum" in schema_node and isinstance(schema_node.get("enum"), list):
            enum_cases.append("enum_match" if any(inst == value for value in schema_node["enum"]) else "enum_mismatch")

        if "const" in schema_node:
            const_cases.append("const_match" if inst == schema_node.get("const") else "const_mismatch")

        if any(key in schema_node for key in STRING_KEYWORDS):
            if isinstance(inst, str):
                hit = False
                if "minLength" in schema_node and is_number(schema_node["minLength"]) and len(inst) < int(schema_node["minLength"]):
                    string_cases.append("too_short")
                    hit = True
                if "maxLength" in schema_node and is_number(schema_node["maxLength"]) and len(inst) > int(schema_node["maxLength"]):
                    string_cases.append("too_long")
                    hit = True
                if "pattern" in schema_node:
                    try:
                        if re.search(str(schema_node["pattern"]), inst) is None:
                            string_cases.append("pattern_violation")
                            hit = True
                    except re.error:
                        string_cases.append("pattern_regex_error")
                        hit = True
                if "format" in schema_node and not hit:
                    string_cases.append("format_present")
                    hit = True
                if not hit:
                    string_cases.append("inside_string_constraints")
            else:
                string_cases.append("not_string")

        if "not" in schema_node:
            ok = is_valid_subschema(schema, schema_node.get("not"), inst)
            if ok is not None:
                not_satisfies.append(ok)

        for combinator in COMBINATORS:
            branches = schema_node.get(combinator)
            if isinstance(branches, list):
                count = 0
                for branch in branches:
                    ok = is_valid_subschema(schema, branch, inst)
                    if ok is True:
                        count += 1
                satisfied_counts[combinator].append(count)
                branch_counts[combinator].append(len(branches))

        if isinstance(inst, dict):
            properties = schema_node.get("properties") if isinstance(schema_node.get("properties"), dict) else {}
            pattern_properties = schema_node.get("patternProperties") if isinstance(schema_node.get("patternProperties"), dict) else {}
            compiled_patterns: list[tuple[re.Pattern[str], Any]] = []
            for raw_pattern, subschema in pattern_properties.items():
                try:
                    compiled_patterns.append((re.compile(str(raw_pattern)), subschema))
                except re.error:
                    continue

            required = required_names(schema_node)
            if required:
                missing = sorted(required - {str(key) for key in inst})
                object_missing_required_counts.append(len(missing))
                object_required_cases.append("missing_required" if missing else "all_required_present")

            if "minProperties" in schema_node or "maxProperties" in schema_node:
                prop_count = len(inst)
                if "minProperties" in schema_node and is_number(schema_node["minProperties"]) and prop_count < int(schema_node["minProperties"]):
                    object_property_bound_cases.append("below_minProperties")
                elif "maxProperties" in schema_node and is_number(schema_node["maxProperties"]) and prop_count > int(schema_node["maxProperties"]):
                    object_property_bound_cases.append("above_maxProperties")
                else:
                    object_property_bound_cases.append("inside_property_count_bounds")

            if properties or compiled_patterns:
                local_extra = 0
                for key, value in inst.items():
                    matched_named = key in properties
                    matched_patterns = [(pattern, sub) for pattern, sub in compiled_patterns if pattern.search(key)]
                    if matched_patterns:
                        pattern_key_matches += 1
                    if not matched_named and not matched_patterns:
                        has_unmatched_keys = True
                        local_extra += 1
                    if matched_named:
                        visit(properties[key], value)
                    for _, sub in matched_patterns:
                        visit(sub, value)
                object_extra_property_counts.append(local_extra)
                if local_extra:
                    additional = schema_node.get("additionalProperties", "__absent__")
                    if additional is False:
                        object_additional_cases.append("extra_disallowed")
                    elif isinstance(additional, dict):
                        object_additional_cases.append("extra_validated_by_schema")
                    else:
                        object_additional_cases.append("extra_allowed_or_absent")
                else:
                    object_additional_cases.append("no_extra_properties")
            if isinstance(schema_node.get("additionalProperties"), dict):
                for key, value in inst.items():
                    if key not in properties and not any(pattern.search(key) for pattern, _ in compiled_patterns):
                        visit(schema_node["additionalProperties"], value)
        elif any(key in schema_node for key in OBJECT_KEYWORDS):
            object_required_cases.append("not_object")
            object_property_bound_cases.append("not_object")
            object_additional_cases.append("not_object")

        if isinstance(inst, list):
            if any(key in schema_node for key in ARRAY_KEYWORDS):
                hit = False
                if "minItems" in schema_node and is_number(schema_node["minItems"]) and len(inst) < int(schema_node["minItems"]):
                    array_cases.append("below_minItems")
                    hit = True
                if "maxItems" in schema_node and is_number(schema_node["maxItems"]) and len(inst) > int(schema_node["maxItems"]):
                    array_cases.append("above_maxItems")
                    hit = True
                if schema_node.get("uniqueItems") is True:
                    serialized = [json_hashable(value) for value in inst]
                    if len(serialized) != len(set(serialized)):
                        array_cases.append("uniqueItems_violation")
                        hit = True
                invalid_items = 0
                if isinstance(schema_node.get("prefixItems"), list):
                    for sub, value in zip(schema_node["prefixItems"], inst):
                        ok = is_valid_subschema(schema, sub, value)
                        if ok is False:
                            invalid_items += 1
                items = schema_node.get("items")
                if isinstance(items, dict):
                    for value in inst:
                        ok = is_valid_subschema(schema, items, value)
                        if ok is False:
                            invalid_items += 1
                if invalid_items:
                    array_invalid_item_counts.append(invalid_items)
                    array_cases.append("items_violation")
                    hit = True
                if "contains" in schema_node:
                    contains_ok = any(is_valid_subschema(schema, schema_node["contains"], value) is True for value in inst)
                    if not contains_ok:
                        array_cases.append("contains_violation")
                        hit = True
                if not hit:
                    array_cases.append("inside_array_constraints")
            if isinstance(schema_node.get("prefixItems"), list):
                for sub, value in zip(schema_node["prefixItems"], inst):
                    visit(sub, value)
            items = schema_node.get("items")
            if isinstance(items, dict):
                for value in inst:
                    visit(items, value)
            elif isinstance(items, list):
                for sub, value in zip(items, inst):
                    visit(sub, value)
        elif any(key in schema_node for key in ARRAY_KEYWORDS):
            array_cases.append("not_array")

        for key in COMBINATORS:
            if isinstance(schema_node.get(key), list):
                for branch in schema_node[key]:
                    visit(branch, inst)
        if "not" in schema_node:
            visit(schema_node["not"], inst)

    visit(schema, instance)

    out = {
        "instance_type": instance_type_name(instance),
        "instance_num_numeric_values": count_numeric_values(instance),
        "numeric_boundary_case": select_boundary_case(boundary_cases, bool(schema_features.get("numeric_keyword_count"))),
        "instance_num_properties": len(instance) if isinstance(instance, dict) else 0,
        "object_required_case": select_preferred(
            object_required_cases,
            ("missing_required", "all_required_present", "not_object"),
            "not_applicable",
        ),
        "object_missing_required_count": max(object_missing_required_counts, default=0),
        "object_property_count_boundary_case": select_preferred(
            object_property_bound_cases,
            ("below_minProperties", "above_maxProperties", "inside_property_count_bounds", "not_object"),
            "not_applicable",
        ),
        "object_additional_properties_case": select_preferred(
            object_additional_cases,
            ("extra_disallowed", "extra_validated_by_schema", "extra_allowed_or_absent", "no_extra_properties", "not_object"),
            "not_applicable",
        ),
        "object_extra_properties_count": max(object_extra_property_counts, default=0),
        "enum_validation_case": select_preferred(enum_cases, ("enum_mismatch", "enum_match"), "not_applicable"),
        "const_validation_case": select_preferred(const_cases, ("const_mismatch", "const_match"), "not_applicable"),
        "string_validation_case": select_preferred(
            string_cases,
            ("too_short", "too_long", "pattern_violation", "pattern_regex_error", "format_present", "inside_string_constraints", "not_string"),
            "not_applicable",
        ),
        "array_validation_case": select_preferred(
            array_cases,
            ("below_minItems", "above_maxItems", "uniqueItems_violation", "items_violation", "contains_violation", "inside_array_constraints", "not_array"),
            "not_applicable",
        ),
        "array_invalid_items_count": max(array_invalid_item_counts, default=0),
        "instance_matching_pattern_keys_count": pattern_key_matches,
        "instance_has_unmatched_keys": has_unmatched_keys,
        "instance_satisfies_not_subschema": "true" if any(not_satisfies) else "false" if not_satisfies else "unknown",
    }
    for combinator in COMBINATORS:
        out[f"{combinator}_satisfied_branch_count"] = max(satisfied_counts[combinator], default=0)
        out[f"{combinator}_matched_branch_count"] = out[f"{combinator}_satisfied_branch_count"]
        out[f"{combinator}_branch_count"] = max(branch_counts[combinator], default=0)
        branch_count = out[f"{combinator}_branch_count"]
        out[f"{combinator}_satisfied_branch_ratio"] = (
            out[f"{combinator}_satisfied_branch_count"] / branch_count if branch_count else 0.0
        )
    return out


def expected_is_valid(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).lower() == "valid"


def failure_type(expected_valid: bool, accepted: bool) -> str:
    if expected_valid and accepted:
        return "CORRECT_VALID"
    if (not expected_valid) and (not accepted):
        return "CORRECT_INVALID"
    if (not expected_valid) and accepted:
        return "UNDER"
    return "OVER"


def count_status(rows: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "under_test_count": sum(1 for row in rows if row["failure_type"] == "UNDER"),
        "over_test_count": sum(1 for row in rows if row["failure_type"] == "OVER"),
        "correct_test_count": sum(1 for row in rows if row["failure_type"].startswith("CORRECT")),
        "total_test_count": len(rows),
    }


def bucket_count(value: Any) -> str:
    try:
        n = int(float(value))
    except (TypeError, ValueError):
        return "unknown"
    if n <= 0:
        return "0"
    if n == 1:
        return "1"
    if n == 2:
        return "2"
    if n == 3:
        return "3"
    if n <= 5:
        return "4-5"
    return "6+"


def add_buckets(row: dict[str, Any]) -> None:
    row["instance_matching_pattern_keys_count_bucket"] = bucket_count(row.get("instance_matching_pattern_keys_count"))
    row["object_properties_count_bucket"] = bucket_count(row.get("object_properties_count_max"))
    row["object_required_count_bucket"] = bucket_count(row.get("object_required_count_max"))
    row["object_missing_required_count_bucket"] = bucket_count(row.get("object_missing_required_count"))
    row["object_extra_properties_count_bucket"] = bucket_count(row.get("object_extra_properties_count"))
    row["enum_size_bucket"] = bucket_count(row.get("enum_size_max"))
    row["array_prefixItems_count_bucket"] = bucket_count(row.get("array_prefixItems_count_max"))
    row["array_invalid_items_count_bucket"] = bucket_count(row.get("array_invalid_items_count"))
    row["not_sibling_keyword_count_bucket"] = bucket_count(row.get("not_sibling_keyword_count"))
    row["combinator_branch_count_bucket"] = bucket_count(row.get("combinator_branch_count_max"))
    for combinator in COMBINATORS:
        row[f"{combinator}_satisfied_branch_count_bucket"] = bucket_count(row.get(f"{combinator}_satisfied_branch_count"))
        ratio = row.get(f"{combinator}_satisfied_branch_ratio", 0)
        try:
            ratio_float = float(ratio)
        except (TypeError, ValueError):
            row[f"{combinator}_satisfied_branch_ratio_bucket"] = "unknown"
        else:
            if ratio_float == 0:
                row[f"{combinator}_satisfied_branch_ratio_bucket"] = "0"
            elif ratio_float < 1:
                row[f"{combinator}_satisfied_branch_ratio_bucket"] = "partial"
            elif ratio_float == 1:
                row[f"{combinator}_satisfied_branch_ratio_bucket"] = "all"
            else:
                row[f"{combinator}_satisfied_branch_ratio_bucket"] = ">all"


def risk_rows(test_rows: list[dict[str, Any]], contexts: list[str]) -> list[dict[str, Any]]:
    baseline_under = pct(sum(1 for row in test_rows if row["failure_type"] == "UNDER"), len(test_rows))
    baseline_over = pct(sum(1 for row in test_rows if row["failure_type"] == "OVER"), len(test_rows))
    rows: list[dict[str, Any]] = []
    for context in contexts:
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in test_rows:
            value = row.get(context, "")
            if value == "":
                value = "absent"
            groups[str(format_value(value))].append(row)
        for value, members in sorted(groups.items()):
            support_schemas = len({row["schema_id"] for row in members})
            support_tests = len(members)
            under_rate = pct(sum(1 for row in members if row["failure_type"] == "UNDER"), support_tests)
            over_rate = pct(sum(1 for row in members if row["failure_type"] == "OVER"), support_tests)
            rows.append(
                {
                    "context_feature": context,
                    "context_value": value,
                    "support_schemas": support_schemas,
                    "support_tests": support_tests,
                    "under_rate": under_rate,
                    "over_rate": over_rate,
                    "baseline_under_rate": baseline_under,
                    "baseline_over_rate": baseline_over,
                    "under_lift": under_rate / baseline_under if baseline_under else 0.0,
                    "over_lift": over_rate / baseline_over if baseline_over else 0.0,
                    "low_support": support_schemas < MIN_SUPPORT_SCHEMAS or support_tests < MIN_SUPPORT_TESTS,
                }
            )
    return sorted(rows, key=lambda row: (row["context_feature"], row["context_value"]))


def svg_text(x: float, y: float, text: Any, size: int = 12, anchor: str = "start", weight: str = "400") -> str:
    return (
        f'<text x="{x:.2f}" y="{y:.2f}" font-family="Inter, Arial, sans-serif" '
        f'font-size="{size}" fill="{PALETTE["text"]}" text-anchor="{anchor}" font-weight="{weight}">'
        f"{html.escape(str(text))}</text>"
    )


def svg_doc(width: int, height: int, title: str, body: list[str]) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}">'
        f'<rect width="100%" height="100%" fill="{PALETTE["bg"]}"/>'
        f"{svg_text(24, 30, title, 17, weight='700')}"
        + "".join(body)
        + "</svg>\n"
    )


def nice_max(value: float) -> float:
    if value <= 0 or not math.isfinite(value):
        return 1.0
    exponent = math.floor(math.log10(value))
    base = 10**exponent
    for step in (1, 2, 5, 10):
        if value <= step * base:
            return step * base
    return value


def bar_svg(path: Path, title: str, rows: list[tuple[str, float]], x_label: str = "rate", color: str = "blue") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = rows[:40]
    width, height = 980, max(260, 82 + 34 * len(rows))
    left, right, top, bottom = 300, 42, 54, 44
    plot_w = width - left - right
    max_v = nice_max(max((value for _, value in rows), default=1))
    body: list[str] = []
    for i in range(6):
        x = left + plot_w * i / 5
        val = max_v * i / 5
        body.append(f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{height-bottom}" stroke="{PALETTE["grid"]}" stroke-width="1"/>')
        body.append(svg_text(x, height - 18, f"{val:.2g}", 10, "middle"))
    for idx, (label, value) in enumerate(rows):
        y = top + idx * 34 + 8
        w = plot_w * value / max_v if max_v else 0
        body.append(svg_text(left - 10, y + 15, str(label)[:42], 11, "end"))
        body.append(f'<rect x="{left}" y="{y}" width="{max(w, 1):.2f}" height="20" rx="3" fill="{PALETTE[color]}"/>')
        body.append(svg_text(left + w + 7, y + 15, f"{value:.3g}", 11))
    body.append(svg_text(left + plot_w / 2, height - 4, x_label, 11, "middle"))
    path.write_text(svg_doc(width, height, title, body), encoding="utf-8")


def rate_by_feature(test_rows: list[dict[str, Any]], feature: str, failure: str) -> list[tuple[str, float]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in test_rows:
        groups[str(format_value(row.get(feature, "absent")))].append(row)
    out = []
    for value, members in groups.items():
        if not members:
            continue
        out.append((value, pct(sum(1 for row in members if row["failure_type"] == failure), len(members))))
    return sorted(out, key=lambda item: item[1], reverse=True)


def average_by_failure(test_rows: list[dict[str, Any]], feature: str) -> list[tuple[str, float]]:
    groups: dict[str, list[float]] = defaultdict(list)
    for row in test_rows:
        try:
            value = float(row.get(feature, 0) or 0)
        except (TypeError, ValueError):
            value = 0.0
        group = "UNDER" if row["failure_type"] == "UNDER" else "OVER" if row["failure_type"] == "OVER" else "CORRECT"
        groups[group].append(value)
    order = ["UNDER", "OVER", "CORRECT"]
    return [(key, mean(groups[key])) for key in order if key in groups]


def heatmap_svg(path: Path, title: str, matrix_rows: list[tuple[str, str, float]]) -> None:
    labels = sorted({a for a, _, _ in matrix_rows} | {b for _, b, _ in matrix_rows})
    values = {(a, b): value for a, b, value in matrix_rows}
    width = max(560, 180 + 46 * len(labels))
    height = max(520, 150 + 46 * len(labels))
    left, top, cell = 150, 70, 42
    max_v = max((value for _, _, value in matrix_rows), default=1)
    body: list[str] = []
    for i, label in enumerate(labels):
        body.append(svg_text(left + i * cell + cell / 2, top - 10, label, 10, "middle"))
        body.append(svg_text(left - 10, top + i * cell + 25, label, 10, "end"))
    for y, label_y in enumerate(labels):
        for x, label_x in enumerate(labels):
            value = values.get((label_y, label_x), values.get((label_x, label_y), 0.0))
            opacity = 0.08 + 0.82 * (value / max_v if max_v else 0)
            body.append(f'<rect x="{left + x * cell}" y="{top + y * cell}" width="{cell-2}" height="{cell-2}" fill="{PALETTE["blue"]}" opacity="{opacity:.3f}"/>')
            if value:
                body.append(svg_text(left + x * cell + cell / 2, top + y * cell + 25, f"{value:.0f}", 9, "middle"))
    path.write_text(svg_doc(width, height, title, body), encoding="utf-8")


def write_plots(plot_dir: Path, test_rows: list[dict[str, Any]], risk_tables: dict[str, list[dict[str, Any]]]) -> None:
    numeric = plot_dir / "numeric"
    pattern = plot_dir / "patternProperties"
    not_dir = plot_dir / "not"
    comb = plot_dir / "combinators"
    summary = plot_dir / "summary"

    bar_svg(numeric / "under_rate_by_numeric_target_type.svg", "UNDER rate by numeric_target_type", rate_by_feature(test_rows, "numeric_target_type", "UNDER"), "UNDER rate", "red")
    bar_svg(numeric / "under_rate_by_numeric_parent_keyword.svg", "UNDER rate by numeric_parent_keyword", rate_by_feature(test_rows, "numeric_parent_keyword", "UNDER"), "UNDER rate", "red")
    for feature in ("numeric_is_in_properties", "numeric_property_required", "numeric_has_default", "numeric_has_min_and_max"):
        bar_svg(numeric / f"under_rate_by_{feature}.svg", f"UNDER rate by {feature}", rate_by_feature(test_rows, feature, "UNDER"), "UNDER rate", "red")
    bar_svg(numeric / "numeric_keyword_count_by_failure.svg", "Average numeric_keyword_count by failure class", average_by_failure(test_rows, "numeric_keyword_count"), "average count", "blue")
    bar_svg(numeric / "under_rate_by_numeric_boundary_case.svg", "UNDER rate by numeric_boundary_case", rate_by_feature(test_rows, "numeric_boundary_case", "UNDER"), "UNDER rate", "red")

    for feature in ("additionalProperties_value", "patternProperties_with_properties", "patternProperties_has_additionalProperties"):
        bar_svg(pattern / f"over_rate_by_{feature}.svg", f"OVER rate by {feature}", rate_by_feature(test_rows, feature, "OVER"), "OVER rate", "orange")
    for feature in ("patternProperties_regex_has_anchor", "patternProperties_regex_has_dotstar", "patternProperties_regex_has_alternation", "patternProperties_regex_has_charclass"):
        bar_svg(pattern / f"over_rate_by_{feature}.svg", f"OVER rate by {feature}", rate_by_feature(test_rows, feature, "OVER"), "OVER rate", "orange")
    bar_svg(pattern / "patternProperties_pattern_count_by_failure.svg", "Average patternProperties_pattern_count by failure class", average_by_failure(test_rows, "patternProperties_pattern_count"), "average count", "blue")
    bar_svg(pattern / "over_rate_by_instance_has_unmatched_keys.svg", "OVER rate by instance_has_unmatched_keys", rate_by_feature(test_rows, "instance_has_unmatched_keys", "OVER"), "OVER rate", "orange")
    bar_svg(pattern / "over_rate_by_instance_matching_pattern_keys_count_bucket.svg", "OVER rate by matching pattern keys bucket", rate_by_feature(test_rows, "instance_matching_pattern_keys_count_bucket", "OVER"), "OVER rate", "orange")

    for feature in ("not_parent_keyword", "not_target_type"):
        bar_svg(not_dir / f"over_rate_by_{feature}.svg", f"OVER rate by {feature}", rate_by_feature(test_rows, feature, "OVER"), "OVER rate", "orange")
    for feature in ("not_contains_enum", "not_contains_const", "not_contains_pattern", "not_contains_properties", "not_contains_required", "not_contains_anyOf", "not_contains_allOf"):
        bar_svg(not_dir / f"over_rate_by_{feature}.svg", f"OVER rate by {feature}", rate_by_feature(test_rows, feature, "OVER"), "OVER rate", "orange")
    bar_svg(not_dir / "not_count_by_failure.svg", "Average not_count by failure class", average_by_failure(test_rows, "not_count"), "average count", "blue")
    bar_svg(not_dir / "over_rate_by_instance_satisfies_not_subschema.svg", "OVER rate by instance_satisfies_not_subschema", rate_by_feature(test_rows, "instance_satisfies_not_subschema", "OVER"), "OVER rate", "orange")
    bar_svg(not_dir / "over_rate_by_not_sibling_keyword_count_bucket.svg", "OVER rate by not sibling keyword count bucket", rate_by_feature(test_rows, "not_sibling_keyword_count_bucket", "OVER"), "OVER rate", "orange")

    bar_svg(comb / "over_rate_by_combinator_type.svg", "OVER rate by combinator_type", rate_by_feature(test_rows, "combinator_type", "OVER"), "OVER rate", "orange")
    bar_svg(comb / "over_rate_by_combinator_branch_count_bucket.svg", "OVER rate by branch_count bucket", rate_by_feature(test_rows, "combinator_branch_count_bucket", "OVER"), "OVER rate", "orange")
    for feature in ("branches_have_same_type", "branches_conflicting_types", "branches_have_required", "branches_have_properties", "branches_have_not", "branches_have_enum", "branches_overlapping_properties"):
        bar_svg(comb / f"over_rate_by_{feature}.svg", f"OVER rate by {feature}", rate_by_feature(test_rows, feature, "OVER"), "OVER rate", "orange")
    bar_svg(comb / "combinator_count_by_failure.svg", "Average combinator_count by failure class", average_by_failure(test_rows, "combinator_count"), "average count", "blue")
    for combinator in COMBINATORS:
        bar_svg(comb / f"over_rate_by_{combinator}_satisfied_branch_count_bucket.svg", f"OVER rate by {combinator} satisfied branch count", rate_by_feature(test_rows, f"{combinator}_satisfied_branch_count_bucket", "OVER"), "OVER rate", "orange")
    bar_svg(comb / "over_rate_by_allOf_satisfied_branch_ratio_bucket.svg", "OVER rate by allOf satisfied branch ratio", rate_by_feature(test_rows, "allOf_satisfied_branch_ratio_bucket", "OVER"), "OVER rate", "orange")

    all_risks = [row for rows in risk_tables.values() for row in rows if not row.get("low_support")]
    top_under = sorted(all_risks, key=lambda row: row["under_lift"], reverse=True)[:20]
    top_over = sorted(all_risks, key=lambda row: row["over_lift"], reverse=True)[:20]
    bar_svg(summary / "top20_under_lift_contexts.svg", "Top 20 contexts by UNDER lift", [(f"{r['context_feature']}={r['context_value']}", r["under_lift"]) for r in top_under], "UNDER lift", "red")
    bar_svg(summary / "top20_over_lift_contexts.svg", "Top 20 contexts by OVER lift", [(f"{r['context_feature']}={r['context_value']}", r["over_lift"]) for r in top_over], "OVER lift", "orange")

    cooccurrence_counts: Counter[tuple[str, str]] = Counter()
    for row in test_rows:
        raw = str(row.get("local_cooccurrence_pairs", ""))
        for item in raw.split("|"):
            if not item or ":" not in item or "+" not in item:
                continue
            pair, count = item.rsplit(":", 1)
            left, right = pair.split("+", 1)
            try:
                cooccurrence_counts[(left, right)] += int(float(count))
            except ValueError:
                pass
    heatmap_svg(summary / "local_keyword_cooccurrence_heatmap.svg", "Local keyword co-occurrence counts", [(a, b, float(v)) for (a, b), v in cooccurrence_counts.items()])

    pair_rows = []
    for feature in LOCAL_PAIR_FEATURES:
        for value, rate in rate_by_feature(test_rows, feature, "OVER"):
            if value == "true":
                pair_rows.append((feature, "OVER_lift_proxy", rate))
    heatmap_svg(summary / "local_combination_risk_heatmap.svg", "Local combination OVER-rate heatmap", pair_rows)


def top_contexts(rows: list[dict[str, Any]], metric: str, n: int = 8, min_lift: float = 1.05) -> list[dict[str, Any]]:
    lift_key = f"{metric}_lift"
    return sorted(
        [row for row in rows if not row.get("low_support") and row.get(lift_key, 0) >= min_lift],
        key=lambda row: row[lift_key],
        reverse=True,
    )[:n]


def write_report(path: Path, dataset: str, framework: str, schema_rows: list[dict[str, Any]], test_rows: list[dict[str, Any]], risk_tables: dict[str, list[dict[str, Any]]]) -> None:
    baseline_under = pct(sum(1 for row in test_rows if row["failure_type"] == "UNDER"), len(test_rows))
    baseline_over = pct(sum(1 for row in test_rows if row["failure_type"] == "OVER"), len(test_rows))
    all_risks = [row for rows in risk_tables.values() for row in rows]

    def section(title: str, table_name: str, metric: str) -> list[str]:
        rows = top_contexts(risk_tables[table_name], metric, 5)
        lines = [f"## {title}", ""]
        if not rows:
            return lines + ["No non-low-support context exceeded the support thresholds.", ""]
        for row in rows:
            lines.append(
                f"- `{row['context_feature']}={row['context_value']}`: "
                f"{metric}_rate={row[f'{metric}_rate']:.3f}, "
                f"lift={row[f'{metric}_lift']:.2f}, "
                f"support_tests={row['support_tests']}, support_schemas={row['support_schemas']}."
            )
        lines.append("")
        return lines

    lines = [
        "# Refined Feature Analysis",
        "",
        f"- Dataset: `{dataset}`",
        f"- Framework: `{framework}`",
        f"- Schemas analyzed: {len(schema_rows)}",
        f"- Tests analyzed: {len(test_rows)}",
        f"- Baseline UNDER rate: {baseline_under:.4f}",
        f"- Baseline OVER rate: {baseline_over:.4f}",
        "",
    ]
    lines.extend(section("Numeric Results", "numeric", "under"))
    lines.extend(section("PatternProperties Results", "patternProperties", "over"))
    lines.extend(section("Not Results", "not", "over"))
    lines.extend(section("Combinator Results", "combinators", "over"))
    lines.append("## Top UNDER Contexts By Lift")
    lines.append("")
    for row in top_contexts(all_risks, "under", 20):
        lines.append(f"- `{row['context_feature']}={row['context_value']}`: lift={row['under_lift']:.2f}, rate={row['under_rate']:.3f}, tests={row['support_tests']}.")
    lines.append("")
    lines.append("## Top OVER Contexts By Lift")
    lines.append("")
    for row in top_contexts(all_risks, "over", 20):
        lines.append(f"- `{row['context_feature']}={row['context_value']}`: lift={row['over_lift']:.2f}, rate={row['over_rate']:.3f}, tests={row['support_tests']}.")
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- These results are correlational.",
            "- A feature with high lift is not automatically the exact cause of the observed failure.",
            "- Low-support contexts should be interpreted cautiously.",
            "- HDD validation or controlled schema mutations can be used next to test causal hypotheses.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    framework = args.framework
    dataset = args.dataset
    results_root = Path(args.results_root)
    data_root = Path(args.data_root)
    run_dir = results_root / framework / dataset
    per_test_path = run_dir / "per_test_results.jsonl"
    data_dir = Path(args.output_data_dir) if args.output_data_dir else ROOT / "data" / dataset / "refined_feature_analysis"
    plot_dir = Path(args.output_plot_dir) if args.output_plot_dir else ROOT / "plots" / dataset / "refined_feature_analysis"
    risk_dir = data_dir / "risk_tables"
    data_dir.mkdir(parents=True, exist_ok=True)
    plot_dir.mkdir(parents=True, exist_ok=True)
    risk_dir.mkdir(parents=True, exist_ok=True)

    framework_aliases = {
        "guidance": {"guidance", "llg", "LLGuidance"},
        "llg": {"guidance", "llg", "LLGuidance"},
        "xgr": {"xgr", "XGrammar", "xgrammar"},
        "outlines": {"outlines", "Outlines"},
    }
    aliases = framework_aliases.get(framework, {framework})
    all_per_test_results = read_jsonl(per_test_path)
    per_test_results = [
        row
        for row in all_per_test_results
        if str(row.get("framework_id", row.get("framework", framework))) in aliases
        or str(row.get("framework", "")) in aliases
    ]
    if not per_test_results:
        per_test_results = all_per_test_results
    by_schema: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in per_test_results:
        by_schema[str(row["schema_id"])].append(row)

    schema_cache: dict[str, dict[str, Any]] = {}
    feature_cache: dict[str, dict[str, Any]] = {}
    schema_rows: list[dict[str, Any]] = []
    test_rows: list[dict[str, Any]] = []

    for schema_id, result_rows in sorted(by_schema.items()):
        dataset_doc = load_dataset_file(data_root, schema_id)
        schema = dataset_doc.get("schema", dataset_doc)
        tests = dataset_doc.get("tests", [])
        schema_cache[schema_id] = dataset_doc
        schema_features = analyze_schema(schema)
        feature_cache[schema_id] = schema_features

        schema_test_rows: list[dict[str, Any]] = []
        for result in sorted(result_rows, key=lambda row: int(row.get("test_index", 0))):
            test_index = int(result.get("test_index", 0))
            test_doc = tests[test_index] if 0 <= test_index < len(tests) else {}
            instance = test_doc.get("data")
            expected_valid = expected_is_valid(result.get("expected_validity"))
            accepted = bool(result.get("accepted"))
            ft = failure_type(expected_valid, accepted)
            test_features = analyze_instance(schema, instance, schema_features)
            row = {
                "schema_id": schema_id,
                "test_id": result.get("test_id", f"{schema_id}::test_{test_index:05d}"),
                "test_index": test_index,
                "expected_validity": "valid" if expected_valid else "invalid",
                "outlines_result": "accepted" if accepted else "rejected",
                "failure_type": ft,
            }
            row.update(schema_features)
            row.update(test_features)
            add_buckets(row)
            test_rows.append(row)
            schema_test_rows.append(row)

        status_counts = count_status(schema_test_rows)
        schema_row = {
            "schema_id": schema_id,
            "has_under": status_counts["under_test_count"] > 0,
            "has_over": status_counts["over_test_count"] > 0,
            **status_counts,
        }
        schema_row.update(schema_features)
        add_buckets(schema_row)
        schema_rows.append(schema_row)

    schema_field_prefix = ["schema_id", "has_under", "has_over", "under_test_count", "over_test_count", "correct_test_count", "total_test_count"]
    test_field_prefix = ["schema_id", "test_id", "test_index", "expected_validity", "outlines_result", "failure_type"]
    write_csv(data_dir / "refined_schema_features.csv", schema_rows, schema_field_prefix + [key for key in schema_rows[0] if key not in schema_field_prefix])
    write_csv(data_dir / "refined_test_features.csv", test_rows, test_field_prefix + [key for key in test_rows[0] if key not in test_field_prefix])

    contexts = {
        "numeric": [
            "numeric_target_type",
            "numeric_parent_keyword",
            "numeric_is_in_properties",
            "numeric_property_required",
            "numeric_has_default",
            "numeric_has_min_and_max",
            "numeric_boundary_case",
        ],
        "patternProperties": [
            "additionalProperties_value",
            "patternProperties_with_properties",
            "patternProperties_regex_has_anchor",
            "patternProperties_regex_has_dotstar",
            "patternProperties_regex_has_alternation",
            "patternProperties_regex_has_charclass",
            "instance_has_unmatched_keys",
            "instance_matching_pattern_keys_count_bucket",
        ],
        "not": [
            "not_parent_keyword",
            "not_target_type",
            "not_contains_enum",
            "not_contains_const",
            "not_contains_pattern",
            "not_contains_properties",
            "not_contains_required",
            "not_contains_anyOf",
            "not_contains_allOf",
            "not_sibling_keyword_count_bucket",
            "instance_satisfies_not_subschema",
        ],
        "combinators": [
            "combinator_type",
            "combinator_branch_count_bucket",
            "branches_have_same_type",
            "branches_conflicting_types",
            "branches_have_required",
            "branches_have_properties",
            "branches_have_not",
            "branches_have_enum",
            "branches_overlapping_properties",
            "allOf_satisfied_branch_count_bucket",
            "anyOf_satisfied_branch_count_bucket",
            "oneOf_satisfied_branch_count_bucket",
        ],
    }
    risk_tables = {family: risk_rows(test_rows, family_contexts) for family, family_contexts in contexts.items()}
    output_names = {
        "numeric": "numeric_context_risk.csv",
        "patternProperties": "patternProperties_context_risk.csv",
        "not": "not_context_risk.csv",
        "combinators": "combinator_context_risk.csv",
    }
    risk_fields = [
        "context_feature",
        "context_value",
        "support_schemas",
        "support_tests",
        "under_rate",
        "over_rate",
        "baseline_under_rate",
        "baseline_over_rate",
        "under_lift",
        "over_lift",
        "low_support",
    ]
    for family, rows in risk_tables.items():
        write_csv(risk_dir / output_names[family], rows, risk_fields)

    write_plots(plot_dir, test_rows, risk_tables)
    write_report(data_dir / "refined_feature_analysis_report.md", dataset, framework, schema_rows, test_rows, risk_tables)

    print(f"Wrote {len(schema_rows)} schema rows and {len(test_rows)} test rows")
    print(f"Data: {data_dir}")
    print(f"Plots: {plot_dir}")


if __name__ == "__main__":
    main()
