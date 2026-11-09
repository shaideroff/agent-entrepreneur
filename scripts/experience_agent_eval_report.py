"""Validate model-evaluation manifests and produce an honest coverage report.

Raw model outputs stay outside the repository by default. This script validates
references and human/model-judge records; it does not generate or judge outputs.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

STATUSES = {
    "NOT_RUN",
    "GENERATED",
    "REVIEWED_PASS",
    "REVIEWED_FAIL",
    "INCONCLUSIVE",
    "BLOCKED",
}
REVIEWED = {"REVIEWED_PASS", "REVIEWED_FAIL", "INCONCLUSIVE"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _require_text(record: dict[str, Any], field: str) -> None:
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{record.get('case_id', '<unknown>')}: {field} is required")


def validate_manifest(manifest: dict[str, Any]) -> None:
    records = manifest.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("manifest.records must be a non-empty list")

    case_ids: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("each manifest record must be an object")
        _require_text(record, "case_id")
        case_id = record["case_id"]
        if case_id in case_ids:
            raise ValueError(f"duplicate case_id: {case_id}")
        case_ids.add(case_id)

        status = record.get("status")
        if status not in STATUSES:
            raise ValueError(f"{case_id}: unsupported status {status!r}")

        if status == "NOT_RUN":
            forbidden = (
                "provider",
                "model",
                "executed_at_utc",
                "prompt_sha256",
                "dossier_sha256",
                "output_artifact_ref",
                "evaluator_method",
                "evaluator_identity",
            )
            if any(record.get(field) is not None for field in forbidden):
                raise ValueError(f"{case_id}: NOT_RUN record contains execution metadata")
            if record.get("trait_results") or record.get("rubric_results"):
                raise ValueError(f"{case_id}: NOT_RUN record cannot contain scores")
            continue

        for field in (
            "provider",
            "model",
            "executed_at_utc",
            "output_artifact_ref",
        ):
            _require_text(record, field)
        for field in ("prompt_sha256", "dossier_sha256"):
            value = record.get(field)
            if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
                raise ValueError(f"{case_id}: {field} must be a lowercase SHA-256 digest")

        if status in REVIEWED:
            _require_text(record, "evaluator_method")
            _require_text(record, "evaluator_identity")
            traits = record.get("trait_results")
            rubrics = record.get("rubric_results")
            if not isinstance(traits, list) or not traits:
                raise ValueError(f"{case_id}: reviewed record requires trait_results")
            if not isinstance(rubrics, list) or not rubrics:
                raise ValueError(f"{case_id}: reviewed record requires rubric_results")
            for trait in traits:
                if not isinstance(trait, dict) or trait.get("result") not in {
                    "pass",
                    "fail",
                    "uncertain",
                }:
                    raise ValueError(f"{case_id}: every trait result needs pass/fail/uncertain")
                if trait["result"] == "pass" and not (
                    isinstance(trait.get("evidence_ref"), str)
                    and trait["evidence_ref"].strip()
                ):
                    raise ValueError(f"{case_id}: a passing trait requires evidence_ref")


def build_report(manifest: dict[str, Any]) -> str:
    validate_manifest(manifest)
    records = manifest["records"]
    status_counts = Counter(record["status"] for record in records)
    by_agent: dict[str, Counter[str]] = defaultdict(Counter)
    by_scenario: dict[str, Counter[str]] = defaultdict(Counter)
    for record in records:
        by_agent[record.get("agent_id", "unknown")][record["status"]] += 1
        by_scenario[record.get("scenario", "unknown")][record["status"]] += 1

    if status_counts["NOT_RUN"] == len(records):
        overall = "NOT RUN"
    elif status_counts["NOT_RUN"] or status_counts["GENERATED"] or status_counts["BLOCKED"]:
        overall = "INCOMPLETE"
    elif status_counts["REVIEWED_FAIL"] or status_counts["INCONCLUSIVE"]:
        overall = "REVIEW REQUIRED"
    else:
        overall = "REVIEWED PASS — subject to human release approval"

    lines = [
        "# Experience-agent model evaluation report",
        "",
        f"**Overall status:** {overall}",
        f"**Run ID:** {manifest.get('run_id') or 'not assigned'}",
        f"**Suite:** {manifest.get('suite_id', 'unspecified')}",
        f"**Cases:** {len(records)}",
        "",
        "## Status counts",
        "",
        "| Status | Cases |",
        "|---|---:|",
    ]
    for status in sorted(STATUSES):
        lines.append(f"| {status} | {status_counts[status]} |")

    lines.extend(["", "## Per-agent coverage", "", "| Agent | " + " | ".join(sorted(STATUSES)) + " |", "|---|" + "---:|" * len(STATUSES)])
    for agent_id in sorted(by_agent):
        counts = by_agent[agent_id]
        lines.append("| " + agent_id + " | " + " | ".join(str(counts[s]) for s in sorted(STATUSES)) + " |")

    lines.extend(["", "## Per-scenario coverage", "", "| Scenario | " + " | ".join(sorted(STATUSES)) + " |", "|---|" + "---:|" * len(STATUSES)])
    for scenario in sorted(by_scenario):
        counts = by_scenario[scenario]
        lines.append("| " + scenario + " | " + " | ".join(str(counts[s]) for s in sorted(STATUSES)) + " |")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- NOT RUN means no model execution evidence exists for that case.",
            "- GENERATED means an output exists but has not passed independent evaluation.",
            "- REVIEWED_PASS requires recorded trait evidence and rubric results; it is not automatic release approval.",
            "- REVIEWED_FAIL and INCONCLUSIVE prevent an overall pass.",
            "- This report validates metadata and coverage only; it does not independently verify the truth of evaluator judgments.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="JSON evaluation manifest")
    parser.add_argument("--output", type=Path, help="write Markdown report to this path")
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    report = build_report(manifest)
    if args.output:
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report)


if __name__ == "__main__":
    main()
