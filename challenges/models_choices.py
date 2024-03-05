from enum import Enum

from django.core.exceptions import ValidationError


class LaptopBrand(Enum):
    HP = "HP"
    DELL = "Dell"
    LENOVO = "Lenovo"
    ASUS = "Asus"
    ACER = "Acer"


class LoremCategory(Enum):
    quaerat = "quaerat"
    etincidunt = 'etincidunt'
    dolorem = 'dolorem'
    modi = 'modi'
    amet = 'amet'
    none = None

    @classmethod
    def is_valid(cls, value: str) -> bool:
        return value in [category.value for category in cls]

    @classmethod
    def validate_category(cls, value: str) -> None:
        if not LoremCategory.is_valid(value):
            raise ValidationError(f"{value} is not a valid category")


class PostStatus(Enum):
    published = "published"
    unpublished = "unpublished"
    banned = "banned"

    @classmethod
    def is_valid(cls, value: str) -> bool:
        return value in [status.value for status in cls]

    @classmethod
    def validate_status(cls, value: str) -> None:
        if value not in [status.value for status in cls]:
            raise ValidationError(f"{value} is not a valid status")
