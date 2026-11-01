from django.conf import settings
from django.urls import translate_url

from config.company import ADVANTAGES, COMPANY, SERVICES


def site_metadata(request):
    """Build canonical and alternate-language URLs from the configured origin."""
    # Tracking and search parameters do not belong in canonical URLs.
    path = request.path
    return {
        "company": COMPANY,
        "company_services": SERVICES,
        "company_advantages": ADVANTAGES,
        "canonical_url": settings.SITE_URL + path,
        "alternate_fa": settings.SITE_URL + translate_url(path, "fa"),
        "alternate_en": settings.SITE_URL + translate_url(path, "en"),
    }
