"""
Django settings for ndr_core project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/

# PyPI-Token: pypi-AgENdGVzdC5weXBpLm9yZwIkMWM5NzE2MzEtZjM4My00MmUxLWJjMDgtYjBhNjdmMjVjYWE2AAIleyJwZXJtaXNzaW9ucyI6ICJ1c2VyIiwgInZlcnNpb24iOiAxfQAABiCp36thAms1p2VbkuxN6TCyJVBrSVCZ8jQ7r9x-Vz7lAQ
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
from django.contrib import messages

BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-tv6meg%j0=z2(d37_7hb(2t%+zeiq45hw=o0d$kcbz)*2no97s'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'ndr_core_ui',
    'ndr_core_api',
    'main',
    'django_static_fontawesome',
    'bootstrap4',
    'crispy_forms',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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

ROOT_URLCONF = 'ndr_core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'ndr_core_ui.context_processors.info_bite',
                'ndr_core_ui.context_processors.carousel_info',
            ],
        },
    },
]

WSGI_APPLICATION = 'ndr_core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_TEMPLATE_PACK = 'bootstrap4'

MESSAGE_TAGS = {
        messages.DEBUG: 'alert-secondary',
        messages.INFO: 'alert-info',
        messages.SUCCESS: 'alert-success',
        messages.WARNING: 'alert-warning',
        messages.ERROR: 'alert-danger',
 }

NDR_CORE_API_CONFIG = {
    "use_dummy_result": True,
    "dummy_result_file": "main/dummy_result.json",
    "api_host": "ghiodata.int",
    "api_protocol": "http",
    "api_port": 80,
    "page_size": 10,
    "search_fields":
        {
            "book_title": {
                "type": "string",
                "required": False,
                "api_param": "title"
            },
            "year": {
                "type": "number-range",
                "number-range": {
                    "min_number": 1863,
                    "max_number": 1950
                }
            },
            "language": {
                "type": "dictionary",
                "api_param": "lang",
                "dictionary": {
                    "type": "tsv",
                    "file": "main/languages.tsv",
                    "search_column": 0,
                    "display_column": 1,
                    "has_title_row": True
                },
                "widget": "default"
            },
            "section_type": {
                "type": "dictionary",
                "api_param": "stype",
                "dictionary": {
                    "type": "tsv",
                    "file": "main/section_type.tsv",
                    "search_column": 0,
                    "display_column": 1,
                    "has_title_row": True
                },
                "widget": "default"
            },
            "table_type": {
                "type": "dictionary",
                "api_param": "inscat",
                "dictionary": {
                    "type": "tsv",
                    "file": "main/table_type.tsv",
                    "search_column": 0,
                    "display_column": 1,
                    "has_title_row": True
                },
                "widget": "multi_search"
            },
            "territory": {
                "type": "dictionary",
                "api_param": "ter",
                "dictionary": {
                    "type": "tsv",
                    "file": "main/territory.tsv",
                    "search_column": 0,
                    "display_column": 1,
                    "has_title_row": True
                },
                "widget": "multi_search"
            }
        },
        "configurations": {
            "advanced": ["__all__", ]
        }
    }


NDR_CORE_UI_CONFIG = {
    "header_title": "Kitler Lectures",
    "header_author": "Lea Kasper",
    "header_description": "History",
    "website_title": "Welcome To The Kitler Lecture Archives",

    "main_view": "main:index",
    "search_view": "main:search",

    "footer_text": "(c) 2022, Institute For European Global Studies"
}
