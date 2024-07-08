from peewee import *
from db_conn import db, Target, Change

db.create_tables([Target, Change])