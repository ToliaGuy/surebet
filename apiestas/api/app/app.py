import os
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette_prometheus import metrics, PrometheusMiddleware

from .api.errors.http_error import http_error_handler
from .api.errors.validation_error import http422_error_handler
from .api.api import router as api_router
from .core.config import ALLOWED_HOSTS, API_PREFIX, DEBUG, PROJECT_NAME, VERSION
from .core.events import create_start_app_handler, create_stop_app_handler
from capiestas.metrics_settings import PROMETHEUS_ENABLED


def get_application() -> FastAPI:
    application = FastAPI(title=PROJECT_NAME, debug=DEBUG, version=VERSION)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_HOSTS or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_event_handler("startup", create_start_app_handler(application))
    application.add_event_handler("shutdown", create_stop_app_handler(application))

    application.add_exception_handler(HTTPException, http_error_handler)
    application.add_exception_handler(RequestValidationError, http422_error_handler)

    application.include_router(api_router, prefix=API_PREFIX)
    # add static files
    application.mount("/static", StaticFiles(directory="capiestas/api/app/api/static/"), name="static")

    if PROMETHEUS_ENABLED:
        application.add_middleware(PrometheusMiddleware)
        application.add_route("/metrics", metrics)

    return application
