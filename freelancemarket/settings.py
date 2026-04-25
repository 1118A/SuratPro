import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    # Jazzmin MUST come before django.contrib.admin
    'jazzmin',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party
    'rest_framework',
    'crispy_forms',
    'crispy_bootstrap5',

    # Project apps
    'accounts',
    'jobs',
    'proposals',
    'contracts',
    'payments',
    'messaging',
    'reviews',
    'notifications',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'freelancemarket.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'notifications.context_processors.notification_count',
                'messaging.context_processors.unread_messages_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'freelancemarket.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.User'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# =============================================================
#  JAZZMIN ADMIN CONFIGURATION
# =============================================================

JAZZMIN_SETTINGS = {
    # ---- Branding ----
    "site_title": "SuratPro Admin",
    "site_header": "SuratPro",
    "site_brand": "SuratPro",
    "site_logo": None,
    "login_logo": None,
    "login_logo_dark": None,
    "site_logo_classes": "img-circle",
    "site_icon": "img/favicon_io/favicon-32x32.png",
    "welcome_sign": "Welcome to SuratPro Admin — Surat's Freelance Marketplace",
    "copyright": "SuratPro Technologies Pvt. Ltd.",

    # ---- Search ----
    "search_model": ["accounts.User"],

    # ---- Top navigation links ----
    "topmenu_links": [
        {"name": "Dashboard",   "url": "admin:index",            "permissions": ["auth.view_user"]},
        {"name": "Users",       "url": "admin:accounts_user_changelist"},
        {"name": "View Site",   "url": "/",                      "new_window": True},
    ],

    # ---- User menu (top-right dropdown) ----
    "usermenu_links": [
        {"name": "View Site",   "url": "/",  "new_window": True, "icon": "fas fa-home"},
        {"model": "accounts.user"},
    ],

    # ---- Left sidebar navigation ----
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],

    # ---- Custom sidebar ordering ----
    "order_with_respect_to": [
        "accounts",
        "accounts.user",
        "jobs",
        "proposals",
        "contracts",
        "payments",
        "messaging",
        "reviews",
        "notifications",
        "auth",
    ],

    # ---- Custom sidebar links (section headers + links) ----
    "custom_links": {
        "accounts": [
            {
                "name": "Freelancers",
                "url": "/admin/accounts/user/?role__exact=freelancer",
                "icon": "fas fa-laptop-code",
                "permissions": ["accounts.view_user"],
            },
            {
                "name": "Clients",
                "url": "/admin/accounts/user/?role__exact=client",
                "icon": "fas fa-building",
                "permissions": ["accounts.view_user"],
            },
        ],
    },

    # ---- Bootstrap Icons for each model ----
    "icons": {
        "auth":                       "fas fa-users-cog",
        "auth.group":                 "fas fa-layer-group",
        "accounts.user":              "fas fa-user-circle",
        "jobs.job":                   "fas fa-briefcase",
        "proposals.proposal":         "fas fa-file-alt",
        "contracts.contract":         "fas fa-handshake",
        "payments.payment":           "fas fa-credit-card",
        "messaging.message":          "fas fa-comments",
        "reviews.review":             "fas fa-star",
        "notifications.notification": "fas fa-bell",
    },
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-circle",

    # ---- UI Tweaks ----
    "related_modal_active": True,
    "custom_css": "admin/css/custom_admin.css",
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,

    # ---- Change view ----
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user":  "collapsible",
        "auth.group": "vertical_tabs",
    },

    # ---- Language chooser ----
    "language_chooser": False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-light",
    "accent": "accent-primary",
    "navbar": "navbar-white navbar-light",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-light-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    "theme": "default",
    "default_theme_mode": "light",
    "button_classes": {
        "primary":   "btn-primary",
        "secondary": "btn-secondary",
        "info":      "btn-info",
        "warning":   "btn-warning",
        "danger":    "btn-danger",
        "success":   "btn-success",
    },
    "actions_sticky_top": True,
}
