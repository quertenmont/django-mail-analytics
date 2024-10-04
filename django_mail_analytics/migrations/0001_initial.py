# Generated by Django 5.1 on 2024-10-03 14:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Mail",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                ("key", models.CharField(db_index=True, max_length=128)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("sender", models.CharField(max_length=2048, null=True)),
                ("subject", models.CharField(max_length=2048, null=True)),
                ("body", models.TextField(blank=True, null=True)),
                ("date", models.DateField(editable=False)),
            ],
        ),
        migrations.CreateModel(
            name="MailRecipient",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                ("recipient", models.CharField(max_length=2048)),
                (
                    "mail",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recipients",
                        to="django_mail_analytics.mail",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="MailRecipientAction",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("action", models.CharField(max_length=2048)),
                (
                    "recipient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="actions",
                        to="django_mail_analytics.mailrecipient",
                    ),
                ),
            ],
        ),
    ]
