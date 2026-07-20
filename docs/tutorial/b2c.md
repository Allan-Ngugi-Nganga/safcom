# B2C — Send Money to Customers

B2C (Business to Customer) lets you send money from your M-Pesa business account to a customer's phone. Common use cases include refunds, payouts, and rewards.

---

## Prerequisites

Before using B2C, your app needs:

- **B2C API** enabled on the Safaricom Developer Portal
- An **Initiator Name** and **Security Credential** (set up in the M-Pesa portal)
- The **Queue Timeout URL** and **Result URL** configured

!!! warning "Not available in sandbox by default"
    B2C requires additional configuration on your M-Pesa account. Test with sandbox first, but be aware that B2C behaves differently in sandbox vs production.

---

## Basic Usage

```python
resp = mpesa.b2c(
    phone="254712345678",
    amount=500,
    remarks="refund",
    initiator_name="testapi",
    security_credential="your_encrypted_credential",
)
```

### The Response

Returns a [`B2CResponse`](../api-reference/models.md#b2cresponse):

| Field | Description |
|---|---|
| `conversation_id` | Unique ID for this transaction |
| `originator_conversation_id` | Originator's conversation ID |
| `response_code` | `"0"` means the request was accepted |
| `response_description` | Human-readable response |

---

## With All Options

```python
resp = mpesa.b2c(
    phone="254712345678",
    amount=500,
    remarks="refund for order #1234",
    initiator_name="your_initiator_name",
    security_credential="your_encrypted_credential",
    occasion="Q1-promotion",          # Optional
)
```

---

## Real-World Example: Automated Refunds

```python
def process_refund(order_id: str, amount: float, phone: str):
    """Send a refund to a customer."""
    try:
        resp = mpesa.b2c(
            phone=phone,
            amount=amount,
            remarks=f"refund-{order_id}",
            initiator_name="refund_bot",
            security_credential=get_credential(),
        )
        log_refund(order_id, resp.conversation_id)
        return True
    except APIError as e:
        log_error(f"Refund failed for {order_id}: {e}")
        return False
```

---

## Important Notes

- B2C requires **initiator credentials** configured in the M-Pesa portal
- The `security_credential` must be encrypted using Safaricom's public key
- Transactions are **asynchronous** — the result arrives via a callback to your `ResultURL`
- Minimum amount is KES 10
- You cannot B2C to your own shortcode
