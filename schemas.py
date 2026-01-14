from pydantic import BaseModel
from typing import List, Optional

# --- 토큰 ---
class Token(BaseModel):
    access_token: str
    token_type: str

# --- 유저 (공통 부분) ---
# 비밀번호 빼고 나머지 다 들어감
class UserBase(BaseModel):
    username: str
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

# --- 유저 생성용 (입력) ---
# ★ 비밀번호는 가입할 때만 필요함!
class UserCreate(UserBase):
    password: str

# --- 유저 응답용 (출력) ---
# ★ 비밀번호 없음! (보안 통과, 에러 해결)
class UserResponse(UserBase):
    id: int
    # farm_id는 필요하면 계산해서 넣거나, affiliated_farm_id로 대체
    
    class Config:
        from_attributes = True

# --- 농장 설정 ---
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

# --- 농장 ---
class FarmCreate(BaseModel):
    name: str
    crop: str
    size: Optional[str] = None
    address: str
    latitude: Optional[str] = None
    longitude: Optional[str] = None

class FarmResponse(FarmCreate):
    id: int
    owner_id: int
    
    class Config:
        from_attributes = True