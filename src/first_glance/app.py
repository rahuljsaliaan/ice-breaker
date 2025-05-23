from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi_proxiedheadersmiddleware import ProxiedHeadersMiddleware
from langchain_core.callbacks.manager import CallbackManager
from contextlib import asynccontextmanager

from first_glance.api.middlewares import error_middleware, add_cors_middleware
from first_glance.api import first_glance_router
from first_glance.core import tracer
from first_glance.utils import https_url_for

# Tracker configure
if tracer:
    CallbackManager.configure(inheritable_callbacks=[tracer])


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 FastAPI application starting up: ✈️")
    yield
    print("🛑 FastAPI application shutting down.")


app = FastAPI(lifespan=lifespan)


add_cors_middleware(app)
app.add_middleware(ProxiedHeadersMiddleware)

app.middleware("http")(error_middleware)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        name="index.html",
        context={
            "request": request,
            "title": "First Glance",
            "name": "Rahul",
            "https_url_for": lambda name, **params: https_url_for(
                request, name, **params
            ),
        },
    )


app.include_router(router=first_glance_router, prefix="/api/v1", tags=["summary"])
