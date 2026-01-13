from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import urllib.parse

# 1. 비밀번호 특수문자(!!) 안전하게 처리
# (그냥 넣으면 에러 날 수 있어서 코드로 감쌌습니다)
password = urllib.parse.quote_plus("AgriMaster2026!!")

# 2. Supabase 연결 주소 (사장님이 주신 aws-1 서버)
SQLALCHEMY_DATABASE_URL = f"postgresql://postgres.oetssbtrdaswdtgvrkqj:{password}@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres"

# 3. 엔진 실행
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()