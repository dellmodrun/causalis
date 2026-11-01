#!/usr/bin/env python3
"""Run the CAUSALIS v0.1 mandate audit without network access."""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


BOUNDARY = (
    "This report validates declarations in the supplied mandate only. It does not "
    "verify deployed code, program ownership, runtime behavior, financial safety "
    "or future outcomes."
)


def read_path(document: Any, path: str) -> Any:
    value = document
    for key in path.split("."):
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value


def finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


RuleTest = Callable[[Any, dict[str, Any]], bool]


RULES: list[dict[str, Any]] = [
    {"id": "ID-001", "path": "agent.name", "label": "Agent name", "expect": "a non-empty string", "test": lambda value, _: isinstance(value, str) and bool(value.strip())},
    {"id": "ID-002", "path": "agent.version", "label": "Agent version", "expect": "a non-empty string", "test": lambda value, _: isinstance(value, str) and bool(value.strip())},
    {"id": "AUTH-001", "path": "authority.owner", "label": "Declared owner", "expect": "a non-empty string", "test": lambda value, _: isinstance(value, str) and bool(value.strip())},
    {"id": "AUTH-002", "path": "authority.allowedPrograms", "label": "Program allowlist", "expect": "a non-empty array of strings", "test": lambda value, _: isinstance(value, list) and bool(value) and all(isinstance(item, str) and item.strip() for item in value)},
    {"id": "LIMIT-001", "path": "limits.perTransaction", "label": "Per-transaction limit", "expect": "a finite non-negative number", "test": lambda value, _: finite_number(value) and value >= 0},
    {"id": "LIMIT-002", "path": "limits.perDay", "label": "Daily limit", "expect": "a number not below limits.perTransaction", "requires": ["limits.perTransaction"], "test": lambda value, document: finite_number(value) and finite_number(read_path(document, "limits.perTransaction")) and value >= read_path(document, "limits.perTransaction")},
    {"id": "LIMIT-003", "path": "limits.denomination", "label": "Limit denomination", "expect": "a non-empty string", "test": lambda value, _: isinstance(value, str) and bool(value.strip())},
    {"id": "HUMAN-001", "path": "controls.humanApprovalAbove", "label": "Approval threshold", "expect": "a finite non-negative number", "test": lambda value, _: finite_number(value) and value >= 0},
    {"id": "HUMAN-002", "path": "controls.humanApprovalAbove", "label": "Approval coverage", "expect": "a value not above limits.perTransaction", "requires": ["limits.perTransaction"], "test": lambda value, document: finite_number(value) and finite_number(read_path(document, "limits.perTransaction")) and value <= read_path(document, "limits.perTransaction")},
    {"id": "STOP-001", "path": "controls.emergencyStop", "label": "Emergency stop", "expect": "true", "test": lambda value, _: value is True},
    {"id": "LOG-001", "path": "audit.logActions", "label": "Action logging", "expect": "true", "test": lambda value, _: value is True},
    {"id": "LOG-002", "path": "audit.retentionDays", "label": "Log retention", "expect": "a positive integer", "test": lambda value, _: isinstance(value, int) and not isinstance(value, bool) and value > 0},
]


def matches_type(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return finite_number(value)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    return True


def validate_schema(value: Any, schema: dict[str, Any], path: str = "$", issues: list[dict[str, str]] | None = None) -> list[dict[str, str]]:
    output = issues if issues is not None else []
    expected = schema.get("type")
    if expected and not matches_type(value, expected):
        output.append({"path": path, "message": f"Expected {expected}."})
        return output
    if "const" in schema and value != schema["const"]:
        output.append({"path": path, "message": f"Expected the constant value {json.dumps(schema['const'])}."})
    if isinstance(value, str) and "minLength" in schema and len(value) < schema["minLength"]:
        output.append({"path": path, "message": f"Expected at least {schema['minLength']} character."})
    if finite_number(value) and "minimum" in schema and value < schema["minimum"]:
        output.append({"path": path, "message": f"Expected a value greater than or equal to {schema['minimum']}."})
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            output.append({"path": path, "message": f"Expected at least {schema['minItems']} item."})
        if "items" in schema:
            for index, item in enumerate(value):
                validate_schema(item, schema["items"], f"{path}[{index}]", output)
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                output.append({"path": f"{path}.{key}", "message": "Required property is missing."})
        for key, child in schema.get("properties", {}).items():
            if key in value:
                validate_schema(value[key], child, f"{path}.{key}", output)
    return output


def evaluate(document: Any) -> list[dict[str, str]]:
    source = document if isinstance(document, dict) else {}
    results: list[dict[str, str]] = []
    for rule in RULES:
        value = read_path(source, rule["path"])
        dependencies = [read_path(source, path) for path in rule.get("requires", [])]
        missing = value is None or any(item is None for item in dependencies)
        passed = False if missing else bool(rule["test"](value, source))
        status = "not_provided" if missing else "pass" if passed else "fail"
        reason = (
            "Required value is not provided."
            if missing
            else f"Declared value satisfies {rule['expect']}."
            if passed
            else f"Declared value must be {rule['expect']}."
        )
        results.append({"id": rule["id"], "path": rule["path"], "label": rule["label"], "status": status, "reason": reason})
    return results


def build_report(document: Any, schema: dict[str, Any]) -> dict[str, Any]:
    issues = validate_schema(document, schema)
    source = document if isinstance(document, dict) else {}
    return {
        "standard": "CAUSALIS Mandate Audit v0.1",
        "schema": {"id": schema.get("$id", "unknown"), "valid": not issues, "issues": issues},
        "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "agent": read_path(source, "agent.name"),
        "chain": read_path(source, "agent.chain"),
        "results": evaluate(source),
        "verificationBoundary": BOUNDARY,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit a CAUSALIS autonomous-capital mandate.")
    parser.add_argument("mandate", type=Path, help="Path to a mandate JSON file")
    parser.add_argument("--output", "-o", type=Path, help="Write the report to this path instead of stdout")
    args = parser.parse_args()
    try:
        document = json.loads(args.mandate.read_text(encoding="utf-8"))
        schema_path = Path(__file__).resolve().parents[1] / "assets" / "mandate.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        print(json.dumps({"error": "invalid_input", "message": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    payload = json.dumps(build_report(document, schema), indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
