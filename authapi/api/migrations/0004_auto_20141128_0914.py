# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20141128_0831'),
    ]

    operations = [
        migrations.AlterField(
            model_name='acl',
            name='user',
            field=models.ForeignKey(to='api.UserData', related_name='acls'),
        ),
    ]
