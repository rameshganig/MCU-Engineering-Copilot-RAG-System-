import streamlit as st
from uuid import uuid4
import tempfile

from rag import (
    initialize_components,
    process_urls,
    generate_answer,
    vector_store
)

from langchain_community.document_loaders import PyPDFLoader, UnstructuredURLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ======================
# UI CONFIG
# ======================
st.set_page_config(page_title="MCU Engineering Copilot", layout="wide")

st.title("⚡ MCU Engineering Copilot (RAG System)")
st.caption("Hardware • Firmware • Test Engineering Assistant")

# ======================
# INIT
# ======================
initialize_components()


# ======================
# MODE SELECTION
# ======================
mode = st.selectbox(
    "Select Engineering Mode",
    ["hardware", "programming", "test"],
    index=1
)


# ======================
# SIDEBAR - INGESTION
# ======================
st.sidebar.header("📥 Knowledge Base Builder")

uploaded_files = st.sidebar.file_uploader(
    "Upload MCU PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

url_input = st.sidebar.text_area(
    "Add Datasheet / Reference URLs (one per line)"
)

if st.sidebar.button("🚀 Build Knowledge Base"):

    all_docs = []

    # ---- PDFs ----
    if uploaded_files:
        for file in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(file.read())
                loader = PyPDFLoader(tmp.name)
                docs = loader.load()
                all_docs.extend(docs)

    # ---- URLs ----
    if url_input.strip():
        urls = [u.strip() for u in url_input.split("\n") if u.strip()]
        loader = UnstructuredURLLoader(urls=urls, mode="elements")
        docs = loader.load()
        all_docs.extend(docs)

    if not all_docs:
        st.warning("No data provided!")
    else:
        st.info("Chunking documents...")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200,
            chunk_overlap=200,
            separators=["\n\n", "\n", "Table", "Figure", ".", " "]
        )

        chunks = splitter.split_documents(all_docs)

        st.info(f"Indexing {len(chunks)} chunks...")

        ids = [str(uuid4()) for _ in range(len(chunks))]
        vector_store.add_documents(chunks, ids=ids)

        st.success("Knowledge base updated ✔")


# ======================
# MAIN CHAT UI
# ======================
st.header("💬 Ask MCU Engineering Questions")

query = st.text_input(
    "Ask something like:",
    "Explain GPIO configuration for output mode"
)

col1, col2 = st.columns([1, 2])

with col1:
    ask_btn = st.button("Ask")

if ask_btn:
    if not query:
        st.warning("Please enter a question")
    else:
        answer, sources = generate_answer(query, mode=mode)

        st.subheader("🧠 Answer")
        st.write(answer)

        st.subheader("📚 Sources")
        for s in sources:
            st.write("•", s)


# ======================
# TEST CASE GENERATOR (SMART MODE)
# ======================
st.divider()
st.header("🧪 Engineering Test Case Generator")

test_query = st.text_input(
    "Generate test cases for:",
    "GPIO output configuration"
)

if st.button("Generate Test Plan"):
    if test_query:
        answer, sources = generate_answer(test_query, mode="test")

        st.subheader("🧪 Test Plan")
        st.write(answer)

        st.subheader("📚 Sources")
        for s in sources:
            st.write("•", s)