# انتشار پروژه در Git و GitHub

دستورها را در پوشه‌ای اجرا کن که `manage.py` و `.gitignore` داخل آن هستند. این راهنما مخزن جدید می‌سازد؛ اگر پروژه از قبل مخزن دارد، ابتدا `git status` و `git remote -v` را بررسی کن و مخزن تازه نساز.

## آماده‌سازی

در PowerShell ابتدا بررسی کن Git نصب است:

```powershell
git --version
```

کد پروژه را از ZIP استخراج کن. خود ZIP نباید جای فایل‌های پروژه داخل مخزن قرار بگیرد. نسخه فعلی را ابتدا محلی اجرا و تست کن:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py test
```

`.gitignore` محیط مجازی، دیتابیس محلی، فایل‌های محیطی، آپلودها و خروجی collectstatic را کنار می‌گذارد. این فایل، فایل‌های ازقبل‌ردیابی‌شده را از تاریخچه Git حذف نمی‌کند.

## ساخت مخزن محلی

```powershell
git init
git branch -M main
git status
```

نام و ایمیل Git را برای همین مخزن تنظیم کن. مقادیر زیر نمونه‌اند؛ قبل از اجرا با اطلاعات خودت جایگزین کن. اگر ایمیلت نباید عمومی باشد، ایمیل noreply حساب GitHub خودت را استفاده کن.

```powershell
git config user.name "YOUR NAME"
git config user.email "YOUR GITHUB EMAIL"
git add .
git diff --cached --stat
git diff --cached
```

فایل‌های مرحله‌بندی‌شده را مرور کن. اطلاعات حساب مشتری، کلید خصوصی و دیتابیس شخصی نباید در فهرست باشند. سپس کامیت واقعی همین نسخه را ثبت کن:

```powershell
git commit -m "Add bilingual industrial catalog and inquiry workflow"
```

## ساخت مخزن GitHub و ارسال

در حساب خودت یک مخزن خالی با نام `django-industrial-catalog` بساز. برای دیده‌شدن توسط کارفرما، حالت Public را انتخاب کن. چون پروژه README و `.gitignore` دارد، گزینه ساخت این فایل‌ها در GitHub را فعال نکن.

توضیح پیشنهادی مخزن:

> Bilingual Django catalog with product search, quote requests, staff administration and automated tests.

آدرس مخزن را از GitHub کپی کن و جای مقدار نمونه بگذار:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/django-industrial-catalog.git
git remote -v
git push -u origin main
```

اگر صفحه ورود باز شد با حساب خودت وارد شو. توکن یا رمز را داخل فایل پروژه، آدرس remote یا پیام چت قرار نده.

## بررسی نتیجه

- README باید در صفحه اصلی مخزن نمایش داده شود.
- تب Actions باید اجرای `Django checks` را نشان بدهد. سبزشدن آن را بعد از اولین push بررسی کن؛ آماده‌بودن workflow به معنی اجرای موفق روی GitHub نیست.
- نام پوشه‌های `config`، `products`، `templates` و `static` باید در ریشه مخزن باشند.
- موضوع‌های مناسب مخزن: `django`، `python`، `b2b`، `rtl`، `internationalization` و `portfolio`.
- پس از تأیید ظاهر، تصاویر واقعی پروژه را به README اضافه کن. لینک دمو را پس از راه‌اندازی هاست قرار بده.

برای تغییرات بعدی، پیام کامیت باید تغییر واقعی را توصیف کند. پس از ویرایش و بررسی:

```powershell
git status
git diff
git add PATH_TO_CHANGED_FILE
git commit -m "Describe the actual change"
git push
```

نام فایل و پیام آخر نمونه‌اند؛ آن‌ها را متناسب با تغییرت بنویس. این راهنما چیزی را روی حساب GitHub تو منتشر نمی‌کند؛ ارسال با دستور push روی سیستم خودت انجام می‌شود.
