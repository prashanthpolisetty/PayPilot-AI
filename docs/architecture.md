# System Architecture & State Machine

## 1. Overview
The Razorpay AI Growth & Agentic Commerce Platform implements a strict **Separation of Concerns**:
- **LLM / AI Layer:** Handles intent understanding, natural language reasoning, catalog search query extraction, product recommendation with explainability, and contextual upsell generation.
- **Deterministic Backend Authority:** Holds 100% control over pricing, inventory checks, bounded policy enforcement, human approval verification, Razorpay test order creation, and payment verification/webhooks.

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

---

## 2. 18-Step Agentic Commerce Pipeline

```mermaid
stateDiagram-v2
    [*] --> UnderstandIntent: 1. User natural language prompt
    UnderstandIntent --> SearchCatalog: 2. Extract category & budget
    SearchCatalog --> RankProducts: 3. Structured catalog filter
    RankProducts --> RecommendProduct: 4. Top recommendation + rationale
    RecommendProduct --> ProposeUpsell: 5. Contextual add-on suggestion
    ProposeUpsell --> BuildCart: 6. Add items to cart (version bump)
    BuildCart --> CalculateAuthoritativeTotal: 7. Server price calculation
    CalculateAuthoritativeTotal --> PolicyCheck: 8. Verify <= ₹1,00,000 cap & quantity
    
    state PolicyCheckDecision <<choice>>
    PolicyCheck --> PolicyCheckDecision
    PolicyCheckDecision --> ExplainPolicyBlock: Policy Exceeded / Out of Stock
    PolicyCheckDecision --> PresentPaymentSummary: Policy Passed

    ExplainPolicyBlock --> [*]

    PresentPaymentSummary --> HumanApprovalGate: 9. Require explicit human confirmation
    
    state ApprovalDecision <<choice>>
    HumanApprovalGate --> ApprovalDecision
    ApprovalDecision --> CartPreserved: Rejected by User
    ApprovalDecision --> CreateRazorpayOrder: 10. Approved for current cart version

    CartPreserved --> [*]

    CreateRazorpayOrder --> PaymentAttempt: 11. Razorpay Test Order Created
    
    state PaymentOutcome <<choice>>
    PaymentAttempt --> PaymentOutcome
    PaymentOutcome --> GracefulRecovery: Payment Failed (Declined)
    PaymentOutcome --> VerifyPaymentSignature: 12. Server-side signature / webhook

    GracefulRecovery --> [*]

    VerifyPaymentSignature --> MarkOrderPaid: 13. Verified PAID + Decrement Inventory
    MarkOrderPaid --> RecordAuditTrail: 14. Write immutable audit log
    RecordAuditTrail --> [*]
```

---

## 3. Database Schema

| Table | Purpose |
| :--- | :--- |
| `users` | Customer reference and identity. |
| `merchants` | Merchant profile and store configuration. |
| `products` | Authoritative catalog items, prices in minor units (paise), inventory, and attributes JSON. |
| `carts` | Session shopping carts with integer versioning for approval invalidation. |
| `cart_items` | Individual line items and authoritative unit totals. |
| `orders` | Completed checkout orders linked to carts and Razorpay order IDs. |
| `payments` | Recorded transaction attempts, methods, and error codes. |
| `approvals` | Explicit user approval checkpoints bound to specific cart versions. |
| `agent_runs` | Conversational session runs with model telemetry. |
| `agent_actions` | Granular tool executions, arguments, summaries, and latency ms. |
| `audit_logs` | Immutable event stream for full traceability. |
| `webhook_events` | Idempotent webhook event ledger. |
