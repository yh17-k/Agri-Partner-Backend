import os
import re
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate

from .prompt import system_prompt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")

# .env 로드
load_dotenv(os.path.join(BASE_DIR, ".env"))


def _load_db(farm_id: str):
    db_dir = os.path.join(STORAGE_DIR, f"farm_{farm_id}")
    if not os.path.exists(db_dir):
        raise RuntimeError(f"벡터 DB가 없습니다. 먼저 reindex 하세요: {db_dir}")

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    return FAISS.load_local(
        db_dir,
        embeddings,
        allow_dangerous_deserialization=True
    )


def _extract_section(text: str, question: str) -> str:
    """
    질문 키워드에 맞는 섹션만 문서에서 추출
    """
    q = question.replace(" ", "")

    target = None
    if "준비" in q or "수확전" in q:
        target = "1"
    elif "순서" in q:
        target = "2"
    elif "정리" in q or "수확후" in q:
        target = "3"
    elif "안전" in q or "주의" in q:
        target = "4"

    if not target:
        return text

    # 섹션 패턴: "1. xxx" ~ 다음 번호 전까지
    pattern = rf"\n{target}\.\s.*?(?=\n[1-9]\.\s|\Z)"
    match = re.search(pattern, "\n" + text, flags=re.DOTALL)

    if match:
        return match.group(0).strip()

    return text


def query(
    farm_id: str,
    role: str,
    question: str,
    lang: str = "ko",
    k: int = 4
):
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY가 .env 또는 환경변수에 없습니다.")

    db = _load_db(farm_id)

    # ✅ 최신 LangChain 방식 (invoke 사용)
    retriever = db.as_retriever(search_kwargs={"k": k})
    docs = retriever.invoke(question)

    if not docs:
        return {
            "answer": "문서에서 근거를 찾지 못했다.",
            "sources": []
        }

    # 검색된 문서 합치기
    raw_context = "\n\n".join(d.page_content for d in docs)

    # 질문에 맞는 섹션만 추출
    context = _extract_section(raw_context, question)
    print("=== DEBUG: context length ===", len(context))
    print("=== DEBUG: calling LLM ===")

    if len(context.strip()) < 30:
        return {
            "answer": "문서에서 질문과 직접 관련된 근거를 찾지 못했다.",
            "sources": []
        }

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt(role, lang)),
        (
            "human",
            "아래 문서(context)에 있는 내용만 근거로 답해라.\n"
            "추측하거나 일반 지식 사용 금지.\n\n"
            "[context]\n{context}\n\n"
            "[question]\n{question}"
        )
    ])

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        max_tokens=500,
        timeout=30
    )

    answer = llm.invoke(
        prompt.format_messages(
            context=context,
            question=question
        )
    ).content.strip()

    sources = [
        {
            "source": d.metadata.get("source", ""),
            "page": d.metadata.get("page")
        }
        for d in docs
    ]

    return {
        "answer": answer,
        "sources": sources
    }
