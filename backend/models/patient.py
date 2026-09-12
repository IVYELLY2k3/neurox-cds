"""
Pydantic models for FHIR-inspired patient records.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import date


class EmergencyContact(BaseModel):
    name: str
    relation: str
    phone: str


class Contact(BaseModel):
    phone: str
    email: str
    emergencyContact: EmergencyContact


class Allergy(BaseModel):
    id: str
    substance: str
    drugClass: Optional[str] = None
    reaction: str
    severity: str  # mild, moderate, severe
    status: str
    documentedDate: str
    documentedBy: str
    notes: str


class Medication(BaseModel):
    id: str
    drug: str
    genericName: str
    brandName: str
    drugClass: str
    dose: str
    frequency: str
    route: str
    startDate: str
    prescribedBy: str
    indication: str
    status: str


class Diagnosis(BaseModel):
    id: str
    code: str
    description: str
    status: str
    diagnosedDate: str
    diagnosedBy: str


class Vitals(BaseModel):
    weight: float
    height: float
    temp: float
    bp: str
    hr: int


class Visit(BaseModel):
    id: str
    date: str
    facility: str
    doctor: str
    department: str
    reason: str
    notes: str
    vitals: Vitals


class LabResult(BaseModel):
    id: str
    test: str
    result: str
    referenceRange: str
    status: str
    date: str
    orderedBy: str


class Procedure(BaseModel):
    id: str
    name: str
    date: str
    facility: str
    result: str
    performedBy: str


class ClinicalNote(BaseModel):
    id: str
    date: str
    author: str
    note: str


class PatientName(BaseModel):
    given: str
    family: str
    full: str


class Patient(BaseModel):
    id: str
    resourceType: str = "Patient"
    mrn: str
    name: PatientName
    gender: str
    dateOfBirth: str
    age: int
    weight: float
    height: float
    bloodType: str
    contact: Contact
    allergies: list[Allergy]
    currentMedications: list[Medication]
    diagnoses: list[Diagnosis]
    visitHistory: list[Visit]
    labResults: list[LabResult]
    procedures: list[Procedure]
    clinicalNotes: list[ClinicalNote]
