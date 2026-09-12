"""
Module 1: Patient Service
Loads and manages synthetic patient records.
"""
import json
import os
from typing import Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
_patients_cache = None


def _load_patients() -> list[dict]:
    global _patients_cache
    if _patients_cache is None:
        with open(os.path.join(DATA_DIR, "patients.json"), "r", encoding="utf-8") as f:
            _patients_cache = json.load(f)
    return _patients_cache

def add_patient(patient_data: dict) -> dict:
    import uuid
    import datetime
    patients = _load_patients()
    patient_data["id"] = f"P-{uuid.uuid4().hex[:6].upper()}"
    if "mrn" not in patient_data or not patient_data["mrn"]:
        patient_data["mrn"] = f"MRN-{datetime.datetime.now().year}-{uuid.uuid4().hex[:4].upper()}"
    
    # Initialize empty lists if not provided
    for list_field in ["allergies", "currentMedications", "diagnoses", "visitHistory", "labResults", "procedures", "clinicalNotes"]:
        if list_field not in patient_data:
            patient_data[list_field] = []
            
    patients.append(patient_data)
    with open(os.path.join(DATA_DIR, "patients.json"), "w", encoding="utf-8") as f:
        json.dump(patients, f, indent=2)
    
    global _patients_cache
    _patients_cache = patients
    return patient_data

def get_all_patients_summary() -> list[dict]:
    """Return a summary list of all patients (for selection screen)."""
    patients = _load_patients()
    summaries = []
    for p in patients:
        summaries.append({
            "id": p.get("id"),
            "mrn": p.get("mrn", "Unknown"),
            "name": p.get("name", {}).get("full", "Unknown"),
            "age": p.get("age", 0),
            "gender": p.get("gender", "Unknown"),
            "weight": p.get("weight", 0),
            "bloodType": p.get("bloodType", "Unknown"),
            "allergiesCount": len(p.get("allergies", [])),
            "activeMedsCount": len([m for m in p.get("currentMedications", []) if m.get("status") == "active"]),
            "diagnosesCount": len(p.get("diagnoses", [])),
            "criticalAllergies": [
                a.get("substance", "Unknown") for a in p.get("allergies", []) if a.get("severity") == "severe"
            ],
        })
    return summaries


def get_patient_by_id(patient_id: str) -> Optional[dict]:
    """Return full patient record by ID."""
    patients = _load_patients()
    for p in patients:
        if p["id"] == patient_id:
            return p
    return None


def search_patients(query: str) -> list[dict]:
    """Search patients by name or MRN."""
    query = query.lower().strip()
    patients = _load_patients()
    results = []
    for p in patients:
        if (query in p["name"]["full"].lower()
                or query in p["mrn"].lower()
                or query in p["name"]["given"].lower()
                or query in p["name"]["family"].lower()):
            results.append(p)
    return results


def get_patient_allergies(patient_id: str) -> list[dict]:
    """Get allergies for a patient."""
    patient = get_patient_by_id(patient_id)
    if not patient:
        return []
    return patient.get("allergies", [])


def get_patient_medications(patient_id: str) -> list[dict]:
    """Get current active medications for a patient."""
    patient = get_patient_by_id(patient_id)
    if not patient:
        return []
    return [m for m in patient.get("currentMedications", []) if m["status"] == "active"]


def get_patient_diagnoses(patient_id: str) -> list[dict]:
    """Get active diagnoses for a patient."""
    patient = get_patient_by_id(patient_id)
    if not patient:
        return []
    return [d for d in patient.get("diagnoses", []) if d["status"] == "active"]


def get_age_bracket(age: int) -> str:
    """Determine age bracket for dosage calculations."""
    if age < 12:
        return "pediatric"
    elif age >= 65:
        return "geriatric"
    else:
        return "adult"
