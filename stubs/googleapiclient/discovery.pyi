from typing import Any

from google.auth.external_account_authorized_user import (
    Credentials as ExternalCredentials,
)
from google.oauth2.credentials import Credentials as OAuthCredentials

def build(
    serviceName: str, version: str, credentials: OAuthCredentials | ExternalCredentials
) -> Any: ...
