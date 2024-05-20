from datetime import datetime

from pydantic import BaseModel


class FilterQuery(BaseModel):
    starts_at: datetime
    ends_at: datetime


class DatabaseError(Exception):
    pass
