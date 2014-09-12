# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('CED_homepage', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cedenvadmingroup',
            name='envadminavatar',
            field=models.URLField(default=b'http://127.0.0.1:8000/static/images/spidertocat.png'),
        ),
    ]
