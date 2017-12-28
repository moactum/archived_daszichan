import os
from datetime import timedelta
from daszichan.settings import INSTALLED_APPS, BASE_DIR, SECRET_KEY
from rest_framework.settings import api_settings
#BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ALLOWED_HOSTS = ['*',]

INSTALLED_APPS += [
	'corsheaders',
	'rest_framework',
	#'rest_framework_simplejwt.token_blacklist',
	#'rest_framework.authtoken',
]

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'corsheaders.middleware.CorsMiddleware',
	#'whitenoise.middleware.WhiteNoiseMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

DATABASES = {
#	'default': {
#	'ENGINE': 'django.db.backends.sqlite3',
#	'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#	},
	'default': {
		'ENGINE': 'django.db.backends.mysql',
		'NAME': 'test',								  # Or path to database file if using sqlite3.
		'HOST': 'localhost',						  # Set to empty string for localhost. Not used with sq
		'USER': 'root',								# Not used with sqlite3.
		'PASSWORD': 'root',				  # Not used with sqlite3.
		'PORT': '',
	}
}

#LOGIN_REDIRECT_URL = "/task.jsp/"
#LOGIN_URL = "/accounts/login/"
#LOGOUT_URL = "/accounts/logout/"
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads')

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=3),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,

    'AUTH_HEADER_TYPES': ('Bearer','JWT'),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(days=3),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=30),
}

REST_FRAMEWORK = {
	'DEFAULT_PERMISSION_CLASSES': [
		#'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
		#'rest_framework.permissions.AllowAny'
		#'rest_framework.permissions.IsAuthenticatedOrReadOnly'
		'rest_framework.permissions.IsAuthenticated'
	],
	'DEFAULT_AUTHENTICATION_CLASSES': (
		*api_settings.defaults['DEFAULT_AUTHENTICATION_CLASSES'],
		'rest_framework_simplejwt.authentication.JWTAuthentication'
	)
	#'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
	#'PAGE_SIZE': 100
}
#STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
TIMEZONE = 'America/Toronto'
USE_TZ =  True
#CORS_ORIGIN_ALLOW_ALL = True
#CORS_ORIGIN_WHITELIST = (
#	'localhost',
#	'read.only.com',
#	'change.allowed.com',
#)
#
#CSRF_TRUSTED_ORIGINS = (
#	'localhost',
#	'change.allowed.com',
#)
#CSRF_COOKIE_NAME = 'XSRF-TOKEN'
#CSRF_HEADER_NAME = 'HTTP_X_XSRF_TOKEN'
