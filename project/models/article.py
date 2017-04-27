from pony.orm import *

from .base import SciNet


class Article(SciNet.Entity):
    artId = PrimaryKey(str, 32)
    artAuthor = Required(str, 40)
    artJournal = Optional(str, 88)
    artDoi = Optional(str, 64)
    artVolume = Optional(str, 4)
    artPage = Optional(str, 4)
    result = Optional('Result')
    references = Set('Article', reverse='references')
