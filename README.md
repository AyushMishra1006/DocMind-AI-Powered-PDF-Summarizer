DocMind is an intelligent PDF Q&A assistant built using Large Language Models (LLMs) and vector-based semantic search.
It allows users to upload any PDF document, automatically extract its contents, create embeddings for efficient retrieval, and then ask natural language questions to get accurate, context-aware answers.

This project integrates Google Gemini 2.5 Flash with LangChain, Chroma, and HuggingFace sentence embeddings, providing a seamless, interactive document understanding experience — all inside a beautiful Streamlit web app.

<img width="1908" height="922" alt="image" src="https://github.com/user-attachments/assets/65113b02-9880-4aa0-9d2b-17d922cc4eec" />





🚀 Key Features

📄 PDF Upload & Extraction – Instantly extract clean text from uploaded PDFs.

🧩 Smart Text Chunking – Splits long text into optimized overlapping chunks for better retrieval accuracy.

🧠 Embeddings Generation – Uses sentence-transformers/all-MiniLM-L6-v2 to convert text into vector embeddings stored locally using Chroma DB.

🔍 Context Retrieval – Fetches the most relevant text segments from the document using semantic similarity search.

💬 Question Answering – Employs Google Gemini 2.5 Flash (Generative AI) to produce precise, well-structured answers based on retrieved document chunks.

🎨 Dark Themed UI – A sleek, modern interface built with Streamlit, featuring dynamic chat display and animated loading elements.

💾 Persistent Storage – Vector embeddings stored in chroma_db_policy allow reuse during the session.

🧩 Tech Stack
Component	Technology Used
Frontend	Streamlit (custom CSS styling for dark mode UI)
Document Processing	PyMuPDF (fitz)
Embeddings	HuggingFace sentence-transformers/all-MiniLM-L6-v2
Vector Database	Chroma
LLM (API)	Google Gemini 2.5 Flash
Frameworks & Libraries	LangChain, LangChain Community Modules
⚙️ How It Works (Pipeline)

Upload PDF → Extracts and cleans the text using PyMuPDF.

Text Chunking → Breaks text into overlapping segments using RecursiveCharacterTextSplitter.

Embedding Creation → Converts each chunk into high-dimensional vectors using HuggingFace embeddings.

Vector Store → Stores embeddings in a ChromaDB collection.

Live Demo - [CLICK HERE](https://docmind-ai-powered-pdf-summarizer-rk3wzyes6jbbuoamuolba7.streamlit.app/)

Query Processing → Retrieves top k similar chunks relevant to the user’s question.

Answer Generation → Combines retrieved content and passes it to Google Gemini 2.5 Flash, which analyzes and generates the final response.
