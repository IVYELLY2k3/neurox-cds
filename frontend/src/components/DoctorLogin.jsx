import React, { useState } from 'react';
import { AlertCircle, Lock, Mail, Loader2 } from 'lucide-react';
import { loginDoctor } from '../services/api';

export default function DoctorLogin({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!email.trim() || !password) {
      setError('Please enter your email and password.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await loginDoctor({
        email: email.trim(),
        password,
      });

      if (result.success && result.doctor) {
        onLogin(result.doctor);
      } else {
        setError('Login failed. Please check your credentials.');
      }
    } catch (err) {
      setError(err.message || 'Unable to log in. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="login-form">

      <div className="login-field">
        <label htmlFor="doctor-email">Doctor Email</label>
        <div className="login-input-wrapper">
          <Mail size={16} strokeWidth={2} />
          <input
            id="doctor-email"
            type="email"
            placeholder="doctor@neurox.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="username"
          />
        </div>
      </div>

      <div className="login-field">
        <div className="login-label-row">
          <label htmlFor="doctor-password">Password</label>
          <button type="button" className="login-forgot" tabIndex={-1}>
            Forgot password?
          </button>
        </div>
        <div className="login-input-wrapper">
          <Lock size={16} strokeWidth={2} />
          <input
            id="doctor-password"
            type="password"
            placeholder="Enter your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
          />
        </div>
      </div>

      {error && (
        <div className="login-error" role="alert">
          <AlertCircle size={15} strokeWidth={2.2} />
          <span>{error}</span>
        </div>
      )}

      <button
        type="submit"
        className="login-button"
        disabled={loading}
      >
        {loading ? (
          <>
            <Loader2 size={16} className="login-spinner" />
            Signing in…
          </>
        ) : (
          'Sign In'
        )}
      </button>

    </form>
  );
}
