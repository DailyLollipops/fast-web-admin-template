import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes.application_setting import router as app_setting_router
from routes.auth import router as auth_router
from routes.role_access_control import router as role_access_control_router
from routes.user import router as user_router


app = FastAPI(
    docs_url='/api/docs',
    openapi_url='/api/openapi.json',
)

app.include_router(app_setting_router, prefix='/api')
app.include_router(auth_router, prefix='/api')
app.include_router(role_access_control_router, prefix='/api')
app.include_router(user_router, prefix='/api')

static_folder_path = os.path.join(os.getcwd(), 'static')
app.mount("/api/static", StaticFiles(directory=static_folder_path), name='static')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust to restrict access as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
