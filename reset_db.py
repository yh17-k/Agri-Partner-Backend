from database import engine, Base
from sqlalchemy import text
import models

def clear_db():
    print("⚠️ DB 초기화를 시작합니다 (강제 모드)...")
    
    with engine.connect() as conn:
        # 1. 외래 키 제약 조건 잠시 끄기 (이게 핵심!)
        conn.execute(text("DROP SCHEMA public CASCADE;"))
        conn.execute(text("CREATE SCHEMA public;"))
        conn.execute(text("GRANT ALL ON SCHEMA public TO postgres;"))
        conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))
        conn.commit()

    # 2. 테이블 다시 생성
    Base.metadata.create_all(bind=engine)
    print("✅ 모든 테이블이 삭제된 후 새로 생성되었습니다! 이제 진짜 깨끗합니다.")

if __name__ == "__main__":
    clear_db()