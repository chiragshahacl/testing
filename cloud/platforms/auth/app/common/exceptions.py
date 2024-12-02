from abc import ABC

from app.common.schemas import ErrorSchema


class BaseValidationException(ABC, ValueError):
    error: ErrorSchema
