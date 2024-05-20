from datetime import date, time
from typing import Optional

from pydantic import BaseModel


class EventDTO(BaseModel):
    id: str
    title: str
    start_date: date
    start_time: time
    end_date: date
    end_time: time
    min_price: float
    max_price: float


class EventErrorDTO(BaseModel):
    code: str
    message: str


class EventsDTO(BaseModel):
    events: list[EventDTO]


class ResponseEventDTO(BaseModel):
    data: Optional[EventsDTO] = None
    error: Optional[EventErrorDTO] = None
