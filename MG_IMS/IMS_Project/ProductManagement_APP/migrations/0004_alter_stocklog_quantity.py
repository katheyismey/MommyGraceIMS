# Generated by Django 5.1.3 on 2024-11-20 05:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ProductManagement_APP', '0003_stocklog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stocklog',
            name='quantity',
            field=models.PositiveIntegerField(),
        ),
    ]
