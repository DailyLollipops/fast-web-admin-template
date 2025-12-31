from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from middlewares.tracing import TracingMiddleware
from routes.application_setting import router as app_setting_router
from routes.auth import router as auth_router
from routes.notification import router as notification_router
from routes.role_access_control import router as role_access_control_router
from routes.template import router as template_router
from routes.user import router as user_router
from tracing import setup_tracing


BASE_PATH = Path(__file__).parent
STATIC_DIR = BASE_PATH / 'static'

app = FastAPI(
    docs_url='/docs',
    openapi_url='/openapi.json',
    root_path='/api',
    version='1.0.0',
)
setup_tracing(app)
app.add_middleware(TracingMiddleware)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(notification_router)
app.include_router(app_setting_router)
app.include_router(role_access_control_router)
app.include_router(template_router)

app.mount('/api/static', StaticFiles(directory=STATIC_DIR), name='static')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # Adjust to restrict access as needed
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    trace_id = getattr(request.state, 'trace_id', '0')
    elapsed_ms = getattr(request.state, 'elapsed_ms', 0)
    return JSONResponse(
        content={'detail': 'Internal Server Error'},
        status_code=500,
        headers={
            'X-Trace-ID': trace_id,
            'X-Elapsed-Time': f'{elapsed_ms:.2f}ms',
        },
    )
