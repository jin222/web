# Generated by Django 2.0.5 on 2019-02-13 15:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trade', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderinfo',
            old_name='singer_mobile',
            new_name='signer_mobile',
        ),
    ]
