# Generated by Django 5.1.1 on 2024-11-09 22:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Circular",
            fields=[
                ("id", models.UUIDField(primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=255)),
                ("content", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "classification",
                    models.CharField(
                        choices=[
                            ("NORMAL", "Normal"),
                            ("CONFIDENTIAL", "Confidential"),
                            ("TOP_SECRET", "Top Secret"),
                            ("RESTRICTED", "Restricted"),
                        ],
                        default="NORMAL",
                        max_length=20,
                    ),
                ),
                ("expiry_date", models.DateTimeField()),
                ("is_confidential", models.BooleanField(default=False)),
                ("is_deleted", models.BooleanField(default=False)),
                ("circular_number", models.CharField(max_length=50, unique=True)),
                ("metadata", models.JSONField(blank=True, null=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="created_circulars",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "target_officers",
                    models.ManyToManyField(
                        related_name="targeted_circulars", to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="CircularAttachment",
            fields=[
                ("id", models.UUIDField(primary_key=True, serialize=False)),
                ("file_name", models.CharField(max_length=255)),
                ("file_type", models.CharField(max_length=100)),
                ("file_size", models.IntegerField()),
                ("file_path", models.FileField(upload_to="circular_attachments/")),
                ("server_url", models.URLField(blank=True, null=True)),
                (
                    "circular",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        to="circular.circular",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CircularAcknowledgment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("device_info", models.CharField(max_length=255)),
                ("ip_address", models.GenericIPAddressField()),
                ("location", models.CharField(max_length=255)),
                (
                    "circular",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="acknowledgments",
                        to="circular.circular",
                    ),
                ),
                (
                    "officer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="circular_acknowledgments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("circular", "officer")},
            },
        ),
    ]