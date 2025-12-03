"""
Django settings for proyecto_creditos project.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-#lsa5-ltu6#lj#ejm#75xtk9te1)8z@-4qazg%oo4_p%0@su+h'

DEBUG = True

ALLOWED_HOSTS = ['*']  # Permite todos los hosts en desarrollo

# CSRF Configuration
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000', 'http://localhost:8000']
SESSION_COOKIE_SECURE = False  # Permite cookies en HTTP (desarrollo)
CSRF_COOKIE_SECURE = False     # Permite CSRF en HTTP (desarrollo)
CSRF_COOKIE_HTTPONLY = False   # JavaScript puede leer el token CSRF


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'usuarios',
    'creditos',
    'actividades',
]
AUTH_USER_MODEL = 'usuarios.Usuario'
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'proyecto_creditos.urls'

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

WSGI_APPLICATION = 'proyecto_creditos.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


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


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'usuarios.Usuario'

# Cuando un usuario inicia sesión, lo mandamos a inicio (ya decides si va a perfil o panel)
LOGIN_REDIRECT_URL = '/inicio/'

# Cuando cierra sesión, lo mandamos al login general
LOGOUT_REDIRECT_URL = '/login/'

# Ruta de login por defecto (para alumnos/admins)
LOGIN_URL = '/login/'

# Si quieres que los docentes usen su propia ruta de login en los correos:
SITE_URL = 'https://tusitio.com'   # cámbialo por tu dominio real
DOCENTE_INVITE_CODE = 'CAMBIA-ESTE-CODIGO'

# Smart Contract (Algorand) integration settings
# - ENABLED: activar/desactivar llamadas on-chain desde la vista de descarga
# - APP_ID: id de la aplicación desplegada (si ya la tienes)
# - SIGNER_MNEMONIC: mnemonic del account que enviará la firma (opcional)
# Nota: por seguridad no dejes mnemonics en el repo en producción; usa variables de entorno.
def _env_bool(key, default=False):
    v = os.getenv(key)
    if v is None:
        return default
    return str(v).lower() in ('1', 'true', 'yes', 'on')

def _env_int(key):
    v = os.getenv(key)
    if v is None or v == '':
        return None
    try:
        return int(v)
    except Exception:
        return None

SMART_CONTRACT = {
    'ENABLED': _env_bool('SMART_CONTRACT_ENABLED', False),
    'DEPLOY_PER_CREDITO': _env_bool('SMART_CONTRACT_DEPLOY_PER_CREDITO', False),
    'APP_ID': _env_int('SMART_CONTRACT_APP_ID'),
    'SIGNER_MNEMONIC': os.getenv('SMART_CONTRACT_SIGNER_MNEMONIC', ''),
    'ADMIN_MNEMONIC': os.getenv('SMART_CONTRACT_ADMIN_MNEMONIC', ''),
    'STUDENT_MNEMONIC': os.getenv('SMART_CONTRACT_STUDENT_MNEMONIC', ''),
    'OFFICER_MNEMONIC': os.getenv('SMART_CONTRACT_OFFICER_MNEMONIC', ''),
}


