from builtins import ValueError, any, bool, str
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid
import re
from app.utils.nickname_gen import generate_nickname
from pydantic import ConfigDict


class UserRole(str, Enum):
    ANONYMOUS = "ANONYMOUS"
    AUTHENTICATED = "AUTHENTICATED"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"


def validate_url(url: Optional[str]) -> Optional[str]:
    if url is None:
        return url
    url_regex = r'^https?:\/\/[^\s/$.?#].[^\s]*$'
    if not re.match(url_regex, url):
        raise ValueError('Invalid URL format')
    return url


class UserBase(BaseModel):
    email: EmailStr = Field(..., json_schema_extra={'example' == "john.doe@example.com"})
    nickname: Optional[str] = Field(
        None, min_length=3, pattern=r'^[\w-]+$', json_schema_extra={'example' == "johnny_dev"})
    first_name: Optional[str] = Field(None, json_schema_extra={'example' == "John"})
    last_name: Optional[str] = Field(None, json_schema_extra={'example' == "Doe"})
    bio: Optional[str] = Field(None, json_schema_extra={'example' == "Experienced developer specializing in web applications."})
    profile_picture_url: Optional[str] = Field(None, json_schema_extra={'example' == "https://example.com/profiles/john.jpg"})
    linkedin_profile_url: Optional[str] = Field(None, json_schema_extra={'example' == "https://linkedin.com/in/johndoe"})
    github_profile_url: Optional[str] = Field(None, json_schema_extra={'example' == "https://github.com/johndoe"})

    _validate_urls = field_validator(
        'profile_picture_url', 'linkedin_profile_url', 'github_profile_url',
        mode='before'

    )(validate_url)

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    password: str = Field(..., json_schema_extra={'example' == "Secure*1234"})


class UserUpdate(UserBase):

    @model_validator(mode='before')
    def check_at_least_one_value(cls, values):
        if not any(values.values()):
            raise ValueError("At least one field must be provided for update")
        return values


class UserResponse(UserBase):
    id: uuid.UUID = Field(..., json_schema_extra={'example'==str(uuid.uuid4())})
    role: UserRole = Field(default=UserRole.AUTHENTICATED, json_schema_extra={'example' == "AUTHENTICATED"})
    is_professional: Optional[bool] = Field(default=False, json_schema_extra={'example'== True})


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., json_schema_extra={'example' == "john.doe@example.com"})
    password: str = Field(..., json_schema_extra={'example' == "Secure*1234"})


class ErrorResponse(BaseModel):
    error: str = Field(..., json_schema_extra={'example' == "Not Found"})
    details: Optional[str] = Field(None, json_schema_extra={'example' == "The requested resource was not found."})


class UserListResponse(BaseModel):
    items: List[UserResponse] = Field(
        ...,
        json_schema_extra={'example' == [
            {
                "id": str(uuid.uuid4()),
                "nickname": "johnny_dev",
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "bio": "Experienced developer",
                "role": "AUTHENTICATED",
                "profile_picture_url": "https://example.com/profiles/john.jpg",
                "linkedin_profile_url": "https://linkedin.com/in/johndoe",
                "github_profile_url": "https://github.com/johndoe",
                "is_professional": True
            }
        ]
   } )
    total: int = Field(..., json_schema_extra={'example' == 100})
    page: int = Field(..., json_schema_extra={'example' == 1})
    size: int = Field(..., json_schema_extra={'example' == 10})
