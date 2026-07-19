from collections.abc import Iterable, Mapping
from typing import Any

from ...standards import SirenMediaType
from .response import EMPTY_HEADERS, EMPTY_VALUES, NinjaExtraSirenResponse, NinjaExtraSirenResponseFactory


def problem_document(
    *,
    title: str,
    status: int,
    detail: str = "",
    type_: str = "",
    instance: str = "",
    errors: tuple[Mapping[str, Any], ...] = (),
    extra: Mapping[str, Any] = EMPTY_VALUES,
) -> dict[str, Any]:
    document: dict[str, Any] = {"title": title, "status": status}
    if type_:
        document["type"] = type_
    if detail:
        document["detail"] = detail
    if instance:
        document["instance"] = instance
    if errors:
        document["errors"] = tuple(dict(error) for error in errors)
    document.update(extra)
    return document


def validation_problem(
    errors: Any,
    *,
    title: str = "Validation error",
    status: int = 422,
    detail: str = "",
    type_: str = "",
    instance: str = "",
) -> dict[str, Any]:
    return problem_document(
        title=title,
        status=status,
        detail=detail,
        type_=type_,
        instance=instance,
        errors=_errors(errors),
    )


def problem_from_exception(
    error: BaseException,
    *,
    title: str = "",
    status: int = 500,
    detail: str = "",
    type_: str = "",
    instance: str = "",
) -> dict[str, Any]:
    resolved_status = _status(error, status)
    resolved_title = title or _title(error, resolved_status)
    resolved_detail = detail or _detail(error)
    errors = _exception_errors(error)
    if errors:
        return validation_problem(
            errors,
            title=resolved_title,
            status=resolved_status,
            detail=resolved_detail,
            type_=type_,
            instance=instance,
        )
    return problem_document(
        title=resolved_title,
        status=resolved_status,
        detail=resolved_detail,
        type_=type_,
        instance=instance,
    )


def problem_response(
    problem: Mapping[str, Any],
    *,
    headers: Mapping[str, str] = EMPTY_HEADERS,
) -> NinjaExtraSirenResponse:
    status = problem.get("status")
    if not isinstance(status, int):
        raise ValueError("Problem document status must be an integer")
    return NinjaExtraSirenResponseFactory().create(
        dict(problem),
        status_code=status,
        headers=headers,
        content_type=SirenMediaType.PROBLEM,
    )


def exception_problem_response(
    error: BaseException,
    *,
    title: str = "",
    status: int = 500,
    detail: str = "",
    type_: str = "",
    instance: str = "",
    headers: Mapping[str, str] = EMPTY_HEADERS,
) -> NinjaExtraSirenResponse:
    return problem_response(
        problem_from_exception(
            error,
            title=title,
            status=status,
            detail=detail,
            type_=type_,
            instance=instance,
        ),
        headers=headers,
    )


def validation_problem_response(
    errors: Any,
    *,
    title: str = "Validation error",
    status: int = 422,
    detail: str = "",
    type_: str = "",
    instance: str = "",
    headers: Mapping[str, str] = EMPTY_HEADERS,
) -> NinjaExtraSirenResponse:
    return problem_response(
        validation_problem(
            errors,
            title=title,
            status=status,
            detail=detail,
            type_=type_,
            instance=instance,
        ),
        headers=headers,
    )


def _status(error: BaseException, fallback: int) -> int:
    for name in ("status_code", "status", "code"):
        value = getattr(error, name, "")
        if isinstance(value, int) and 100 <= value <= 599:
            return value
    return fallback


def _title(error: BaseException, status: int) -> str:
    for name in ("title", "reason", "message"):
        value = getattr(error, name, "")
        if isinstance(value, str) and value:
            return value
    if status == 400:
        return "Bad request"
    if status == 401:
        return "Unauthorized"
    if status == 403:
        return "Forbidden"
    if status == 404:
        return "Not found"
    if status == 422:
        return "Validation error"
    return "Internal server error" if status >= 500 else "Request error"


def _detail(error: BaseException) -> str:
    value = getattr(error, "detail", "")
    if isinstance(value, str) and value:
        return value
    if value:
        return str(value)
    message = str(error)
    if message:
        return message
    if error.args:
        return str(error.args[0])
    return message if message else ""


def _exception_errors(error: BaseException) -> tuple[Mapping[str, Any], ...]:
    if hasattr(error, "errors") and callable(error.errors):
        return _errors(error.errors())
    value = getattr(error, "errors", ())
    if value:
        return _errors(value)
    value = getattr(error, "detail", ())
    if not isinstance(value, str) and value:
        return _errors(value)
    return ()


def _errors(errors: Any) -> tuple[Mapping[str, Any], ...]:
    if isinstance(errors, Mapping):
        return tuple({"field": field, "message": message} for field, message in errors.items())
    if isinstance(errors, (str, bytes)) or not isinstance(errors, Iterable):
        return ({"message": str(errors)},)
    return tuple(_error(error) for error in errors)


def _error(error: Any) -> Mapping[str, Any]:
    if isinstance(error, Mapping):
        return dict(error)
    return {"message": str(error)}


__all__ = [
    "exception_problem_response",
    "problem_document",
    "problem_from_exception",
    "problem_response",
    "validation_problem",
    "validation_problem_response",
]
