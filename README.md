[![Build Status](https://travis-ci.org/defrex/django-encrypted-fields.png)](https://travis-ci.org/defrex/django-encrypted-fields)
[![Pypi Package](https://badge.fury.io/py/django-encrypted-fields.png)](http://badge.fury.io/py/django-encrypted-fields)

### Django Encrypted Fields

This is a collection of Django Model Field classes that are encrypted using [Keyczar](http://www.keyczar.org/).

#### About Keyczar

[Keyczar](http://www.keyczar.org/) is a crypto library that exposes a simple API by letting the user set things like the algorithm and key size right in the keyfile. It also provides for things like expiring old keys and cycling in new ones.

#### Getting Started
```shell
$ pip install django-encrypted-fields
```
Create a basic keyczar keyset. `AES-256` in this case.
```shell
$ mkdir fieldkeys
$ keyczart create --location=fieldkeys --purpose=crypt
$ keyczart addkey --location=fieldkeys --status=primary --size=256
```
In your `settings.py`
```python
ENCRYPTED_FIELDS_KEYDIR = '/path/to/fieldkeys'
```
Then, in `models.py`
```python
from encrypted_fields import EncryptedTextField

class MyModel(models.Model):
    text_field = EncryptedTextField()
```
Use your model as normal and your data will be encrypted in the database.

_Warning:_ Once the data is encrypted, it can no longer to used to query or sort. In SQL, these will all look like text fields with random noise in them (which is what you want).

#### Available Fields

Currently build in and unit-tested fields. They have the same APIs as their non-encrypted counterparts.

- `EncryptedCharField`
- `EncryptedTextField`
- `EncryptedDateTimeField`
- `EncryptedIntegerField`
- `EncryptedFloatField`
- `EncryptedEmailField`
- `EncryptedBooleanField`

#### Encrypt All The Fields!

Making new fields is easy! Django Encrypted Fields uses a handy mixin to make upgrading pre-existing fields quite easy.
```python
from django.db import models
from encrypted_fields import EncryptedFieldMixin

class EncryptedIPAddressField(EncryptedFieldMixin, models.IPAddressField):
    pass
```
Please report an issues you encounter when trying this, since I've only tested it with the fields above.
