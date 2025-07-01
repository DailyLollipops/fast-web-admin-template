from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import routes
import os

import routes.application_setting
import routes.auth
import routes.user

app = FastAPI(
    docs_url='/api/docs',
    openapi_url='/api/openapi.json',
)

app.include_router(routes.user.router, prefix='/api')
app.include_router(routes.auth.router, prefix='/api')
app.include_router(routes.application_setting.router, prefix='/api')

static_folder_path = os.path.join(os.getcwd(), 'static')
app.mount("/api/static", StaticFiles(directory=static_folder_path), name='static')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust to restrict access as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
