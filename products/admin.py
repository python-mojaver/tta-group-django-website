from django.contrib import admin

from .models import Category, InsulationType, Product, Project, QuoteRequest


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name_fa", "name_en")
    search_fields = ("name_fa", "name_en")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name_fa", "grade", "category", "is_active", "updated_at")
    list_filter = ("category", "is_active")
    list_select_related = ("category",)
    search_fields = ("name_fa", "name_en", "grade")
    prepopulated_fields = {"slug": ("name_en", "grade")}
    readonly_fields = ("created_at", "updated_at")


@admin.register(InsulationType)
class InsulationTypeAdmin(admin.ModelAdmin):
    list_display = ("name_fa", "name_en", "thermal_conductivity", "thickness_cm")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title_fa", "title_en", "category")
    list_filter = ("category",)
    search_fields = ("title_fa", "title_en")


@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    # Staff can update status; submitted contact details remain read-only.
    list_display = ("full_name", "company", "product_name", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("full_name", "email", "company", "product_name")
    readonly_fields = (
        "full_name",
        "email",
        "company",
        "product",
        "product_name",
        "quantity",
        "message",
        "created_at",
    )
    list_select_related = ("product",)

    def has_add_permission(self, request):
        # Inquiries enter through the validated public form.
        return False
