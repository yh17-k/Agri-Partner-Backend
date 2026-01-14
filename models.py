from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    name = Column(String)
    role = Column(String) # "owner", "worker", "admin"
    phone = Column(String)
    language = Column(String, default="ko")
    
    # 선택 정보
    email = Column(String, nullable=True)
    business_number = Column(String, nullable=True)
    visa = Column(String, nullable=True)
    nationality = Column(String, nullable=True)
    
    # ★ 프로필 사진 (COM-003)
    profile_image = Column(String, nullable=True)
    
    # ★ 약관 동의
    is_agreed = Column(Boolean, default=False)
    
    # ★ [핵심] 근로자가 소속될 농장 ID
    affiliated_farm_id = Column(Integer, ForeignKey("farms.id"), nullable=True)

    # 관계 설정
    owned_farms = relationship("Farm", back_populates="owner", foreign_keys="Farm.owner_id")
    working_farm = relationship("Farm", back_populates="workers", foreign_keys=[affiliated_farm_id])


class Farm(Base):
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    
    # ★ [핵심] 작물 및 규모 (FRM-001)
    crop = Column(String)  
    size = Column(String, nullable=True)
    
    address = Column(String)
    farm_image = Column(String, nullable=True)
    
    latitude = Column(String, nullable=True)
    longitude = Column(String, nullable=True)

    owner_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="owned_farms", foreign_keys=[owner_id])
    workers = relationship("User", back_populates="working_farm", foreign_keys="User.affiliated_farm_id")
    setting = relationship("FarmSetting", uselist=False, back_populates="farm")


class FarmSetting(Base):
    __tablename__ = "farm_settings"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"))
    
    wifi_id = Column(String, nullable=True)
    wifi_pw = Column(String, nullable=True)
    breakfast_time = Column(String, nullable=True)
    lunch_time = Column(String, nullable=True)
    dinner_time = Column(String, nullable=True)
    dorm_rules = Column(String, nullable=True)
    emergency_contact = Column(String, nullable=True)

    farm = relationship("Farm", back_populates="setting")