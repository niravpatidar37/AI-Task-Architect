# 🤖 AI Task Architect: NestJS + FastAPI Workflow Generator

Generate valid **n8n workflow JSON** from natural language using a scalable microservice architecture.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)  
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![NestJS](https://img.shields.io/badge/NestJS-E0234E?style=for-the-badge&logo=nestjs&logoColor=white)](https://nestjs.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/)
[![n8n](https://img.shields.io/badge/n8n-FE8040?style=for-the-badge&logo=n8n&logoColor=white)](https://n8n.io/)


---

## ✨ Project Overview

The **AI Task Architect** is a dual-backend AI application that takes natural language prompts like:

> _"Fetch Tesla stock price every morning and post to Slack."_

and generates a valid, executable **n8n workflow JSON** using the OpenAI API.

### 🔧 Core Features

- ✅ FastAPI-powered AI backend with OpenAI function calling
- ✅ NestJS Gateway with typed DTOs and error handling
- ✅ Generates clean, importable n8n workflows (`name`, `nodes`, `connections`)
- ✅ SQLite database integration for workflow history and reuse
- ✅ JSON structure repair, enrichment, and validation

---

## 🧱 Architecture Overview

| Layer | Tech Stack | Role |
|-------|------------|------|
| **Frontend** | HTML/JS or REST client | Sends natural prompts |
| **API Gateway** | NestJS (TypeScript) | Receives prompts, validates input, forwards to FastAPI |
| **AI Engine** | FastAPI (Python) | Generates structured workflows using GPT-4o |
| **Database** | SQLite via SQLAlchemy | Stores generated workflows persistently |

---

---

## 🚀 Getting Started

### 1. 🧠 Clone the repo

```bash
git clone https://github.com/niravpatidar37/ai-task-architect.git
cd ai-task-architect

cd llm_agent
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

pip install -r requirements.txt
cp .env.example .env      # Add your OpenAI API Key
uvicorn main:app --reload

cd backend
npm install
npm run start:dev

# FastAPI .env
OPENAI_API_KEY=your-openai-api-key-here

POST /generate

{
  "prompt": "Create a workflow that triggers every morning, fetches Tesla's stock price, and posts it to Slack."
}

Response 

{
  "name": "Tesla Stock Summary",
  "nodes": [...],
  "connections": {...}
}
