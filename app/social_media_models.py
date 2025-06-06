from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import validator

class SocialMediaBase(SQLModel):
    date: str = Field(..., min_length=3, max_length=50)
    age: int = Field(..., ge=10, le=100)
    gender: str = Field(..., min_length=1, max_length=30)
    occupation_status: str = Field(..., min_length=1, max_length=50)
    organization_affiliation: str = Field(default=None, max_length=100)
    uses_social_media: str = Field(..., regex=r"^(Yes|No)$")
    platforms_used: str = Field(..., min_length=1, max_length=255)
    daily_use_average: str = Field(..., min_length=1, max_length=50)
    usage_without_purpose: int = Field(..., ge=1, le=5)
    distraction_when_busy: int = Field(..., ge=1, le=5)
    restless_without_social_media: int = Field(..., ge=1, le=5)
    easily_distracted: int = Field(..., ge=1, le=5)
    compare_with_successful_people: int = Field(..., ge=1, le=5)
    seek_validation: int = Field(..., ge=1, le=5)
    image_url: str = Field(..., min_length=3, max_length=500)

class SocialMedia(SocialMediaBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class SocialMediaCreate(SocialMediaBase):
    pass

class SocialMediaRead(SocialMediaBase):
    id: int

class SocialMediaUpdate(SQLModel):
    date: Optional[str] = Field(None, min_length=3, max_length=50)
    age: Optional[int] = Field(..., ge=10, le=100)
    gender: Optional[str] = Field(..., min_length=1, max_length=30)
    occupation_status: Optional[str] = Field(..., min_length=1, max_length=50)
    organization_affiliation: Optional[str] = Field(default=None, max_length=100)
    uses_social_media: Optional[str] = Field(..., regex=r"^(Yes|No)$")
    platforms_used: Optional[str] = Field(..., min_length=1, max_length=255)
    daily_use_average: Optional[str] = Field(..., min_length=1, max_length=50)
    usage_without_purpose: Optional[int] = Field(..., ge=1, le=5)
    distraction_when_busy: Optional[int] = Field(..., ge=1, le=5)
    restless_without_social_media: Optional[int] = Field(..., ge=1, le=5)
    easily_distracted: Optional[int] = Field(..., ge=1, le=5)
    compare_with_successful_people: Optional[int] = Field(..., ge=1, le=5)
    seek_validation: Optional[int] = Field(..., ge=1, le=5)
    image_url: Optional[str] = Field(..., min_length=3, max_length=500)

    @validator('*', pre=True)
    def skip_blank_strings(cls, v):
        if v == "":
            return None
        return v

class SocialMediaResponse(SQLModel):
    id: int
    date: str
    age: int
    gender: str
    occupation_status: str
    organization_affiliation: str
    uses_social_media: str
    platforms_used: str
    daily_use_average: str
    usage_without_purpose: int
    distraction_when_busy: int
    restless_without_social_media: int
    easily_distracted: int
    compare_with_successful_people: int
    seek_validation: int
    image_url: str

class DeletedSocialMedia(SocialMediaBase, table=True):
    __tablename__ = "deleted_social_media"
    id: Optional[int] = Field(default=None, primary_key=True)