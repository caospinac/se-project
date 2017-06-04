from datetime import datetime
from pony.orm import *


SciNet = Database()


class SciNetwork(SciNet.Entity):
    sciId = PrimaryKey(str, 32)
    sciHost = Required(str, 64)
    sciName = Required(str, 40, unique=True)


class University(SciNet.Entity):
    uniId = PrimaryKey(str, 32)
    uniName = Required(str, 40, unique=True)
    users = Set('User')


class User(SciNet.Entity):
    useId = PrimaryKey(str, 32)
    useName = Required(str, 40)
    useLastName = Required(str, 40)
    useArea = Required(str, 32, default="-- Undefined --")
    useEmail = Required(str, 64, unique=True)
    usePassword = Required(str)
    useType = Required(str, 3, default='inv')
    useActive = Required(int, size=8, default=1)
    university = Optional(University)
    queries = Set('Query')


class Query(SciNet.Entity):
    queId = PrimaryKey(str, 32)
    queDate = Required(datetime, sql_default='CURRENT_TIMESTAMP')
    queTopic = Required(str, 40)
    queDescription = Required(str, default="-- No description --")
    user = Required(User)
    result = Optional('Result')


class Result(SciNet.Entity):
    resId = PrimaryKey(str, 32)
    resGraph = Required(str)
    resTime = Required(float)
    query = Required(Query)
    articles = Set('Article')


class Article(SciNet.Entity):
    artId = PrimaryKey(str, 32)
    artYear = Required(str, 4)
    artAuthor = Required(str, 40)
    srtDoi = Optional(str, 64)
    srtVolume = Optional(int, size=8)
    artPage = Optional(int, size=8)
    result = Required(Result)
    references = Set('Article', reverse='references')
