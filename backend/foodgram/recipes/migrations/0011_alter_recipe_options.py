# Generated by Django 3.2.16 on 2024-05-01 21:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0010_alter_ingredientamount_recipe'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'default_related_name': 'recipes', 'ordering': ['-pub_date'], 'verbose_name': 'Рецепт'},
        ),
    ]
