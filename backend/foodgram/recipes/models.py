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
        default_related_name = 'tags'

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

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепт."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
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
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        blank=True
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(1, message='Время приготовления не '
                                      'может быть меньше 1 минуты!')]
    )
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'Рецепт'
        ordering = ['-pub_date', ]
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['ingredients'],
        #         name='unique_ingredients'
        #     ),
        # ]
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
        verbose_name='Количество',
        validators=[MinValueValidator(1, message='Количество должно быть '
                                      'больше 0!')]
    )

    class Meta:
        verbose_name = 'Ингредиент для рецепта'
        default_related_name = 'ingredientamounts'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredientamount',
            ),
        ]


class ShoppingCart(models.Model):
    """"Корзина покупок."""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Пользователь'
    )

    class Meta:
        default_related_name = 'shoppingcarts'
        verbose_name = 'Корзина покупок'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.user} добавил: {self.recipe}'


class FavoriteRecipe(models.Model):
    """"Избранный рецепт."""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Пользователь'
    )

    class Meta:
        default_related_name = 'favoriterecipes'
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.user} добавил: {self.recipe}'
