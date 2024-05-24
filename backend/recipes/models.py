from colorfield.fields import ColorField
from django.db import models
from django.core.validators import MinValueValidator
from django.template.defaultfilters import truncatechars

from foodgram.constants import MAX_LENGTH_NAME, TEXT_LENGTH, DEFAULT_TRUNCATE
from users.models import User


class Tag(models.Model):
    """Тэг."""

    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        unique=True,
        verbose_name='Название'
    )
    color = ColorField(
        default='#FF0000',
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self):
        return truncatechars(self.name, DEFAULT_TRUNCATE)


class Ingredient(models.Model):
    """Ингредиент."""

    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=MAX_LENGTH_NAME,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient',
            ),
        ]

    def __str__(self):
        return truncatechars(self.name, DEFAULT_TRUNCATE)


class Recipe(models.Model):
    """Рецепт."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        null=False,
        default=None,
        verbose_name='Изображение'
    )
    text = models.TextField(verbose_name='Текст')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        verbose_name='Тэги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1, message='Время приготовления не '
                                      'может быть меньше 1 минуты!')],
        verbose_name='Время приготовления'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name='Дата добавления'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date', ]
        default_related_name = 'recipes'

    def __str__(self):
        return f'{self.name[:TEXT_LENGTH]}'


class IngredientAmount(models.Model):
    """"Количество ингредиента."""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1, message='Количество должно быть '
                                      'больше 0!')],
        verbose_name='Количество'
    )

    class Meta:
        default_related_name = 'ingredientamounts'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredientamount',
            ),
        ]


class ShoppingCartFavoriteBaseModel(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        default_related_name = '%(class)ss'
        ordering = ('-recipe__pub_date',)
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_%(class)s',
            ),
        )

    def __str__(self):
        return f'{self.user} добавил: {self.recipe}'


class ShoppingCart(ShoppingCartFavoriteBaseModel):
    """"Корзина покупок."""

    class Meta(ShoppingCartFavoriteBaseModel.Meta):
        verbose_name = 'Корзина покупок'
        verbose_name_plural = verbose_name


class FavoriteRecipe(ShoppingCartFavoriteBaseModel):
    """"Избранный рецепт."""

    class Meta(ShoppingCartFavoriteBaseModel.Meta):
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
