import React, { useRef } from 'react';
import { Printer, Send, X, Download } from 'lucide-react';

export default function PrescriptionOutput({ prescription, analysis, onClose }) {
  if (!prescription) return null;
  const printRef = useRef(null);

  const handlePrint = () => {
    window.print();
  };

  const currentDate = prescription.date || new Date().toLocaleDateString('en-IN', {
    day: '2-digit', month: '2-digit', year: 'numeric',
  });

  const currentTime = new Date().toLocaleTimeString('en-US', {
    hour: '2-digit', minute: '2-digit', hour12: true,
  });

  return (
    <div className="rx-output-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="rx-output-container">
        {/* Action bar — not printed */}
        <div className="rx-output-actions no-print">
          <button className="btn btn-primary" onClick={handlePrint}>
            <Printer size={14} /> Print
          </button>
          <button className="btn btn-success">
            <Send size={14} /> Send to Pharmacy
          </button>
          <button className="btn btn-outline">
            <Download size={14} /> Download PDF
          </button>
          <div style={{ flex: 1 }} />
          <button className="btn btn-outline" onClick={onClose}>
            <X size={14} /> Close
          </button>
        </div>

        {/* ═══════ PRINTABLE PRESCRIPTION ═══════ */}
        <div className="rx-prescription" ref={printRef} id="prescription-printable">

          {/* ── Hospital Header ── */}
          <div className="rx-hosp-header">
            <div className="rx-hosp-logo-area">
              <div className="rx-hosp-logo">
                <svg viewBox="0 0 40 40" width="40" height="40">
                  <rect x="0" y="0" width="40" height="40" rx="8" fill="#0D3B66"/>
                  <path d="M12 8 v24 h6 v-9 h4 v9 h6 v-24 h-6 v9 h-4 v-9z" fill="#4FC3F7"/>
                  <rect x="16" y="14" width="8" height="8" rx="1" fill="#fff" opacity="0.3"/>
                </svg>
              </div>
              <div className="rx-hosp-info">
                <h1 className="rx-hosp-name">NeuroX Medical Center</h1>
                <p className="rx-hosp-tagline">AI-Powered Clinical Decision Support</p>
              </div>
            </div>
          </div>

          {/* Decorative double line */}
          <div className="rx-divider-double" />

          {/* ── Doctor Info Bar ── */}
          <div className="rx-doctor-bar">
            <div className="rx-doctor-main">
              <strong>{prescription.prescriber || 'Dr. Demo Physician'}</strong>
              <span className="rx-doctor-qual">MBBS, MD (Internal Medicine)</span>
            </div>
            <div className="rx-doctor-reg">
              <span>Reg. No: <strong>MCI-2024-DEMO</strong></span>
              <span>Dept: General Medicine</span>
            </div>
          </div>

          <div className="rx-divider" />

          {/* ── Patient Information Block ── */}
          <div className="rx-patient-block">
            <div className="rx-patient-block-title">Patient Information</div>
            <div className="rx-patient-grid">
              <div className="rx-patient-field">
                <span className="rx-field-label">Name</span>
                <span className="rx-field-value">{prescription.patientName}</span>
              </div>
              <div className="rx-patient-field">
                <span className="rx-field-label">Age / Gender</span>
                <span className="rx-field-value">{prescription.patientAge} yrs / {prescription.patientGender}</span>
              </div>
              <div className="rx-patient-field">
                <span className="rx-field-label">Weight</span>
                <span className="rx-field-value">{prescription.patientWeight} kg</span>
              </div>
              <div className="rx-patient-field">
                <span className="rx-field-label">MRN</span>
                <span className="rx-field-value">{prescription.patientMrn}</span>
              </div>
              <div className="rx-patient-field">
                <span className="rx-field-label">Date</span>
                <span className="rx-field-value">{currentDate}</span>
              </div>
              <div className="rx-patient-field">
                <span className="rx-field-label">Rx ID</span>
                <span className="rx-field-value rx-field-mono">{prescription.prescriptionId}</span>
              </div>
            </div>
          </div>

          {/* ── Clinical Information ── */}
          <div className="rx-clinical-section">
            <div className="rx-clinical-row">
              <span className="rx-clinical-label">Diagnosis:</span>
              <span className="rx-clinical-value">
                {(prescription.diagnoses && prescription.diagnoses.length > 0)
                  ? prescription.diagnoses.map((d, i) => (
                      <span key={i} className="rx-diag-chip">{d}</span>
                    ))
                  : <em style={{ color: '#868E96' }}>As noted in clinical records</em>
                }
              </span>
            </div>
          </div>

          <div className="rx-divider" />

          {/* ── Rx Symbol + Medication List ── */}
          <div className="rx-medications-section">
            <div className="rx-symbol-large">℞</div>

            <div className="rx-med-list">
              {prescription.items.map((item, idx) => (
                <div key={idx} className="rx-med-row">
                  <div className="rx-med-number">{idx + 1}.</div>
                  <div className="rx-med-content">
                    <div className="rx-med-name-line">
                      <span className="rx-med-generic">{item.drugName || item.genericName}</span>
                      {item.brandName && (
                        <span className="rx-med-brand">({item.brandName})</span>
                      )}
                    </div>
                    <div className="rx-med-details-line">
                      <span className="rx-med-detail-item">
                        <span className="rx-med-detail-label">Dose:</span> {item.dose}
                      </span>
                      <span className="rx-med-detail-sep">•</span>
                      <span className="rx-med-detail-item">
                        <span className="rx-med-detail-label">Route:</span> {item.route}
                      </span>
                      <span className="rx-med-detail-sep">•</span>
                      <span className="rx-med-detail-item">
                        <span className="rx-med-detail-label">Freq:</span> {item.frequency}
                      </span>
                      {item.duration && (
                        <>
                          <span className="rx-med-detail-sep">•</span>
                          <span className="rx-med-detail-item">
                            <span className="rx-med-detail-label">Duration:</span> {item.duration}
                          </span>
                        </>
                      )}
                    </div>
                    {item.instructions && (
                      <div className="rx-med-instructions">
                        <em>📋 {item.instructions}</em>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* ── Pharmacy Notes ── */}
          {prescription.pharmacyNotes && (
            <div className="rx-pharmacy-notes">
              <strong>Pharmacy Notes:</strong> {prescription.pharmacyNotes}
            </div>
          )}

          {/* ── Safety Verification Badge ── */}
          {analysis && analysis.totalAlerts > 0 && (
            <div className="rx-safety-review">
              <div className="rx-safety-icon">⚠</div>
              <div className="rx-safety-text">
                <strong>Safety Review Completed</strong>
                <span>
                  {analysis.totalAlerts} alert(s) reviewed by prescriber
                  {analysis.criticalCount > 0 && ` — ${analysis.criticalCount} Critical`}
                  {analysis.highCount > 0 && `, ${analysis.highCount} High`}
                  {analysis.moderateCount > 0 && `, ${analysis.moderateCount} Moderate`}
                  {analysis.informationalCount > 0 && `, ${analysis.informationalCount} Info`}
                </span>
              </div>
            </div>
          )}

          {analysis && analysis.totalAlerts === 0 && (
            <div className="rx-safety-clear">
              <span>✅</span>
              <strong>No safety alerts detected — prescription verified.</strong>
            </div>
          )}

          <div className="rx-divider" />

          {/* ── Footer: Signature + Verification ── */}
          <div className="rx-footer-section">
            <div className="rx-footer-left">
              <div className="rx-verification-badges">
                <div className="rx-verify-item">
                  <span className="rx-verify-dot green" />
                  AI Safety Analysis: Complete
                </div>
                <div className="rx-verify-item">
                  <span className="rx-verify-dot teal" />
                  Zero-Knowledge Verified
                </div>
              </div>
              <div className="rx-qr-placeholder">
                <svg viewBox="0 0 60 60" width="60" height="60">
                  <rect width="60" height="60" fill="#F4F6F9" rx="4"/>
                  {/* Simple QR-like pattern */}
                  <rect x="5" y="5" width="15" height="15" fill="#0D3B66" rx="2"/>
                  <rect x="40" y="5" width="15" height="15" fill="#0D3B66" rx="2"/>
                  <rect x="5" y="40" width="15" height="15" fill="#0D3B66" rx="2"/>
                  <rect x="8" y="8" width="9" height="9" fill="#4FC3F7" rx="1"/>
                  <rect x="43" y="8" width="9" height="9" fill="#4FC3F7" rx="1"/>
                  <rect x="8" y="43" width="9" height="9" fill="#4FC3F7" rx="1"/>
                  <rect x="25" y="5" width="5" height="5" fill="#0D3B66"/>
                  <rect x="25" y="15" width="5" height="5" fill="#0D3B66"/>
                  <rect x="25" y="25" width="10" height="10" fill="#0D3B66" rx="2"/>
                  <rect x="25" y="40" width="5" height="5" fill="#0D3B66"/>
                  <rect x="40" y="30" width="5" height="5" fill="#0D3B66"/>
                  <rect x="50" y="40" width="5" height="5" fill="#0D3B66"/>
                  <rect x="40" y="50" width="15" height="5" fill="#0D3B66"/>
                  <rect x="5" y="25" width="5" height="5" fill="#0D3B66"/>
                  <rect x="15" y="30" width="5" height="5" fill="#0D3B66"/>
                </svg>
                <span className="rx-qr-label">Scan to verify</span>
              </div>
            </div>

            <div className="rx-footer-right">
              <div className="rx-signature-block">
                <div className="rx-signature-line-thick" />
                <div className="rx-signature-name">{prescription.prescriber || 'Dr. Demo Physician'}</div>
                <div className="rx-signature-desig">MBBS, MD (Internal Medicine)</div>
                <div className="rx-signature-stamp">Signature & Stamp</div>
              </div>
            </div>
          </div>

          {/* ── Bottom Tear-off Note ── */}
          <div className="rx-tearoff">
            <div className="rx-tearoff-line" />
            <div className="rx-tearoff-content">
              <div><strong>For Pharmacy Use</strong></div>
              <div className="rx-tearoff-grid">
                <span>Rx ID: {prescription.prescriptionId}</span>
                <span>Patient: {prescription.patientName}</span>
                <span>Date: {currentDate}</span>
                <span>Items: {prescription.items.length}</span>
              </div>
              <div className="rx-tearoff-dispensed">
                Dispensed by: ________________________ &nbsp;&nbsp; Date: ____________
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
