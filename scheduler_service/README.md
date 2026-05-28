# Task Scheduler Service

This service is responsible for managing the lifecycle of scheduled tasks. It provides a REST API to create tasks, stores them in a database, and uses a Celery-based system to trigger their execution at the specified time.

## Architecture

This service follows a clean, layered architecture to ensure separation of concerns and maintainability.

- **API Layer (`api/`):** Built with FastAPI. It defines the REST endpoints for interacting with the service (e.g., creating tasks). It handles request validation and serialization.
- **Controller Layer (`controllers/`):** Acts as an intermediary between the API and the service layer. It orchestrates calls to the service layer but contains no business logic itself.
- **Service Layer (`services/`):** Contains the core business logic. It orchestrates operations like creating task definitions, dispatching due tasks, and handling webhook responses.
- **Repository Layer (`repository/`):** The data access layer. It is responsible for all communication with the database, abstracting away the specifics of SQL queries.
- **Database (`db/` & `models/`):** Uses SQLAlchemy and Alembic for ORM and database migrations. It connects to a dedicated PostgreSQL database.
- **Background Jobs (`celery_worker/`):**
    - **Celery:** Used for executing background and scheduled tasks.
    - **Redis:** Acts as the message broker and backend for Celery.
    - **Celery Beat:** A scheduler that periodically triggers tasks (e.g., checking for due webhooks every minute).
    - **Celery Worker:** Listens for tasks on the Redis queue and executes them (e.g., making the actual HTTP call to a webhook).

## How to Run This Service

**Note:** This service is designed to be run as part of the whole system from the **root directory's `docker-compose.yml`**. The instructions below are for context but are superseded by the main project's `README.md`.

### Running with Docker (Recommended)

The entire application stack (web server, Celery worker, Celery beat, and Redis) is managed by the main `docker-compose.yml` at the project root.

1.  **Navigate to the Project Root:**
    ```sh
    cd /path/to/TaskScheduling&ExecutionSystem
    ```

2.  **Start All Services:**
    ```sh
    docker-compose up
    ```
    This command will build and start this service along with all its dependencies and the other microservices.

### Local Development (Without Docker)

If you need to run this service locally for debugging:

1.  **Set up a virtual environment:**
    ```sh
    python -m venv venv
    source venv/bin/activate
    ```
2.  **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```
3.  **Set up environment variables:**
    Create a `.env` file based on the existing one and ensure the `SCHEDULER_POSTGRES_HOST` and `REDIS_HOST` are set to `localhost`.
4.  **Run the database migrations:**
    ```sh
    alembic upgrade head
    ```
5.  **Start the services in separate terminals:**
    ```sh
    # Terminal 1: FastAPI Server
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload

    # Terminal 2: Celery Worker
    celery -A celery_worker.app worker --loglevel=info

    # Terminal 3: Celery Beat
    celery -A celery_worker.app beat --loglevel=info
    ```
