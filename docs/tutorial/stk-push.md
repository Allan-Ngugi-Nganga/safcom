# STK Push

STK Push (also called Lipa Na M-Pesa Online) is the most common M-Pesa integration. It sends a payment prompt to a customer's phone &mdash; they enter their PIN, and the money moves instantly.

---

## The Basics

### Minimal Example

```python
from safcom import Mpesa

mpesa = Mpesa(
    consumer_key="your_key",
    consumer_secret="your_secret",
    passkey="your_passkey",
    shortcode="174379",
    env="sandbox",
)

resp = mpesa.stk_push(
    phone="254712345678",
    amount=500,
    account_ref="INV-001",
)

print(resp.checkout_request_id)  # Save this for later queries
```

That's it. The customer gets an M-Pesa PIN prompt on their phone.

### With All Options

```python
resp = mpesa.stk_push(
    phone="254712345678",
    amount=500,
    account_ref="INV-001",
    transaction_desc="Payment for invoice INV-001 — thank you!",
    callback_url="https://your-app.com/mpesa/callback",
)
```

### The Response

The method returns a [`STKPushResponse`](../api-reference/models.md#stkpushresponse) with:

| Field | Description |
|---|---|
| `checkout_request_id` | Unique ID for this transaction. Save it — you'll need it to query the result later. |
| `merchant_request_id` | Merchant request ID from M-Pesa. |
| `response_code` | `"0"` means the request was received (not paid yet — the customer still needs to enter their PIN). |
| `response_description` | Human-readable description of the response. |
| `customer_message` | Message shown on the customer's phone. |

!!! warning "Important"
    A successful STK Push response means M-Pesa **received** the request. It does **not** mean the customer paid. The customer still needs to enter their PIN on their phone. You must check the final status using [Payment Query](query-status.md) or a [callback](#setting-up-callbacks).

---

## Setting Up Callbacks

Callbacks let M-Pesa notify your server automatically when a payment completes. Without callbacks, you have to [poll for the status](query-status.md) yourself.

### 1. Set a Global Callback URL

```python
mpesa.set_callback_url("https://your-app.com/mpesa/callback")
```

All subsequent STK pushes will use this URL unless you override it per-request.

### 2. Handle the Callback

M-Pesa sends a POST request to your callback URL with this payload:

```json
{
  "Body": {
    "stkCallback": {
      "MerchantRequestID": "23070-43918244-1",
      "CheckoutRequestID": "ws_CO_202507202359590000",
      "ResultCode": 0,
      "ResultDesc": "The service request is processed successfully.",
      "CallbackMetadata": {
        "Item": [
          {"Name": "Amount", "Value": 100.0},
          {"Name": "MpesaReceiptNumber", "Value": "NLJ91HA6ES"},
          {"Name": "TransactionDate", "Value": 20250720235959},
          {"Name": "PhoneNumber", "Value": 254712345678}
        ]
      }
    }
  }
}
```

You can process this manually, or use safcom's helper:

```python
from safcom.callbacks import parse_stk_callback

# Inside your Flask/FastAPI/anything webhook handler
@app.post("/mpesa/callback")
def mpesa_callback(request):
    data = request.json()
    result = parse_stk_callback(data)

    if result.success:
        print(f"Payment received! KES {result.amount}")
        print(f"Receipt: {result.receipt}")
        # Update your database, mark invoice as paid, etc.
    else:
        print(f"Payment failed: {result.result_description}")

    return {"ResultCode": 0, "ResultDesc": "Success"}
```

!!! tip "Always return 200"
    M-Pesa expects a `200 OK` response with `{"ResultCode": 0}`. If you don't respond in time, they'll retry.

---

## Phone Number Format

safcom accepts phone numbers in any of these formats:

```python
# All of these work — safcom normalises them automatically
mpesa.stk_push(phone="0712345678", ...)       # Kenyan format (07XX)
mpesa.stk_push(phone="254712345678", ...)     # International format
mpesa.stk_push(phone="+254712345678", ...)    # With plus
mpesa.stk_push(phone="254 712 345 678", ...)  # With spaces
mpesa.stk_push(phone="254-712-345-678", ...)  # With hyphens
```

If the phone number is invalid, you get a clear error:

```python
>>> mpesa.stk_push(phone="12345", amount=100, account_ref="test")
ValidationError: Phone number must be 12 digits in 254 format, got 5 digits
```

---

## Common Patterns

### Invoice Payment Flow

```python
def charge_customer(invoice_id: str, amount: float, phone: str):
    """Charge a customer and return the checkout ID for tracking."""
    mpesa.set_callback_url(f"https://your-app.com/mpesa/callback/{invoice_id}")

    resp = mpesa.stk_push(
        phone=phone,
        amount=amount,
        account_ref=invoice_id,
        transaction_desc=f"Payment for invoice {invoice_id}",
    )

    # Save checkout_request_id to your database
    save_to_db(invoice_id, resp.checkout_request_id)

    return resp.checkout_request_id
```

### Payment with Retry Logic

```python
from safcom import Mpesa
from safcom.exceptions import APIError
import time

mpesa = Mpesa(...)

for attempt in range(3):
    try:
        resp = mpesa.stk_push(phone="254712345678", amount=500, account_ref="INV-001")
        print(f"Sent! Checkout: {resp.checkout_request_id}")
        break
    except APIError as e:
        if attempt < 2:
            print(f"Attempt {attempt + 1} failed, retrying...")
            time.sleep(2)
        else:
            raise
```

---

## What's Next?

- [Check if the payment went through](query-status.md)
- [Set up for production](production.md)
