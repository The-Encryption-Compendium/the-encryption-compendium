# Generated by Django 3.0.1 on 2020-03-08 08:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("research_assistant", "0004_auto_20200308_0756"),
    ]

    operations = [
        migrations.RemoveField(model_name="compendiumentry", name="authors_text",),
    ]