from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models, schemas, auth
from database import get_db

router = APIRouter(
    prefix="/users",
    tags=["사용자 관리 (USR)"],
)

@router.post("/", response_model=schemas.UserResponse, summary="회원가입")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. 중복 ID 체크
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 아이디입니다.")
    
    # ★ [COM-006] 2. 필수 약관 동의 검증 (서버측 방어)
    if not (user.agreed_terms and user.agreed_privacy and user.agreed_location):
        raise HTTPException(status_code=400, detail="필수 약관에 모두 동의해야 가입할 수 있습니다.")

    # 3. 사용자 저장
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        name=user.name,
        role=user.role,
        phone=user.phone,
        # 약관 동의 저장
        agreed_terms=user.agreed_terms,
        agreed_privacy=user.agreed_privacy,
        agreed_location=user.agreed_location
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# [기존] 농장 취직/가입
@router.put("/join", summary="농장 소속 신청")
def join_farm(farm_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != "worker":
        raise HTTPException(status_code=400, detail="근로자만 농장에 가입할 수 있습니다.")
    
    farm = db.query(models.Farm).filter(models.Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="해당 농장을 찾을 수 없습니다.")
    
    current_user.affiliated_farm_id = farm.id
    db.commit()
    return {"message": f"{farm.name}에 성공적으로 소속되었습니다!"}

# ★ [COM-003 신규] 내 프로필 조회
@router.get("/me", response_model=schemas.UserResponse, summary="내 프로필 조회")
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    """
    현재 로그인된 사용자의 상세 정보를 조회합니다.
    """
    return current_user

# ★ [COM-003 신규] 내 프로필 수정
@router.put("/me", response_model=schemas.UserResponse, summary="내 프로필 수정")
def update_user_me(
    user_update: schemas.UserUpdate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    현재 로그인된 사용자의 이름이나 연락처를 수정합니다.
    """
    # 입력된 값이 있을 때만 수정 (없으면 기존 데이터 유지)
    if user_update.name:
        current_user.name = user_update.name
    if user_update.phone:
        current_user.phone = user_update.phone
    
    db.commit()
    db.refresh(current_user)
    return current_user