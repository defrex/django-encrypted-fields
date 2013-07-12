### Django Encrypted Fields

This is a collection of Django Model Field classes that are encrypted using [Keyczar](http://www.keyczar.org/).

#### About Keyczar

[Keyczar](http://www.keyczar.org/) is a crypto library that exposes a simple API by letting the user set things like the algorithm and key size right in the keyfile. It also provides for things like expiring old keys and cycling in new ones.

#### Getting Started

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

#### Licence

    Copyright (c) 2013, Aron Jones
    All rights reserved.
    
    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:
    1. Redistributions of source code must retain the above copyright
       notice, this list of conditions and the following disclaimer.
    2. Redistributions in binary form must reproduce the above copyright
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.
    3. All advertising materials mentioning features or use of this software
       must display the following acknowledgement:
       This product includes software developed by Aron Jones.
    4. Neither the name of Aron Jones nor the
       names of its contributors may be used to endorse or promote products
       derived from this software without specific prior written permission.
    
    THIS SOFTWARE IS PROVIDED BY ARON JONES ''AS IS'' AND ANY
    EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL ARON JONES BE LIABLE FOR ANY
    DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
    ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
