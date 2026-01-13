import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
STORAGE_DIR = os.path.join(BASE_DIR, "storage")


def _load_documents_recursive(farm_id: str):
    farm_dir = os.path.join(DATA_DIR, f"farm_{farm_id}")
    if not os.path.exists(farm_dir):
        raise RuntimeError(f"문서 폴더가 없습니다: {farm_dir}")

    docs = []
    for root, _, files in os.walk(farm_dir):
        for fn in files:
            path = os.path.join(root, fn)
            lower = fn.lower()

            if lower.endswith(".pdf"):
                docs.extend(PyPDFLoader(path).load())
            elif lower.endswith((".txt", ".md")):
                docs.extend(TextLoader(path, encoding="utf-8").load())

    if not docs:
        raise RuntimeError(f"{farm_dir} 아래에 PDF/TXT/MD 문서가 없습니다.")
    return docs


def reindex(farm_id: str):
    load_dotenv(os.path.join(BASE_DIR, ".env"))
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY가 .env에 없습니다.")

    farm_dir = os.path.join(DATA_DIR, f"farm_{farm_id}")  # ✅ 여기서 정의
    docs = _load_documents_recursive(farm_id)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    db = FAISS.from_documents(chunks, embeddings)

    out_dir = os.path.join(STORAGE_DIR, f"farm_{farm_id}")
    os.makedirs(out_dir, exist_ok=True)
    db.save_local(out_dir)

    return {
        "farmId": farm_id,
        "docs": len(docs),
        "chunks": len(chunks),
        "storage": out_dir,
        "loaded_from": farm_dir,
    }


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--farmId", default="1")
    args = ap.parse_args()

    result = reindex(args.farmId)
    print("reindex OK:", result)
