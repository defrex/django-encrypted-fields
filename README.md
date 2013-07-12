[![Build Status](https://travis-ci.org/defrex/django-encrypted-fields.png)](https://travis-ci.org/defrex/django-encrypted-fields)

### Django Encrypted Fields

This is a collection of Django Model Field classes that are encrypted using [Keyczar](http://www.keyczar.org/).

#### About Keyczar

[Keyczar](http://www.keyczar.org/) is a crypto library that exposes a simple API by letting the user set things like the algorithm and key size right in the keyfile. It also provides for things like expiring old keys and cycling in new ones.

#### Getting Started

    $ pip install django-encrypted-fields

Create a basic keyczar keyset. `AES-256` in this case.

    $ mkdir fieldkeys
    $ keyczart create --location=fieldkeys --purpose=crypt
    $ keyczart addkey --location=fieldkeys --status=primary --size=256

In your `settings.py`

    ENCRYPTED_FIELDS_KEYDIR = '/path/to/fieldkeys'

Then, in `models.py`

    from encrypted_fields import (
        EncryptedCharField,
        EncryptedTextField,
        EncryptedDateTimeField,
        EncryptedIntegerField,
    )

    class MyModel(models.Model):
        char_field = EncryptedCharField(max_length=255)
        text_field = EncryptedTextField()
        datetime_field = EncryptedDateTimeField()
        integer_field = EncryptedIntegerField()


#### Available Fields

Currently, there are only 4 fields available. `EncryptedCharField`, `EncryptedTextField`, `EncryptedDateTimeField`, `EncryptedIntegerField`. They have the save APIs as their non-encrypted counterparts.

#### Encrypt All The Fields!

Making new fields is easy! Django Encrypted Fields uses a handy mixin to make upgrading pre-existing fields quite easy.

    from django.db import models
    from encrypted_fields import EncryptedFieldMixin

    class EncryptedIPAddressField(EncryptedFieldMixin, models.IPAddressField):
        pass

Please report an issues you encounter when trying this, since I've only tested it with the 4 fields above.


