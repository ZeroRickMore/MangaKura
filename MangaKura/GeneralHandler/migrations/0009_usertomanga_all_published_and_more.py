# Generated by Django 5.1.6 on 2025-03-02 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GeneralHandler', '0008_usertovariant_to_sell'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertomanga',
            name='all_published',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AddField(
            model_name='usertomanga',
            name='single_volume_price',
            field=models.FloatField(default=0.0),
        ),
    ]
