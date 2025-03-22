from django.core.management.base import BaseCommand
from faker import Faker
from SecurityStaff.models import ContactInfo, Post, Violation, ViolationType, Waiter


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными'

    def handle(self, *args, **kwargs):
        fake = Faker('ru_RU')
        self.stdout.write("Создание тестовых данных...")

        contact_infos = []
        for _ in range(10):
            contact = ContactInfo(
                email=fake.email(),
                phone=fake.phone_number(),
                address=fake.address(),
            )
            contact.save()
            contact_infos.append(contact)
        self.stdout.write("Создано 10 контактных записей.")

        # Создание Post (должностей)
        posts = []
        for _ in range(5):
            post = Post(
                title=fake.job(),
                description=fake.text(),
                salary=fake.random_int(min=20000, max=100000),
                experience_required=fake.random_int(min=0, max=10),
            )
            post.save()
            posts.append(post)
        self.stdout.write("Создано 5 должностей.")

        # Создание Waiter (официантов)
        waiters = []
        for _ in range(10):
            waiter = Waiter(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                patronymic=fake.middle_name(),
                contact_info=fake.random_element(elements=contact_infos),
            )
            waiter.save()
            # Назначаем случайные должности официанту
            waiter.posts.set(fake.random_elements(elements=posts, length=fake.random_int(min=1, max=3)))
            waiters.append(waiter)
        self.stdout.write("Создано 10 официантов.")

        # Создание ViolationType (типов нарушений)
        violation_types = []
        for _ in range(5):
            violation_type = ViolationType(
                name=fake.word().capitalize() + " нарушение",
                description=fake.text(),
            )
            violation_type.save()
            violation_types.append(violation_type)
        self.stdout.write("Создано 5 типов нарушений.")

        # Создание Violation (нарушений)
        for _ in range(20):
            violation = Violation(
                note=fake.text(),
                feedback=fake.random_element(elements=waiters),
                violation_type=fake.random_element(elements=violation_types),
            )
            violation.save()
        self.stdout.write("Создано 20 нарушений.")

        self.stdout.write(self.style.SUCCESS("Тестовые данные успешно созданы!"))
