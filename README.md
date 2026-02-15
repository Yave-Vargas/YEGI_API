# 📘 YEGI API

Academic PDF Summarization API powered by **FastAPI + Ollama**

Note: This repository is for APIs only, but the complete application has a backend and a frontend.

**Version:** 0.2.0
**Authors:** Yavé Emmanuel Vargas Márquez   (Backend)
             Giovanna Inosuli Campos Flores (Frontend)
---

# Overview

YEGI API allows users to:

* 📄 Upload academic PDF files (max 30MB)
* 🧩 Extract structured section headers
* 🧠 Generate scientific summaries using local LLMs (Ollama)
* 🎯 Apply weighted emphasis to document sections
* ⚙ Control inference parameters (temperature, top_p, etc.)

Designed for research environments and academic text processing.

---

# 🧱 Tech Stack

* **FastAPI** – Web framework
* **Ollama** – Local LLM runtime
* **PyMuPDF** – PDF parsing
* **Langdetect** – Language detection
* **python-dotenv** – Environment configuration
* **Uvicorn** – ASGI server

---

# 📂 Project Structure

```
YEGI-API/
│
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── extract.py
│   │   │   ├── models.py
│   │   │   └── summarizer.py
│   │   └── router.py
│   │
│   ├── controllers/
│   │   ├── llm_controller.py
│   │   ├── extract_headers.py
│   │   ├── pdf_extractor.py
│   │   └── text_preprocessor.py
│   │
│   ├── services/
│   │   └── summarization_service.py
│   │
│   ├── core/
│   │   └── config.py
│   │
│   └── main.py
│
├── requirements.txt
├── .env
└── README.md
```

---

# ⚙️ Requirements

* Python 3.11+
* Ollama installed
* At least 8GB RAM recommended (for 3B models)

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Configuration

Create a `.env` file in the project root:

```
FRONTEND_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

In production:

```
FRONTEND_ORIGINS=https://your-frontend-domain.com
```

CORS is restricted to these origins.

---

# 🧪 Running Locally

Start Ollama:

```bash
ollama serve
```

Run the API:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --limit-concurrency 2
```

Access interactive docs:

```
http://localhost:8000/docs
```

---

# 📌 API Endpoints

## 📦 Get Available Models

```
GET /api/models/
```

Returns available Ollama models.

---

## 📑 Extract PDF Headers

```
POST /api/extract/headers
```

**Form-data:**

* `archivo_pdf` (file)

Response:

```json
{
  "total": 6,
  "headers": ["Introduction", "Methods", "Results"]
}
```

---

## 🧠 Summarize PDF

```
POST /api/summarizer/
```

**Form-data:**

| Field          | Type        |
| -------------- | ----------- |
| archivo_pdf    | file        |
| model          | string      |
| temperature    | float       |
| top_p          | float       |
| repeat_penalty | float       |
| repeat_last_n  | int         |
| num_predict    | int         |
| language       | string      |
| header_weights | JSON string |

---

# 🛡 Security & Stability Features

* ✅ 30MB file size limit
* ✅ Strict PDF validation
* ✅ Header weight normalization
* ✅ Automatic language detection
* ✅ Global error handler
* ✅ Restricted CORS
* ✅ No internal stack trace exposure
* ✅ Temporary file cleanup

---

# ⚙ Performance Notes

Since the API runs local LLM models:

* Performance depends heavily on RAM and CPU.
* Recommended: limit concurrency using:

```bash
--limit-concurrency 2
```

* 3B models recommended for 8GB VPS environments.

---

# 🐳 Docker (Optional)

Build image:

```bash
docker build -t yegi-api .
```

Run container:

```bash
docker run -p 8000:8000 --env-file .env yegi-api
```

---

# ⚠️ Limitations (v0.2.0)

* No authentication
* No rate limiting
* No structured logging yet
* Designed for single-node deployment

---

# 📄 License

Academic use – Internal research project.

---

# 🧠 Architecture Notes

This project follows a layered structure:

* API Layer → Request handling
* Controller Layer → Business logic orchestration
* Service Layer → Model interaction
* Core Layer → Configuration

Designed for maintainability and future scaling.

---
