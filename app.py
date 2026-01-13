from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from rag.ingest import reindex
from rag.chat import query

app = FastAPI(title="Farm RAG Chatbot")


class QueryReq(BaseModel):
    farmId: str = "1"
    role: str = "WORKER"   # OWNER | WORKER
    question: str
    lang: str = "ko"
    k: int = 4


class ReindexReq(BaseModel):
    farmId: str = "1"


@app.get("/health")
def health():
    # UTF-8 명시 (PowerShell 출력 깨짐 완화에 도움)
    return JSONResponse({"ok": True}, media_type="application/json; charset=utf-8")


@app.post("/reindex")
def reindex_api(req: ReindexReq):
    try:
        result = reindex(req.farmId)
        return JSONResponse(result, media_type="application/json; charset=utf-8")
    except Exception as e:
        # 실제 에러 원인 확인 가능하게 detail에 넣어줌
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
def query_api(req: QueryReq):
    try:
        result = query(req.farmId, req.role, req.question, req.lang, req.k)
        return JSONResponse(result, media_type="application/json; charset=utf-8")
    except Exception as e:
        # 실제 에러 원인 확인 가능하게 detail에 넣어줌
        raise HTTPException(status_code=500, detail=str(e))
