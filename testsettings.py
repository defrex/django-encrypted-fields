
import os

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': ':memory:',
    # },
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'django_encrypted_fields',
        'USER': 'defrex',
    },
}

SECRET_KEY = 'notsecure'

INSTALLED_APPS = (
    'encrypted_fields',
)

ENCRYPTED_FIELDS_KEYDIR = os.path.join(os.path.dirname(__file__), 'testkey')
