# Async Task Processor API

A robust, non-blocking API that offloads time-consuming tasks to background workers - a foundational pattern for scalable AI applications.

## 🏗️ Architecture

This application demonstrates a production-ready microservices architecture:

- **FastAPI**: High-performance web framework providing the REST API
- **Celery**: Distributed task queue for background job processing  
- **Redis**: Message broker and result backend
- **PostgreSQL**: Persistent storage for task status and results
- **Docker Compose**: Orchestrates all services with proper networking

## 🚀 How It Works

1. **Client Request**: POST to `/process` with optional data payload
2. **Non-blocking Response**: API immediately returns a `task_id` (< 50ms)
3. **Background Processing**: Celery worker picks up the task from Redis queue
4. **Heavy Computation**: Worker simulates time-consuming processing (5-10 seconds)
5. **Result Storage**: Completed results stored in PostgreSQL with timestamps
6. **Status Polling**: Client polls GET `/results/{task_id}` to check progress

## 📋 Requirements

- Docker and Docker Compose
- Python 3.11+ (for local development)

## 🔧 Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd AsyncTaskProcessor
```

### 2. Start All Services
```bash
docker-compose up --build
```

This launches:
- **API**: http://localhost:8000 (FastAPI with auto-reload)
- **Worker**: Celery worker process
- **Redis**: localhost:6379
- **PostgreSQL**: localhost:5432

### 3. Test the API

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Create Task (Non-blocking):**
```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"data": {"input": 42, "operation": "compute"}}'
```

**Check Status:**
```bash
curl http://localhost:8000/results/{task_id}
```

## 🧪 Running Tests

The comprehensive test suite validates the entire async workflow:

```bash
# Start services first
docker-compose up -d

# Run integration tests
python test_async_processor.py
```

**Test Coverage:**
- ✅ Non-blocking task creation (< 50ms response time)
- ✅ Task status retrieval and polling
- ✅ Complete async workflow validation
- ✅ Error handling for non-existent tasks
- ✅ Database operations and data persistence

## 📊 API Specification

### POST `/process`
Creates a new background task.

**Request Body:**
```json
{
  "data": {
    "input": 42,
    "operation": "compute"
  }
}
```

**Response (< 50ms):**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Task queued for processing"
}
```

### GET `/results/{task_id}`
Retrieves task status and results.

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "result": 499999500000,
  "error_message": null,
  "created_at": "2025-10-02T10:30:00.123456",
  "completed_at": "2025-10-02T10:30:08.654321"
}
```

**Status Values:**
- `pending`: Task queued but not yet processed
- `completed`: Task finished successfully
- `failed`: Task encountered an error

## 🏛️ Database Schema

**Tasks Table:**
```sql
CREATE TABLE tasks (
    task_id VARCHAR PRIMARY KEY,
    status VARCHAR DEFAULT 'pending',
    result INTEGER NULL,
    error_message TEXT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP NULL
);
```

## 🐳 Docker Services

### API Service
- **Image**: Custom Python 3.11 with FastAPI
- **Port**: 8000
- **Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

### Celery Worker
- **Image**: Same as API (shared codebase)
- **Command**: `celery -A app.celery_app worker --loglevel=info`

### Redis Broker
- **Image**: `redis:7-alpine`
- **Port**: 6379
- **Health Check**: `redis-cli ping`

### PostgreSQL Database
- **Image**: `postgres:15`
- **Port**: 5432
- **Database**: `async_processor`
- **Health Check**: `pg_isready -U postgres`

## 🔧 Local Development

### Setup Environment
```bash
# Copy environment template
cp .env.example .env

# Install dependencies
pip install -r requirements.txt
```

### Run Services Separately
```bash
# Terminal 1: Start Redis and PostgreSQL
docker-compose up postgres redis

# Terminal 2: Start API
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/async_processor"
export CELERY_BROKER_URL="redis://localhost:6379/0"
export CELERY_RESULT_BACKEND="redis://localhost:6379/0"
uvicorn app.main:app --reload

# Terminal 3: Start Celery Worker
celery -A app.celery_app worker --loglevel=info
```

## 📈 Performance Characteristics

- **Task Creation**: < 50ms response time (non-blocking)
- **Background Processing**: 5-10 seconds (simulated heavy computation)
- **Throughput**: Limited by worker capacity (horizontally scalable)
- **Persistence**: All task data stored in PostgreSQL
- **Reliability**: Automatic retries on task failure (3 attempts)

## 🔒 Production Considerations

1. **Security**: Add authentication/authorization middleware
2. **Monitoring**: Integrate Prometheus metrics and health checks
3. **Scaling**: Add more Celery workers based on queue depth
4. **Logging**: Structured logging with correlation IDs
5. **Rate Limiting**: Implement request throttling
6. **Caching**: Add Redis caching for frequently accessed results

## 🤝 Use Cases

This pattern is fundamental for:
- **AI/ML Inference**: Long-running model predictions
- **Data Processing**: ETL pipelines and batch operations  
- **Image/Video Processing**: Media transcoding and analysis
- **Report Generation**: Complex document creation
- **Email Campaigns**: Large-scale notification delivery
- **API Integrations**: Third-party service calls with timeouts

## 📝 License

MIT License - Feel free to use this pattern in your applications!
