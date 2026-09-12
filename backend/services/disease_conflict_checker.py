"""
Module 6: Disease-Medication Conflict Detector
Cross-references diagnoses with medication to flag contraindications.
"""
import json
import os
from models.alert import SafetyAlert, AlertSeverity, AlertType

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
_conflicts_cache = None


def _load_conflicts() -> list[dict]:
    global _conflicts_cache
    if _conflicts_cache is None:
        with open(os.path.join(DATA_DIR, "disease_conflicts.json"), "r", encoding="utf-8") as f:
            _conflicts_cache = json.load(f)
    return _conflicts_cache


def check_disease_conflicts(drug_name: str, patient_diagnoses: list[dict]) -> list[SafetyAlert]:
    """
    Check if a drug conflicts with any of the patient's diagnoses.
    """
    alerts = []
    conflicts = _load_conflicts()
    drug_lower = drug_name.lower().strip()

    # Get drug class for class-level matching
    from services.drug_service import get_drug_class
    drug_class = get_drug_class(drug_name)

    # Get all diagnosis descriptions and codes
    diagnosis_texts = set()
    for dx in patient_diagnoses:
        desc = dx.get("description", "").lower()
        diagnosis_texts.add(desc)
        # Also add individual words for fuzzy matching
        for word in desc.split():
            if len(word) > 3:
                diagnosis_texts.add(word)

    for conflict in conflicts:
        # Check if the drug matches (by name or class)
        conflict_drug = conflict["drug"].lower()
        conflict_class = conflict.get("drugClass", "").lower()

        drug_matches = (
            drug_lower == conflict_drug
            or (drug_class and drug_class.lower() == conflict_class)
        )

        if not drug_matches:
            continue

        # Check if any patient diagnosis matches
        disease_name = conflict["disease"].lower()
        disease_aliases = [a.lower() for a in conflict.get("diseaseAliases", [])]
        all_disease_names = [disease_name] + disease_aliases

        matched_diagnosis = None
        for dx in patient_diagnoses:
            dx_desc = dx.get("description", "").lower()
            for disease_term in all_disease_names:
                if disease_term in dx_desc or dx_desc in disease_term:
                    matched_diagnosis = dx.get("description", disease_name)
                    break
            if matched_diagnosis:
                break

        if matched_diagnosis:
            severity_map = {
                "critical": AlertSeverity.CRITICAL,
                "high": AlertSeverity.HIGH,
                "moderate": AlertSeverity.MODERATE,
            }
            alert_severity = severity_map.get(
                conflict["severity"], AlertSeverity.MODERATE
            )

            alerts.append(SafetyAlert(
                id=f"DC-{drug_name}-{conflict['disease'].replace(' ', '_')}",
                severity=alert_severity,
                type=AlertType.DISEASE_CONFLICT,
                title=f"Disease Conflict: {drug_name} ↔ {matched_diagnosis}",
                message=conflict["reason"],
                details=f"Patient diagnosis: {matched_diagnosis}",
                recommendation=conflict.get("recommendation", "Consult specialist."),
                drugName=drug_name,
            ))

    return alerts
