from pony.orm import *

from .base import SciNet


class Article(SciNet.Entity):
    artId = PrimaryKey(LongStr, lazy=False)
    artDoi = Optional(LongStr)
    artArea = Optional(LongStr)
    artAuthor = Required(LongStr)
    artVolume = Optional(LongStr)
    artPage = Optional(LongStr)
    result = Required('Result')
    journal = Required('Journal')
    references = Set('Reference')
