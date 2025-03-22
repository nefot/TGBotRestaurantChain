from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator


def validate_image_size(image):
    """
    Валидация для изображения: проверка размера файла.
    Максимальный размер — 5 МБ.
    """
    max_size = 5 * 1024 * 1024  # 5 МБ
    if image.size > max_size:
        raise ValidationError('Размер изображения не должен превышать 5 МБ.')


class Violation(models.Model):
    # Изображение нарушения
    image = models.ImageField(
        upload_to='violations/images/',
        verbose_name='Изображение нарушения',
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_image_size,
        ],
        help_text='Загрузите изображение нарушения (формат: JPG, JPEG, PNG; размер: до 5 МБ).'
    )

    # Примечание к нарушению
    note = models.TextField(
        default='',
        verbose_name='Примечание',
        help_text='Введите дополнительную информацию о нарушении.',
        blank=True,
    )


    date = models.DateField(
        auto_now_add=True,
        verbose_name='Дата нарушения',
        help_text='Дата фиксации нарушения.',
    )

    # Связь с официантом (нарушителем)
    feedback = models.ForeignKey(
        "Waiter",
        on_delete=models.CASCADE,
        verbose_name='Официант',
        help_text='Выберите официанта, связанного с нарушением.',
    )
    feedback_by = models.ForeignKey(
        "Waiter",
        on_delete=models.SET_NULL,
        verbose_name='Обратная связь от',
        help_text='Выберите официанта, оставившего обратную связь.',
        null=True,
        blank=True,
    ),
    violation_type = models.ForeignKey(
        "ViolationType",
        on_delete=models.SET_NULL,
        verbose_name='Тип нарушения',
        help_text='Выберите тип нарушения.',
        null=True,
        blank=True,
    )

    def clean(self):
        """
        Валидация: обратная связь не может быть оставлена нарушителем.
        """
        if self.feedback_by and self.feedback_by == self.waiter:
            raise ValidationError({
                'feedback_by': 'Обратная связь не может быть оставлена нарушителем.'
            })

    def __str__(self):
        """
        Строковое представление объекта.
        """
        return f'Нарушение #{self.pk}'

    class Meta:
        verbose_name = 'Нарушение'
        verbose_name_plural = 'Нарушения'
        ordering = ['-date']