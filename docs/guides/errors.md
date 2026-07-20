# Error Handling

safcom raises clear, typed exceptions so you always know what went wrong.

---

## Exception Hierarchy

```
SafcomError
├── AuthError          — Authentication failures
├── APIError           — M-Pesa API errors
└── ValidationError    — Input validation errors
```

---

## AuthError

Raised when M-Pesa authentication fails. Usually means your consumer key or secret is wrong.

```python
from safcom import Mpesa
from safcom.exceptions import AuthError

mpesa = Mpesa("wrong_key", "wrong_secret", "passkey", "174379")

try:
    mpesa.stk_push(phone="254712345678", amount=100, account_ref="test")
except AuthError as e:
    print(f"Authentication failed: {e}")
    # → "Authentication failed: 401 Client Error: Unauthorized"
```

**Common causes:**

- Consumer key or secret is incorrect
- API not subscribed to your app on the developer portal
- Using sandbox credentials against production environment (or vice versa)

---

## APIError

Raised when the M-Pesa API returns an error response or the request fails.

```python
from safcom.exceptions import APIError

try:
    mpesa.stk_push(phone="254712345678", amount=100, account_ref="test")
except APIError as e:
    print(f"API Error: {e}")
    # Error object includes:
    # e.response_code — M-Pesa error code (if available)
```

**Common error codes:**

| Response Code | Meaning | What to do |
|---|---|---|
| `0` | Success | All good |
| `1` | Insufficient balance | Customer doesn't have enough money |
| `1032` | Request cancelled | Customer declined the PIN prompt |
| `1037` | Request timeout | Customer didn't respond in time |
| `1031` | Wrong passkey | Check your passkey |
| `2001` | Invalid initiator | B2C initiator credentials are wrong |

---

## ValidationError

Raised before any API call if your input is invalid.

```python
from safcom.exceptions import ValidationError

try:
    mpesa.stk_push(phone="123", amount=100, account_ref="test")
except ValidationError as e:
    print(f"Invalid input: {e}")
    # → "Phone number must be 12 digits in 254 format, got 3 digits"
```

**What's validated:**

| Input | Validation |
|---|---|
| Phone number | Must be a valid Kenyan number (12 digits in 254 format) |
| Amount | Must be greater than 0 |
| Account reference | Must be 1–12 characters |
| Environment | Must be `"sandbox"` or `"production"` |

---

## Best Practices

### 1. Always catch specific exceptions

```python
# Good — handle each case differently
try:
    resp = mpesa.stk_push(...)
except AuthError:
    alert_team("M-Pesa credentials need updating")
except APIError:
    retry_with_backoff()
except ValidationError:
    log_bad_input()
    return error_to_user()
```

### 2. Log the full error

```python
import logging

logger = logging.getLogger(__name__)

try:
    resp = mpesa.stk_push(...)
except APIError as e:
    logger.error(f"M-Pesa API error: {e}", exc_info=True)
    # exc_info=True captures the full traceback
```

### 3. Use retries for transient failures

```python
import time
from safcom.exceptions import APIError

max_retries = 3
for attempt in range(max_retries):
    try:
        resp = mpesa.stk_push(...)
        break
    except APIError as e:
        if attempt == max_retries - 1:
            raise
        time.sleep(2 ** attempt)  # Exponential backoff
```
