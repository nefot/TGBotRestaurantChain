from django.core.management.base import BaseCommand
from faker import Faker

from SecurityStaff.models import ContactInfo, Post, Violation, ViolationType, Waiter, ViolationStatus, ViolationWaiter


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными'

    def handle(self, *args, **kwargs):
        fake = Faker('ru_RU')
        self.stdout.write("Создание тестовых данных...")

        self.stdout.write("Очистка существующих данных...")
        ViolationWaiter.objects.all().delete()
        Violation.objects.all().delete()
        Waiter.objects.all().delete()
        ViolationType.objects.all().delete()
        Post.objects.all().delete()
        ContactInfo.objects.all().delete()
        ViolationStatus.objects.all().delete()
        self.stdout.write("Существующие данные очищены.")

        # Создание ContactInfo (контактной информации)
        contact_infos = []
        _i = 10
        for _ in range(_i):
            contact = ContactInfo(
                email=fake.email(),
                phone=fake.phone_number(),
                address=fake.address(),
            )
            contact.save()
            contact_infos.append(contact)
        self.stdout.write(f"Создано {_i} контактных записей.")

        # Создание Post (должностей)
        posts = []
        _i = 5
        for _ in range(_i):
            post = Post(
                title=fake.job(),
                description=fake.text(),
                salary=fake.random_int(min=20000, max=100000),
                experience_required=fake.random_int(min=0, max=10),
            )
            post.save()
            posts.append(post)
        self.stdout.write(f"Создано {_i} должностей.")

        # Создание Waiter (официантов)
        waiters = []
        _i = 10
        for i in range(_i):
            waiter = Waiter(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                patronymic=fake.middle_name(),
                contact_info=fake.random_element(elements=contact_infos),
                user_id=i + 1,
            )
            waiter.save()

            waiter.posts.set(fake.random_elements(elements=posts, length=fake.random_int(min=1, max=3)))
            waiters.append(waiter)
        self.stdout.write(f"Создано {_i} официантов.")

        # Создание ViolationType (типов нарушений)
        violation_types = []
        _i = 5
        for _ in range(_i):
            violation_type = ViolationType(
                name=fake.word().capitalize() + " нарушение",
                description=fake.text(),
            )
            violation_type.save()
            violation_types.append(violation_type)
        self.stdout.write(f"Создано {_i} типов нарушений.")

        # Создание ViolationStatus (состояний нарушений)
        violation_statuses = []
        status_names = ["Открыто", "В процессе", "Закрыто"]
        for name in status_names:
            status = ViolationStatus(name=name)
            status.save()
            violation_statuses.append(status)
        self.stdout.write(f"Создано {len(status_names)} состояний нарушений.")

        # Создание Violation (нарушений)
        _i = 122
        for _ in range(_i):
            violation = Violation(
                note=fake.text(),
                violation_type=fake.random_element(elements=violation_types),
                status=fake.random_element(elements=violation_statuses),
            )
            violation.save()

            violator = fake.random_element(elements=waiters)
            ViolationWaiter.objects.create(
                violation=violation,
                waiter=violator,
                role='Нарушитель',
            )

            # Выбираем случайного официанта как оставившего обратную связь (опционально)
            if fake.boolean(chance_of_getting_true=50):
                feedback_by = fake.random_element(elements=waiters)
                if feedback_by != violator:
                    ViolationWaiter.objects.create(
                        violation=violation,
                        waiter=feedback_by,
                        role='Обратная связь',
                    )

        self.stdout.write(f"Создано {_i} нарушений.")

        self.stdout.write(self.style.SUCCESS("Тестовые данные успешно созданы!"))
