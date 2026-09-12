"""
Module 8: AI Alert Prioritization Engine
Aggregates all safety alerts, applies contextual scoring, deduplicates, and prioritizes.
"""
from datetime import datetime, timezone
from models.alert import SafetyAlert, AlertSeverity, AlertType, AnalysisResult, ZKProofInfo
from services.lasa_detector import check_lasa
from services.dosage_validator import validate_dosage
from services.allergy_checker import check_allergies
from services.interaction_checker import check_interactions
from services.disease_conflict_checker import check_disease_conflicts
from services.duplicate_detector import check_duplicates
from services.diagnosis_medicine_matcher import check_diagnosis_medicine_match
from services.zk_service import generate_proof_for_alert


def analyze_prescription(
    patient: dict,
    drug_name: str,
    dose: str,
    diagnoses: list[str] = None,
) -> AnalysisResult:
    """
    Run all safety modules and return a prioritized, deduplicated set of alerts.
    """
    all_alerts: list[SafetyAlert] = []

    # Module 2: LASA Check
    lasa_alerts = check_lasa(drug_name, diagnoses)
    all_alerts.extend(lasa_alerts)

    # Module 3: Dosage Validation
    dosage_alerts = validate_dosage(
        drug_name,
        dose,
        patient["age"],
        patient["weight"],
    )
    all_alerts.extend(dosage_alerts)

    # Module 4: Allergy Check
    allergy_alerts = check_allergies(drug_name, patient.get("allergies", []))
    all_alerts.extend(allergy_alerts)

    # Module 5: Drug-Drug Interactions
    interaction_alerts = check_interactions(
        drug_name, patient.get("currentMedications", [])
    )
    all_alerts.extend(interaction_alerts)

    # Module 6: Disease-Medication Conflicts
    dynamic_dx = [{"description": d} for d in (diagnoses or [])]
    combined_diagnoses = patient.get("diagnoses", []) + dynamic_dx
    conflict_alerts = check_disease_conflicts(
        drug_name, combined_diagnoses
    )
    all_alerts.extend(conflict_alerts)

    # Module 7: Duplicate Medications
    duplicate_alerts = check_duplicates(
        drug_name, patient.get("currentMedications", [])
    )
    all_alerts.extend(duplicate_alerts)

    # Module 9: Diagnosis-Medicine Matching
    diagnosis_match_alerts = check_diagnosis_medicine_match(
        drug_name, diagnoses or []
    )
    all_alerts.extend(diagnosis_match_alerts)

    # Deduplicate alerts by ID
    seen_ids = set()
    unique_alerts = []
    for alert in all_alerts:
        if alert.id not in seen_ids:
            seen_ids.add(alert.id)
            unique_alerts.append(alert)

    # Attach ZK proofs to all alerts
    for alert in unique_alerts:
        zk_proof = generate_proof_for_alert(alert, patient)
        alert.zkProof = zk_proof

    # Sort by severity (Critical first, then High, Moderate, Informational)
    severity_order = {
        AlertSeverity.CRITICAL: 0,
        AlertSeverity.HIGH: 1,
        AlertSeverity.MODERATE: 2,
        AlertSeverity.INFORMATIONAL: 3,
    }
    unique_alerts.sort(key=lambda a: severity_order.get(a.severity, 99))

    # Count by severity
    critical_count = sum(1 for a in unique_alerts if a.severity == AlertSeverity.CRITICAL)
    high_count = sum(1 for a in unique_alerts if a.severity == AlertSeverity.HIGH)
    moderate_count = sum(1 for a in unique_alerts if a.severity == AlertSeverity.MODERATE)
    info_count = sum(1 for a in unique_alerts if a.severity == AlertSeverity.INFORMATIONAL)

    return AnalysisResult(
        patientId=patient["id"],
        alerts=unique_alerts,
        totalAlerts=len(unique_alerts),
        criticalCount=critical_count,
        highCount=high_count,
        moderateCount=moderate_count,
        informationalCount=info_count,
        analysisTimestamp=datetime.now(timezone.utc).isoformat(),
        zkVerified=all(a.zkProof and a.zkProof.verified for a in unique_alerts),
    )


def analyze_full_prescription(patient: dict, items: list[dict], diagnoses: list[str] = None) -> AnalysisResult:
    """
    Analyze all items in a prescription against the patient record.
    """
    all_alerts: list[SafetyAlert] = []

    for item in items:
        drug_name = item.get("drugName", item.get("genericName", ""))
        dose = item.get("dose", "")

        if not drug_name:
            continue

        result = analyze_prescription(patient, drug_name, dose, diagnoses)
        all_alerts.extend(result.alerts)

    # Deduplicate across all items
    seen_ids = set()
    unique_alerts = []
    for alert in all_alerts:
        if alert.id not in seen_ids:
            seen_ids.add(alert.id)
            unique_alerts.append(alert)

    # Re-sort
    severity_order = {
        AlertSeverity.CRITICAL: 0,
        AlertSeverity.HIGH: 1,
        AlertSeverity.MODERATE: 2,
        AlertSeverity.INFORMATIONAL: 3,
    }
    unique_alerts.sort(key=lambda a: severity_order.get(a.severity, 99))

    critical_count = sum(1 for a in unique_alerts if a.severity == AlertSeverity.CRITICAL)
    high_count = sum(1 for a in unique_alerts if a.severity == AlertSeverity.HIGH)
    moderate_count = sum(1 for a in unique_alerts if a.severity == AlertSeverity.MODERATE)
    info_count = sum(1 for a in unique_alerts if a.severity == AlertSeverity.INFORMATIONAL)

    return AnalysisResult(
        patientId=patient["id"],
        alerts=unique_alerts,
        totalAlerts=len(unique_alerts),
        criticalCount=critical_count,
        highCount=high_count,
        moderateCount=moderate_count,
        informationalCount=info_count,
        analysisTimestamp=datetime.now(timezone.utc).isoformat(),
        zkVerified=all(a.zkProof and a.zkProof.verified for a in unique_alerts if a.zkProof),
    )
