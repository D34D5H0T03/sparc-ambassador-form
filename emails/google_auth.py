import os
from pathlib import Path

from django.conf import settings
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

from .constants import (
    DEFAULT_GMAIL_SCOPE,
    GOOGLE_AUTH_URI,
    GOOGLE_CERTS_URI,
    GOOGLE_TOKEN_URI,
    OAUTH_CALLBACK_PATH,
    TOKEN_FILENAME,
)

TOKEN_PATH = Path(settings.BASE_DIR) / TOKEN_FILENAME


def _build_client_config():
    client_id = getattr(settings, "DEV_GOOGLE_CLOUD_CLIENT_ID", "")
    client_secret = getattr(settings, "DEV_GOOGLE_CLOUD_CLIENT_SECRET", "")
    project_id = getattr(settings, "DEV_GOOGLE_CLOUD_PROJECT_ID", "")

    if not client_id or not client_secret:
        raise RuntimeError(
            "Google Cloud OAuth client credentials are missing from settings/.env."
        )

    return {
        "web": {
            "client_id": client_id,
            "project_id": project_id,
            "auth_uri": GOOGLE_AUTH_URI,
            "token_uri": GOOGLE_TOKEN_URI,
            "auth_provider_x509_cert_url": GOOGLE_CERTS_URI,
            "client_secret": client_secret,
            "redirect_uris": [f"{settings.SITE_URL}{OAUTH_CALLBACK_PATH}"],
        }
    }


def create_oauth_flow(state=None):
    if settings.DEBUG:
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

    scopes = getattr(settings, "DEV_SCOPES", [DEFAULT_GMAIL_SCOPE])
    redirect_uri = f"{settings.SITE_URL}{OAUTH_CALLBACK_PATH}"

    flow = Flow.from_client_config(
        _build_client_config(),
        scopes=scopes,
        state=state,
    )
    flow.redirect_uri = redirect_uri
    return flow


def save_credentials(creds):
    TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")


def get_credentials():
    if not TOKEN_PATH.exists():
        return None

    scopes = getattr(settings, "DEV_SCOPES", [DEFAULT_GMAIL_SCOPE])
    creds = Credentials.from_authorized_user_file(
        str(TOKEN_PATH),
        scopes,
    )

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        save_credentials(creds)
        return creds

    return None