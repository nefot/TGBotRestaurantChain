from .contactInfo import ContactInfo

from .post import Post
from .violation import Violation
from .violationType import ViolationType
from .waiter import Waiter

# Опционально: можно указать, какие модели будут доступны при импорте из models
__all__ = ['Post', 'Violation', 'Waiter', 'ContactInfo','ViolationType']