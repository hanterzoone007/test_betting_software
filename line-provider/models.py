from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class EventStatus(BaseModel):
    id: str
    name: str

class Event(BaseModel):
    id: str
    odds: float
    deadline: datetime
    status: EventStatus  # "ongoing", "team1_wins", "team2_wins"

class EventCreate(BaseModel):
    id: str
    odds: float
    deadline: datetime
