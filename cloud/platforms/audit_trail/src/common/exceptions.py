from abc import ABC

from src.common.schemas import ErrorSchema


class BaseValidationException(ABC, ValueError):
    error: ErrorSchema
