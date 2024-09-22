from typing import Any

from google.auth.external_account_authorized_user import (
    Credentials as ExternalCredentials,
)
from google.oauth2.credentials import Credentials as OAuthCredentials

class Flow:
    @classmethod
    def from_client_config(
        cls, client_config: dict[str, Any], scopes: list[str], **kwargs: Any
    ) -> "Flow":
        pass
    def authorization_url(self, **kwargs: str) -> tuple[str, Any]:
        pass
    def fetch_token(self, **kwargs: str) -> None:
        pass
    state: Any
    credentials: OAuthCredentials | ExternalCredentials
