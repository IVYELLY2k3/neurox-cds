"""
Pydantic models for prescriptions.
"""
from pydantic import BaseModel
from typing import Optional


class PrescriptionItem(BaseModel):
    drugId: Optional[str] = None
    drugName: str
    genericName: Optional[str] = None
    brandName: Optional[str] = None
    dose: str  # e.g., "500 mg"
    doseValue: Optional[float] = None  # numeric value in mg
    frequency: str
    route: str
    duration: Optional[str] = ""
    instructions: Optional[str] = None


class PrescriptionRequest(BaseModel):
    patientId: str
    diagnoses: list[str] = []
    items: list[PrescriptionItem]
    prescriber: str = "Dr. Demo Physician"
    pharmacyNotes: Optional[str] = None


class GeneratedPrescription(BaseModel):
    prescriptionId: str
    patientId: str
    patientName: str
    patientAge: int
    patientWeight: float
    patientMrn: str
    patientGender: str
    diagnoses: list[str] = []
    prescriber: str
    date: str
    items: list[PrescriptionItem]
    pharmacyNotes: Optional[str] = None
    alertsSummary: Optional[str] = None
