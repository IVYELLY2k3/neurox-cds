import React, { useState } from 'react';
import { X, KeyRound, ShieldCheck, ExternalLink } from 'lucide-react';
import {
  AI_PROVIDER_OPTIONS,
  getAiConfig,
  saveAiConfig,
  clearAiConfig,
} from '../services/aiClient';

const PROVIDER_LINKS = {
  zai: 'https://z.ai/manage-apikey/apikey-list',
  openai: 'https://platform.openai.com/api-keys',
  groq: 'https://console.groq.com/keys',
  openrouter: 'https://openrouter.ai/keys',
};

export default function AiSettings({ open, onClose, onConfigChange }) {
  const existing = getAiConfig();
  const [provider, setProvider] = useState(existing?.provider || 'zai');
  const [apiKey, setApiKey] = useState('');
  const [model, setModel] = useState(existing?.model || '');
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);

  if (!open) return null;

  const providerDefaults = AI_PROVIDER_OPTIONS.find((p) => p.value === provider);

  const handleProviderChange = (value) => {
    setProvider(value);
    setModel('');
  };

  const handleSave = () => {
    const key = apiKey.trim();
    if (!key && !existing) {
      setError('Please paste your API key first.');
      return;
    }
    if (key && key.length < 10) {
      setError('That key looks too short — please check it.');
      return;
    }
    setError(null);
    setSaving(true);
    try {
      const config = {
        provider,
        apiKey: key || existing.apiKey,
        model: model.trim() || providerDefaults?.defaultModel || '',
      };
      saveAiConfig(config);
      onConfigChange?.(config);
      onClose();
    } catch (e) {
      setError('Could not save settings in this browser.');
    } finally {
      setSaving(false);
    }
  };

  const handleDisconnect = () => {
    clearAiConfig();
    onConfigChange?.(null);
    onClose();
  };

  return (
    <div className="ai-modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="ai-modal">
        <div className="ai-modal-header">
          <div className="ai-modal-title">
            <KeyRound size={16} /> AI Settings — Connect Your Own Key
          </div>
          <button className="ai-modal-close" onClick={onClose} aria-label="Close">
            <X size={16} />
          </button>
        </div>

        <div className="ai-modal-body">
          <div className="ai-privacy-note">
            <ShieldCheck size={14} />
            <span>
              Your key is stored <strong>only in your browser</strong> and sent only to the AI
              provider you choose. It is never saved on the NeuroX server.
            </span>
          </div>

          <label className="ai-field-label">AI Provider</label>
          <select className="ai-select" value={provider} onChange={(e) => handleProviderChange(e.target.value)}>
            {AI_PROVIDER_OPTIONS.map((p) => (
              <option key={p.value} value={p.value}>{p.label}</option>
            ))}
          </select>

          <label className="ai-field-label">
            API Key{' '}
            <a className="ai-key-link" href={PROVIDER_LINKS[provider]} target="_blank" rel="noreferrer">
              Get a key <ExternalLink size={10} style={{ verticalAlign: '-1px' }} />
            </a>
          </label>
          <input
            className="ai-input"
            type="password"
            placeholder={existing ? '•••••••••• (saved — leave blank to keep)' : 'Paste your API key here'}
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            autoComplete="off"
          />

          <label className="ai-field-label">Model (optional)</label>
          <input
            className="ai-input"
            type="text"
            placeholder={`Default: ${providerDefaults?.defaultModel || 'provider default'}`}
            value={model}
            onChange={(e) => setModel(e.target.value)}
          />

          {error && <div className="ai-error">{error}</div>}

          <div className="ai-modal-actions">
            <button className="btn btn-outline" onClick={onClose}>Cancel</button>
            {existing && (
              <button className="btn btn-danger" onClick={handleDisconnect}>Disconnect Key</button>
            )}
            <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
              {existing ? 'Update' : 'Connect'}
            </button>
          </div>

          <p className="ai-footnote">
            Note: the core NeuroX safety checks (allergies, interactions, dosage, LASA, ZK proofs)
            run on the NeuroX server and <strong>do not require any AI key</strong>. The key only
            powers the optional “AI Explain” assistant.
          </p>
        </div>
      </div>
    </div>
  );
}
