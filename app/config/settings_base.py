"""
Django settings for app project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path

import environ

env = environ.Env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('SECRET_KEY', default=None)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'provider',
    'distributions',
    'access',
    'cognito',
    'bod'
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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env.str('DB_NAME', 'service_control'),
        'USER': env.str('DB_USER', 'service_control'),
        'PASSWORD': env.str('DB_PW', 'service_control'),
        'HOST': env.str('DB_HOST', 'service_control'),
        'PORT': env.str('DB_PORT', "5432"),
        'TEST': {
            'NAME': env.str('DB_NAME_TEST', 'test_service_control'),
        }
    },
    'bod': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env.str('BOD_NAME', 'service_control'),
        'USER': env.str('BOD_USER', 'service_control'),
        'PASSWORD': env.str('BOD_PW', 'service_control'),
        'HOST': env.str('BOD_HOST', 'service_control'),
        'PORT': env.str('BOD_PORT', "5432"),
        'OPTIONS': {
            'options': '-c search_path=public'
        },
    }
}

DATABASE_ROUTERS = ['utils.database_router.CustomRouter']

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Cognito
COGNITO_ENDPOINT_URL = env.str('COGNITO_ENDPOINT_URL', 'http://localhost:9229')
COGNITO_POOL_ID = env.str('COGNITO_POOL_ID', 'local')
COGNITO_MANAGED_FLAG_NAME = env.str('COGNITO_MANAGED_FLAG_NAME', 'dev:custom:managed_by_service')

# Testing
TESTING = False

# nanoid
SHORT_ID_SIZE = env.int('SHORT_ID_SIZE', 12)
SHORT_ID_ALPHABET = env.str('SHORT_ID_ALPHABET', '0123456789abcdefghijklmnopqrstuvwxyz')
