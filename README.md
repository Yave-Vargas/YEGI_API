# 📘 YEGI API

Academic PDF Summarization API powered by **FastAPI + Ollama**

> [!WARNING]
> This repository contains the backend API only.
> The complete application includes a separate frontend service.

**Version:** 0.2.0

**Authors:**

* Yavé Emmanuel Vargas Márquez (Backend)
* Giovanna Inosuli Campos Flores (Frontend)

**Contributors:**

* Jezreel Mejía Miranda
* Mayra Alejandra Torres Hernández
* Roberto Oswaldo Cruz Leija
* Mario Cesar Ordoñez Gutiérrez
* Erika Sánchez-Femat

---

# 🚀 Overview

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
* **Docker & Docker Compose** – Containerized deployment

---

# 📂 Project Structure

```
YEGI-API/
│
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   └── router.py
│   │
│   ├── controllers/
│   ├── services/
│   ├── core/
│   └── main.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .dockerignore
└── README.md
```

---

# ⚙️ Requirements

> [!IMPORTANT]
> If running without Docker:
>
> * Python 3.11+
> * Ollama installed
> * 8GB RAM recommended (for 3B models)

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Configuration

> [!IMPORTANT]
> Create a `.env` file in the project root.

```
FRONTEND_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
OLLAMA_HOST=http://ollama:11434
```

In production:

```
FRONTEND_ORIGINS=https://your-frontend-domain.com
```

> [!NOTE]
> CORS is restricted to the origins defined in the `.env` file.

---

# 🐳 Quick Start (Recommended)

## 1️⃣ Build & Start Services

```bash
docker compose up --build -d
```

> [!TIP]
> This will automatically start:
>
> * `yegi_api`
> * `yegi_ollama`

---

## 2️⃣ Pull LLM Model (First Time Only)

```bash
docker exec -it yegi_ollama ollama pull llama3.2:3b
```

> [!CAUTION]
> Pulling models for the first time may take several minutes depending on your internet speed and model size.

---

## 3️⃣ Access API Docs

```
http://localhost:8000/docs
```

---

# ➕ Adding More Models to Ollama

YEGI API supports any model installed in the Ollama container.

---

## 🔍 1️⃣ List Available Remote Models

You can browse models from the official Ollama library:

👉 [https://ollama.com](https://ollama.com)

---

## 📥 2️⃣ Pull a New Model (Docker)

Run inside the Ollama container:

```bash
docker exec -it yegi_ollama ollama pull mistral:7b
```

Example models:

```bash
docker exec -it yegi_ollama ollama pull llama3.2:1b
docker exec -it yegi_ollama ollama pull llama3.2:3b
docker exec -it yegi_ollama ollama pull mistral:7b
docker exec -it yegi_ollama ollama pull phi3:mini
```

---

## 🖥 3️⃣ Pull Model (Without Docker)

If running locally:

```bash
ollama pull mistral:7b
```

---

## 📋 4️⃣ Verify Installed Models

Docker:

```bash
docker exec -it yegi_ollama ollama list
```

Local:

```bash
ollama list
```

---

## ⚠️ Resource Considerations

> [!WARNING]
> Model size directly impacts RAM usage and server stability.

| Model Size | Recommended RAM |
| ---------- | --------------- |
| 1B         | 4GB             |
| 3B         | 8GB             |
| 7B         | 16GB            |
| 13B+       | 32GB+           |

---

# 🧪 Running Locally (Without Docker)

Start Ollama:

```bash
ollama serve
```

Run API:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

> [!TIP]
> Use `--reload` during development for automatic reload on code changes.

---

# 📌 API Endpoints

## 📦 GET /api/health/

Returns the API status.

---

## 📦 GET /api/models/

Returns available Ollama models.

---

## 📑 POST /api/extract/headers

Form-data:

* `archivo_pdf` (file)

---

## 🧠 POST /api/summarizer/

Form-data:

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

Example:

```bash
-F 'header_weights={"Introduction":40,"Results":60}'
```

> [!NOTE]
> Header weights are automatically normalized if they do not sum to 100.

---

# 🛡 Security & Stability

* 30MB file size limit
* Strict PDF validation
* Header weight normalization
* Automatic language verification
* Global error handler
* Restricted CORS
* No internal stack traces exposed
* Temporary file cleanup

> [!IMPORTANT]
> This version does not include authentication or rate limiting.

---

# ⚙ Performance Considerations

> [!CAUTION]
> Since this API runs local LLM models, performance depends heavily on CPU and RAM availability.

Recommended concurrency limit:

```bash
--limit-concurrency 2
```

* 3B models recommended for 8GB VPS
* For production, consider vertical scaling or GPU acceleration

---

# ⚠️ Limitations (v0.2.0)

* No authentication
* No rate limiting
* No persistent storage
* Single-node deployment
* No background job queue

> [!WARNING]
> Not production-hardened for public exposure without additional security layers.

---

# 🧠 Architecture

Layered structure:

* API Layer → HTTP handling
* Controller Layer → Business logic
* Service Layer → LLM interaction
* Core Layer → Configuration

Designed for maintainability and future scaling.

---

# 📄 License

Academic use – Internal research project.

---
