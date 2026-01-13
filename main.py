from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine

# 1. 라우터 불러오기 (auth는 아직 파일이 없어서 뺐습니다!)
from routers import users, farms 
from routers import auth

# 2. DB 테이블 자동 생성
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Agri-Partner API Server")

# 3. CORS 설정 (완벽합니다! 그대로 둡니다)
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

# 4. 기능 연결 (Users, Farms)
app.include_router(users.router)
app.include_router(farms.router)
app.include_router(auth.router)

# 5. 서버 생존신고
@app.get("/")
def read_root():
    return {"message": "Agri-Partner 서버가 정상 작동 중입니다! 🚀"}