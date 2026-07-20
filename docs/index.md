# safcom

<p align="center" style="font-size:1.3rem; color:#6366f1; margin-top:-0.5rem;">
  <strong>M-Pesa API — the way it should be.</strong>
</p>

---

## One line.

```python
from safcom import Mpesa

mpesa = Mpesa("consumer_key", "consumer_secret", "passkey", "174379")

# That's it. One line. STK push. Done.
resp = mpesa.stk_push(phone="254712345678", amount=100, account_ref="INV-001")
```

No raw JSON. No hunting for the right endpoint. No wondering why sandbox wants different keys than production. Just clean, typed Python.

---

## Why safcom?

The M-Pesa API is powerful but painful. Every Kenyan developer hits the same wall:

:material-close-circle: **Manual authentication** — Generate a token, track expiry, refresh. Every. Single. Time.

:material-close-circle: **Inconsistent responses** — Sandbox and production disagree on field names, error codes, and response shapes.

:material-close-circle: **Copy-paste code** — Every project starts by copying a Medium post from 2022 that's already outdated.

:material-check-circle: **safcom** fixes all of that. One package. One `pip install`. Sensible defaults. Clear errors. Done.

---

## Features

| Feature | Description |
|---|---|
| :material-cellphone: **STK Push** | Initiate Lipa Na M-Pesa Online payments in one call |
| :material-magnify: **Payment Query** | Check if a payment went through |
| :material-cash: **B2C** | Send money to customers |
| :material-scale-balance: **Account Balance** | Query your M-Pesa balance |
| :material-key: **Auto Auth** | Tokens refresh automatically, you never think about it |
| :material-code-json: **Typed Responses** | Every response is a dataclass, not a raw dict |
| :material-console: **CLI Included** | Test payments right from the terminal |
| :material-shield-check: **100% Private** | Your keys never leave your machine |

---

## Quick Install

```bash
pip install safcom
```

That's it. No extra dependencies to manage. No system requirements. **Works on every platform Python runs on.**

---

## Next Steps

- **Quickstart** — Get your first payment live in under 2 minutes. [Get started &rarr;](quickstart.md)
- **Tutorial** — Walk through every feature step by step. [Start the tutorial &rarr;](tutorial/)
- **API Reference** — Complete reference for the Mpesa client and all models. [Browse API docs &rarr;](api-reference/)
- **Guides** — Error handling, testing, common gotchas. [Read the guides &rarr;](guides/)

---

## License

MIT &mdash; use it freely in personal and commercial projects.
