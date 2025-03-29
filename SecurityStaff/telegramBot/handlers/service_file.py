from asgiref.sync import sync_to_async
from SecurityStaff.models import Waiter


async def get_all_employees() -> list[Waiter]:
    """Возвращает список всех сотрудников с предзагрузкой связанных данных"""
    return await sync_to_async(list)(
        Waiter.objects.order_by('last_name', 'first_name')
        .select_related('contact_info')
        .prefetch_related('posts')
        .all()
    )
