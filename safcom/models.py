from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class STKPushResponse:
    """Response from an STK push request."""
    merchant_request_id: str
    checkout_request_id: str
    response_code: str
    response_description: str
    customer_message: str
    raw: dict = field(repr=False)


@dataclass
class STKPushStatus:
    """Status of a completed STK push transaction."""
    response_code: str
    response_description: str
    merchant_request_id: str
    checkout_request_id: str
    result_code: str | None = None
    result_description: str | None = None
    amount: float | None = None
    receipt: str | None = None
    transaction_date: datetime | None = None
    phone: str | None = None
    raw: dict = field(default_factory=dict, repr=False)

    @property
    def success(self) -> bool:
        return self.result_code == "0"


@dataclass
class B2CResponse:
    """Response from a B2C (send money) request."""
    conversation_id: str
    originator_conversation_id: str
    response_code: str
    response_description: str
    raw: dict = field(repr=False)


@dataclass
class AccountBalanceResponse:
    """Response from an account balance request."""
    conversation_id: str
    originator_conversation_id: str
    response_code: str
    response_description: str
    raw: dict = field(repr=False)
