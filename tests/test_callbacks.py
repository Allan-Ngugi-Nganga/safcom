"""Tests for safcom callback parser."""

import pytest
from datetime import datetime
from safcom.callbacks import parse_stk_callback, extract_payment_info
from safcom.exceptions import APIError


def make_callback(
    result_code: str = "0",
    result_desc: str = "The service request is processed successfully.",
    amount: float | None = 100.0,
    receipt: str = "NLJ91HA6ES",
    phone: str = "254712345678",
    date: str = "20250720235959",
) -> dict:
    """Build a sample M-Pesa callback payload for testing."""
    body = {
        "Body": {
            "stkCallback": {
                "MerchantRequestID": "23070-43918244-1",
                "CheckoutRequestID": "ws_CO_202507202359590000",
                "ResultCode": result_code,
                "ResultDesc": result_desc,
            }
        }
    }

    if result_code == "0":
        body["Body"]["stkCallback"]["CallbackMetadata"] = {
            "Item": [
                {"Name": "Amount", "Value": amount},
                {"Name": "MpesaReceiptNumber", "Value": receipt},
                {"Name": "TransactionDate", "Value": date},
                {"Name": "PhoneNumber", "Value": phone},
            ]
        }

    return body


class TestParseStkCallback:
    def test_successful_payment(self):
        body = make_callback()
        result = parse_stk_callback(body)

        assert result.success is True
        assert result.receipt == "NLJ91HA6ES"
        assert result.amount == 100.0
        assert result.phone == "254712345678"
        assert result.checkout_request_id == "ws_CO_202507202359590000"
        assert isinstance(result.transaction_date, datetime)

    def test_failed_payment(self):
        body = make_callback(
            result_code="1037",
            result_desc="Request cancelled by user",
            amount=None,
            receipt=None,
            phone=None,
        )
        result = parse_stk_callback(body)

        assert result.success is False
        assert result.receipt is None
        assert result.amount is None
        assert result.result_code == "1037"
        assert result.result_description == "Request cancelled by user"

    def test_insufficient_balance(self):
        body = make_callback(result_code="1", result_desc="Insufficient balance")
        result = parse_stk_callback(body)

        assert result.success is False
        assert result.result_code == "1"

    def test_timeout(self):
        body = make_callback(result_code="1037", result_desc="Request timeout")
        result = parse_stk_callback(body)

        assert result.success is False
        assert result.result_code == "1037"

    def test_invalid_payload_missing_body(self):
        with pytest.raises(APIError, match="Invalid callback payload"):
            parse_stk_callback({})

    def test_invalid_payload_none(self):
        with pytest.raises(APIError):
            parse_stk_callback(None)  # type: ignore


class TestExtractPaymentInfo:
    def test_successful_payment(self):
        body = make_callback()
        result = parse_stk_callback(body)
        info = extract_payment_info(result)

        assert info["paid"] is True
        assert info["receipt"] == "NLJ91HA6ES"
        assert info["amount"] == 100.0
        assert info["phone"] == "254712345678"
        assert info["date"] is not None

    def test_failed_payment(self):
        body = make_callback(result_code="1037", result_desc="Cancelled")
        result = parse_stk_callback(body)
        info = extract_payment_info(result)

        assert info["paid"] is False
        assert info["receipt"] is None
        assert info["date"] is None
