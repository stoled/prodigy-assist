# AI Knowledge Assistant Platform

## Цель проекта

Практический проект для изучения и демонстрации навыков, соответствующих вакансии Backend Developer (AI Platform).

Суть продукта: **Telegram-бот «всезнайка»** — отвечает на любые вопросы, подкрепляя ответы актуальными данными из Wikipedia. Пользователь задаёт вопрос в свободной форме, система ищет релевантные статьи, строит контекст и возвращает точный, структурированный ответ.

Стек:

- Node.js + TypeScript (Nest.js)
- Python (FastAPI)
- PostgreSQL + pgvector
- Prisma
- REST API
- Kafka
- LangChain
- LangGraph
- MCP
- RAG
- Embeddings
- Prompt Engineering
- Context Management
- Object Storage
- AI Agents
- Docker

---

# Архитектура

```text
Telegram
   ↓
Telegram Bot (Node.js)
   ↓
Backend API (Node.js)
   ↓
Kafka
   ↓
AI Service (Python)
        ↓
    LangGraph
        ↓
     MCP Tools
     /        \
  RAG        Wikipedia Fetcher
   |                |
pgvector     Wikipedia API / HTML
        ↓
   PostgreSQL
        ↓
     MinIO (images)
```

---

# Сервисы

## 1. Telegram Gateway

Назначение:

- получение сообщений от пользователей
- отправка готовых ответов

Стек:

- Node.js
- TypeScript
- Telegraf

---

## 2. Backend API

Назначение:

- управление пользователями
- история диалогов
- управление сохранёнными документами знаний
- постановка задач в очередь

Стек:

- Node.js
- TypeScript
- Nest.js
- Prisma
- PostgreSQL

Функции:

- REST API
- DTO
- Validation (class-validator)
- Error Handling
- OpenAPI (Swagger)

Маршруты:

```http
POST   /messages
GET    /messages/:userId
DELETE /messages/:userId

POST   /knowledge
GET    /knowledge/search?q=
DELETE /knowledge/:id

GET    /health
```

---

## 3. AI Service

Назначение:

- оркестрация агентов
- LangGraph workflow
- RAG поверх сохранённых статей
- вызов MCP-инструментов

Стек:

- Python 3.12+
- FastAPI
- Pydantic v2
- LangChain
- LangGraph
- OpenAI SDK

Обязанности:

- orchestration
- prompt engineering
- context management
- structured output
- tool execution

---

## 4. Wikipedia Fetcher

Назначение:

Получение текстового контента из Wikipedia для последующей индексации в RAG.

Стек:

- Python
- `wikipedia-api` (pip)
- BeautifulSoup (fallback — парсинг HTML при обходе ограничений)

Сценарии использования:

```text
Пользователь спрашивает: «Расскажи о квантовой запутанности»
  ↓
Wikipedia Fetcher ищет статью «Quantum entanglement»
  ↓
Извлекает разделы: Summary, History, Applications
  ↓
Передаёт в Embedding Pipeline
  ↓
Результат доступен для RAG
```

Пример результата:

```json
{
  "title": "Quantum entanglement",
  "url": "https://en.wikipedia.org/wiki/Quantum_entanglement",
  "summary": "...",
  "sections": [
    { "title": "History", "content": "..." },
    { "title": "Applications", "content": "..." }
  ],
  "lang": "en"
}
```

Поддерживать мультиязычность: ru / en (определять язык запроса, тянуть статью на нужном языке).

---

## 5. Embedding Pipeline

Назначение:

Индексация статей и документов.

Стек:

- Python
- OpenAI Embeddings (`text-embedding-3-small`)

Поток:

```text
Статья Wikipedia / сохранённый документ
   ↓
Chunking (по разделам или по токенам)
   ↓
OpenAI Embeddings
   ↓
pgvector (таблица Document)
```

---

## 6. Worker Service

Назначение:

Асинхронная обработка задач из очереди.

Стек:

- Python 3.12+
- FastAPI (health endpoint)
- Pydantic v2

Задачи:

- генерация ответов (вызов AI Service)
- индексация новых статей Wikipedia
- сохранение изображений в MinIO
- генерация изображений (опционально)

---

# Очереди

## Этап 1

BullMQ (простая реализация, Redis-backed)

## Этап 2

Kafka

Изучить:

