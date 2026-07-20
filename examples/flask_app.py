"""Flask example: STK Push + callback handler.

Run:
    pip install safcom flask
    python examples/flask_app.py

Expose with ngrok:
    ngrok http 5000
    # Set callback URL to https://your-ngrok.ngrok.io/mpesa/callback
"""

import os
from flask import Flask, request, jsonify

from safcom import Mpesa
from safcom.callbacks import parse_stk_callback

app = Flask(__name__)

mpesa = Mpesa(
    consumer_key=os.environ["CONSUMER_KEY"],
    consumer_secret=os.environ["CONSUMER_SECRET"],
    passkey=os.environ["PASSKEY"],
    shortcode=os.environ.get("SHORTCODE", "174379"),
    env=os.environ.get("ENV", "sandbox"),
)
mpesa.set_callback_url(os.environ["CALLBACK_URL"])


@app.route("/stkpush", methods=["POST"])
def charge_customer():
    """Send an STK push to a customer."""
    data = request.get_json()
    resp = mpesa.stk_push(
        phone=data["phone"],
        amount=data["amount"],
        account_ref=data.get("reference", "INV-001"),
    )
    return jsonify(
        success=True,
        checkout_request_id=resp.checkout_request_id,
        message=resp.customer_message,
    )


@app.route("/mpesa/callback", methods=["POST"])
def mpesa_callback():
    """Handle M-Pesa payment notifications."""
    body = request.get_json()
    result = parse_stk_callback(body)

    if result.success:
        print(f"✅ Payment received: KES {result.amount}")
        print(f"   Receipt: {result.receipt}")
        print(f"   From: {result.phone}")
        # Update your database here
    else:
        print(f"❌ Payment failed: {result.result_description}")

    return jsonify(ResultCode=0, ResultDesc="Success")


@app.route("/status/<checkout_id>")
def check_payment(checkout_id):
    """Poll the status of a payment."""
    status = mpesa.stk_push_query(checkout_id)
    return jsonify(
        success=status.success,
        receipt=status.receipt,
        amount=status.amount,
        phone=status.phone,
        date=status.transaction_date.isoformat() if status.transaction_date else None,
        result_description=status.result_description,
    )


@app.errorhandler(Exception)
def handle_error(exc):
    return jsonify(success=False, error=str(exc)), 400


if __name__ == "__main__":
    app.run(debug=True, port=5000)
