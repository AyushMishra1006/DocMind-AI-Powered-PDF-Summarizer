# 🤖 DocMind – AI-Powered Document Intelligence Assistant

DocMind is a production-ready **AI document intelligence system** that allows users to upload PDFs or images and interact with them through natural language.
It combines **OCR, semantic search, and Gemini LLM reasoning** to deliver clean, human-readable answers from messy, scanned, or structured documents.

Built with **Streamlit + Gemini + LangChain**, DocMind is designed to be fast, accurate, and cloud-safe.

---

## ✨ Key Features

### 📄 Smart Document Ingestion

* Supports **PDF, PNG, JPG, JPEG**
* Automatically detects:

  * native text PDFs
  * scanned PDFs
  * mixed PDFs
* Falls back to **multi-pass OCR** when required

### 🔍 Advanced OCR Engine

* 3-pass OCR pipeline:

  * raw grayscale
  * adaptive thresholding
  * contrast enhancement
* Line de-duplication & noise cleaning
* Optimized for real-world scanned documents

### 🧠 Semantic Understanding (RAG)

* Text chunking with overlap for context continuity
* **HuggingFace MiniLM embeddings**
* **In-memory Chroma vector store** (cloud safe)
* Top-k semantic retrieval for every question

### 💬 Intelligent Q&A

* Powered by **Gemini 2.5 Flash**
* OCR-aware prompting (reconstructs broken text)
* Context merging across document sections
* No hallucinations — answers are grounded in document text

### 💡 Smart Question Suggestions

* Automatically generates relevant questions after upload
* Helps users explore documents faster
* One-click question asking

### 🎨 Modern Chat UI

* ChatGPT-style interface
* Fixed input bar
* Thinking indicators
* Smooth animations & dark theme
* Responsive layout

---

## 🏗 Architecture Overview

```
Upload File
   ↓
Text Extraction (pdfplumber)
   ↓
OCR Fallback (OpenCV + Tesseract)
   ↓
Text Cleaning & Chunking
   ↓
Embeddings (MiniLM)
   ↓
In-Memory Vector DB (Chroma)
   ↓
Retriever (Top-K)
   ↓
Gemini LLM
   ↓
Final Answer
```

---

## 🛠 Tech Stack

| Layer            | Technology                     |
| ---------------- | ------------------------------ |
| UI               | Streamlit                      |
| OCR              | OpenCV, Tesseract              |
| PDF Parsing      | pdfplumber                     |
| Embeddings       | sentence-transformers (MiniLM) |
| Vector DB        | Chroma (in-memory)             |
| LLM              | Google Gemini 2.5 Flash        |
| RAG              | LangChain                      |
| Image Processing | Pillow, NumPy                  |
| Deployment       | Streamlit Cloud / Local        |

---

## 🚀 Getting Started

### 1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/docmind.git
cd docmind
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Set environment variable

```bash
export GEMINI_API_KEY="your_api_key_here"
```

*(On Windows use `set` instead of `export`)*

### 4️⃣ Run the app

```bash
streamlit run main.py
```

---

## 📁 Project Structure

```
docmind/
│
├── main.py
├── pdf_utils.py
├── ocr_utils.py
├── embeddings_utils.py
├── llm_utils.py
├── question_suggestions.py
├── text_chunker.py
├── requirements.txt
└── README.md
```

---

## 🧪 How It Works (In Short)

1. User uploads a document
2. DocMind extracts text (or runs OCR)
3. Text is chunked and embedded
4. Embeddings are stored in-memory
5. User asks a question (or clicks suggestion)
6. Relevant chunks are retrieved
7. Gemini generates a clean answer
8. Chat UI displays the response

---

## 🔐 Privacy & Security

* No documents are written to disk
* No embeddings are persisted
* Everything runs in memory
* Safe for sensitive documents

---

## ⚡ Performance

* Fast ingestion for native PDFs
* Optimized OCR pipeline
* Lightweight embeddings model
* Low-latency Gemini Flash responses

---

## 🧩 Future Improvements

* Streaming responses
* Multi-document chat
* Highlight source citations
* Table extraction
* Export answers to PDF
* User authentication
* Async OCR pipeline

---

## 👨‍💻 Author

**Ayush Mishra**
B.Tech CSE (Data Science)
Built with ❤️ and too much coffee ☕

---

## ⭐ If you like this project

Give it a star ⭐ — it helps a lot!


