import React from 'react';
import { AlertTriangle, Droplets, Calendar, Weight, User } from 'lucide-react';

export default function PatientHeader({ patient, onBack }) {
  const initials = patient.name.full
    ? patient.name.full.split(' ').map(n => n[0]).join('')
    : '?';

  const severeAllergies = patient.allergies?.filter(a => a.severity === 'severe') || [];

  return (
    <div className="patient-header">
      <div className="patient-avatar">{initials}</div>

      <div className="patient-info">
        <div className="patient-name">{patient.name.full}</div>
        <div className="patient-meta">
          <span className="patient-meta-item">
            <User size={13} />
            <strong>{patient.age}y</strong> {patient.gender}
          </span>
          <span className="patient-meta-item">
            <Weight size={13} />
            <strong>{patient.weight} kg</strong>
          </span>
          <span className="patient-meta-item">
            <Droplets size={13} />
            {patient.bloodType}
          </span>
          <span className="patient-meta-item">
            MRN: <strong>{patient.mrn}</strong>
          </span>
        </div>
      </div>

      <div className="patient-critical-allergies">
        {severeAllergies.map(a => (
          <span key={a.id} className="allergy-badge">
            <AlertTriangle size={11} />
            {a.substance}: {a.reaction}
          </span>
        ))}
        {onBack && (
          <button
            className="btn btn-outline"
            onClick={onBack}
            style={{ marginLeft: '8px', padding: '4px 12px', fontSize: '0.7rem' }}
          >
            ← Back
          </button>
        )}
      </div>
    </div>
  );
}
