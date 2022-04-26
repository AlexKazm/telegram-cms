from tortoise import fields
from tortoise.models import Model


class TimestampedMixin:
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-updated_at']


class AbstractBaseModel(Model):
    id = fields.IntField(pk=True, index=True, unique=True)

    class Meta:
        abstract = True
