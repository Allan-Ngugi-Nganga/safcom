# Going Live

Moving from sandbox to production is straightforward, but there are a few things you need to get right.

---

## 1. Get Production Credentials

Go to the [Safaricom Developer Portal](https://developer.safaricom.co.ke/):

1. Create a **production app** (or upgrade your sandbox app)
2. Subscribe to the APIs you need:
   - Lipa Na M-Pesa Online (STK Push)
   - B2C (if sending money)
   - Account Balance (if checking balance)
3. Note your production **Consumer Key**, **Consumer Secret**, and **Passkey**
4. Your **Shortcode** is your real Paybill/Till number

---

## 2. Update Your Code

The only change is the `env` parameter:

```python
# Sandbox
mpesa = Mpesa(
    consumer_key=...,
    consumer_secret=...,
    passkey=...,
    shortcode="174379",       # Sandbox shortcode
    env="sandbox",
)

# Production — same code, just change env and credentials
mpesa = Mpesa(
    consumer_key="prod_key",
    consumer_secret="prod_secret",
    passkey="prod_passkey",
    shortcode="123456",        # Your real Paybill number
    env="production",
)
```

!!! warning "Don't use env vars in your codebase"
    Never hardcode production credentials. Use environment variables:

    ```python
    import os

    mpesa = Mpesa(
        consumer_key=os.environ["MPESA_CONSUMER_KEY"],
        consumer_secret=os.environ["MPESA_CONSUMER_SECRET"],
        passkey=os.environ["MPESA_PASSKEY"],
        shortcode=os.environ["MPESA_SHORTCODE"],
        env=os.environ.get("MPESA_ENV", "sandbox"),
    )
    ```

---

## 3. Configure Callbacks

Your production callback URLs must be **publicly accessible** and use **HTTPS**:

```python
mpesa.set_callback_url("https://your-app.com/mpesa/callback")
```

Make sure your server:

- Responds with `200 OK` and `{"ResultCode": 0}` within **10 seconds**
- Is **idempotent** — M-Pesa may retry callbacks
- **Logs** every callback for debugging

---

## 4. Test with Small Amounts

Start with small transactions (KES 10–50) to verify everything works:

1. Send a test STK push to your own phone
2. Check the callback arrives at your server
3. Verify the payment query returns the correct status
4. Process a refund to verify B2C works
5. Monitor your logs for errors

---

## 5. Monitor Your Usage

Things to watch in production:

- **Callback failure rate** — if callbacks aren't arriving, check your server logs
- **STK Push success rate** — a high timeout rate may indicate network issues
- **Error rates** — watch for `APIError` exceptions in your error tracker
- **Transaction volumes** — M-Pesa has rate limits; don't exceed ~50 requests/second

---

## Common Production Issues

| Symptom | Likely Cause |
|---|---|
| Authentication fails | Wrong production consumer key/secret |
| STK push returns `1037` immediately | Wrong passkey |
| Callbacks not arriving | Server unreachable, or not returning 200 |
| B2C failing | Initiator credentials not configured |
| "Invalid shortcode" | Shortcode not subscribed to the API |

---

## Checklist

- [ ] Production credentials obtained from developer portal
- [ ] APIs subscribed in production app
- [ ] Callback URLs use HTTPS
- [ ] Server handles callbacks with 200 response
- [ ] Environment variables set for production credentials (not hardcoded)
- [ ] Tested with KES 10 to own number
- [ ] Error logging in place
- [ ] Monitoring set up for callback failures
