# Project guidance

## Project overview

This repository contains a FastAPI product API and a React frontend. The backend entry point is `main.py`; product routes are in `routers/products.py`. Pydantic request models are in `models.py`, SQLAlchemy table definitions are in `db_models.py`, and database engine/session setup is in `database.py`. The frontend lives in `frontend/`.

## Working with this repository

- Read the relevant route, model, and database code before proposing or making changes.
- Keep changes focused on the requested task. Do not change API behavior, database behavior, or frontend behavior unless asked.
- Do not copy credentials, tokens, or other secrets into source, documentation, examples, or tool output. The current database connection is configured in `database.py`; treat its values as local-only and flag secure configuration as follow-up work.
- Preserve the existing Python and JavaScript dependency versions unless an upgrade is requested.
- Backend tests are in `tests/` and use pytest. Run them with `pytest`. Do not claim checks pass unless they have actually been run; describe any manual verification separately.
- For API work, inspect the generated OpenAPI documentation at `/docs` when the app and its MySQL database are available.

## Useful commands

- Backend: `uvicorn main:app --reload` (run from the repository root).
- Frontend: `cd frontend && npm start`.
- Frontend production build: `cd frontend && npm run build`.
