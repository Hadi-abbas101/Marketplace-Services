from .users import router as users_router
from .services import router as services_router
from .categories import router as categories_router
from .candidatures import router as candidatures_router
from .favoris import router as favoris_router
from .messages import router as messages_router
from .avis import router as avis_router

__all__ = [
    "users_router",
    "services_router",
    "categories_router",
    "candidatures_router",
    "favoris_router",
    "messages_router",
    "avis_router",
]