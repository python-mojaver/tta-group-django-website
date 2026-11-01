from django.core.management.base import BaseCommand
from django.db import transaction

from products.models import Category, InsulationType, Product, Project


class Command(BaseCommand):
    help = "Create fictional demo catalog data without deleting existing records or creating user accounts."

    # Keep demo initialization all-or-nothing if any insert fails.
    @transaction.atomic
    def handle(self, *args, **options):
        # Existing entries are left unchanged when the command runs again.
        categories = {}
        for code, fa, en in [
            ("polymer", "پلیمر و رزین", "Polymers & resins"),
            ("chemical", "مواد شیمیایی", "Chemical materials"),
            ("insulation", "عایق صنعتی", "Industrial insulation"),
        ]:
            categories[code], _ = Category.objects.get_or_create(
                name_en=en, defaults={"name_fa": fa}
            )
        rows = [
            (
                "hdpe-pipe",
                "polymer",
                "پلی‌اتیلن سنگین",
                "High-density polyethylene",
                "PIPE / DEMO",
                "تولید لوله و اتصالات",
                "Pipes and fittings",
            ),
            (
                "pp-fiber",
                "polymer",
                "پلی‌پروپیلن الیافی",
                "Polypropylene fiber resin",
                "FIBER / DEMO",
                "الیاف و منسوجات",
                "Fibers and textiles",
            ),
            (
                "abs-injection",
                "polymer",
                "رزین ای‌بی‌اس",
                "ABS injection resin",
                "INJECTION / DEMO",
                "قطعات تزریقی و لوازم خانگی",
                "Molded parts and appliances",
            ),
            (
                "mdi-component",
                "chemical",
                "ایزوسیانات پلیمری",
                "Polymeric MDI component",
                "FOAM / DEMO",
                "فرمولاسیون فوم سخت",
                "Rigid foam formulation",
            ),
            (
                "polyol-blend",
                "chemical",
                "پلی‌ال ترکیبی",
                "Polyol blend",
                "BLEND / DEMO",
                "تولید فوم و عایق",
                "Foam and insulation production",
            ),
            (
                "urea-granules",
                "chemical",
                "اوره گرانول",
                "Granular urea",
                "GRANULAR / DEMO",
                "فرآوری مواد شیمیایی",
                "Chemical processing",
            ),
            (
                "pu-panel",
                "insulation",
                "پنل پلی‌یورتان",
                "Polyurethane insulation panel",
                "PANEL / DEMO",
                "سردخانه و ساختمان صنعتی",
                "Cold storage and industrial buildings",
            ),
            (
                "xps-board",
                "insulation",
                "برد عایق اکسترود",
                "Extruded insulation board",
                "BOARD / DEMO",
                "کف و دیواره عایق",
                "Insulated floors and walls",
            ),
            (
                "rock-wool",
                "insulation",
                "عایق پشم سنگ",
                "Mineral wool insulation",
                "WOOL / DEMO",
                "عایق‌کاری تجهیزات صنعتی",
                "Industrial equipment insulation",
            ),
        ]
        for slug, code, fa, en, grade, apps_fa, apps_en in rows:
            Product.objects.get_or_create(
                slug=slug,
                defaults={
                    "category": categories[code],
                    "name_fa": fa,
                    "name_en": en,
                    "grade": grade,
                    "description_fa": f"{fa} برای نمایش ساختار کاتالوگ مواد صنعتی. این رکورد نمونه است؛ مشخصات نهایی باید بر اساس دیتاشیت معتبر سازنده و نیاز فنی پروژه تعیین شود.",
                    "description_en": f"{en} presented as an illustrative industrial catalog entry. This is demo data; final specifications must be confirmed against manufacturer documentation and project requirements.",
                    "applications_fa": apps_fa,
                    "applications_en": apps_en,
                },
            )
        for en, fa, conductivity, thickness, feature_fa, feature_en in [
            (
                "PU/PIR foam",
                "فوم پلی‌یورتان",
                "0.022–0.028",
                "5–10",
                "نمونه عایق سبک",
                "Illustrative lightweight insulation",
            ),
            (
                "XPS",
                "پلی‌استایرن اکسترود",
                "0.029–0.035",
                "8–14",
                "نمونه برد عایق",
                "Illustrative insulation board",
            ),
            (
                "EPS",
                "پلی‌استایرن منبسط",
                "0.032–0.038",
                "10–16",
                "نمونه ماده اقتصادی",
                "Illustrative economical material",
            ),
            (
                "Mineral wool",
                "پشم سنگ",
                "0.035–0.040",
                "10–18",
                "نمونه عایق الیافی",
                "Illustrative fibrous insulation",
            ),
        ]:
            InsulationType.objects.get_or_create(
                name_en=en,
                defaults={
                    "name_fa": fa,
                    "thermal_conductivity": conductivity,
                    "thickness_cm": thickness,
                    "feature_fa": feature_fa,
                    "feature_en": feature_en,
                },
            )
        for fa, en, category in [
            ("پروژه نمایشی سردخانه", "Fictional cold storage project", "cold_storage"),
            (
                "پروژه نمایشی تأمین صنعتی",
                "Fictional industrial sourcing project",
                "industrial",
            ),
        ]:
            Project.objects.get_or_create(
                title_en=en, defaults={"title_fa": fa, "category": category}
            )
        self.stdout.write(
            self.style.SUCCESS(
                "Demo catalog ready: 9 sample products. No accounts or inquiries created."
            )
        )
