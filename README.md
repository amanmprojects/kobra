# Kobra

Kobra is a hackathon-grade cyber threat defense platform with three demo flows:

- URL scanning with lexical analysis, XGBoost-style scoring, SHAP-like explanations, and external verdict sources
- Prompt injection detection through a LiteLLM proxy with local classification fallbacks
- Gmail inbox scanning with phishing scoring and explainable results

## Stack

- Frontend: Next.js 14, TypeScript, Tailwind CSS
- Backend: FastAPI, Pydantic
- LLM gateway: LiteLLM proxy
- Deployment: Docker / Cloud Run compatible

## Local Setup

### Backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```

### LiteLLM

```bash
litellm --config litellm/config.yaml --port 4000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Environment

Copy these examples and fill in the values:

- `backend/.env.example` -> `backend/.env`
- `frontend/.env.example` -> `frontend/.env.local`

## Deployment

The included `Dockerfile` and `cloudbuild.yaml` target Google Cloud Run. Any Docker-capable host can run the backend image.

