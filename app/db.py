from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from os import getenv, environ
from pathlib import Path
from dotenv import load_dotenv, dotenv_values

# Load .env from the project root explicitly (…\snapcart-backend-fastapi\.env)
ROOT_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT_DIR / ".env"

# 1) Try normal load
load_dotenv(dotenv_path=str(ENV_PATH))

DATABASE_URL = getenv("DATABASE_URL")

# 2) Fallback: parse .env manually and inject into os.environ
if not DATABASE_URL and ENV_PATH.exists():
    vals = dotenv_values(str(ENV_PATH))
    for k, v in vals.items():
        if v is not None and k not in environ:
            environ[k] = v
    DATABASE_URL = environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(f"DATABASE_URL is not set. Looked for {ENV_PATH}. "
                       "Open your .env and ensure DATABASE_URL=... is on a single line.")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
