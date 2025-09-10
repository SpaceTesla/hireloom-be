from fastapi import FastAPI
from dotenv import load_dotenv
from api.routes import router as api_router


def main():
    # Ensure .env variables are loaded when running via uvicorn factory
    load_dotenv()
    app = FastAPI(title="HireLoom Backend")
    app.include_router(api_router)
    return app


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:main", host="0.0.0.0", port=8000, factory=True)
