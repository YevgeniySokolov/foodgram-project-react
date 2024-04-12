from colorfield.fields import ColorField
from django.db import models
from django.core.validators import MinValueValidator

from foodgram.constants import MAX_LENGTH_NAME, TEXT_LENGTH
from users.models import User


class Tag(models.Model):
    """Тэг."""

    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        verbose_name='Название',
        unique=True
    )
    color = ColorField(
        verbose_name='Цвет',
        default='#FF0000'
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True
    )

    class Meta:
        verbose_name = 'Тэг'
        ordering = ('name',)

    def __str__(self):
        return self.slug


class Ingredient(models.Model):
    """Ингредиент."""

    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=MAX_LENGTH_NAME,
        verbose_name='Единицы измерения'
    )


class Recipe(models.Model):
    """Рецепт."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        null=False,
        default=None
    )
    text = models.TextField(verbose_name='Текст')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты',
    )
    tag = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        blank=True,
        related_name='recipes',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(1, message='Время приготовления не '
                                      'может быть меньше 1 минуты!')]
    )
    is_favorited = models.BooleanField(default=False)
    is_in_shopping_cart = models.BooleanField(default=False)
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'Рецепт'
        ordering = ['-pub_date', ]
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'author'],
                name='unique_recipe',
            ),
        ]

    def __str__(self):
        return f'{self.name[:TEXT_LENGTH]}'


class IngredientAmount(models.Model):
    """"Количество ингредиента."""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт',
        related_name='recipe_ingredient'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1, message='Количество должно быть '
                                      'больше 0!')]
    )
