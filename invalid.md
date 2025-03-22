в представленной реализации будет 2 бота, 1 бот должен взаимодействовать со службой безопасности
2 будет взаимодействовать с официантами с +- одинаковыми интерфейсами, но по факту разными ботами

1 бот службы безопасности
на начальном экране будет выводиться общая информация о всех нарушениях
В службе безопасности будет 3 кнопки

- управление нарушениями
  здесь будут кнопки
    + Просмотр своих нарушений (Видит все нарушения которые он добавил)
    + Добавить нарушение (добавляет нарушение)
    + ОС на нарушение ()
      (ОС) - обратная связь
- управление профилем
    + Мой профиль
    + Профили сотрудника
        * Добавить нового сотрудника
- статистика
    + Вывод всех сотрудников
    + Поиск сотрудника по имени

2 бот сотрудника
Будут 3 кнопки

- Профиль сотрудника
    + Личные данные
    + История нарушений
- Главный интерфейс - Просмотр нарушений
  при нажатии выводится общая информация о всех нарушениях как и в 1 боте
  Если у него есть нарушения, то будут 3 кнопки
    + Исправлюсь
    + Не согласен (Комментарий почему)
    + Иное
- рейтинговая система
    + Публичный топ сотрудников

Форматы отображения:
было бы хорошо сделать единый шаблон форматов в отдельном файле и уже его отправлять

1. Просмотр своих нарушений:

- Фото
- Кто добавил нарушение
- Тип нарушения
- Выбор официанта из списка
- Примечание
- Дата нарушения
- Обратная связ от сотрудника (если есть)

2. Личные данные

- Фио
- Количество нарушений
- рейтинг

3. Мой профиль

- Фото
- ФИО
- Должность
- Контактная информация

Все данные берутся из бд, а также при добавлении какой-либо инфы через телеграм бот используется валидация как в моделях 


```python
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

```
```python
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

```
```python
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

```
```python
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
```
```python
from django.db import models
from django.core.validators import MinLengthValidator

from SecurityStaff.models import ContactInfo


class Waiter(models.Model):
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

    class Meta:
        verbose_name = 'Официант'
        verbose_name_plural = 'Официанты'
        ordering = ['last_name', 'first_name']

```
```python

```