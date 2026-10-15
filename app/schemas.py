from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class EventFields(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=5000)
    date: datetime
    location: str = Field(default="", max_length=200)
    category: str = Field(default="Other", min_length=1, max_length=80)
    source_url: str = Field(default="", max_length=1000)



class EventPatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    date: datetime | None = None
    location: str | None = Field(default=None, max_length=200)
    category: str | None = Field(default=None, min_length=1, max_length=80)
    source_url: str | None = Field(default=None, max_length=1000)


class EventCreate(EventFields):
    pass


class EventUpdate(EventFields):
    pass


class EventRead(EventFields):
    id: int
    model_config = ConfigDict(from_attributes=True)
