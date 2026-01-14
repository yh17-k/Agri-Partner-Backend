from sqlalchemy import text
from database import engine
from models import Base
import models

print("🚧 데이터베이스 강제 초기화(CASCADE) 시작...")

try:
    with engine.connect() as conn:
        # 1. 무식하게 강제로 테이블 날리기 (CASCADE 옵션 사용)
        # 순서 상관없이 연결된 거 다 끊고 지워버립니다.
        conn.execute(text("DROP TABLE IF EXISTS farm_settings CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS farms CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
        conn.commit()
        print("🗑️  기존 테이블 강제 삭제 완료!")

    # 2. 다시 예쁘게 짓기
    Base.metadata.create_all(bind=engine)
    print("✨  새로운 테이블 생성 완료!")
    print("✅  DB 초기화 성공! 이제 서버를 켜세요.")

except Exception as e:
    print(f"❌ 오류 발생: {e}")