# Worknoon Desk — AI-Powered Resolution Panel

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![Next.js](https://img.shields.io/badge/Next.js-15-black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal)
![License](https://img.shields.io/badge/license-MIT-yellow)

**An AI-powered customer support system that evaluates requests against company policies and returns structured decisions using Google Gemini.**

[Features](#features) • [Architecture](#architecture) • [Installation](#installation) • [API Docs](#api-documentation) • [Demo](#demo)

</div>

---

## Overview

The WorkNoon AI Support Assistant is a full-stack application that automates customer support triage. When a customer submits a support request, the system:

1. **Resolves** the customer by ID or name
2. **Fetches** their order history
3. **Evaluates** applicable company policies (deterministic — no AI needed)
4. **Calls Gemini AI** with full context and structured output schema
5. **Returns** a policy-grounded decision: `approved`, `denied`, or `escalated`

The key architectural insight: **policy enforcement happens deterministically before the AI call**. This prevents hallucinations from overriding clear policy rules (e.g., the AI cannot approve a final-sale refund).

---

## Features

### Core
- ✨ **Structured Policy Resolutions** — Gemini 2.0 Flash with structured JSON output
- 📋 **Deterministic Rule Engine** — Hard-stop rules evaluated before AI, preventing hallucination
- 🏷️ **Customer Tiers** — Standard, VIP (60-day window), Enterprise (auto-escalate)
- 🔍 **Smart Autocomplete** — Search and resolve customer profiles by ID or name
- 📜 **Audit Trail** — Every decision logged with full reasoning and policies applied
- 📊 **Support History** — Paginated history with decision status

### Technical
- ⚡ **FastAPI** — Async, auto OpenAPI docs at `/docs`
- 🗃️ **SQLite + SQLAlchemy ORM** — Zero-infra, WAL mode for performance
- 🎨 **Next.js 15** — TypeScript, Tailwind CSS, App Router
- 🔒 **Security** — CORS, input validation, sanitized error responses
- 🧪 **Tests** — Unit tests for policy engine + integration tests for all endpoints

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Next.js Frontend                      │
│                   (localhost:3000)                       │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Pages: Main Support Form | History Dashboard      │  │
│  │  Components: CustomerLookup, SupportForm,          │  │
│  │              ResponseDisplay, HistoryTable         │  │
│  │  State: Zustand | API: Axios                       │  │
│  └────────────────────────┬───────────────────────────┘  │
└───────────────────────────┼─────────────────────────────┘
                            │ REST API
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Backend                        │
│                   (localhost:8000)                       │
│                                                          │
│  POST /support/request ──→ [8-Step Pipeline]            │
│  ┌──────────────────────────────────────────────────┐   │
│  │ 1. Resolve Customer                              │   │
│  │ 2. Fetch Recent Orders                           │   │
│  │ 3. Resolve Target Order                          │   │
│  │ 4. Load Active Policies                          │   │
│  │ 5. Policy Engine (deterministic hard-stops)      │   │
│  │ 6. AI Context Builder                            │   │
│  │ 7. Gemini API (structured JSON output)           │   │
│  │ 8. Persist + Return Response                     │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  Database: SQLite (SQLAlchemy ORM, WAL mode)             │
│  Tables: customers, orders, support_requests,            │
│          support_policies, conversation_history          │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              Google Gemini 2.0 Flash API                 │
│  • response_mime_type: application/json                  │
│  • temperature: 0.2 (consistent decisions)               │
│  • Full policy context injected as system prompt         │
└─────────────────────────────────────────────────────────┘
```

### Hallucination Prevention

The system uses a **defense-in-depth** approach to prevent AI from making incorrect decisions:

| Layer | Mechanism |
|---|---|
| **Pre-AI Policy Engine** | Hard-stops evaluated before any AI call. Final-sale, expired window, enterprise escalation — no AI involved. |
| **Policy Grounding** | All applicable policies injected verbatim into the prompt. AI cannot invent rules. |
| **Structured Output** | `response_mime_type: application/json` forces JSON-shaped responses. |
| **Post-AI Validation** | Response validated against Pydantic schema. If AI somehow approves a hard-denied case, it's overridden. |
| **Low Temperature** | 0.2 temperature reduces creativity, improves consistency. |

---

## Support Policies

| Policy | Key Rule |
|---|---|
| **Standard Refund** | Full refund within 30 days, delivered, non-final-sale |
| **VIP Customer** | 60-day refund window, priority response |
| **Damaged Product** | Refund/replacement always available, overrides time window |
| **Final Sale** | No refunds — store credit at management discretion only |
| **Large Transaction** | Orders >$500 require manager escalation |
| **Delivery** | Complaints accepted within 14 days of expected delivery |
| **Escalation** | Safety concerns, legal threats, enterprise customers → human agent |

---

## Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- Google Gemini API key ([Get one free](https://aistudio.google.com/))

### 1. Clone / Navigate

```bash
cd worknoon_assessment_ai
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Seed the database
python seed_data.py

# Start the server
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
copy .env.local.example .env.local
# Edit .env.local if needed (default points to localhost:8000)

# Start the dev server
npm run dev
```

### 4. Access the App

| Service | URL | Notes |
|---|---|---|
| Frontend | http://localhost:3000 | Will auto-shift to `3001` or `3002` if port 3000 is occupied. |
| Backend API | http://localhost:8000 | |
| API Docs (Swagger) | http://localhost:8000/docs | |
| API Docs (ReDoc) | http://localhost:8000/redoc | |
| Health Check | http://localhost:8000/health | |

*Note: The backend CORS settings are pre-configured to allow frontend access from local ports `3000`, `3001`, and `3002` automatically.*

---

## Environment Variables

### Backend (`.env`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | ✅ Yes | — | Your Google Gemini API key |
| `GEMINI_MODEL` | No | `gemini-2.0-flash` | Gemini model to use |
| `DATABASE_URL` | No | `sqlite:///./support_assistant.db` | Database connection string |
| `CORS_ORIGINS` | No | `http://localhost:3000` | Allowed CORS origins |
| `DEBUG` | No | `true` | Enable debug logging |
| `LOG_LEVEL` | No | `INFO` | Logging level |

### Frontend (`.env.local`)

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API base URL |

---

## API Documentation

Full interactive docs available at `http://localhost:8000/docs` once running.

### Key Endpoints

#### `POST /support/request`
Submit a support request for AI evaluation.

**Request:**
```json
{
  "customer_identifier": "CUST001",
  "order_id": "ORD001",
  "request_text": "I received a damaged product and would like a refund."
}
```

**Response:**
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "customer_id": "CUST001",
  "customer_name": "Alice Johnson",
  "order_id": "ORD001",
  "request_text": "I received a damaged product and would like a refund.",
  "decision": "approved",
  "reasoning": "Order ORD001 is flagged as damaged. Per the Damaged Product Policy, damaged items are eligible for full refund or replacement regardless of purchase date. The 15-day-old order falls within all applicable windows.",
  "recommended_action": "Process full refund of $89.99 to original payment method.",
  "customer_response": "Hello Alice, I'm so sorry to hear about the damaged product. I've approved a full refund of $89.99 which will be returned to your original payment method within 3-5 business days.",
  "policies_applied": ["DAMAGED_PRODUCT_POLICY", "REFUND_POLICY"],
  "confidence_score": 0.95,
  "created_at": "2025-01-15T14:30:00Z"
}
```

#### `GET /customers/{customer_id}`
Get customer profile.

#### `GET /customers/search?q={query}`
Search customers by name or ID.

#### `GET /orders/customer/{customer_id}`
Get all orders for a customer.

#### `GET /support/history?page=1&page_size=20`
Paginated support request history.

#### `GET /policies`
List all active support policies.

---

## Testing

```bash
cd backend

# Run all tests
pytest tests/ -v

# Run only policy engine unit tests
pytest tests/test_policy_engine.py -v

# Run only API integration tests
pytest tests/test_api.py -v

# With coverage
pytest tests/ --cov=app --cov-report=term-missing
```

### Test Coverage Highlights

- ✅ Policy engine: all hard-stop scenarios (final sale, expired window, large transaction, enterprise)
- ✅ Customer API: lookup, search, 404 handling
- ✅ Orders API: single order, customer orders, 404 handling
- ✅ Support API: full pipeline, policy-specific scenarios, validation errors
- ✅ History: pagination, detail retrieval

---

## Mock Data

The seed script creates **10 customers** and **10 orders** covering all scenarios:

| Order | Scenario | Expected Decision |
|---|---|---|
| ORD001 | Within 30-day window, delivered | ✅ Approved |
| ORD002 | 45 days old, outside window | ❌ Denied |
| ORD003 | Final sale item | ❌ Denied |
| ORD004 | Damaged product | ✅ Approved |
| ORD005 | $1,249.99 large transaction | ⬆️ Escalated |
| ORD006 | VIP customer, 45 days (within 60-day window) | ✅ Approved |
| ORD007 | Overdue delivery complaint | 🔍 AI evaluates |
| ORD008 | Enterprise customer | ⬆️ Escalated |
| ORD009 | Wrong size, within window | ✅ Approved |
| ORD010 | VIP + damaged + large transaction | ⬆️ Escalated |

---

## Project Structure

```
worknoon_assessment_ai/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry
│   │   ├── config.py            # Settings (pydantic-settings)
│   │   ├── database.py          # SQLAlchemy engine + session
│   │   ├── models/              # ORM models (5 tables)
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── routers/             # API route handlers
│   │   └── services/            # Business logic layer
│   │       ├── customer_service.py
│   │       ├── order_service.py
│   │       ├── policy_engine.py  # ← Key differentiator
│   │       ├── ai_service.py     # ← Gemini integration
│   │       └── support_service.py # ← Pipeline orchestrator
│   ├── tests/
│   │   ├── test_policy_engine.py
│   │   └── test_api.py
│   ├── seed_data.py
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── app/                 # Next.js App Router pages
    │   ├── components/          # React components
    │   ├── lib/                 # API client + types
    │   ├── hooks/               # Custom React hooks
    │   └── store/               # Zustand state management
    └── package.json
```

---

## Future Improvements

1. **Authentication** — JWT-based auth with customer portal login
2. **Multi-turn Conversations** — Allow follow-up questions in the same support thread
3. **Agent Dashboard** — Internal tool for human agents to review escalations
4. **Webhook Integration** — Notify agents via Slack/email on escalation
5. **Analytics** — Decision distribution charts, resolution time tracking
6. **RAG Enhancement** — Vector database of past resolved cases for context injection
7. **A/B Prompting** — Test different prompt strategies and measure decision quality
8. **Production Database** — PostgreSQL migration with connection pooling
9. **Docker Compose** — Single-command development environment
10. **CI/CD Pipeline** — GitHub Actions for automated testing and deployment

---

## AI Configuration

The system uses **Google Gemini 2.0 Flash** with these key configurations:

```python
genai.GenerationConfig(
    response_mime_type="application/json",  # Forces structured output
    temperature=0.2,                         # Low = consistent decisions
)
```

### Why Gemini over OpenAI?
- Native structured output via `response_mime_type`
- Generous free tier for development and demos
- Strong performance on instruction-following tasks
- Differentiator: most assessment submissions use OpenAI

### Prompt Architecture
The system prompt establishes the AI's role and critical rules. The user prompt provides:
- Customer profile (tier, spend history)
- Recent order history (last 5 orders)
- Target order details with all policy flags
- Applicable policies with full rule sets
- Policy engine evaluation notes (pre-computed context)

---

*Built as part of the WorkNoon Full Stack Engineer Assessment*
