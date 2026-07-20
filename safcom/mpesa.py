import base64
import datetime
import httpx
from typing import Callable

from safcom.auth import Auth, BASE_URLS
from safcom.exceptions import APIError, ValidationError
from safcom.models import (
    STKPushResponse,
    STKPushStatus,
    B2CResponse,
    AccountBalanceResponse,
)


class Mpesa:
    """M-Pesa API client.

    Usage:
        from safcom import Mpesa

        mpesa = Mpesa(
            consumer_key="your_key",
            consumer_secret="your_secret",
            passkey="your_passkey",
            shortcode="174379",
            env="sandbox"
        )

        response = mpesa.stk_push(
            phone="254712345678",
            amount=100,
            account_ref="INV-001",
        )
    """

    def __init__(
        self,
        consumer_key: str,
        consumer_secret: str,
        passkey: str,
        shortcode: str,
        env: str = "sandbox",
    ):
        if env not in ("sandbox", "production"):
            raise ValueError(f"env must be 'sandbox' or 'production', got '{env}'")

        self.shortcode = shortcode
        self.passkey = passkey
        self.env = env
        self.base_url = BASE_URLS[env]
        self._auth = Auth(consumer_key, consumer_secret, env)
        self._callback_url: str | None = None

    @property
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._auth.token}",
            "Content-Type": "application/json",
        }

    # ── Configuration ──────────────────────────────────────────────

    def set_callback_url(self, url: str) -> None:
        """Set the default callback URL for transaction notifications."""
        self._callback_url = url

    # ── STK Push (Lipa Na M-Pesa Online) ──────────────────────────

    def stk_push(
        self,
        phone: str,
        amount: float,
        account_ref: str,
        transaction_desc: str | None = None,
        callback_url: str | None = None,
    ) -> STKPushResponse:
        """Initiate an STK push to a customer's phone.

        Args:
            phone: Customer phone number (e.g. 254712345678).
            amount: Amount to charge.
            account_ref: Account reference visible to the customer.
            transaction_desc: Optional description (defaults to account_ref).
            callback_url: Override the default callback URL for this request.

        Returns:
            STKPushResponse with checkout details.

        Raises:
            ValidationError: If input validation fails.
            APIError: If the API returns an error.
        """
        phone = self._normalise_phone(phone)
        if amount <= 0:
            raise ValidationError("amount must be greater than 0")
        if not account_ref or len(account_ref) > 12:
            raise ValidationError("account_ref must be 1–12 characters")

        timestamp = self._timestamp()
        password = self._password(timestamp)
        callback = callback_url or self._callback_url

        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(round(amount)),
            "PartyA": phone,
            "PartyB": self.shortcode,
            "PhoneNumber": phone,
            "CallBackURL": callback or "",
            "AccountReference": account_ref,
            "TransactionDesc": transaction_desc or account_ref,
        }

        resp = self._post("/mpesa/stkpush/v1/processrequest", payload)
        return STKPushResponse(
            merchant_request_id=resp.get("MerchantRequestID", ""),
            checkout_request_id=resp.get("CheckoutRequestID", ""),
            response_code=resp.get("ResponseCode", ""),
            response_description=resp.get("ResponseDescription", ""),
            customer_message=resp.get("CustomerMessage", ""),
            raw=resp,
        )

    def stk_push_query(self, checkout_request_id: str) -> STKPushStatus:
        """Query the status of an STK push transaction.

        Args:
            checkout_request_id: The CheckoutRequestID from stk_push().

        Returns:
            STKPushStatus with transaction details.
        """
        timestamp = self._timestamp()
        password = self._password(timestamp)

        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id,
        }

        resp = self._post("/mpesa/stkpushquery/v1/query", payload)

        date_str = resp.get("TransactionDate", "")
        transaction_date = None
        if date_str:
            try:
                transaction_date = datetime.datetime.strptime(str(date_str), "%Y%m%d%H%M%S")
            except ValueError:
                pass

        return STKPushStatus(
            response_code=resp.get("ResponseCode", ""),
            response_description=resp.get("ResponseDescription", ""),
            merchant_request_id=resp.get("MerchantRequestID", ""),
            checkout_request_id=resp.get("CheckoutRequestID", ""),
            result_code=resp.get("ResultCode"),
            result_description=resp.get("ResultDesc"),
            amount=float(resp["Amount"]) if resp.get("Amount") else None,
            receipt=resp.get("MpesaReceiptNumber"),
            transaction_date=transaction_date,
            phone=resp.get("PhoneNumber"),
            raw=resp,
        )

    # ── B2C (Send money to customer) ──────────────────────────────

    def b2c(
        self,
        phone: str,
        amount: float,
        remarks: str = "payment",
        initiator_name: str = "testapi",
        security_credential: str = "",
        occasion: str = "",
    ) -> B2CResponse:
        """Send money to a customer (B2C payment).

        Args:
            phone: Recipient phone number (e.g. 254712345678).
            amount: Amount to send.
            remarks: Optional remark.
            initiator_name: API initiator name (configured in M-Pesa portal).
            security_credential: Encrypted security credential.
            occasion: Optional occasion field.

        Returns:
            B2CResponse with conversation details.
        """
        phone = self._normalise_phone(phone)
        if amount <= 0:
            raise ValidationError("amount must be greater than 0")

        payload = {
            "InitiatorName": initiator_name,
            "SecurityCredential": security_credential,
            "CommandID": "BusinessPayment",
            "Amount": int(round(amount)),
            "PartyA": self.shortcode,
            "PartyB": phone,
            "Remarks": remarks,
            "QueueTimeOutURL": self._callback_url or "",
            "ResultURL": self._callback_url or "",
            "Occasion": occasion or "",
        }

        resp = self._post("/mpesa/b2c/v3/paymentrequest", payload)
        return B2CResponse(
            conversation_id=resp.get("ConversationID", ""),
            originator_conversation_id=resp.get("OriginatorConversationID", ""),
            response_code=resp.get("ResponseCode", ""),
            response_description=resp.get("ResponseDescription", ""),
            raw=resp,
        )

    # ── Account Balance ──────────────────────────────────────────

    def account_balance(
        self,
        initiator_name: str = "testapi",
        security_credential: str = "",
    ) -> AccountBalanceResponse:
        """Query M-Pesa account balance.

        Args:
            initiator_name: API initiator name (configured in M-Pesa portal).
            security_credential: Encrypted security credential.

        Returns:
            AccountBalanceResponse with conversation details.
        """
        payload = {
            "InitiatorName": initiator_name,
            "SecurityCredential": security_credential,
            "CommandID": "AccountBalance",
            "PartyA": self.shortcode,
            "IdentifierType": "4",
            "QueueTimeOutURL": self._callback_url or "",
            "ResultURL": self._callback_url or "",
        }

        resp = self._post("/mpesa/accountbalance/v1/query", payload)
        return AccountBalanceResponse(
            conversation_id=resp.get("ConversationID", ""),
            originator_conversation_id=resp.get("OriginatorConversationID", ""),
            response_code=resp.get("ResponseCode", ""),
            response_description=resp.get("ResponseDescription", ""),
            raw=resp,
        )

    # ── Helpers ──────────────────────────────────────────────────

    def _post(self, path: str, payload: dict) -> dict:
        url = f"{self.base_url}{path}"
        try:
            resp = httpx.post(url, json=payload, headers=self._headers, timeout=30)
            data = resp.json()
        except httpx.HTTPStatusError as e:
            raise APIError(f"HTTP {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            raise APIError(f"Request failed: {e}")
        except ValueError:
            raise APIError(f"Non-JSON response: {resp.text}")

        # M-Pesa returns ResponseCode in various places
        error_code = data.get("ResponseCode")
        if error_code and error_code != "0":
            raise APIError(
                message=data.get("ResponseDescription", "M-Pesa API error"),
                response_code=error_code,
            )

        return data

    @staticmethod
    def _normalise_phone(phone: str) -> str:
        """Normalise a Kenyan phone number to 254 format."""
        cleaned = phone.strip().replace(" ", "").replace("-", "")
        if cleaned.startswith("+"):
            cleaned = cleaned[1:]
        if cleaned.startswith("0"):
            cleaned = "254" + cleaned[1:]
        if not cleaned.startswith("254"):
            raise ValidationError(
                f"Phone number must start with 254 or 0, got '{phone}'"
            )
        if len(cleaned) != 12:
            raise ValidationError(
                f"Phone number must be 12 digits in 254 format, got {len(cleaned)} digits"
            )
        return cleaned

    def _timestamp(self) -> str:
        return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    def _password(self, timestamp: str) -> str:
        raw = f"{self.shortcode}{self.passkey}{timestamp}"
        return base64.b64encode(raw.encode()).decode()
