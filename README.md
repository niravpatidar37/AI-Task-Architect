<<<<<<< HEAD
# 🤖 AI Task Architect: NestJS + FastAPI Workflow Generator

### Generate valid n8n workflow JSON from natural language using a robust microservice architecture.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![NestJS](https://img.shields.io/badge/NestJS-E0234E?style=for-the-badge&logo=nestjs&logoColor=white)](https://nestjs.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/)

## ✨ Project Overview

The **AI Task Architect** is a demonstration of a **structured AI application** using a modern, scalable, dual-backend architecture. It functions as an **AI Agent** that takes a user's natural language request (e.g., "Monitor my email for new sales leads and log them in a Google Sheet") and automatically generates the corresponding, executable **n8n workflow JSON**.

This project showcases clean separation of concerns and robust API communication between two major backend frameworks:

| Component | Technology | Role |
| :--- | :--- | :--- |
| **API Gateway** | **NestJS (TypeScript)** | Handles client requests, input validation (`class-validator`), environment variable management, and detailed error mapping from the AI Engine. |
| **AI Engine** | **FastAPI (Python)** | Dedicated service for AI computation, hosting the OpenAI function calling logic, prompt engineering, JSON validation, and business logic. |

## 📐 System Architecture

The application follows a clean **API Gateway pattern** to ensure the core AI logic is decoupled and scalable.

1.  **Frontend (HTML/JS):** Sends the user prompt to the NestJS Gateway.
2.  **NestJS Gateway (Port 3000):** Validates the request (DTO), looks up the FastAPI URL via `ConfigService`, and forwards the request via `axios`.
3.  **FastAPI AI Engine (Port 8000):** Executes the Python `generate_workflow` function, calls the **GPT-4o** model using **Function Calling** to enforce JSON output, validates the n8n structure, and returns the final JSON.
4.  **NestJS Gateway:** Catches any specific errors (like connection timeout or internal AI errors) and maps them to clean, descriptive HTTP responses for the client.

## 🚀 Getting Started

Follow these steps to get both services running locally.

### Prerequisites

* Node.js (v18+) and npm
* Python (v3.10+) and pip
* An **OpenAI API Key**
=======
# AI-Task-Architect
Generates structured n8n workflow JSON from text prompts using GPT-4o, orchestrated via a NestJS Gateway and FastAPI AI Engine.
>>>>>>> 2ec4cf27ef1741ce975be1de9f981214194b3b2f
