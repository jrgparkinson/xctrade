# Generated by Django 3.1.7 on 2021-04-01 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("trading", "0002_auto_20210401_1847"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="created",
            field=models.DateTimeField(auto_now_add=True, default="2021-01-01 00:00"),
            preserve_default=False,
        ),
    ]
