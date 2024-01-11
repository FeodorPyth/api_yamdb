from django.core.exceptions import ValidationError
from django.utils.timezone import now


def validate_year(value):
    """
    Валидация поля year.
    Значение не должно быть больше чем текущий год.
    """
    if value > now().year:
        raise ValidationError('Указанный год не может быть больше текущего.')
    return value


def validate_username(value):
    """
    Валидация поля username.
    Значение не должно быть равно 'me'.
    """
    if value == 'me':
        raise ValidationError('Нельзя использовать "me"'
                              ' в качестве имени пользователя.')
    return value
