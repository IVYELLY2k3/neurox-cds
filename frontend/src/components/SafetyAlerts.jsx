import React, { useState } from 'react';
import { AlertTriangle, AlertOctagon, Info, ShieldAlert, ShieldCheck, Lightbulb, Sparkles, Loader2 } from 'lucide-react';
import ZKBadge from './ZKBadge';
import { callAi } from '../services/aiClient';

const SEVERITY_CONFIG = {
  critical: { icon: AlertOctagon, label: 'CRITICAL', className: 'critical' },
  high: { icon: ShieldAlert, label: 'HIGH', className: 'high' },
  moderate: { icon: Info, label: 'MODERATE', className: 'moderate' },
  informational: { icon: Lightbulb, label: 'INFO', className: 'informational' },
};

function buildPrompt(alert, patient) {
  const patientLine = patient
    ? `Patient: ${patient.age} years old, ${patient.gender}, ${patient.weight} kg.`
    : 'Patient details unavailable.';

  return [
    `You are a clinical decision support assistant for doctors. A prescription safety alert fired:`,
    ``,
    patientLine,
    `Alert severity: ${(alert.severity || '').toUpperCase()}`,
    `Alert type: ${alert.type || 'unknown'}`,
    `Alert title: ${alert.title}`,
    `Alert message: ${alert.message}`,
    alert.details ? `Details: ${alert.details}` : '',
    alert.evidence ? `Evidence: ${alert.evidence}` : '',
    alert.recommendation ? `System recommendation: ${alert.recommendation}` : '',
    ``,
    `Explain to the prescriber, in 4-6 short bullet points: (1) why this alert matters clinically, (2) the underlying mechanism, (3) practical safer alternatives or next steps. Be concise and factual. If information is insufficient, say so.`,
  ].filter(Boolean).join('\n');
}

function AlertCard({ alert, patient, onConnectAi }) {
  const [aiText, setAiText] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState(null);

  const config = SEVERITY_CONFIG[alert.severity] || SEVERITY_CONFIG.informational;
  const Icon = config.icon;

  const handleExplain = async () => {
    if (aiText) {
      setAiText(null); // toggle off
      return;
    }
    setAiLoading(true);
    setAiError(null);
    try {
      const content = await callAi([
        { role: 'system', content: 'You are a concise clinical pharmacology assistant for physicians.' },
        { role: 'user', content: buildPrompt(alert, patient) },
      ]);
      setAiText(content);
    } catch (err) {
      if (err.code === 'NO_KEY') {
        setAiError('Connect your own AI key to use this.');
        onConnectAi?.();
      } else {
        setAiError(err.message || 'AI request failed.');
      }
    } finally {
      setAiLoading(false);
    }
  };

  return (
    <div className={`alert-card ${config.className}`}>
      <div className="alert-card-header">
        <span className={`alert-severity-badge ${config.className}`}>
          <Icon size={10} /> {config.label}
        </span>
        <span className="alert-title">{alert.title}</span>
      </div>

      <div className="alert-message">{alert.message}</div>

      {alert.details && (
        <div className="alert-details">{alert.details}</div>
      )}

      {alert.evidence && (
        <div className="alert-details">📋 {alert.evidence}</div>
      )}

      {alert.recommendation && (
        <div className="alert-recommendation">
          💡 {alert.recommendation}
        </div>
      )}

      <div className="alert-footer">
        {alert.zkProof && (
          <ZKBadge
            proofId={alert.zkProof.proofId}
            statement={alert.zkProof.statement}
          />
        )}
        <span style={{ fontSize: '0.65rem', color: '#ADB5BD' }}>
          {alert.type?.replace('_', ' ').toUpperCase()}
        </span>
      </div>

      <div className="alert-ai-row">
        <button className="alert-ai-btn" onClick={handleExplain} disabled={aiLoading}>
          {aiLoading ? <Loader2 size={11} className="ai-spin" /> : <Sparkles size={11} />}
          {aiLoading ? 'Thinking…' : aiText ? 'Hide AI explanation' : 'AI Explain'}
        </button>
      </div>

      {aiError && <div className="alert-ai-error">{aiError}</div>}

      {aiText && (
        <div className="alert-ai-response">
          <div className="alert-ai-response-title">
            <Sparkles size={11} /> AI Clinical Explanation
          </div>
          <div className="alert-ai-response-body">{aiText}</div>
        </div>
      )}
    </div>
  );
}

export default function SafetyAlerts({ alerts = [], analysis = null, patient = null, onConnectAi }) {
  const [filterSeverity, setFilterSeverity] = React.useState(null);

  if (!alerts.length) {
    return (
      <div className="dashboard-panel">
        <div className="panel-header">
          <div className="panel-title">
            <ShieldCheck size={16} /> AI Safety Alerts
          </div>
        </div>
        <div className="alerts-empty">
          <div className="alerts-empty-icon">🛡️</div>
          <div>No alerts yet</div>
          <div style={{ fontSize: '0.7rem', marginTop: '4px' }}>
            Prescribe a medication to run safety analysis
          </div>
        </div>
      </div>
    );
  }

  const criticalCount = alerts.filter(a => a.severity === 'critical').length;
  const highCount = alerts.filter(a => a.severity === 'high').length;
  const moderateCount = alerts.filter(a => a.severity === 'moderate').length;
  const infoCount = alerts.filter(a => a.severity === 'informational').length;

  return (
    <div className="dashboard-panel">
      <div className="panel-header">
        <div className="panel-title">
          <ShieldCheck size={16} /> AI Safety Alerts
          <span style={{ fontSize: '0.7rem', color: '#868E96', fontWeight: '400', marginLeft: '4px' }}>
            ({alerts.length})
          </span>
        </div>
      </div>

      <div className="alert-summary">
        {criticalCount > 0 && (
          <span 
            className={`alert-count-badge critical ${filterSeverity === 'critical' ? 'active' : ''}`}
            onClick={() => setFilterSeverity(f => f === 'critical' ? null : 'critical')}
            style={{ cursor: 'pointer' }}
          >
            <AlertOctagon size={11} /> {criticalCount} Critical
          </span>
        )}
        {highCount > 0 && (
          <span 
            className={`alert-count-badge high ${filterSeverity === 'high' ? 'active' : ''}`}
            onClick={() => setFilterSeverity(f => f === 'high' ? null : 'high')}
            style={{ cursor: 'pointer' }}
          >
            <AlertTriangle size={11} /> {highCount} High
          </span>
        )}
        {moderateCount > 0 && (
          <span 
            className={`alert-count-badge moderate ${filterSeverity === 'moderate' ? 'active' : ''}`}
            onClick={() => setFilterSeverity(f => f === 'moderate' ? null : 'moderate')}
            style={{ cursor: 'pointer' }}
          >
            <Info size={11} /> {moderateCount} Moderate
          </span>
        )}
        {infoCount > 0 && (
          <span 
            className={`alert-count-badge info ${filterSeverity === 'informational' ? 'active' : ''}`}
            onClick={() => setFilterSeverity(f => f === 'informational' ? null : 'informational')}
            style={{ cursor: 'pointer' }}
          >
            <Lightbulb size={11} /> {infoCount} Info
          </span>
        )}
      </div>

      <div>
        {alerts
          .filter(alert => !filterSeverity || alert.severity === filterSeverity)
          .map((alert, idx) => (
            <AlertCard key={alert.id || idx} alert={alert} patient={patient} onConnectAi={onConnectAi} />
          ))}
      </div>
    </div>
  );
}
