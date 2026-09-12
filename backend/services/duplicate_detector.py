"""
Module 7: Duplicate Medication Detector
Detects same or therapeutically overlapping medicines from different sources.
"""
from models.alert import SafetyAlert, AlertSeverity, AlertType

# Therapeutic class overlap groups — medications in the same group are therapeutic duplicates
THERAPEUTIC_GROUPS = {
    "NSAIDs": ["Ibuprofen", "Naproxen", "Diclofenac", "Aspirin", "Indomethacin", "Piroxicam", "Meloxicam"],
    "PPIs": ["Omeprazole", "Pantoprazole", "Esomeprazole", "Lansoprazole", "Rabeprazole"],
    "Statins": ["Atorvastatin", "Rosuvastatin", "Simvastatin", "Pravastatin", "Fluvastatin"],
    "ACE Inhibitors": ["Lisinopril", "Enalapril", "Ramipril", "Captopril", "Perindopril"],
    "ARBs": ["Losartan", "Valsartan", "Telmisartan", "Irbesartan", "Candesartan"],
    "SSRIs": ["Sertraline", "Fluoxetine", "Paroxetine", "Citalopram", "Escitalopram", "Fluvoxamine"],
    "Beta-Blockers": ["Metoprolol", "Propranolol", "Atenolol", "Bisoprolol", "Carvedilol"],
    "Thiazide Diuretics": ["Hydrochlorothiazide", "Chlorthalidone", "Indapamide"],
    "Loop Diuretics": ["Furosemide", "Bumetanide", "Torsemide"],
    "Sulfonylureas": ["Glimepiride", "Glipizide", "Glyburide"],
    "Benzodiazepines": ["Diazepam", "Lorazepam", "Clonazepam", "Alprazolam"],
    "Penicillins": ["Amoxicillin", "Ampicillin", "Penicillin V"],
    "Macrolides": ["Azithromycin", "Erythromycin", "Clarithromycin"],
    "Fluoroquinolones": ["Ciprofloxacin", "Levofloxacin", "Moxifloxacin"],
    "Cephalosporins": ["Cephalexin", "Cefixime", "Cefuroxime", "Ceftriaxone"],
    "Opioids": ["Codeine", "Tramadol", "Morphine", "Fentanyl"],
    "Antihistamines": ["Cetirizine", "Chlorpheniramine", "Hydroxyzine", "Loratadine", "Fexofenadine"],
    "Corticosteroids": ["Prednisone", "Prednisolone", "Methylprednisolone", "Dexamethasone"],
    "Anticonvulsants": ["Phenytoin", "Carbamazepine", "Valproic Acid", "Gabapentin", "Lamotrigine"],
    "Bronchodilators": ["Salbutamol", "Theophylline", "Ipratropium"],
    "Anticoagulants": ["Warfarin", "Heparin", "Enoxaparin", "Rivaroxaban", "Apixaban"],
    "Antiplatelets": ["Aspirin", "Clopidogrel", "Ticagrelor", "Prasugrel"],
}


def check_duplicates(drug_name: str, current_medications: list[dict]) -> list[SafetyAlert]:
    """
    Check for duplicate or therapeutically overlapping medications.
    """
    alerts = []
    drug_lower = drug_name.lower().strip()

    for med in current_medications:
        med_name = med.get("genericName", med.get("drug", "")).lower()
        med_drug = med.get("drug", "")

        # 1. Exact duplicate (same drug prescribed again)
        if med_name == drug_lower:
            alerts.append(SafetyAlert(
                id=f"DUP-EXACT-{drug_name}-{med['id']}",
                severity=AlertSeverity.HIGH,
                type=AlertType.DUPLICATE,
                title=f"Duplicate Medication: {drug_name}",
                message=f"Patient is already receiving {med_drug} ({med.get('dose', '')}, {med.get('frequency', '')}). "
                        f"Prescribing {drug_name} again would result in duplicate therapy.",
                details=f"Current: {med_drug} {med.get('dose', '')} {med.get('frequency', '')}, "
                        f"prescribed by {med.get('prescribedBy', 'unknown')} since {med.get('startDate', 'unknown')}.",
                recommendation=f"Verify if this is an intentional dose change or accidental duplication.",
                drugName=drug_name,
            ))
            continue

        # 2. Therapeutic class overlap
        drug_group = _find_therapeutic_group(drug_name)
        med_group = _find_therapeutic_group(med_drug)

        if drug_group and med_group and drug_group == med_group:
            alerts.append(SafetyAlert(
                id=f"DUP-CLASS-{drug_name}-{med_drug}",
                severity=AlertSeverity.MODERATE,
                type=AlertType.DUPLICATE,
                title=f"Therapeutic Duplication: {drug_name} ↔ {med_drug}",
                message=f"Both {drug_name} and {med_drug} belong to the {drug_group} class. "
                        f"Concurrent use of two {drug_group} may increase side effects without additional benefit.",
                details=f"Current: {med_drug} {med.get('dose', '')} {med.get('frequency', '')}.",
                recommendation=f"Consider whether both medications are needed. "
                               f"If switching, discontinue {med_drug} before starting {drug_name}.",
                drugName=drug_name,
            ))

    return alerts


def _find_therapeutic_group(drug_name: str) -> str | None:
    """Find which therapeutic group a drug belongs to."""
    drug_lower = drug_name.lower().strip()
    for group, members in THERAPEUTIC_GROUPS.items():
        for member in members:
            if member.lower() == drug_lower:
                return group
    return None
