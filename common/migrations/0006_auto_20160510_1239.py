# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-10 12:39
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0005_auto_20160504_1336'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='myuser',
            name='user_point',
        ),
        migrations.RemoveField(
            model_name='myuser',
            name='user_points',
        ),
    ]
