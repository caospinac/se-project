from pony.orm import *

from .base import SciNet


class Journal(SciNet.Entity):
    jouIssn = PrimaryKey(LongStr, lazy=False)
    jouName = Required(LongStr)
    jouCountry = Optional(LongStr)
    jouFrequent = Optional(LongStr)
    jouArea = Required(LongStr)

    articles = Set('Article')
