from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models, schemas
from database import get_db
from routers.auth import get_current_user 

router = APIRouter(
    prefix="/farms",
    tags=["farms"],
)

# 1. 농장 등록 (POST /farms/)
@router.post("/", response_model=schemas.FarmResponse)
def create_farm(
    farm: schemas.FarmCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="농장주만 등록 가능")

    new_farm = models.Farm(
        name=farm.name,
        crop=farm.crop,         # ★ 작물 저장
        size=farm.size,         # ★ 규모 저장
        address=farm.address,
        latitude=farm.latitude,
        longitude=farm.longitude,
        owner_id=current_user.id 
    )
    
    db.add(new_farm)
    db.commit()
    db.refresh(new_farm)
    return new_farm

# 2. 농장 목록 조회 (GET /farms/) - ★ 검색 기능 + 로그인 해제
@router.get("/", response_model=List[schemas.FarmResponse])
def read_farms(
    skip: int = 0, 
    limit: int = 100, 
    search: str = None, 
    db: Session = Depends(get_db)
):
    query = db.query(models.Farm)
    if search:
        query = query.filter(models.Farm.name.ilike(f"%{search}%"))
    farms = query.offset(skip).limit(limit).all()
    return farms

# 3. 내 농장 보기 (GET /farms/my)
@router.get("/my", response_model=List[schemas.FarmResponse])
def read_my_farms(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    my_farms = db.query(models.Farm).filter(models.Farm.owner_id == current_user.id).all()
    return my_farms

# 4. 설정 저장
@router.post("/{farm_id}/settings", response_model=schemas.FarmSettingResponse)
def create_or_update_farm_setting(
    farm_id: int,
    setting: schemas.FarmSettingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    farm = db.query(models.Farm).filter(models.Farm.id == farm_id).first()
    if not farm or farm.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="권한이 없습니다.")

    db_setting = db.query(models.FarmSetting).filter(models.FarmSetting.farm_id == farm_id).first()

    if db_setting:
        for key, value in setting.dict(exclude_unset=True).items():
            setattr(db_setting, key, value)
    else:
        db_setting = models.FarmSetting(farm_id=farm_id, **setting.dict())
        db.add(db_setting)

    db.commit()
    db.refresh(db_setting)
    return db_setting

# 5. 설정 조회
@router.get("/{farm_id}/settings", response_model=schemas.FarmSettingResponse)
def read_farm_setting(farm_id: int, db: Session = Depends(get_db)):
    setting = db.query(models.FarmSetting).filter(models.FarmSetting.farm_id == farm_id).first()
    if not setting:
        raise HTTPException(status_code=404, detail="설정 없음")
    return setting