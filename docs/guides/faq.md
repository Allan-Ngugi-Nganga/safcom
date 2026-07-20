# FAQ

## General

### What Python version do I need?

Python 3.10 or higher.

### Does safcom work on Windows?

Yes. And macOS, and Linux. Anywhere Python runs.

### Does safcom send my data anywhere?

No. safcom communicates directly with the M-Pesa API using credentials you provide. Your consumer key, secret, and passkey never leave your machine.

### Is safcom free?

Yes. safcom is open source under the MIT license. You only pay M-Pesa transaction fees (normal M-Pesa rates).

---

## STK Push

### The customer didn't get the PIN prompt. Why?

A few things to check:

1. **Phone number format** — Make sure it's in `254` format: `254712345678` (12 digits total)
2. **Network** — The customer's phone needs Safaricom network signal
3. **API subscription** — Make sure your app is subscribed to "Lipa Na M-Pesa Online" on the developer portal
4. **Shortcode** — Use `174379` for sandbox, your Paybill number for production

### The STK Push succeeded but the payment failed. Why?

A successful STK Push response means M-Pesa **received** your request. The customer still needs to enter their PIN on their phone. Common failures:

- **1037** — Customer didn't respond in time (30 seconds)
- **1032** — Customer cancelled the request
- **1** — Insufficient balance

Use [Payment Query](../tutorial/query-status.md) or a [Callback](../tutorial/stk-push.md#setting-up-callbacks) to check the final status.

### How do I check if a payment went through?

Use `stk_push_query(checkout_request_id)` or set up a callback URL. See the [Payment Status tutorial](../tutorial/query-status.md) for both approaches.

### How long should I wait before querying?

Wait at least 5 seconds before the first query. If the result isn't ready, wait 3-5 seconds between retries. M-Pesa usually processes payments within 15-30 seconds.

---

## B2C

### What's an initiator name?

The initiator is a username configured in the M-Pesa portal that has permission to send B2C transactions. You set it up on the M-Pesa org portal, not on the developer portal.

### What's a security credential?

A base64-encrypted version of your initiator password. Safaricom provides a tool to generate this.

---

## Production

### What changes when I move to production?

The only code change is `env="production"` and using your real credentials. But you need:

- Real Paybill/Till number for your shortcode
- Production consumer key and secret from the developer portal
- HTTPS callback URLs
- Callback server that responds within 10 seconds

### Can I use the same credentials for sandbox and production?

No. Sandbox and production use different consumer keys, secrets, and shortcodes.

### How fast are M-Pesa payments?

STK pushes usually complete within 15-30 seconds. B2C payments can take 1-5 minutes.

### Are there rate limits?

Yes. M-Pesa recommends no more than ~50 requests per second. Most applications won't hit this limit.

---

## Errors

### I got "Authentication failed: 401". What now?

Your consumer key or secret is wrong for the environment you're targeting. Check:

- Are you using sandbox credentials with `env="production"`?
- Is the API subscribed to your app?
- Has your consumer key been revoked?

### I got a 500 Internal Server Error from M-Pesa

This is a server-side issue on M-Pesa's end. Retry after a few seconds. If it persists, check the [Safaricom status page](https://developer.safaricom.co.ke/status) for outages.

### The callback isn't arriving

Check:

- Is your server publicly accessible? (Use a tool like ngrok for local testing)
- Is your callback URL using HTTPS? M-Pesa requires HTTPS in production
- Is your server returning `200 OK` with `{"ResultCode": 0}` within 10 seconds?
- Check your server logs for incoming requests
