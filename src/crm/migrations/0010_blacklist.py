# Generated by Django 5.0.3 on 2024-05-12 15:58

import crm.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0009_alter_peopledetailedinfo_phone_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlackList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('national_code', models.CharField(max_length=10, unique=True, validators=[crm.validators.national_code])),
            ],
        ),
    ]
