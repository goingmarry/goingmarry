# Generated by Django 5.1.3 on 2024-11-29 04:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("login", "0002_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="login",
            old_name="login_id",
            new_name="id",
        ),
        migrations.RenameField(
            model_name="login",
            old_name="is_successful",
            new_name="is_success",
        ),
        migrations.AlterModelTable(
            name="login",
            table="logins",
        ),
    ]
