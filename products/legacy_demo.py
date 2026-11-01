"""Exact legacy seed values used only to recognize untouched sample records.

Keep these snapshots stable: an import must not mistake staff-edited content
for demo data and overwrite it during a later update.
"""

PRODUCTS = {
    "hdpe-pipe": {
        "name_fa": "پلی\u200cاتیلن سنگین",
        "name_en": "High-density polyethylene",
        "grade": "PIPE / DEMO",
        "applications_fa": "تولید لوله و اتصالات",
        "applications_en": "Pipes and fittings",
        "description_fa": "پلی\u200cاتیلن سنگین برای نمایش ساختار کاتالوگ مواد صنعتی. این "
        "رکورد نمونه است؛ مشخصات نهایی باید بر اساس دیتاشیت معتبر سازنده "
        "و نیاز فنی پروژه تعیین شود.",
        "description_en": "High-density polyethylene presented as an illustrative "
        "industrial catalog entry. This is demo data; final "
        "specifications must be confirmed against manufacturer "
        "documentation and project requirements.",
    },
    "pp-fiber": {
        "name_fa": "پلی\u200cپروپیلن الیافی",
        "name_en": "Polypropylene fiber resin",
        "grade": "FIBER / DEMO",
        "applications_fa": "الیاف و منسوجات",
        "applications_en": "Fibers and textiles",
        "description_fa": "پلی\u200cپروپیلن الیافی برای نمایش ساختار کاتالوگ مواد صنعتی. این "
        "رکورد نمونه است؛ مشخصات نهایی باید بر اساس دیتاشیت معتبر سازنده و "
        "نیاز فنی پروژه تعیین شود.",
        "description_en": "Polypropylene fiber resin presented as an illustrative industrial "
        "catalog entry. This is demo data; final specifications must be "
        "confirmed against manufacturer documentation and project "
        "requirements.",
    },
    "abs-injection": {
        "name_fa": "رزین ای\u200cبی\u200cاس",
        "name_en": "ABS injection resin",
        "grade": "INJECTION / DEMO",
        "applications_fa": "قطعات تزریقی و لوازم خانگی",
        "applications_en": "Molded parts and appliances",
        "description_fa": "رزین ای\u200cبی\u200cاس برای نمایش ساختار کاتالوگ مواد "
        "صنعتی. این رکورد نمونه است؛ مشخصات نهایی باید بر اساس "
        "دیتاشیت معتبر سازنده و نیاز فنی پروژه تعیین شود.",
        "description_en": "ABS injection resin presented as an illustrative industrial "
        "catalog entry. This is demo data; final specifications must "
        "be confirmed against manufacturer documentation and project "
        "requirements.",
    },
    "mdi-component": {
        "name_fa": "ایزوسیانات پلیمری",
        "name_en": "Polymeric MDI component",
        "grade": "FOAM / DEMO",
        "applications_fa": "فرمولاسیون فوم سخت",
        "applications_en": "Rigid foam formulation",
        "description_fa": "ایزوسیانات پلیمری برای نمایش ساختار کاتالوگ مواد صنعتی. این "
        "رکورد نمونه است؛ مشخصات نهایی باید بر اساس دیتاشیت معتبر "
        "سازنده و نیاز فنی پروژه تعیین شود.",
        "description_en": "Polymeric MDI component presented as an illustrative "
        "industrial catalog entry. This is demo data; final "
        "specifications must be confirmed against manufacturer "
        "documentation and project requirements.",
    },
    "polyol-blend": {
        "name_fa": "پلی\u200cال ترکیبی",
        "name_en": "Polyol blend",
        "grade": "BLEND / DEMO",
        "applications_fa": "تولید فوم و عایق",
        "applications_en": "Foam and insulation production",
        "description_fa": "پلی\u200cال ترکیبی برای نمایش ساختار کاتالوگ مواد صنعتی. این "
        "رکورد نمونه است؛ مشخصات نهایی باید بر اساس دیتاشیت معتبر "
        "سازنده و نیاز فنی پروژه تعیین شود.",
        "description_en": "Polyol blend presented as an illustrative industrial catalog "
        "entry. This is demo data; final specifications must be "
        "confirmed against manufacturer documentation and project "
        "requirements.",
    },
    "urea-granules": {
        "name_fa": "اوره گرانول",
        "name_en": "Granular urea",
        "grade": "GRANULAR / DEMO",
        "applications_fa": "فرآوری مواد شیمیایی",
        "applications_en": "Chemical processing",
        "description_fa": "اوره گرانول برای نمایش ساختار کاتالوگ مواد صنعتی. این رکورد "
        "نمونه است؛ مشخصات نهایی باید بر اساس دیتاشیت معتبر سازنده و "
        "نیاز فنی پروژه تعیین شود.",
        "description_en": "Granular urea presented as an illustrative industrial "
        "catalog entry. This is demo data; final specifications must "
        "be confirmed against manufacturer documentation and project "
        "requirements.",
    },
    "pu-panel": {
        "name_fa": "پنل پلی\u200cیورتان",
        "name_en": "Polyurethane insulation panel",
        "grade": "PANEL / DEMO",
        "applications_fa": "سردخانه و ساختمان صنعتی",
        "applications_en": "Cold storage and industrial buildings",
        "description_fa": "پنل پلی\u200cیورتان برای نمایش ساختار کاتالوگ مواد صنعتی. این "
        "رکورد نمونه است؛ مشخصات نهایی باید بر اساس دیتاشیت معتبر سازنده و "
        "نیاز فنی پروژه تعیین شود.",
        "description_en": "Polyurethane insulation panel presented as an illustrative "
        "industrial catalog entry. This is demo data; final specifications "
        "must be confirmed against manufacturer documentation and project "
        "requirements.",
    },
    "xps-board": {
        "name_fa": "برد عایق اکسترود",
        "name_en": "Extruded insulation board",
        "grade": "BOARD / DEMO",
        "applications_fa": "کف و دیواره عایق",
        "applications_en": "Insulated floors and walls",
        "description_fa": "برد عایق اکسترود برای نمایش ساختار کاتالوگ مواد صنعتی. این رکورد "
        "نمونه است؛ مشخصات نهایی باید بر اساس دیتاشیت معتبر سازنده و نیاز "
        "فنی پروژه تعیین شود.",
        "description_en": "Extruded insulation board presented as an illustrative "
        "industrial catalog entry. This is demo data; final "
        "specifications must be confirmed against manufacturer "
        "documentation and project requirements.",
    },
    "rock-wool": {
        "name_fa": "عایق پشم سنگ",
        "name_en": "Mineral wool insulation",
        "grade": "WOOL / DEMO",
        "applications_fa": "عایق\u200cکاری تجهیزات صنعتی",
        "applications_en": "Industrial equipment insulation",
        "description_fa": "عایق پشم سنگ برای نمایش ساختار کاتالوگ مواد صنعتی. این رکورد "
        "نمونه است؛ مشخصات نهایی باید بر اساس دیتاشیت معتبر سازنده و نیاز "
        "فنی پروژه تعیین شود.",
        "description_en": "Mineral wool insulation presented as an illustrative industrial "
        "catalog entry. This is demo data; final specifications must be "
        "confirmed against manufacturer documentation and project "
        "requirements.",
    },
}

