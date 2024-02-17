# Generated by Django 4.2.1 on 2024-02-17 05:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("oauth", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="oauthuser",
            name="discord_id",
            field=models.BigIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="oauthuser",
            name="discord_mention",
            field=models.CharField(default="", max_length=255),
            preserve_default=False,
        ),
    ]
