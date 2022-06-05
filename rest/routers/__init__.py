from rest.routers.deep_search import deep_search_router

# All the available routers
routers = [
    deep_search_router,
]

__all__ = [
    "routers",
    "deep_search_router",
]
