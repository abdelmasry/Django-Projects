# Generated by Django 4.2.4 on 2024-05-04 12:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0003_basket_basketline"),
    ]

    operations = [
        migrations.CreateModel(
            name="Order",
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
                (
                    "status",
                    models.IntegerField(
                        choices=[(10, "New"), (20, "Paid"), (30, "Done")], default=10
                    ),
                ),
                ("billing_name", models.CharField(max_length=60)),
                ("billing_address1", models.CharField(max_length=60)),
                ("billing_address2", models.CharField(blank=True, max_length=60)),
                ("billing_zip_code", models.CharField(max_length=12)),
                ("billing_city", models.CharField(max_length=60)),
                ("billing_country", models.CharField(max_length=3)),
                ("shipping_name", models.CharField(max_length=60)),
                ("shipping_address1", models.CharField(max_length=60)),
                ("shipping_address2", models.CharField(blank=True, max_length=60)),
                ("shipping_zip_code", models.CharField(max_length=12)),
                ("shipping_city", models.CharField(max_length=60)),
                ("shipping_country", models.CharField(max_length=3)),
                ("date_updated", models.DateTimeField(auto_now=True)),
                ("date_added", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="OrderLine",
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
                (
                    "status",
                    models.IntegerField(
                        choices=[
                            (10, "New"),
                            (20, "Processing"),
                            (30, "Sent"),
                            (40, "Cancelled"),
                        ],
                        default=10,
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lines",
                        to="main.order",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="main.product"
                    ),
                ),
            ],
        ),
    ]
