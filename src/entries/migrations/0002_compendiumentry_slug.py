# Generated by Django 3.0.3 on 2020-03-24 05:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("entries", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="compendiumentry",
            name="slug",
            field=models.SlugField(blank=True, max_length=250, null=True),
        ),
    ]