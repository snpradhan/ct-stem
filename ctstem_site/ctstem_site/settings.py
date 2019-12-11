"""
Django settings for ctstem_site project.

Generated by 'django-admin startproject' using Django 1.8.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

from .base_settings import *

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'nlzkjs+7u#q+v_6hv2$!y5+t#@yjje9vqbqqq7)47b-2_1a$7i'

# SECURITY WARNING: don't run with debug turned on in production!

ALLOWED_HOSTS = ['*']

SITE_ID = 1

LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/'

# Application definition

INSTALLED_APPS = (
    'dal', #django-autocomplete-light
    'dal_select2',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ctstem_app',
    'django-dia',
    'ckeditor',
    'ckeditor_uploader',
    'nested_formset',
    'storages',
    'password_reset',
    'smart_selects',
    'django_cleanup',
    'django_crontab',
    'dbbackup', #django-dbbackup
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'ctstem_app.middleware.UpdateSession',
)

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = 'ct-stem'
AWS_S3_REGION_NAME = 'us-west-1'
AWS_S3_HOST = 's3-us-west-1.amazonaws.com'
AWS_S3_URL = '%s.%s/' % (AWS_STORAGE_BUCKET_NAME, AWS_S3_HOST)
AWS_S3_SECURE_URLS = True       # use http instead of https
AWS_QUERYSTRING_AUTH = False
AWS_DEFAULT_ACL = 'public-read'


#database backup storage
#DBBACKUP_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
#DBBACKUP_STORAGE_OPTIONS = {
#    'access_key': AWS_ACCESS_KEY_ID,
#    'secret_key': AWS_SECRET_ACCESS_KEY,
#    'bucket_name': 'ct-stem-db-backup',
#}
DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': '/var/backups/ctstem'}
DBBACKUP_AWS_S3_BUCKET = 'ct-stem-db-backup'

#CKEDITOR_JQUERY_URL = 'https://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js'
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_UPLOAD_SLUGIFY_FILENAME = False
CKEDITOR_RESTRICT_BY_USER = True
#CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_FILENAME_GENERATOR = 'ctstem_site.utils.get_filename'
CKEDITOR_CONFIGS = {
    'default': {
        'removePlugins': 'stylesheetparser',
        'toolbar': [
             ['Bold', 'Italic', 'Underline','-', 'Subscript', 'Superscript', '-', 'NumberedList',
            'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', '-', 'JustifyLeft', 'JustifyCenter',
            'JustifyRight', 'JustifyBlock', 'Image', 'Table', 'HorizontalRule', 'SpecialChar', 'Mathjax', 'Iframe' ,
             '-','Link', 'Unlink'] ,
             "/",
             ['Styles', 'Format', 'Font', 'FontSize', 'TextColor',
             'BGColor', 'Maximize', 'ShowBlocks', '-','Source','-','RemoveFormat']
        ],
        'height': 100,
        'width': '98%',
        'allowedContent': True,
        'mathJaxLib': '//cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_HTMLorMML',
        'codeSnippet_theme': 'monokai_sublime',
        'extraPlugins': ','.join(
            ['mathjax', 'codesnippet', 'scayt', 'uploadimage', 'autogrow', 'pasteFromGoogleDoc']
        ),
        'autoGrow_onStartup': True,
        'scayt_autoStartup': True,
        'scayt_sLang': 'en_US',
        'disableNativeSpellChecker': False,
    },
    'question_ckeditor': {
        'removePlugins': 'stylesheetparser',
        'toolbar': [
                 ['Bold', 'Italic', 'Underline','-', 'Subscript', 'Superscript', '-', 'NumberedList',
                'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', '-', 'JustifyLeft', 'JustifyCenter',
                'JustifyRight', 'JustifyBlock', 'Image', 'Table', 'HorizontalRule', 'SpecialChar', 'Mathjax', 'Iframe' ,
                 '-','Link', 'Unlink'] ,
                 "/",
                 ['Styles', 'Format', 'Font', 'FontSize', 'TextColor',
                 'BGColor', 'Maximize', 'ShowBlocks', '-','Source','-','RemoveFormat']
        ],
        'height': 100,
        'width': '98%',
        'allowedContent': True,
        'mathJaxLib': '//cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_HTMLorMML',
        'extraPlugins': ','.join(
            ['mathjax', 'scayt', 'uploadimage']
        ),
        'scayt_autoStartup': True,
        'scayt_sLang': 'en_US',
        'disableNativeSpellChecker': False,
    },
    'student_response_ckeditor': {
        'removePlugins': 'stylesheetparser',
        'toolbar': [['Bold', 'Italic', 'Underline', 'Strike', 'Subscript','Superscript','-','SpellChecker', 'Scayt']],
        'height': 100,
        'extraPlugins': ','.join(
            ['scayt']
        ),
        'scayt_autoStartup': True,
        'scayt_sLang': 'en_US',
        'disableNativeSpellChecker': False,
    },

}

MEDIA_ROOT = os.environ.get('MEDIA_ROOT',os.path.join(BASE_DIR, 'media'))
MEDIA_URL = '/media/'

ROOT_URLCONF = 'ctstem_site.urls'

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
            'debug': DEBUG,
        },
    },
]

WSGI_APPLICATION = 'ctstem_site.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Chicago'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, "..", "www", "static")
STATIC_URL = '/static/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# Auto logout delay in minutes
AUTO_LOGOUT_DELAY = 30

#Cron jobs
CRONJOBS = [
    # run cron at midnight to clean up inactive teacher accounts
    ('0 0 * * *', 'ctstem_app.cron.cleanup_teacher_accounts', '>> /srv/project/logs/cron.log'),
    # run cron at 1 am to backup database
    ('0 1 * * *', 'ctstem_app.cron.backup_db', '>> /srv/project/logs/cron.log'),
]
