# README.md Checklist

**For Arbel to manually write the final README.md.**

This is a structural guide only - fill in the actual content yourself.

---

## Sections to Include

### 1. Project Title & Overview
- [ ] Project name
- [ ] One-sentence description
- [ ] What problem it solves
- [ ] Target audience (pharmacy customers)

### 2. Features
- [ ] Real-time streaming responses
- [ ] Tool/function calling (6 tools)
- [ ] Bilingual (English + Hebrew)
- [ ] Safety guardrails (no medical advice)
- [ ] Multi-step conversation flows

### 3. Tech Stack
- [ ] Backend: Python, FastAPI, SQLite
- [ ] Frontend: React, TypeScript, Vite
- [ ] AI: OpenAI GPT-4o (vanilla API, no frameworks)
- [ ] Streaming: Server-Sent Events (SSE)
- [ ] Deployment: Docker, docker-compose

### 4. Screenshots
- [ ] Chat UI with streaming response
- [ ] Tool calls visible in UI
- [ ] Hebrew conversation example
- [ ] Safety refusal example

### 5. Quick Start (Docker)
- [ ] Prerequisites (Docker, API key)
- [ ] Reference: `docs/docker_run.md`
- [ ] Basic commands:
  - `docker compose build`
  - `docker compose up`

### 6. Development Setup
- [ ] Backend setup (venv, requirements, uvicorn)
- [ ] Frontend setup (npm install, npm run dev)
- [ ] Environment variables needed

### 7. Architecture
- [ ] High-level diagram or description
- [ ] Stateless design explanation
- [ ] SSE streaming flow
- [ ] Tool calling loop

### 8. Core Flows
- [ ] Flow A: Medication information
- [ ] Flow B: Stock availability
- [ ] Flow C: Prescription refill
- [ ] Example prompts for each

### 9. Safety & Policy
- [ ] What the assistant will NOT do
- [ ] Example of a refusal
- [ ] Redirect to healthcare professionals

### 10. Evaluation
- [ ] Reference: `docs/evaluation_plan.md`
- [ ] How to run tests
- [ ] Test scenarios covered

### 11. API Reference
- [ ] `POST /api/chat` (SSE streaming)
- [ ] `GET /api/health`
- [ ] SSE event types

### 12. Project Structure
- [ ] Key directories
- [ ] Important files

### 13. Known Limitations
- [ ] Synthetic data only
- [ ] No real pharmacy integration
- [ ] Simulated reservations/refills

### 14. License
- [ ] License type (if applicable)

---

## Tips

- Keep it concise but complete
- Use code blocks for commands
- Include at least 2-3 screenshots
- Test the quick start instructions on a fresh machine
- Reference docs/evaluation_plan.md for flow details
- Reference docs/docker_run.md for Docker instructions

