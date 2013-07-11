
from django.db import models, connection
from django.test import TestCase

from .fields import EncryptedCharField


class TestModel(models.Model):
    char_field = EncryptedCharField(max_length=255)


class FieldTest(TestCase):

    def test_char_field_encrypted(self):
        plaintext = 'Oh hi, test reader!'

        model = TestModel()
        model.char_field = plaintext
        model.save()

        cursor = connection.cursor()
        cursor.execute(
            'select char_field '
            'from encrypted_fields_testmodel '
            'where id = {};'.format(model.id)
        )
        ciphertext = cursor.fetchone()[0]

        self.assertNotEqual(plaintext, ciphertext)
        self.assertTrue('test' not in ciphertext)

        fresh_model = TestModel.objects.get(id=model.id)
        self.assertEqual(fresh_model.char_field, plaintext)
