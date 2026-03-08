from fastapi import FastAPI
from app.api.v1.endpoints import videos,auth,ingest
from app.db.session import engine, Base
from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from fastapi.security import OAuth2PasswordBearer

# Create the tables in PostgreSQL automatically
Base.metadata.create_all(bind=engine) #[cite: 37]

app = FastAPI(title="Railway CCTV Dashboard")

# This line is the key—it adds the "Authorize" button to Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


# 1. Authentication Endpoints
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
# 2. Ingest Endpoints (Matches the 'Ingest' section in your reference)
app.include_router(ingest.router, prefix="/api/v1/ingest", tags=["Ingest"])
# 3. Railway APIs (Retrieval and Summary)
app.include_router(videos.router, prefix="/api/v1", tags=["API"])

@app.get("/api/v1/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}

# Instead of using try/except blocks in every route, we create a global handler
@app.exception_handler(SQLAlchemyError)
async def db_exception_handler(request: Request, exc: SQLAlchemyError):
    # Specialized handler for database errors
    return JSONResponse(
        status_code=500,
        content={"message": "Database connection error", "detail": str(exc)}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Catch-all for any other unexpected errors
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error", "type": type(exc).__name__}
    )