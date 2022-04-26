from tortoise import fields

from services.core.models import AbstractBaseModel, TimestampedMixin
from services.core.enums import Database


class AdminPlugin(AbstractBaseModel, TimestampedMixin):
    config = fields.JSONField(
        default=None, null=True, blank=True)

    class Meta:
        table = 'AdminPlugin'
        default_connection = Database.telegramcms.name

    def __str__(self):
        return str(self.__repr__())