- Producer
- Consumer
- Consumer Group
- Partition
- Offset
- Retry
- Dead Letter Queue

Топики:

```text
messages.incoming     — новые сообщения от пользователей
knowledge.index       — задачи индексации статей
responses.outgoing    — готовые ответы для отправки в Telegram
```

---

# PostgreSQL

Использовать:

- PostgreSQL
- Prisma
- pgvector

## User

```prisma
model User {
  id         String   @id @default(uuid())
  telegramId String   @unique
  createdAt  DateTime @default(now())

  messages   Message[]
}
```

## Message

```prisma
model Message {
  id        String   @id @default(uuid())
  role      String   // "user" | "assistant"
  content   String

  userId    String
  user      User     @relation(fields: [userId], references: [id])

  createdAt DateTime @default(now())
}
```

## Document

```prisma
model Document {
  id        String   @id @default(uuid())
  title     String
  content   String
  source    String   // URL статьи Wikipedia или "manual"
  lang      String   @default("en")
  embedding Unsupported("vector(1536)")

  createdAt DateTime @default(now())
}
```

---

# MCP Server

Реализован на Python, является частью AI Service.

Реализовать полноценный MCP Server с инструментами:

## searchKnowledge

Семантический поиск по RAG (pgvector).

```python
search_knowledge(query: str, top_k: int = 5)
```

## fetchWikipedia

Получить и сохранить статью из Wikipedia.

```python
fetch_wikipedia(topic: str, lang: str = "en")  # lang: "en" | "ru"
```

## generateImage

Генерация изображения по описанию (DALL-E).

```python
generate_image(prompt: str)
```

## getCurrentTime

Получение текущего времени и даты (нужно для контекста агента).

## saveKnowledge

Ручное сохранение произвольного документа.

```python
save_knowledge(title: str, content: str, source: str = "manual")
```

---

# RAG

## Цель

Подмешивание актуального контекста из базы знаний (Wikipedia + сохранённые документы) в промпт LLM.

Формула:

```text
RAG = Vector Search + Context Injection + LLM
```

Поток:

```text
User Query
    ↓
Embedding запроса
    ↓
Vector Search (pgvector, cosine similarity)
    ↓
Top-K релевантных чанков
    ↓
Context Injection в промпт
    ↓
LLM → ответ
```

Стратегия чанкинга:

- Разбивать статьи по разделам (H2/H3)
- Максимальный размер чанка: 512 токенов
- Overlap: 50 токенов

---

# LangGraph

State:

```python
from typing import TypedDict

class AgentState(TypedDict):
    user_message: str
    retrieved_docs: list[str]
    wikipedia_fetched: bool
    tool_results: list
    final_answer: str | None
```

Workflow:

```text
Input
  ↓
Router           ← определяет: нужен ли Wikipedia fetch или достаточно RAG
  ↓
RAG Search
  ↓
[если недостаточно контекста] → Wikipedia Fetch → Re-index → RAG Search
  ↓
Tool Selection
  ↓
LLM
  ↓
Validator        ← проверяет полноту и наличие источников
  ↓
Output
```

Validator Loop:

```text
LLM
 ↓
Validation (есть ли источник? достаточно ли контекста?)
 ↓
Retry (если нет — дополнительный Wikipedia fetch)
```

Причины использования LangGraph:

- state management
- branching (RAG vs. Wikipedia fetch)
- retries
- agent workflows

---

# Prompt Management

Структура:

```text
prompts/
  system.txt       — системный промпт агента-всезнайки
  router.txt       — промпт для определения нужного инструмента
  retriever.txt    — промпт для формирования контекста из документов
  validator.txt    — промпт для проверки качества ответа
```

Правила системного промпта:

- Всегда указывать источник (ссылку на Wikipedia)
- Отвечать на языке пользователя
- Если информации нет — честно сообщать об этом

---

# Observability

Node.js:

- Pino (structured logging)

Python:

- Loguru

Добавить:

- structured logging
- request_id (сквозной между сервисами)
- tracing (опционально: OpenTelemetry)

---

# Docker

Контейнеры:

```text
postgres        — основная БД + pgvector
redis           — для BullMQ (этап 1)
kafka           — брокер сообщений (этап 2)
minio           — хранение изображений
backend         — Node.js API
ai-service      — Python FastAPI
telegram-bot    — Telegraf бот
```

