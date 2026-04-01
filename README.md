# FastAPI REST API Blueprint

A clean, scalable, and modular FastAPI boilerplate.

## Project Structure

```text
.
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   └── health.py    # Health check endpoint
│   │       └── api.py           # V1 router
│   ├── core/
│   │   └── config.py            # Configuration (Pydantic settings)
│   ├── db/                      # Database logic (session, etc.)
│   ├── models/                  # Database models
│   ├── schemas/                 # Pydantic schemas
│   └── main.py                  # API entry point
├── .env                         # Environment variables
├── .gitignore                   # Python gitignore
└── requirements.txt             # Project dependencies
```

## Setup and Running

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Access the API**:
   - API Root: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
   - Health Check: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)
   - Interactive Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
