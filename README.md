# FastAPI Product API

A learning project with a FastAPI backend for product CRUD operations and a React frontend.

## Project layout

- `main.py` — creates the FastAPI application and includes the product router.
- `routers/products.py` — product endpoints and database operations.
- `models.py` — Pydantic product request model.
- `db_models.py` — SQLAlchemy product table model.
- `database.py` — SQLAlchemy engine and session configuration.
- `frontend/` — React application and its npm scripts.

## Requirements

- Python 3.13 (the existing project environment uses Python 3.13).
- MySQL running locally, with a database named `fastapidb` available to the application.
- Node.js and npm for the frontend; the checked-in `frontend/package-lock.json` can be used for reproducible npm installs.

The backend reads its database connection URL from the `DATABASE_URL` environment variable. For local MySQL, set it in your shell before starting the backend. Replace the placeholders with your local database name, username, and password:

```bash
export DATABASE_URL='mysql+pymysql://<username>:<password>@localhost:3306/fastapidb'
```

Set `CORS_ORIGINS` to a comma-separated list of trusted frontend origins when the frontend is hosted outside `http://localhost:3000`. For example:

```bash
export CORS_ORIGINS='https://shop.example.com,https://admin.example.com'
```

Do not commit real credentials. Tests use an in-memory SQLite database and do not need MySQL credentials.

## Backend setup and run

From the repository root, create and activate a virtual environment if needed, then install the pinned backend dependencies:

```bash
python3.13 -m venv myenv
source myenv/bin/activate
python -m pip install -r requirements.txt
```

Set `DATABASE_URL` and start the backend after MySQL is available:

```bash
uvicorn main:app --reload
```

The API listens at `http://localhost:8000`. FastAPI's interactive API documentation is at `http://localhost:8000/docs`.

## Database migrations

Apply migrations from the repository root before starting the backend:

```bash
alembic upgrade head
```

For a database that already has a `products` table, first verify its schema matches the initial migration. Only then mark that revision as applied:

```bash
alembic stamp 20261028_0001
```

## Backend tests

Install the development dependencies and run the backend tests from the repository root:

```bash
python -m pip install -r requirements-dev.txt
pytest
```

The route tests use an in-memory SQLite database and do not require the local MySQL service.

## Frontend setup and run

In another terminal:

```bash
cd frontend
npm ci
npm start
```

The React development server runs at `http://localhost:3000`. Its package configuration proxies API requests to the backend at `http://localhost:8000`.

To create a frontend production build, run `npm run build` from `frontend/`.

## Current project status

The product API is under active improvement. The first backend tests cover CRUD behavior, request validation, response models, and not-found cases. Database migrations, startup lifecycle, authentication, and production deployment controls remain follow-up work.
