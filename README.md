# TTA Group

A bilingual B2B catalog for industrial materials, built with Django. Visitors can browse products, review grades and technical documents, and submit an inquiry. Staff manage catalog content and follow up on requests through Django admin.

**Author:** Babak Mojaver

[راهنمای فارسی](START_HERE_FA.md) · [Code walkthrough / آموزش کد](docs/CODE_WALKTHROUGH_FA.md) · [GitHub guide](docs/GITHUB_FA.md) · [Architecture and deployment](docs/ARCHITECTURE.md) · [Company-content import](docs/CONTENT_UPDATE_FA.md)

## Stack

Python 3.12+ · Django 6.0 · SQLite · Django templates · CSS · JavaScript

The frontend uses local assets and requires no build step. Persian pages use Vazirmatn and English pages use Roboto. Both fonts are bundled with their license notices; the home hero uses the original project photograph.

## Features

- Persian RTL and English LTR, with language switching that retains the current page and search filters.
- Product search by name, grade and application; category filters, sorting and pagination.
- Product detail pages with bilingual descriptions, images and optional TDS/MSDS PDFs.
- Inquiry form with server-side validation, CSRF protection and a honeypot.
- Staff-only inquiry review with status tracking and a product-name snapshot.
- Publication controls that exclude inactive products from public pages, form choices and the sitemap.
- Editable insulation comparison data and project references.
- Canonical URLs, alternate-language links, sitemap and robots.txt.
- Repeatable company-content import, optional sample data, incremental migrations and automated tests.

## Product illustrations

[راهنمای نصب تصاویر روی نسخه فعلی](docs/PRODUCT_IMAGES_FA.md)

| Urea 46% | ABS resin | PM200 / MDI |
| --- | --- | --- |
| ![Urea fertilizer granules](static/images/products/urea.png) | ![Natural ABS resin pellets](static/images/products/abs.png) | ![Illustrative MDI drum and sample bottle](static/images/products/mdi.png) |

The three catalog illustrations are bundled under `static/images/products/`, so a fresh checkout displays them without a media upload. Home, catalog and detail pages share `Product.image_url`: an admin-uploaded photo takes precedence, followed by the bundled image for a known product slug, then a generic placeholder. The illustrations represent product types; they do not document a particular shipment or supplier package.

## Getting started

### Windows / PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py load_company_content
.\.venv\Scripts\python.exe manage.py runserver
```

### Linux / macOS

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py load_company_content
.venv/bin/python manage.py runserver
```

Open http://127.0.0.1:8000/fa/ or http://127.0.0.1:8000/en/.

Create an administrator using your virtual environment's Python:

```bash
python manage.py createsuperuser
```

The admin panel is available at `/fa/admin/` and `/en/admin/`. No default account is included.

## Checks

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py collectstatic --noinput
```

The 35 tests cover filtering, pagination, publication rules, language redirects, form validation, CSRF, admin permissions, upload validation, upgrades of existing catalog data and product image precedence. Local verification used Python 3.12.14 with the pinned runtime dependencies. The GitHub Actions workflow is configured for Python 3.12 and 3.13; a remote run has not yet been verified.

### Formatting

Development tools are separate from runtime dependencies:

```bash
python -m pip install -r requirements-dev.txt
python -m black --check .
python -m djlint templates --check
```

Use `python -m black .` and `python -m djlint templates --reformat` to apply formatting. Migrations keep their existing generated format. Comments explain data preservation, validation boundaries and query choices; ordinary field declarations and markup are left self-explanatory.

## Configuration

Local development works with the default settings. For deployment, use `config.settings_production` and configure:

- `DJANGO_SECRET_KEY`: a private random key.
- `DJANGO_ALLOWED_HOSTS`: the actual hostname(s).
- `DJANGO_SITE_URL`: the HTTPS origin used for canonical URLs and the sitemap.

`.env.example` lists the environment variables. It is a reference file and is not loaded automatically. The public development secret is rejected by the production settings.

Static assets are collected into `staticfiles/`. Uploads are stored in `media/`. Configure the hosting web server to serve both paths; `collectstatic` does not perform that configuration. See [deployment notes](docs/ARCHITECTURE.md) for HTTPS, trusted proxies and HSTS settings.

## Structure

| Path | Responsibility |
| --- | --- |
| `config/` | Settings, routing, WSGI and ASGI entry points |
| `products/` | Models, views, forms, admin and validators |
| `products/migrations/` | Schema changes and existing-product slug migration |
| `products/management/commands/` | Sample catalog initialization |
| `products/test*.py` | Behavior, upgrade, content preservation and product image tests |
| `templates/` | Pages and shared components |
| `static/` | Component styles, navigation script, local fonts and images |
| `docs/` | Architecture and operational notes |

## Current scope

Inquiries are saved in admin; email delivery, payments and customer accounts are not implemented. SQLite is used for local development. PostgreSQL support and shared request rate limiting are planned deployment improvements.

Company history, services, three original product descriptions and the refinery photograph come from the original project. The footer follows the latest supplied reference image, including its updated mobile number. English catalog copy translates the Persian source. The optional `seed_demo` command creates fictional sample records; it is not required to load the company catalog. Insulation ranges are reference values and should be checked against manufacturer documentation for engineering design. Upload checks validate size, extension and PDF headers; they do not provide malware scanning. A hosted demo is not currently included.
