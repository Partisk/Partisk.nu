# Generated by Django 2.0.2 on 2018-03-10 00:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partisk', '0003_auto_20180309_2129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='source',
            field=models.TextField(default=None, null=True),
        ),
    ]
