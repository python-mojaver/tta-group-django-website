from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings

from .company_catalog import PRODUCTS
from .models import InsulationType, Product, QuoteRequest


@override_settings(ALLOWED_HOSTS=["testserver"])
class CompanyContentTests(TestCase):
    def load_content(self):
        output = StringIO()
        call_command("load_company_content", stdout=output)
        return output.getvalue()

    def test_fresh_import_contains_original_products_and_no_customer_records(self):
        self.load_content()
        self.assertEqual(Product.objects.count(), 3)
        self.assertEqual(InsulationType.objects.count(), 4)
        self.assertFalse(get_user_model().objects.exists())
        self.assertFalse(QuoteRequest.objects.exists())
        for source in PRODUCTS:
            product = Product.objects.get(slug=source["slug"])
            self.assertEqual(product.description_fa, source["description_fa"])
            for language in ["fa", "en"]:
                response = self.client.get(f"/{language}/products/{product.slug}/")
                self.assertContains(response, source[f"description_{language}"])
                self.assertNotContains(response, "TDS · PDF")

    def test_import_keeps_product_links_uploads_accounts_and_existing_inquiries(self):
        call_command("seed_demo", stdout=StringIO())
        product = Product.objects.get(slug="mdi-component")
        product.image = "products/previous.png"
        product.tds_file = "documents/tds/previous.pdf"
        product.save()
        inquiry = QuoteRequest.objects.create(
            product=product,
            product_name="Original submitted product name",
            full_name="Existing buyer",
            email="buyer@example.com",
            message="Existing inquiry that must survive a catalog content update.",
        )
        user = get_user_model().objects.create_user(username="existing-staff")
        self.load_content()
        product.refresh_from_db()
        inquiry.refresh_from_db()
        self.assertEqual(product.name_en, "PM200 / MDI Isocyanate")
        self.assertEqual(product.image.name, "products/previous.png")
        self.assertEqual(product.tds_file.name, "documents/tds/previous.pdf")
        self.assertEqual(inquiry.product_id, product.pk)
        self.assertEqual(inquiry.product_name, "Original submitted product name")
        self.assertTrue(get_user_model().objects.filter(pk=user.pk).exists())
        self.assertEqual(Product.objects.count(), 9)
        self.assertEqual(Product.objects.filter(is_active=True).count(), 3)

    def test_staff_changes_are_preserved_in_products_and_comparison_data(self):
        call_command("seed_demo", stdout=StringIO())
        product = Product.objects.get(slug="abs-injection")
        product.description_fa = "توضیح اختصاصی ثبت‌شده توسط مدیر"
        product.save()
        extra = Product.objects.get(slug="hdpe-pipe")
        extra.description_en = "Staff-maintained HDPE description"
        extra.save()
        insulation = InsulationType.objects.get(name_en="XPS")
        insulation.feature_fa = "ویژگی ویرایش‌شده توسط مدیر"
        insulation.save()
        output = self.load_content()
        product.refresh_from_db()
        extra.refresh_from_db()
        insulation.refresh_from_db()
        self.assertEqual(product.description_fa, "توضیح اختصاصی ثبت‌شده توسط مدیر")
        self.assertTrue(extra.is_active)
        self.assertEqual(insulation.feature_fa, "ویژگی ویرایش‌شده توسط مدیر")
        self.assertIn("Preserved staff-edited product", output)

    def test_repeated_import_does_not_duplicate_or_rewrite_unchanged_records(self):
        self.load_content()
        original = list(Product.objects.values_list("pk", "updated_at"))
        self.load_content()
        self.assertEqual(
            original, list(Product.objects.values_list("pk", "updated_at"))
        )
        self.assertEqual(InsulationType.objects.count(), 4)
        Product.objects.filter(slug="urea-granules").update(is_active=False)
        self.load_content()
        self.assertFalse(Product.objects.get(slug="urea-granules").is_active)

    def test_services_comparison_and_contacts_are_shared_across_languages(self):
        self.load_content()
        for language in ["fa", "en"]:
            for route in ["", "about/", "products/", "contact/"]:
                response = self.client.get(f"/{language}/{route}")
                for value in [
                    'href="tel:+982144050272"',
                    'href="tel:+982144099661"',
                    'href="tel:+989121574462"',
                    "info@ttagroup.ir",
                    "ttagroupco@gmail.com",
                    "213198" if language == "en" else "۲۱۳۱۹۸",
                    "1481713118" if language == "en" else "۱۴۸۱۷۱۳۱۱۸",
                ]:
                    self.assertContains(response, value)
                self.assertNotContains(response, "hello@example.com")
                if route in ["", "about/"]:
                    for value in ["Graco", "PM200", "0.022–0.028", "0.035–0.040"]:
                        self.assertContains(response, value)
        row = InsulationType.objects.get(name_en="XPS")
        row.feature_fa = "تغییر مشترک جدول مقایسه"
        row.save()
        for route in ["/fa/", "/fa/about/"]:
            self.assertContains(self.client.get(route), "تغییر مشترک جدول مقایسه")
