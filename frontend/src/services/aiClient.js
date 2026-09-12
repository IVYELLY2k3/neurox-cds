/**
 * AI Assistant client — Bring Your Own Key.
 * The user's provider + API key + model are stored only in their browser
 * (localStorage) and sent per-request to our backend, which forwards the
 * call to the chosen AI provider without ever storing the key.
 */

const LS_KEY = 'neurox_ai_config';

export const AI_PROVIDER_OPTIONS = [
  { value: 'zai', label: 'Z.AI — GLM (glm-4-flash)', defaultModel: 'glm-4-flash' },
  { value: 'openai', label: 'OpenAI (gpt-4o-mini)', defaultModel: 'gpt-4o-mini' },
  { value: 'groq', label: 'Groq — Llama (free tier)', defaultModel: 'llama-3.3-70b-versatile' },
  { value: 'openrouter', label: 'OpenRouter (many models)', defaultModel: 'openrouter/auto' },
];

export function getAiConfig() {
  try {
    const raw = localStorage.getItem(LS_KEY);
    const cfg = raw ? JSON.parse(raw) : null;
    if (!cfg || !cfg.apiKey) return null;
    return cfg;
  } catch {
    return null;
  }
}

export function saveAiConfig(config) {
  localStorage.setItem(LS_KEY, JSON.stringify(config));
}

export function clearAiConfig() {
  localStorage.removeItem(LS_KEY);
}

/**
 * Call the AI assistant. `messages` is an OpenAI-style chat array.
 * Throws Error with .code = 'NO_KEY' when no key is connected.
 */
export async function callAi(messages) {
  const cfg = getAiConfig();
  if (!cfg) {
    const err = new Error('No AI key connected');
    err.code = 'NO_KEY';
    throw err;
  }

  const res = await fetch('/api/ai/assistant', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      provider: cfg.provider || 'zai',
      apiKey: cfg.apiKey,
      model: cfg.model || '',
      messages,
    }),
  });

  const data = await res.json().catch(() => ({ detail: 'AI request failed' }));
  if (!res.ok) {
    const err = new Error(data.detail || `AI error (${res.status})`);
    err.code = res.status;
    throw err;
  }
  return data.content;
}
