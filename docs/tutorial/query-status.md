# Payment Status

After sending an STK push, you need to know whether the customer actually paid. There are two ways to check.

---

## Option 1: Query the Status (Polling)

Use the `checkout_request_id` from your STK Push response to check the final status:

```python
status = mpesa.stk_push_query("ws_CO_202507202359590000")

if status.success:                          # ResultCode == "0"
    print(f"✅ Payment received!")
    print(f"   Receipt: {status.receipt}")          # M-Pesa receipt number
    print(f"   Amount: KES {status.amount}")        # Amount charged
    print(f"   Phone: {status.phone}")              # Customer's number
    print(f"   Date: {status.transaction_date}")    # Date of transaction
else:
    print(f"❌ Failed: {status.result_description}")
```

### When to poll

Polling is useful when:

- You don't have a callback URL set up
- You're testing in sandbox
- You want a quick check during a user session

!!! tip "Don't poll too aggressively"
    Wait at least 5 seconds before the first query (the customer needs time to enter their PIN). If the result isn't ready, space queries 3-5 seconds apart.

### Status result codes

| `result_code` | Meaning |
|---|---|
| `0` | **Success** — payment completed |
| `1037` | **Timeout** — customer didn't enter PIN in time |
| `1032` | **Cancelled** — customer declined the request |
| `1` | **Insufficient balance** |
| Any other | See the `result_description` field |

---

## Option 2: Use Callbacks (Recommended)

[Callbacks](stk-push.md#setting-up-callbacks) are the better approach. M-Pesa notifies your server automatically when the payment completes — no polling needed.

```python
from safcom.callbacks import parse_stk_callback

@app.post("/mpesa/callback")
async def handle_callback(request):
    body = await request.json()
    result = parse_stk_callback(body)

    if result.success:
        await mark_invoice_as_paid(result.receipt, result.amount)
        print(f"✅ Paid: {result.receipt}")
    else:
        print(f"❌ Failed: {result.result_description}")

    return {"ResultCode": 0, "ResultDesc": "Success"}
```

---

## Full Example: Poll + Callback

A robust integration uses both:

1. **Callback** as the primary notification mechanism
2. **Query** as a fallback if the callback doesn't arrive

```python
from safcom import Mpesa
from safcom.exceptions import APIError
import time

mpesa = Mpesa(consumer_key=..., consumer_secret=..., passkey=..., shortcode=...)
mpesa.set_callback_url("https://your-app.com/mpesa/callback")

# Send
resp = mpesa.stk_push(phone="254712345678", amount=500, account_ref="INV-001")
checkout_id = resp.checkout_request_id

# Poll for up to 60 seconds as a safety net
for _ in range(12):  # 12 attempts × 5 seconds = 60 seconds
    time.sleep(5)
    status = mpesa.stk_push_query(checkout_id)
    if status.success:
        print(f"✅ Payment confirmed: {status.receipt}")
        break
    elif status.result_code and status.result_code != "1037":
        print(f"❌ Payment failed: {status.result_description}")
        break
else:
    print("⚠️  No response within 60 seconds — check callback later")
```
