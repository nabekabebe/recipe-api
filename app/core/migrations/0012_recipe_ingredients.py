# Generated by Django 3.2.21 on 2023-09-26 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_ingredient'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(to='core.Ingredient'),
        ),
    ]