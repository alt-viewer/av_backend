"""Utils! I couldn't think of a clever name, so these are now eggs D:"""
from utils.dict import omit, pick, replace_with, has_all
from utils.async_ import map_async

__all__ = [
    "omit",
    "replace_with",
    "pick",
    "has_all",
    "map_async",
]
