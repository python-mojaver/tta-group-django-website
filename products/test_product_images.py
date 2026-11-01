from io import StringIO

from django.contrib.staticfiles import finders
from django.core.management import call_command
from django.test import TestCase, override_settings

from .models import Product


@override_settings(ALLOWED_HOSTS=["testserver"], STATIC_URL="/static/")
class ProductImageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("load_company_content", stdout=StringIO())

    def test_bundled_images_appear_on_home_catalog_and_detail_without_uploads(self):
        expected = {
            "urea-granules": "images/products/urea.png",
            "abs-injection": "images/products/abs.png",
            "mdi-component": "images/products/mdi.png",
        }
        for slug, image in expected.items():
            self.assertTrue(finders.find(image), image)
            for language in ["fa", "en"]:
                for route in ["", "products/", f"products/{slug}/"]:
                    with self.subTest(slug=slug, language=language, route=route):
                        response = self.client.get(f"/{language}/{route}")
                        self.assertContains(response, f'src="/static/{image}"')

    @override_settings(MEDIA_URL="/staff-uploads/")
    def test_staff_photo_takes_precedence_over_the_default_illustration(self):
        product = Product.objects.get(slug="mdi-component")
        product.image = "products/staff-photo.png"
        product.save()
        for route in ["/en/", "/en/products/", "/en/products/mdi-component/"]:
            response = self.client.get(route)
            self.assertContains(
                response, 'src="/staff-uploads/products/staff-photo.png"'
            )
            self.assertNotContains(response, 'src="/static/images/products/mdi.png"')

    def test_an_unmapped_product_keeps_the_generic_placeholder(self):
        product = Product(slug="another-material")
        self.assertEqual(product.image_url, "/static/images/material.svg")
