from decimal import Decimal
from io import BytesIO, StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import Client, TestCase, TransactionTestCase, override_settings
from PIL import Image

from .forms import QuoteRequestForm
from .models import Category, Product, QuoteRequest
from .validators import validate_pdf, validate_upload_size


@override_settings(ALLOWED_HOSTS=["testserver"], SITE_URL="https://example.com")
class CatalogTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name_fa="پلیمر", name_en="Polymers")
        cls.other = Category.objects.create(name_fa="عایق", name_en="Insulation")
        cls.product = Product.objects.create(
            category=cls.category,
            slug="hdpe",
            name_fa="پلی‌اتیلن",
            name_en="Polyethylene",
            description_fa="شرح محصول",
            description_en="An industrial resin",
            grade="HDPE-100",
            applications_en="Pipes",
            applications_fa="لوله",
        )
        Product.objects.create(
            category=cls.other,
            slug="hidden",
            name_fa="مخفی",
            name_en="Hidden",
            description_fa="مخفی",
            description_en="Hidden",
            grade="H",
            is_active=False,
        )

    def test_public_pages_in_both_languages(self):
        for language in ["fa", "en"]:
            for path in ["", "products/", "products/hdpe/", "about/", "contact/"]:
                with self.subTest(language=language, path=path):
                    response = self.client.get(f"/{language}/{path}")
                    self.assertEqual(response.status_code, 200)
                    self.assertContains(response, f'lang="{language}"')
                    self.assertContains(
                        response, 'dir="rtl"' if language == "fa" else 'dir="ltr"'
                    )

    def test_home_uses_database_products_and_shared_spec_table(self):
        response = self.client.get("/en/")
        self.assertContains(response, "Polyethylene")
        self.assertNotContains(response, "Hidden")
        self.assertContains(response, "No specifications have been published yet")

    def test_search_name_grade_and_application(self):
        for query in ["Polyethylene", "پلی‌اتیلن", "HDPE", "Pipes", "لوله"]:
            with self.subTest(query=query):
                response = self.client.get("/en/products/", {"q": query})
                self.assertEqual(
                    [p.pk for p in response.context["products"]], [self.product.pk]
                )

    def test_category_filter(self):
        response = self.client.get("/en/products/", {"category": self.category.pk})
        self.assertEqual(response.context["page_obj"].paginator.count, 1)
        self.assertEqual(
            self.client.get("/en/products/", {"category": self.other.pk})
            .context["page_obj"]
            .paginator.count,
            0,
        )

    def test_malformed_category_and_sort_do_not_crash(self):
        for value in ["text", "-1", "9" * 100, "۱۲"]:
            self.assertEqual(
                self.client.get(
                    "/en/products/", {"category": value, "sort": "DROP TABLE"}
                ).status_code,
                200,
            )
        self.assertEqual(
            self.client.get("/en/products/", {"category": "999"}).status_code, 404
        )

    def test_empty_search_has_no_fake_products(self):
        response = self.client.get("/en/products/", {"q": "no-such-material"})
        self.assertContains(response, "No materials found")
        self.assertNotContains(response, "کود اوره")

    def test_pagination_preserves_filters(self):
        for n in range(7):
            Product.objects.create(
                category=self.category,
                slug=f"resin-{n}",
                name_fa=f"رزین {n}",
                name_en=f"Resin {n}",
                description_fa="نمونه",
                description_en="Resin",
                grade="HDPE",
            )
        response = self.client.get(
            "/en/products/", {"q": "HDPE", "category": self.category.pk, "page": "2"}
        )
        self.assertEqual(response.context["page_obj"].number, 2)
        self.assertEqual(len(response.context["products"]), 2)
        self.assertContains(response, "q=HDPE&amp;category=")
        self.assertEqual(
            self.client.get("/en/products/", {"page": "bad"}).status_code, 200
        )

    def test_catalog_query_count_does_not_grow_per_product(self):
        for n in range(5):
            Product.objects.create(
                category=self.category,
                slug=f"extra-{n}",
                name_fa="نمونه",
                name_en="Extra",
                description_fa="نمونه",
                description_en="Sample",
                grade="D",
            )
        with self.assertNumQueries(3):
            self.client.get("/en/products/")

    def test_hidden_and_missing_product_return_404(self):
        for slug in ["hidden", "missing"]:
            self.assertEqual(self.client.get(f"/en/products/{slug}/").status_code, 404)

    def test_language_switch_preserves_page_and_query_without_referer(self):
        response = self.client.post(
            "/i18n/setlang/",
            {"language": "fa", "next": "/en/products/?q=HDPE&sort=name"},
        )
        self.assertEqual(response.headers["Location"], "/fa/products/?q=HDPE&sort=name")
        page = self.client.get("/en/products/?q=HDPE")
        self.assertContains(page, 'name="next" value="/en/products/?q=HDPE"')

    def test_language_switch_rejects_external_redirect(self):
        response = self.client.post(
            "/i18n/setlang/", {"language": "en", "next": "https://evil.example/"}
        )
        self.assertNotIn("evil.example", response.headers["Location"])

    def test_seo_and_sitemap_languages(self):
        page = self.client.get("/en/products/hdpe/")
        self.assertContains(
            page, 'rel="canonical" href="https://example.com/en/products/hdpe/"'
        )
        self.assertContains(page, 'hreflang="fa"')
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "https://example.com/en/products/hdpe/")
        self.assertContains(response, "https://example.com/fa/products/hdpe/")
        self.assertNotContains(response, "/products/hidden/")
        self.assertContains(
            self.client.get("/robots.txt"), "https://example.com/sitemap.xml"
        )

    def test_query_is_html_escaped(self):
        response = self.client.get(
            "/en/products/", {"q": '<script>alert("x")</script>'}
        )
        self.assertNotContains(response, '<script>alert("x")</script>')
        self.assertContains(response, "&lt;script&gt;")

    def test_csrf_enforced_for_inquiry(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(
            client.post("/en/contact/", {"full_name": "Demo"}).status_code, 403
        )

    def inquiry_data(self, **overrides):
        return {
            "full_name": "Demo Buyer",
            "email": "buyer@example.com",
            "company": "Demo Company",
            "product": str(self.product.pk),
            "quantity": "2.50",
            "message": "Please provide technical information about this sample material.",
            "website": "",
            **overrides,
        }

    def test_successful_inquiry_prg_and_snapshot(self):
        response = self.client.post("/en/contact/", self.inquiry_data(), follow=True)
        self.assertContains(response, "Your request has been saved")
        inquiry = QuoteRequest.objects.get()
        self.assertEqual(inquiry.quantity, Decimal("2.50"))
        self.assertEqual(inquiry.product_name, "Polyethylene")
        self.client.get("/en/contact/")
        self.assertEqual(QuoteRequest.objects.count(), 1)
        self.product.delete()
        inquiry.refresh_from_db()
        self.assertIsNone(inquiry.product)
        self.assertEqual(inquiry.product_name, "Polyethylene")

    def test_invalid_inquiries_never_saved(self):
        hidden = Product.objects.get(slug="hidden")
        for bad in [
            {"email": "bad"},
            {"quantity": "-1"},
            {"quantity": "0"},
            {"message": "short"},
            {"message": "x" * 3001},
            {"website": "spam.example"},
            {"product": hidden.pk},
        ]:
            with self.subTest(bad=bad):
                response = self.client.post("/en/contact/", self.inquiry_data(**bad))
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context["form"].errors)
                self.assertEqual(QuoteRequest.objects.count(), 0)

    def test_optional_product_and_quantity(self):
        form = QuoteRequestForm(
            self.inquiry_data(product="", quantity=""), language="en"
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertIsNone(form.save().product)

    def test_product_prefill_and_inactive_prefill(self):
        response = self.client.get("/en/contact/?product=hdpe")
        self.assertEqual(response.context["form"].initial["product"], self.product)
        self.assertEqual(
            self.client.get("/en/contact/?product=hidden").status_code, 404
        )

    def test_inquiry_admin_requires_staff(self):
        self.assertEqual(
            self.client.get("/en/admin/products/quoterequest/").status_code, 302
        )
        user = get_user_model().objects.create_user(
            username="ordinary", password="temporary-test-password"
        )
        self.client.force_login(user)
        self.assertEqual(
            self.client.get("/en/admin/products/quoterequest/").status_code, 302
        )

    def test_staff_can_review_inquiry(self):
        user = get_user_model().objects.create_superuser(
            username="reviewer",
            email="admin@example.com",
            password="temporary-test-password",
        )
        self.client.force_login(user)
        self.assertEqual(
            self.client.get("/en/admin/products/quoterequest/").status_code, 200
        )

    def test_admin_status_update_preserves_submitted_details(self):
        self.client.post("/en/contact/", self.inquiry_data())
        inquiry = QuoteRequest.objects.get()
        user = get_user_model().objects.create_superuser(
            username="sales", email="sales@example.com", password="test-password"
        )
        self.client.force_login(user)
        response = self.client.post(
            f"/en/admin/products/quoterequest/{inquiry.pk}/change/",
            {"status": "reviewing", "email": "changed@example.com", "_save": "Save"},
        )
        self.assertEqual(response.status_code, 302)
        inquiry.refresh_from_db()
        self.assertEqual(inquiry.status, "reviewing")
        self.assertEqual(inquiry.email, "buyer@example.com")
        self.assertEqual(inquiry.product_name, "Polyethylene")

    def test_unsupported_http_methods(self):
        self.assertEqual(self.client.post("/en/products/").status_code, 405)
        self.assertEqual(self.client.put("/en/contact/").status_code, 405)

    def test_pdf_validation_header_size_and_extension(self):
        invalid = SimpleUploadedFile("bad.pdf", b"<html>not a PDF</html>")
        with self.assertRaises(ValidationError):
            validate_pdf(invalid)
        valid = SimpleUploadedFile("good.pdf", b"%PDF-1.4\nexample")
        validate_pdf(valid)
        self.assertEqual(valid.tell(), 0)
        field = Product._meta.get_field("tds_file")
        with self.assertRaises(ValidationError):
            field.run_validators(SimpleUploadedFile("bad.html", b"%PDF-1.4"))
        oversized = SimpleUploadedFile("huge.pdf", b"x" * (5 * 1024 * 1024 + 1))
        with self.assertRaises(ValidationError):
            validate_upload_size(oversized)

    def test_media_upload_is_written_beneath_media_root(self):
        with TemporaryDirectory() as directory, override_settings(MEDIA_ROOT=directory):
            buffer = BytesIO()
            Image.new("RGB", (8, 8), "white").save(buffer, "PNG")
            self.product.image = SimpleUploadedFile(
                "sample.png", buffer.getvalue(), content_type="image/png"
            )
            self.product.full_clean()
            self.product.save()
            self.assertTrue(Path(self.product.image.path).is_file())
            self.assertTrue(self.product.image.url.startswith("/media/products/"))

    def test_demo_seed_is_idempotent_and_creates_no_accounts(self):
        call_command("seed_demo", stdout=StringIO())
        counts = (Product.objects.count(), Category.objects.count())
        call_command("seed_demo", stdout=StringIO())
        self.assertEqual(counts, (Product.objects.count(), Category.objects.count()))
        self.assertEqual(get_user_model().objects.count(), 0)

    @override_settings(DEBUG=False)
    def test_production_404_template(self):
        response = self.client.get("/en/missing-page/")
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")


class ExistingCatalogMigrationTests(TransactionTestCase):
    """Upgrade a pre-existing catalog instead of testing only fresh installs."""

    migrate_from = [("products", "0002_insulationtype_project")]
    migrate_to = [
        ("products", "0003_product_is_active_product_slug_product_updated_at_and_more")
    ]

    def setUp(self):
        super().setUp()
        executor = MigrationExecutor(connection)
        self.latest = executor.loader.graph.leaf_nodes()
        # Restore the current schema even if setup or the upgrade fails.
        self.addCleanup(self.restore_schema)
        executor.migrate(self.migrate_from)
        self.old_apps = executor.loader.project_state(self.migrate_from).apps

    def restore_schema(self):
        MigrationExecutor(connection).migrate(self.latest)

    def test_existing_products_receive_unique_slugs_without_losing_content(self):
        Category = self.old_apps.get_model("products", "Category")
        Product = self.old_apps.get_model("products", "Product")
        category = Category.objects.create(name_fa="پلیمر", name_en="Polymers")
        original = []
        # Duplicate names and non-Latin names exercise both slug collisions
        # and the fallback used when slugify cannot produce an ASCII name.
        for name in ["Same resin", "Same resin", "رزین"]:
            original.append(
                Product.objects.create(
                    category=category,
                    name_fa="رزین",
                    name_en=name,
                    grade="EXISTING",
                    description_fa="شرح ثبت‌شده قبلی",
                    description_en="Existing customer catalog content",
                ).pk
            )
        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_to)
        apps = executor.loader.project_state(self.migrate_to).apps
        Product = apps.get_model("products", "Product")
        products = list(Product.objects.order_by("pk"))
        self.assertEqual([product.pk for product in products], original)
        self.assertEqual(len({product.slug for product in products}), 3)
        for product in products:
            self.assertTrue(product.slug)
            self.assertTrue(product.is_active)
            self.assertEqual(product.description_fa, "شرح ثبت‌شده قبلی")
            self.assertEqual(product.category_id, category.pk)
