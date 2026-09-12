/**
 * API Client for NeuroX Clinical Decision Support System
 */
const API_BASE = '/api';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options.headers },
  };
  const response = await fetch(url, config);
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

// Patient endpoints
export const getPatients = () => request('/patients');
export const getPatient = (id) => request(`/patients/${id}`);
export const getPatientHistory = (id) => request(`/patients/${id}/history`);
export const searchPatients = (q) => request(`/patients/search?q=${encodeURIComponent(q)}`);
export const createPatient = (data) => request('/patients', { method: 'POST', body: JSON.stringify(data) });

// Drug endpoints
export const searchDrugs = (q) => request(`/drugs/search?q=${encodeURIComponent(q)}`);
export const getDrug = (id) => request(`/drugs/${id}`);
export const getDosageRange = (drug, age, weight) =>
  request(`/drugs/dosage-range?drug=${encodeURIComponent(drug)}&age=${age}&weight=${weight}`);

// Prescription analysis
export const analyzeDrug = (data) =>
  request('/prescriptions/analyze', { method: 'POST', body: JSON.stringify(data) });

export const analyzeFullPrescription = (data) =>
  request('/prescriptions/analyze-full', { method: 'POST', body: JSON.stringify(data) });

export const generatePrescription = (data) =>
  request('/prescriptions/generate', { method: 'POST', body: JSON.stringify(data) });

// ZK endpoints
export const getZKProofs = (patientId) => request(`/zk/proofs/${patientId}`);
export const verifyZKProof = (proofData) =>
  request('/zk/verify', { method: 'POST', body: JSON.stringify(proofData) });

// Doctor authentication
export const loginDoctor = (credentials) =>
  request('/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  });

// Patient portal authentication
export const loginPatient = (credentials) =>
  request('/auth/patient-login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  });