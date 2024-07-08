from peewee import *
import datetime

db = SqliteDatabase('test.db')
class BaseModel(Model):
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db

class Target(BaseModel):
    steam_id = CharField(unique=True)
    vanity_url = TextField()
    name = TextField()

class Change(BaseModel):
    steam_id = ForeignKeyField(Target, backref='targets')
    alias = TextField()

db.connect()
