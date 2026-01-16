from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

# DB 설정
import models
from database import engine

# ★ 이제 모든 파일이 같은 폴더에 있습니다! (경로 문제 해결)
import users
import farms
import auth
import attendance

# 1. DB 테이블 자동 생성
models.Base.metadata.create_all(bind=engine)

# 2. 앱 생성
app = FastAPI(title="Agri-Partner API Server")

origins = [
    "http://localhost:3000", # 리액트(React) 보통 포트
    "http://localhost:8080", # 뷰(Vue) 보통 포트
    "*",                     # 에라이 모르겠다, 모든 곳에서 다 허용해! (개발용)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # GET, POST, PUT, DELETE 다 허용
    allow_headers=["*"], # 모든 헤더 허용
)

# 3. CORS 설정
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. 기능 연결 (폴더 이름 없이 바로 연결!)
app.include_router(users.router)
app.include_router(farms.router)
app.include_router(auth.router)
app.include_router(attendance.router)

# 5. 서버 생존신고
@app.get("/")
def read_root():
    return {"message": "Agri-Partner 서버가 정상 작동 중입니다! 🚀"}