# Arjun Mehta — Full Demo Script

Every scenario below was tested against the live backend. Arjun is the
richest demo patient: **8 years old, 25 kg, male** with a **severe Penicillin
anaphylaxis**, on **Phenytoin 50 mg** (epilepsy) and **Theophylline 75 mg**
(asthma), diagnosed with **Epilepsy (partial seizures)** and **Bronchial
Asthma (mild persistent)**.

How to run a scenario: select **Arjun Mehta** → type the Diagnosis → type the
drug name and pick it from the autocomplete → type the dose → watch the
**AI Safety Alerts** panel.

---

## Patient Portal login

The login page has **Doctor** and **Patient** tabs. Demo patient accounts
(all with password `patient123`) map to the five seeded patients:

| Patient | Email | Password |
|---|---|---|
| Arjun Mehta | `parent.mehta@email.com` | `patient123` |
| Priya Sharma | `priya.sharma@email.com` | `patient123` |
| Rahul Verma | `rahul.verma@email.com` | `patient123` |
| Ananya Gupta | `ananya.gupta@email.com` | `patient123` |
| Vikram Singh | `vikram.singh@email.com` | `patient123` |

A patient login opens a **read-only** view of that patient's own unified
record (medications, allergies, diagnoses, labs, visits, notes) with the ZK
verification badge — the doctor workflow is unchanged. Accounts are defined
in `backend/auth/patient_accounts.json` (`POST /api/auth/patient-login`).

---

## Scenario 1 — The headline demo (fires 5 alerts from 4 modules)

| Field | Enter |
|---|---|
| Diagnosis | `Upper Respiratory Tract Infection` |
| Drug | `Amoxicillin` |
| Dose | `500 mg` |

Verified alerts:

- 🔴 **CRITICAL** Drug-class allergy: Amoxicillin is in the **Penicillins** class — patient had anaphylaxis *(Allergy module)*
- 🟠 **HIGH** Dose exceeds safe pediatric range — 25 kg child needs 25–50 mg/kg/day (≈625–1250 mg/day); 500 mg × 3 = 1500 *(Dosage module)*
- 🟠 **HIGH** LASA warning: Amoxicillin ↔ Ampicillin *(LASA module)*
- 🔵 **MODERATE** Interaction: Amoxicillin ↔ his current Phenytoin *(Interaction module)*
- 🔵 **MODERATE** Diagnosis mismatch *(LASA module)*

Every alert carries a **ZK Verified** badge — click it to see the proof
statement without exposing the underlying record.

## Scenario 2 — The safe fix → clean prescription

Same diagnosis, but: Drug `Azithromycin`, Dose `125 mg` (≈5 mg/kg for 25 kg).

Only mild informational notes remain (name-similarity with Erythromycin).
**Add to Prescription → Generate Prescription** → shows the clean, printable
prescription (no address header) → **Print**.

## Scenario 3 — Decimal-point 10× overdose

Diagnosis `Fever`, Drug `Paracetamol`, Dose `2500 mg` (a typo for 250):

- 🔴 **CRITICAL** Possible decimal error — 10× overdose
- 🔴 **CRITICAL** Single dose exceeds maximum **daily** dose
- 🟠 **HIGH** Adult dose for pediatric patient (needs 40–60 mg/kg/day)

Now retype the dose as `250 mg` → **zero alerts**. Great before/after moment.

## Scenario 4 — Disease conflict: epilepsy

Diagnosis `Pain`, Drug `Tramadol`, Dose `50 mg`:

- 🔴 **CRITICAL** Not recommended under 12 years
- 🔴 **CRITICAL** Disease conflict — Tramadol lowers the seizure threshold (active epilepsy)
- 🟠 **HIGH** Adult dose for pediatric patient
- 🔵 **MODERATE** LASA: Tramadol ↔ Trazodone

## Scenario 5 — Disease conflict: asthma

Diagnosis `Migraine prophylaxis`, Drug `Propranolol`, Dose `10 mg`:

- 🔴 **CRITICAL** Disease conflict — beta-blockers can trigger bronchospasm (active asthma)

## Scenario 6 — Drug–drug interaction with his current meds

Diagnosis `Upper Respiratory Tract Infection`, Drug `Erythromycin`, Dose `250 mg`:

- 🟠 **HIGH** Interaction: Erythromycin ↔ his current Theophylline (raises Theophylline to toxic levels)

## Scenario 7 — One drug, three modules

Diagnosis `Epilepsy`, Drug `Carbamazepine`, Dose `200 mg`:

- 🟠 **HIGH** Interaction: Carbamazepine ↔ his current Phenytoin
- 🔵 **MODERATE** Therapeutic duplication with Phenytoin (both Anticonvulsants)
- 🟠 **HIGH** LASA: Carbamazepine ↔ Oxcarbazepine

## Scenario 8 — Bring-your-own-key AI explanations

1. Click **Connect AI Key** (navbar) → pick Z.AI or Groq (both have free keys)
   → paste key → **Connect**.
2. Run Scenario 1 again → click **AI Explain** on the critical allergy alert →
   clinical explanation of why it matters, the mechanism, and safer
   alternatives — powered by *your own* key, never the site owner's.

---

## While you're on Arjun's dashboard

- **Medical History panel** (left) — tabs for Medications, Allergies,
  Diagnoses, Labs, Visits, Notes: the unified record story.
- The ZK proofs show safety facts ("patient has a serious allergy in this
  drug class") **without** revealing the allergen, dates, or prescribers.

## Suggested 5-minute demo order

1. Scenario 1 (the shock) → 2 (the fix + generate prescription)
2. Scenario 3 (decimal error)
3. Scenario 7 (three modules at once)
4. Scenario 8 (AI explain, if key connected)
5. Scenarios 4–6 on demand if judges ask about disease conflicts/interactions.
