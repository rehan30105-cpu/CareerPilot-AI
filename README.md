# CareerPilot AI

AI-powered career intelligence platform — resume analysis, semantic job matching, career agent, and roadmap generation.

## Monorepo structure

```
apps/api/   # FastAPI + Python 3.12 backend
apps/web/   # React + TypeScript + Vite frontend
```

## Getting started

### Backend

```powershell
cd apps/api
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Configure `.env` from `.env.example`, then:

```powershell
uvicorn app.main:app --reload
```

Health: `http://localhost:8000/health`

### Frontend

```powershell
cd apps/web
npm install
npm run dev
```

Frontend proxies `/api` to `http://localhost:8000`.

### Database

PostgreSQL via Docker Compose:

```powershell
docker-compose up -d postgres chromadb
```

### Deployment

Frontend: Vercel | Backend: Render | Database: Managed PostgreSQL
