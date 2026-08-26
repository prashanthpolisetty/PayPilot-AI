from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import init_db
from app.db.seed import seed_database
from app.api.router import router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Agentic Commerce Platform built for Razorpay Buildathon Track 01"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()
    seed_database()

from pathlib import Path
from fastapi.staticfiles import StaticFiles

app.include_router(router)

dist_path = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if dist_path.exists():
    app.mount("/", StaticFiles(directory=str(dist_path), html=True), name="frontend")
else:
    @app.get("/")
    def root():
        return {
            "status": "online",
            "project": settings.PROJECT_NAME,
            "track": "Track 01: AI Growth & Agentic Commerce",
            "razorpay_key_id": settings.RAZORPAY_KEY_ID[:8] + "...",
            "llm_provider": settings.LLM_PROVIDER
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
