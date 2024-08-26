import decimal
import enum
import time
from typing import Optional
import httpx
from fastapi import Depends, FastAPI, Path, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, Event as EventModel, init_db

init_db()

class EventState(enum.Enum):
    NEW = 1
    FINISHED_WIN = 2
    FINISHED_LOSE = 3


class Event(BaseModel):
    event_id: Optional[str] = None
    coefficient: Optional[decimal.Decimal] = None
    deadline: Optional[int] = None
    state: Optional[EventState] = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


@app.put('/event', response_model=Event)
async def create_event(event: Event, db: Session = Depends(get_db) ):
    db_event = db.query(EventModel).filter(EventModel.event_id == event.event_id).first()
    if db_event:
        raise HTTPException(status_code=400, detail="Event already exists")

    event_data = event.dict()
    event_data["state"] = event.state.value if event.state else None

    db_event = EventModel(**event_data)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


@app.get('/event/{event_id}')
async def get_event(event_id: str = Path(...), db: Session = Depends(get_db)):
    db_event = db.query(EventModel).filter(EventModel.event_id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")

    return db_event

async def notify_status_event(event_id: str, status: EventState):
    async with httpx.AsyncClient() as client:
        try:
            await client.post(f"http://bet_maker:8081/event-status-update", json={"event_id":event_id,"status":status})
        except Exception as e:
            print(e)

@app.put("/events/{event_id}", response_model=Event)
async def update_event(event: Event,event_id: str, db: Session = Depends(get_db)):
    db_event = db.query(EventModel).filter(EventModel.event_id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    if not event.state:
        raise HTTPException(status_code=404, detail="State not None")
    if db_event.state == EventState.NEW.value:
        db_event.state = event.state.value if event.state else None
        db.commit()
        db.refresh(db_event)
        await notify_status_event(event_id,event.state.value)
    return db_event

@app.get('/events')
async def get_events(db: Session = Depends(get_db)):
    db_events = db.query(EventModel).filter(EventModel.deadline >= time.time()).all()
    return db_events
