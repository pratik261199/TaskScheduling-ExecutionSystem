# Task Executor Service

This service acts as a mock business application that receives and processes webhooks. It is designed to simulate both synchronous and asynchronous task processing, making it a realistic target for the `scheduler-service`.

## Architecture

This service is a standard FastAPI application with a layered architecture.

- **API Layer (`api/`):**
- **Controller Layer (`controllers/`):**
- **Service Layer (`services/`):**  Contains business logic.
- **Repository Layer (`repository/`):** Interacts with database.
- **Database (`db/` & `models/`):**.

### Key Features

- **Synchronous Endpoint:** A webhook endpoint that processes the request immediately and returns a `200 OK` status.
- **Asynchronous Endpoint:** An endpoint that accepts a task, returns a `202 Accepted` status immediately, and provides a `check_url` for polling. The actual processing happens in the background.
- **Status Endpoint:** An endpoint (`/status/{task_id}`) that allows a client (like the `scheduler-service`) to poll for the status of an asynchronously processed task.

## How to Run This Service

**Note:** This service is designed to be run as part of the whole system from the **root directory's `docker-compose.yml`**. The instructions below are for context but are superseded by the main project's `README.md`.

### Running with Docker (Recommended)

The service is managed by the main `docker-compose.yml` at the project root.

1.  **Navigate to the Project Root:**
    ```sh
    cd /path/to/TaskScheduling&ExecutionSystem
    ```

2.  **Start All Services:**
    ```sh
    docker-compose up
    ```
    This command will build and start this service on port `8001` alongside the scheduler and other components. When running inside the Docker network, this service is accessible to other services at the hostname `http://executor:8001`.

### Local Development (Without Docker)

To run this service directly on your local machine for debugging:

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
    Create a `.env` file and ensure `EXECUTOR_POSTGRES_HOST` is set to `localhost`.
4.  **Run the database migrations:**
    ```sh
    alembic upgrade head
    ```
5.  **Start the FastAPI server:**
    ```sh
    uvicorn main:app --host 0.0.0.0 --port 8001 --reload
    ```
