import React, { useState, useEffect } from 'react';
import { Search, Users, AlertTriangle, Heart, Weight, Droplets, Plus, X } from 'lucide-react';
import { getPatients, createPatient } from '../services/api';

export default function PatientSelector({ onSelectPatient }) {
  const [patients, setPatients] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newPatient, setNewPatient] = useState({
  name: { given: '', family: '', full: '' },
  gender: 'male',
  age: '',
  weight: '',
  height: 170,
  bloodType: 'O+',
  contact: {
    phone: '',
    email: '',
    emergencyContact: {
      name: '',
      relation: '',
      phone: ''
    }
  },
  allergies: []
});

const [newAllergy, setNewAllergy] = useState({
  substance: '',
  reaction: '',
  severity: 'moderate'
});

  const loadPatients = () => {
    setLoading(true);
    getPatients()
      .then(setPatients)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadPatients();
  }, []);
  const handleAddAllergy = () => {
  if (!newAllergy.substance.trim() || !newAllergy.reaction.trim()) {
    return;
  }

  const allergy = {
    id: `ALG-${Date.now()}`,
    substance: newAllergy.substance.trim(),
    drugClass: null,
    reaction: newAllergy.reaction.trim(),
    severity: newAllergy.severity,
    status: 'active',
    documentedDate: new Date().toISOString().split('T')[0],
    documentedBy: 'Dr. Demo Physician',
    notes: ''
  };

  setNewPatient(prev => ({
    ...prev,
    allergies: [...prev.allergies, allergy]
  }));

  setNewAllergy({
    substance: '',
    reaction: '',
    severity: 'moderate'
  });
};

