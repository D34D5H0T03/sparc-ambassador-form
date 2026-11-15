from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect

from .google_auth import create_oauth_flow, get_credentials, save_credentials


@staff_member_required
def oauth2_init(request):
    flow = create_oauth_flow()
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    request.session["google_oauth_state"] = state
    return redirect(authorization_url)


@staff_member_required
def oauth2_callback(request):
    if "error" in request.GET:
        return HttpResponseBadRequest(
            f"Google OAuth authorization failed: {request.GET.get('error')}"
        )

    expected_state = request.session.get("google_oauth_state")
    returned_state = request.GET.get("state")

    if not expected_state or expected_state != returned_state:
        return HttpResponseBadRequest(
            "Invalid OAuth state parameter. Start authorization again from /init/oauth2/."
        )

    flow = create_oauth_flow(state=expected_state)
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    save_credentials(flow.credentials)

    request.session.pop("google_oauth_state", None)

    return HttpResponse(
        "<h2>Gmail API Authorization Successful</h2>"
        "<p>OAuth credentials have been saved to <code>token.json</code>. "
        "Background confirmation emails are now ready to send.</p>"
        "<p><a href='/admin/emails/mailjob/'>View Mail Jobs in Django Admin</a></p>"
    )