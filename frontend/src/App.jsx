import React, { useState, useCallback, useEffect } from 'react';
import { Activity, Shield, Clock, KeyRound } from 'lucide-react';
import PatientSelector from './components/PatientSelector';
import Login from './components/Login';
import PatientHeader from './components/PatientHeader';
import MedicalHistory from './components/MedicalHistory';
import PrescriptionEntry from './components/PrescriptionEntry';
import SafetyAlerts from './components/SafetyAlerts';
import PrescriptionOutput from './components/PrescriptionOutput';
import AiSettings from './components/AiSettings';
import { getPatient, getPatientHistory, generatePrescription } from './services/api';
import { getAiConfig } from './services/aiClient';


export default function App() {
  // Workflow state
  const [view, setView] = useState('select');
  const [doctor, setDoctor] = useState(null);
  const [patientUser, setPatientUser] = useState(null);
  const [patient, setPatient] = useState(null);
  const [zkProofs, setZkProofs] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [rxOutput, setRxOutput] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleLogin = (doctorData) => {
  setDoctor(doctorData);
};

const handlePatientLogin = async (account) => {
  setLoading(true);
  try {
    const [patientData, history] = await Promise.all([
      getPatient(account.patientId),
      getPatientHistory(account.patientId),
    ]);
    setPatientUser(account);
    setPatient(patientData);
    setZkProofs(history.zkProofs || []);
    setView('portal');
  } catch (err) {
    console.error('Failed to load patient record:', err);
    throw err;
  } finally {
    setLoading(false);
  }
};

const handleLogout = () => {
  setDoctor(null);
  setPatientUser(null);
  setPatient(null);
  setAlerts([]);
  setAnalysis(null);
  setRxOutput(null);
  setView('select');
};

  const handleSelectPatient = async (patientId) => {
    setLoading(true);
    try {
      const [patientData, history] = await Promise.all([
        getPatient(patientId),
        getPatientHistory(patientId),
      ]);
      setPatient(patientData);
      setZkProofs(history.zkProofs || []);
      setAlerts([]);
      setAnalysis(null);
      setRxOutput(null);
      setView('dashboard');
    } catch (err) {
      console.error('Failed to load patient:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    setView('select');
    setPatient(null);
    setAlerts([]);
    setAnalysis(null);
    setRxOutput(null);
  };

  const handleAlertsUpdate = useCallback((newAlerts, newAnalysis) => {
    setAlerts(newAlerts);
    if (newAnalysis) setAnalysis(newAnalysis);
  }, []);

  const [generating, setGenerating] = useState(false);
  const [generateError, setGenerateError] = useState(null);

  // Bring-your-own-key AI assistant settings
  const [aiConnected, setAiConnected] = useState(false);
  const [showAiSettings, setShowAiSettings] = useState(false);

  useEffect(() => {
    setAiConnected(!!getAiConfig());
  }, []);

  const handleGenerateRx = async (rxData) => {
    setGenerating(true);
    setGenerateError(null);
    try {
      const result = await generatePrescription(rxData);
      setRxOutput(result);
    } catch (err) {
      console.error('Failed to generate prescription:', err);
      setGenerateError(err.message || 'Failed to generate prescription. Please try again.');
      // Auto-clear error after 5 seconds
      setTimeout(() => setGenerateError(null), 5000);
    } finally {
      setGenerating(false);
    }
  };

  const currentTime = new Date().toLocaleTimeString('en-US', {
    hour: '2-digit', minute: '2-digit',
  });

  if (!doctor && !patientUser) {
  return <Login onDoctorLogin={handleLogin} onPatientLogin={handlePatientLogin} />;
}

  return (
    <>

      {/* Navbar */}
      <nav className="navbar">
        <div className="navbar-brand">
          <div className="navbar-logo">
            <Activity size={18} />
          </div>
          <div>
            <div className="navbar-title">NeuroX CDS</div>
            <div className="navbar-subtitle">Clinical Decision Support System</div>
          </div>
        </div>
        <div className="navbar-right">
          {doctor && (
            <button
              className={`navbar-ai-btn ${aiConnected ? 'connected' : ''}`}
              onClick={() => setShowAiSettings(true)}
              title={aiConnected ? 'AI key connected — manage' : 'Connect your own AI key'}
            >
              <KeyRound size={13} />
              {aiConnected ? 'AI Key Connected' : 'Connect AI Key'}
            </button>
          )}
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Shield size={13} style={{ color: '#4FC3F7' }} />
            ZK Privacy Layer Active
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Clock size={13} />
            {currentTime}
          </span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
  <span>{doctor ? doctor.name : `${patientUser.name} (Patient)`}</span>
  <button
    onClick={handleLogout}
style={{
  border: '1px solid #ef9a9a',
  background: '#c62828',
  color: '#ffffff',
  borderRadius: '6px',
  padding: '5px 10px',
  fontSize: '12px',
  cursor: 'pointer',
}}
  >
    Logout
  </button>
</div>
        </div>
      </nav>

      {/* Loading overlay */}
      {loading && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(255,255,255,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 300 }}>
          <div style={{ textAlign: 'center' }}>
            <div className="loading-spinner" style={{ width: '32px', height: '32px', marginBottom: '12px' }} />
            <div style={{ color: '#1B5E96', fontWeight: 500 }}>Loading patient record...</div>
          </div>
        </div>
      )}

      {/* Main Content */}
      {view === 'portal' && patient && (
        <>
          <div className="portal-banner">
            <Shield size={14} />
            Patient Portal — viewing your own medical record (read-only)
          </div>
          <PatientHeader patient={patient} />
          <div className="dashboard" style={{ gridTemplateColumns: '1fr', width: '100%', maxWidth: '960px', margin: '0 auto' }}>
            <MedicalHistory patient={patient} zkProofs={zkProofs} />
          </div>
        </>
      )}

      {view === 'select' && (
        <PatientSelector onSelectPatient={handleSelectPatient} />
      )}

      {view === 'dashboard' && patient && (
        <>
          <PatientHeader patient={patient} onBack={handleBack} />
          <div className="dashboard">
            {/* Left: Medical History */}
            <MedicalHistory patient={patient} zkProofs={zkProofs} />

            {/* Center: Prescription Entry */}
            <PrescriptionEntry
              patient={patient}
              onAlertsUpdate={handleAlertsUpdate}
              onGenerateRx={handleGenerateRx}
              generating={generating}
              generateError={generateError}
            />

            {/* Right: Safety Alerts */}
            <SafetyAlerts
              alerts={alerts}
              analysis={analysis}
              patient={patient}
              onConnectAi={() => setShowAiSettings(true)}
            />
          </div>
        </>
      )}

      {/* Prescription Output Modal */}
      {rxOutput && (
        <PrescriptionOutput
          prescription={rxOutput.prescription}
          analysis={rxOutput.analysis}
          onClose={() => setRxOutput(null)}
        />
      )}

      {/* AI Settings Modal (bring your own key) */}
      <AiSettings
        open={showAiSettings}
        onClose={() => setShowAiSettings(false)}
        onConfigChange={(cfg) => setAiConnected(!!cfg)}
      />
    </>
  );
}
