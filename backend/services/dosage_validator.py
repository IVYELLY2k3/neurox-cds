"""
Module 3: Patient-Specific Dosage Validator
Checks entered dosage against patient's age/weight and safe ranges.
"""
import re
from models.alert import SafetyAlert, AlertSeverity, AlertType
from services.drug_service import get_drug_by_name, get_dosage_range, _estimate_doses_per_day
from services.patient_service import get_age_bracket


def validate_dosage(
    drug_name: str,
    entered_dose: str,
    patient_age: int,
    patient_weight: float,
) -> list[SafetyAlert]:
    """
    Validate the entered dosage against safe ranges for the patient.
    Returns alerts for any dosage concerns.
    """
    alerts = []
    dose_mg = _parse_dose_mg(entered_dose)
    if dose_mg is None:
        return alerts  # Can't validate if we can't parse the dose

    drug = get_drug_by_name(drug_name)
    if not drug:
        return alerts  # Drug not in database

    age_bracket = get_age_bracket(patient_age)
    dosage_info = get_dosage_range(drug_name, age_bracket, patient_weight)

    if not dosage_info:
        return alerts

    # 1. Check if dose is in pediatric range when patient is a child
    if age_bracket == "pediatric":
        alerts.extend(_check_pediatric_dose(
            drug_name, dose_mg, patient_weight, patient_age, dosage_info, drug
        ))

    # 2. Check adult/geriatric per-dose range
    if age_bracket in ("adult", "geriatric"):
        alerts.extend(_check_adult_dose(
            drug_name, dose_mg, age_bracket, dosage_info
        ))

    # 3. Check for decimal errors (10x or 100x the normal dose)
    alerts.extend(_check_decimal_errors(drug_name, dose_mg, age_bracket, dosage_info, patient_weight))

    # 4. Check max daily dose
    max_daily = dosage_info.get("maxDailyDose", 0)
    if max_daily > 0 and dose_mg > max_daily:
        alerts.append(SafetyAlert(
            id=f"DOSE-MAX-DAILY-{drug_name}",
            severity=AlertSeverity.CRITICAL,
            type=AlertType.DOSAGE,
            title=f"Single Dose Exceeds Maximum DAILY Dose",
            message=f"Entered dose of {dose_mg}mg for {drug_name} exceeds the maximum daily dose of {max_daily}mg for {age_bracket} patients.",
            recommendation=f"Maximum daily dose: {max_daily}mg. Please reduce the dose.",
            drugName=drug_name,
        ))

    return alerts


