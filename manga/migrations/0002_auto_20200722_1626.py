# Generated by Django 3.0.7 on 2020-07-22 20:26

from django.db import migrations
import fernet_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('manga', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='DexPassword',
            field=fernet_fields.fields.EncryptedCharField(max_length=255),
        ),
    ]