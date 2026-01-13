from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import models, schemas
from database import get_db
# auth.py에서 로그인한 유저 정보를 가져오는 함수를 불러옵니다
from routers.auth import get_current_user 

router = APIRouter(
    prefix="/farms",
    tags=["farms"],
)

# 1. 농장 등록 (POST /farms/)
# ★ 로그인한 사람만 가능 (current_user)
@router.post("/", response_model=schemas.FarmResponse)
def create_farm(
    farm: schemas.FarmCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # (옵션) 사장님(owner) 권한이 있는 사람만 농장을 만들게 하려면?
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="농장주(owner)만 농장을 등록할 수 있습니다.")

    # DB 모델 생성
    new_farm = models.Farm(
        name=farm.name,
        address=farm.address,
        latitude=farm.latitude,
        longitude=farm.longitude,
        # ★ 여기가 핵심! 로그인한 유저의 ID를 주인 ID로 자동 등록
        owner_id=current_user.id 
    )
    
    db.add(new_farm)
    db.commit()
    db.refresh(new_farm)
    
    return new_farm

# 2. 농장 목록 조회 (GET /farms/)
@router.get("/", response_model=List[schemas.FarmResponse])
def read_farms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    farms = db.query(models.Farm).offset(skip).limit(limit).all()
    return farms

# 3. 내 농장만 보기 (GET /farms/my)
@router.get("/my", response_model=List[schemas.FarmResponse])
def read_my_farms(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # 내가 주인인 농장만 찾아서 보여줌
    my_farms = db.query(models.Farm).filter(models.Farm.owner_id == current_user.id).all()
    return my_farms

# routers/farms.py 맨 아래에 추가

# 4. 농장 상세 설정 등록/수정 (POST /farms/{farm_id}/settings)
@router.post("/{farm_id}/settings", response_model=schemas.FarmSettingResponse)
def create_or_update_farm_setting(
    farm_id: int,
    setting: schemas.FarmSettingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 1. 농장이 존재하는지, 그리고 내가 주인인지 확인
    farm = db.query(models.Farm).filter(models.Farm.id == farm_id).first()
    
    if not farm:
        raise HTTPException(status_code=404, detail="농장을 찾을 수 없습니다.")
    if farm.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="본인 소유의 농장 설정만 변경할 수 있습니다.")

    # 2. 이미 설정이 있는지 확인
    db_setting = db.query(models.FarmSetting).filter(models.FarmSetting.farm_id == farm_id).first()

    if db_setting:
        # (A) 있으면 수정 (Update)
        db_setting.wifi_id = setting.wifi_id
        db_setting.wifi_pw = setting.wifi_pw
        db_setting.breakfast_time = setting.breakfast_time
        db_setting.lunch_time = setting.lunch_time
        db_setting.dinner_time = setting.dinner_time
        db_setting.dorm_rules = setting.dorm_rules
        db_setting.emergency_contact = setting.emergency_contact
    else:
        # (B) 없으면 생성 (Create)
        db_setting = models.FarmSetting(
            farm_id=farm_id,
            wifi_id=setting.wifi_id,
            wifi_pw=setting.wifi_pw,
            breakfast_time=setting.breakfast_time,
            lunch_time=setting.lunch_time,
            dinner_time=setting.dinner_time,
            dorm_rules=setting.dorm_rules,
            emergency_contact=setting.emergency_contact
        )
        db.add(db_setting)

    db.commit()
    db.refresh(db_setting)
    
    return db_setting

# 5. 농장 상세 설정 조회 (GET /farms/{farm_id}/settings)
@router.get("/{farm_id}/settings", response_model=schemas.FarmSettingResponse)
def read_farm_setting(
    farm_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 1. 설정값 찾기
    setting = db.query(models.FarmSetting).filter(models.FarmSetting.farm_id == farm_id).first()
    
    if not setting:
        raise HTTPException(status_code=404, detail="아직 설정이 등록되지 않았습니다.")
        
    return setting