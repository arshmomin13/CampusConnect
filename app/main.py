from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import Depends, FastAPI, Form, HTTPException, Query, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Event
from .schemas import EventCreate, EventRead, EventUpdate

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="CampusConnect", description="A simple campus event aggregator MVP", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/events", response_model=list[EventRead])
def list_events(
    q: str | None = Query(default=None, description="Search title, description, or location"),
    category: str | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(Event)
    if q and q.strip():
        term = f"%{q.strip()}%"
        stmt = stmt.where(or_(Event.title.ilike(term), Event.description.ilike(term), Event.location.ilike(term)))
    if category and category.lower() != "all":
        stmt = stmt.where(Event.category == category)
    if from_date:
        stmt = stmt.where(Event.date >= from_date)
    if to_date:
        stmt = stmt.where(Event.date <= to_date)
    stmt = stmt.order_by(Event.date.asc())
    return list(db.scalars(stmt).all())


@app.get("/api/events/{event_id}", response_model=EventRead)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@app.post("/api/events", response_model=EventRead, status_code=201)
def create_event(payload: EventCreate, db: Session = Depends(get_db)):
    event = Event(**payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@app.put("/api/events/{event_id}", response_model=EventRead)
def update_event(event_id: int, payload: EventUpdate, db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    for key, value in payload.model_dump().items():
        setattr(event, key, value)
    db.commit()
    db.refresh(event)
    return event


@app.delete("/api/events/{event_id}", status_code=204)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(event)
    db.commit()
    return Response(status_code=204)


@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    events = list(db.scalars(select(Event).order_by(Event.date.asc())).all())
    categories = sorted({event.category for event in events})
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"events": events, "categories": categories},
    )


@app.post("/events/new")
def create_event_from_form(
    title: str = Form(...),
    description: str = Form(""),
    date: str = Form(...),
    location: str = Form(""),
    category: str = Form("Other"),
    source_url: str = Form(""),
    db: Session = Depends(get_db),
):
    try:
        parsed_date = datetime.fromisoformat(date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Please provide a valid date and time")
    if not title.strip():
        raise HTTPException(status_code=400, detail="Title is required")
    event = Event(
        title=title.strip(),
        description=description.strip(),
        date=parsed_date,
        location=location.strip(),
        category=category.strip() or "Other",
        source_url=source_url.strip(),
    )
    db.add(event)
    db.commit()
    return RedirectResponse(url="/", status_code=303)


@app.post("/events/{event_id}/delete")
def delete_event_from_form(event_id: int, db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if event is not None:
        db.delete(event)
        db.commit()
    return RedirectResponse(url="/", status_code=303)
