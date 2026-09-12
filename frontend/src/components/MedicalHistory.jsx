import React, { useState } from 'react';
import { FileText, Pill, AlertTriangle, FlaskConical, Calendar, ClipboardList } from 'lucide-react';
import ZKBadge from './ZKBadge';

const TABS = [
  { key: 'meds', label: 'Medications', icon: Pill },
  { key: 'allergies', label: 'Allergies', icon: AlertTriangle },
  { key: 'diagnoses', label: 'Diagnoses', icon: FileText },
  { key: 'labs', label: 'Lab Results', icon: FlaskConical },
  { key: 'visits', label: 'Visits', icon: Calendar },
  { key: 'notes', label: 'Notes', icon: ClipboardList },
];

export default function MedicalHistory({ patient, zkProofs = [] }) {
  const [activeTab, setActiveTab] = useState('meds');

  return (
    <div className="dashboard-panel" style={{ background: '#FAFBFC' }}>
      <div className="history-tabs">
        {TABS.map(tab => (
          <button
            key={tab.key}
            className={`history-tab ${activeTab === tab.key ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.key)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div style={{ padding: '0' }}>
        {zkProofs.length > 0 && (
          <div style={{ padding: '8px 12px', background: '#E0F2F1', borderBottom: '1px solid #B2DFDB', fontSize: '0.7rem', color: '#00695C', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <ZKBadge /> Medical history accessed via Zero-Knowledge verification
          </div>
        )}

        {activeTab === 'meds' && <MedicationsTab medications={patient.currentMedications} />}
        {activeTab === 'allergies' && <AllergiesTab allergies={patient.allergies} />}
        {activeTab === 'diagnoses' && <DiagnosesTab diagnoses={patient.diagnoses} />}
        {activeTab === 'labs' && <LabsTab labs={patient.labResults} />}
        {activeTab === 'visits' && <VisitsTab visits={patient.visitHistory} />}
        {activeTab === 'notes' && <NotesTab notes={patient.clinicalNotes} />}
      </div>
    </div>
  );
}

function MedicationsTab({ medications }) {
  if (!medications?.length) return <EmptyState text="No current medications" />;
  return medications.map(med => (
    <div key={med.id} className="history-item">
      <div className="history-item-header">
        <div className="history-item-title">{med.drug}</div>
        <span className="history-item-badge status-active">Active</span>
      </div>
      <div className="history-item-body">
        <div>{med.dose} — {med.frequency} ({med.route})</div>
        <div style={{ marginTop: '2px', fontSize: '0.7rem', color: '#868E96' }}>
          {med.indication} • Prescribed by {med.prescribedBy} • Since {med.startDate}
        </div>
      </div>
    </div>
  ));
}

function AllergiesTab({ allergies }) {
  if (!allergies?.length) return <EmptyState text="No documented allergies" />;
  return allergies.map(allergy => (
    <div key={allergy.id} className="history-item">
      <div className="history-item-header">
        <div className="history-item-title">{allergy.substance}</div>
        <span className={`history-item-badge severity-${allergy.severity}`}>
          {allergy.severity}
        </span>
      </div>
      <div className="history-item-body">
        <div><strong>Reaction:</strong> {allergy.reaction}</div>
        {allergy.drugClass && <div><strong>Drug Class:</strong> {allergy.drugClass}</div>}
        <div style={{ marginTop: '4px', fontSize: '0.7rem', color: '#868E96' }}>
          {allergy.notes}
        </div>
        <div style={{ marginTop: '2px', fontSize: '0.68rem', color: '#ADB5BD' }}>
          Documented {allergy.documentedDate} by {allergy.documentedBy}
        </div>
      </div>
    </div>
  ));
}

function DiagnosesTab({ diagnoses }) {
  if (!diagnoses?.length) return <EmptyState text="No diagnoses on record" />;
  return diagnoses.map(dx => (
    <div key={dx.id} className="history-item">
      <div className="history-item-header">
        <div className="history-item-title">{dx.description}</div>
        <span className="history-item-badge status-active">{dx.status}</span>
      </div>
      <div className="history-item-body">
        <div>ICD: {dx.code}</div>
        <div style={{ fontSize: '0.7rem', color: '#868E96' }}>
          Diagnosed {dx.diagnosedDate} by {dx.diagnosedBy}
        </div>
      </div>
    </div>
  ));
}

function LabsTab({ labs }) {
  if (!labs?.length) return <EmptyState text="No lab results" />;
  return labs.map(lab => (
    <div key={lab.id} className="history-item">
      <div className="history-item-header">
        <div className="history-item-title">{lab.test}</div>
        <span className={`history-item-badge status-${lab.status}`}>{lab.status}</span>
      </div>
      <div className="history-item-body">
        <div><strong>Result:</strong> {lab.result}</div>
        <div>Ref: {lab.referenceRange}</div>
        <div style={{ fontSize: '0.7rem', color: '#868E96' }}>
          {lab.date} • Ordered by {lab.orderedBy}
        </div>
      </div>
    </div>
  ));
}

function VisitsTab({ visits }) {
  if (!visits?.length) return <EmptyState text="No visit history" />;
  return visits.map(visit => (
    <div key={visit.id} className="history-item">
      <div className="history-item-header">
        <div className="history-item-title">{visit.department}</div>
        <span className="history-item-date">{visit.date}</span>
      </div>
      <div className="history-item-body">
        <div><strong>{visit.facility}</strong> — {visit.doctor}</div>
        <div>Reason: {visit.reason}</div>
        <div style={{ marginTop: '4px', fontSize: '0.7rem', color: '#868E96' }}>
          {visit.notes}
        </div>
      </div>
    </div>
  ));
}

function NotesTab({ notes }) {
  if (!notes?.length) return <EmptyState text="No clinical notes" />;
  return notes.map(note => (
    <div key={note.id} className="history-item">
      <div className="history-item-header">
        <div className="history-item-title">{note.author}</div>
        <span className="history-item-date">{note.date}</span>
      </div>
      <div className="history-item-body">{note.note}</div>
    </div>
  ));
}

function EmptyState({ text }) {
  return (
    <div style={{ padding: '24px', textAlign: 'center', color: '#868E96', fontSize: '0.8rem' }}>
      {text}
    </div>
  );
}
