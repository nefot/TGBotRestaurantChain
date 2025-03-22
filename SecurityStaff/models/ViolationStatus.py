from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

class ViolationStatus(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название состояния',
        help_text='Введите название состояния нарушения (например, "Открыто", "В процессе", "Закрыто").',
        unique=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Состояние нарушения'
        verbose_name_plural = 'Состояния нарушений'
        ordering = ['name']
