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
        """Set the default callback URL for M-Pesa transaction notifications.

        All subsequent STK Push requests will use this URL unless
        overridden per-request with the ``callback_url`` parameter.

        Args:
            url: Public HTTPS URL where M-Pesa will POST transaction
                results. Must be reachable from the internet.
        """
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
        """Send a payment request to a customer's phone.

        The customer receives an M-Pesa PIN prompt on their phone.
        They enter their PIN and the money moves instantly.
        This is known as Lipa Na M-Pesa Online.

        A successful response only means M-Pesa *received* the request.
        Use ``stk_push_query()`` or set up a callback URL to learn
        whether the customer actually paid.

        Args:
            phone: Customer's phone number. Accepts any format —
                ``0712345678``, ``254712345678``, ``+254712345678``,
                or with spaces/dashes. All get normalised to
                ``254712345678`` automatically.
            amount: Amount to charge in KES. Must be greater than 0.
            account_ref: Short reference visible to the customer on
                their M-Pesa screen. Maximum 12 characters.
            transaction_desc: Optional description. Defaults to the
                value of ``account_ref`` if not provided.
            callback_url: Override the default callback URL for this
                request only. If not provided, the URL set via
                ``set_callback_url()`` is used.

        Returns:
            STKPushResponse with the ``checkout_request_id``.
            Save this ID — you'll need it to query the payment
            status later.

        Raises:
            ValidationError: If the phone number is invalid,
                amount is not positive, or account_ref is too long.
            APIError: If the M-Pesa API returns an error.

        Example:
            >>> resp = mpesa.stk_push(
            ...     phone="254712345678",
            ...     amount=500,
            ...     account_ref="INV-001",
            ... )
            >>> resp.checkout_request_id
            'ws_CO_202507202359590000'
            >>> resp.customer_message
            'Please enter your M-Pesa PIN'
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
        """Check whether an STK push payment went through.

        Use this to poll for the final status after sending an STK push.
        The customer needs time to enter their PIN — wait at least 5
        seconds before the first query.

        Args:
            checkout_request_id: The ``checkout_request_id`` returned
                by ``stk_push()``.

        Returns:
            STKPushStatus with the transaction result. Check
            ``status.success`` (``True`` if payment completed) or
            ``status.result_code`` for details (e.g. ``"1037"`` for
            timeout, ``"1032"`` for cancelled).

        Raises:
            APIError: If the M-Pesa API returns an error.

        Example:
            >>> status = mpesa.stk_push_query("ws_CO_202507202359590000")
            >>> status.success
            True
            >>> status.receipt
            'NLJ91HA6ES'
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
        """Send money from your business to a customer.

        Used for refunds, payouts, and rewards. Requires B2C API
        enabled and initiator credentials configured in the M-Pesa
        org portal.

        Args:
            phone: Recipient phone number. Accepts any format
                (``0712...``, ``254712...``, ``+254712...``).
            amount: Amount to send in KES.
            remarks: Reason for the payment. Shows in the customer's
                M-Pesa statement.
            initiator_name: The API initiator username configured in
                your M-Pesa org portal.
            security_credential: Base64-encrypted initiator password.
                Generate this using Safaricom's provided tool.
            occasion: Optional field (e.g. for promotions).

        Returns:
            B2CResponse with the ``conversation_id`` for tracking.
            The actual result arrives via callback to your
            ``ResultURL``.

        Raises:
            ValidationError: If the phone number or amount is invalid.
            APIError: If the M-Pesa API returns an error.
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
        """Query your M-Pesa account balance.

        Sends a balance inquiry request. The actual balance information
        arrives via callback to your ``ResultURL``.

        Args:
            initiator_name: The API initiator username configured in
                your M-Pesa org portal.
            security_credential: Base64-encrypted initiator password.
                Generate this using Safaricom's provided tool.

        Returns:
            AccountBalanceResponse confirming the request was received.
            Balance details arrive via callback to your ResultURL.

        Raises:
            APIError: If the M-Pesa API returns an error.
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
        """Send a POST request to the M-Pesa API."""
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
        """Normalise a Kenyan phone number to 254 format.

        Accepts:
            ``0712345678`` → ``254712345678``
            ``254712345678`` → ``254712345678``
            ``+254712345678`` → ``254712345678``
            ``254 712 345 678`` → ``254712345678``
        """
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
        """Generate M-Pesa timestamp in YYYYMMDDHHMMSS format."""
        return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    def _password(self, timestamp: str) -> str:
        """Generate base64-encoded password for M-Pesa requests."""
        raw = f"{self.shortcode}{self.passkey}{timestamp}"
        return base64.b64encode(raw.encode()).decode()
