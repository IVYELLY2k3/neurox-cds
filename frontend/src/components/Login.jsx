import React, { useState } from 'react';
import { Shield, Stethoscope, User, Lock } from 'lucide-react';
import DoctorLogin from './DoctorLogin';
import PatientLogin from './PatientLogin';

const ROLES = [
  { key: 'doctor', label: 'Doctor', icon: Stethoscope },
  { key: 'patient', label: 'Patient', icon: User },
];

export default function Login({ onDoctorLogin, onPatientLogin }) {
  const [role, setRole] = useState('doctor');

  return (
    <div className="login-page">

      {/* ── Left branding panel (desktop) ── */}
      <div className="login-brand-panel">
        {/* Animated neural-network background nodes */}
        <div className="login-brand-bg">
          <svg className="login-neural-svg" viewBox="0 0 600 800" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            {/* Connecting lines */}
            <line x1="80" y1="120" x2="220" y2="200" stroke="rgba(22,198,217,0.08)" strokeWidth="1"/>
            <line x1="220" y1="200" x2="150" y2="340" stroke="rgba(22,198,217,0.06)" strokeWidth="1"/>
            <line x1="150" y1="340" x2="350" y2="380" stroke="rgba(22,198,217,0.07)" strokeWidth="1"/>
            <line x1="350" y1="380" x2="480" y2="280" stroke="rgba(22,198,217,0.05)" strokeWidth="1"/>
            <line x1="480" y1="280" x2="520" y2="450" stroke="rgba(22,198,217,0.06)" strokeWidth="1"/>
            <line x1="520" y1="450" x2="350" y2="550" stroke="rgba(22,198,217,0.07)" strokeWidth="1"/>
            <line x1="350" y1="550" x2="120" y2="600" stroke="rgba(22,198,217,0.05)" strokeWidth="1"/>
            <line x1="120" y1="600" x2="250" y2="720" stroke="rgba(22,198,217,0.06)" strokeWidth="1"/>
            <line x1="220" y1="200" x2="480" y2="280" stroke="rgba(22,198,217,0.04)" strokeWidth="1"/>
            <line x1="150" y1="340" x2="520" y2="450" stroke="rgba(22,198,217,0.04)" strokeWidth="1"/>
            <line x1="80" y1="120" x2="350" y2="380" stroke="rgba(22,198,217,0.03)" strokeWidth="1"/>
            {/* Nodes */}
            <circle cx="80"  cy="120" r="3" fill="rgba(22,198,217,0.18)"/>
            <circle cx="220" cy="200" r="4" fill="rgba(22,198,217,0.22)"/>
            <circle cx="150" cy="340" r="3" fill="rgba(22,198,217,0.15)"/>
            <circle cx="350" cy="380" r="5" fill="rgba(22,198,217,0.20)"/>
            <circle cx="480" cy="280" r="3" fill="rgba(22,198,217,0.16)"/>
            <circle cx="520" cy="450" r="4" fill="rgba(22,198,217,0.18)"/>
            <circle cx="350" cy="550" r="3" fill="rgba(22,198,217,0.14)"/>
            <circle cx="120" cy="600" r="4" fill="rgba(22,198,217,0.17)"/>
            <circle cx="250" cy="720" r="3" fill="rgba(22,198,217,0.12)"/>
            {/* Pulsing accent nodes */}
            <circle className="login-node-pulse" cx="350" cy="380" r="8" fill="rgba(22,198,217,0.08)"/>
            <circle className="login-node-pulse login-node-pulse-delay" cx="220" cy="200" r="6" fill="rgba(22,198,217,0.06)"/>
          </svg>
        </div>

        <div className="login-brand-content">
          <div className="login-brand-logo">
            <img src="/neurox-logo.jpeg" alt="NeuroX Logo" />
          </div>
          <h1 className="login-brand-title">NeuroX CDS</h1>
          <p className="login-brand-desc">Clinical Decision Support System</p>
          <div className="login-brand-divider"></div>
          <p className="login-brand-tagline">Smarter alerts. Safer medicine.</p>

          <div className="login-brand-features">
            <div className="login-brand-feature">
              <div className="login-brand-feature-dot"></div>
              <span>AI-Powered Safety Checks</span>
            </div>
            <div className="login-brand-feature">
              <div className="login-brand-feature-dot"></div>
              <span>Unified Patient Records</span>
            </div>
            <div className="login-brand-feature">
              <div className="login-brand-feature-dot"></div>
              <span>Zero-Knowledge Privacy</span>
            </div>
          </div>
        </div>
      </div>

      {/* ── Mobile logo (shown only on small screens) ── */}
      <div className="login-mobile-logo">
        <img src="/neurox-logo.jpeg" alt="NeuroX Logo" />
      </div>

      {/* ── Right login form panel ── */}
      <div className="login-form-panel">
        <div className="login-card">

          <p className="login-welcome">Welcome back</p>
          <h2 className="login-heading">Sign in to NeuroX CDS</h2>
          <p className="login-supporting">
            Access your clinical decision support dashboard.
          </p>

          {/* Segmented role selector */}
          <div className="login-tabs" role="tablist" aria-label="Login role">
            {ROLES.map(({ key, label, icon: Icon }) => (
              <button
                key={key}
                type="button"
                role="tab"
                aria-selected={role === key}
                className={`login-tab ${role === key ? 'active' : ''}`}
                onClick={() => setRole(key)}
              >
                <Icon size={15} strokeWidth={2.2} />
                {label}
              </button>
            ))}
          </div>

          {/* Login form */}
          {role === 'doctor'
            ? <DoctorLogin onLogin={onDoctorLogin} />
            : <PatientLogin onLogin={onPatientLogin} />}

          {/* Security indicator */}
          <div className="login-security">
            <Lock size={13} strokeWidth={2.5} />
            Secure &amp; encrypted access
          </div>

          {/* Footer */}
          <div className="login-footer">
            <span>© 2026 NeuroX CDS</span>
            <span className="login-footer-sep">·</span>
            <span>Clinical Decision Support System</span>
          </div>
        </div>
      </div>

    </div>
  );
}
