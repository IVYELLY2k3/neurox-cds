AI Conclave Hackathon
AI-Powered Unified Patient Medical Record & Clinical Decision Support System
Problem Statement
Patients often visit multiple hospitals and doctors throughout their lifetime, while important medical information can
remain fragmented across different hospital systems. During a new consultation, a doctor may not have immediate
access to the patient's complete history, including previous diagnoses, medications, adverse reactions, investigations
and treatment history. At the same time, digital prescription systems may not provide sufficient real-time contextual
safety checks before a prescription is finalized.
This creates a need for a unified medical record combined with an AI-based Clinical Decision Support (CDS) layer that
can use the patient's history to identify and prioritize potential medication and prescription errors.
Proposed AI-Based Solution
A centralized, continuously updated patient medical record that can be securely accessed by authorized healthcare
providers, together with a lightweight AI safety layer that reviews prescriptions in real time.
Module 1: Unified Patient Medical History
Maintains a longitudinal record beginning from the patient's first recorded hospital visit.
• Hospital/clinic visits
• Doctors consulted
• Diagnoses and diseases
• Previous and current medications
• Documented allergies and adverse reactions
• Lab reports and investigations
• Procedures and treatments
• Relevant clinical notes
• Age, weight and other prescription-relevant information
Module 2: Drug Name Confusion Detector
Detects look-alike/sound-alike (LASA) medication names and checks whether the selected drug is consistent with the
diagnosis.
• Fuzzy string matching against a LASA database
• Diagnosis–drug cross-checking
• Suggests a likely intended medication when a probable selection error is detected
Module 3: Patient-Specific Dosage Validator
Checks the entered dosage against a standard safe-range reference for the medication and the patient's age/weight
bracket.
• Detects unusually high or low doses
• Identifies decimal/entry mistakes
• Flags possible adult-dose use in pediatric patients
• Displays a concise confirmation alert

---

Module 4: Allergy & Adverse Reaction Safety Check
Uses documented history to warn when a prescribed medicine has previously caused an allergy or adverse reaction.
• Matches the proposed medication with recorded allergies/reactions
• Raises a high-priority warning for serious documented reactions
• Shows the relevant historical record to the doctor for verification
Module 5: Drug–Drug Interaction Detector
Reviews the new prescription against the patient's current medications and identifies potentially harmful interactions.
• Checks current medication list
• Flags potentially significant interactions
• Prioritizes alerts according to severity
Module 6: Disease–Medication Conflict Detector
Uses known diagnoses and clinical history to identify medications that may require review because of an existing
condition.
• Cross-references diagnosis with medication
• Flags potentially unsuitable prescriptions
• Provides the reason for the warning
Module 7: Duplicate Medication Detector
Identifies duplicate or overlapping medications across prescriptions from different doctors or hospitals.
• Compares current and previous medications
• Detects same or therapeutically overlapping medicines
• Helps reduce accidental duplication
Module 8: AI Alert Prioritization
Ranks detected issues so that doctors see the most important risks first rather than receiving a large number of equally
weighted warnings.
• Critical — potentially serious immediate safety concern
• High — requires prompt review
• Moderate — should be reviewed
• Informational — useful historical/contextual information
How the System Works
1. Patient identifies themselves at an authorized hospital  →  2. Doctor retrieves relevant medical history  →  3. Doctor
enters diagnosis and prescription  →  4. AI analyzes the prescription using patient history and reference data  →  5.
Alerts are generated and prioritized  →  6. Doctor reviews the warnings and makes the final decision.
Example
Patient History
New Prescription
AI Output
Documented serious reaction to Drug
X
Current medication: Drug Y
Weight: 25 kg
Drug X — 500 mg
CRITICAL: Previous documented reaction to
Drug X.
HIGH: Dosage requires verification for
patient's weight.
Output

---

A short, non-blocking, prioritized alert is displayed to the doctor before the prescription is finalized. The system should
explain why an alert was raised and point to the relevant patient-history information. The AI flags and suggests; it does
not automatically prescribe, change or cancel medication.
Why This Works for a Hackathon Demo
• Can be demonstrated using synthetic patient records; no real hospital data is required.
• A simple EHR-style prescription screen can simulate the doctor workflow.
• A static LASA database and dosage/reference tables can support the core safety modules.
• Fuzzy matching, rule-based checks and lightweight AI can provide an explainable prototype without requiring a heavy
ML model.
• The complete flow can be demonstrated end-to-end: patient history → prescription → AI checks → prioritized alerts.
Suggested Technology Stack
Frontend: React / HTML-CSS-JavaScript    Backend: Python (Flask/FastAPI)    Database: MongoDB/PostgreSQL or
mock JSON/CSV data    AI/Logic: fuzzy matching, rule-based validation and contextual risk scoring.
Core Hackathon Value
One Patient, One Medical History, One Intelligent Safety Layer. The system combines continuity of medical
information with real-time prescription safety checks, helping doctors make better-informed decisions while keeping the
healthcare professional in control.
Note: This is a hackathon prototype concept intended for demonstration and decision support, not a replacement for professional
clinical judgment.
