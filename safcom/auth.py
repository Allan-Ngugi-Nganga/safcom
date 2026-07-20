import datetime
import httpx
from safcom.exceptions import AuthError

BASE_URLS = {
    "sandbox": "https://sandbox.safaricom.co.ke",
    "production": "https://api.safaricom.co.ke",
}


class Auth:
    """Handles M-Pesa OAuth token generation with automatic refresh."""

    def __init__(self, consumer_key: str, consumer_secret: str, env: str = "sandbox"):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.base_url = BASE_URLS.get(env)
        if not self.base_url:
            raise ValueError(f"env must be 'sandbox' or 'production', got '{env}'")
        self._token: str | None = None
        self._expires_at: datetime.datetime | None = None

    @property
    def token(self) -> str:
        """Get a valid token, refreshing automatically if expired."""
        if self._token and self._expires_at and datetime.datetime.utcnow() < self._expires_at:
            return self._token
        return self._refresh()

    def _refresh(self) -> str:
        """Request a new OAuth token from the M-Pesa API."""
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        try:
            resp = httpx.get(url, auth=(self.consumer_key, self.consumer_secret), timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPStatusError as e:
            raise AuthError(f"Authentication failed: {e.response.status_code} {e.response.text}")
        except httpx.RequestError as e:
            raise AuthError(f"Could not reach M-Pesa API: {e}")

        token = data.get("access_token")
        if not token:
            raise AuthError(f"Unexpected auth response: {data}")

        # Token expires in 3600 seconds (1 hour) per M-Pesa docs
        expires_in = data.get("expires_in", 3600)
        self._token = token
        self._expires_at = datetime.datetime.utcnow() + datetime.timedelta(
            seconds=int(expires_in) - 60  # 60s buffer
        )
        return self._token
