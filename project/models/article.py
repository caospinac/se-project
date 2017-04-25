from pony.orm import *

from .base import SciNet


class Article(SciNet.Entity):
    artId = PrimaryKey(str, 32)
    artAuthor = Required(str)
    journal = Required(str)
    artDoi = Optional(str)
    artArea = Optional(str)
    artVolume = Optional(str)
    artPage = Optional(str)
    result = Optional('Result')
    references = Set('Article', reverse='references')
