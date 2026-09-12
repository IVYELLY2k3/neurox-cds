import React, { useState, useEffect, useCallback } from 'react';
import { Plus, Trash2, Send, FileText, Activity, CheckCircle, AlertTriangle, Loader2 } from 'lucide-react';
import DrugAutocomplete from './DrugAutocomplete';
import { analyzeDrug, getDosageRange } from '../services/api';

export default function PrescriptionEntry({ patient, onAlertsUpdate, onGenerateRx, generating = false, generateError = null }) {
  const [diagnoses, setDiagnoses] = useState([]);
  const [diagnosisInput, setDiagnosisInput] = useState('');
  const [drugSearch, setDrugSearch] = useState('');
  const [selectedDrug, setSelectedDrug] = useState(null);
  const [dose, setDose] = useState('');
  const [frequency, setFrequency] = useState('');
  const [route, setRoute] = useState('oral');
  const [duration, setDuration] = useState('');
  const [instructions, setInstructions] = useState('');
  const [rxItems, setRxItems] = useState([]);
  const [safeRange, setSafeRange] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [allAlerts, setAllAlerts] = useState([]);

  // Fetch safe range when drug is selected
  useEffect(() => {
    if (selectedDrug && patient) {
      getDosageRange(selectedDrug.genericName, patient.age, patient.weight)
        .then(range => {
          if (range.found) setSafeRange(range);
          else setSafeRange(null);
        })
        .catch(() => setSafeRange(null));
    } else {
      setSafeRange(null);
    }
  }, [selectedDrug, patient]);

  // Auto-analyze when drug + dose are entered
  const runAnalysis = useCallback(async (drugName, doseVal, currentDiagnoses) => {
    if (!drugName || !doseVal || !patient) return;
    setAnalyzing(true);
    try {
      const result = await analyzeDrug({
        patientId: patient.id,
        drugName,
        dose: doseVal,
        diagnoses: currentDiagnoses || diagnoses,
      });
      // Merge alerts from this analysis with existing ones from rxItems
      const validDrugNames = rxItems.map(i => i.drugName);
      const existingAlerts = allAlerts.filter(a => validDrugNames.includes(a.drugName));
      const newAlerts = [...existingAlerts, ...(result.alerts || [])];
      setAllAlerts(newAlerts);
      onAlertsUpdate(newAlerts, result);
    } catch (err) {
      console.error('Analysis error:', err);
    } finally {
      setAnalyzing(false);
    }
  }, [patient, diagnoses, allAlerts, onAlertsUpdate]);

  // Debounced analysis on dose change
  useEffect(() => {
    if (!selectedDrug || !dose) return;
    const timer = setTimeout(() => {
      runAnalysis(selectedDrug.genericName, dose, diagnoses);
    }, 500);
    return () => clearTimeout(timer);
  }, [dose, selectedDrug, diagnoses]);

  const handleDrugSelect = (drug) => {
    setSelectedDrug(drug);
    setDrugSearch(drug.genericName);
    // Trigger analysis if dose already entered
    if (dose) {
      runAnalysis(drug.genericName, dose, diagnoses);
    }
  };

  const handleSearchChange = (val) => {
    setDrugSearch(val);
    if (selectedDrug && val !== selectedDrug.genericName) {
      setSelectedDrug(null);
      const validDrugNames = rxItems.map(i => i.drugName);
      const filtered = allAlerts.filter(a => validDrugNames.includes(a.drugName));
      setAllAlerts(filtered);
      onAlertsUpdate(filtered, null);
    }
  };

  // Re-analyze all existing rx items when diagnoses change
  const reAnalyzeAllItems = useCallback(async (newDiagnoses) => {
    if (!patient || rxItems.length === 0) return;
    let combinedAlerts = [];
    for (const item of rxItems) {
      try {
        const result = await analyzeDrug({
          patientId: patient.id,
          drugName: item.drugName,
          dose: item.dose,
          diagnoses: newDiagnoses,
        });
        if (result.alerts) {
          combinedAlerts = [...combinedAlerts, ...result.alerts];
        }
      } catch (err) {
        console.error('Re-analysis error for', item.drugName, err);
      }
    }
    // Deduplicate by alert id
    const seen = new Set();
    const unique = combinedAlerts.filter(a => {
      if (seen.has(a.id)) return false;
      seen.add(a.id);
      return true;
    });
    setAllAlerts(unique);
    onAlertsUpdate(unique, null);
  }, [patient, rxItems, onAlertsUpdate]);

  const handleAddDiagnosis = (e) => {
    e.preventDefault();
    if (diagnosisInput.trim() && !diagnoses.includes(diagnosisInput.trim())) {
      const newDiagnoses = [...diagnoses, diagnosisInput.trim()];
      setDiagnoses(newDiagnoses);
      setDiagnosisInput('');
      // Trigger analysis for currently selected drug
      if (selectedDrug && dose) {
        runAnalysis(selectedDrug.genericName, dose, newDiagnoses);
      }
      // Re-analyze all existing rx items with updated diagnoses
      reAnalyzeAllItems(newDiagnoses);
    }
  };

  const handleRemoveDiagnosis = (diagToRemove) => {
    const newDiagnoses = diagnoses.filter(d => d !== diagToRemove);
    setDiagnoses(newDiagnoses);
    if (selectedDrug && dose) {
      runAnalysis(selectedDrug.genericName, dose, newDiagnoses);
    }
    // Re-analyze all existing rx items with updated diagnoses
    reAnalyzeAllItems(newDiagnoses);
  };

  const handleAddItem = () => {
    if (!selectedDrug || !dose || !frequency) return;

    const newItem = {
      id: Date.now().toString(),
      drugId: selectedDrug.id,
      drugName: selectedDrug.genericName,
      genericName: selectedDrug.genericName,
      brandName: selectedDrug.brandNames?.[0] || '',
      dose,
      frequency,
      route,
      duration,
      instructions,
    };

    setRxItems(prev => [...prev, newItem]);

    // Reset form for next item
    setDrugSearch('');
    setSelectedDrug(null);
    setDose('');
    setFrequency('');
    setRoute('oral');
    setDuration('');
    setInstructions('');
    setSafeRange(null);
  };

  const handleRemoveItem = (id) => {
    const item = rxItems.find(i => i.id === id);
    setRxItems(prev => prev.filter(i => i.id !== id));
    // Remove alerts for this drug
    if (item) {
      const filtered = allAlerts.filter(a => a.drugName !== item.drugName);
      setAllAlerts(filtered);
      onAlertsUpdate(filtered, null);
    }
  };

  const handleGenerate = () => {
    if (rxItems.length === 0) return;
    onGenerateRx({
      patientId: patient.id,
      diagnoses: diagnoses,
      items: rxItems.map(({ id, ...rest }) => rest),
      prescriber: 'Dr. Demo Physician',
    });
  };

  const isDoseWarning = safeRange && dose && (() => {
    const val = parseFloat(dose);
    if (isNaN(val)) return false;
    const max = safeRange.perDoseMax || 0;
    return max > 0 && val > max;
  })();

  return (
    <div className="dashboard-panel" style={{ background: '#FFFFFF' }}>
      <div className="panel-header">
        <div className="panel-title">
          <FileText size={16} /> Prescription Entry
        </div>
      </div>

      <div className="panel-content">
        <div className="rx-form">
          {/* Diagnoses */}
          <div className="form-group">
            <label className="form-label">Diagnoses</label>
            <div className="diagnosis-chips" style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '8px' }}>
              {diagnoses.map(diag => (
                <span key={diag} className="badge badge-primary" style={{ display: 'flex', alignItems: 'center', gap: '4px', background: '#E3F2FD', color: '#1B5E96', padding: '4px 8px', borderRadius: '12px', fontSize: '0.75rem' }}>
                  {diag}
                  <button type="button" onClick={() => handleRemoveDiagnosis(diag)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#1B5E96', padding: 0, display: 'flex' }}>
                    <Trash2 size={12} />
                  </button>
                </span>
              ))}
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              <input
                id="diagnosis-input"
                className="form-input"
                type="text"
                placeholder="Enter diagnosis and press Add..."
                value={diagnosisInput}
                onChange={e => setDiagnosisInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' ? handleAddDiagnosis(e) : null}
                list="diagnosis-suggestions"
              />
              <button type="button" className="btn btn-secondary" onClick={handleAddDiagnosis}>Add</button>
            </div>
            <datalist id="diagnosis-suggestions">
              {patient?.diagnoses?.map(d => (
                <option key={d.id} value={d.description} />
              ))}
              <option value="Upper Respiratory Tract Infection" />
              <option value="Urinary Tract Infection" />
              <option value="Acute Bronchitis" />
              <option value="Migraine" />
              <option value="Musculoskeletal Pain" />
            </datalist>
          </div>

          {/* Drug Search */}
          <div className="form-group">
            <label className="form-label">Medication</label>
            <DrugAutocomplete
              value={drugSearch}
              onChange={handleSearchChange}
              onSelect={handleDrugSelect}
            />
          </div>

          {/* Safe Range Display */}
          {safeRange && (
            <div className={`safe-range-display ${isDoseWarning ? 'warning' : ''}`}>
              <Activity size={14} />
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.75rem' }}>
                  Safe Range ({safeRange.ageBracket}): {safeRange.displayRange}
                </div>
                <div style={{ fontSize: '0.68rem', opacity: 0.8 }}>
                  Max daily: {safeRange.maxDailyDose}mg • {safeRange.frequency}
                  {safeRange.notes && ` • ${safeRange.notes}`}
                </div>
              </div>
            </div>
          )}

          {/* Dose, Frequency, Route */}
          <div className="form-row-3">
            <div className="form-group">
              <label className="form-label">Dose</label>
              <input
                id="dose-input"
                className="form-input"
                type="text"
                placeholder="e.g. 500 mg"
                value={dose}
                onChange={e => setDose(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Frequency</label>
              <select
                id="frequency-select"
                className="form-select"
                value={frequency}
                onChange={e => setFrequency(e.target.value)}
              >
                <option value="">Select...</option>
                <option value="once daily">Once Daily</option>
                <option value="twice daily">Twice Daily</option>
                <option value="three times daily">Three Times Daily</option>
                <option value="four times daily">Four Times Daily</option>
                <option value="every 4 hours">Every 4 Hours</option>
                <option value="every 6 hours">Every 6 Hours</option>
                <option value="every 8 hours">Every 8 Hours</option>
                <option value="every 12 hours">Every 12 Hours</option>
                <option value="as needed">As Needed (PRN)</option>
                <option value="at bedtime">At Bedtime</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Route</label>
              <select
                id="route-select"
                className="form-select"
                value={route}
                onChange={e => setRoute(e.target.value)}
              >
                <option value="oral">Oral</option>
                <option value="IV">IV</option>
                <option value="IM">IM</option>
                <option value="topical">Topical</option>
                <option value="inhaler">Inhaler</option>
                <option value="sublingual">Sublingual</option>
                <option value="rectal">Rectal</option>
              </select>
            </div>
          </div>

          {/* Duration & Instructions */}
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Duration</label>
              <input
                id="duration-input"
                className="form-input"
                type="text"
                placeholder="e.g. 5 days"
                value={duration}
                onChange={e => setDuration(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Instructions</label>
              <input
                className="form-input"
                type="text"
                placeholder="e.g. After meals"
                value={instructions}
                onChange={e => setInstructions(e.target.value)}
              />
            </div>
          </div>

          {/* Add Button */}
          <button
            id="add-medication-btn"
            className="btn btn-primary btn-full"
            onClick={handleAddItem}
            disabled={!selectedDrug || !dose || !frequency}
          >
            <Plus size={14} /> Add to Prescription
          </button>

          {/* Analyzing indicator */}
          {analyzing && (
            <div style={{ textAlign: 'center', fontSize: '0.75rem', color: '#1B5E96', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}>
              <div className="loading-spinner" style={{ width: '14px', height: '14px' }} />
              Analyzing safety...
            </div>
          )}

          {/* Rx Items List */}
          {rxItems.length > 0 && (
            <div className="rx-items-list">
              <div style={{ fontSize: '0.7rem', fontWeight: 600, color: '#868E96', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '6px' }}>
                Prescription Items ({rxItems.length})
              </div>
              {rxItems.map(item => {
                // Check if this item has a diagnosis mismatch alert
                const hasMismatch = allAlerts.some(
                  a => a.id && a.id.startsWith('DMM-') && a.drugName === item.drugName
                );
                return (
                  <div key={item.id}>
                    <div className="rx-item" style={hasMismatch ? { borderColor: '#FFD54F', background: '#FFFDE7' } : {}}>
                      <div className="rx-item-info">
                        <span className="rx-item-drug">
                          {item.drugName}
                          {hasMismatch && (
                            <span style={{ marginLeft: '6px', fontSize: '0.65rem', color: '#E65100', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '2px' }}>
                              ⚠️ Diagnosis mismatch
                            </span>
                          )}
                        </span>
                        <span className="rx-item-details">
                          {item.dose} • {item.frequency} • {item.route}
                          {item.duration ? ` • ${item.duration}` : ''}
                        </span>
                      </div>
                      <button
                        className="rx-item-remove"
                        onClick={() => handleRemoveItem(item.id)}
                        title="Remove"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>
                );
              })}

              <div className="section-divider" />

              {generateError && (
                <div className="rx-diagnosis-warning" style={{ marginBottom: '8px', borderLeftColor: '#C62828', background: '#FFEBEE' }}>
                  <div className="rx-diagnosis-warning-icon">❌</div>
                  <div className="rx-diagnosis-warning-text">
                    <strong style={{ color: '#C62828' }}>Generation Failed</strong>
                    {generateError}
                  </div>
                </div>
              )}

              <button
                id="generate-rx-btn"
                className="btn btn-success btn-full btn-lg"
                onClick={handleGenerate}
                disabled={generating}
              >
                {generating ? (
                  <><div className="loading-spinner" style={{ width: '16px', height: '16px', borderColor: 'rgba(255,255,255,0.3)', borderTopColor: 'white' }} /> Generating...</>
                ) : (
                  <><CheckCircle size={16} /> Generate Prescription</>
                )}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
