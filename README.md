# AI Pharmacy Agent - Project

AI powered pharmacist assistant for a retail pharmacy chain project.
The agent able to serve customers through chat, using data from the pharmacy's internal data base ( once run you will see it under (backend/pharmacy.db) ).
The system uses function calling to interact with the pharmacy data base, suppoerts bilingual conversations ( English and Hebrew ), and enforces strict guidlines to avoid providing medical advices.

**See it in action:** Check out [conversation examples with screenshots](docs/SCREENSHOTS.md)

## Dev flow
First I read the guidlnes and understood them. Then I took the mission guidlines to `Chat GPT` and together we understood it better and decided on the `Tech Stack`.
Once I understood the mission and had the tech stack I created a plan for the mission and the architecture structure of the project in cursor with milestones as if cursor will do the whole plan in one prompt/chat it will start 
hallucinate. [You can see the initial plan with Cursor here](docs/pharmacy-assistant-plan-8f1e0cfa.plan.md) 
Once I had a draft plan and architecture structure I understood each milestone, devided it into sub tasks implement and test each milestone, [Can see the tests here](backend/tests).
I built automated unit tests along with manually tests of eadge cases and bug fixed based on them.

**Note:** Please use `gpt-4o mini` instead of `gpt-5` as each inference of `gpt-5` can be very slow.


## Tech Stack

**Backend:**
- Python 3.11
- FastAPI (REST API + SSE streaming)
- SQLite (synthetic pharmacy database)
- OpenAI GPT-4o (vanilla API, no frameworks)

**Frontend:**
- React + TypeScript
- Vite (development and build)
- nginx (production serving in Docker)

**Deployment:**
- Docker Compose
- Server-Sent Events for streaming

## Running the project on your local machine

[Docker run guide](docs/docker_run.md)

## Architecture

The system is built on a few key design principles:

### Stateless Design
The frontend sends the full conversation history with each request. No server-side session storage.

### Event-Driven Streaming
The backend emits structured SSE events that the frontend renders in real-time.
Such as `assistant_token` and `tool_call`.

### Tool-First Facts
Any information about medications, stock, or prescriptions must come from a tool call to the database. The system prompt instructs the LLM not to hallucinate or invent data.

### Architecture Diagram

```mermaid
graph LR
    User[User Browser] -->|HTTP Request| Frontend[React Frontend]
    Frontend -->|POST /api/chat SSE| Backend[FastAPI Backend]
    Backend -->|Chat Completion API| OpenAI[OpenAI GPT-5]
    Backend -->|Tool Calls| DB[(SQLite Database)]
    OpenAI -->|Function Calls| Backend
    Backend -->|SSE Events| Frontend
    Frontend -->|Real-time UI| User
```

The flow:
1. User sends a message
2. Frontend streams the conversation to the backend via SSE
3. Backend calls OpenAI with the conversation + available tools
4. OpenAI decides which tools to call (if any)
5. Backend executes tool calls against SQLite
6. Tool results are sent back to OpenAI
7. OpenAI generates the final response
8. Backend streams everything back to the frontend via SSE

## Core Flows

Following the mission guidelines the system handles three main workflows.
Each demonstrates multi-run conversations and appropriate tool usage.
[Check here the document which covers the flows](docs/evaluation_plan.md)

## Project Structure

```
├── backend/                    # FastAPI application
│   ├── routers/               # API endpoints
│   │   ├── chat.py           # Main chat endpoint (SSE streaming)
│   │   ├── health.py         # Health check endpoint
│   │   └── medications.py    # Medication info endpoints
│   ├── services/              # Business logic
│   │   ├── openai_client.py  # OpenAI API client
│   │   └── agent_service.py  # Agent orchestration + tool calling loop
│   ├── tools/                 # Tool implementations
│   │   ├── registry.py       # Tool schemas and dispatcher
│   │   ├── medication_tools.py
│   │   ├── user_tools.py
│   │   └── prescription_tools.py
│   ├── repositories/          # Database access layer
│   │   ├── medication_repo.py
│   │   ├── user_repo.py
│   │   ├── prescription_repo.py
│   │   └── stock_repo.py
│   ├── prompts/               # System prompts
│   │   └── system_prompt.py  # Main assistant instructions
│   ├── schemas/               # Pydantic models
│   ├── tests/                 # pytest tests
│   │   ├── test_tools_medication.py
│   │   ├── test_agent_safety.py
│   │   └── test_normalization.py
│   ├── utils/                 # Utilities
│   │   └── normalization.py  # Input normalization (phone, email, branch names)
│   ├── main.py               # Application entry point
│   ├── database.py           # Database connection and schema
│   ├── seed_data.py          # Synthetic data population
│   └── requirements.txt      # Python dependencies
│
├── frontend/                  # React application
│   └── src/
│       ├── components/       # UI components
│       │   ├── ChatPage.tsx  # Main chat interface
│       │   ├── MessageList.tsx
│       │   ├── MessageInput.tsx
│       │   └── ToolActivity.tsx  # Tool call visualization
│       ├── hooks/
│       │   └── useChatStream.ts  # SSE streaming hook
│       ├── types/            # TypeScript types
│       │   └── chat.ts
│       ├── App.tsx
│       └── main.tsx
│
├── docs/                      # Documentation
│   ├── SCREENSHOTS.md        # Conversation examples with images
│   ├── evaluation_plan.md    # Test scenarios and evaluation criteria
│   ├── docker_run.md         # Detailed Docker instructions
│   ├── DATABASE_SCHEMA.md    # Database structure and sample data
│   └── decisions.md          # Architecture decisions
│
├── docker-compose.yml        # Docker orchestration
├── .gitignore
└── README.md                 # This file
```
