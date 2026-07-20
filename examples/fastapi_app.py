"""FastAPI example: STK Push + callback handler.

Run:
    pip install safcom fastapi uvicorn
    uvicorn examples.fastapi_app:app --reload

Expose with ngrok:
    ngrok http 8000
    # Set callback URL to https://your-ngrok.ngrok.io/mpesa/callback
"""

import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from safcom import Mpesa
from safcom.callbacks import parse_stk_callback

app = FastAPI(title="safcom + FastAPI", version="0.1.0")

mpesa = Mpesa(
    consumer_key=os.environ["CONSUMER_KEY"],
    consumer_secret=os.environ["CONSUMER_SECRET"],
    passkey=os.environ["PASSKEY"],
    shortcode=os.environ.get("SHORTCODE", "174379"),
    env=os.environ.get("ENV", "sandbox"),
)
mpesa.set_callback_url(os.environ["CALLBACK_URL"])  # e.g. https://abc.ngrok.io/mpesa/callback


@app.post("/stkpush")
def charge_customer(phone: str, amount: int, reference: str = "INV-001"):
    """Send an STK push to a customer."""
    resp = mpesa.stk_push(
        phone=phone,
        amount=amount,
        account_ref=reference,
    )
    return {
        "success": True,
        "checkout_request_id": resp.checkout_request_id,
        "message": resp.customer_message,
    }


@app.post("/mpesa/callback")
async def mpesa_callback(request: Request):
    """Handle M-Pesa payment notifications."""
    body = await request.json()
    result = parse_stk_callback(body)

    if result.success:
        print(f"✅ Payment received: KES {result.amount}")
        print(f"   Receipt: {result.receipt}")
        print(f"   From: {result.phone}")
        # Update your database here
    else:
        print(f"❌ Payment failed: {result.result_description}")

    return {"ResultCode": 0, "ResultDesc": "Success"}


@app.get("/status/{checkout_id}")
def check_payment(checkout_id: str):
    """Poll the status of a payment."""
    status = mpesa.stk_push_query(checkout_id)
    return {
        "success": status.success,
        "receipt": status.receipt,
        "amount": status.amount,
        "phone": status.phone,
        "date": status.transaction_date.isoformat() if status.transaction_date else None,
        "result_description": status.result_description,
    }


@app.exception_handler(Exception)
def handle_error(request, exc):
    """Return clean error responses."""
    return JSONResponse(
        status_code=400,
        content={"success": False, "error": str(exc)},
    )
