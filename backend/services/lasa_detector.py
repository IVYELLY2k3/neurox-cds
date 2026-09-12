"""
Module 2: LASA (Look-Alike Sound-Alike) Drug Name Confusion Detector
Uses fuzzy matching against a LASA database + diagnosis-drug consistency check.
"""
import json
import os
from rapidfuzz import fuzz
from models.alert import SafetyAlert, AlertSeverity, AlertType

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
_lasa_cache = None

# Common diagnosis-drug associations for consistency checking
DIAGNOSIS_DRUG_MAP = {
    "hypertension": ["Lisinopril", "Losartan", "Amlodipine", "Metoprolol", "Hydrochlorothiazide",
                      "Enalapril", "Propranolol", "Hydralazine", "Furosemide", "Spironolactone"],
    "diabetes": ["Metformin", "Glimepiride", "Insulin Glargine"],
    "infection": ["Amoxicillin", "Azithromycin", "Ciprofloxacin", "Levofloxacin", "Cephalexin",
                  "Cefixime", "Doxycycline", "Metronidazole", "Clindamycin", "Erythromycin",
                  "Clarithromycin", "Ampicillin", "Penicillin V"],
    "respiratory": ["Amoxicillin", "Azithromycin", "Salbutamol", "Theophylline", "Montelukast"],
    "pain": ["Paracetamol", "Ibuprofen", "Diclofenac", "Naproxen", "Tramadol", "Codeine", "Gabapentin"],
    "epilepsy": ["Phenytoin", "Carbamazepine", "Valproic Acid", "Gabapentin"],
    "asthma": ["Salbutamol", "Theophylline", "Montelukast", "Prednisone", "Prednisolone"],
    "allergy": ["Cetirizine", "Chlorpheniramine", "Hydroxyzine"],
    "acid reflux": ["Omeprazole", "Pantoprazole", "Ranitidine"],
    "depression": ["Sertraline", "Fluoxetine"],
    "cholesterol": ["Atorvastatin", "Rosuvastatin", "Simvastatin"],
    "anticoagulation": ["Warfarin", "Clopidogrel", "Aspirin"],
    "nausea": ["Ondansetron", "Domperidone"],
    "thyroid": ["Levothyroxine"],
}


def _load_lasa_pairs() -> list[dict]:
    global _lasa_cache
    if _lasa_cache is None:
        with open(os.path.join(DATA_DIR, "lasa_pairs.json"), "r", encoding="utf-8") as f:
            _lasa_cache = json.load(f)
    return _lasa_cache


def check_lasa(drug_name: str, diagnoses: list[str] = None) -> list[SafetyAlert]:
    """
    Check if the prescribed drug has LASA concerns.
    Returns alerts for any LASA matches found.
    """
    alerts = []
    drug_lower = drug_name.lower().strip()
    lasa_pairs = _load_lasa_pairs()

    # 1. Check against known LASA pairs
    for pair in lasa_pairs:
        pair_drugs = [d.lower() for d in pair["pair"]]
        if drug_lower in pair_drugs:
            other_drug = pair["pair"][0] if pair["pair"][1].lower() == drug_lower else pair["pair"][1]
            similarity = fuzz.ratio(drug_lower, other_drug.lower())

            if similarity > 50:
                severity = AlertSeverity.HIGH if similarity > 75 else AlertSeverity.MODERATE
                alerts.append(SafetyAlert(
                    id=f"LASA-{drug_name}-{other_drug}",
                    severity=severity,
                    type=AlertType.LASA,
                    title=f"LASA Alert: {drug_name} ↔ {other_drug}",
                    message=f"{drug_name} is a known Look-Alike/Sound-Alike pair with {other_drug} ({pair['category']}). Similarity score: {similarity}%.",
                    details=f"Risk: {pair['risk']}",
                    recommendation=f"Please verify you intended to prescribe {drug_name} and not {other_drug}.",
                    drugName=drug_name,
                ))

    # 2. Fuzzy match against all drug names for unrecognized near-matches
    from services.drug_service import _load_drugs
    all_drugs = _load_drugs()
    for drug in all_drugs:
        other_name = drug["genericName"]
        if other_name.lower() == drug_lower:
            continue
        similarity = fuzz.ratio(drug_lower, other_name.lower())
        if similarity >= 80:
            # Check if already covered by LASA pairs
            already_covered = any(
                other_name.lower() in [d.lower() for d in p["pair"]]
                for p in lasa_pairs
                if drug_lower in [d.lower() for d in p["pair"]]
            )
            if not already_covered:
                alerts.append(SafetyAlert(
                    id=f"LASA-FUZZY-{drug_name}-{other_name}",
                    severity=AlertSeverity.MODERATE,
                    type=AlertType.LASA,
                    title=f"Name Similarity: {drug_name} ↔ {other_name}",
                    message=f"{drug_name} has high name similarity ({similarity}%) with {other_name} ({drug['drugClass']}).",
                    recommendation=f"Verify intended medication is {drug_name}, not {other_name}.",
                    drugName=drug_name,
                ))

    # 3. Diagnosis-drug consistency check
    if diagnoses:
        for diagnosis in diagnoses:
            consistency_alert = _check_diagnosis_consistency(drug_name, diagnosis)
            if consistency_alert:
                alerts.append(consistency_alert)
                break # Only add one consistency alert per drug

    return alerts


def _check_diagnosis_consistency(drug_name: str, diagnosis: str) -> SafetyAlert | None:
    """
    Check if the prescribed drug is consistent with the diagnosis.
    Returns an alert if the drug seems inconsistent.
    """
    diagnosis_lower = diagnosis.lower()
    drug_lower = drug_name.lower()

    # Find matching diagnosis category
    matched_category = None
    for category, drugs in DIAGNOSIS_DRUG_MAP.items():
        if category in diagnosis_lower:
            matched_category = category
            # Check if the drug is in the expected list
            if any(d.lower() == drug_lower for d in drugs):
                return None  # Drug matches the diagnosis

    if matched_category:
        # Drug doesn't match any expected drug for the diagnosis
        expected_drugs = DIAGNOSIS_DRUG_MAP[matched_category]
        return SafetyAlert(
            id=f"LASA-CONSISTENCY-{drug_name}-{matched_category}",
            severity=AlertSeverity.INFORMATIONAL,
            type=AlertType.LASA,
            title=f"Diagnosis-Drug Consistency Check",
            message=f"{drug_name} is not commonly associated with the diagnosis '{diagnosis}'. Please verify this is the intended medication.",
            details=f"Common medications for {matched_category}: {', '.join(expected_drugs[:5])}",
            recommendation=f"If this is intentional, no action needed. Otherwise, consider a medication typically used for {matched_category}.",
            drugName=drug_name,
        )

    return None
