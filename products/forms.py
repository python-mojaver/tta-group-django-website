from django import forms

from .models import Product, QuoteRequest


class QuoteRequestForm(forms.ModelForm):
    """Public inquiry fields; workflow status is managed separately in admin."""

    # Hidden from visitors. Basic bots often fill every available input.
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}),
    )

    class Meta:
        model = QuoteRequest
        fields = ["full_name", "email", "company", "product", "quantity", "message"]
        widgets = {
            "message": forms.Textarea(
                attrs={"rows": 5, "minlength": 20, "maxlength": 3000}
            )
        }

    def __init__(self, *args, language="fa", **kwargs):
        super().__init__(*args, **kwargs)
        # Set this per request so newly unpublished products cannot be submitted.
        self.fields["product"].queryset = Product.objects.filter(
            is_active=True
        ).order_by("name_en")
        labels = {
            "fa": [
                "نام و نام خانوادگی",
                "ایمیل",
                "نام شرکت (اختیاری)",
                "محصول (اختیاری)",
                "مقدار به تن (اختیاری)",
                "شرح درخواست",
                "وب‌سایت",
            ],
            "en": [
                "Full name",
                "Email",
                "Company (optional)",
                "Product (optional)",
                "Quantity in tonnes (optional)",
                "Your requirements",
                "Website",
            ],
        }
        for name, label in zip(
            [*self.Meta.fields, "website"], labels.get(language, labels["en"])
        ):
            self.fields[name].label = label
        self.fields["product"].empty_label = (
            "انتخاب محصول" if language == "fa" else "Select a product"
        )
        for name, autocomplete in [
            ("full_name", "name"),
            ("email", "email"),
            ("company", "organization"),
        ]:
            self.fields[name].widget.attrs["autocomplete"] = autocomplete

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Please leave this field empty.")
        return ""

    def clean_message(self):
        # Validate the trimmed text; HTML minlength can be bypassed by a direct POST.
        value = self.cleaned_data["message"].strip()
        if not 20 <= len(value) <= 3000:
            raise forms.ValidationError(
                "Use 20–3000 characters / بین ۲۰ تا ۳۰۰۰ نویسه بنویسید."
            )
        return value

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Copy the product name now to preserve the original inquiry context.
        instance.product_name = instance.product.name_en if instance.product else ""
        if commit:
            instance.save()
        return instance
