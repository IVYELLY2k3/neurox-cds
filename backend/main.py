"""
AI-Powered Unified Patient Medical Record & Clinical Decision Support System
FastAPI Backend Application
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from auth.auth_service import authenticate_doctor, authenticate_patient
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import httpx
import os
import uuid

from services.patient_service import (
    get_all_patients_summary,
    get_patient_by_id,
    search_patients,
    get_patient_medications,
    get_patient_diagnoses,
    add_patient,
)
from services.drug_service import search_drugs, get_drug_by_id, get_drug_by_name
from services.dosage_validator import get_safe_range_for_display
from services.alert_engine import analyze_prescription, analyze_full_prescription
from services.zk_service import get_patient_proofs, verify_proof as verify_zk_proof
from models.prescription import PrescriptionRequest, GeneratedPrescription, PrescriptionItem
from models.alert import ZKProofInfo

app = FastAPI(
    title="NeuroX Clinical Decision Support API",
    description="AI-Powered Unified Patient Medical Record & Clinical Decision Support System",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────── Patient Endpoints ────────────────

@app.get("/api/patients")
def list_patients():
    """List all patients with summary info."""
    return get_all_patients_summary()

@app.post("/api/patients")
def create_patient(patient_data: dict):
    """Add a new patient."""
    return add_patient(patient_data)

@app.get("/api/patients/search")
def search_patient(q: str = Query(..., min_length=1)):
    """Search patients by name or MRN."""
    results = search_patients(q)
    return [
        {
            "id": p["id"],
            "mrn": p["mrn"],
            "name": p["name"]["full"],
            "age": p["age"],
            "gender": p["gender"],
            "weight": p["weight"],
        }
        for p in results
    ]


@app.get("/api/patients/{patient_id}")
def get_patient(patient_id: str):
    """Get full patient record."""
    patient = get_patient_by_id(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@app.get("/api/patients/{patient_id}/history")
def get_patient_history(patient_id: str):
    """Get ZK-protected medical history for a patient."""
    patient = get_patient_by_id(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Return the history with ZK proofs attached
    proofs = get_patient_proofs(patient)
    return {
        "patient": {
            "id": patient["id"],
            "name": patient["name"]["full"],
            "age": patient["age"],
            "weight": patient["weight"],
        },
        "allergies": patient.get("allergies", []),
        "currentMedications": patient.get("currentMedications", []),
        "diagnoses": patient.get("diagnoses", []),
        "visitHistory": patient.get("visitHistory", []),
        "labResults": patient.get("labResults", []),
        "procedures": patient.get("procedures", []),
        "clinicalNotes": patient.get("clinicalNotes", []),
        "zkProofs": proofs,
    }


# ──────────────── Drug Endpoints ────────────────

@app.get("/api/drugs/search")
def drug_search(q: str = Query(..., min_length=1)):
    """Search drugs by name (brand or generic) for autocomplete."""
    return search_drugs(q)


@app.get("/api/drugs/{drug_id}")
def get_drug(drug_id: str):
    """Get full drug details by ID."""
    drug = get_drug_by_id(drug_id)
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")
    return drug


@app.get("/api/drugs/dosage-range")
def get_dosage_range(
    drug: str = Query(...),
    age: int = Query(...),
    weight: float = Query(...),
):
    """Get safe dosage range for a drug given patient age and weight."""
    result = get_safe_range_for_display(drug, age, weight)
    if not result:
        return {"found": False, "message": "Drug not found in database"}
    return {"found": True, **result}


# ──────────────── Prescription Analysis ────────────────

class SingleDrugAnalysis(BaseModel):
    patientId: str
    drugName: str
    dose: str
    diagnoses: list[str] = []


@app.post("/api/prescriptions/analyze")
def analyze_single_drug(request: SingleDrugAnalysis):
    """Analyze a single drug against patient record. Returns safety alerts."""
    patient = get_patient_by_id(request.patientId)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    result = analyze_prescription(
        patient, request.drugName, request.dose, request.diagnoses
    )
    return result.model_dump()


@app.post("/api/prescriptions/analyze-full")
def analyze_full_rx(request: PrescriptionRequest):
    """Analyze a full prescription (multiple drugs) against patient record."""
    patient = get_patient_by_id(request.patientId)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    items = [item.model_dump() for item in request.items]
    result = analyze_full_prescription(patient, items, request.diagnoses)
    return result.model_dump()


@app.post("/api/prescriptions/generate")
def generate_prescription(request: PrescriptionRequest):
    """Generate a final prescription document."""
    patient = get_patient_by_id(request.patientId)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Run final analysis
    items = [item.model_dump() for item in request.items]
    analysis = analyze_full_prescription(patient, items, request.diagnoses)

    # Generate prescription
    prescription = GeneratedPrescription(
        prescriptionId=f"RX-{uuid.uuid4().hex[:8].upper()}",
        patientId=patient["id"],
        patientName=patient["name"]["full"],
        patientAge=patient["age"],
        patientWeight=patient["weight"],
        patientMrn=patient.get("mrn", "UNKNOWN"),
        patientGender=patient.get("gender", "Unknown"),
        diagnoses=request.diagnoses,
        prescriber=request.prescriber,
        date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        items=request.items,
        pharmacyNotes=request.pharmacyNotes,
        alertsSummary=f"{analysis.totalAlerts} alerts ({analysis.criticalCount} critical, {analysis.highCount} high, {analysis.moderateCount} moderate)",
    )

    return {
        "prescription": prescription.model_dump(),
        "analysis": analysis.model_dump(),
    }


# ──────────────── ZK Proof Endpoints ────────────────

@app.get("/api/zk/proofs/{patient_id}")
def get_zk_proofs(patient_id: str):
    """Get pre-computed ZK proofs for a patient."""
    patient = get_patient_by_id(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return get_patient_proofs(patient)


class ZKVerifyRequest(BaseModel):
    proofId: str
    statement: str
    commitmentHash: str
    verified: bool = True
    timestamp: str = ""
    patientId: str = ""


@app.post("/api/zk/verify")
def verify_proof(request: ZKVerifyRequest):
    """Verify a ZK proof."""
    proof = ZKProofInfo(
        proofId=request.proofId,
        statement=request.statement,
        commitmentHash=request.commitmentHash,
        verified=request.verified,
        timestamp=request.timestamp or datetime.now(timezone.utc).isoformat(),
    )
    return verify_zk_proof(proof, request.patientId)


# ──────────────── AI Assistant (Bring Your Own Key) ────────────────
# Each user connects their own AI provider key in the app's AI Settings.
# The key is stored only in the user's browser and forwarded per-request;
# it is never persisted or logged on this server.

AI_PROVIDERS = {
    "zai": {
        "name": "Z.AI (GLM)",
        "url": "https://api.z.ai/api/paas/v4/chat/completions",
        "default_model": "glm-4-flash",
    },
    "openai": {
        "name": "OpenAI",
        "url": "https://api.openai.com/v1/chat/completions",
        "default_model": "gpt-4o-mini",
    },
    "groq": {
        "name": "Groq (free tier available)",
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "default_model": "llama-3.3-70b-versatile",
    },
    "openrouter": {
        "name": "OpenRouter",
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "default_model": "openrouter/auto",
    },
}


class AIAssistantRequest(BaseModel):
    provider: str = "zai"
    apiKey: str
    model: str = ""
    messages: list[dict] = []

class DoctorLoginRequest(BaseModel):
    email: str
    password: str

@app.post("/api/auth/login")
def doctor_login(credentials: DoctorLoginRequest):
    """
    Authenticate a predefined doctor account.
    """
    email = credentials.email
    password = credentials.password

    if not email or not password:
        raise HTTPException(
            status_code=400,
            detail="Email and password are required"
        )

    doctor = authenticate_doctor(email, password)

    if not doctor:
        raise HTTPException(
            status_code=401,
            detail="Invalid doctor credentials"
        )

    return {
        "success": True,
        "doctor": doctor
    }


class PatientLoginRequest(BaseModel):
    email: str
    password: str

@app.post("/api/auth/patient-login")
def patient_login(credentials: PatientLoginRequest):
    """
    Authenticate a predefined patient portal account and confirm the
    linked medical record exists.
    """
    email = credentials.email
    password = credentials.password

    if not email or not password:
        raise HTTPException(
            status_code=400,
            detail="Email and password are required"
        )

    account = authenticate_patient(email, password)

    if not account:
        raise HTTPException(
            status_code=401,
            detail="Invalid patient credentials"
        )

    patient = get_patient_by_id(account["patientId"])
    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Linked patient record not found"
        )

    return {
        "success": True,
        "patient": {
            "patientId": patient["id"],
            "name": patient["name"]["full"],
            "email": account["email"],
            "mrn": patient.get("mrn", "")
        }
    }

@app.get("/api/ai/providers")
def list_ai_providers():
    """Providers supported by the bring-your-own-key AI assistant."""
    return {key: {"name": p["name"], "defaultModel": p["default_model"]} for key, p in AI_PROVIDERS.items()}


@app.post("/api/ai/assistant")
async def ai_assistant(request: AIAssistantRequest):
    """Forward a chat-completion request to the user's chosen AI provider.

    The user's API key travels in the request body from their browser, is used
    for this single call, and is never stored.
    """
    provider = AI_PROVIDERS.get(request.provider)
    if not provider:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown provider. Choose one of: {', '.join(AI_PROVIDERS)}",
        )
    if not request.apiKey or not request.apiKey.strip():
        raise HTTPException(
            status_code=400,
            detail="No AI key connected. Open AI Settings to connect your own key.",
        )

    payload = {
        "model": request.model.strip() or provider["default_model"],
        "messages": request.messages,
        "temperature": 0.3,
        "max_tokens": 600,
    }
    headers = {
        "Authorization": f"Bearer {request.apiKey.strip()}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(provider["url"], json=payload, headers=headers)
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="The AI provider timed out. Please try again.")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Could not reach the AI provider: {e}")

    if resp.status_code == 401:
        raise HTTPException(status_code=401, detail="Invalid API key — please check it in AI Settings.")
    if resp.status_code == 429:
        raise HTTPException(status_code=429, detail="Rate limited by the AI provider. Try again in a moment.")
    if resp.status_code != 200:
        detail = ""
        try:
            detail = resp.json().get("error", {}).get("message", "")
        except Exception:
            pass
        raise HTTPException(
            status_code=resp.status_code,
            detail=detail or f"AI provider error ({resp.status_code}).",
        )

    data = resp.json()
    choices = data.get("choices") or []
    if not choices:
        raise HTTPException(status_code=502, detail="The AI provider returned an empty response.")
    content = ((choices[0].get("message") or {}).get("content") or "").strip()
    return {"content": content, "model": data.get("model", payload["model"])}


# ──────────────── Health Check ────────────────

@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "NeuroX Clinical Decision Support",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ──────────────── Static Frontend (for deployment) ────────────────
# When the built frontend (frontend/dist) has been copied into backend/static,
# this single service serves both the API and the site.

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")


@app.get("/", include_in_schema=False)
def serve_root():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "message": "NeuroX API is running. Frontend not built yet — see DEPLOY.md.",
        "docs": "/docs",
    }


# Mounted last so all /api routes above take precedence.
if os.path.isdir(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="frontend")
