# SecurityStaff/telegramBot/templates.py

def violation_template(violation):
    return (
        f"📷 Фото: {violation.image.url}\n"
        f"👤 Кто добавил: {violation.feedback_by}\n"
        f"🚨 Тип нарушения: {violation.violation_type.name}\n"
        f"👨‍💼 Официант: {violation.waiter}\n"
        f"📝 Примечание: {violation.note}\n"
        f"📅 Дата нарушения: {violation.date}\n"
        f"💬 Обратная связь: {violation.feedback if violation.feedback else 'Нет'}\n"
        f"🔒 Состояние: {violation.status.name if violation.status else 'Не указано'}"
    )


def personal_data_template(waiter):
    return (
        f"👤 ФИО: {waiter.last_name} {waiter.first_name} {waiter.patronymic}\n"
        f"🚨 Количество нарушений: {waiter.violations.count()}\n"
        f"⭐ Рейтинг: {waiter.rating}"
    )


def profile_template(waiter):
    return (
        f"📷 Фото: {waiter.image.url}\n"
        f"👤 ФИО: {waiter.last_name} {waiter.first_name} {waiter.patronymic}\n"
        f"💼 Должность: {', '.join([post.title for post in waiter.posts.all()])}\n"
        f"📞 Контактная информация: {waiter.contact_info.email}, {waiter.contact_info.phone}"
    )
