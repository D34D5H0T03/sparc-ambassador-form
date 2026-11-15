from urllib.parse import urlparse

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect

from .constants import (
    OAUTH_ACCESS_TYPE,
    OAUTH_INCLUDE_GRANTED_SCOPES,
    OAUTH_INIT_PATH,
    OAUTH_PROMPT,
    SESSION_OAUTH_STATE_KEY,
    SESSION_OAUTH_VERIFIER_KEY,
)
from .google_auth import create_oauth_flow, get_credentials, save_credentials


@staff_member_required
def oauth2_init(request):
    expected_host = urlparse(settings.SITE_URL).netloc
    if expected_host and request.get_host() != expected_host:
        return redirect(f"{settings.SITE_URL}{request.get_full_path()}")

    flow = create_oauth_flow()
    authorization_url, state = flow.authorization_url(
        access_type=OAUTH_ACCESS_TYPE,
        include_granted_scopes=OAUTH_INCLUDE_GRANTED_SCOPES,
        prompt=OAUTH_PROMPT,
    )
    request.session[SESSION_OAUTH_STATE_KEY] = state
    request.session[SESSION_OAUTH_VERIFIER_KEY] = getattr(
        flow, "code_verifier", None
    )
    request.session.modified = True
    return redirect(authorization_url)


@staff_member_required
def oauth2_callback(request):
    if "error" in request.GET:
        return HttpResponseBadRequest(
            f"Google OAuth authorization failed: {request.GET.get('error')}"
        )

    expected_state = request.session.get(SESSION_OAUTH_STATE_KEY)
    returned_state = request.GET.get("state")

    if not expected_state or expected_state != returned_state:
        return HttpResponseBadRequest(
            f"Invalid OAuth state parameter. Start authorization again from {OAUTH_INIT_PATH}."
        )

    flow = create_oauth_flow(state=expected_state)
    flow.code_verifier = request.session.get(SESSION_OAUTH_VERIFIER_KEY)
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    save_credentials(flow.credentials)

    request.session.pop(SESSION_OAUTH_STATE_KEY, None)
    request.session.pop(SESSION_OAUTH_VERIFIER_KEY, None)

    return HttpResponse(
        "<h2>Gmail API Authorization Successful</h2>"
        "<p>OAuth credentials have been saved to <code>token.json</code>. "
        "Background confirmation emails are now ready to send.</p>"
        "<p><a href='/admin/emails/mailjob/'>View Mail Jobs in Django Admin</a></p>"
    )