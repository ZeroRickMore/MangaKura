# Generated by Django 5.1.6 on 2025-03-02 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GeneralHandler', '0010_usertomanga_whole_series_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertomanga',
            name='whole_series_price_calculated',
            field=models.FloatField(blank=True, default=0.0),
        ),
    ]
