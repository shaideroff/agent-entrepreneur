from __future__ import annotations
import json
from pathlib import Path
from typing import Any
VALID_LEVELS = {"A", "B", "C", "unverified"}
class KnowledgeRepository:
    def __init__(self, seed_file: Path | None = None) -> None:
        self.seed_file = seed_file or Path(__file__).parent / "seed_data" / "experts.json"
        self._profiles = json.loads(self.seed_file.read_text(encoding="utf-8")) if self.seed_file.exists() else []
    def search_profiles(self, query: str = "", domain: str | None = None, region: str | None = None, evidence_level: str | None = None) -> list[dict[str, Any]]:
        if evidence_level and evidence_level not in VALID_LEVELS: raise ValueError(f"evidence_level must be one of {sorted(VALID_LEVELS)}")
        q = query.casefold(); results = []
        for profile in self._profiles:
            haystack = " ".join([profile["name"], profile.get("summary", ""), *profile.get("domains", [])]).casefold()
            if q and q not in haystack: continue
            if domain and domain.casefold() not in [x.casefold() for x in profile.get("domains", [])]: continue
            if region and region.casefold() != str(profile.get("region", "")).casefold(): continue
            if evidence_level and profile.get("evidence_level") != evidence_level: continue
            results.append(profile)
        return results
    def get_profile(self, profile_id: str) -> dict[str, Any] | None:
        return next((p for p in self._profiles if p["id"] == profile_id), None)
    @staticmethod
    def validate_profile(profile: dict[str, Any]) -> list[str]:
        errors = []
        for field in ("id", "name", "domains", "evidence_level", "summary", "attribution", "sources"):
            if field not in profile: errors.append(f"missing required field: {field}")
        if profile.get("evidence_level") not in VALID_LEVELS: errors.append("invalid evidence_level")
        if not profile.get("sources"): errors.append("at least one traceable source is required")
        return errors