def _check_pediatric_dose(
    drug_name: str, dose_mg: float, weight: float, age: int,
    dosage_info: dict, drug: dict
) -> list[SafetyAlert]:
    """Check pediatric dosing — most critical safety check."""
    alerts = []

    # Get weight-based calculated ranges
    calc_per_dose_min = dosage_info.get("calculatedPerDoseMin")
    calc_per_dose_max = dosage_info.get("calculatedPerDoseMax")
    calc_daily_min = dosage_info.get("calculatedDailyMin")
    calc_daily_max = dosage_info.get("calculatedDailyMax")

    # Also check against adult dose to detect adult-dose-for-child error
    adult_range = drug.get("dosageRanges", {}).get("adult", {})
    adult_per_dose_min = adult_range.get("dosePerAdmin", {}).get("min", 0)

    if calc_per_dose_min is not None and calc_per_dose_max is not None:
        safe_range_str = f"{calc_per_dose_min}–{calc_per_dose_max}mg per dose (based on {weight}kg body weight)"

        # Check if the dose looks like an adult dose
        if adult_per_dose_min and dose_mg >= adult_per_dose_min and dose_mg > calc_per_dose_max * 1.5:
            alerts.append(SafetyAlert(
                id=f"DOSE-ADULT-PEDIATRIC-{drug_name}",
                severity=AlertSeverity.HIGH,
                type=AlertType.DOSAGE,
                title=f"Adult Dose for Pediatric Patient",
                message=f"Entered dose {dose_mg}mg appears to be an ADULT dose for a {age}-year-old, {weight}kg child. "
                        f"Safe pediatric range: {safe_range_str}.",
                details=f"Mg/kg calculation: {dosage_info.get('mgPerKgPerDay', {}).get('min', '?')}–{dosage_info.get('mgPerKgPerDay', {}).get('max', '?')} mg/kg/day.",
                recommendation=f"Recommended dose for this patient: {safe_range_str}.",
                drugName=drug_name,
            ))
        elif dose_mg > calc_per_dose_max:
            # Over the safe range but not necessarily adult dose
            over_pct = round(((dose_mg - calc_per_dose_max) / calc_per_dose_max) * 100, 1)
            severity = AlertSeverity.CRITICAL if over_pct > 100 else AlertSeverity.HIGH
            alerts.append(SafetyAlert(
                id=f"DOSE-HIGH-PEDIATRIC-{drug_name}",
                severity=severity,
                type=AlertType.DOSAGE,
                title=f"Dose Exceeds Safe Pediatric Range",
                message=f"Entered dose {dose_mg}mg is {over_pct}% above the maximum safe dose for a {weight}kg child. "
                        f"Safe range: {safe_range_str}.",
                recommendation=f"Reduce dose to within {safe_range_str}.",
                drugName=drug_name,
            ))
        elif dose_mg < calc_per_dose_min * 0.5:
            # Unusually low dose
            alerts.append(SafetyAlert(
                id=f"DOSE-LOW-PEDIATRIC-{drug_name}",
                severity=AlertSeverity.MODERATE,
                type=AlertType.DOSAGE,
                title=f"Dose Below Expected Range",
                message=f"Entered dose {dose_mg}mg is below the expected minimum for a {weight}kg child. "
                        f"Safe range: {safe_range_str}.",
                recommendation=f"Verify this dose is intentional. Therapeutic effect may be suboptimal.",
                drugName=drug_name,
            ))

    # Check for drugs not recommended for pediatric use
    notes = dosage_info.get("notes", "")
    if "contraindicated" in notes.lower() or "not recommended" in notes.lower() or "not approved" in notes.lower():
        max_dose = dosage_info.get("maxDailyDose", 0)
        if max_dose == 0:
            alerts.append(SafetyAlert(
                id=f"DOSE-PEDS-CONTRA-{drug_name}",
                severity=AlertSeverity.CRITICAL,
                type=AlertType.DOSAGE,
                title=f"{drug_name} Not Recommended for Pediatric Use",
                message=f"{drug_name}: {notes}",
                recommendation=f"Consider an age-appropriate alternative medication.",
                drugName=drug_name,
            ))

    return alerts


def _check_adult_dose(
    drug_name: str, dose_mg: float, age_bracket: str, dosage_info: dict
) -> list[SafetyAlert]:
    """Check adult/geriatric dose ranges."""
    alerts = []
    per_dose = dosage_info.get("dosePerAdmin", {})
    dose_min = per_dose.get("min", 0)
    dose_max = per_dose.get("max", 0)

    if dose_max > 0:
        if dose_mg > dose_max:
            over_pct = round(((dose_mg - dose_max) / dose_max) * 100, 1)
            severity = AlertSeverity.CRITICAL if over_pct > 100 else AlertSeverity.HIGH
            alerts.append(SafetyAlert(
                id=f"DOSE-HIGH-{age_bracket.upper()}-{drug_name}",
                severity=severity,
                type=AlertType.DOSAGE,
                title=f"Dose Exceeds Safe {age_bracket.title()} Range",
                message=f"Entered dose {dose_mg}mg exceeds maximum recommended dose of {dose_max}mg for {age_bracket} patients ({over_pct}% above limit).",
                recommendation=f"Recommended range: {dose_min}–{dose_max}mg per dose.",
                drugName=drug_name,
            ))
        elif dose_mg < dose_min * 0.5 and dose_min > 0:
            alerts.append(SafetyAlert(
                id=f"DOSE-LOW-{age_bracket.upper()}-{drug_name}",
                severity=AlertSeverity.MODERATE,
                type=AlertType.DOSAGE,
                title=f"Dose Below Expected Range",
                message=f"Entered dose {dose_mg}mg is below the usual minimum of {dose_min}mg for {age_bracket} patients.",
                recommendation=f"Verify dose is intentional. Usual range: {dose_min}–{dose_max}mg per dose.",
                drugName=drug_name,
            ))

    return alerts


