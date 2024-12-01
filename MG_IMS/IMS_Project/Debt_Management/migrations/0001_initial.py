# Generated by Django 5.1.3 on 2024-11-29 05:41

import django.db.models.deletion
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('POS_APP', '0002_remove_transactionitem_product_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('phone', models.CharField(blank=True, max_length=15, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Debt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_due', models.DecimalField(decimal_places=2, max_digits=10)),
                ('amount_paid', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('due_date', models.DateField()),
                ('status', models.CharField(choices=[('Unpaid', 'Unpaid'), ('Partially Paid', 'Partially Paid'), ('Paid', 'Paid')], default='Unpaid', max_length=20)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='debts', to='Debt_Management.customer')),
                ('transaction', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='debt', to='POS_APP.transaction')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_paid', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date_paid', models.DateTimeField(auto_now_add=True)),
                ('debt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='Debt_Management.debt')),
            ],
        ),
    ]