`docker-compose.yml` — dev-среда  
`docker-compose.prod.yml` — prod-среда (multi-stage builds)

---

# Что изучить по ходу проекта

## JavaScript / TypeScript

1. Event Loop
2. Promise.all / Promise.allSettled
3. Generics
4. Type Guards
5. Async/Await

## Backend

6. Express
7. REST API Design
8. OpenAPI / Swagger
9. Idempotency
10. Retry Logic

## PostgreSQL

11. JOIN, GROUP BY, HAVING
12. Индексы (B-tree, GIN, HNSW для pgvector)
13. EXPLAIN ANALYZE
14. Транзакции

## Python

15. FastAPI
16. Pydantic v2
17. wikipedia-api, BeautifulSoup

## AI

18. OpenAI API (Chat + Embeddings + DALL-E)
19. MCP
20. RAG
21. Embeddings + Vector Search
22. LangChain (Chains, Tools, Memory)
23. LangGraph (State, Branching, Retries)
24. Prompt Engineering
25. Context Management
26. Chunking Strategies

## Infrastructure

27. Kafka (Producer, Consumer, DLQ)
28. Worker Pattern / Queue Pattern
29. Docker + multi-stage builds
30. MinIO / S3

## Architecture

31. Microservices
32. AI Agents
33. Structured Output
34. Tool Calling
35. Circuit Breaker
36. Dead Letter Queue

---

# Результат

Telegram-бот, который:

- отвечает на вопросы любой сложности
- автоматически находит и индексирует статьи Wikipedia
- хранит базу знаний и умеет по ней искать
- цитирует источники в каждом ответе
- работает на русском и английском языке

После завершения — практические навыки по большинству требований вакансии:

- Backend на Node.js/TypeScript
- Python AI Layer (FastAPI + LangChain + LangGraph)
- PostgreSQL + pgvector (RAG)
- REST API + Kafka
- MCP + Tool Calling
- Prompt Engineering + Context Management
- Object Storage (MinIO)
- AI Architecture (Agents, RAG, Embeddings)

---

# Разработка

## Подход

Итеративная разработка по функциональностям. Начинаем с MVP, затем расширяем.

---

## Итерация 1 — MVP

### Что входит

- Telegram Bot (Telegraf) — приём и отправка сообщений
- Backend API (Nest.js) — сохранение пользователей и сообщений, REST
- AI Service (FastAPI) — ответ через OpenAI ChatCompletion (без RAG)
- PostgreSQL + Prisma — хранение данных
- Docker Compose — запуск всего окружения

### Что откладывается

- Kafka / BullMQ
- RAG / pgvector / Embeddings
- Wikipedia Fetcher
- MCP Server
- LangGraph
- MinIO

### Поток данных

```text
Telegram
   ↓ сообщение
Telegram Bot (Telegraf)
   ↓ POST /messages
Backend API (Nest.js)
   ↓ сохраняет user + message в БД
   ↓ POST /generate
AI Service (FastAPI)
   ↓ OpenAI ChatCompletion
   ↓ ответ
Backend API
   ↓ сохраняет ответ в БД
   ↓ возвращает текст боту
Telegram Bot
   ↓ отправляет ответ пользователю
```

### Структура проекта

```text
prodigy/
├── docker-compose.yml
├── context.md
├── backend/                   ← Nest.js API
│   ├── src/
│   │   ├── users/
│   │   ├── messages/
│   │   └── prisma/
│   ├── prisma/
│   │   └── schema.prisma
│   ├── package.json
│   └── Dockerfile
├── ai-service/                ← Python FastAPI
│   ├── app/
│   │   ├── main.py
│   │   └── routes/
│   ├── requirements.txt
│   └── Dockerfile
└── telegram-bot/              ← Node.js Telegraf
    ├── src/
    │   └── index.ts
    ├── package.json
    └── Dockerfile
```

### Шаги реализации

1. `docker-compose.yml` — postgres + все три сервиса
2. **Backend API** — инициализация Nest.js, Prisma схема, модули `users` и `messages`, REST эндпоинты
3. **AI Service** — FastAPI проект, эндпоинт `POST /generate`, интеграция с OpenAI
4. **Telegram Bot** — Telegraf, обработка text-сообщений, вызовы Backend API
