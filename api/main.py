from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from api.middlewares.tracing import TracingMiddleware, setup_tracing
from api.routes.application_setting import router as app_setting_router
from api.routes.auth import router as auth_router
from api.routes.notification import router as notification_router
from api.routes.role_access_control import router as role_access_control_router
from api.routes.template import router as template_router
from api.routes.user import router as user_router
from api.settings import settings


BASE_PATH = Path(__file__).parent
STATIC_DIR = BASE_PATH / 'static'
ROOT_API_PATH = '/api'
FAVICON_URL = f'{ROOT_API_PATH}/static/brand.png'

app = FastAPI(
    title=settings.APP_NAME.title(),
    description=f'API documentation for {settings.APP_NAME.title()}',
    docs_url=f'{ROOT_API_PATH}/docs',
    redoc_url=f'{ROOT_API_PATH}/redoc',
    openapi_url='/openapi.json',
    root_path=ROOT_API_PATH,
    version='1.0.0',
)
setup_tracing(app)
app.add_middleware(TracingMiddleware)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(notification_router)
app.include_router(app_setting_router)
app.include_router(role_access_control_router)
app.include_router(template_router)

app.mount('/static', StaticFiles(directory=STATIC_DIR), name='static')

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


@app.get('/docs', include_in_schema=False)
async def swagger_ui_docs(request: Request):
    root_path = request.scope.get('root_path', '').rstrip('/')
    openapi_url = root_path + app.openapi_url
    oauth2_redirect_url = app.swagger_ui_oauth2_redirect_url
    if oauth2_redirect_url:
        oauth2_redirect_url = root_path + oauth2_redirect_url

    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title=f'{app.title} - Swagger UI',
        oauth2_redirect_url=oauth2_redirect_url,
        init_oauth=app.swagger_ui_init_oauth,
        swagger_favicon_url=FAVICON_URL,
        swagger_ui_parameters=app.swagger_ui_parameters,
    )


@app.get('/redoc', include_in_schema=False)
async def redoc_docs(request: Request):
    root_path = request.scope.get('root_path', '').rstrip('/')
    openapi_url = root_path + app.openapi_url

    return get_redoc_html(
        openapi_url=openapi_url, title=f'{app.title} - ReDoc',
        redoc_favicon_url=FAVICON_URL
    )
