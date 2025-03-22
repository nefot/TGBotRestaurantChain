from django.db import models

from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator, MinValueValidator, EmailValidator


def validate_salary(value):
    """
    Валидация для поля salary (зарплата).
    Зарплата не может быть отрицательной.
    """
    if value < 0:
        raise ValidationError('Зарплата не может быть отрицательной.')


class Post(models.Model):
    # Название должности
    title = models.CharField(
        max_length=100,
        verbose_name='Название должности',
        help_text='Введите название должности (например, "Повар", "Официант").'
    )

    # Описание должности
    description = models.TextField(
        verbose_name='Описание должности',
        help_text='Введите описание обязанностей и требований для этой должности.',
        blank=True,
    )

    # Зарплата
    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Зарплата',
        help_text='Введите размер зарплаты для этой должности.',
        validators=[validate_salary],
    )

    # Требуемый опыт работы (в годах)
    experience_required = models.PositiveIntegerField(
        verbose_name='Требуемый опыт работы',
        help_text='Введите требуемый опыт работы в годах.',
        default=0,
    )

    # Дата создания записи
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )

    # Дата обновления записи
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления',
    )

    def __str__(self):
        """
        Строковое представление объекта.
        """
        return self.title

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'
        ordering = ['title']
