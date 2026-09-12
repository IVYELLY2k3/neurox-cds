"""
Module 4: Allergy & Adverse Reaction Safety Check
Matches prescribed medicine against documented allergies/reactions,
including drug-class cross-reactivity.
"""
from models.alert import SafetyAlert, AlertSeverity, AlertType

# Drug class cross-reactivity mapping
CROSS_REACTIVITY = {
    "Penicillins": {
        "members": ["Amoxicillin", "Ampicillin", "Penicillin V", "Piperacillin"],
        "related_classes": {"Cephalosporins": 0.1},  # ~10% cross-reactivity
    },
    "NSAIDs": {
        "members": ["Ibuprofen", "Naproxen", "Diclofenac", "Aspirin", "Indomethacin", "Piroxicam", "Meloxicam"],
        "related_classes": {},
    },
    "Sulfonamides": {
        "members": ["Sulfamethoxazole", "Sulfadiazine", "Sulfasalazine"],
        "related_classes": {},
    },
    "Macrolides": {
        "members": ["Azithromycin", "Erythromycin", "Clarithromycin"],
        "related_classes": {},
    },
    "Fluoroquinolones": {
        "members": ["Ciprofloxacin", "Levofloxacin", "Moxifloxacin"],
        "related_classes": {},
    },
    "Cephalosporins": {
        "members": ["Cephalexin", "Cefixime", "Cefuroxime", "Ceftriaxone"],
        "related_classes": {"Penicillins": 0.02},  # ~2% cross-reactivity
    },
    "Opioids": {
        "members": ["Codeine", "Tramadol", "Morphine", "Fentanyl", "Hydrocodone", "Oxycodone"],
        "related_classes": {},
    },
    "Statins": {
        "members": ["Atorvastatin", "Rosuvastatin", "Simvastatin", "Pravastatin"],
        "related_classes": {},
    },
    "ACE Inhibitors": {
        "members": ["Lisinopril", "Enalapril", "Ramipril", "Captopril"],
        "related_classes": {},
    },
    "Beta-Blockers": {
        "members": ["Metoprolol", "Propranolol", "Atenolol", "Bisoprolol"],
        "related_classes": {},
    },
    "Tetracyclines": {
        "members": ["Doxycycline", "Tetracycline", "Minocycline"],
        "related_classes": {},
    },
}


def check_allergies(drug_name: str, patient_allergies: list[dict]) -> list[SafetyAlert]:
    """
    Check a prescribed drug against the patient's documented allergies.
    Handles exact matches, drug class matches, and cross-reactivity.
    """
    alerts = []
    drug_lower = drug_name.lower().strip()

    for allergy in patient_allergies:
        substance = allergy.get("substance", "")
        allergy_class = allergy.get("drugClass", "")
        reaction = allergy.get("reaction", "")
        severity = allergy.get("severity", "moderate")
        notes = allergy.get("notes", "")

        # 1. Direct substance match
        if substance.lower() == drug_lower:
            alert_severity = AlertSeverity.CRITICAL if severity == "severe" else AlertSeverity.HIGH
            alerts.append(SafetyAlert(
                id=f"ALLERGY-DIRECT-{drug_name}-{allergy['id']}",
                severity=alert_severity,
                type=AlertType.ALLERGY,
                title=f"⚠ ALLERGY: {drug_name}",
                message=f"Patient has a DOCUMENTED {severity.upper()} reaction to {substance}: {reaction}.",
                details=notes,
                evidence=f"Documented on {allergy.get('documentedDate', 'unknown')} by {allergy.get('documentedBy', 'unknown')}.",
                recommendation=f"DO NOT prescribe {drug_name}. Choose an alternative medication from a different drug class.",
                drugName=drug_name,
            ))
            continue

        # 2. Drug class match (e.g., prescribing Amoxicillin when allergy is to Penicillin class)
        drug_class = _get_drug_class(drug_name)
        if allergy_class and drug_class:
            if allergy_class.lower() == drug_class.lower():
                alert_severity = AlertSeverity.CRITICAL if severity == "severe" else AlertSeverity.HIGH
                alerts.append(SafetyAlert(
                    id=f"ALLERGY-CLASS-{drug_name}-{allergy['id']}",
                    severity=alert_severity,
                    type=AlertType.ALLERGY,
                    title=f"⚠ DRUG CLASS ALLERGY: {drug_name} ({drug_class})",
                    message=f"Patient has a {severity.upper()} allergy to {substance} ({allergy_class} class). "
                            f"{drug_name} belongs to the SAME drug class. Previous reaction: {reaction}.",
                    details=notes,
                    evidence=f"Documented on {allergy.get('documentedDate', 'unknown')} by {allergy.get('documentedBy', 'unknown')}.",
                    recommendation=f"DO NOT prescribe {drug_name}. It belongs to the {drug_class} class, same as the allergen.",
                    drugName=drug_name,
                ))
                continue

        # 3. Check if drug is a member of the allergic substance's class
        if allergy_class:
            class_info = CROSS_REACTIVITY.get(allergy_class, {})
            members = class_info.get("members", [])
            if any(m.lower() == drug_lower for m in members):
                alert_severity = AlertSeverity.CRITICAL if severity == "severe" else AlertSeverity.HIGH
                alerts.append(SafetyAlert(
                    id=f"ALLERGY-MEMBER-{drug_name}-{allergy['id']}",
                    severity=alert_severity,
                    type=AlertType.ALLERGY,
                    title=f"⚠ DRUG CLASS ALLERGY: {drug_name} is a {allergy_class}",
                    message=f"Patient has a {severity.upper()} allergy to {substance} ({allergy_class}). "
                            f"{drug_name} is a member of the {allergy_class} class. Previous reaction: {reaction}.",
                    details=notes,
                    evidence=f"Documented on {allergy.get('documentedDate', 'unknown')} by {allergy.get('documentedBy', 'unknown')}.",
                    recommendation=f"DO NOT prescribe {drug_name}. Choose a non-{allergy_class} alternative.",
                    drugName=drug_name,
                ))
                continue

        # 4. Cross-reactivity check (e.g., Penicillin allergy + Cephalosporin prescription)
        if allergy_class and drug_class:
            allergy_class_info = CROSS_REACTIVITY.get(allergy_class, {})
            cross_classes = allergy_class_info.get("related_classes", {})
            if drug_class in cross_classes:
                cross_rate = cross_classes[drug_class]
                alerts.append(SafetyAlert(
                    id=f"ALLERGY-CROSS-{drug_name}-{allergy['id']}",
                    severity=AlertSeverity.HIGH,
                    type=AlertType.ALLERGY,
                    title=f"Cross-Reactivity Risk: {allergy_class} → {drug_class}",
                    message=f"Patient has a {severity} allergy to {substance} ({allergy_class}). "
                            f"{drug_name} ({drug_class}) has ~{int(cross_rate*100)}% cross-reactivity with {allergy_class}.",
                    details=f"Previous reaction: {reaction}. {notes}",
                    recommendation=f"Use with extreme caution or choose an alternative from a different class.",
                    drugName=drug_name,
                ))

    return alerts


def _get_drug_class(drug_name: str) -> str | None:
    """Look up drug class from cross-reactivity map or drug service."""
    drug_lower = drug_name.lower()
    for class_name, info in CROSS_REACTIVITY.items():
        for member in info.get("members", []):
            if member.lower() == drug_lower:
                return class_name

    # Fallback to drug service
    from services.drug_service import get_drug_class
    return get_drug_class(drug_name)
