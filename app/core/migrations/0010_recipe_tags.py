# Generated by Django 3.2.21 on 2023-09-26 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_remove_recipe_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(to='core.Tag'),
        ),
    ]