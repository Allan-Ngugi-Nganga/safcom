# Account Balance

Query your M-Pesa account balance programmatically.

---

## Prerequisites

Your app needs:

- **Account Balance API** enabled on the Safaricom Developer Portal
- An **Initiator Name** and **Security Credential**
- Configured **Queue Timeout URL** and **Result URL**

---

## Basic Usage

```python
resp = mpesa.account_balance(
    initiator_name="testapi",
    security_credential="your_encrypted_credential",
)
```

### The Response

Returns an [`AccountBalanceResponse`](../api-reference/models.md#accountbalanceresponse):

| Field | Description |
|---|---|
| `conversation_id` | Unique ID for this request |
| `originator_conversation_id` | Originator's conversation ID |
| `response_code` | `"0"` means the request was accepted |
| `response_description` | Human-readable response |

!!! note "Balance details arrive in the callback"
    Like B2C, the actual balance information arrives asynchronously via a callback to your `ResultURL`. The initial response only confirms that the request was accepted.
