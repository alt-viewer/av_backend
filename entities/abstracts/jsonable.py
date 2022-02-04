from abc import ABC


class Jsonable(ABC):
    def json(self) -> dict:
        ...
