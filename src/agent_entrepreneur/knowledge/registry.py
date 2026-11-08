"""Validated, searchable seed knowledge for entrepreneur reference profiles."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

VALID_LEVELS = {"A", "B", "C", "unverified"}
VALID_REGIONS = {
    "North America",
    "Europe",
    "South Asia",
    "East and Southeast Asia",
    "Middle East",
    "Africa",
    "Latin America",
    "Oceania",
}
VALID_SOURCE_TYPES = {
    "primary",
    "independent_secondary",
    "official_filing",
    "dataset",
    "interview",
    "other",
    "founder_contributed",
}
VALID_CONFIDENCE = {"high", "medium", "low"}


class KnowledgeRepository:
    def __init__(self, seed_file: Path | None = None) -> None:
        self.seed_file = seed_file or Path(__file__).parent / "seed_data" / "experts.json"
        loaded: Any = (
            json.loads(self.seed_file.read_text(encoding="utf-8"))
            if self.seed_file.exists()
            else []
        )
        if not isinstance(loaded, list):
            raise ValueError("entrepreneur seed registry must be a JSON list")
        profile_ids: set[str] = set()
        for index, profile in enumerate(loaded):
            if not isinstance(profile, dict):
                raise ValueError(f"entrepreneur profile at index {index} must be an object")
            errors = self.validate_profile(profile)
            if errors:
                raise ValueError(
                    f"invalid entrepreneur profile at index {index}: {', '.join(errors)}"
                )
            profile_id = profile["id"]
            if profile_id in profile_ids:
                raise ValueError(f"duplicate entrepreneur profile id: {profile_id}")
            profile_ids.add(profile_id)
        self._profiles: list[dict[str, Any]] = loaded

    def search_profiles(
        self,
        query: str = "",
        domain: str | None = None,
        region: str | None = None,
        evidence_level: str | None = None,
    ) -> list[dict[str, Any]]:
        if evidence_level and evidence_level not in VALID_LEVELS:
            raise ValueError(f"evidence_level must be one of {sorted(VALID_LEVELS)}")
        normalized_query = query.casefold()
        results: list[dict[str, Any]] = []
        for profile in self._profiles:
            haystack = " ".join(
                [profile["name"], profile.get("summary", ""), *profile.get("domains", [])]
            ).casefold()
            if normalized_query and normalized_query not in haystack:
                continue
            if domain and domain.casefold() not in [
                item.casefold() for item in profile.get("domains", [])
            ]:
                continue
            if region and region.casefold() != str(profile.get("region", "")).casefold():
                continue
            if evidence_level and profile.get("evidence_level") != evidence_level:
                continue
            results.append(profile)
        return results

    def get_profile(self, profile_id: str) -> dict[str, Any] | None:
        return next((profile for profile in self._profiles if profile["id"] == profile_id), None)

    @staticmethod
    def validate_profile(profile: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        required = (
            "id",
            "name",
            "region",
            "domains",
            "evidence_level",
            "summary",
            "attribution",
            "ventures",
            "expertise",
            "methods",
            "decisions",
            "outcomes",
            "confidence",
            "updated_at",
            "sources",
        )
        for field in required:
            if field not in profile:
                errors.append(f"missing required field: {field}")

        for field in ("id", "name", "summary", "attribution"):
            value = profile.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{field} must be a non-empty string")
        evidence_level = profile.get("evidence_level")
        if not isinstance(evidence_level, str) or evidence_level not in VALID_LEVELS:
            errors.append("invalid evidence_level")
        region = profile.get("region")
        if not isinstance(region, str) or region not in VALID_REGIONS:
            errors.append("invalid region")
        confidence = profile.get("confidence")
        if not isinstance(confidence, str) or confidence not in VALID_CONFIDENCE:
            errors.append("invalid confidence")

        updated_at = profile.get("updated_at")
        if isinstance(updated_at, str):
            try:
                date.fromisoformat(updated_at)
            except ValueError:
                errors.append("updated_at must be an ISO 8601 date")
        else:
            errors.append("updated_at must be an ISO 8601 date")

        for field in ("domains", "ventures", "expertise", "methods", "decisions", "outcomes"):
            value = profile.get(field)
            if not isinstance(value, list):
                errors.append(f"{field} must be a list")
            elif any(not isinstance(item, str) or not item.strip() for item in value):
                errors.append(f"{field} must contain non-empty strings")

        sources = profile.get("sources")
        if not isinstance(sources, list) or not sources:
            errors.append("at least one traceable source is required")
            return errors

        seen_source_ids: set[str] = set()
        for index, source in enumerate(sources):
            prefix = f"source {index + 1}"
            if not isinstance(source, dict):
                errors.append(f"{prefix} must be an object")
                continue
            for field in (
                "source_id",
                "title",
                "publisher",
                "source_type",
                "accessed_at",
                "supports",
            ):
                value = source.get(field)
                if not isinstance(value, str) or not value.strip():
                    errors.append(f"{prefix} missing valid {field}")
            source_id = source.get("source_id")
            if isinstance(source_id, str):
                if source_id in seen_source_ids:
                    errors.append(f"duplicate source_id: {source_id}")
                seen_source_ids.add(source_id)
            source_type = source.get("source_type")
            if not isinstance(source_type, str) or source_type not in VALID_SOURCE_TYPES:
                errors.append(f"{prefix} has invalid source_type")
            url = source.get("url")
            if source_type == "founder_contributed":
                if url not in (None, "") and not (
                    isinstance(url, str) and url.startswith("https://")
                ):
                    errors.append(f"{prefix} has invalid URL")
            elif not isinstance(url, str) or not url.startswith("https://"):
                errors.append(f"{prefix} requires an HTTPS URL")
            accessed_at = source.get("accessed_at")
            if isinstance(accessed_at, str):
                try:
                    date.fromisoformat(accessed_at)
                except ValueError:
                    errors.append(f"{prefix} accessed_at must be an ISO 8601 date")
            else:
                errors.append(f"{prefix} accessed_at must be an ISO 8601 date")
            limitations = source.get("limitations", [])
            if not isinstance(limitations, list) or any(
                not isinstance(item, str) or not item.strip() for item in limitations
            ):
                errors.append(f"{prefix} limitations must be a list of non-empty strings")
        return errors
