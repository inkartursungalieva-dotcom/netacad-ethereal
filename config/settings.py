import os
from pathlib import Path
from dotenv import load_dotenv # pyright: ignore[reportMissingImports]

load_dotenv()  # Загрузка переменных из .env

# Поддержка MySQL через PyMySQL (чтобы не было проблем при установке на Render)
try:
    import pymysql # pyright: ignore
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-key-for-dev-only')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# ALLOWED_HOSTS
ALLOWED_HOSTS = ['*'] # Для отладки в облаке разрешаем всё


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Required for allauth

    # Allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    'accounts',
    'courses',
    'laboratory',
    'core',
    'dashboard',

    # 'rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # Add this
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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
                'django.template.context_processors.i18n', 
                'dashboard.context_processors.dashboard_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# Параметры из .env
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = os.getenv('DB_PORT', '3306')

# На бесплатном тарифе Render используем SQLite (надежно и бесплатно)
if os.getenv('RENDER'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    # Попытка подключения к MySQL, если нет - используем SQLite (для портативности на защите)
    USE_SQLITE = False
    if not DB_NAME:
        USE_SQLITE = True
    else:
        try:
            # Пытаемся подключиться к MySQL через MySQLdb (который теперь pymysql)
            import MySQLdb
            # Быстрая проверка доступности MySQL
            conn = MySQLdb.connect(
                host=DB_HOST,
                user=DB_USER,
                passwd=DB_PASSWORD,
                port=int(DB_PORT),
                connect_timeout=2
            )
            conn.close()
        except (ImportError, Exception):
            print("⚠️ [WARNING] MySQL недоступен или библиотека не установлена. Используем SQLite.")
            USE_SQLITE = True

    if USE_SQLITE:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': DB_NAME,
                'USER': DB_USER,
                'PASSWORD': DB_PASSWORD,
                'HOST': DB_HOST,
                'PORT': DB_PORT,
                'OPTIONS': {
                    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                    'charset': 'utf8mb4',
                },
            }
        }


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/


LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Asia/Almaty'

USE_TZ = True

USE_I18N = True
LOCALE_PATHS = [BASE_DIR / 'locale']
LANGUAGES = [('ru', 'Русский'), ('kk', 'Қазақша')]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise storage for compression and caching
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


AUTH_USER_MODEL = 'accounts.User'
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# =============================================================================
# 📧 EMAIL CONFIGURATION - config/settings.py
# =============================================================================

# 🔐 Gmail SMTP настройки
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

# ← ВСТАВЬТЕ СЮДА ВАШ ДАННЫЕ:
EMAIL_HOST_USER = 'inkartursungalieva@gmail.com'  # Ваш полный Gmail
EMAIL_HOST_PASSWORD = 'hoighjzrmrekxgov'  # App Password (16 символов, БЕЗ ПРОБЕЛОВ!)

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER
EMAIL_TIMEOUT = 30
EMAIL_SUBJECT_PREFIX = '[NetAcad Ethereal] '

# Для отладки
if DEBUG:
    # Раскомментируйте строку ниже, чтобы письма выводились в консоль при отладке
    # EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    pass
# =============================================================================

# Настройки бизнес-логики
TEST_PASS_PERCENTAGE = 70  # Процент правильных ответов для прохождения теста

# =============================================================================
# 🔐 ALLAUTH CONFIGURATION
# =============================================================================
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

LOGIN_REDIRECT_URL = 'dashboard:index'
LOGOUT_REDIRECT_URL = 'home'

# Allauth SocialAccount Settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
    }
}

# Если мы хотим, чтобы аллаут не требовал подтверждения email для соц.сетей
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_QUERY_EMAIL = True

ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email', 'password1']
