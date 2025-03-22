from django.db import models
from django.core.validators import EmailValidator, RegexValidator


class ContactInfo(models.Model):
    # Электронная почта
    email = models.CharField(
        max_length=254,
        verbose_name='Электронная почта',
        validators=[EmailValidator(message='Введите корректный адрес электронной почты.')],
        help_text='Введите адрес электронной почты.',
        unique=True,
    )

    # Номер телефона
    phone = models.CharField(
        max_length=20,
        verbose_name='Номер телефона',
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message='Номер телефона должен быть в формате: "+999999999". Допустимо от 9 до 15 цифр.'
            )
        ],
        help_text='Введите номер телефона в формате +999999999.',
        blank=True,
    )

    # Адрес
    address = models.TextField(
        verbose_name='Адрес',
        help_text='Введите полный адрес.',
        blank=True,
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
        return self.email

    class Meta:
        verbose_name = 'Контактная информация'
        verbose_name_plural = 'Контактные информации'
        ordering = ['email']
