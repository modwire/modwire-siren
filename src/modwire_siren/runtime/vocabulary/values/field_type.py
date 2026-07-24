from enum import StrEnum


class SirenFieldType(StrEnum):
    CHECKBOX = "checkbox"
    COLOR = "color"
    DATE = "date"
    DATETIME = "datetime"
    DATETIME_LOCAL = "datetime-local"
    EMAIL = "email"
    FILE = "file"
    HIDDEN = "hidden"
    MONTH = "month"
    NUMBER = "number"
    PASSWORD = "password"
    RADIO = "radio"
    RANGE = "range"
    SEARCH = "search"
    TEL = "tel"
    TEXT = "text"
    TIME = "time"
    URL = "url"
    WEEK = "week"
