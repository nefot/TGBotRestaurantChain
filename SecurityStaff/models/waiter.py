from django.core.validators import MinLengthValidator
from django.db import models

from SecurityStaff.models import ContactInfo, Violation


class Waiter(models.Model):
    user_id = models.BigIntegerField(unique=False, verbose_name="ID пользователя Telegram")
    # Фотография официанта
    image = models.ImageField(
        upload_to='waiters/images/',
        verbose_name='Фотография',
        help_text='Загрузите фотографию официанта.',
        blank=True,
    )

    # Имя
    first_name = models.CharField(
        max_length=50,
        verbose_name='Имя',
        help_text='Введите имя официанта.',
        validators=[MinLengthValidator(2, 'Имя должно содержать минимум 2 символа.')],
    )

    # Фамилия
    last_name = models.CharField(
        max_length=50,
        verbose_name='Фамилия',
        help_text='Введите фамилию официанта.',
        validators=[MinLengthValidator(2, 'Фамилия должна содержать минимум 2 символа.')],
    )

    # Отчество
    patronymic = models.CharField(
        max_length=50,
        verbose_name='Отчество',
        help_text='Введите отчество официанта.',
        blank=True,
    )

    # Должности (связь Many-to-Many с моделью Post)
    posts = models.ManyToManyField(
        "Post",
        verbose_name='Должности',
        help_text='Выберите должности официанта.',
        related_name='waiters',
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
    contact_info = models.ForeignKey(
        ContactInfo,
        on_delete=models.SET_NULL,
        related_name='waiters',
        null=True, blank=True
    )

    def __str__(self):
        """
        Строковое представление объекта.
        """
        return f'{self.last_name} {self.first_name} {self.patronymic}'

    def delete_violations(self):
        """Удаляет все нарушения, связанные с этим официантом"""
        violations = Violation.objects.filter(violation_waiters__waiter=self)
        for violation in violations:
            violation.delete()  # Это вызовет каскадное удаление через ViolationWaiter

    def delete(self, *args, **kwargs):
        """Переопределяем стандартное удаление для очистки нарушений"""
        self.delete_violations()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'Официант'
        verbose_name_plural = 'Официанты'
        ordering = ['last_name', 'first_name']
