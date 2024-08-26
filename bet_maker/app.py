from decimal import Decimal
from typing import Optional
import enum
import httpx
from fastapi import Depends, FastAPI, HTTPException, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, Bet as BetModel, init_db

init_db()

LINE_PROVIDER_URL = "http://line-provider:8080"

class BetStatus(enum.Enum):
    ONGOING = 1
    WIN = 2
    LOSE = 3

class Bet(BaseModel):
    event_id: str
    amount: Optional[Decimal] = None
    status: Optional[BetStatus] = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()

@app.post("/event-status-update")
async def update_status_event(event_id: str, status: int, db: Session = Depends(get_db)):
    db_bet = db.query(BetModel).filter(BetModel.event_id == event_id)
    if status == 2:
        db_bet.update({BetModel.status: BetStatus.WIN})
    else:
        db_bet.update({BetModel.status: BetStatus.LOSE})

@app.get('/bets')
async def get_bets(db: Session = Depends(get_db)):
    db_bets = db.query(BetModel).all()
    return db_bets

@app.get('/bet/{bet_id}')
async def get_bet(bet_id = Path(...),db: Session = Depends(get_db)):
    db_bet = db.query(BetModel).filter(BetModel.id == bet_id).first()
    if not db_bet:
        raise HTTPException(status_code=404,detail="Bet Not found")
    return db_bet

@app.put('/bet')
async def create_bet(bet: Bet, db: Session = Depends(get_db)):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{LINE_PROVIDER_URL}/events")
        if not bet.event_id in [ event['event_id'] for event in response.json()]:
            raise HTTPException(status_code=404,detail="Bet Not found")
    db_bet = BetModel(**bet)
    db.add(db_bet)
    db.commit()
    db.refresh(db_bet)
    return db_bet

@app.get('/events')
async def get_events():
    result = None
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{LINE_PROVIDER_URL}/events")
        result = JSONResponse(response.json())
    except Exception as e:
        print(e)
        result = JSONResponse({'error':str(e)},500)
    finally:
        return result
