from peewee import *
import datetime

db = SqliteDatabase('database/test.db')
class BaseModel(Model):
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db

class Target(BaseModel):
    steam_id = CharField(unique=True)
    vanity_url = TextField()
    name = TextField()
    status = TextField(null = True)

class Change(BaseModel):
    steam_id = ForeignKeyField(Target, backref='targets')
    alias = TextField()
    
def main():
    db.connect()

if __name__ == "__main__":
    main()

def get_targets():
    return Target.select()

def getTargetById(id):
    query = Target.select().where(Target.steam_id == id)
    if not query.exists():
        return False
    else:
        return query.get()
    
def putTarget(steamId,name1,vanityURL,status1):
    newRecord = Target(
        steam_id=steamId, 
        name=name1, 
        vanity_url=vanityURL,
        status=status1)
    newRecord.save()

def deleteTarget(id):
    qry = Target.delete().where(Target.steam_id == id)
    qry.execute()

def getLatestChangeById(id):
    query = Change.select().where(Change.steam_id == id).order_by(Change.created_at.desc())
    if not query.exists():
        return False
    else:
        return query.get()

def putChangeRecord(id,newAlias):
    updateRecord = Change(steam_id=id, alias=newAlias)
    updateRecord.save()
    
def updateTargetStatus(id,status):
    updateRecord : Target = Target.select().where(Target.steam_id == id).get()
    updateRecord.status = status
    updateRecord.save()
    