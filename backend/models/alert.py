"""
Alert models for the clinical decision support system.
"""
from pydantic import BaseModel
from typing import Optional
from enum import Enum


class AlertSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MODERATE = "moderate"
    INFORMATIONAL = "informational"


class AlertType(str, Enum):
    ALLERGY = "allergy"
    DOSAGE = "dosage"
    LASA = "lasa"
    INTERACTION = "interaction"
    DISEASE_CONFLICT = "disease_conflict"
    DUPLICATE = "duplicate"


class ZKProofInfo(BaseModel):
    proofId: str
    statement: str
    verified: bool
    commitmentHash: str
    timestamp: str


class SafetyAlert(BaseModel):
    id: str
    severity: AlertSeverity
    type: AlertType
    title: str
    message: str
    details: Optional[str] = None
    evidence: Optional[str] = None
    recommendation: Optional[str] = None
    drugName: Optional[str] = None
    zkProof: Optional[ZKProofInfo] = None

    @property
    def severity_order(self) -> int:
        order = {
            AlertSeverity.CRITICAL: 0,
            AlertSeverity.HIGH: 1,
            AlertSeverity.MODERATE: 2,
            AlertSeverity.INFORMATIONAL: 3,
        }
        return order.get(self.severity, 99)


class AnalysisResult(BaseModel):
    patientId: str
    alerts: list[SafetyAlert]
    totalAlerts: int
    criticalCount: int
    highCount: int
    moderateCount: int
    informationalCount: int
    analysisTimestamp: str
    zkVerified: bool
