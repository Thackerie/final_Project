# Generated by Django 4.1.5 on 2023-08-29 12:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('WalletWise', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='funds',
            name='defaultOwner',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='defaultFunds', to=settings.AUTH_USER_MODEL),
        ),
    ]
