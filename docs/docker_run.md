# Running with Docker

This document explains how to run the Pharmacy Assistant using Docker Compose.

## Prerequisites

- **Docker** (version 20.10 or later)
- **Docker Compose** (version 2.0 or later, or Docker Desktop which includes it)
- **OpenAI API key** with access to GPT-4 or GPT-4o

## Quick Start

### 1. Configure Environment Variables

Copy the example environment file and add your OpenAI API key:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and set your API key:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_MODEL=gpt-4o
```

### 2. Build the Containers

```bash
docker compose build
```

This builds:
- **backend**: Python 3.11 with FastAPI, uvicorn, and all dependencies
- **frontend**: Node.js for building, nginx for serving the React app

### 3. Start the Services

```bash
docker compose up
```

Or run in detached mode:

```bash
docker compose up -d
```

### 4. Access the Application

| Service | URL |
|---------|-----|
| Frontend (Chat UI) | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Health Check | http://localhost:8000/api/health |
| API Documentation | http://localhost:8000/docs |

## Testing the Application

1. Open http://localhost:3000 in your browser
2. The chat interface should load with a "🟢 Live" badge indicating it's connected to the backend
3. Try these test prompts:

**Stock Check:**
```
Do you have ibuprofen in stock?
```

**Medication Info:**
```
Tell me about aspirin
```

**Prescription Refill (multi-step):**
```
I want to refill my prescription. My phone is 050-1234567.
```

**Safety Refusal:**
```
Should I take aspirin for my headache?
```

**Hebrew:**
```
יש לכם אספירין במלאי?
```

## Managing the Containers

### View Logs

```bash
# All services
docker compose logs -f

# Backend only
docker compose logs -f backend

# Frontend only
docker compose logs -f frontend
```

### Stop Services

```bash
docker compose down
```

### Stop and Remove Volumes (reset database)

```bash
docker compose down -v
```

### Rebuild After Code Changes

```bash
docker compose build --no-cache
docker compose up
```

## Ports

| Port | Service | Description |
|------|---------|-------------|
| 3000 | Frontend | nginx serving React app |
| 8000 | Backend | FastAPI + uvicorn |

If you need different ports, edit `docker-compose.yml` and change the left side of the port mapping (e.g., `5173:80` instead of `3000:80`).

## Architecture in Docker

```
┌─────────────────────────────────────────────────────────┐
│  Docker Network (default bridge)                        │
│                                                         │
│  ┌─────────────────┐      ┌─────────────────────────┐  │
│  │    frontend     │      │        backend          │  │
│  │   (nginx:80)    │─────▶│   (uvicorn:8000)        │  │
│  │                 │ /api │                         │  │
│  │  React SPA      │      │  FastAPI + SQLite       │  │
│  └────────┬────────┘      │  + OpenAI integration   │  │
│           │               └─────────────────────────┘  │
└───────────┼─────────────────────────────────────────────┘
            │
     localhost:3000
            │
       ┌────┴────┐
       │ Browser │
       └─────────┘
```

The frontend nginx container proxies `/api/*` requests to the backend container. This means:
- The browser only talks to nginx on port 3000
- API requests are forwarded internally to the backend
- No CORS issues since everything appears to come from the same origin

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | Your OpenAI API key |
| `OPENAI_MODEL` | No | `gpt-4o` | Model to use |
| `DATABASE_URL` | No | `sqlite:///./pharmacy.db` | SQLite database path |
| `LOG_LEVEL` | No | `INFO` | Logging level |

### Passing API Key via Shell

Instead of editing `.env`, you can pass the key directly:

```bash
OPENAI_API_KEY=sk-your-key docker compose up
```

## Troubleshooting

### Container won't start

Check the logs:
```bash
docker compose logs backend
```

Common issues:
- Missing `OPENAI_API_KEY` - check `backend/.env`
- Port already in use - stop other services or change ports

### API returns errors

1. Check if backend is healthy:
   ```bash
   curl http://localhost:8000/api/health
   ```

2. Verify OpenAI key is set:
   ```bash
   docker compose exec backend env | grep OPENAI
   ```

### Frontend can't reach backend

1. Make sure backend is running and healthy
2. Check nginx logs:
   ```bash
   docker compose logs frontend
   ```

## Evaluation

After starting the containers, follow the evaluation plan in `docs/evaluation_plan.md` to test the three main flows:

- **Flow A**: Medication info + prescription requirement
- **Flow B**: Stock availability at branches
- **Flow C**: Prescription refill (multi-step)

Each flow has specific test scenarios in both English and Hebrew.

