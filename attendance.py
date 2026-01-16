from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List, Optional

from database import get_db
from auth import get_current_user
import models, schemas

router = APIRouter(
    prefix="/attendance",
    tags=["출퇴근 관리 API"],
)

@router.post("/clock-in", 
             response_model=schemas.AttendanceResponse,
             summary="출근 등록",
             description="근로자가 현재 위치(GPS)와 함께 출근 기록을 생성합니다. 하루에 한 번만 가능합니다.")
def clock_in(location: schemas.AttendanceCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "worker":
        raise HTTPException(status_code=400, detail="근로자만 출근할 수 있습니다.")
    today = date.today()
    existing = db.query(models.Attendance).filter(models.Attendance.user_id == current_user.id, models.Attendance.date == today).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 오늘 출근 처리가 되었습니다.")
    new_attendance = models.Attendance(
        date=today, start_time=datetime.now(), latitude=location.latitude, longitude=location.longitude,
        user_id=current_user.id, farm_id=current_user.affiliated_farm_id, status="출근"
    )
    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)
    return new_attendance

@router.post("/clock-out", 
             response_model=schemas.AttendanceResponse,
             summary="퇴근 등록",
             description="근로자가 퇴근 시 위치를 기록하고 퇴근 시간을 업데이트합니다.")
def clock_out(location: schemas.AttendanceCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    today = date.today()
    attendance = db.query(models.Attendance).filter(models.Attendance.user_id == current_user.id, models.Attendance.date == today).first()
    if not attendance:
        raise HTTPException(status_code=400, detail="오늘 출근 기록이 없습니다.")
    attendance.end_time = datetime.now()
    attendance.latitude = location.latitude
    attendance.longitude = location.longitude
    attendance.status = "퇴근"
    db.commit()
    db.refresh(attendance)
    return attendance

@router.get("/history", 
            response_model=List[schemas.AttendanceResponse],
            summary="근무 기록 조회 (필터 포함)",
            description="사장님은 농장 전체 기록을, 근로자는 본인 기록만 볼 수 있습니다. 날짜와 아이디로 필터링이 가능합니다.")
def get_history(
    target_date: Optional[date] = Query(None, description="조회할 날짜 (YYYY-MM-DD)"),
    username: Optional[str] = Query(None, description="조회할 근로자 ID"),
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    query = db.query(models.Attendance)
    if current_user.role == "owner":
        my_farms = db.query(models.Farm).filter(models.Farm.owner_id == current_user.id).all()
        farm_ids = [f.id for f in my_farms]
        query = query.filter(models.Attendance.farm_id.in_(farm_ids))
    else:
        query = query.filter(models.Attendance.user_id == current_user.id)

    if target_date:
        query = query.filter(models.Attendance.date == target_date)
    if username:
        query = query.join(models.User).filter(models.User.username == username)
    return query.all()

@router.delete("/{attendance_id}", 
               summary="근무 기록 삭제",
               description="잘못 입력된 근태 기록을 삭제합니다. (사장님 권한 필요)")
def delete_attendance(attendance_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="사장님만 기록을 삭제할 수 있습니다.")
    record = db.query(models.Attendance).filter(models.Attendance.id == attendance_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="해당 기록을 찾을 수 없습니다.")
    db.delete(record)
    db.commit()
    return {"message": "기록이 성공적으로 삭제되었습니다."}