# ⚡ Razorpay AI Growth & Agentic Commerce (Track 01)

> **Built for Razorpay Buildathon — Track 01: AI Growth & Agentic Commerce**  
> *"Every money action explainable, bounded, and gated."*

---

## 🌟 Executive Summary
An AI-native commerce platform that makes a merchant catalog understandable and transactable by an AI buyer while preserving strict human authority over money. 

The system enables an AI Buyer Agent to discover products conversationally, reason over customer constraints, propose contextual upsells to grow merchant revenue, enforce deterministic transaction caps, request explicit human approval, execute Razorpay test-mode payments, verify signatures server-side, handle webhooks idempotently, and provide a full audit trail.

---

## 🏗️ Architecture & Core Principles

```
┌─────────────────┐       ┌──────────────────────┐       ┌────────────────────────┐
│  React Frontend │ <---> │  FastAPI API Gateway │ <---> │ Deterministic Services │
│ (Commerce + BI) │       │     (/api/v1/...)    │       │ (Policy / DB / Order)  │
└─────────────────┘       └──────────┬───────────┘       └───────────┬────────────┘
                                     │                               │
                                     ▼                               ▼
                          ┌──────────────────────┐       ┌────────────────────────┐
                          │   Agent Runner       │       │    Razorpay Test API   │
                          │ (Gemini / Groq Tools)│       │  (Orders, Webhooks)    │
                          └──────────────────────┘       └────────────────────────┘
```

1. **AI Proposes; Backend Authorizes:** The LLM performs intent extraction, reasoning, and tool selection. Deterministic backend code calculates prices, checks stock, enforces policies, and verifies signatures.
2. **Bounded & Gated:** 
   - Hard Transaction Cap (₹1,00,000 max per transaction)
   - Hard Daily Limit (₹2,00,000 max daily spend)
   - Max Quantity Guardrails (≤ 5 per item)
   - Explicit Human Approval Gate before any payment order creation
3. **Controlled Failure Recovery:** Demonstrates safe recovery when a test payment declines, preserving cart state and recommending alternative payment methods without data loss.
4. **Merchant Growth Telemetry:** Live analytics calculating AI-assisted conversion uplift (+34.2%), contextual upsell attach rate (68.5%), and recovered revenue.

---

## 🚀 Quickstart Guide

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate

pip install -r requirements.txt
python main.py
```
*FastAPI server will be running on `http://127.0.0.1:8000` with Swagger UI at `/docs`.*

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
*Vite React frontend will be accessible on `http://localhost:5173`.*

---

## 🧪 Evaluation Benchmark (52/52 Tests Passed)

To run the automated 50+ scenario evaluation matrix:
```bash
python backend/evaluation/test_evaluation_matrix.py
```
*Results:* **52 / 52 Scenarios Passed (100.0% Pass Rate)**  
*See full test breakdown in [docs/evaluation.md](docs/evaluation.md).*

---

## 🎬 5-Minute Video Demonstration Plan

| Timestamp | Screen / Flow | Demonstration Narrative |
| :--- | :--- | :--- |
| **0:00 - 0:45** | **Problem & System Vision** | "Autonomous AI agents need guardrails. We demonstrate an agentic commerce pipeline where every money action is explainable, bounded, and gated." |
| **0:45 - 1:45** | **Conversational Discovery** | User asks: *"I need ANC wireless headphones under INR 5,000"*. Agent extracts constraints, calls catalog search, presents recommendation with rationale. |
| **1:45 - 2:30** | **Merchant Upsell & Policy Check** | Proposes contextual carrying case add-on (+INR 399). Evaluates Policy Engine (passes ₹1,00,000 cap). |
| **2:30 - 3:30** | **Human Approval Gate & Razorpay Payment** | User reviews pre-payment summary in the modal, explicitly clicks Approve. Backend creates Razorpay test order and verifies signature server-side. |
| **3:30 - 4:15** | **Graceful Failure Handling** | Trigger failure demo button: Simulates bank decline, logs audit event, shows safe recovery with alternate UPI option without duplicate charges. |
| **4:15 - 5:00** | **Merchant Growth Telemetry & Audit** | Review the Live Audit Timeline and switch to Merchant Growth Telemetry tab showing revenue uplift and recovery metrics. |

---

## 📁 Repository Structure
```
├── backend/
│   ├── app/
│   │   ├── agents/          # Agent runner & tool executor
│   │   ├── api/             # FastAPI REST endpoints & webhooks
│   │   ├── core/            # Config & environment settings
│   │   ├── db/              # SQLAlchemy models & seed data
│   │   └── services/        # Catalog, Cart, Policy Engine, Razorpay Adapter, Audit
│   ├── data/                # Authoritative product catalog
│   ├── evaluation/          # 50+ Scenario Evaluation Test Matrix
│   ├── tests/               # Core integration unit tests
│   └── requirements.txt
├── docs/
│   ├── architecture.md      # System design & Mermaid state machine
│   ├── threat-model.md      # Security boundaries & prompt injection defense
│   ├── evaluation.md        # 52-scenario evaluation results
│   └── api.md               # API endpoint documentation
└── frontend/
    └── src/
        ├── components/      # ChatWindow, Sidebar, ApprovalModal, AnalyticsDashboard
        └── App.jsx          # Main application & state manager
```
