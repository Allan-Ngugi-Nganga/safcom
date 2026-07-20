# CLI

safcom includes a full command-line interface for testing and scripting M-Pesa operations.

---

## Setup

Set your credentials as environment variables:

```bash
export SAFCOM_CONSUMER_KEY=your_key
export SAFCOM_CONSUMER_SECRET=your_secret
export SAFCOM_PASSKEY=your_passkey
export SAFCOM_SHORTCODE=174379
```

Or pass them as flags for each command (see below).

---

## Commands

### stkpush

Send an STK push to a phone.

```bash
# Minimal
safcom stkpush 254712345678 100

# With all options
safcom stkpush 254712345678 500 \
    --ref INV-001 \
    --desc "Payment for invoice INV-001" \
    --callback https://your-app.com/mpesa/callback \
    --key your_key \
    --secret your_secret \
    --passkey your_passkey \
    --shortcode 174379 \
    --env production
```

**Arguments:**

| Argument | Description |
|---|---|
| `phone` | Customer phone number (e.g. `254712345678`) |
| `amount` | Amount to charge in KES |

**Options:**

| Option | Default | Description |
|---|---|---|
| `--ref` | `INV-001` | Account reference visible to customer |
| `--desc` | *same as ref* | Transaction description |
| `--callback` | — | Callback URL for M-Pesa notification |
| `--key` | `SAFCOM_CONSUMER_KEY` | Consumer key |
| `--secret` | `SAFCOM_CONSUMER_SECRET` | Consumer secret |
| `--passkey` | `SAFCOM_PASSKEY` | Passkey |
| `--shortcode` | `SAFCOM_SHORTCODE` | Shortcode |
| `--env` | `sandbox` | Environment (`sandbox` or `production`) |

---

### query

Check the status of an STK push transaction.

```bash
safcom query ws_CO_202507202359590000
```

**Arguments:**

| Argument | Description |
|---|---|
| `checkout_id` | The `CheckoutRequestID` from the STK push response |

**Options:**

Same credential options as `stkpush`.

---

## Environment Variables

Instead of passing `--key`, `--secret`, `--passkey`, and `--shortcode` for every command, set these:

| Variable | Description |
|---|---|
| `SAFCOM_CONSUMER_KEY` | M-Pesa consumer key |
| `SAFCOM_CONSUMER_SECRET` | M-Pesa consumer secret |
| `SAFCOM_PASSKEY` | M-Pesa passkey |
| `SAFCOM_SHORTCODE` | M-Pesa shortcode |

If both a flag and an environment variable are provided, the flag takes precedence.
