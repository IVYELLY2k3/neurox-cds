"""
Module 5: Drug-Drug Interaction Detector
Checks new prescription against current patient medications.
"""
import json
import os
from models.alert import SafetyAlert, AlertSeverity, AlertType

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
_interactions_cache = None


def _load_interactions() -> list[dict]:
    global _interactions_cache
    if _interactions_cache is None:
        with open(os.path.join(DATA_DIR, "interactions.json"), "r", encoding="utf-8") as f:
            _interactions_cache = json.load(f)
    return _interactions_cache


def check_interactions(drug_name: str, current_medications: list[dict]) -> list[SafetyAlert]:
    """
    Check a new drug against all current patient medications for interactions.
    """
    alerts = []
    interactions = _load_interactions()
    drug_lower = drug_name.lower().strip()

    current_drug_names = set()
    for med in current_medications:
        current_drug_names.add(med.get("drug", "").lower())
        current_drug_names.add(med.get("genericName", "").lower())

    for interaction in interactions:
        d1 = interaction["drug1"].lower()
        d2 = interaction["drug2"].lower()

        # Check if the new drug + a current medication form an interacting pair
        interacting_current = None
        if drug_lower == d1 or _drug_matches_class(drug_name, interaction["drug1"]):
            if any(_drug_name_matches(cn, interaction["drug2"]) for cn in current_drug_names):
                interacting_current = interaction["drug2"]
        elif drug_lower == d2 or _drug_matches_class(drug_name, interaction["drug2"]):
            if any(_drug_name_matches(cn, interaction["drug1"]) for cn in current_drug_names):
                interacting_current = interaction["drug1"]

        if interacting_current:
            severity_map = {
                "critical": AlertSeverity.CRITICAL,
                "high": AlertSeverity.HIGH,
                "moderate": AlertSeverity.MODERATE,
            }
            alert_severity = severity_map.get(
                interaction["severity"], AlertSeverity.MODERATE
            )

            alerts.append(SafetyAlert(
                id=f"DDI-{drug_name}-{interacting_current}",
                severity=alert_severity,
                type=AlertType.INTERACTION,
                title=f"Drug Interaction: {drug_name} ↔ {interacting_current}",
                message=f"{interaction['mechanism']}. Effect: {interaction['effect']}",
                details=f"Severity: {interaction['severity'].upper()}",
                recommendation=interaction.get("recommendation", "Consult pharmacist."),
                drugName=drug_name,
            ))

    return alerts


def _drug_name_matches(name: str, target: str) -> bool:
    """Check if a drug name matches a target (case-insensitive, handles generic/brand)."""
    name = name.lower().strip()
    target = target.lower().strip()
    if name == target:
        return True
    # Check if name contains target or vice versa (for class-level matching like "ACE Inhibitors")
    if target in name or name in target:
        return True
    return False


def _drug_matches_class(drug_name: str, interaction_drug: str) -> bool:
    """Check if a drug matches a class-level interaction entry."""
    from services.drug_service import get_drug_class
    drug_class = get_drug_class(drug_name)
    if drug_class and interaction_drug.lower() == drug_class.lower():
        return True
    # Also handle specific class references
    interaction_lower = interaction_drug.lower()
    if interaction_lower in ("ace inhibitors", "nsaids", "beta-blockers", "statins"):
        if drug_class and drug_class.lower() == interaction_lower:
            return True
    return False
