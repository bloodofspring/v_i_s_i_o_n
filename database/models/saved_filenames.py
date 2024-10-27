from peewee import CharField

from database.models.base import BaseModel


class SavedFileNames(BaseModel):
    file_name = CharField()
