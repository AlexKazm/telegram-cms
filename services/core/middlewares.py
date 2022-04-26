from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from fastapi import middleware


class LoginRequired(middleware.Middleware):
    pass
