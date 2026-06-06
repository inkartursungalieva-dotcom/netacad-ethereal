import os
import dj_database_url
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
ALLOWED_HOSTS = [x.strip() for x in os.getenv('ALLOWED_HOSTS', '*').split(',') if x.strip()]
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ['*']

# Доверяем доменам для CSRF
CSRF_TRUSTED_ORIGINS = [
    'https://*.pythonanywhere.com',
    'https://*.onrender.com',
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'http://0.0.0.0:8000',
]
_extra_csrf = os.getenv('CSRF_TRUSTED_ORIGINS', '')
if _extra_csrf:
    CSRF_TRUSTED_ORIGINS.extend(
        [x.strip() for x in _extra_csrf.split(',') if x.strip()]
    )

# Добавляем текущий хост Render в доверенные
render_url = os.getenv('RENDER_EXTERNAL_URL')
if render_url:
    # Добавляем и с https и без, если вдруг
    CSRF_TRUSTED_ORIGINS.append(render_url)
    # Также извлекаем домен
    from urllib.parse import urlparse
    domain = urlparse(render_url).netloc
    if domain:
        CSRF_TRUSTED_ORIGINS.append(f"https://{domain}")
        CSRF_TRUSTED_ORIGINS.append(f"http://{domain}")
    
# HTTPS за обратным прокси (Render и др.)
if os.getenv('RENDER') or os.getenv('PYTHONANYWHERE_DOMAIN'):
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_X_FORWARDED_HOST = True
    # На Render часто возникают проблемы с куками если они слишком строгие
    # SESSION_COOKIE_SECURE = True
    # CSRF_COOKIE_SECURE = True
    # Оставляем стандартные для начала, чтобы "просто работало"
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False') == 'True'
    CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'False') == 'True'


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

# Настройка БД (Приоритет: DATABASE_URL -> MySQL -> SQLite)
db_url = os.getenv('DATABASE_URL')
if db_url:
    try:
        DATABASES = {
            'default': dj_database_url.config(
                default=db_url,
                conn_max_age=0, # Отключаем persistent connections для стабильности на free tier
            )
        }
    except Exception as e:
        print(f"⚠️ [ERROR] Invalid DATABASE_URL: {e}. Falling back to SQLite.")
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
elif os.getenv('RENDER') or os.getenv('PYTHONANYWHERE_DOMAIN'):
    # Если на Render/PA но нет DATABASE_URL, используем SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    # Локальная настройка: пробуем MySQL, иначе SQLite
    USE_SQLITE = False
    if not DB_NAME:
        USE_SQLITE = True
    else:
        try:
            import MySQLdb
            conn = MySQLdb.connect(
                host=DB_HOST,
                user=DB_USER,
                passwd=DB_PASSWORD,
                port=int(DB_PORT),
                connect_timeout=2
            )
            conn.close()
        except (ImportError, Exception):
            print("⚠️ [WARNING] MySQL недоступен. Используем SQLite.")
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

# API Keys
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
# =============================================================================
# 📧 EMAIL CONFIGURATION - config/settings.py
# =============================================================================

# 🔐 Gmail SMTP настройки
if os.getenv('RENDER'):
    # На Render отключаем SMTP чтобы не было таймаутов (10 сек)
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False') == 'True'
EMAIL_TIMEOUT = 10

# Почта: пароль только через переменные окружения (.env локально, Dashboard на Render)
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'inkartursungalieva@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')

DEFAULT_FROM_EMAIL = f"Computer Networks <{EMAIL_HOST_USER}>"
SERVER_EMAIL = EMAIL_HOST_USER
EMAIL_TIMEOUT = 10
EMAIL_SUBJECT_PREFIX = '[Computer Networks] '

# Для отладки
if DEBUG:
    # Раскомментируйте строку ниже, чтобы письма выводились в консоль при отладке
    # EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    pass
# =============================================================================

# Настройки бизнес-логики
TEST_PASS_PERCENTAGE = 70  # Процент правильных ответов для прохождения теста

# Логирование для отладки 500 ошибок в облаке
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# =============================================================================
# 🔐 ALLAUTH CONFIGURATION
# =============================================================================
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

LOGIN_URL = 'accounts:login'
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

# Allauth settings
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_QUERY_EMAIL = True
