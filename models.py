from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    name = Column(String)
    role = Column(String)  # 'owner' or 'worker'
    phone = Column(String)
    language = Column(String, default="ko")
    
    email = Column(String, nullable=True)
    business_number = Column(String, nullable=True)
    visa = Column(String, nullable=True)
    nationality = Column(String, nullable=True)
    is_agreed = Column(Boolean, default=False)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=True)
    affiliated_farm_id = Column(Integer, nullable=True) 

    # -------------------------------------------------------
    # [관계 설정 1: 사장님] 내가 소유한 농장들
    # (Farm 테이블의 owner_id를 바라봄)
    owned_farms = relationship("Farm", back_populates="owner", foreign_keys="Farm.owner_id")

    # [관계 설정 2: 직원] 내가 일하는 농장
    # (내 테이블의 farm_id를 바라봄)
    working_farm = relationship("Farm", back_populates="workers", foreign_keys=[farm_id])
    # -------------------------------------------------------


class Farm(Base):
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String)
    
    # [사장님용] 이 농장의 주인 ID
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    latitude = Column(String, nullable=True)
    longitude = Column(String, nullable=True)

    # -------------------------------------------------------
    # [관계 설정 1: 사장님] 이 농장의 주인
    owner = relationship("User", back_populates="owned_farms", foreign_keys=[owner_id])
    
    # [관계 설정 2: 직원] 이 농장에서 일하는 직원들
    workers = relationship("User", back_populates="working_farm", foreign_keys="User.farm_id")
    
    # [관계 설정 3] 상세 설정 (와이파이 등)
    setting = relationship("FarmSetting", uselist=False, back_populates="farm")
    # -------------------------------------------------------


class FarmSetting(Base):
    __tablename__ = "farm_settings"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), unique=True)
    
    wifi_id = Column(String, nullable=True)
    wifi_pw = Column(String, nullable=True)
    
    breakfast_time = Column(String, nullable=True)
    lunch_time = Column(String, nullable=True)
    dinner_time = Column(String, nullable=True)
    
    dorm_rules = Column(Text, nullable=True)
    emergency_contact = Column(String, nullable=True)

    farm = relationship("Farm", back_populates="setting")