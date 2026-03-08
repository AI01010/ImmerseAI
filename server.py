"""
ImmerseAI Production Server

Serves the React frontend as static files and proxies ADK API routes
to the adk api_server running on localhost:8001.
"""

import os
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

ADK_BACKEND = "http://127.0.0.1:8001"
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

app = FastAPI(docs_url=None, redoc_url=None)


async def _proxy(request: Request) -> Response:
    path = request.url.path
    query = f"?{request.url.query}" if request.url.query else ""
    url = f"{ADK_BACKEND}{path}{query}"
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.request(
                method=request.method,
                url=url,
                headers={
                    k: v for k, v in request.headers.items()
                    if k.lower() not in ("host", "content-length")
                },
                content=await request.body(),
            )
            return Response(
                content=resp.content,
                status_code=resp.status_code,
                headers={
                    k: v for k, v in resp.headers.items()
                    if k.lower() != "transfer-encoding"
                },
            )
    except httpx.ConnectError:
        return Response(
            content=b'{"error":"ADK backend starting up — retry in a moment"}',
            status_code=503,
            media_type="application/json",
        )


@app.api_route("/run", methods=["GET", "POST", "OPTIONS"])
async def proxy_run(request: Request):
    return await _proxy(request)


@app.api_route("/list", methods=["GET", "OPTIONS"])
async def proxy_list(request: Request):
    return await _proxy(request)


@app.api_route("/apps/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def proxy_apps(request: Request, path: str):
    return await _proxy(request)


@app.api_route("/debug/{path:path}", methods=["GET", "OPTIONS"])
async def proxy_debug(request: Request, path: str):
    return await _proxy(request)


# Serve React SPA — must be registered last
if os.path.exists(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
