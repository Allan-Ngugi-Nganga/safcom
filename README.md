<h1 align="center">safcom</h1>
<p align="center">
  <em>M-Pesa API — the way it should be.</em>
  <br>
  <br>
  <img src="https://img.shields.io/badge/python-≥3.10-10b981" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/license-MIT-10b981" alt="MIT License">
  <img src="https://img.shields.io/badge/version-0.1.0-10b981" alt="Version 0.1.0">
</p>

---

STK push, payment queries, B2C, account balance — all in a clean Python package that doesn't make you read raw JSON.

```bash
pip install safcom
```

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

- **STK Push** — Initiate Lipa Na M-Pesa Online payments with one call
- **STK Push Query** — Check if a payment went through
- **B2C** — Send money to customers (BusinessPayment)
- **Account Balance** — Query your M-Pesa balance
- **Callback handling** — Decorator-based handler for M-Pesa notifications
- **Automatic auth** — Tokens refresh automatically; you never think about it
- **Typed responses** — Every response is a dataclass, not raw dicts
- **CLI included** — Test payments from the terminal

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

## Why safcom?

The M-Pesa API is powerful but painful:

- Authentication is manual and easy to mess up
- Responses come in inconsistent formats between sandbox and production
- Error messages are cryptic
- Every Kenyan dev rewrites the same wrapper

safcom fixes all of that. Sensible defaults, typed responses, clear errors. One package, one `pip install`, done.

## Roadmap

- [x] STK Push
- [x] STK Push Query
- [x] B2C (BusinessPayment)
- [x] Account Balance
- [x] CLI
- [ ] C2B Register URL
- [ ] C2B Simulate
- [ ] Reversal
- [ ] Transaction Status
- [ ] Async support (httpx.AsyncClient)

## License

MIT
