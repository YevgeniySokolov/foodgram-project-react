from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from foodgram.constants import PROHIBITED_USERNAME


def prohibited_username_validator(value):
    if value.lower() == PROHIBITED_USERNAME:
        raise ValidationError(
            f'Username {PROHIBITED_USERNAME} is prohibited.'
        )


regex_validator = RegexValidator(regex=r'^[\w.@+-]+\Z',
                                 message='This Username format is not allowed')
