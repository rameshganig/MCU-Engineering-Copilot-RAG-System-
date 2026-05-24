# ⚡ MCU Engineering Copilot (RAG System)

An AI-powered Retrieval-Augmented Generation (RAG) system designed for embedded systems engineers working with microcontrollers.  
It helps in hardware design, firmware development, and test case generation using MCU datasheets and technical references.

---

## 🚀 Features

### 🧠 Multi-Role Engineering Assistant
Switch between engineering modes:

- **Hardware Mode** → Circuit design, pin configuration, electrical interfacing  
- **Programming Mode** → Firmware logic, SDK usage, communication protocols  
- **Test Mode** → Validation strategies, hardware testing, debugging steps  

---

### 📄 Knowledge Base (RAG)
- Upload MCU datasheets (PDF)
- Add reference URLs (NXP, ST, etc.)
- Automatic chunking + embedding
- Vector storage using **ChromaDB**

---

### 💬 Intelligent Q&A
Ask questions like:

- How to configure GPIO output mode?
- How to initialize CAN communication?
- How to test SPI interface in hardware?

---

### 🧪 Test Case Generator
Automatically generates:

- Hardware validation steps
- Debugging strategies
- Expected signal behavior
- Test equipment recommendations

---

## 🏗️ Architecture
PDFs / URLs
↓
Document Loader (PyPDF / UnstructuredURLLoader)
↓
Text Splitter (RecursiveCharacterTextSplitter)
↓
Embeddings (HuggingFace MiniLM)
↓
Vector DB (Chroma)
↓
Retriever
↓
LLM (Groq - LLaMA 3)
↓
Engineering Prompt Engine
↓
Hardware / Firmware / Test Output


---

## 🧰 Tech Stack

- Python
- LangChain
- Groq LLM (LLaMA 3)
- ChromaDB
- HuggingFace Embeddings
- PyPDF / Unstructured Loader
- Streamlit

---

## 📦 Installation

### Clone repository
```bash
git clone https://github.com/your-username/mcu-engineering-copilot.git
cd mcu-engineering-copilot

conda create -n mcu_rag python=3.10
conda activate mcu_rag

GROQ_API_KEY=your_api_key_here
streamlit run app.py
```
---

# 📥 How to Use

### 1. Build Knowledge Base
* Upload MCU datasheets (PDF)
* Or paste reference URLs
* Click **Build Knowledge Base**

### 2. Select Mode
Choose your desired focus area:
* **Hardware**
* **Programming**
* **Test**

### 3. Ask Questions
* *Example:* "Explain GPIO configuration for output mode and how to test it in hardware."


## 🧪 Example Outputs

### 🔌 Hardware Mode
* Pin configuration
* Electrical constraints
* Circuit considerations

### 💻 Programming Mode
* SDK initialization
* Register-level setup
* Communication protocol usage

### 🔬 Test Mode
* Validation steps
* Debugging strategy
* Measurement tools

---

## 📌 Future Improvements
* 🤖 Auto mode detection (AI router)
* ⚙️ Firmware code generator (C output)
* 📄 PDF export for test plans
* 📊 Multi-datasheet comparison
* 🧠 Chat memory support

---

## 👨‍💻 Author

This project demonstrates how **Retrieval-Augmented Generation (RAG)** accelerates complex technical workflows. 

Development cycles often require reading massive volumes of datasheets, manuals, and architectural specifications. Manual information extraction is slow and hurts engineering velocity. 

This tool solves that bottleneck through a structured machine-learning pipeline:

* 🗄️ **Vector Database:** Ingests scattered text, PDFs, and web URLs into an organized vector store [3].
* 🔍 **Similarity Search:** Locates exact technical contexts within seconds [3].
* 🤖 **LLM Synthesis:** Generates precise technical answers tailored to your engineering domain [3].

By transforming static documentation into an active knowledge partner, this RAG implementation drastically cuts down research time, eliminates manual parsing, and maximizes engineering productivity.
