from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
import models, schemas

router = APIRouter(
    prefix="/farms",
    tags=["farms"],
)

# [3단계] 농장 생성 (사장님만 가능)
@router.post("/", response_model=schemas.FarmResponse)
def create_farm(
    farm: schemas.FarmCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 1. 사장님(owner)인지 확인
    if current_user.role != "owner":
        raise HTTPException(status_code=400, detail="농장주만 농장을 등록할 수 있습니다.")
    
    # 2. 농장 데이터 저장 (여기에 latitude 같은 게 섞여있으면 에러가 납니다)
    # farm.dict()를 통해 schemas.py에 정의된 (name, crop, address, size)만 정확히 들어갑니다.
    db_farm = models.Farm(
        name=farm.name,
        crop=farm.crop,
        address=farm.address,
        size=farm.size,
        owner_id=current_user.id
    )
    
    db.add(db_farm)
    db.commit()
    db.refresh(db_farm)
    return db_farm

# 농장 검색 기능
@router.get("/search", response_model=list[schemas.FarmResponse])
def search_farms(
    query: str, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    farms = db.query(models.Farm).filter(models.Farm.name.contains(query)).all()
    return farms