def _check_decimal_errors(
    drug_name: str, dose_mg: float, age_bracket: str,
    dosage_info: dict, weight: float
) -> list[SafetyAlert]:
    """Detect potential decimal/entry errors (10x or 100x overdose)."""
    alerts = []

    # Determine the expected typical dose
    if age_bracket == "pediatric":
        typical_max = dosage_info.get("calculatedPerDoseMax", 0)
    else:
        per_dose = dosage_info.get("dosePerAdmin", {})
        typical_max = per_dose.get("max", 0)

    if typical_max <= 0:
        return alerts

    # Check for 10x error
    if abs(dose_mg - typical_max * 10) < typical_max * 2:
        alerts.append(SafetyAlert(
            id=f"DOSE-DECIMAL-10X-{drug_name}",
            severity=AlertSeverity.CRITICAL,
            type=AlertType.DOSAGE,
            title=f"Possible Decimal Error — 10x Overdose",
            message=f"Entered dose {dose_mg}mg appears to be approximately 10 times the typical maximum dose of {typical_max}mg. "
                    f"This may be a decimal point error.",
            recommendation=f"Did you mean {typical_max}mg instead of {dose_mg}mg?",
            drugName=drug_name,
        ))

    # Check for 100x error
    if abs(dose_mg - typical_max * 100) < typical_max * 20:
        alerts.append(SafetyAlert(
            id=f"DOSE-DECIMAL-100X-{drug_name}",
            severity=AlertSeverity.CRITICAL,
            type=AlertType.DOSAGE,
            title=f"Possible Decimal Error — 100x Overdose",
            message=f"Entered dose {dose_mg}mg appears to be approximately 100 times the typical dose. "
                    f"This is very likely a decimal point error.",
            recommendation=f"Did you mean {round(typical_max, 1)}mg instead of {dose_mg}mg?",
            drugName=drug_name,
        ))

    return alerts


def get_safe_range_for_display(drug_name: str, patient_age: int, patient_weight: float) -> dict | None:
    """
    Get the safe dosage range formatted for display in the UI.
    """
    age_bracket = get_age_bracket(patient_age)
    dosage_info = get_dosage_range(drug_name, age_bracket, patient_weight)

    if not dosage_info:
        return None

    result = {
        "ageBracket": age_bracket,
        "frequency": dosage_info.get("frequency", ""),
        "maxDailyDose": dosage_info.get("maxDailyDose", 0),
        "notes": dosage_info.get("notes", ""),
    }

    if age_bracket == "pediatric":
        mg_per_kg = dosage_info.get("mgPerKgPerDay", {})
        result["mgPerKgMin"] = mg_per_kg.get("min", 0)
        result["mgPerKgMax"] = mg_per_kg.get("max", 0)
        result["calculatedDailyMin"] = dosage_info.get("calculatedDailyMin", 0)
        result["calculatedDailyMax"] = dosage_info.get("calculatedDailyMax", 0)
        result["perDoseMin"] = dosage_info.get("calculatedPerDoseMin", 0)
        result["perDoseMax"] = dosage_info.get("calculatedPerDoseMax", 0)
        result["displayRange"] = (
            f"{result['perDoseMin']}–{result['perDoseMax']}mg per dose "
            f"({result['mgPerKgMin']}–{result['mgPerKgMax']} mg/kg/day for {patient_weight}kg)"
        )
    else:
        per_dose = dosage_info.get("dosePerAdmin", {})
        result["perDoseMin"] = per_dose.get("min", 0)
        result["perDoseMax"] = per_dose.get("max", 0)
        result["displayRange"] = f"{result['perDoseMin']}–{result['perDoseMax']}mg per dose"

    return result


def _parse_dose_mg(dose_str: str) -> float | None:
    """Parse a dose string like '500 mg' or '0.25 g' into mg."""
    if not dose_str:
        return None
    dose_str = dose_str.strip().lower()

    # Try to extract numeric value and unit
    match = re.match(r"([\d.]+)\s*(mg|g|mcg|ug|ml|units?|iu)?", dose_str)
    if not match:
        return None

    value = float(match.group(1))
    unit = match.group(2) or "mg"

    if unit == "g":
        return value * 1000
    elif unit in ("mcg", "ug"):
        return value / 1000
    elif unit == "mg":
        return value
    else:
        return value  # Assume mg for unknown units
