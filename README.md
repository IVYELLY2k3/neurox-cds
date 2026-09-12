# NeuroX — AI-Powered Unified Patient Medical Record & Clinical Decision Support System

> **One Patient → One Medical History → One Intelligent Safety Layer → Clean Prescription to Pharmacy**

A production-quality hackathon prototype combining a unified medical record with real-time AI prescription safety checks and a Zero-Knowledge privacy layer.

![Stack](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square)
![Stack](https://img.shields.io/badge/Frontend-React+Vite-61DAFB?style=flat-square)
![Stack](https://img.shields.io/badge/Privacy-Zero_Knowledge-00897B?style=flat-square)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ with pip
- Node.js 18+ with npm

### 1. Start the Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be running at `http://localhost:8000`

### 2. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will be running at `http://localhost:5173`

### 3. Open in Browser

Navigate to `http://localhost:5173` to start the application.

### One-command alternative (site + API together)

```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

If `backend/static` exists (it does — the built frontend ships with the repo),
this single command serves the entire app at `http://localhost:8000`.

---

## 🔑 AI Assistant — Bring Your Own Key

Every visitor can connect their **own** AI key via the **Connect AI Key** button
in the navbar. Supported providers: Z.AI (GLM), OpenAI, Groq, OpenRouter.
The key is stored only in the visitor's browser and forwarded per-request to
their chosen provider — it is never saved on the server, and the site owner
pays nothing for AI usage. With a key connected, safety alerts gain an
**AI Explain** button with clinical explanations. All core safety features
work for everyone with no key at all.

---

## 🌐 Publishing

See **[DEPLOY.md](DEPLOY.md)** — the app deploys as one free service
(Render / Hugging Face Spaces / Railway / Koyeb), no environment variables
required.

---

## 🎯 How to Demo the Full Flow

### Primary Demo: Arjun Mehta (Pediatric — Critical Alerts)

1. **Select Patient**: Click on **Arjun Mehta** (8yr, 25kg, Penicillin anaphylaxis)
2. **View History**: Browse the Medical History panel — see allergies, current medications (Phenytoin, Theophylline), diagnoses
3. **Enter Diagnosis**: Type "Upper Respiratory Tract Infection"
4. **Search Drug**: Type "**Amo**" in the medication field → Select **Amoxicillin** from the dropdown
5. **Enter Dose**: Type "**500 mg**" (this is an adult dose for a 25kg child)
6. **Watch the Alerts Panel** light up:
   - 🔴 **CRITICAL**: Penicillin-class allergy — Amoxicillin is in the Penicillin class, patient had anaphylaxis
   - 🟠 **HIGH**: Adult dose for pediatric patient — Safe range is ~208–417mg (25–50 mg/kg/day)
   - 🔵 **MODERATE**: Drug interaction — Amoxicillin may reduce Phenytoin absorption
   - All alerts show **"ZK Verified"** badges
7. **Change to safe drug**: Clear and type "**Azi**" → Select **Azithromycin** → Enter "**125 mg**"
8. **Add to Prescription** → **Generate Prescription**
9. **View the clean, printable prescription** ready for the pharmacy

### Secondary Demo: Priya Sharma (Warfarin Interactions)

1. Select **Priya Sharma** (72yr, on Warfarin, CKD Stage 3)
2. Try prescribing **Ibuprofen 400 mg** for pain
3. Watch: CRITICAL Warfarin-NSAID interaction + CRITICAL CKD-NSAID conflict

---

## 🏗️ Architecture

```
NEUROX1/
├── backend/                    # FastAPI Python Backend
│   ├── main.py                # API routes
│   ├── models/                # Pydantic data models
│   │   ├── patient.py         # FHIR-inspired patient model
│   │   ├── prescription.py    # Prescription models
│   │   └── alert.py           # Alert severity/type models
│   ├── services/              # Core clinical logic
│   │   ├── patient_service.py     # Module 1: Patient data
│   │   ├── drug_service.py        # Drug lookup + autocomplete
│   │   ├── lasa_detector.py       # Module 2: LASA detection
│   │   ├── dosage_validator.py    # Module 3: Dosage validation
│   │   ├── allergy_checker.py     # Module 4: Allergy checking
│   │   ├── interaction_checker.py # Module 5: Drug interactions
│   │   ├── disease_conflict_checker.py # Module 6: Disease conflicts
│   │   ├── duplicate_detector.py  # Module 7: Duplicate detection
│   │   ├── alert_engine.py        # Module 8: Alert prioritization
│   │   └── zk_service.py         # Zero-Knowledge privacy layer
│   └── data/                  # Synthetic clinical data
│       ├── patients.json      # 5 FHIR-inspired patient records
│       ├── drugs.json         # 60+ drugs with dosage ranges
│       ├── lasa_pairs.json    # 40 LASA drug pairs
│       ├── interactions.json  # 48 drug-drug interactions
│       └── disease_conflicts.json  # 32 disease-medication conflicts
├── frontend/                  # React + Vite Frontend
│   └── src/
│       ├── App.jsx            # Main application shell
│       ├── index.css          # Clinical design system
│       ├── components/        # UI components
│       └── services/api.js    # API client
└── README.md
```

---

## 🔒 Zero-Knowledge Privacy Layer

### How It Works

The ZK layer ensures that doctors receive **safety signals** without needing access to the full patient history from other providers.

**Key Principle**: The system can prove safety-relevant facts without revealing the underlying data.

#### Proof Types

| Proof Type | Statement (Doctor Sees) | Hidden Data |
|-----------|------------------------|-------------|
| `HAS_ALLERGY` | "Patient has documented serious allergic reaction to a medication in the prescribed drug's class." | Specific allergen, reaction details, dates |
| `WEIGHT_PEDIATRIC` | "Patient weight is in pediatric range. Weight-based dosing required." | Exact weight, growth data |
| `ON_INTERACTING_DRUG` | "Patient is currently on a medication that has a known interaction." | Drug names, doses, prescribers |
| `HAS_DISEASE_CONFLICT` | "Patient has an active diagnosis that may conflict with the prescribed medication." | Diagnosis details, ICD codes |
| `THERAPEUTIC_DUPLICATION` | "There is therapeutic duplication with a medication the patient is currently receiving." | Drug names, classes |

#### Technical Implementation

1. **Commitment Scheme**: Patient data is hashed using SHA-256 with a secret salt
2. **Proof Generation**: Safety-relevant facts are converted to human-readable statements with cryptographic commitments
3. **Verification**: Proofs can be verified by checking the commitment hash without accessing patient data
4. **Deterministic**: Same patient data produces the same proofs (reproducible)

In a production system, this would use actual ZK-SNARK or ZK-STARK circuits. For the hackathon, we use a cryptographic commitment scheme that demonstrates the core privacy concept.

---

## 🏥 Clinical Safety Modules

### Module 1: Unified Patient Medical History
FHIR-inspired patient records with visits, doctors, diagnoses, medications, allergies, labs, procedures, and clinical notes.

### Module 2: LASA Drug Name Confusion Detector
Uses `rapidfuzz` for fuzzy string matching against 40 known LASA pairs. Also checks diagnosis-drug consistency.

### Module 3: Patient-Specific Dosage Validator
Weight-based dosing for pediatric patients (mg/kg/day calculations). Detects adult doses given to children, decimal errors (10x/100x), and doses outside safe range.

### Module 4: Allergy & Adverse Reaction Safety Check
Matches against documented allergies with drug-class cross-reactivity (e.g., Amoxicillin → Penicillin class). Handles severity prioritization.

### Module 5: Drug-Drug Interaction Detector
Checks 48 interaction pairs with severity (Critical/High/Moderate). Includes mechanism and clinical effect descriptions.

### Module 6: Disease-Medication Conflict Detector
32 disease-drug contraindications covering CKD, liver disease, pregnancy, asthma, diabetes, and more.

### Module 7: Duplicate Medication Detector
Exact duplicate detection + therapeutic class overlap across 20 drug categories.

### Module 8: AI Alert Prioritization
Aggregates all alerts, deduplicates, attaches ZK proofs, and sorts by severity (Critical → High → Moderate → Info).

---

## 👥 Synthetic Patients

| Patient | Age | Weight | Key Features | Demo Purpose |
|---------|-----|--------|-------------|-------------|
| **Arjun Mehta** | 8 | 25kg | Penicillin anaphylaxis, on Phenytoin + Theophylline, epilepsy, asthma | ⭐ Primary demo — triggers Critical + High alerts |
| **Priya Sharma** | 72 | 58kg | CKD Stage 3, on Warfarin + Metformin, SJS history to Sulfonamides | Warfarin interactions + renal contraindications |
| **Rahul Verma** | 45 | 82kg | Diabetes, HTN, Aspirin-sensitive asthma | NSAID cross-reactivity |
| **Ananya Gupta** | 32 | 65kg | Pregnant, NSAID-induced GI bleed history | Pregnancy contraindications |
| **Vikram Singh** | 55 | 90kg | NAFLD, Codeine allergy, on Atorvastatin | Hepatotoxicity flags |

---

## ⚖️ Important Notes

- The AI **only flags and suggests** — it never automatically changes or cancels medication
- The doctor is always in full control of the final prescription decision
- This is a **hackathon prototype** intended for demonstration and decision support
- All patient data is **synthetic** — no real medical records are used

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI, Pydantic |
| Frontend | React, Vite, Lucide Icons |
| AI/Logic | `rapidfuzz` fuzzy matching, rule-based validation, contextual scoring |
| Privacy | SHA-256 commitment scheme (ZK simulation) |
| Data | FHIR-inspired JSON |
| Design | Hospital-grade clinical UI (Epic/Cerner-inspired) |
