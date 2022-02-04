from abc import ABCMeta


class Jsonable(ABCMeta):
    def json(self) -> dict:
        ...
