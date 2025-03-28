from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator


class ViolationType(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название типа нарушения',
        help_text='Введите название типа нарушения (например, "Опоздание").',
        unique=True,
    )

    # Описание типа нарушения
    description = models.TextField(
        verbose_name='Описание типа нарушения',
        help_text='Введите описание типа нарушения.',
        blank=True,
    )

    def __str__(self):
        """
        Строковое представление объекта.
        """
        return self.name

    class Meta:
        verbose_name = 'Тип нарушения'
        verbose_name_plural = 'Типы нарушений'
        ordering = ['name']