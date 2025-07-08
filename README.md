# FastAPI User Authentication App

A production-ready user authentication API using FastAPI, PostgreSQL, SQLAlchemy, Alembic, and JWT.

## Features
- User registration and login
- JWT authentication
- Password hashing
- Modular, scalable structure
- Dockerized for easy setup

## Quickstart

### 1. Clone and configure environment

```
git clone <repo-url>
cd user-authentication-fast-api
cp .env.example .env
```

### 2. Run with Docker

```
docker-compose up --build
```

### 3. Run locally

- Create a PostgreSQL database and update `.env`.
- Run migrations:

```
alembic upgrade head
```

- Start the app:

```
uvicorn app.main:app --reload
```

## Folder Structure

- `app/` - Main application code
- `alembic/` - Database migrations

## API Docs

Visit [http://localhost:8000/docs](http://localhost:8000/docs) after running the app. 