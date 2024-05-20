from abc import ABC

from pydantic import BaseModel


class AbstractEvent(BaseModel, ABC):
    pass
