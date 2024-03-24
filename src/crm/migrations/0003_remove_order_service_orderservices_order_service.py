# Generated by Django 5.0.3 on 2024-03-24 17:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0002_alter_people_managers_alter_order_discount_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='service',
        ),
        migrations.CreateModel(
            name='OrderServices',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cost', models.PositiveBigIntegerField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.order')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.service')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='order',
            name='service',
            field=models.ManyToManyField(through='crm.OrderServices', to='crm.service'),
        ),
    ]