
from django.db import models
from django.conf import settings

try:
    from django.utils.encoding import smart_text
except ImportError:
    from django.utils.encoding import smart_str as smart_text

from keyczar import keyczar


crypter = keyczar.Crypter.Read(settings.ENCRYPTED_FIELDS_KEYDIR)


class EncryptedFieldException(Exception): pass


class EncryptedFieldMixin(object):
    __metaclass__ = models.SubfieldBase

    def get_internal_type(self):
        return 'TextField'

    def to_python(self, value):
        if value is None or not isinstance(value, basestring):
            return value

        try:
            value = crypter.Decrypt(value)
        except keyczar.errors.KeyczarError:
            pass

        return super(EncryptedFieldMixin, self).to_python(value)

    def get_prep_value(self, value):
        value = super(EncryptedFieldMixin, self).get_prep_value(value)
        if value is None or value == '':
            return value
        return crypter.Encrypt(smart_text(value))

    def get_db_prep_value(self, value, connection, prepared=False):
        if not prepared:
            value = self.get_prep_value(value)
        return value


class EncryptedCharField(EncryptedFieldMixin, models.CharField):
    pass


class EncryptedTextField(EncryptedFieldMixin, models.TextField):
    pass


class EncryptedDateTimeField(EncryptedFieldMixin, models.DateTimeField):
    pass


class EncryptedIntegerField(EncryptedFieldMixin, models.IntegerField):
    pass
