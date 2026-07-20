"""Callback parsing utilities for M-Pesa notifications.

M-Pesa sends transaction results to your callback URL as POST requests.
This module provides helpers to parse those callbacks into typed Python objects.
"""

from datetime import datetime
from typing import Any

from safcom.exceptions import APIError
from safcom.models import STKPushStatus


def parse_stk_callback(body: dict[str, Any]) -> STKPushStatus:
    """Parse an STK Push callback payload from M-Pesa.

    Call this inside your webhook handler when M-Pesa POSTs a payment
    notification to your callback URL.

    Args:
        body: The full JSON payload received from M-Pesa. Must contain
            the ``Body.stkCallback`` structure.

    Returns:
        An ``STKPushStatus`` with the parsed transaction result.
        Check ``status.success`` to determine if payment went through.

    Raises:
        APIError: If the callback payload is malformed or missing
            required fields.

    Example:
        .. code-block:: python

            @app.post(\"/mpesa/callback\")
            async def handle_callback(request):
                body = await request.json()
                result = parse_stk_callback(body)

                if result.success:
                    print(f\"✅ Paid KES {result.amount} — {result.receipt}\")
                else:
                    print(f\"❌ Failed: {result.result_description}\")

                return {\"ResultCode\": 0, \"ResultDesc\": \"Success\"}
    """
    try:
        stk = body["Body"]["stkCallback"]
    except (KeyError, TypeError):
        raise APIError(
            "Invalid callback payload: missing Body.stkCallback structure. "
            "Make sure you're passing the full M-Pesa POST body."
        )

    checkout_request_id = stk.get("CheckoutRequestID", "")
    merchant_request_id = stk.get("MerchantRequestID", "")
    result_code = str(stk.get("ResultCode", ""))
    result_description = stk.get("ResultDesc", "")

    # Parse metadata items if present
    amount = None
    receipt = None
    phone = None
    transaction_date = None

    metadata = stk.get("CallbackMetadata")
    if metadata and isinstance(metadata, dict):
        items = metadata.get("Item", [])
        if isinstance(items, list):
            for item in items:
                name = item.get("Name", "")
                value = item.get("Value")
                if name == "Amount":
                    amount = float(value) if value is not None else None
                elif name == "MpesaReceiptNumber":
                    receipt = str(value) if value else None
                elif name == "PhoneNumber":
                    phone = str(value) if value else None
                elif name == "TransactionDate":
                    if value:
                        try:
                            transaction_date = datetime.strptime(
                                str(value), "%Y%m%d%H%M%S"
                            )
                        except (ValueError, TypeError):
                            pass

    return STKPushStatus(
        response_code="0" if result_code == "0" else result_code,
        response_description=(
            "Success" if result_code == "0" else (result_description or "Failed")
        ),
        merchant_request_id=merchant_request_id,
        checkout_request_id=checkout_request_id,
        result_code=result_code,
        result_description=result_description,
        amount=amount,
        receipt=receipt,
        transaction_date=transaction_date,
        phone=phone,
        raw=body,
    )


def extract_payment_info(result: STKPushStatus) -> dict[str, Any]:
    """Extract a clean payment summary from a callback result.

    Useful for logging, database storage, or API responses.

    Args:
        result: An ``STKPushStatus`` returned by ``parse_stk_callback()``.

    Returns:
        A dictionary with cleaned-up payment info.

    Example:
        >>> info = extract_payment_info(status)
        >>> info[\"paid\"]
        True
        >>> info[\"receipt\"]
        'NLJ91HA6ES'
    """
    return {
        "paid": result.success,
        "receipt": result.receipt,
        "amount": result.amount,
        "phone": result.phone,
        "date": result.transaction_date.isoformat() if result.transaction_date else None,
        "checkout_request_id": result.checkout_request_id,
        "result_code": result.result_code,
        "result_description": result.result_description,
    }
