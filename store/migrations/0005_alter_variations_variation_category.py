# Generated by Django 4.1 on 2022-10-27 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_alter_variations_variation_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variations',
            name='variation_category',
            field=models.CharField(choices=[('color', 'color'), ('size', 'size')], max_length=100),
        ),
    ]
