from django.db import models


class ViolationWaiter(models.Model):
    violation = models.ForeignKey(
        "Violation",
        on_delete=models.CASCADE,
        verbose_name='Нарушение',
        related_name='violation_waiters',
    )
    waiter = models.ForeignKey(
        "Waiter",
        on_delete=models.CASCADE,
        verbose_name='Официант',
        related_name='violation_waiters',
    )
    role = models.CharField(
        max_length=50,
        verbose_name='Роль',
        help_text='Роль официанта в нарушении (например, "Нарушитель", "Обратная связь").',
    )

    class Meta:
        verbose_name = 'Связь нарушения и официанта'
        verbose_name_plural = 'Связи нарушений и официантов'
        unique_together = ('violation', 'waiter', 'role')  # Уникальная связь

    def __str__(self):
        return f'{self.waiter} - {self.role} в нарушении #{self.violation.id}'
