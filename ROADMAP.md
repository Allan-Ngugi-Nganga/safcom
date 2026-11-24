# safcom roadmap

Where the library is going, and why each step earns its place. Nothing here is
speculative work for its own sake: every item removes a real cost that a user of
`pip install safcom` pays today.

## Where 0.1.0 stands

- 11 synchronous methods on a single `Mpesa` class.
- Every call does `httpx.post(...)` at module level, so each request opens a new
  connection and re-sends headers, with nowhere to hang a shared timeout policy.
- 10 type annotations across 391 lines. No `py.typed`, so an IDE cannot type-check
  against the package it installed.
- Tests mock at the network boundary by patching.
- No lint, type or coverage gate in CI. The only workflow builds the docs.

## 0.1.1: typing and a client that is reused

1. **Hold a client on the instance.** One `httpx.Client` per `Mpesa`, created in
   `__init__` and closed by a context manager. Connection reuse, one timeout
   policy, and headers set in one place instead of per call.
2. **Annotate the public surface.** Return types on every method, `TypedDict`s for
   request payloads, `Literal` for `env`, and a model per response.
3. **Ship `py.typed`** so a user on mypy or pyright gets the types, not `Any`.
4. **`mypy --strict` and `ruff` in CI**, and a coverage floor of 90% on the
   package. A library whose whole job is being trusted earns a gate.

## 0.2.0: an async client that shares everything

5. **`AsyncMpesa`** with the same methods on `httpx.AsyncClient`. Payload builders,
   auth token caching and response models are shared with the sync class, so the
   two cannot drift: one implementation of each request, two ways to send it.
6. **Tests on `httpx.MockTransport`**, which exercises both clients through the
   same handler and removes the patch-the-network style that hides bugs.
7. **A matrix across Python 3.10 to 3.13** on every push.

## After that

8. **A benchmark in the README**: 100 sequential STK pushes against a mock
   transport, sync against async, with the harness committed so the number can be
   reproduced. A performance claim without a script is a rumour.
9. **Retries with backoff on 429 and 5xx**, opt-in, because M-Pesa rate limits are
   real and every user currently writes the same loop.

## What this is not

Not a rewrite. The API a user calls does not change between 0.1 and 0.2: same
method names, same arguments, same exceptions. The work is underneath, which is
the point of a wrapper library.
