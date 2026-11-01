from urllib.parse import urlencode, urlsplit

from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import translation
from django.utils.translation import get_language_from_path
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from django.views.i18n import set_language as django_set_language

from .forms import QuoteRequestForm
from .models import Category, InsulationType, Product, Project


@require_GET
def home(request):
    """Show the latest published materials and the shared comparison table."""
    return render(
        request,
        "home.html",
        {
            "products": Product.objects.filter(is_active=True)
            .select_related("category")
            .order_by("-created_at", "-pk")[:3],
            "insulations": InsulationType.objects.all(),
        },
    )


@require_GET
def products_list(request):
    """Apply catalog filters before paginating the result set."""
    # Cards use category names; join once instead of querying per product.
    queryset = Product.objects.filter(is_active=True).select_related("category")
    query = request.GET.get("q", "").strip()[:100]
    category_id = request.GET.get("category", "")
    selected_category = None
    if query:
        queryset = queryset.filter(
            Q(name_fa__icontains=query)
            | Q(name_en__icontains=query)
            | Q(grade__icontains=query)
            | Q(description_fa__icontains=query)
            | Q(description_en__icontains=query)
            | Q(applications_fa__icontains=query)
            | Q(applications_en__icontains=query)
        )
    if category_id:
        # Reject malformed IDs before conversion; a missing numeric ID is a 404.
        selected_category = (
            get_object_or_404(Category, pk=int(category_id))
            if category_id.isascii()
            and category_id.isdecimal()
            and len(category_id) < 10
            else None
        )
        queryset = (
            queryset.filter(category=selected_category)
            if selected_category
            else queryset.none()
        )
    sort = request.GET.get("sort", "newest")
    # Map public sort keys to known fields rather than accepting field names.
    ordering = {
        "newest": ("-created_at", "-pk"),
        "name": ("name_fa" if request.LANGUAGE_CODE == "fa" else "name_en", "pk"),
    }
    if sort not in ordering:
        sort = "newest"
    # The primary-key tiebreaker keeps page boundaries stable for equal values.
    page = Paginator(queryset.order_by(*ordering[sort]), 6).get_page(
        request.GET.get("page")
    )
    # Rebuild pagination links from the supported filters only.
    params = {
        k: v
        for k, v in {"q": query, "category": category_id, "sort": sort}.items()
        if v
    }
    return render(
        request,
        "products/products_list.html",
        {
            "products": page,
            "page_obj": page,
            "categories": Category.objects.all(),
            "query": query,
            "selected_category": category_id,
            "sort": sort,
            "filter_query": urlencode(params),
        },
    )


@require_GET
def product_detail(request, slug):
    """Unpublished products must remain inaccessible through direct URLs."""
    product = get_object_or_404(
        Product.objects.select_related("category"), slug=slug, is_active=True
    )
    return render(request, "products/product_detail.html", {"product": product})


@require_GET
def about(request):
    return render(
        request,
        "about.html",
        {
            "insulations": InsulationType.objects.all(),
            "projects": Project.objects.all(),
        },
    )


@require_http_methods(["GET", "POST"])
def contact(request):
    """Prefill a product on GET and save validated inquiries on POST."""
    initial = {}
    if request.method == "GET" and request.GET.get("product"):
        initial["product"] = get_object_or_404(
            Product, slug=request.GET["product"], is_active=True
        )
    form = QuoteRequestForm(
        request.POST if request.method == "POST" else None,
        initial=initial,
        language=request.LANGUAGE_CODE,
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request,
            (
                "درخواست شما برای بررسی ثبت شد."
                if request.LANGUAGE_CODE == "fa"
                else "Your request has been saved for review by the sales team."
            ),
        )
        # A refresh after this redirect repeats GET, not the submitted POST.
        return redirect("contact")
    return render(request, "contact.html", {"form": form})


@require_GET
def robots(request):
    return HttpResponse(
        "User-agent: *\nDisallow: /fa/admin/\nDisallow: /en/admin/\nSitemap: "
        + settings.SITE_URL
        + reverse("sitemap")
        + "\n",
        content_type="text/plain",
    )


@require_POST
def set_language(request):
    """Translate the current route even when its language differs from the cookie."""
    # The unprefixed endpoint may have a cookie language different from the URL.
    # Resolve translation under the source URL's language; Django still validates
    # the redirect host, requested language and cookie attributes itself.
    next_url = request.POST.get("next", "")
    try:
        source_language = get_language_from_path(urlsplit(next_url).path)
    except ValueError:
        source_language = None
    with translation.override(source_language or translation.get_language()):
        return django_set_language(request)
