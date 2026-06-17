"""
database.py
-----------
ChromaDB setup and context fetchers.
chroma_db/ folder must be committed to the HuggingFace Space repo.
"""

import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# chroma_db/ must exist in the repo root
_DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db         = Chroma(persist_directory=_DB_PATH, embedding_function=embeddings)
all_data   = db.get()
companies  = sorted(set(m.get("company", "Unknown") for m in all_data["metadatas"]))


def detect_company_from_query(query: str, selected: str) -> str:
    if selected != "All":
        return selected
    try:
        docs = db.similarity_search(query, k=1)
        if docs:
            return docs[0].metadata.get("company", "All")
    except Exception:
        pass
    return "All"


def get_policy_context(company: str, query: str) -> str:
    if company == "All":
        docs = db.as_retriever(
            search_kwargs={"k": 1, "filter": {"doc_type": "policy"}}
        ).invoke(query)
        return "\n\n".join(d.page_content for d in docs)
    result = db.get(
        where={"$and": [{"company": company}, {"doc_type": "policy"}]},
        include=["documents"],
    )
    return "\n\n".join(result.get("documents", []))


def get_process_context(company: str) -> str:
    if company == "All":
        result = db.get(where={"doc_type": "process"}, include=["documents"])
    else:
        result = db.get(
            where={"$and": [{"company": company}, {"doc_type": "process"}]},
            include=["documents"],
        )
    return "\n\n".join(result.get("documents", []))


def get_combined_context(company: str, query: str) -> str:
    return (get_policy_context(company, query) + "\n\n" + get_process_context(company)).strip()


def get_doc_category(company: str, query: str) -> str:
    f    = None if company == "All" else {"company": company}
    kw   = {"k": 1}
    if f: kw["filter"] = f
    docs = db.as_retriever(search_kwargs=kw).invoke(query)
    return docs[0].metadata.get("category", "") if docs else ""
