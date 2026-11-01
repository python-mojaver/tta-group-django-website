from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Product


class SiteDomainMixin:
    """Use SITE_URL so canonical links do not depend on the request Host."""

    def get_urls(self, site=None, protocol=None, **kwargs):
        from types import SimpleNamespace
        from urllib.parse import urlsplit

        parsed = urlsplit(settings.SITE_URL)
        return super().get_urls(
            site=SimpleNamespace(domain=parsed.netloc), protocol=parsed.scheme, **kwargs
        )


class StaticSitemap(SiteDomainMixin, Sitemap):
    i18n = True
    languages = ["fa", "en"]
    changefreq = "weekly"

    def items(self):
        return ["home", "products_list", "about", "contact"]

    def location(self, item):
        return reverse(item)


class ProductSitemap(SiteDomainMixin, Sitemap):
    i18n = True
    languages = ["fa", "en"]
    changefreq = "weekly"

    def items(self):
        return Product.objects.filter(is_active=True).order_by("pk")

    def lastmod(self, item):
        return item.updated_at
