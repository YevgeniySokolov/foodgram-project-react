# Generated by Django 3.2.16 on 2024-05-08 22:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0014_auto_20240507_0221'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='ingredientamount',
            name='unique_ingredientamount',
        ),
    ]
