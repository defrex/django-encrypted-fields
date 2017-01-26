
import os
import types

import django
from django.db import models
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import cached_property

try:
    from django.utils.encoding import smart_text
except ImportError:
    from django.utils.encoding import smart_str as smart_text

from keyczar import keyczar


class EncryptedFieldException(Exception):
    pass


# Simple wrapper around keyczar to standardize the initialization
# of the crypter object and allow for others to extend as needed.
class KeyczarWrapper(object):
    def __init__(self, keyname, *args, **kwargs):
        self.crypter = keyczar.Crypter.Read(keyname)

    def encrypt(self, cleartext):
        return self.crypter.Encrypt(cleartext)

    def decrypt(self, ciphertext):
        return self.crypter.Decrypt(ciphertext)


class EncryptedFieldMixin(object):
    """
    EncryptedFieldMixin will use keyczar to encrypt/decrypt data that is being
    marshalled in/out of the database into application Django model fields.

    This is very helpful in ensuring that data at rest is encrypted and
    minimizing the effects of SQL Injection or insider access to sensitive
    databases containing sensitive information.

    The most basic use of this mixin is to have a single encryption key for all
    data in your database. This lives in a Keyczar key directory specified by:
    the setting - settings.ENCRYPTED_FIELDS_KEYDIR -

    Optionally, you can name specific encryption keys for data-specific
    purposes in your model such as:
        special_data = EncrytpedCharField( ..., keyname='special_data' )

    The Mixin will handle the encryption/decryption seamlessly, but native
    SQL queries may need a way to filter data that is encrypted. Using the
    optional 'prefix' kwarg will prepend a static identifier to your encrypted
    data before it is written to the database.

    There are other use cases where you may not wish to encrypt all of the data
    in a database. For example, if you have a survey application that allows
    users to enter arbitrary questions and answers, users may request sensitive
    information to be stored such as SSN, Driver License #, Credit Card, etc.
    Your application can detect these sensitive fields, manually encrypt the
    data and store that in the database mixed with other cleartext data.
    The model should then only decrypt the specific fields needed. Use the
    kwarg 'decrypt_only' to specify this behavior and the model will not
    encrypt the data inbound and only attempt to decrypt outbound.

    Encrypting data will significantly change the size of the data being stored
    and this may cause issues with your database column size. Before storing
    any encrypted data in your database, ensure that you have the proper
    column width otherwise you may experience truncation of your data depending
    on the database engine in use.

    To have the mixin enforce max field length, either:
        a) set ENFORCE_MAX_LENGTH = True in your settings files
        b) set 'enforce_max_length' to True in the kwargs of your model.

    A ValueError will be raised if the encrypted length of the data (including
    prefix if specified) is greater than the max_length of the field.
    """

    if django.VERSION < (1, 8):
        __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        """
        Initialize the EncryptedFieldMixin with the following
        optional settings:
        * keyname: The name of the keyczar key
        * crypter_klass: A custom class that is extended from Keyczar.
        * prefix: A static string prepended to all encrypted data
        * decrypt_only: Boolean whether to only attempt to decrypt data coming
                        from the database and not attempt to encrypt the data
                        being written to the database.
        """
        # Allow for custom class extensions of Keyczar.
        self._crypter_klass = kwargs.pop('crypter_klass', KeyczarWrapper)

        self.keyname = kwargs.pop('keyname', None)

        # If settings.DEFAULT_KEY_DIRECTORY, then the key
        # is located in DEFAULT_KEY_DIRECTORY/keyname
        if self.keyname:
            if hasattr(settings, 'DEFAULT_KEY_DIRECTORY'):
                self.keydir = os.path.join(
                    settings.DEFAULT_KEY_DIRECTORY,
                    self.keyname
                )
            else:
                raise ImproperlyConfigured(
                    'You must set settings.DEFAULT_KEY_DIRECTORY'
                    'when using the keyname kwarg'
                )

        # If the keyname is not defined on a per-field
        # basis, then check for the global data encryption key.
        if not self.keyname and hasattr(settings, 'ENCRYPTED_FIELDS_KEYDIR'):
            self.keydir = settings.ENCRYPTED_FIELDS_KEYDIR

        # If we still do not have a keydir, then raise an exception
        if not self.keydir:
            raise ImproperlyConfigured(
                'You must set settings.ENCRYPTED_FIELDS_KEYDIR '
                'or name a key with kwarg `keyname`'
            )

        # The name of the keyczar key without path for logging purposes.
        self.keyname = os.path.dirname(self.keydir)

        # Prefix encrypted data with a static string to allow filtering
        # of encrypted data vs. non-encrypted data using vanilla MySQL queries.
        self.prefix = kwargs.pop('prefix', '')

        # Allow for model decryption-only, bypassing encryption of data.
        # Useful for models that have a sparse amount of data that is required
        # to be encrypted.
        self.decrypt_only = kwargs.pop('decrypt_only', False)

        self.load_crypter()

        # Ensure the encrypted data does not exceed the max_length
        # of the database. Data truncation is a possibility otherwise.
        self.enforce_max_length = getattr(
            settings,
            'ENFORCE_MAX_LENGTH',
            False
        )
        if not self.enforce_max_length:
            self.enforce_max_length = kwargs.pop('enforce_max_length', False)

        super(EncryptedFieldMixin, self).__init__(*args, **kwargs)

    def crypter(self):
        return self._crypter

    def get_internal_type(self):
        return 'TextField'

    def load_crypter(self):
        self._crypter = self._crypter_klass(self.keydir)

    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)

    def to_python(self, value):
        if value is None or not isinstance(value, types.StringTypes):
            return value

        if self.prefix and value.startswith(self.prefix):
            value = value[len(self.prefix):]

        try:
            value = self.crypter().decrypt(value)
            value = value.decode('unicode_escape')
        except keyczar.errors.KeyczarError:
            pass
        except UnicodeEncodeError:
            pass
        except binascii.Error:
            pass        

        return super(EncryptedFieldMixin, self).to_python(value)

    def get_prep_value(self, value):
        value = super(EncryptedFieldMixin, self).get_prep_value(value)

        if value is None or value == '' or self.decrypt_only:
            return value

        if isinstance(value, types.StringTypes):
            value = value.encode('unicode_escape')
            value = value.encode('ascii')
        else:
            value = str(value)

        return self.prefix + self.crypter().encrypt(value)

    def get_db_prep_value(self, value, connection, prepared=False):
        if not prepared:
            value = self.get_prep_value(value)

            if self.enforce_max_length:
                if (
                    value and hasattr(self, 'max_length') and
                    self.max_length and
                    len(value) > self.max_length
                ):
                    raise ValueError(
                        'Field {0} max_length={1} encrypted_len={2}'.format(
                            self.name,
                            self.max_length,
                            len(value),
                        )
                    )
        return value


class EncryptedCharField(EncryptedFieldMixin, models.CharField):
    pass


class EncryptedTextField(EncryptedFieldMixin, models.TextField):
    pass


class EncryptedDateTimeField(EncryptedFieldMixin, models.DateTimeField):
    pass


class EncryptedIntegerField(EncryptedFieldMixin, models.IntegerField):
    @cached_property
    def validators(self):
        """
        See issue https://github.com/defrex/django-encrypted-fields/issues/7
        Need to keep all field validators, but need to change
        `get_internal_type` on the fly to prevent fail in django 1.7.
        """
        self.get_internal_type = lambda: 'IntegerField'
        return models.IntegerField.validators.__get__(self)


class EncryptedDateField(EncryptedFieldMixin, models.DateField):
    pass


class EncryptedFloatField(EncryptedFieldMixin, models.FloatField):
    pass


class EncryptedEmailField(EncryptedFieldMixin, models.EmailField):
    pass


class EncryptedBooleanField(EncryptedFieldMixin, models.BooleanField):
    pass


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ['^encrypted_fields\.fields\.\w+Field'])

except ImportError:
    pass
