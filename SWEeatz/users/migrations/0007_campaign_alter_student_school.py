# Generated by Django 5.1.2 on 2024-10-28 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0006_alter_student_school"),
    ]

    operations = [
        migrations.CreateModel(
            name="Campaign",
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
                    "title",
                    models.CharField(
                        help_text="Enter the title of the campaign", max_length=200
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        help_text="Enter a brief description of the campaign"
                    ),
                ),
                ("start_date", models.DateField(help_text="Campaign start date")),
                ("end_date", models.DateField(help_text="Campaign end date")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["-start_date"],
            },
        ),
        migrations.AlterField(
            model_name="student",
            name="school",
            field=models.CharField(
                choices=[
                    ("MCAS", "MCAS"),
                    ("CSOM", "CSOM"),
                    ("CSON", "CSON"),
                    ("LSEHD", "LSEHD"),
                    ("MESSINA", "MESSINA"),
                ],
                default="MCAS",
                max_length=100,
            ),
        ),
    ]
