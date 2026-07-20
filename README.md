<h1 align="center">safcom</h1>
<p align="center">
  <em>M-Pesa API — the way it should be.</em>
  <br>
  <br>
  <img src="https://img.shields.io/badge/python-≥3.10-10b981" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/license-MIT-10b981" alt="MIT License">
  <img src="https://img.shields.io/badge/version-0.1.0-10b981" alt="Version 0.1.0">
  <a href="https://allan-ngugi-nganga.github.io/safcom/"><img src="https://img.shields.io/badge/docs-mkdocs-2563eb" alt="Docs"></a>
</p>

---

STK push, payment queries, B2C, account balance, callback parsing — all in a clean Python package that doesn't make you read raw JSON.

```bash
pip install safcom
```

📖 **[Full documentation →](https://allan-ngugi-nganga.github.io/safcom/)**

---

## Quick Start

```python
from safcom import Mpesa

mpesa = Mpesa(
    consumer_key="your_key",
    consumer_secret="your_secret",
    passkey="your_passkey",
    shortcode="174379",
    env="sandbox",      # or "production"
)

# One line. STK push. Done.
resp = mpesa.stk_push(
    phone="254712345678",
    amount=100,
    account_ref="INV-001",
)

print(resp.checkout_request_id)   # → "ws_CO_...202507..."
print(resp.customer_message)      # → "Please enter your M-Pesa PIN"
```

## Features

### Core API

| Feature | | Description |
|---|---|---|
| **STK Push** | ✅ | Lipa Na M-Pesa Online — one call to charge a customer |
| **Payment Query** | ✅ | Check if a transaction went through |
| **B2C** | ✅ | Send money from your business to customers |
| **Account Balance** | ✅ | Query your M-Pesa balance |
| **Callbacks** | ✅ | Parse M-Pesa payment notifications with `parse_stk_callback()` |
| **CLI** | ✅ | Test payments right from the terminal |

### Developer Experience

- **Automatic auth** — OAuth tokens refresh automatically. Never think about it.
- **Typed responses** — Every response is a dataclass, not a raw dict.
- **Phone normalisation** — `0712...`, `254712...`, `+254712...` all work.
- **Clear errors** — No cryptic M-Pesa error codes. Each exception tells you what went wrong.
- **CLI included** — Test payments without writing any code.
- **Examples included** — Copy-paste ready FastAPI and Flask apps in `/examples/`.

## Usage

### STK Push

```python
# Minimal
resp = mpesa.stk_push(phone="254712345678", amount=500, account_ref="INV-001")

# With all options
resp = mpesa.stk_push(
    phone="254712345678",
    amount=500,
    account_ref="INV-001",
    transaction_desc="Payment for invoice INV-001",
    callback_url="https://your-app.com/mpesa/callback",
)
```

### Check Payment Status

```python
status = mpesa.stk_push_query("ws_CO_...202507...")

if status.success:
    print(f"Paid! Receipt: {status.receipt}")
else:
    print(f"Not paid: {status.result_description}")
```

### Parse a Callback Notification

M-Pesa sends payment results to your callback URL. Parse them with:

```python
from safcom.callbacks import parse_stk_callback

@app.post("/mpesa/callback")
def handle_callback(request):
    body = request.get_json()
    result = parse_stk_callback(body)

    if result.success:
        print(f"✅ KES {result.amount} — Receipt: {result.receipt}")
        # Update your database, mark invoice as paid
    else:
        print(f"❌ Failed: {result.result_description}")

    return {"ResultCode": 0, "ResultDesc": "Success"}
```

### Send Money (B2C)

```python
resp = mpesa.b2c(
    phone="254712345678",
    amount=500,
    remarks="refund",
    initiator_name="testapi",
    security_credential="...",
)
```

### Account Balance

```python
resp = mpesa.account_balance(
    initiator_name="testapi",
    security_credential="...",
)
```

### From the CLI

```bash
# Set credentials (or use SAFCOM_* env vars)
export SAFCOM_CONSUMER_KEY=your_key
export SAFCOM_CONSUMER_SECRET=your_secret
export SAFCOM_PASSKEY=your_passkey
export SAFCOM_SHORTCODE=174379

# Send STK push
safcom stkpush 254712345678 100 --ref INV-001

# Query payment status
safcom query ws_CO_...202507...
```

### Example Apps

Copy-paste ready applications that demonstrate a full payment flow:

```bash
# FastAPI
pip install safcom[fastapi]
CONSUMER_KEY=... CONSUMER_SECRET=... PASSKEY=... CALLBACK_URL=... uvicorn examples.fastapi_app:app

# Flask
pip install safcom[flask]
CONSUMER_KEY=... CONSUMER_SECRET=... PASSKEY=... CALLBACK_URL=... python examples/flask_app.py
```

## Why safcom?

The M-Pesa API is powerful but painful. Every Kenyan developer hits the same wall:

- ❌ **Manual authentication** — Generate a token, track expiry, refresh. Every. Single. Time.
- ❌ **Inconsistent responses** — Sandbox and production disagree on field names, error codes, and response shapes.
- ❌ **Copy-paste code** — Every project starts by copying a Medium post from 2022 that's already outdated.

✅ **safcom** fixes all of that. Sensible defaults, typed responses, clear errors. One package, one `pip install`, done.

## Roadmap

- [x] STK Push
- [x] STK Push Query
- [x] B2C (BusinessPayment)
- [x] Account Balance
- [x] Callback parsing
- [x] CLI
- [x] Example apps (FastAPI + Flask)
- [x] Documentation site (MkDocs + Material)
- [ ] C2B Register URL
- [ ] C2B Simulate
- [ ] Reversal
- [ ] Transaction Status
- [ ] Async support (httpx.AsyncClient)

## Installation

```bash
pip install safcom
```

Optional extras:

| Extra | Includes |
|---|---|
| `safcom[fastapi]` | FastAPI + Uvicorn (for examples) |
| `safcom[flask]` | Flask (for examples) |
| `safcom[docs]` | MkDocs + Material (build docs locally) |
| `safcom[dev]` | Pytest (run tests) |

## Documentation

Full documentation with tutorial, API reference, and guides:

📖 **[allan-ngugi-nganga.github.io/safcom](https://allan-ngugi-nganga.github.io/safcom/)**

## License

MIT — use it freely in personal and commercial projects.
