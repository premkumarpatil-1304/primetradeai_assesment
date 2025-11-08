# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.api.v1 import auth, tasks

app = FastAPI(title="Primetrade API", version="1.0")

# ✅ Allow frontend access (React app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"] for your React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Include routers only once
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["Tasks"])


# ✅ MongoDB connection events
@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()


# ✅ Add proper JWT Bearer security to Swagger UI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Primetrade API",
        version="1.0",
        description="FastAPI backend with JWT authentication and CRUD support",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
