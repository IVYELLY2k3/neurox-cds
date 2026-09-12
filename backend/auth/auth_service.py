"""
Authentication Service
Hackathon prototype with predefined doctor and patient accounts.
"""

import json
import os
import hashlib
import secrets

AUTH_DIR = os.path.dirname(__file__)
DOCTORS_FILE = os.path.join(AUTH_DIR, "doctors.json")
PATIENT_ACCOUNTS_FILE = os.path.join(AUTH_DIR, "patient_accounts.json")


def _load_doctors() -> list[dict]:
    """Load predefined doctor accounts."""
    with open(DOCTORS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_patient_accounts() -> list[dict]:
    """Load predefined patient portal accounts."""
    with open(PATIENT_ACCOUNTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def authenticate_doctor(email: str, password: str) -> dict | None:
    """
    Authenticate a doctor using email and password.

    Returns doctor information if credentials are valid.
    Returns None if authentication fails.
    """
    doctors = _load_doctors()
    password_hash = _hash_password(password)

    for doctor in doctors:
        # Support both plaintext prototype passwords and future hashes
        stored_password = doctor.get("password", "")
        stored_hash = doctor.get("passwordHash", "")

        if stored_hash:
            password_matches = secrets.compare_digest(
                password_hash,
                stored_hash
            )
        else:
            password_matches = secrets.compare_digest(
                password,
                stored_password
            )

        if (
            doctor.get("email", "").lower() == email.lower().strip()
            and password_matches
        ):
            return {
                "id": doctor["id"],
                "name": doctor["name"],
                "email": doctor["email"],
                "specialization": doctor.get("specialization", "")
            }

    return None


def authenticate_patient(email: str, password: str) -> dict | None:
    """
    Authenticate a patient portal account.

    Returns the linked patient identity if credentials are valid.
    Returns None if authentication fails.
    """
    accounts = _load_patient_accounts()
    password_hash = _hash_password(password)

    for account in accounts:
        # Support both plaintext prototype passwords and future hashes
        stored_password = account.get("password", "")
        stored_hash = account.get("passwordHash", "")

        if stored_hash:
            password_matches = secrets.compare_digest(
                password_hash,
                stored_hash
            )
        else:
            password_matches = secrets.compare_digest(
                password,
                stored_password
            )

        if (
            account.get("email", "").lower() == email.lower().strip()
            and password_matches
        ):
            return {
                "patientId": account["patientId"],
                "name": account.get("name", ""),
                "email": account["email"]
            }

    return None