# Generated by Django 5.0.3 on 2024-06-19 13:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='people',
            name='father_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='people',
            name='minimum_salary',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='people',
            name='firstname',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='people',
            name='lastname',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='people',
            name='national_code',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='peopledetailedinfo',
            name='detail_type',
            field=models.CharField(choices=[('P', 'شماره تماس'), ('C', 'کارت بانکی'), ('S', 'شماره شبا')], max_length=1),
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=250)),
                ('postal_code', models.CharField(blank=True, max_length=10, null=True)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.catalog')),
                ('people', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.people')),
            ],
        ),
        migrations.CreateModel(
            name='EmergencyInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(blank=True, max_length=50, null=True)),
                ('lastname', models.CharField(blank=True, max_length=50, null=True)),
                ('phone_number', models.CharField(max_length=15)),
                ('address', models.CharField(blank=True, max_length=250, null=True)),
                ('people', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.people')),
                ('relation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='crm.catalog')),
            ],
        ),
    ]