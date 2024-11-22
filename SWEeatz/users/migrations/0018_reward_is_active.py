# Generated by Django 5.1.2 on 2024-11-22 00:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_campaign_completed_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='reward',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Set to False when the reward is no longer redeemable'),
        ),
    ]
