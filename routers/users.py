from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# 상위 폴더에 있는 파일들을 가져오기 위해 .. 문법 대신 절대 경로 방식 사용 권장
import models, schemas
from database import get_db # database.py에 get_db 함수가 있다고 가정

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

# 1. 회원가입 (Create User)
@router.post("/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. 중복 유저 체크
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="이미 등록된 아이디입니다.")

    # 2. DB 모델 생성 (여기가 핵심입니다!)
    # schemas.py에서 받은 데이터를 models.py의 양식에 맞춰 옮겨 담습니다.
    new_user = models.User(
        username=user.username,
        password=user.password,  # 실무에선 여기서 해싱(암호화)을 해야 합니다!
        name=user.name,
        role=user.role,
        phone=user.phone,
        language=user.language,
        email=user.email,
        business_number=user.business_number,
        visa=user.visa,
        nationality=user.nationality,
        affiliated_farm_id=user.affiliated_farm_id,
        # ▼▼▼ 에러가 났던 부분! 여기서 명시적으로 넣어주면 해결됩니다. ▼▼▼
        is_agreed=user.is_agreed 
    )

    # 3. DB 저장
    db.add(new_user)
    db.commit()
    db.refresh(new_user) # 저장된 후 생성된 ID 등을 다시 받아옴

    return new_user

# 2. 유저 목록 조회 (테스트용)
@router.get("/", response_model=List[schemas.UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users