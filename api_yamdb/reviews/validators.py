from django.core.exceptions import ValidationError
from django.utils.timezone import now

from api_yamdb.settings import URL_PATH_NAME


def validate_year(value):
    """
    Валидация поля year.
    Значение не должно быть больше чем текущий год.
    """
    if value > now().year:
        raise ValidationError('Указанный год не может быть больше текущего.')
    return value


def validate_username_me(value):
    """
    Валидация поля username.
    Значение не должно быть равно 'me'.
    """
    if value == URL_PATH_NAME:
        raise ValidationError(f'Нельзя использовать {URL_PATH_NAME}'
                              ' в качестве имени пользователя.')
    return value
