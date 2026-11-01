from decimal import Decimal

from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from django.templatetags.static import static
from django.urls import reverse
from django.utils.translation import get_language

from .assets import PRODUCT_IMAGES
from .validators import validate_pdf, validate_upload_size


class LocalizedModel(models.Model):
    """Expose translated fields without storing a second copy of their values."""

    class Meta:
        abstract = True

    def localized(self, field):
        # Missing Persian content falls back to the English field.
        language = "fa" if (get_language() or "fa").startswith("fa") else "en"
        return getattr(self, f"{field}_{language}", "") or getattr(
            self, f"{field}_en", ""
        )

    @property
    def name(self):
        return self.localized("name")

    @property
    def description(self):
        return self.localized("description")

    @property
    def applications(self):
        return self.localized("applications")

    @property
    def title(self):
        return self.localized("title")

    @property
    def feature(self):
        return self.localized("feature")


class Category(LocalizedModel):
    """Bilingual grouping for catalog products."""

    name_fa = models.CharField(max_length=100, verbose_name="نام دسته‌بندی (فارسی)")
    name_en = models.CharField(max_length=100, verbose_name="نام دسته‌بندی (انگلیسی)")

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"

    def __str__(self):
        return self.name


class Product(LocalizedModel):
    """Catalog entry with bilingual content and optional technical documents."""

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="دسته‌بندی",
    )
    grade = models.CharField(max_length=50, verbose_name="گرید (Grade)")
    image = models.ImageField(
        upload_to="products/",
        validators=[
            validate_upload_size,
            FileExtensionValidator(["jpg", "jpeg", "png", "webp"]),
        ],
        blank=True,
        null=True,
        verbose_name="تصویر محصول",
    )

    slug = models.SlugField(max_length=220, unique=True)
    is_active = models.BooleanField(default=True, verbose_name="منتشر شده")
    updated_at = models.DateTimeField(auto_now=True)

    # Store catalog translations explicitly so staff can edit both in admin.
    name_fa = models.CharField(max_length=200, verbose_name="نام محصول (فارسی)")
    description_fa = models.TextField(verbose_name="توضیحات (فارسی)")
    applications_fa = models.TextField(blank=True, verbose_name="کاربردها (فارسی)")

    name_en = models.CharField(max_length=200, verbose_name="نام محصول (انگلیسی)")
    description_en = models.TextField(verbose_name="توضیحات (انگلیسی)")
    applications_en = models.TextField(blank=True, verbose_name="کاربردها (انگلیسی)")

    # Both PDF extension and header checks run during form validation.
    tds_file = models.FileField(
        upload_to="documents/tds/",
        validators=[
            validate_upload_size,
            FileExtensionValidator(["pdf"]),
            validate_pdf,
        ],
        blank=True,
        null=True,
        verbose_name="فایل TDS",
    )
    msds_file = models.FileField(
        upload_to="documents/msds/",
        validators=[
            validate_upload_size,
            FileExtensionValidator(["pdf"]),
            validate_pdf,
        ],
        blank=True,
        null=True,
        verbose_name="فایل MSDS",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"

    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"slug": self.slug})

    @property
    def image_url(self):
        """Prefer the staff-uploaded photo over the bundled catalog illustration."""
        if self.image:
            return self.image.url
        # Static defaults survive a fresh checkout without copying a media folder.
        return static(PRODUCT_IMAGES.get(self.slug, "images/material.svg"))

    def __str__(self):
        return f"{self.name} ({self.grade})"


class InsulationType(LocalizedModel):
    """Shared comparison data for the home and about pages."""

    name_fa = models.CharField(max_length=100, verbose_name="نوع عایق (فارسی)")
    name_en = models.CharField(max_length=100, verbose_name="نوع عایق (انگلیسی)")
    thermal_conductivity = models.CharField(
        max_length=50, verbose_name="ضریب هدایت حرارتی λ"
    )
    thickness_cm = models.CharField(max_length=50, verbose_name="ضخامت متداول (cm)")
    feature_fa = models.CharField(max_length=255, verbose_name="ویژگی کلیدی (فارسی)")
    feature_en = models.CharField(max_length=255, verbose_name="ویژگی کلیدی (انگلیسی)")

    class Meta:
        verbose_name = "مشخصات عایق"
        verbose_name_plural = "جدول مقایسه عایق‌ها"

    def __str__(self):
        return self.name_fa


class Project(LocalizedModel):
    """Project reference with a localized title and optional image."""

    CATEGORY_CHOICES = [
        ("cold_storage", "سردخانه و صنایع غذایی"),
        ("petrochemical", "پتروشیمی و نفت/گاز"),
        ("industrial", "صنعتی و خودروسازی"),
    ]
    title_fa = models.CharField(max_length=200, verbose_name="نام پروژه / شرکت (فارسی)")
    title_en = models.CharField(
        max_length=200, verbose_name="نام پروژه / شرکت (انگلیسی)"
    )
    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, verbose_name="دسته‌بندی پروژه"
    )
    image = models.ImageField(
        upload_to="projects/",
        validators=[
            validate_upload_size,
            FileExtensionValidator(["jpg", "jpeg", "png", "webp"]),
        ],
        blank=True,
        null=True,
        verbose_name="تصویر پروژه",
    )

    class Meta:
        verbose_name = "پروژه / مشتری"
        verbose_name_plural = "پروژه‌ها و همکاران"

    @property
    def category_label(self):
        if (get_language() or "fa").startswith("fa"):
            return self.get_category_display()
        return {
            "cold_storage": "Cold storage & food",
            "petrochemical": "Petrochemicals & energy",
            "industrial": "Industrial & automotive",
        }.get(self.category, self.category)

    def __str__(self):
        return self.title


class QuoteRequest(models.Model):
    """Sales inquiry whose history is retained when a product is removed."""

    STATUS_CHOICES = [
        ("new", "New / جدید"),
        ("reviewing", "Reviewing / در حال بررسی"),
        ("replied", "Replied / پاسخ داده شده"),
        ("closed", "Closed / بسته شده"),
    ]
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    company = models.CharField(max_length=160, blank=True)
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True
    )
    # The snapshot survives product deletion and later catalog name changes.
    product_name = models.CharField(max_length=200, blank=True)
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    message = models.TextField(max_length=3000)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
        verbose_name = "درخواست قیمت"
        verbose_name_plural = "درخواست‌های قیمت"

    def __str__(self):
        return f"{self.full_name} — {self.product_name or self.company}"
