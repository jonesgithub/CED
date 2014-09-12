# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CedEnvAdminGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('envadminstatus', models.IntegerField(default=0)),
                ('envadmingroup', models.CharField(max_length=50)),
                ('envadminavatar', models.URLField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),

        migrations.CreateModel(
            name='AuthUser',
            fields=[
            ],
            options={
                'db_table': 'auth_user',
                'managed': False,
            },
            bases=(models.Model,),
        ),

        migrations.AddField(
            model_name='cedenvadmingroup',
            name='envadminname',
            field=models.ForeignKey(related_name=b'user_envadmin', to='CED_homepage.AuthUser'),
            preserve_default=True,
        ),
    ]
