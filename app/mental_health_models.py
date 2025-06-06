from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import validator

class MentalHealthBase(SQLModel):
    date: str = Field(..., min_length=3, max_length=50)
    age: int = Field(..., ge=10, le=100)
    gender: str = Field(..., min_length=1, max_length=30)
    relationship_status: str = Field(..., min_length=1, max_length=50)
    bothered_by_worries: int = Field(..., ge=1, le=5)
    difficulty_concentrating: int = Field(..., ge=1, le=5)
    comparison_feelings: int = Field(..., ge=1, le=5)
    feel_depressed: int = Field(..., ge=1, le=5)
    fluctuation_interest: int = Field(..., ge=1, le=5)
    sleep_issues: int = Field(..., ge=1, le=5)
    image_url: str = Field(..., min_length=3, max_length=500)

class MentalHealth(MentalHealthBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class MentalHealthCreate(MentalHealthBase):
    pass

class MentalHealthRead(MentalHealthBase):
    id: int

class MentalHealthUpdate(SQLModel):
    date: Optional[str] = Field(..., min_length=3, max_length=50)
    age: Optional[int] = Field(..., ge=10, le=100)
    gender: Optional[str] = Field(..., min_length=1, max_length=30)
    relationship_status: Optional[str] = Field(..., min_length=1, max_length=50)
    bothered_by_worries: Optional[int] = Field(..., ge=1, le=5)
    difficulty_concentrating: Optional[int] = Field(..., ge=1, le=5)
    comparison_feelings: Optional[int] = Field(..., ge=1, le=5)
    feel_depressed: Optional[int] = Field(..., ge=1, le=5)
    fluctuation_interest: Optional[int] = Field(..., ge=1, le=5)
    sleep_issues: Optional[int] = Field(..., ge=1, le=5)
    image_url: Optional[str] = Field(..., min_length=3, max_length=500)

    @validator('*', pre=True)
    def skip_blank_strings(cls, v):
        if v == "":
            return None
        return v

class MentalHealthResponse(SQLModel):
    id: int
    date: str
    age: int
    gender: str
    relationship_status: str
    bothered_by_worries: int
    difficulty_concentrating: int
    comparison_feelings: int
    feel_depressed: int
    fluctuation_interest: int
    sleep_issues: int
    image_url: str

class DeletedMentalHealth(MentalHealthBase, table=True):
    __tablename__ = "deleted_mental_health"
    id: Optional[int] = Field(default=None, primary_key=True)