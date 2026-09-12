"""
Drug Service: Drug lookup and autocomplete supporting brand + generic names.
"""
import json
import os
from typing import Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
_drugs_cache = None


def _load_drugs() -> list[dict]:
    global _drugs_cache
    if _drugs_cache is None:
        with open(os.path.join(DATA_DIR, "drugs.json"), "r", encoding="utf-8") as f:
            _drugs_cache = json.load(f)
    return _drugs_cache


def search_drugs(query: str, limit: int = 15) -> list[dict]:
    """
    Search drugs by generic name or brand name.
    Returns matching drugs with summary info for autocomplete.
    """
    query = query.lower().strip()
    if not query:
        return []

    drugs = _load_drugs()
    results = []

    for drug in drugs:
        match_score = 0
        matched_name = drug["genericName"]

        # Check generic name
        generic_lower = drug["genericName"].lower()
        if generic_lower.startswith(query):
            match_score = 100
            matched_name = drug["genericName"]
        elif query in generic_lower:
            match_score = 70
            matched_name = drug["genericName"]

        # Check brand names
        for brand in drug.get("brandNames", []):
            brand_lower = brand.lower()
            if brand_lower.startswith(query):
                if match_score < 90:
                    match_score = 90
                    matched_name = brand
            elif query in brand_lower:
                if match_score < 60:
                    match_score = 60
                    matched_name = brand

        if match_score > 0:
            results.append({
                "id": drug["id"],
                "genericName": drug["genericName"],
                "brandNames": drug.get("brandNames", []),
                "drugClass": drug["drugClass"],
                "therapeuticCategory": drug.get("therapeuticCategory", ""),
                "forms": drug.get("forms", []),
                "matchedName": matched_name,
                "matchScore": match_score,
            })

    # Sort by match score (best first), then alphabetically
    results.sort(key=lambda x: (-x["matchScore"], x["genericName"]))
    return results[:limit]


def get_drug_by_id(drug_id: str) -> Optional[dict]:
    """Get full drug info by ID."""
    drugs = _load_drugs()
    for d in drugs:
        if d["id"] == drug_id:
            return d
    return None


def get_drug_by_name(name: str) -> Optional[dict]:
    """Get drug by generic name or brand name (case-insensitive)."""
    name_lower = name.lower().strip()
    drugs = _load_drugs()
    for d in drugs:
        if d["genericName"].lower() == name_lower:
            return d
        for brand in d.get("brandNames", []):
            if brand.lower() == name_lower:
                return d
    return None


def get_drug_class(drug_name: str) -> Optional[str]:
    """Get the drug class for a given drug name."""
    drug = get_drug_by_name(drug_name)
    if drug:
        return drug.get("drugClass")
    return None


def get_dosage_range(drug_name: str, age_bracket: str, weight: float = None) -> Optional[dict]:
    """
    Get dosage range for a drug given age bracket and optional weight.
    Returns the appropriate dosage range dict.
    """
    drug = get_drug_by_name(drug_name)
    if not drug:
        return None

    ranges = drug.get("dosageRanges", {})
    bracket_range = ranges.get(age_bracket)
    if not bracket_range:
        return None

    result = dict(bracket_range)

    # Calculate weight-based dose for pediatric patients
    if age_bracket == "pediatric" and weight and "mgPerKgPerDay" in bracket_range:
        mg_per_kg = bracket_range["mgPerKgPerDay"]
        result["calculatedDailyMin"] = round(mg_per_kg["min"] * weight, 1)
        result["calculatedDailyMax"] = round(mg_per_kg["max"] * weight, 1)

        # Estimate per-dose range based on frequency
        freq = bracket_range.get("frequency", "")
        doses_per_day = _estimate_doses_per_day(freq)
        if doses_per_day > 0:
            result["calculatedPerDoseMin"] = round(result["calculatedDailyMin"] / doses_per_day, 1)
            result["calculatedPerDoseMax"] = round(result["calculatedDailyMax"] / doses_per_day, 1)

    return result


def _estimate_doses_per_day(frequency: str) -> int:
    """Estimate number of doses per day from frequency string."""
    freq_lower = frequency.lower()
    if "once" in freq_lower or "1 time" in freq_lower:
        return 1
    elif "twice" in freq_lower or "2 times" in freq_lower:
        return 2
    elif "three" in freq_lower or "3 times" in freq_lower or "every 8 hours" in freq_lower:
        return 3
    elif "four" in freq_lower or "4 times" in freq_lower or "every 6 hours" in freq_lower:
        return 4
    elif "every 4" in freq_lower:
        return 6
    elif "every 12" in freq_lower:
        return 2
    elif "4-6" in freq_lower:
        return 4
    elif "6-8" in freq_lower:
        return 3
    elif "2-3" in freq_lower:
        return 3
    elif "3-4" in freq_lower:
        return 3
    return 3  # Default assumption
