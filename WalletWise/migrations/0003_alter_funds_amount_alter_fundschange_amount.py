# Generated by Django 4.1.5 on 2023-09-17 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WalletWise', '0002_alter_funds_defaultowner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='funds',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=20),
        ),
        migrations.AlterField(
            model_name='fundschange',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=20),
        ),
    ]
