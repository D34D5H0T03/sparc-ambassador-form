import os
from pathlib import Path

from django.conf import settings
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

TOKEN_PATH = Path(settings.BASE_DIR) / "token.json"

def _build_client_config():
    if not settings.DEV_GOOGLE_CLOUD_CLIENT_ID or not settings.DEV_GOOGLE_CLOUD_CLIENT_SECRET:
        raise RuntimeError(
            "Google Cloud OAuth client credentials are missing from settings/.env."
        )

    return {
        "web": {
            "client_id": settings.DEV_GOOGLE_CLOUD_CLIENT_ID,
            "project_id": settings.DEV_GOOGLE_CLOUD_PROJECT_ID,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": settings.DEV_GOOGLE_CLOUD_CLIENT_SECRET,
            "redirect_uris": [f"{settings.SITE_URL}/init/oauth2callback"],
        }
    }
    
def create_oauth_flow(state=None):
    if settings.DEBUG: # non-https transport for development
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

    redirect_uri = f"{settings.SITE_URL}/init/oauth2callback"
    flow = Flow.from_client_config(
        _build_client_config(),
        scopes=settings.DEV_SCOPES,
        state=state,
    )
    flow.redirect_uri = redirect_uri
    return flow

# save and get credentials from token.json
def save_credentials(creds):
    TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")


def get_credentials():
    if not TOKEN_PATH.exists():
        return None

    creds = Credentials.from_authorized_user_file(
        str(TOKEN_PATH),
        settings.DEV_SCOPES,
    )

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        save_credentials(creds)
        return creds

    return None 