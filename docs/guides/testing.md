# Testing & Sandbox

The Safaricom sandbox lets you test your integration without real money. Here's how to use it effectively.

---

## Getting Sandbox Credentials

1. Go to the [Safaricom Developer Portal](https://developer.safaricom.co.ke/)
2. Create an account (if you haven't already)
3. Create a new app and subscribe to **Lipa Na M-Pesa Online**
4. Note your **Consumer Key** and **Consumer Secret**
5. Use the standard sandbox passkey: `bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919`
6. Use the sandbox shortcode: `174379`

---

## Testing STK Push

```python
from safcom import Mpesa

mpesa = Mpesa(
    consumer_key="your_sandbox_key",
    consumer_secret="your_sandbox_secret",
    passkey="bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919",
    shortcode="174379",
    env="sandbox",
)

# In sandbox, use a test phone number
resp = mpesa.stk_push(
    phone="254708374149",  # Standard sandbox test number
    amount=100,
    account_ref="TEST-001",
)
```

!!! tip "Sandbox test numbers"
    - `254708374149` — Simulates a successful payment
    - `254708374148` — Simulates a payment timeout (ResultCode 1037)
    - `254708374147` — Simulates an insufficient balance (ResultCode 1)

---

## Testing Callbacks

The sandbox doesn't send real callbacks. To test your callback handler:

1. Run your server locally with a tool like [ngrok](https://ngrok.com/)
2. Set your callback URL to your ngrok URL
3. Send an STK push to a sandbox test number
4. After 10-15 seconds, the sandbox will POST a simulated callback to your URL

```bash
# In one terminal — start your server
uvicorn my_app:app --reload

# In another terminal — expose it
ngrok http 8000
# → https://abc123.ngrok.io
```

```python
mpesa.set_callback_url("https://abc123.ngrok.io/mpesa/callback")
```

---

## Running the Test Suite

safcom includes a test suite for validation logic. Run it with:

```bash
cd safcom
python -m pytest tests/ -v
```

The tests cover:

- Phone number normalisation (`0712...`, `254712...`, `+254712...`)
- Amount validation
- Account reference length validation
- Password/timestamp format

---

## Testing Checklist

Before going live, verify:

- [ ] STK Push sends successfully in sandbox
- [ ] STK Push Query returns the correct status
- [ ] Callback handler processes incoming notifications
- [ ] Invalid phone numbers are rejected gracefully
- [ ] Negative amounts are rejected
- [ ] Error handling catches and logs failures
- [ ] Production credentials are separate from sandbox
