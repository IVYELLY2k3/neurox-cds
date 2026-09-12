# Publishing NeuroX — Step by Step

This project deploys as **one service**: the FastAPI backend serves both the API
and the prebuilt frontend (`backend/static`). No API keys, no environment
variables, no database — it works immediately for anyone who opens the link.

---

## What's already done for you

- The frontend is built and copied into `backend/static`, so a single backend
  service serves the whole site.
- `render.yaml` (Render blueprint) and `Dockerfile` are included.
- **Bring-your-own-key AI assistant**: each visitor can connect their own AI
  key (Z.AI / OpenAI / Groq / OpenRouter) via the **Connect AI Key** button in
  the navbar. The key is stored only in that person's browser and forwarded
  per-request to their chosen provider — it is never saved on the server, and
  you never pay for anyone else's AI usage.
- All core safety features (allergies, interactions, dosage, LASA, ZK proofs,
  prescriptions) run on the server and need **no key at all**.

---

## Option A — Render (recommended, free, ~5 minutes)

1. **Push the project to GitHub**
   1. Go to https://github.com/new
   2. Name it (e.g. `neurox-cds`), keep it **Public** (required for the free Render plan), click **Create repository**.
   3. In this project folder, run:
      ```bash
      git init
      git add .
      git commit -m "NeuroX CDS — ready to publish"
      git branch -M main
      git remote add origin https://github.com/<your-username>/neurox-cds.git
      git push -u origin main
      ```
      (GitHub will ask you to sign in once.)

2. **Deploy on Render**
   1. Go to https://render.com and sign up (free).
   2. Click **New +** → **Blueprint**, pick your `neurox-cds` repo — Render reads
      the included `render.yaml` automatically.
   3. Click **Apply**. Wait ~3–5 minutes for the build.

3. **Your public link** will look like:
   `https://neurox-cds.onrender.com` — share it with anyone. Works on mobile
   and desktop. (Free services sleep after ~15 min of inactivity; the first
   load after sleeping takes ~30–60 seconds.)

---

## Option B — Hugging Face Spaces (free, Docker)

1. Go to https://huggingface.co/new-space
2. Space name: `neurox-cds`, SDK: **Docker**, visibility: **Public** → Create.
3. Upload this whole folder as a repository (Files tab → Add file → Upload
   files), making sure `Dockerfile` is at the root.
4. The site goes live at `https://<your-username>-neurox-cds.hf.space`.

> Hugging Face Spaces use port 7860 by default — the included Dockerfile
> already handles this.

## Option C — Railway / Koyeb / Fly.io

All of them can deploy this repo directly (Railway/Koyeb: pick the Dockerfile
or a Python service running `uvicorn main:app --host 0.0.0.0 --port $PORT`
from the `backend` directory). Free tiers exist on each.

---

## After you change the frontend

Rebuild and re-deploy:

```bash
./build-site.sh        # rebuilds frontend, copies to backend/static
git add . && git commit -m "Update site" && git push
```

Render auto-deploys on every push.

---

## How visitors use the AI features

1. Open the site → click **Connect AI Key** in the top navbar.
2. Pick a provider (Z.AI, OpenAI, Groq, or OpenRouter) — the dialog links
   straight to each provider's key page (Groq and Z.AI have free keys).
3. Paste the key → **Connect**. The key stays in *their* browser only.
4. Safety alerts now show an **AI Explain** button with clinical explanations.

Everything else on the site works without any key.
