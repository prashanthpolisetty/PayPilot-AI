# Machine-Readable API Reference

Base URL: `/api/v1`

## 1. Conversational Agent
### `POST /api/v1/chat`
Conversational endpoint for the AI Buyer Agent.
- **Request Body:**
  ```json
  {
    "message": "I need ANC wireless headphones under INR 5,000",
    "session_id": "demo_session",
    "user_id": "user_demo_001",
    "cart_id": "optional_cart_id"
  }
  ```
- **Response:**
  ```json
  {
    "run_id": "uuid",
    "session_id": "demo_session",
    "user_message": "...",
    "agent_response": "Markdown formatted recommendation + explanation",
    "actions_taken": [...],
    "cart_id": "cart_uuid"
  }
  ```

---

## 2. Structured Catalog
### `GET /api/v1/products`
Fetch machine-readable product catalog with filtering.
- **Query Params:**
  - `query` (str): Search term
  - `category` (str): Filter by category (e.g. `Audio`, `Laptops`)
  - `max_price` (float): Max price in Rupees
  - `min_price` (float): Min price in Rupees

### `GET /api/v1/products/{product_id}`
Retrieve authoritative product data and available upsells.

---

## 3. Cart & Policy Control
### `POST /api/v1/carts`
Initialize a new shopping cart.
- **Request Body:** `{"user_id": "...", "merchant_id": "..."}`

### `POST /api/v1/carts/{cart_id}/items`
Add product item with quantity.
- **Request Body:** `{"product_id": "prod_apex_anc", "quantity": 1}`

### `POST /api/v1/carts/{cart_id}/policy-check`
Deterministic Policy Engine evaluation. Returns `{allowed: boolean, reason_codes: [], details: {}}`.

### `POST /api/v1/carts/{cart_id}/approval`
Record explicit user approval for a specific cart version.

---

## 4. Razorpay Orders & Verification
### `POST /api/v1/orders`
Create a Razorpay Test Mode Payment Order (requires policy pass & approval check).

### `POST /api/v1/payments/verify`
Verify Razorpay HMAC-SHA256 signature server-side and transition order to `PAID`.

### `POST /api/v1/webhooks/razorpay`
Idempotent webhook receiver for `order.paid`, `payment.captured`, and `payment.failed`.

---

## 5. Telemetry & Analytics
### `GET /api/v1/analytics/merchant`
Returns live Track 01 metrics: total verified revenue, AI uplift %, attach rates, and recovery stats.

### `GET /api/v1/audit`
Returns immutable audit log event stream.
