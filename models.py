# models.py (전체 복사해서 덮어씌우기)
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float, DateTime
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    name = Column(String)
    role = Column(String)
    phone = Column(String, nullable=True)
    affiliated_farm_id = Column(Integer, ForeignKey("farms.id"), nullable=True)

    # [COM-006] 약관 동의
    agreed_terms = Column(Boolean, default=False)
    agreed_privacy = Column(Boolean, default=False)
    agreed_location = Column(Boolean, default=False)

    farm = relationship("Farm", back_populates="workers")

class Farm(Base):
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    owner_id = Column(Integer)
    location = Column(String)
    description = Column(String, nullable=True)

    workers = relationship("User", back_populates="farm")

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime, nullable=True)
    
    # [FRM-007] 근무 시간 (예: 25.3 시간)
    working_hours = Column(Float, nullable=True) 
    
    latitude = Column(Float)
    longitude = Column(Float)
    status = Column(String)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    farm_id = Column(Integer)