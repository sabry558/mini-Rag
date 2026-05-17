# mini-RAG

A lightweight, efficient, and robust implementation of a Retrieval-Augmented Generation (RAG) system for document-based question answering. Built with **FastAPI**, **MongoDB**, **Qdrant**, and integrating industry-leading LLMs like **OpenAI** and **Cohere**.

## Features

- **Document Processing**: Supports chunking and processing of various document types (e.g., plain text, PDFs).
- **Vector Search Engine**: High-performance semantic search using **Qdrant** for efficient context retrieval.
- **LLM Integration**: Abstracted interfaces to easily plug-and-play generation and embedding models via **OpenAI** or **Cohere**.
- **Database Management**: Stores projects, assets, and chunks reliably using **MongoDB** (Motor asynchronous driver).
- **FastAPI Backend**: Fast, intuitive, and modern REST API for seamless integration.
- **Multi-language Support**: Locale-based prompt templating architecture.

## Requirements

- Python 3.8 or later
- MongoDB
- Qdrant
- Docker & Docker Compose (optional but recommended for services)

## Installation & Environment Setup

### 1. Install Python using Miniconda

We recommend using [Miniconda](https://docs.anaconda.com/free/miniconda/index.html) to manage your Python environment.

```bash
# Create a new conda environment
$ conda create -n miniRag python=3.14

# Activate the environment
$ conda activate miniRag
```

### 2. Install Required Packages

Navigate to the source directory and install the Python dependencies:

```bash
$ cd src
$ pip install -r requirements.txt
```

### 3. Setup Environment Variables

Copy the example environment file and configure it with your API keys:

```bash
$ cp .env.example .env
```

Open the `.env` file and set the required variables:
- **API Keys:** Provide `OPENAI_API_KEY` or `COHERE_API_KEY` based on your configured backend.
- **Model Configs:** Configure `GENERATION_MODEL_ID` and `EMBEDDING_MODEL_ID` for your chosen providers.
- **Database Configs:** Setup your `MONGODB_URL`.

## Running the Services

### Start Infrastructure (Docker Compose)

The project requires databases to be running. You can quickly spin them up using Docker:

```bash
$ cd docker
$ cp .env.example .env
# Edit the .env file with your database credentials
$ docker compose up -d
```

### Run the FastAPI Server

Navigate to the `src` directory and start the ASGI web server using Uvicorn:

```bash
$ cd src
$ uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

The API documentation (Swagger UI) will be automatically available at `http://127.0.0.1:5000/docs`.

---
*(Optional)* Setup your command line for better readability:
```bash
$ export PS1="\[\033[01;32m\]\u@\h:\w\n\[\033[00m\]\$ "
```