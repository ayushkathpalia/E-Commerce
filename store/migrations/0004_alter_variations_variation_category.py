# Generated by Django 4.1 on 2022-10-27 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_alter_variations_variation_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variations',
            name='variation_category',
            field=models.CharField(choices=[('Color', 'Color'), ('Size', 'size')], max_length=100),
        ),
    ]