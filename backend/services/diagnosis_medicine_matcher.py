"""
Diagnosis–Medicine Matcher
Checks whether a prescribed medicine is commonly used for at least one of the entered diagnoses.
If not, returns a warning alert.
"""
from models.alert import SafetyAlert, AlertSeverity, AlertType

# Comprehensive mapping of diagnoses (lowercase keywords) to commonly used medicines (lowercase)
# Each key is a diagnosis keyword/phrase, and the value is a set of generic medicine names
DIAGNOSIS_MEDICINE_MAP = {
    # ── Fever / Pyrexia ──
    "fever": {
        "paracetamol", "ibuprofen", "aspirin", "naproxen", "diclofenac",
        "mefenamic acid", "nimesulide", "acetaminophen",
    },
    "pyrexia": {
        "paracetamol", "ibuprofen", "aspirin", "naproxen", "diclofenac",
        "mefenamic acid", "nimesulide",
    },

    # ── Pain / Analgesic conditions ──
    "pain": {
        "paracetamol", "ibuprofen", "diclofenac", "naproxen", "tramadol",
        "codeine", "aspirin", "gabapentin", "pregabalin", "mefenamic acid",
    },
    "headache": {
        "paracetamol", "ibuprofen", "aspirin", "naproxen", "sumatriptan",
    },
    "migraine": {
        "sumatriptan", "paracetamol", "ibuprofen", "naproxen", "aspirin",
        "propranolol", "amitriptyline", "valproic acid", "topiramate",
    },
    "musculoskeletal": {
        "ibuprofen", "diclofenac", "naproxen", "paracetamol", "tramadol",
        "methocarbamol", "cyclobenzaprine",
    },
    "arthritis": {
        "ibuprofen", "diclofenac", "naproxen", "prednisone", "prednisolone",
        "methotrexate", "hydroxychloroquine",
    },
    "neuropathic": {
        "gabapentin", "pregabalin", "amitriptyline", "duloxetine", "carbamazepine",
    },
    "toothache": {
        "ibuprofen", "paracetamol", "diclofenac", "amoxicillin", "clindamycin",
    },

    # ── Respiratory / Asthma / COPD ──
    "asthma": {
        "salbutamol", "montelukast", "prednisone", "prednisolone", "theophylline",
        "budesonide", "fluticasone", "ipratropium", "formoterol", "salmeterol",
        "beclomethasone",
    },
    "copd": {
        "salbutamol", "ipratropium", "tiotropium", "theophylline", "prednisone",
        "budesonide", "formoterol", "salmeterol",
    },
    "bronchitis": {
        "amoxicillin", "azithromycin", "doxycycline", "salbutamol",
        "paracetamol", "ibuprofen", "cephalexin", "levofloxacin",
        "prednisone", "prednisolone",
    },
    "pneumonia": {
        "amoxicillin", "azithromycin", "levofloxacin", "ceftriaxone",
        "doxycycline", "clarithromycin", "cephalexin", "ciprofloxacin",
        "paracetamol",
    },
    "cough": {
        "dextromethorphan", "codeine", "salbutamol", "ambroxol",
        "paracetamol", "azithromycin", "amoxicillin", "cetirizine",
        "chlorpheniramine", "montelukast",
    },
    "cold": {
        "paracetamol", "cetirizine", "chlorpheniramine", "pseudoephedrine",
        "ibuprofen", "amoxicillin", "azithromycin",
    },
    "sinusitis": {
        "amoxicillin", "azithromycin", "levofloxacin", "pseudoephedrine",
        "paracetamol", "ibuprofen", "cetirizine", "fluticasone",
    },
    "upper respiratory": {
        "amoxicillin", "azithromycin", "paracetamol", "ibuprofen",
        "cetirizine", "chlorpheniramine", "doxycycline",
    },
    "respiratory tract infection": {
        "amoxicillin", "azithromycin", "cephalexin", "levofloxacin",
        "paracetamol", "ibuprofen", "doxycycline", "clarithromycin",
    },
    "pharyngitis": {
        "amoxicillin", "azithromycin", "penicillin v", "paracetamol",
        "ibuprofen", "cephalexin",
    },
    "tonsillitis": {
        "amoxicillin", "azithromycin", "penicillin v", "cephalexin",
        "paracetamol", "ibuprofen",
    },

    # ── Urinary Tract Infections ──
    "urinary tract infection": {
        "ciprofloxacin", "levofloxacin", "nitrofurantoin", "trimethoprim",
        "amoxicillin", "cephalexin", "cefixime", "norfloxacin",
    },
    "uti": {
        "ciprofloxacin", "levofloxacin", "nitrofurantoin", "trimethoprim",
        "amoxicillin", "cephalexin", "cefixime", "norfloxacin",
    },
    "cystitis": {
        "ciprofloxacin", "nitrofurantoin", "trimethoprim", "cephalexin",
        "amoxicillin", "levofloxacin",
    },
    "pyelonephritis": {
        "ciprofloxacin", "levofloxacin", "ceftriaxone", "ampicillin",
    },

    # ── Gastrointestinal ──
    "gastritis": {
        "omeprazole", "pantoprazole", "ranitidine", "antacid", "sucralfate",
        "domperidone",
    },
    "gerd": {
        "omeprazole", "pantoprazole", "ranitidine", "domperidone",
        "metoclopramide",
    },
    "acid reflux": {
        "omeprazole", "pantoprazole", "ranitidine", "domperidone",
    },
    "peptic ulcer": {
        "omeprazole", "pantoprazole", "ranitidine", "sucralfate",
        "amoxicillin", "clarithromycin", "metronidazole",
    },
    "diarrhea": {
        "loperamide", "metronidazole", "ciprofloxacin", "ondansetron",
        "oral rehydration salts",
    },
    "nausea": {
        "ondansetron", "domperidone", "metoclopramide", "promethazine",
    },
    "vomiting": {
        "ondansetron", "domperidone", "metoclopramide", "promethazine",
    },
    "constipation": {
        "lactulose", "bisacodyl", "polyethylene glycol",
    },
    "gastroenteritis": {
        "ciprofloxacin", "metronidazole", "ondansetron", "domperidone",
        "paracetamol", "oral rehydration salts",
    },
    "abdominal pain": {
        "paracetamol", "hyoscine", "dicyclomine", "omeprazole",
        "pantoprazole", "tramadol",
    },

    # ── Infections (Bacterial) ──
    "infection": {
        "amoxicillin", "azithromycin", "ciprofloxacin", "levofloxacin",
        "cephalexin", "cefixime", "doxycycline", "metronidazole",
        "clindamycin", "ampicillin", "erythromycin", "clarithromycin",
    },
    "bacterial infection": {
        "amoxicillin", "azithromycin", "ciprofloxacin", "levofloxacin",
        "cephalexin", "cefixime", "doxycycline", "metronidazole",
        "clindamycin",
    },
    "skin infection": {
        "cephalexin", "clindamycin", "doxycycline", "amoxicillin",
        "dicloxacillin", "mupirocin",
    },
    "cellulitis": {
        "cephalexin", "clindamycin", "amoxicillin", "dicloxacillin",
    },
    "wound infection": {
        "amoxicillin", "cephalexin", "clindamycin", "metronidazole",
    },
    "sepsis": {
        "ceftriaxone", "meropenem", "vancomycin", "piperacillin",
    },
    "otitis media": {
        "amoxicillin", "azithromycin", "cefixime", "cephalexin",
        "paracetamol", "ibuprofen",
    },

    # ── Cardiovascular ──
    "hypertension": {
        "amlodipine", "lisinopril", "losartan", "metoprolol", "enalapril",
        "hydrochlorothiazide", "propranolol", "ramipril", "valsartan",
        "telmisartan", "atenolol", "nifedipine",
    },
    "high blood pressure": {
        "amlodipine", "lisinopril", "losartan", "metoprolol", "enalapril",
        "hydrochlorothiazide",
    },
    "heart failure": {
        "furosemide", "spironolactone", "lisinopril", "enalapril",
        "metoprolol", "digoxin", "carvedilol", "losartan",
    },
    "atrial fibrillation": {
        "warfarin", "digoxin", "metoprolol", "amiodarone", "rivaroxaban",
        "apixaban",
    },
    "angina": {
        "nitroglycerin", "amlodipine", "metoprolol", "atenolol",
        "propranolol", "aspirin", "clopidogrel", "atorvastatin",
    },
    "coronary artery disease": {
        "aspirin", "clopidogrel", "atorvastatin", "rosuvastatin",
        "metoprolol", "lisinopril", "amlodipine",
    },
    "dvt": {
        "warfarin", "heparin", "rivaroxaban", "apixaban",
    },
    "deep vein thrombosis": {
        "warfarin", "heparin", "rivaroxaban", "apixaban",
    },
    "stroke": {
        "aspirin", "clopidogrel", "warfarin", "atorvastatin",
    },

    # ── Diabetes ──
    "diabetes": {
        "metformin", "glimepiride", "insulin glargine", "gliclazide",
        "sitagliptin", "pioglitazone", "voglibose", "empagliflozin",
    },
    "diabetes mellitus": {
        "metformin", "glimepiride", "insulin glargine", "gliclazide",
        "sitagliptin",
    },
    "type 2 diabetes": {
        "metformin", "glimepiride", "sitagliptin", "pioglitazone",
        "empagliflozin", "dapagliflozin",
    },
    "type 1 diabetes": {
        "insulin glargine", "insulin lispro", "insulin aspart",
    },
    "hyperglycemia": {
        "metformin", "glimepiride", "insulin glargine",
    },

    # ── Cholesterol / Dyslipidemia ──
    "dyslipidemia": {
        "atorvastatin", "rosuvastatin", "simvastatin", "fenofibrate",
    },
    "hyperlipidemia": {
        "atorvastatin", "rosuvastatin", "simvastatin", "fenofibrate",
    },
    "high cholesterol": {
        "atorvastatin", "rosuvastatin", "simvastatin",
    },

    # ── Allergy ──
    "allergy": {
        "cetirizine", "chlorpheniramine", "hydroxyzine", "loratadine",
        "fexofenadine", "montelukast", "prednisolone", "prednisone",
    },
    "allergic rhinitis": {
        "cetirizine", "loratadine", "fexofenadine", "fluticasone",
        "montelukast", "chlorpheniramine",
    },
    "urticaria": {
        "cetirizine", "hydroxyzine", "loratadine", "fexofenadine",
        "prednisolone",
    },
    "anaphylaxis": {
        "epinephrine", "hydrocortisone", "chlorpheniramine",
    },

    # ── Epilepsy / Seizures ──
    "epilepsy": {
        "phenytoin", "carbamazepine", "valproic acid", "levetiracetam",
        "gabapentin", "lamotrigine", "topiramate",
    },
    "seizure": {
        "phenytoin", "carbamazepine", "valproic acid", "levetiracetam",
        "gabapentin", "diazepam", "lorazepam",
    },
    "convulsion": {
        "phenytoin", "carbamazepine", "valproic acid", "diazepam",
    },

    # ── Mental Health ──
    "depression": {
        "sertraline", "fluoxetine", "escitalopram", "amitriptyline",
        "venlafaxine", "duloxetine", "mirtazapine",
    },
    "anxiety": {
        "sertraline", "fluoxetine", "escitalopram", "hydroxyzine",
        "buspirone", "diazepam", "alprazolam", "lorazepam",
    },
    "insomnia": {
        "zolpidem", "hydroxyzine", "melatonin", "amitriptyline",
    },

    # ── Thyroid ──
    "hypothyroidism": {
        "levothyroxine",
    },
    "thyroid": {
        "levothyroxine", "carbimazole", "propylthiouracil",
    },
    "hyperthyroidism": {
        "carbimazole", "propylthiouracil", "propranolol",
    },

    # ── Edema / Fluid Overload ──
    "edema": {
        "furosemide", "hydrochlorothiazide", "spironolactone",
    },
    "fluid overload": {
        "furosemide", "spironolactone",
    },

    # ── Malaria ──
    "malaria": {
        "chloroquine", "artemether", "lumefantrine", "quinine",
        "primaquine", "paracetamol",
    },

    # ── Dental ──
    "dental": {
        "amoxicillin", "metronidazole", "clindamycin", "ibuprofen",
        "paracetamol",
    },
    "abscess": {
        "amoxicillin", "metronidazole", "clindamycin", "cephalexin",
    },

    # ── Skin conditions ──
    "eczema": {
        "hydrocortisone", "prednisolone", "cetirizine", "hydroxyzine",
        "emollients",
    },
    "dermatitis": {
        "hydrocortisone", "prednisolone", "cetirizine", "hydroxyzine",
    },
    "acne": {
        "doxycycline", "clindamycin", "isotretinoin", "erythromycin",
    },
    "fungal infection": {
        "fluconazole", "clotrimazole", "terbinafine", "itraconazole",
    },

    # ── Vitamin / Nutritional ──
    "anemia": {
        "ferrous sulfate", "iron", "folic acid", "vitamin b12",
    },
    "vitamin d deficiency": {
        "cholecalciferol", "vitamin d",
    },

    # ── Other common ──
    "gout": {
        "colchicine", "allopurinol", "indomethacin", "naproxen",
    },
    "osteoporosis": {
        "alendronate", "risedronate", "calcium", "vitamin d",
    },
}


