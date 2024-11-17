from datetime import datetime, timezone
from pydantic import BaseModel, field_validator
from typing import List

class Schedule(BaseModel):
    users: List[str]
    handover_start_at: datetime
    handover_interval_days: int

    @field_validator('handover_interval_days')
    def validate_interval(cls, v):
        if v <= 0:
            raise ValueError('Handover interval must be positive')
        return v

    @field_validator('users')
    def validate_users(cls, v):
        if len(v) == 0:
            raise ValueError('Must have at least one user')
        return v

class Override(BaseModel):
    user: str
    start_at: datetime
    end_at: datetime

class Overrides(BaseModel):
    overrides: List[Override] 


class ScheduleEntry(BaseModel):
    user: str
    start_at: datetime
    end_at: datetime