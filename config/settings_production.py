"""HTTPS production settings. Static and media must be served by the web server."""

import os

from django.core.exceptions import ImproperlyConfigured

os.environ["DJANGO_DEBUG"] = "false"
from .settings import *  # noqa: E402, F403

if not os.getenv("DJANGO_ALLOWED_HOSTS"):
    raise ImproperlyConfigured("DJANGO_ALLOWED_HOSTS is required in production.")
if not os.getenv("DJANGO_SITE_URL", "").startswith("https://"):
    raise ImproperlyConfigured("DJANGO_SITE_URL must use HTTPS in production.")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
# Set this only when your trusted proxy strips incoming X-Forwarded-Proto headers.
if os.getenv("DJANGO_TRUST_PROXY", "false").lower() == "true":
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
