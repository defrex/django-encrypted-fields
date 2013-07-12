
import re
from datetime import datetime

from django.db import models, connection
from django.test import TestCase

from .fields import (
    EncryptedCharField,
    EncryptedTextField,
    EncryptedDateTimeField,
    EncryptedIntegerField,
)


class TestModel(models.Model):
    char = EncryptedCharField(max_length=255, null=True)
    text = EncryptedTextField(null=True)
    datetime = EncryptedDateTimeField(null=True)
    integer = EncryptedIntegerField(null=True)


class FieldTest(TestCase):

    def get_db_value(self, field, model_id):
        cursor = connection.cursor()
        cursor.execute(
            'select {0} '
            'from encrypted_fields_testmodel '
            'where id = {1};'.format(field, model_id)
        )
        return cursor.fetchone()[0]

    def test_char_field_encrypted(self):
        plaintext = 'Oh hi, test reader!'

        model = TestModel()
        model.char = plaintext
        model.save()

        ciphertext = self.get_db_value('char', model.id)

        self.assertNotEqual(plaintext, ciphertext)
        self.assertTrue('test' not in ciphertext)

        fresh_model = TestModel.objects.get(id=model.id)
        self.assertEqual(fresh_model.char, plaintext)

    def test_text_field_encrypted(self):
        plaintext = 'Oh hi, test reader!' * 10

        model = TestModel()
        model.text = plaintext
        model.save()

        ciphertext = self.get_db_value('text', model.id)

        self.assertNotEqual(plaintext, ciphertext)
        self.assertTrue('test' not in ciphertext)

        fresh_model = TestModel.objects.get(id=model.id)
        self.assertEqual(fresh_model.text, plaintext)

    def test_datetime_field_encrypted(self):
        plaintext = datetime.now()

        model = TestModel()
        model.datetime = plaintext
        model.save()

        ciphertext = self.get_db_value('datetime', model.id)

        # Django's normal date serialization format
        self.assertTrue(re.search('^\d\d\d\d-\d\d-\d\d', ciphertext) is None)

        fresh_model = TestModel.objects.get(id=model.id)
        self.assertEqual(fresh_model.datetime, plaintext)

    def test_integer_field_encrypted(self):
        plaintext = 42

        model = TestModel()
        model.integer = plaintext
        model.save()

        ciphertext = self.get_db_value('integer', model.id)

        self.assertNotEqual(plaintext, ciphertext)
        self.assertNotEqual(plaintext, str(ciphertext))

        fresh_model = TestModel.objects.get(id=model.id)
        self.assertEqual(fresh_model.integer, plaintext)
