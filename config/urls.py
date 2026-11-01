from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from products.sitemaps import ProductSitemap, StaticSitemap
from products.views import robots, set_language

urlpatterns = [
    path("i18n/setlang/", set_language, name="set_language"),
    path("robots.txt", robots, name="robots"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": {"pages": StaticSitemap, "products": ProductSitemap}},
        name="sitemap",
    ),
]
urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls), path("", include("products.urls"))
)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
