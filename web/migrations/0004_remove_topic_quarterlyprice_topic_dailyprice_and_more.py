# Generated by Django 5.1.6 on 2025-05-12 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_remove_topic_dailyprice_remove_topic_weeklyprice_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='topic',
            name='quarterlyPrice',
        ),
        migrations.AddField(
            model_name='topic',
            name='dailyPrice',
            field=models.DecimalField(decimal_places=2, default=30000, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='topic',
            name='weeklyPrice',
            field=models.DecimalField(decimal_places=2, default=40000, max_digits=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='topic',
            name='monthlyPrice',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
