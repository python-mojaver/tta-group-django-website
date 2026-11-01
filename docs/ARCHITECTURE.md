# Architecture and operational notes

## Request flow

Django LocaleMiddleware chooses Persian or English from `/fa/` and `/en/`. Views query models and render templates; `LocalizedModel` exposes translated values. Product lists use `select_related` and database pagination. Product documents/images are optional; no fake downloadable files are rendered.

`GET /<lang>/contact/?product=<slug>` preselects an active product. POST validates the ModelForm and records a `QuoteRequest` plus a product-name snapshot. A successful POST redirects to GET, preventing browser refresh from repeating the same POST. This is not a universal idempotency guarantee against double clicks/network retries.

Only authenticated staff with model permissions can review requests in Django admin. No public request-list API exists. Uploaded images/PDFs are entered by staff, not through the public inquiry form.

The language endpoint wraps Django's `set_language` under the source URL's language, addressing cookie/URL-language mismatches. Django still performs redirect-host and language validation. The hidden `next` field supplies the full current path and query.

## Data model

- Category → Product: existing bilingual category/product fields retained.
- Product: unique slug, publication state and modification timestamp added.
- Product → QuoteRequest: optional link with SET_NULL; name snapshot survives product deletion.
- InsulationType: one editable source for the comparison table on both pages.
- Project: bilingual title and category with optional image.

Migration 0003 first adds nullable unique slugs, fills them using a name plus primary key, then makes the field non-nullable. This avoids collisions when upgrading existing products with equal English names. The original 0001/0002 migrations are retained. Always back up a real database before upgrading. Local installations start with an empty database; load_company_content imports the three original company catalog entries and the shared insulation table. The optional seed_demo command adds fictional examples.

## Production configuration

Use a real WSGI/ASGI server and a separately configured HTTPS reverse proxy. Django `runserver` is for local development only.

Set the following in the hosting environment:

```text
DJANGO_SETTINGS_MODULE=config.settings_production
DJANGO_SECRET_KEY=<private random key of at least 50 characters>
DJANGO_ALLOWED_HOSTS=<your actual hostname>
DJANGO_SITE_URL=https://<your actual hostname>
```

Generate a key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Set `DJANGO_TRUST_PROXY=true` only when a trusted reverse proxy removes client-supplied forwarding headers and sets `X-Forwarded-Proto` correctly. Otherwise the default remains false. This choice depends on the host.

Run migrations and `collectstatic`. Configure the host to serve `STATIC_ROOT` at `/static/` and `MEDIA_ROOT` at `/media/` as inert files. Do not execute uploaded content. Back up database and media together, restrict admin access, and add production monitoring as part of real hosting work.

```bash
python manage.py check --deploy --settings=config.settings_production
```

Expected advisory warnings: W005 and W021. HSTS applies to the configured host for one hour. Include-subdomains and preload stay off because a generic portfolio cannot assume every subdomain has HTTPS or authorize a preload commitment. These warnings are documented, not silenced; CI fails on errors while retaining the warnings. A concrete host should decide these settings deliberately.

`.env.example` is documentation; the project uses `os.environ`, not dotenv. It is not a secret store or an auto-loaded configuration file.

## Tested versus planned

Tested locally on Python 3.12.14 with Django 6.0.9, Pillow 12.3.0, asgiref 3.12.1, sqlparse 0.6.0 and tzdata 2026.3. All 35 tests pass, including a real upgrade from migration 0002 with duplicate product names and a staff status-change test that preserves submitted contact details. The GitHub workflow also targets Python 3.13; a remote run has not yet been verified. PostgreSQL, email delivery, Docker, hosting and domain configuration are not implemented.

Before operating a public inquiry form for real customers, add shared rate limiting, retention/privacy policies and appropriate email delivery/monitoring. File extension/header/size validation is not malware scanning. This is a portfolio baseline, not a claim of a completed penetration test.

## Technical references

- [Django deployment checklist](https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/)
- [Django internationalization](https://docs.djangoproject.com/en/6.0/topics/i18n/translation/)
- [Django 6.0.9 security release, 2026-10-06](https://www.djangoproject.com/weblog/2026/oct/06/security-releases/)

## Company content

`config/company.py` holds shared bilingual company copy and contact details. Services and competitive advantages are shared template components. `products/company_catalog.py` contains the original three catalog entries and the four insulation rows. `load_company_content` recognizes exact legacy demo text before replacing it; edited records are preserved and reported. It retains product IDs, categories, publication states, uploaded files and inquiry links. Untouched extra demo products without attachments are unpublished rather than deleted. `products/legacy_demo.py` is a compatibility snapshot; do not rewrite it when updating future sample data.

## Product images

`products/assets.py` maps the three original product slugs to bundled PNG illustrations. The `Product.image_url` property resolves uploaded media first, then the mapped static asset, then the generic illustration for other products. Both card and detail templates use the same property. This changes no database fields and requires no migration. Run `collectstatic` before deployment and configure `/static/` on the host; uploaded replacements remain in `/media/` and are not committed to Git.
