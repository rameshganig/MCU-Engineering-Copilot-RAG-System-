from uuid import uuid4
from dotenv import load_dotenv
from pathlib import Path
import requests

from prompt import (
    HARDWARE_PROMPT,
    PROGRAMMING_PROMPT,
    TEST_PROMPT
)

from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from langchain_groq import ChatGroq
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader

load_dotenv()

# ======================
# CONFIG
# ======================
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

VECTORSTORE_DIR = Path(__file__).parent / "resources/vectorstore_mcu"
COLLECTION_NAME = "mcu_datasheet"

llm = None
vector_store = None


# ======================
# INIT COMPONENTS
# ======================
def initialize_components():
    global llm, vector_store

    if llm is None:
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.0,
            max_tokens=900
        )

    if vector_store is None:
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"trust_remote_code": True}
        )

        vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=str(VECTORSTORE_DIR)
        )


# ======================
# PDF LOADER
# ======================
def load_pdf_from_url(url):
    response = requests.get(url)

    file_path = f"temp_{uuid4()}.pdf"

    with open(file_path, "wb") as f:
        f.write(response.content)

    loader = PyPDFLoader(file_path)
    return loader.load()


# ======================
# INGESTION PIPELINE
# ======================
def process_urls(urls):
    global vector_store

    yield "Initializing system..."
    initialize_components()

    yield "Resetting vector DB..."

    if vector_store is not None:
        vector_store.delete_collection()
        vector_store = None

    initialize_components()

    all_docs = []

    for url in urls:

        if url.endswith(".pdf"):
            yield f"Loading PDF: {url}"
            docs = load_pdf_from_url(url)

        else:
            yield f"Loading web page: {url}"
            loader = UnstructuredURLLoader(
                urls=[url],
                mode="elements"
            )
            docs = loader.load()

        all_docs.extend(docs)

    yield "Chunking documents..."

    splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", "Table", "Figure", ".", " "],
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    docs = splitter.split_documents(all_docs)

    yield f"Indexing {len(docs)} chunks..."

    ids = [str(uuid4()) for _ in range(len(docs))]
    vector_store.add_documents(docs, ids=ids)

    yield "Datasheet ingestion complete ✔"


# ======================
# PROMPT SELECTOR
# ======================
def select_prompt(mode: str):
    if mode == "hardware":
        return HARDWARE_PROMPT
    elif mode == "programming":
        return PROGRAMMING_PROMPT
    elif mode == "test":
        return TEST_PROMPT
    else:
        return PROGRAMMING_PROMPT  # default fallback


# ======================
# RAG PIPELINE (LCEL)
# ======================
def generate_answer(query, mode="programming"):

    if vector_store is None:
        raise RuntimeError("Vector DB not initialized")

    retriever = vector_store.as_retriever(
        search_kwargs={"k": 6}
    )

    prompt = select_prompt(mode)

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {
            "summaries": retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    answer = chain.invoke(query)

    docs = retriever.invoke(query)

    sources = list(set(
        doc.metadata.get("source", "unknown") for doc in docs
    ))

    return answer, sources


# ======================
# MAIN TEST
# ======================
if __name__ == "__main__":

    urls = [
        "https://www.nxp.com/docs/en/data-sheet/MPC5775E.pdf",
        "https://www.nxp.com/products/MPC5775B-E",
        "https://www.nxp.com/docs/en/fact-sheet/MPC5775B-E-EVB_FS.pdf"
    ]

    for step in process_urls(urls):
        print(step)

    q = "Explain GPIO configuration for output mode and how to test it in hardware"

    # Change mode here:
    answer, sources = generate_answer(q, mode="hardware")

    print("\nANSWER:\n", answer)
    print("\nSOURCES:\n", sources)