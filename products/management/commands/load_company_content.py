from django.core.management.base import BaseCommand
from django.db import transaction

from products import legacy_demo
from products.company_catalog import INSULATIONS, PRODUCTS
from products.models import Category, InsulationType, Product


def matches(record, values):
    return all(getattr(record, name) == value for name, value in values.items())


class Command(BaseCommand):
    help = "Load original TTA catalog copy while preserving staff edits, files and inquiries."

    @transaction.atomic
    def handle(self, *args, **options):
        loaded = preserved = hidden = 0
        for source in PRODUCTS:
            values = {
                name: value
                for name, value in source.items()
                if name not in {"slug", "category_fa", "category_en"}
            }
            product = Product.objects.filter(slug=source["slug"]).first()
            if product and not (
                matches(product, values)
                or matches(product, legacy_demo.PRODUCTS[source["slug"]])
            ):
                self.stdout.write(
                    self.style.WARNING(
                        f"Preserved staff-edited product: {product.slug}"
                    )
                )
                preserved += 1
                continue
            if product is None:
                category = (
                    Category.objects.filter(name_en=source["category_en"])
                    .order_by("pk")
                    .first()
                )
                if category is None:
                    category = Category.objects.create(
                        name_fa=source["category_fa"], name_en=source["category_en"]
                    )
                Product.objects.create(slug=source["slug"], category=category, **values)
            elif not matches(product, values):
                # Update text only: keep identifiers, attachments, publication
                # state, category assignments and inquiry relationships intact.
                for name, value in values.items():
                    setattr(product, name, value)
                product.save(update_fields=[*values, "updated_at"])
            loaded += 1

        company_slugs = {source["slug"] for source in PRODUCTS}
        for slug, values in legacy_demo.PRODUCTS.items():
            if slug in company_slugs:
                continue
            product = Product.objects.filter(slug=slug, is_active=True).first()
            if (
                product
                and matches(product, values)
                and not any([product.image, product.tds_file, product.msds_file])
            ):
                # Retire untouched examples without deleting their history.
                product.is_active = False
                product.save(update_fields=["is_active", "updated_at"])
                hidden += 1

        for source in INSULATIONS:
            values = {k: v for k, v in source.items() if k != "lookup_en"}
            record = (
                InsulationType.objects.filter(name_en=source["lookup_en"])
                .order_by("pk")
                .first()
            )
            if record is None:
                InsulationType.objects.create(**values)
            elif matches(record, legacy_demo.INSULATIONS[source["lookup_en"]]):
                for name, value in values.items():
                    setattr(record, name, value)
                record.save(update_fields=list(values))
            elif not matches(record, values):
                self.stdout.write(
                    self.style.WARNING(
                        f"Preserved staff-edited insulation: {record.name_en}"
                    )
                )
                preserved += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Company content ready: {loaded} products loaded; "
                f"{hidden} untouched demo products hidden; "
                f"{preserved} staff-edited records preserved. "
                "No accounts, inquiries or uploaded files deleted."
            )
        )
