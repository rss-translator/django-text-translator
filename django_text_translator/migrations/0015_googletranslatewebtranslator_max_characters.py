# Generated by Django 5.0.2 on 2024-02-20 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("translator", "0014_testtranslator_interval"),
    ]

    operations = [
        migrations.AddField(
            model_name="googletranslatewebtranslator",
            name="max_characters",
            field=models.IntegerField(default=5000),
        ),
    ]
