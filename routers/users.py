from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models, schemas
from database import get_db
from routers.auth import get_current_user # ★ 13페이지 기능 위해 미리 추가

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 1. 회원가입 (POST /users/)
@router.post("/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="이미 등록된 사용자입니다.")
    
    # ★ [해결] 72글자 넘으면 짤라서 에러 방지 ([:72] 추가됨)
    hashed_password = pwd_context.hash(user.password[:72])

    new_user = models.User(
        username=user.username,
        hashed_password=hashed_password, 
        name=user.name,
        role=user.role,
        phone=user.phone,
        language=user.language,
        email=user.email,
        business_number=user.business_number,
        visa=user.visa,
        nationality=user.nationality,
        affiliated_farm_id=user.affiliated_farm_id,
        is_agreed=user.is_agreed
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# 2. 내 정보 조회 (GET /users/me) - ★ 13페이지 기능 미리 추가!
@router.get("/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user