const handleRemoveAllergy = (allergyId) => {
  setNewPatient(prev => ({
    ...prev,
    allergies: prev.allergies.filter(a => a.id !== allergyId)
  }));
};
  const handleAddPatient = async (e) => {
    e.preventDefault();
    try {
      const patientToCreate = {
        ...newPatient,
        age: parseInt(newPatient.age) || 0,
        weight: parseFloat(newPatient.weight) || 0,
        name: {
          ...newPatient.name,
          full: `${newPatient.name.given} ${newPatient.name.family}`.trim()
        }
      };
      await createPatient(patientToCreate);
      setShowAddModal(false);
      loadPatients(); // Reload the list
    } catch (err) {
      console.error("Failed to add patient", err);
    }
  };

  const filtered = searchQuery
    ? patients.filter(p =>
        p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (p.mrn && p.mrn.toLowerCase().includes(searchQuery.toLowerCase()))
      )
    : patients;

  return (
    <div className="patient-selector">
      <div className="selector-header">
        <h1>Patient Selection</h1>
        <p>Select a patient to begin the prescription workflow</p>
      </div>

      <div style={{ display: 'flex', gap: '16px', maxWidth: '600px', margin: '0 auto 32px' }}>
        <div className="patient-search" style={{ margin: 0, flex: 1 }}>
          <Search size={18} className="search-icon" />
          <input
            id="patient-search-input"
            type="text"
            placeholder="Search by name or MRN..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
          />
        </div>
        <button 
          className="btn btn-primary"
          onClick={() => setShowAddModal(true)}
          style={{ padding: '0 20px' }}
        >
          <Plus size={16} style={{ marginRight: '8px' }} /> Add Patient
        </button>
      </div>

      {loading ? (
        <div className="text-center mt-4">
          <div className="loading-spinner" />
        </div>
      ) : (
        <div className="patient-grid">
          {filtered.map(patient => (
            <div
              key={patient.id}
              id={`patient-card-${patient.id}`}
              className="patient-card"
              onClick={() => onSelectPatient(patient.id)}
            >
              <div className="card-header">
                <div className="card-avatar">
                  {patient.name.split(' ').map(n => n[0]).join('')}
                </div>
                <div>
                  <div className="card-name">{patient.name}</div>
                  <div className="card-mrn">{patient.mrn}</div>
                </div>
              </div>

              <div className="card-details">
                <div>
                  <div className="card-detail-label">Age</div>
                  <div>{patient.age} yrs</div>
                </div>
                <div>
                  <div className="card-detail-label">Weight</div>
                  <div>{patient.weight} kg</div>
                </div>
                <div>
                  <div className="card-detail-label">Gender</div>
                  <div style={{ textTransform: 'capitalize' }}>{patient.gender}</div>
                </div>
                <div>
                  <div className="card-detail-label">Blood Type</div>
                  <div>{patient.bloodType}</div>
                </div>
              </div>

              <div className="card-badges">
                {patient.criticalAllergies?.length > 0 && patient.criticalAllergies.map(a => (
                  <span key={a} className="card-badge allergy">
                    <AlertTriangle size={10} /> {a}
                  </span>
                ))}
                {patient.activeMedsCount > 0 && (
                  <span className="card-badge meds">
                    {patient.activeMedsCount} Active Meds
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Patient Modal */}
      {showAddModal && (
        <div className="rx-output-overlay" onClick={(e) => e.target === e.currentTarget && setShowAddModal(false)}>
          <div className="rx-output-container" style={{ width: '500px', padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h2 style={{ fontSize: '1.25rem', color: '#0D3B66' }}>Add New Patient</h2>
              <button className="btn btn-outline" style={{ padding: '4px' }} onClick={() => setShowAddModal(false)}>
                <X size={16} />
              </button>
            </div>
            
            <form onSubmit={handleAddPatient} className="rx-form">
              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">First Name</label>
                  <input className="form-input" required value={newPatient.name.given} onChange={e => setNewPatient({...newPatient, name: {...newPatient.name, given: e.target.value}})} />
                </div>
                <div className="form-group">
                  <label className="form-label">Last Name</label>
                  <input className="form-input" required value={newPatient.name.family} onChange={e => setNewPatient({...newPatient, name: {...newPatient.name, family: e.target.value}})} />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">Age</label>
                  <input className="form-input" type="number" required value={newPatient.age} onChange={e => setNewPatient({...newPatient, age: e.target.value})} />
                </div>
                <div className="form-group">
                  <label className="form-label">Weight (kg)</label>
                  <input className="form-input" type="number" step="0.1" required value={newPatient.weight} onChange={e => setNewPatient({...newPatient, weight: e.target.value})} />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">Gender</label>
                  <select className="form-select" value={newPatient.gender} onChange={e => setNewPatient({...newPatient, gender: e.target.value})}>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Blood Type</label>
                  <select className="form-select" value={newPatient.bloodType} onChange={e => setNewPatient({...newPatient, bloodType: e.target.value})}>
                    <option value="A+">A+</option>
                    <option value="A-">A-</option>
                    <option value="B+">B+</option>
                    <option value="B-">B-</option>
                    <option value="O+">O+</option>
                    <option value="O-">O-</option>
                    <option value="AB+">AB+</option>
                    <option value="AB-">AB-</option>
                  </select>
                </div>
              </div>
              {/* Allergies */}
<div className="form-group" style={{ marginTop: '8px' }}>
  <label className="form-label">Allergies</label>

  {newPatient.allergies.map(allergy => (
    <div
      key={allergy.id}
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '10px',
        padding: '10px',
        marginBottom: '8px',
        border: '1px solid #e5e7eb',
        borderRadius: '8px',
        background: '#fafafa'
      }}
    >
      <div>
        <strong>{allergy.substance}</strong>
        <div style={{ fontSize: '0.85rem', color: '#666' }}>
          {allergy.reaction} · {allergy.severity}
        </div>
      </div>

      <button
        type="button"
        className="btn btn-outline"
        style={{ padding: '4px 8px' }}
        onClick={() => handleRemoveAllergy(allergy.id)}
      >
        <X size={14} />
      </button>
    </div>
  ))}

  <div className="form-row">
    <div className="form-group">
      <input
        className="form-input"
        placeholder="Substance (e.g. Penicillin)"
        value={newAllergy.substance}
        onChange={e =>
          setNewAllergy({
            ...newAllergy,
            substance: e.target.value
          })
        }
      />
    </div>

    <div className="form-group">
      <input
        className="form-input"
        placeholder="Reaction (e.g. Anaphylaxis)"
        value={newAllergy.reaction}
        onChange={e =>
          setNewAllergy({
            ...newAllergy,
            reaction: e.target.value
          })
        }
      />
    </div>
  </div>

  <div className="form-row">
    <div className="form-group">
      <select
        className="form-select"
        value={newAllergy.severity}
        onChange={e =>
          setNewAllergy({
            ...newAllergy,
            severity: e.target.value
          })
        }
      >
        <option value="mild">Mild</option>
        <option value="moderate">Moderate</option>
        <option value="severe">Severe</option>
      </select>
    </div>

    <div className="form-group">
      <button
        type="button"
        className="btn btn-outline"
        style={{ width: '100%' }}
        onClick={handleAddAllergy}
      >
        <Plus size={14} style={{ marginRight: '6px' }} />
        Add Allergy
      </button>
    </div>
  </div>
</div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '16px' }}>
                <button type="button" className="btn btn-outline" onClick={() => setShowAddModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Save Patient</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
