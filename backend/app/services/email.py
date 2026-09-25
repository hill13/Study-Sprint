"""
Email Service - Send transactional email through Brevo.

WHY BREVO:
Brevo supports "single sender verification" - you verify one email address you
already own, then you may send to ANY recipient. Providers that only support
domain verification (Resend, Mailgun's sandbox) restrict who can RECEIVE mail
until you own a domain, which makes a password reset useless for real users.

FAILURE POLICY:
Sending never raises into the request. A password reset must not 500 because an
email provider is slow or down - the token is already valid either way, and the
caller must not learn whether the address exists. Failures are logged instead.
"""

import logging
from typing import Optional

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

BREVO_ENDPOINT = "https://api.brevo.com/v3/smtp/email"
REQUEST_TIMEOUT_SECONDS = 10


def _reset_email_html(reset_url: str, expire_minutes: int) -> str:
    """Build the reset email body. Inline styles - email clients strip <style>."""
    return f"""\
<div style="font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:480px;margin:0 auto;padding:24px;color:#1f2937">
  <h1 style="font-size:22px;margin:0 0 16px">Reset your StudySprint password</h1>
  <p style="margin:0 0 20px;line-height:1.6">
    We received a request to reset your password. Click the button below to choose a new one.
  </p>
  <p style="margin:0 0 24px">
    <a href="{reset_url}"
       style="display:inline-block;background:#2563eb;color:#ffffff;text-decoration:none;
              padding:12px 24px;border-radius:8px;font-weight:600">
      Reset password
    </a>
  </p>
  <p style="margin:0 0 8px;font-size:14px;color:#6b7280;line-height:1.6">
    This link expires in {expire_minutes} minutes and can only be used once.
  </p>
  <p style="margin:0 0 20px;font-size:14px;color:#6b7280;line-height:1.6">
    If you did not request this, you can ignore this email - your password will not change.
  </p>
  <p style="margin:0;font-size:12px;color:#9ca3af;word-break:break-all">
    If the button does not work, paste this into your browser:<br>{reset_url}
  </p>
</div>"""


def send_password_reset_email(to_email: str, reset_url: str) -> bool:
    """
    Send a password reset email. Returns True if Brevo accepted it.

    Never raises - see FAILURE POLICY above.
    """
    settings = get_settings()

    # No provider configured: log the link so local development still works.
    if not settings.brevo_api_key or not settings.mail_from_email:
        logger.warning(
            "Email not configured (BREVO_API_KEY / MAIL_FROM_EMAIL). "
            "Reset link for %s: %s",
            to_email,
            reset_url,
        )
        return False

    payload = {
        "sender": {
            "name": settings.mail_from_name,
            "email": settings.mail_from_email,
        },
        "to": [{"email": to_email}],
        "subject": "Reset your StudySprint password",
        "htmlContent": _reset_email_html(
            reset_url, settings.password_reset_token_expire_minutes
        ),
    }

    try:
        response = httpx.post(
            BREVO_ENDPOINT,
            json=payload,
            headers={
                "api-key": settings.brevo_api_key,
                "content-type": "application/json",
                "accept": "application/json",
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except httpx.RequestError as exc:
        logger.error("Could not reach Brevo for %s: %s", to_email, exc)
        return False

    if response.status_code >= 400:
        # Brevo returns a JSON body explaining the rejection. The most common
        # cause is mail_from_email not being a verified sender.
        logger.error(
            "Brevo rejected the reset email for %s (HTTP %s): %s",
            to_email,
            response.status_code,
            response.text[:300],
        )
        return False

    logger.info("Password reset email sent to %s", to_email)
    return True


def build_reset_url(token: str) -> str:
    """Build the link that lands on the frontend reset page."""
    settings = get_settings()
    return f"{settings.frontend_url.rstrip('/')}/reset-password?token={token}"
