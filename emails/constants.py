# Database Field Lengths & Log Truncation
MAX_CAMPAIGN_LENGTH = 40
MAX_STATUS_LENGTH = 10
MAX_GMAIL_MESSAGE_ID_LENGTH = 64
MAX_ERROR_LOG_LENGTH = 500

# Campaign & Subject Defaults
CAMPAIGN_AMBASSADOR_RECEIVED = "ambassador_received"
SUBJECT_APPLICATION_RECEIVED = "SPARC 2026 - Ambassador Application Received"

# Google OAuth 2.0 & Gmail API Configuration
TOKEN_FILENAME = "token.json"
OAUTH_INIT_PATH = "/init/oauth2/"
OAUTH_CALLBACK_PATH = "/init/oauth2callback"
GOOGLE_AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URI = "https://oauth2.googleapis.com/token"
GOOGLE_CERTS_URI = "https://www.googleapis.com/oauth2/v1/certs"
DEFAULT_GMAIL_SCOPE = "https://www.googleapis.com/auth/gmail.send"
GMAIL_USER_ID = "me"

# OAuth Authorization Query Parameters
OAUTH_ACCESS_TYPE = "offline"
OAUTH_INCLUDE_GRANTED_SCOPES = "true"
OAUTH_PROMPT = "consent"

# Session Keys
SESSION_OAUTH_STATE_KEY = "google_oauth_state"
SESSION_OAUTH_VERIFIER_KEY = "google_oauth_code_verifier"

# Email Templates & Static Assets
TEMPLATE_RECEIVED_HTML = "emails/ambassador_received.html"
TEMPLATE_RECEIVED_TXT = "emails/ambassador_received.txt"
STATIC_LOGO_PATH = "/static/images/SPARC26LogoMin.png"
LOCAL_HOSTS = ("localhost", "127.0.0.1")

# Retry Management Command Defaults
DEFAULT_RETRY_FROM_ID = 1
BATCH_SEND_DELAY_SECONDS = 3