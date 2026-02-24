## Project Structure
```
app/
├── main.py                 # Main entry point, creates FastAPI instance and starts the server
├── core/
│   ├── config.py           # Environment variables and settings (Pydantic)
│   ├── security.py         # JWT creation, password hashing, OAuth flows
│   └── dependencies.py     # Reusable dependencies (e.g., get_db_session)
├── db/
│   ├── session.py          # SQLAlchemy engine and sessionmaker setup
│   └── base.py             # Declarative base for models
├── services/
│   └── utils.py            # Common utility functions
├── features/
│   ├── users/              # User management feature
│   │   ├── models.py       # SQLAlchemy models
│   │   ├── schemas.py      # Pydantic schemas (request/response validation)
│   │   ├── crud.py         # Database access/query logic
│   │   ├── services.py     # Business logic
│   │   └── routers.py      # API endpoints (APIRouter)
│   ├── items/              # Item management feature
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── crud.py
│   │   ├── services.py
│   │   └── routers.py
│   └── ...                 # Other features
└── tests/                    # Unit and integration tests
requirements.txt              # Separated dependency files
README.md                     # Project documentation
```