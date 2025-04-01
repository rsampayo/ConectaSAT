# CFDI Verification API

A FastAPI application for verifying CFDIs (Comprobantes Fiscales Digitales por Internet) with the Mexican SAT (Servicio de Administración Tributaria).

## Features

- Verify individual CFDI documents
- Batch verify multiple CFDIs in a single request
- Admin panel for token management
- Secure API authentication

## Tech Stack

- **Python 3.10 LTS**: For performance and stability
- **FastAPI**: Modern, high-performance API framework
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL** (production) / **SQLite** (development): Database
- **Pydantic**: Data validation and settings management
- **Pytest**: Testing framework

## Local Development

### Setup

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Set up environment variables (or modify `.env` file):
```
DATABASE_URL=sqlite:///./dev.db
ADMIN_USERNAME=admin
ADMIN_PASSWORD=changeme
SECRET_KEY=supersecretkey123456789
```

### Running the Application

```bash
uvicorn app.main:app --reload
```

Access the API at http://localhost:8000 and documentation at http://localhost:8000/docs

### Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=term
```

## API Endpoints

### Public Endpoints
- `GET /health` - Health check endpoint
- `GET /` - API information

### Authenticated Endpoints
- `POST /verify-cfdi` - Verify a single CFDI
- `POST /verify-cfdi-batch` - Verify multiple CFDIs

### Admin Endpoints
- `POST /admin/tokens` - Create a new API token
- `GET /admin/tokens` - List all API tokens
- `GET /admin/tokens/{token_id}` - Get a specific API token
- `PUT /admin/tokens/{token_id}` - Update an API token
- `DELETE /admin/tokens/{token_id}` - Delete an API token
- `POST /admin/tokens/{token_id}/regenerate` - Regenerate an API token
- `POST /admin/superadmins` - Create a new superadmin
- `PUT /admin/superadmins/{username}/password` - Update a superadmin's password
- `DELETE /admin/superadmins/{username}` - Deactivate a superadmin account

## Authentication

The API uses two types of authentication:
- **Bearer Token**: For API endpoints (used by `verify-cfdi` and related endpoints)
- **HTTP Basic**: For admin endpoints

## Deployment to Heroku

This application is optimized for deployment to Heroku:

1. Create a new Heroku app
```bash
heroku create
```

2. Set environment variables
```bash
heroku config:set ADMIN_PASSWORD=yoursecurepassword
heroku config:set SECRET_KEY=yoursecretkey
```

3. Deploy
```bash
git push heroku main
```

## License

MIT
