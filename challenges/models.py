from django.core.exceptions import ValidationError
from django.db import models
from enum import Enum


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


class Book(models.Model):
    title: models.CharField = models.CharField(max_length=256)
    author_full_name: models.CharField = models.CharField(max_length=256)
    isbn: models.CharField = models.CharField(max_length=10)

    def __str__(self) -> str:
        return self.title


class Laptop(models.Model):
    class Meta:
        ordering = ["-created_at"]

    brand = models.CharField(max_length=256, choices=[(brand.name, brand.value) for brand in LaptopBrand])
    year = models.IntegerField()
    memory = models.IntegerField()
    disk = models.IntegerField()
    price = models.FloatField()
    count = models.IntegerField()
    created_at = models.DateTimeField()

    def __str__(self) -> str:
        return self.brand

    def to_json(self) -> dict[str, int | str | float | models.DateTimeField]:
        json = {}
        for field in self._meta.get_fields():
            json[field.name] = getattr(self, field.name)
        return json


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


class Post(models.Model):

    class Meta:
        ordering = ["-created_at"]

    title = models.CharField(max_length=256)
    content = models.TextField()
    author = models.CharField(max_length=256)
    status = models.CharField(choices=[(status.name, status.value) for status in PostStatus],
                              default=PostStatus.unpublished, max_length=16, validators=[PostStatus.validate_status])
    created_at = models.DateTimeField(null=False, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    category = models.CharField(choices=[(category.name, category.value) for category in LoremCategory],
                                max_length=64, null=True, blank=True, validators=[LoremCategory.validate_category])

    def __str__(self) -> str:
        return self.title

    def to_json(self) -> dict[str, str | models.DateTimeField]:
        json = {}
        for field in self._meta.get_fields():
            json[field.name] = getattr(self, field.name)
        return json

    def clean(self, *args, **kwargs) -> None:
        if self.status == PostStatus.unpublished:
            self.published_at = None
        elif self.published_at is not None and self.published_at <= self.created_at:
            raise ValidationError("publication date shall be after creation date.")
        super().clean(*args, **kwargs)

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)
