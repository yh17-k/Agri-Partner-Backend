from pydantic import BaseModel
from typing import Optional

# --- 유저 (User) 관련 ---
class UserCreate(BaseModel):
    username: str
    password: str
    name: str
    role: str
    phone: str
    language: str = "ko"
    email: Optional[str] = None
    business_number: Optional[str] = None
    visa: Optional[str] = None
    nationality: Optional[str] = None
    affiliated_farm_id: Optional[int] = None
    is_agreed: bool = False

class UserResponse(UserCreate):
    id: int
    class Config:
        from_attributes = True

# --- 농장 (Farm) 관련 ---
class FarmCreate(BaseModel):
    name: str
    address: str
    latitude: Optional[str] = None
    longitude: Optional[str] = None

class FarmResponse(FarmCreate):
    id: int
    class Config:
        from_attributes = True

# --- 농장 상세 설정 (Farm Settings) ---
class FarmSettingCreate(BaseModel):
    wifi_id: Optional[str] = None
    wifi_pw: Optional[str] = None
    breakfast_time: Optional[str] = None
    lunch_time: Optional[str] = None
    dinner_time: Optional[str] = None
    dorm_rules: Optional[str] = None
    emergency_contact: Optional[str] = None

class FarmSettingResponse(FarmSettingCreate):
    id: int
    farm_id: int
    class Config:
        from_attributes = True

# --- 토큰 (Token) ---
class Token(BaseModel):
    access_token: str
    token_type: str