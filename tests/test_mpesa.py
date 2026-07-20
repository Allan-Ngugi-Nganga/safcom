"""Tests for safcom M-Pesa client."""

import pytest
from safcom import Mpesa, ValidationError


@pytest.fixture
def mpesa():
    return Mpesa(
        consumer_key="test_key",
        consumer_secret="test_secret",
        passkey="test_passkey",
        shortcode="174379",
        env="sandbox",
    )


class TestNormalisePhone:
    def test_0712345678(self, mpesa):
        assert mpesa._normalise_phone("0712345678") == "254712345678"

    def test_254712345678(self, mpesa):
        assert mpesa._normalise_phone("254712345678") == "254712345678"

    def test_plus254712345678(self, mpesa):
        assert mpesa._normalise_phone("+254712345678") == "254712345678"

    def test_with_spaces(self, mpesa):
        assert mpesa._normalise_phone("254 712 345 678") == "254712345678"

    def test_with_hyphens(self, mpesa):
        assert mpesa._normalise_phone("254-712-345-678") == "254712345678"

    def test_invalid_short(self, mpesa):
        with pytest.raises(ValidationError):
            mpesa._normalise_phone("712345678")

    def test_invalid_prefix(self, mpesa):
        with pytest.raises(ValidationError):
            mpesa._normalise_phone("11234567890")


class TestSTKPushValidation:
    def test_negative_amount(self, mpesa):
        with pytest.raises(ValidationError, match="amount must be greater than 0"):
            mpesa.stk_push(phone="254712345678", amount=-100, account_ref="test")

    def test_zero_amount(self, mpesa):
        with pytest.raises(ValidationError, match="amount must be greater than 0"):
            mpesa.stk_push(phone="254712345678", amount=0, account_ref="test")

    def test_long_account_ref(self, mpesa):
        with pytest.raises(ValidationError, match="account_ref must be 1–12 characters"):
            mpesa.stk_push(phone="254712345678", amount=100, account_ref="X" * 13)


class TestPassword:
    def test_password_format(self, mpesa):
        password = mpesa._password("20250720235959")
        assert isinstance(password, str)
        assert len(password) > 0


class TestTimestamp:
    def test_timestamp_format(self, mpesa):
        ts = mpesa._timestamp()
        assert len(ts) == 14
        assert ts.isdigit()
