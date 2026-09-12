import sys
import os

sys.path.append(os.path.abspath('backend'))

from services.patient_service import add_patient, get_patient_by_id
from services.zk_service import get_patient_proofs
import json

print("Testing adding a new patient...")
new_patient = {
    "name": {"given": "Alan", "family": "Renny", "full": "Alan Renny"},
    "gender": "male",
    "age": 20,
    "weight": 75,
    "height": 170,
    "bloodType": "A+",
    "contact": {"phone": "", "email": "", "emergencyContact": {"name": "", "relation": "", "phone": ""}}
}
try:
    added = add_patient(new_patient)
    print("Added successfully. ID:", added["id"])
except Exception as e:
    print("Error adding:", e)

print("\nTesting getting proofs for new patient...")
try:
    patient_new = get_patient_by_id(added["id"])
    proofs = get_patient_proofs(patient_new)
    print("Proofs for new patient:", proofs)
except Exception as e:
    print("Error getting proofs for new patient:", e)

print("\nTesting getting proofs for existing patient...")
try:
    patient_existing = get_patient_by_id("PAT-001")
    proofs = get_patient_proofs(patient_existing)
    print("Proofs for existing patient:", proofs)
except Exception as e:
    print("Error getting proofs for existing patient:", e)