def _normalize(text: str) -> str:
    """Lowercase and strip whitespace."""
    return text.lower().strip()


def check_diagnosis_medicine_match(
    drug_name: str,
    diagnoses: list[str],
) -> list[SafetyAlert]:
    """
    Check if a prescribed drug is commonly used for at least one of the entered diagnoses.
    Returns a warning alert if the drug does not match any diagnosis.

    Logic:
    - If there are no diagnoses, do not warn (nothing to compare against).
    - Compare the drug name against ALL diagnoses.
    - If it matches ANY one diagnosis, return NO warning.
    - If it matches NONE, return a warning alert.
    """
    if not diagnoses or not drug_name:
        return []

    drug_lower = _normalize(drug_name)

    for diagnosis in diagnoses:
        diag_lower = _normalize(diagnosis)

        # Check each key in the diagnosis-medicine map
        for diag_key, medicines in DIAGNOSIS_MEDICINE_MAP.items():
            # Check if the diagnosis text matches this key (fuzzy: either contains the other)
            if diag_key in diag_lower or diag_lower in diag_key:
                if drug_lower in medicines:
                    # Drug matches at least one diagnosis — no warning needed
                    return []

        # Also check individual words from the diagnosis for partial matching
        diag_words = [w for w in diag_lower.split() if len(w) > 3]
        for word in diag_words:
            for diag_key, medicines in DIAGNOSIS_MEDICINE_MAP.items():
                if word in diag_key or diag_key in word:
                    if drug_lower in medicines:
                        return []

    # If we get here, the drug didn't match ANY diagnosis
    diagnoses_str = ", ".join(diagnoses)
    return [SafetyAlert(
        id=f"DMM-{drug_name.replace(' ', '_')}-nomatch",
        severity=AlertSeverity.MODERATE,
        type=AlertType.DISEASE_CONFLICT,
        title=f"Diagnosis Mismatch: {drug_name}",
        message=(
            f"This medicine is not commonly used for any of the entered diagnoses. "
            f"Please verify the prescription."
        ),
        details=f"Entered diagnoses: {diagnoses_str}",
        recommendation=(
            f"Verify that {drug_name} is appropriate for the patient's condition(s): {diagnoses_str}. "
            f"If this is intentional (e.g., off-label use or prophylaxis), you may proceed."
        ),
        drugName=drug_name,
    )]