INSULATIONS = {
    "PU/PIR foam": {
        "name_en": "PU/PIR foam",
        "name_fa": "فوم پلی\u200cیورتان",
        "thermal_conductivity": "0.022–0.028",
        "thickness_cm": "5–10",
        "feature_fa": "نمونه عایق سبک",
        "feature_en": "Illustrative lightweight insulation",
    },
    "XPS": {
        "name_en": "XPS",
        "name_fa": "پلی\u200cاستایرن اکسترود",
        "thermal_conductivity": "0.029–0.035",
        "thickness_cm": "8–14",
        "feature_fa": "نمونه برد عایق",
        "feature_en": "Illustrative insulation board",
    },
    "EPS": {
        "name_en": "EPS",
        "name_fa": "پلی\u200cاستایرن منبسط",
        "thermal_conductivity": "0.032–0.038",
        "thickness_cm": "10–16",
        "feature_fa": "نمونه ماده اقتصادی",
        "feature_en": "Illustrative economical material",
    },
    "Mineral wool": {
        "name_en": "Mineral wool",
        "name_fa": "پشم سنگ",
        "thermal_conductivity": "0.035–0.040",
        "thickness_cm": "10–18",
        "feature_fa": "نمونه عایق الیافی",
        "feature_en": "Illustrative fibrous insulation",
    },
}
