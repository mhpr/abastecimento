# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2018-07-19 18:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('abastecimento', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='operador',
            options={'ordering': ['nome']},
        ),
        migrations.AlterModelOptions(
            name='veiculo',
            options={'ordering': ['placa']},
        ),
    ]
